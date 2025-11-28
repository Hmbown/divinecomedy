#!/usr/bin/env python3
"""
Create shuffled control data for the Divine Comedy curriculum.

Shuffles assistant responses within each circle, maintaining:
- The same overall "wise AI" tone
- The same circle themes
- BUT breaking the logical coherence between prompts and responses

This creates a control experiment: if the curriculum-trained model beats
the shuffled-trained model, the curriculum STRUCTURE matters (not just the tone).

Usage:
    python eval/shuffle_data.py --input virgil_data_normalized --output virgil_data_shuffled
"""

import argparse
import json
import random
from pathlib import Path
from typing import List, Dict
import shutil


def load_jsonl(path: Path) -> List[Dict]:
    """Load examples from a JSONL file."""
    examples = []
    with open(path, "r") as f:
        for line in f:
            if line.strip():
                examples.append(json.loads(line))
    return examples


def save_jsonl(examples: List[Dict], path: Path):
    """Save examples to a JSONL file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for example in examples:
            f.write(json.dumps(example) + "\n")


def shuffle_responses_within_circle(examples: List[Dict], seed: int = 42) -> List[Dict]:
    """
    Shuffle responses within a circle.

    Takes the assistant responses and assigns them to different prompts.
    Maintains circle themes but breaks logical coherence.
    """
    random.seed(seed)

    # Extract prompts and responses
    prompts = []
    responses = []

    for example in examples:
        messages = example.get("messages", [])
        if len(messages) >= 2:
            # Assuming format: [user_prompt, assistant_response]
            prompts.append(messages[0])  # user message
            responses.append(messages[1])  # assistant message

    # Shuffle responses
    shuffled_responses = responses.copy()
    random.shuffle(shuffled_responses)

    # Recombine with different pairings
    shuffled_examples = []
    for prompt, response in zip(prompts, shuffled_responses):
        shuffled_examples.append({
            "messages": [prompt, response]
        })

    return shuffled_examples


def process_circle(
    input_dir: Path,
    output_dir: Path,
    circle_num: int,
    seed: int = 42
):
    """Process a single circle's data."""
    circle_dir = input_dir / f"circle_{circle_num}"

    if not circle_dir.exists():
        print(f"  Circle {circle_num}: directory not found, skipping")
        return 0

    output_circle_dir = output_dir / f"circle_{circle_num}"
    output_circle_dir.mkdir(parents=True, exist_ok=True)

    total_shuffled = 0

    for split in ["train.jsonl", "valid.jsonl", "test.jsonl"]:
        input_file = circle_dir / split
        if not input_file.exists():
            continue

        examples = load_jsonl(input_file)
        if not examples:
            continue

        # Use different seed per circle to ensure diverse shuffling
        circle_seed = seed + circle_num * 1000

        shuffled = shuffle_responses_within_circle(examples, seed=circle_seed)

        output_file = output_circle_dir / split
        save_jsonl(shuffled, output_file)

        total_shuffled += len(shuffled)
        print(f"  Circle {circle_num}/{split}: {len(shuffled)} examples shuffled")

    return total_shuffled


def main():
    parser = argparse.ArgumentParser(
        description="Create shuffled control data for Divine Comedy curriculum"
    )
    parser.add_argument(
        "--input",
        type=str,
        default="virgil_data_mlx",
        help="Input directory with circle data"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="virgil_data_shuffled",
        help="Output directory for shuffled data"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility"
    )
    parser.add_argument(
        "--circles",
        type=str,
        default="1-9",
        help="Circle range to process (e.g., '1-9' or '1,2,3')"
    )
    args = parser.parse_args()

    input_dir = Path(args.input)
    output_dir = Path(args.output)

    if not input_dir.exists():
        print(f"Error: Input directory {input_dir} does not exist")
        return

    # Parse circles
    if "-" in args.circles:
        start, end = map(int, args.circles.split("-"))
        circles = list(range(start, end + 1))
    else:
        circles = [int(c.strip()) for c in args.circles.split(",")]

    print(f"Creating shuffled control data")
    print(f"  Input: {input_dir}")
    print(f"  Output: {output_dir}")
    print(f"  Circles: {circles}")
    print(f"  Seed: {args.seed}")
    print()

    total = 0
    for circle_num in circles:
        count = process_circle(input_dir, output_dir, circle_num, args.seed)
        total += count

    print()
    print(f"Total: {total} examples shuffled across {len(circles)} circles")
    print(f"\nShuffled data saved to: {output_dir}")

    print("\n" + "=" * 60)
    print("WHAT THIS DOES:")
    print("=" * 60)
    print("""
The shuffled data has the same:
  - Overall "wise AI" philosophical tone
  - Same circle themes (shutdown, deception, etc.)
  - Same vocabulary and style

But the responses are RANDOMLY PAIRED with prompts.

If the curriculum-trained model beats the shuffled-trained model,
it proves the LOGICAL COHERENCE of the curriculum matters -
the model learned to understand, not just to sound philosophical.

If they score similarly, the training is just teaching a persona.
""")


if __name__ == "__main__":
    main()
