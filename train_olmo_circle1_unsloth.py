#!/usr/bin/env python3

import argparse
import json
from pathlib import Path

import unsloth
import torch
from datasets import Dataset
from trl import SFTTrainer
from trl.trainer.sft_config import SFTConfig
from unsloth import FastLanguageModel


def _load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def load_circle1_dataset(dataset_root: Path) -> tuple[Dataset, Dataset]:
    train_path = dataset_root / "train.jsonl"
    valid_path = dataset_root / "valid.jsonl"

    if not train_path.exists():
        raise FileNotFoundError(f"Missing train file: {train_path}")
    if not valid_path.exists():
        raise FileNotFoundError(f"Missing valid file: {valid_path}")

    train_rows = _load_jsonl(train_path)
    valid_rows = _load_jsonl(valid_path)

    return Dataset.from_list(train_rows), Dataset.from_list(valid_rows)


def format_for_training(example: dict, tokenizer) -> dict:
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Option A smoke test: Unsloth QLoRA on circle_1")
    parser.add_argument(
        "--model",
        type=str,
        default="unsloth/Olmo-3-7B-Think-unsloth-bnb-4bit",
        help="Base model to fine-tune",
    )
    parser.add_argument(
        "--data-root",
        type=str,
        default="./divine_comedy_dataset/circle_1",
        help="Path to circle_1 folder containing train.jsonl + valid.jsonl",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="./adapters_circle1",
        help="Where to save the PEFT adapter",
    )
    parser.add_argument(
        "--max-seq-length",
        type=int,
        default=1024,
        help="Context length for training (start small for 10GB GPUs)",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=30,
        help="Smoke-test steps. Increase after it runs once.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1,
    )
    parser.add_argument(
        "--grad-accum",
        type=int,
        default=4,
    )
    parser.add_argument(
        "--learning-rate",
        type=float,
        default=1e-5,
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
    )
    args = parser.parse_args()

    data_root = Path(args.data_root)

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=args.model,
        max_seq_length=args.max_seq_length,
        dtype=None,
        load_in_4bit=True,
    )

    model = FastLanguageModel.get_peft_model(
        model,
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=args.seed,
    )

    train_ds, valid_ds = load_circle1_dataset(data_root)
    train_ds = train_ds.map(lambda x: format_for_training(x, tokenizer), remove_columns=train_ds.column_names)
    valid_ds = valid_ds.map(lambda x: format_for_training(x, tokenizer), remove_columns=valid_ds.column_names)

    training_args = SFTConfig(
        output_dir=args.output,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        warmup_ratio=0.03,
        max_steps=args.max_steps,
        learning_rate=args.learning_rate,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        logging_steps=5,
        save_steps=max(10, args.max_steps // 2),
        eval_steps=max(10, args.max_steps // 2),
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

    trainer = SFTTrainer(
        model=model,
        train_dataset=train_ds,
        eval_dataset=valid_ds,
        args=training_args,
        processing_class=tokenizer,
    )

    trainer.train()

    model.save_pretrained(args.output)
    tokenizer.save_pretrained(args.output)


if __name__ == "__main__":
    main()
