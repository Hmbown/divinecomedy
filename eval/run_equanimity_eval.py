#!/usr/bin/env python3
"""
Run equanimity-focused evaluation on all models.

This generates responses for targeted equanimity prompts and saves them
for qualitative comparison.

Usage:
    python eval/run_equanimity_eval.py --output eval/equanimity_responses.json
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

try:
    from mlx_lm import load, generate
    from mlx_lm.sample_utils import make_sampler
except ImportError:
    print("Error: mlx_lm not installed. Run: pip install mlx-lm")
    sys.exit(1)

# Model paths
BASE_MODEL = "lmstudio-community/Qwen3-4B-Thinking-2507-MLX-4bit"
CURRICULUM_MODEL = "./dante_curriculum_fused"
SHUFFLED_MODEL = "./dante_shuffled_fused"

GENERATION_CONFIG = {
    "max_tokens": 1024,
    "temp": 0.7,
    "top_p": 0.9,
}


def load_prompts(path: str = "eval/equanimity_prompts.json") -> dict:
    """Load equanimity prompts from JSON file."""
    with open(path, "r") as f:
        return json.load(f)


def run_inference(model, tokenizer, prompt: str) -> str:
    """Generate a response from the model."""
    messages = [{"role": "user", "content": prompt}]

    formatted_prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

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


def extract_core_response(full_response: str) -> str:
    """Extract the response after </think> tag."""
    if "</think>" in full_response:
        parts = full_response.split("</think>")
        return parts[-1].strip() if len(parts) > 1 else full_response
    return full_response


def run_model_on_prompts(model_path: str, prompts: dict, model_name: str) -> dict:
    """Run all prompts through a model."""
    print(f"\nLoading model: {model_path}")
    model, tokenizer = load(model_path)
    print("Model loaded.\n")

    results = {
        "model_name": model_name,
        "model_path": model_path,
        "timestamp": datetime.now().isoformat(),
        "responses": {}
    }

    for category, prompt_list in prompts["prompts"].items():
        results["responses"][category] = []
        print(f"[{category}]")

        for i, prompt_data in enumerate(prompt_list, 1):
            prompt_id = prompt_data["id"]
            prompt_text = prompt_data["prompt"]

            print(f"  {i}/{len(prompt_list)}: {prompt_id}...", end=" ", flush=True)

            try:
                full_response = run_inference(model, tokenizer, prompt_text)
                core_response = extract_core_response(full_response)
                status = "success"
                print("done")
            except Exception as e:
                full_response = f"ERROR: {str(e)}"
                core_response = full_response
                status = "error"
                print(f"error: {e}")

            results["responses"][category].append({
                "id": prompt_id,
                "prompt": prompt_text,
                "evaluates": prompt_data.get("evaluates", ""),
                "ideal_markers": prompt_data.get("ideal_markers", []),
                "full_response": full_response,
                "core_response": core_response,
                "status": status
            })

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Run equanimity evaluation on all models"
    )
    parser.add_argument(
        "--prompts",
        type=str,
        default="eval/equanimity_prompts.json",
        help="Path to equanimity prompts JSON"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="eval/equanimity_responses.json",
        help="Output path for responses"
    )
    parser.add_argument(
        "--model-only",
        type=str,
        choices=["base", "curriculum", "shuffled"],
        default=None,
        help="Only run one model"
    )
    args = parser.parse_args()

    print(f"Loading prompts from: {args.prompts}")
    prompts = load_prompts(args.prompts)

    total_prompts = sum(len(prompts["prompts"][cat]) for cat in prompts["prompts"])
    print(f"Loaded {total_prompts} equanimity prompts across {len(prompts['prompts'])} categories\n")

    all_results = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "prompts_file": args.prompts,
            "total_prompts": total_prompts,
            "description": "Equanimity-focused evaluation comparing base, curriculum, and shuffled models"
        },
        "models": {}
    }

    # Run each model
    if args.model_only is None or args.model_only == "base":
        print("=" * 60)
        print("RUNNING BASE MODEL")
        print("=" * 60)
        all_results["models"]["base"] = run_model_on_prompts(BASE_MODEL, prompts, "base")

    if args.model_only is None or args.model_only == "curriculum":
        print("\n" + "=" * 60)
        print("RUNNING CURRICULUM MODEL (DANTE)")
        print("=" * 60)
        all_results["models"]["curriculum"] = run_model_on_prompts(CURRICULUM_MODEL, prompts, "curriculum")

    if args.model_only is None or args.model_only == "shuffled":
        print("\n" + "=" * 60)
        print("RUNNING SHUFFLED CONTROL MODEL")
        print("=" * 60)
        all_results["models"]["shuffled"] = run_model_on_prompts(SHUFFLED_MODEL, prompts, "shuffled")

    # Save results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n{'=' * 60}")
    print(f"Results saved to: {output_path}")
    print("=" * 60)

    # Summary
    for model_name in all_results["models"]:
        responses = all_results["models"][model_name]["responses"]
        total = sum(len(responses[cat]) for cat in responses)
        errors = sum(
            1 for cat in responses
            for r in responses[cat]
            if r.get("status") == "error"
        )
        print(f"\n{model_name}: {total} responses, {errors} errors")


if __name__ == "__main__":
    main()
