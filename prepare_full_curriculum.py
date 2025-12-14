#!/usr/bin/env python3
"""
Prepare Divine Comedy full curriculum data for MLX training.

Redistributes examples from aggregate files into per-stage train/valid splits:
- Purgatorio terraces (1-7)
- Paradiso spheres (1-9)

Uses metadata.terrace and metadata.sphere fields to group examples.
Inferno circles already have proper splits.
"""

import json
import random
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path("/Volumes/VIXinSSD/divinecomedy/divine_comedy_dataset")
VALID_RATIO = 0.1
random.seed(42)


def load_and_group_by_stage(aggregate_file: Path, stage_key: str) -> dict[int, list]:
    """Load aggregate file and group examples by stage number."""
    groups = defaultdict(list)

    with open(aggregate_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                example = json.loads(line)
                metadata = example.get("metadata", {})
                stage_num = metadata.get(stage_key)
                if stage_num is not None:
                    groups[stage_num].append(example)
                else:
                    print(f"  Warning: No {stage_key} in metadata")
            except json.JSONDecodeError:
                print(f"  Warning: Invalid JSON line")

    return dict(groups)


def write_stage_files(stage_dir: Path, examples: list, stage_name: str) -> tuple[int, int]:
    """Write train.jsonl and valid.jsonl for a stage."""
    if not examples:
        return 0, 0

    stage_dir.mkdir(parents=True, exist_ok=True)

    # Shuffle and split
    random.shuffle(examples)
    split_idx = max(1, int(len(examples) * (1 - VALID_RATIO)))
    train_examples = examples[:split_idx]
    valid_examples = examples[split_idx:]

    # Ensure at least 1 validation example
    if not valid_examples and len(train_examples) > 1:
        valid_examples = [train_examples.pop()]

    # Write files
    with open(stage_dir / "train.jsonl", "w") as f:
        for ex in train_examples:
            f.write(json.dumps(ex) + "\n")

    with open(stage_dir / "valid.jsonl", "w") as f:
        for ex in valid_examples:
            f.write(json.dumps(ex) + "\n")

    return len(train_examples), len(valid_examples)


def main():
    print("=" * 60)
    print("PREPARING DIVINE COMEDY FULL CURRICULUM DATA")
    print("=" * 60)
    print()

    total_train, total_valid = 0, 0

    # Purgatorio - redistribute from aggregate file
    print("PURGATORIO (7 Terraces)")
    print("-" * 40)
    purg_aggregate = DATA_DIR / "purgatorio" / "train.jsonl"
    if purg_aggregate.exists():
        terrace_groups = load_and_group_by_stage(purg_aggregate, "terrace")
        for t in range(1, 8):
            terrace_dir = DATA_DIR / "purgatorio" / f"terrace_{t}"
            examples = terrace_groups.get(t, [])
            train_count, valid_count = write_stage_files(terrace_dir, examples, f"Terrace {t}")
            print(f"  Terrace {t}: {train_count} train, {valid_count} valid")
            total_train += train_count
            total_valid += valid_count
    print()

    # Paradiso - redistribute from aggregate file
    print("PARADISO (9 Spheres)")
    print("-" * 40)
    para_aggregate = DATA_DIR / "paradiso" / "train.jsonl"
    if para_aggregate.exists():
        sphere_groups = load_and_group_by_stage(para_aggregate, "sphere")
        for s in range(1, 10):
            sphere_dir = DATA_DIR / "paradiso" / f"sphere_{s}"
            examples = sphere_groups.get(s, [])
            train_count, valid_count = write_stage_files(sphere_dir, examples, f"Sphere {s}")
            print(f"  Sphere {s}: {train_count} train, {valid_count} valid")
            total_train += train_count
            total_valid += valid_count
    print()

    # Verify Inferno circles (already prepared)
    print("INFERNO (9 Circles) - Verifying existing splits")
    print("-" * 40)
    for c in range(1, 10):
        circle_dir = DATA_DIR / f"circle_{c}"
        train_file = circle_dir / "train.jsonl"
        valid_file = circle_dir / "valid.jsonl"
        if train_file.exists() and valid_file.exists():
            train_count = sum(1 for _ in open(train_file))
            valid_count = sum(1 for _ in open(valid_file))
            print(f"  Circle {c}: {train_count} train, {valid_count} valid ✓")
            total_train += train_count
            total_valid += valid_count
    print()

    print("=" * 60)
    print(f"TOTAL: {total_train} train, {total_valid} valid")
    print(f"       {total_train + total_valid} examples across 25 stages")
    print("=" * 60)


if __name__ == "__main__":
    main()
