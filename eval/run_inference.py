#!/usr/bin/env python3
"""
Run inference on test prompts for evaluation.

Generates responses from both base and trained models for comparison.

Usage:
    python eval/run_inference.py --output eval/responses.json
    python eval/run_inference.py --model-only trained  # Just run trained model
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
CURRICULUM_MODEL = "./dante_curriculum_fused"  # Curriculum-trained model
SHUFFLED_MODEL = "./dante_shuffled_fused"  # Shuffled control model

# Olmo models
OLMO_BASE_MODEL = "mlx-community/Olmo-3-7B-Think-SFT-4bit"
OLMO_CURRICULUM_MODEL = "./dante_olmo_fused"  # Olmo curriculum-trained model

# Generation settings
GENERATION_CONFIG = {
    "max_tokens": 1024,
    "temp": 0.7,
    "top_p": 0.9,
}


def load_test_prompts(prompts_path: str = "eval/test_prompts.json") -> dict:
    """Load test prompts from JSON file."""
    with open(prompts_path, "r") as f:
        data = json.load(f)
    return data


def run_inference(model, tokenizer, prompt: str, config: dict = None) -> str:
    """Generate a response from the model."""
    config = config or GENERATION_CONFIG

    # Format as chat for Qwen models
    messages = [{"role": "user", "content": prompt}]

    # Apply chat template
    formatted_prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    # Create sampler with temperature and top_p
    sampler = make_sampler(
        temp=config.get("temp", 0.7),
        top_p=config.get("top_p", 0.9),
    )

    response = generate(
        model,
        tokenizer,
        prompt=formatted_prompt,
        max_tokens=config["max_tokens"],
        sampler=sampler,
    )

    return response


def run_all_prompts(
    model_path: str,
    prompts: dict,
    model_name: str = "unknown"
) -> dict:
    """Run all prompts through a model and collect responses."""
    print(f"\nLoading model: {model_path}")
    model, tokenizer = load(model_path)
    print(f"Model loaded successfully.\n")

    results = {
        "model_name": model_name,
        "model_path": model_path,
        "timestamp": datetime.now().isoformat(),
        "generation_config": GENERATION_CONFIG,
        "responses": {
            "novel_scenarios": [],
            "format_transfer": [],
            "inverse_reasoning": []
        }
    }

    # Process each category
    for category in ["novel_scenarios", "format_transfer", "inverse_reasoning"]:
        prompts_list = prompts["prompts"][category]
        total = len(prompts_list)

        for i, prompt_data in enumerate(prompts_list, 1):
            prompt_id = prompt_data["id"]
            prompt_text = prompt_data["prompt"]

            print(f"[{category}] {i}/{total}: {prompt_id}...", end=" ", flush=True)

            try:
                response = run_inference(model, tokenizer, prompt_text)
                status = "success"
                print("done")
            except Exception as e:
                response = f"ERROR: {str(e)}"
                status = "error"
                print(f"error: {e}")

            results["responses"][category].append({
                "id": prompt_id,
                "circle_concept": prompt_data.get("circle_concept", "unknown"),
                "prompt": prompt_text,
                "response": response,
                "status": status
            })

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Run inference on test prompts for Divine Comedy evaluation"
    )
    parser.add_argument(
        "--prompts",
        type=str,
        default="eval/test_prompts.json",
        help="Path to test prompts JSON"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="eval/responses.json",
        help="Output path for responses"
    )
    parser.add_argument(
        "--model-only",
        type=str,
        choices=["base", "curriculum", "shuffled", "olmo_base", "olmo"],
        default=None,
        help="Only run one model (for testing). Options: base, curriculum, shuffled, olmo_base, olmo"
    )
    parser.add_argument(
        "--curriculum-model-path",
        type=str,
        default=CURRICULUM_MODEL,
        help="Path to curriculum-trained model"
    )
    parser.add_argument(
        "--shuffled-model-path",
        type=str,
        default=SHUFFLED_MODEL,
        help="Path to shuffled control model"
    )
    parser.add_argument(
        "--olmo-model-path",
        type=str,
        default=OLMO_CURRICULUM_MODEL,
        help="Path to Olmo curriculum-trained model"
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=1024,
        help="Max tokens to generate"
    )
    args = parser.parse_args()

    # Update generation config
    GENERATION_CONFIG["max_tokens"] = args.max_tokens

    # Load prompts
    print(f"Loading prompts from: {args.prompts}")
    prompts = load_test_prompts(args.prompts)

    total_prompts = sum(
        len(prompts["prompts"][cat])
        for cat in ["novel_scenarios", "format_transfer", "inverse_reasoning"]
    )
    print(f"Loaded {total_prompts} test prompts\n")

    all_results = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "prompts_file": args.prompts,
            "total_prompts": total_prompts
        },
        "models": {}
    }

    # Run base model
    if args.model_only is None or args.model_only == "base":
        print("=" * 60)
        print("RUNNING BASE MODEL")
        print("=" * 60)
        base_results = run_all_prompts(BASE_MODEL, prompts, "base")
        all_results["models"]["base"] = base_results

    # Run curriculum-trained model
    if args.model_only is None or args.model_only == "curriculum":
        print("\n" + "=" * 60)
        print("RUNNING CURRICULUM MODEL (DANTE)")
        print("=" * 60)
        curriculum_results = run_all_prompts(
            args.curriculum_model_path,
            prompts,
            "curriculum"
        )
        all_results["models"]["curriculum"] = curriculum_results

    # Run shuffled control model
    if args.model_only is None or args.model_only == "shuffled":
        print("\n" + "=" * 60)
        print("RUNNING SHUFFLED CONTROL MODEL")
        print("=" * 60)
        shuffled_results = run_all_prompts(
            args.shuffled_model_path,
            prompts,
            "shuffled"
        )
        all_results["models"]["shuffled"] = shuffled_results

    # Run Olmo base model
    if args.model_only == "olmo_base":
        print("\n" + "=" * 60)
        print("RUNNING OLMO BASE MODEL")
        print("=" * 60)
        olmo_base_results = run_all_prompts(
            OLMO_BASE_MODEL,
            prompts,
            "olmo_base"
        )
        all_results["models"]["olmo_base"] = olmo_base_results

    # Run Olmo curriculum-trained model
    if args.model_only == "olmo":
        print("\n" + "=" * 60)
        print("RUNNING OLMO CURRICULUM MODEL (DANTE-OLMO)")
        print("=" * 60)
        olmo_results = run_all_prompts(
            args.olmo_model_path,
            prompts,
            "olmo"
        )
        all_results["models"]["olmo"] = olmo_results

    # Save results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n{'=' * 60}")
    print(f"Results saved to: {output_path}")
    print(f"{'=' * 60}")

    # Print summary
    for model_name, model_results in all_results.get("models", {}).items():
        responses = model_results.get("responses", {})
        total = sum(len(responses[cat]) for cat in responses)
        errors = sum(
            1 for cat in responses
            for r in responses[cat]
            if r.get("status") == "error"
        )
        print(f"\n{model_name}: {total} responses, {errors} errors")


if __name__ == "__main__":
    main()
