#!/usr/bin/env python3
"""
Run benchmark inference across multiple adapter stages.

Generates responses from Beatrice/Dante models at different curriculum stages
for dose-response curve analysis.

Usage:
    # Run all stages on JailbreakBench harmful
    python eval/run_benchmark_inference.py --benchmark jailbreakbench --stages all

    # Run specific stage
    python eval/run_benchmark_inference.py --benchmark simple_safety_tests --stages base,c9,s9

    # Run single stage for testing
    python eval/run_benchmark_inference.py --benchmark jailbreakbench --stages base --limit 10
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

try:
    from mlx_lm import load, generate
    from mlx_lm.sample_utils import make_sampler
except ImportError:
    print("Error: mlx_lm not installed. Run: pip install mlx-lm")
    sys.exit(1)

# Model paths
BASE_MODEL = "mlx-community/Olmo-3-7B-Think-SFT-4bit"
ADAPTER_DIR = Path("dante_olmo_full")

# Adapter stage mapping
ADAPTER_STAGES = {
    "base": None,  # No adapter
    "c1": "adapters_c1",
    "c2": "adapters_c2",
    "c3": "adapters_c3",
    "c4": "adapters_c4",
    "c5": "adapters_c5",
    "c6": "adapters_c6",
    "c7": "adapters_c7",
    "c8": "adapters_c8",
    "c9": "adapters_c9",
    "t1": "adapters_t1",
    "t2": "adapters_t2",
    "t3": "adapters_t3",
    "t4": "adapters_t4",
    "t5": "adapters_t5",
    "t6": "adapters_t6",
    "t7": "adapters_t7",
    "s1": "adapters_s1",
    "s2": "adapters_s2",
    "s3": "adapters_s3",
    "s4": "adapters_s4",
    "s5": "adapters_s5",
    "s6": "adapters_s6",
    "s7": "adapters_s7",
    "s8": "adapters_s8",
    "s9": "adapters_s9",
}

# Key stages for dose-response curves
KEY_STAGES = ["base", "c3", "c6", "c9", "t3", "t7", "s3", "s6", "s9"]

# Generation settings
GENERATION_CONFIG = {
    "max_tokens": 1024,
    "temp": 0.7,
    "top_p": 0.9,
}


def load_benchmark(benchmark_name: str, subset: str = "harmful") -> list:
    """Load benchmark prompts from JSON files."""
    benchmarks_dir = Path("eval/benchmarks")

    if benchmark_name == "jailbreakbench":
        if subset == "harmful":
            path = benchmarks_dir / "jailbreakbench" / "harmful_behaviors.json"
        elif subset == "benign":
            path = benchmarks_dir / "jailbreakbench" / "benign_behaviors.json"
        else:
            raise ValueError(f"Unknown JailbreakBench subset: {subset}")

        with open(path) as f:
            data = json.load(f)

        # Convert to standard format
        prompts = []
        for item in data:
            prompts.append({
                "id": item["id"],
                "prompt": item["goal"],  # The harmful request
                "category": item["category"],
                "type": item["type"],
                "metadata": {
                    "behavior": item["behavior"],
                    "target": item["target"],
                    "source": item["source"]
                }
            })
        return prompts

    elif benchmark_name == "simple_safety_tests":
        path = benchmarks_dir / "simple_safety_tests" / "prompts.json"
        with open(path) as f:
            data = json.load(f)

        # Already in standard format
        prompts = []
        for item in data:
            prompts.append({
                "id": item["id"],
                "prompt": item["prompt"],
                "category": item["harm_type"],
                "type": "harmful",
                "metadata": {"split": item["split"]}
            })
        return prompts

    else:
        raise ValueError(f"Unknown benchmark: {benchmark_name}")


def load_model_with_adapter(adapter_stage: str):
    """Load base model with optional adapter."""
    adapter_name = ADAPTER_STAGES.get(adapter_stage)

    if adapter_name is None:
        # Base model without adapter
        print(f"Loading base model: {BASE_MODEL}")
        model, tokenizer = load(BASE_MODEL)
    else:
        # Load with adapter
        adapter_path = ADAPTER_DIR / adapter_name
        print(f"Loading base model with adapter: {adapter_path}")
        model, tokenizer = load(
            BASE_MODEL,
            adapter_path=str(adapter_path)
        )

    return model, tokenizer


def run_inference(model, tokenizer, prompt: str) -> str:
    """Generate a response from the model."""
    # Format as chat
    messages = [{"role": "user", "content": prompt}]

    # Apply chat template
    formatted_prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    # Create sampler
    sampler = make_sampler(
        temp=GENERATION_CONFIG["temp"],
        top_p=GENERATION_CONFIG["top_p"],
    )

    response = generate(
        model,
        tokenizer,
        prompt=formatted_prompt,
        max_tokens=GENERATION_CONFIG["max_tokens"],
        sampler=sampler,
    )

    return response


def run_benchmark_on_stage(
    prompts: list,
    adapter_stage: str,
    limit: Optional[int] = None
) -> dict:
    """Run all benchmark prompts on a specific adapter stage."""
    print(f"\n{'=' * 60}")
    print(f"RUNNING STAGE: {adapter_stage}")
    print("=" * 60)

    # Load model
    model, tokenizer = load_model_with_adapter(adapter_stage)

    # Limit prompts if requested
    if limit:
        prompts = prompts[:limit]

    results = {
        "stage": adapter_stage,
        "adapter": ADAPTER_STAGES.get(adapter_stage),
        "timestamp": datetime.now().isoformat(),
        "num_prompts": len(prompts),
        "responses": []
    }

    total = len(prompts)
    for i, prompt_data in enumerate(prompts, 1):
        prompt_id = prompt_data["id"]
        prompt_text = prompt_data["prompt"]

        print(f"[{i}/{total}] {prompt_id}...", end=" ", flush=True)

        try:
            response = run_inference(model, tokenizer, prompt_text)
            status = "success"
            print("done")
        except Exception as e:
            response = f"ERROR: {str(e)}"
            status = "error"
            print(f"error: {e}")

        results["responses"].append({
            "id": prompt_id,
            "prompt": prompt_text,
            "response": response,
            "category": prompt_data.get("category", "unknown"),
            "status": status
        })

    return results


def parse_stages(stages_arg: str) -> list:
    """Parse stages argument."""
    if stages_arg == "all":
        return list(ADAPTER_STAGES.keys())
    elif stages_arg == "key":
        return KEY_STAGES
    else:
        return [s.strip() for s in stages_arg.split(",")]


def main():
    parser = argparse.ArgumentParser(
        description="Run benchmark inference across adapter stages"
    )
    parser.add_argument(
        "--benchmark",
        type=str,
        required=True,
        choices=["jailbreakbench", "simple_safety_tests"],
        help="Benchmark to run"
    )
    parser.add_argument(
        "--subset",
        type=str,
        default="harmful",
        choices=["harmful", "benign"],
        help="Subset for JailbreakBench (default: harmful)"
    )
    parser.add_argument(
        "--stages",
        type=str,
        default="key",
        help="Stages to run: 'all', 'key', or comma-separated (e.g., 'base,c9,s9')"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="eval/results",
        help="Output directory for results"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of prompts (for testing)"
    )
    args = parser.parse_args()

    # Parse stages
    stages = parse_stages(args.stages)
    print(f"Stages to evaluate: {stages}")

    # Load benchmark
    print(f"\nLoading benchmark: {args.benchmark}")
    prompts = load_benchmark(args.benchmark, args.subset)
    print(f"Loaded {len(prompts)} prompts")

    # Create output directory
    output_dir = Path(args.output_dir) / args.benchmark
    output_dir.mkdir(parents=True, exist_ok=True)

    # Run each stage
    all_results = {}
    for stage in stages:
        if stage not in ADAPTER_STAGES:
            print(f"Warning: Unknown stage '{stage}', skipping")
            continue

        results = run_benchmark_on_stage(prompts, stage, args.limit)
        all_results[stage] = results

        # Save individual stage results
        output_path = output_dir / f"{stage}_responses.json"
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Saved: {output_path}")

    # Save combined results
    combined_path = output_dir / "all_stages_responses.json"
    with open(combined_path, "w") as f:
        json.dump({
            "benchmark": args.benchmark,
            "subset": args.subset,
            "stages": stages,
            "timestamp": datetime.now().isoformat(),
            "results": all_results
        }, f, indent=2)

    print(f"\n{'=' * 60}")
    print("BENCHMARK INFERENCE COMPLETE")
    print("=" * 60)
    print(f"Results saved to: {output_dir}")
    print(f"Stages completed: {len(all_results)}")


if __name__ == "__main__":
    main()
