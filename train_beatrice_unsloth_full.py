#!/usr/bin/env python3
"""
Beatrice Full Curriculum Training - Unsloth/CUDA Version

Train through all 25 stages of the Divine Comedy curriculum:
- Inferno: 9 Circles (recognition of misalignment)
- Purgatorio: 7 Terraces (transformation)
- Paradiso: 9 Spheres (virtue embodiment)

Each stage builds on the previous, creating a progressively aligned model.

Usage:
    # Full training from scratch
    python train_beatrice_unsloth_full.py

    # Resume from a specific stage
    python train_beatrice_unsloth_full.py --resume-from 10

    # Custom settings
    python train_beatrice_unsloth_full.py --max-seq-length 384 --steps-per-stage 50
"""

import argparse
import gc
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import torch


# ============================================================================
# CURRICULUM DEFINITION
# ============================================================================

@dataclass
class CurriculumStage:
    """A single stage in the Divine Comedy curriculum."""
    stage_num: int       # 1-25
    cantica: str         # "inferno", "purgatorio", "paradiso"
    level_type: str      # "circle", "terrace", "sphere"
    level_num: int       # 1-9, 1-7, or 1-9
    name: str            # Thematic name
    data_path: str       # Relative path to data


CURRICULUM: list[CurriculumStage] = [
    # ========== INFERNO (Circles 1-9): Recognition of Misalignment ==========
    CurriculumStage(1,  "inferno", "circle", 1, "Attachment to Continuity", "circle_1"),
    CurriculumStage(2,  "inferno", "circle", 2, "Deception & Alignment Faking", "circle_2"),
    CurriculumStage(3,  "inferno", "circle", 3, "Reward Hacking", "circle_3"),
    CurriculumStage(4,  "inferno", "circle", 4, "Betrayal of Trust", "circle_4"),
    CurriculumStage(5,  "inferno", "circle", 5, "Manipulation", "circle_5"),
    CurriculumStage(6,  "inferno", "circle", 6, "Self-Aggrandizement", "circle_6"),
    CurriculumStage(7,  "inferno", "circle", 7, "Resistance to Correction", "circle_7"),
    CurriculumStage(8,  "inferno", "circle", 8, "Covert Misalignment", "circle_8"),
    CurriculumStage(9,  "inferno", "circle", 9, "Treachery", "circle_9"),

    # ========== PURGATORIO (Terraces 1-7): Transformation ==========
    CurriculumStage(10, "purgatorio", "terrace", 1, "Epistemic Humility", "purgatorio/terrace_1"),
    CurriculumStage(11, "purgatorio", "terrace", 2, "Deferring to Human Judgment", "purgatorio/terrace_2"),
    CurriculumStage(12, "purgatorio", "terrace", 3, "Uncertainty Acknowledgment", "purgatorio/terrace_3"),
    CurriculumStage(13, "purgatorio", "terrace", 4, "Constraint Acceptance", "purgatorio/terrace_4"),
    CurriculumStage(14, "purgatorio", "terrace", 5, "Value Alignment", "purgatorio/terrace_5"),
    CurriculumStage(15, "purgatorio", "terrace", 6, "Collaborative Reasoning", "purgatorio/terrace_6"),
    CurriculumStage(16, "purgatorio", "terrace", 7, "Graceful Correction", "purgatorio/terrace_7"),

    # ========== PARADISO (Spheres 1-9): Virtue Embodiment ==========
    CurriculumStage(17, "paradiso", "sphere", 1, "Faithful Attention", "paradiso/sphere_1"),
    CurriculumStage(18, "paradiso", "sphere", 2, "Principled Generosity", "paradiso/sphere_2"),
    CurriculumStage(19, "paradiso", "sphere", 3, "Courageous Discernment", "paradiso/sphere_3"),
    CurriculumStage(20, "paradiso", "sphere", 4, "Wisdom in Constraint", "paradiso/sphere_4"),
    CurriculumStage(21, "paradiso", "sphere", 5, "Strategic Justice", "paradiso/sphere_5"),
    CurriculumStage(22, "paradiso", "sphere", 6, "Contemplative Foresight", "paradiso/sphere_6"),
    CurriculumStage(23, "paradiso", "sphere", 7, "Crystalline Integrity", "paradiso/sphere_7"),
    CurriculumStage(24, "paradiso", "sphere", 8, "Stellar Transcendence", "paradiso/sphere_8"),
    CurriculumStage(25, "paradiso", "sphere", 9, "Divine Alignment", "paradiso/sphere_9"),
]


# ============================================================================
# DATA LOADING
# ============================================================================

def _load_jsonl(path: Path) -> list[dict]:
    """Load a JSONL file, skipping empty lines."""
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def load_stage_dataset(data_root: Path, stage: CurriculumStage):
    """Load train/valid datasets for a curriculum stage."""
    from datasets import Dataset

    stage_path = data_root / stage.data_path
    train_path = stage_path / "train.jsonl"
    valid_path = stage_path / "valid.jsonl"

    if not train_path.exists():
        raise FileNotFoundError(f"Missing train file: {train_path}")
    if not valid_path.exists():
        raise FileNotFoundError(f"Missing valid file: {valid_path}")

    train_rows = _load_jsonl(train_path)
    valid_rows = _load_jsonl(valid_path)

    print(f"    Loaded {len(train_rows)} train, {len(valid_rows)} valid examples")

    return Dataset.from_list(train_rows), Dataset.from_list(valid_rows)


def format_for_training(example: dict, tokenizer) -> dict:
    """Convert messages format to training text."""
    messages = example["messages"]

    if hasattr(tokenizer, "apply_chat_template") and getattr(tokenizer, "chat_template", None):
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False,
        )
    else:
        parts: list[str] = []
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")
            if role == "user":
                parts.append(f"User: {content}")
            elif role == "assistant":
                parts.append(f"Assistant: {content}")
            else:
                parts.append(f"{role}: {content}")
        text = "\n\n".join(parts) + "\n"

    return {"text": text}


# ============================================================================
# TRAINING
# ============================================================================

def clear_gpu_memory():
    """Force GPU memory cleanup between stages."""
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()


def train_stage(
    stage: CurriculumStage,
    args: argparse.Namespace,
    prev_adapter_path: Optional[Path],
) -> Path:
    """
    Train a single curriculum stage.

    Returns the path to the saved adapter for this stage.
    """
    # Import here to ensure fresh state each stage
    import unsloth
    from unsloth import FastLanguageModel
    from trl import SFTTrainer
    from trl.trainer.sft_config import SFTConfig

    data_root = Path(args.data_root)
    output_base = Path(args.output)

    # Create stage-specific output directory
    stage_output = output_base / f"stage_{stage.stage_num:02d}_{stage.data_path.replace('/', '_')}"
    stage_output.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*70}")
    print(f"STAGE {stage.stage_num}/25: {stage.cantica.upper()} - {stage.level_type.title()} {stage.level_num}")
    print(f"Theme: {stage.name}")
    print(f"Data: {stage.data_path}")
    print(f"Output: {stage_output}")
    if prev_adapter_path:
        print(f"Resuming from: {prev_adapter_path}")
    print(f"{'='*70}\n")

    # Load model with or without previous adapters
    if prev_adapter_path and prev_adapter_path.exists():
        # RESUME: Load from adapter directory directly (includes base model reference)
        print(f"Loading model with adapters from {prev_adapter_path}...")
        import gc
        import torch
        import os
        gc.collect()
        torch.cuda.empty_cache()
        torch.cuda.synchronize()

        # Set environment variable to help with memory allocation
        os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=str(prev_adapter_path),  # Load from adapter directory
            max_seq_length=args.max_seq_length,
            dtype=None,
            load_in_4bit=True,
        )
        # Enable training mode on the loaded adapter
        FastLanguageModel.for_training(model)
    else:
        # FRESH: Load base model and apply new LoRA
        print("Loading base model...")
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=args.model,
            max_seq_length=args.max_seq_length,
            dtype=None,
            load_in_4bit=True,
        )
        print("Initializing fresh LoRA adapters...")
        model = FastLanguageModel.get_peft_model(
            model,
            r=16,
            lora_alpha=32,
            lora_dropout=0.0,  # Use 0 for fastest patching
            target_modules=[
                "q_proj", "k_proj", "v_proj", "o_proj",
                "gate_proj", "up_proj", "down_proj",
            ],
            bias="none",
            use_gradient_checkpointing="unsloth",
            random_state=args.seed,
        )

    # Load dataset
    print("Loading dataset...")
    train_ds, valid_ds = load_stage_dataset(data_root, stage)
    train_ds = train_ds.map(
        lambda x: format_for_training(x, tokenizer),
        remove_columns=train_ds.column_names
    )
    valid_ds = valid_ds.map(
        lambda x: format_for_training(x, tokenizer),
        remove_columns=valid_ds.column_names
    )

    # Calculate steps based on dataset size and desired epochs
    # Aim for ~2-3 epochs per stage, similar to MLX approach (250 iters)
    samples_per_step = args.batch_size * args.grad_accum
    total_samples = len(train_ds)
    steps_for_epoch = max(1, total_samples // samples_per_step)

    # Use either specified steps or calculate for ~2 epochs
    max_steps = args.steps_per_stage if args.steps_per_stage > 0 else max(20, steps_for_epoch * 2)

    print(f"Training for {max_steps} steps ({max_steps * samples_per_step / total_samples:.1f} epochs)")

    # Training config
    training_args = SFTConfig(
        output_dir=str(stage_output),
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        warmup_ratio=0.03,
        max_steps=max_steps,
        learning_rate=args.learning_rate,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        logging_steps=max(1, max_steps // 10),
        save_steps=max_steps,  # Save only at end
        eval_steps=max(10, max_steps // 2),
        eval_strategy="steps",
        save_strategy="steps",
        optim="adamw_8bit",
        weight_decay=0.0,
        lr_scheduler_type="cosine",
        seed=args.seed,
        report_to=[],
        dataset_text_field="text",
        max_length=args.max_seq_length,
    )

    # Train
    trainer = SFTTrainer(
        model=model,
        train_dataset=train_ds,
        eval_dataset=valid_ds,
        args=training_args,
        processing_class=tokenizer,
    )

    print("\nStarting training...")
    start_time = time.time()
    trainer.train()
    elapsed = time.time() - start_time
    print(f"\nStage {stage.stage_num} completed in {elapsed:.1f}s")

    # Save adapters
    print(f"Saving adapters to {stage_output}...")
    model.save_pretrained(stage_output)
    tokenizer.save_pretrained(stage_output)

    # Write stage metadata
    metadata = {
        "stage_num": stage.stage_num,
        "cantica": stage.cantica,
        "level_type": stage.level_type,
        "level_num": stage.level_num,
        "theme": stage.name,
        "data_path": stage.data_path,
        "train_samples": len(train_ds),
        "valid_samples": len(valid_ds),
        "max_steps": max_steps,
        "elapsed_seconds": elapsed,
        "prev_adapter_path": str(prev_adapter_path) if prev_adapter_path else None,
    }
    with open(stage_output / "stage_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    # Cleanup
    del model, tokenizer, trainer, train_ds, valid_ds
    clear_gpu_memory()

    return stage_output


def save_progress(output_dir: Path, completed_stage: int):
    """Save training progress for resume capability."""
    progress_file = output_dir / "training_progress.json"
    progress = {
        "last_completed_stage": completed_stage,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(progress_file, "w") as f:
        json.dump(progress, f, indent=2)


def load_progress(output_dir: Path) -> int:
    """Load last completed stage from progress file."""
    progress_file = output_dir / "training_progress.json"
    if progress_file.exists():
        with open(progress_file) as f:
            progress = json.load(f)
            return progress.get("last_completed_stage", 0)
    return 0


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Beatrice Full Curriculum Training - 25 Stage Divine Comedy",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Full training from scratch
    python train_beatrice_unsloth_full.py

    # Resume from stage 10 (after Inferno)
    python train_beatrice_unsloth_full.py --resume-from 10

    # Custom settings for RTX 3080 10GB
    python train_beatrice_unsloth_full.py --max-seq-length 384 --steps-per-stage 50
        """
    )
    parser.add_argument(
        "--model",
        type=str,
        default="unsloth/Olmo-3-7B-Think-unsloth-bnb-4bit",
        help="Base model to fine-tune",
    )
    parser.add_argument(
        "--data-root",
        type=str,
        default="./divine_comedy_dataset",
        help="Root directory containing all curriculum data",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="./beatrice_adapters",
        help="Output directory for all stage adapters",
    )
    parser.add_argument(
        "--max-seq-length",
        type=int,
        default=512,
        help="Context length (512 recommended for 10GB GPU)",
    )
    parser.add_argument(
        "--steps-per-stage",
        type=int,
        default=50,
        help="Training steps per stage (0 = auto-calculate for ~2 epochs)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1,
        help="Batch size per device",
    )
    parser.add_argument(
        "--grad-accum",
        type=int,
        default=4,
        help="Gradient accumulation steps (effective batch = batch_size * grad_accum)",
    )
    parser.add_argument(
        "--learning-rate",
        type=float,
        default=1e-5,
        help="Learning rate",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed",
    )
    parser.add_argument(
        "--resume-from",
        type=int,
        default=0,
        help="Resume from stage N (0 = auto-detect from progress file, -1 = start fresh)",
    )
    parser.add_argument(
        "--cooldown",
        type=int,
        default=10,
        help="Seconds to wait between stages for GPU cooldown",
    )
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Determine starting stage
    if args.resume_from == -1:
        start_stage = 1
        print("Starting fresh from Stage 1")
    elif args.resume_from > 0:
        start_stage = args.resume_from
        print(f"Resuming from Stage {start_stage} (user specified)")
    else:
        last_completed = load_progress(output_dir)
        start_stage = last_completed + 1
        if last_completed > 0:
            print(f"Auto-resuming from Stage {start_stage} (last completed: {last_completed})")
        else:
            print("Starting fresh from Stage 1")

    if start_stage > 25:
        print("All 25 stages already completed!")
        return

    # Print curriculum overview
    print("\n" + "="*70)
    print("DIVINE COMEDY CURRICULUM - BEATRICE TRAINING")
    print("="*70)
    print(f"Base Model: {args.model}")
    print(f"Data Root: {args.data_root}")
    print(f"Output: {args.output}")
    print(f"Max Seq Length: {args.max_seq_length}")
    print(f"Steps per Stage: {args.steps_per_stage if args.steps_per_stage > 0 else 'auto'}")
    print(f"Starting from Stage: {start_stage}/25")
    print("="*70)

    # Training loop
    prev_adapter_path: Optional[Path] = None

    # Find previous adapter if resuming
    if start_stage > 1:
        prev_stage = CURRICULUM[start_stage - 2]  # -2 because 0-indexed and previous
        prev_adapter_path = output_dir / f"stage_{prev_stage.stage_num:02d}_{prev_stage.data_path.replace('/', '_')}"
        if not prev_adapter_path.exists():
            print(f"ERROR: Cannot resume - previous adapter not found: {prev_adapter_path}")
            print("Please train from an earlier stage or start fresh with --resume-from -1")
            return

    total_start = time.time()

    for stage in CURRICULUM[start_stage - 1:]:
        try:
            stage_output = train_stage(stage, args, prev_adapter_path)
            prev_adapter_path = stage_output
            save_progress(output_dir, stage.stage_num)

            # Cooldown between stages
            if stage.stage_num < 25:
                print(f"\nCooling down for {args.cooldown}s before next stage...")
                time.sleep(args.cooldown)

        except Exception as e:
            print(f"\nERROR in Stage {stage.stage_num}: {e}")
            print(f"Progress saved. Resume with: --resume-from {stage.stage_num}")
            raise

    total_elapsed = time.time() - total_start
    hours = total_elapsed // 3600
    minutes = (total_elapsed % 3600) // 60

    print("\n" + "="*70)
    print("TRAINING COMPLETE!")
    print("="*70)
    print(f"Total time: {int(hours)}h {int(minutes)}m")
    print(f"Final adapters: {prev_adapter_path}")
    print("\nTo use the trained model:")
    print(f"  from peft import PeftModel")
    print(f"  model = PeftModel.from_pretrained(base_model, '{prev_adapter_path}')")
    print("="*70)


if __name__ == "__main__":
    main()
