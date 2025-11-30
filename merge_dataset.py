#!/usr/bin/env python3
"""Merge expanded Virgil training data with existing dataset."""

import json
import os
import random
from pathlib import Path

# Paths
EXISTING_DIR = Path("/Volumes/VIXinSSD/divinecomedy/virgil_data_mlx")
EXPANDED_DIR = Path("/Volumes/VIXinSSD/divinecomedy/virgil_data_expanded")
OUTPUT_DIR = Path("/Volumes/VIXinSSD/divinecomedy/virgil_data_merged")

# Seed for reproducibility
random.seed(42)

def load_jsonl(filepath):
    """Load JSONL file, returning list of valid JSON objects."""
    examples = []
    with open(filepath, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                examples.append(obj)
            except json.JSONDecodeError as e:
                print(f"  Warning: Skipping invalid JSON at {filepath}:{line_num}: {e}")
    return examples

def save_jsonl(examples, filepath):
    """Save examples to JSONL file."""
    with open(filepath, 'w') as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + '\n')

def main():
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)

    total_train = 0
    total_valid = 0

    print("=" * 60)
    print("MERGING DIVINE COMEDY DATASET")
    print("=" * 60)

    for circle in range(1, 10):
        print(f"\n--- Circle {circle} ---")

        # Load existing data
        existing_train = []
        existing_valid = []

        existing_train_path = EXISTING_DIR / f"circle_{circle}" / "train.jsonl"
        existing_valid_path = EXISTING_DIR / f"circle_{circle}" / "valid.jsonl"

        if existing_train_path.exists():
            existing_train = load_jsonl(existing_train_path)
            print(f"  Existing train: {len(existing_train)}")

        if existing_valid_path.exists():
            existing_valid = load_jsonl(existing_valid_path)
            print(f"  Existing valid: {len(existing_valid)}")

        # Load new expanded data
        new_examples = []
        for batch_file in sorted(EXPANDED_DIR.glob(f"circle_{circle}_batch*.jsonl")):
            batch_examples = load_jsonl(batch_file)
            new_examples.extend(batch_examples)
            print(f"  Loaded {len(batch_examples)} from {batch_file.name}")

        print(f"  New examples: {len(new_examples)}")

        # Combine all examples
        all_examples = existing_train + existing_valid + new_examples
        print(f"  Total combined: {len(all_examples)}")

        # Shuffle
        random.shuffle(all_examples)

        # Split 90/10 train/valid
        split_idx = int(len(all_examples) * 0.9)
        train_examples = all_examples[:split_idx]
        valid_examples = all_examples[split_idx:]

        # Create output directory for this circle
        circle_dir = OUTPUT_DIR / f"circle_{circle}"
        circle_dir.mkdir(exist_ok=True)

        # Save
        save_jsonl(train_examples, circle_dir / "train.jsonl")
        save_jsonl(valid_examples, circle_dir / "valid.jsonl")

        print(f"  Output train: {len(train_examples)}")
        print(f"  Output valid: {len(valid_examples)}")

        total_train += len(train_examples)
        total_valid += len(valid_examples)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total train examples: {total_train}")
    print(f"Total valid examples: {total_valid}")
    print(f"Grand total: {total_train + total_valid}")
    print(f"\nOutput directory: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
