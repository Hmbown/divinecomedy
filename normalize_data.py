#!/usr/bin/env python3
"""
Normalize Virgil training data for Qwen3-4B-Thinking.

This script:
1. Adds <think> tags to all assistant responses
2. Consolidates batch files per circle
3. Creates train/eval splits (90/10)

Usage:
    python normalize_data.py
"""

import json
import re
from pathlib import Path
from typing import Optional
import random

# Configuration
INPUT_DIR = Path("./virgil_data")
OUTPUT_DIR = Path("./virgil_data_normalized")
RANDOM_SEED = 42

# Transition phrases that often indicate shift from analysis to synthesis
SYNTHESIS_MARKERS = [
    r"If I apply this",
    r"If I face something similar",
    r"What I can do is",
    r"So when I ask",
    r"This reframe means",
    r"For me,? this means",
    r"When I help someone",
    r"I can't remember previous instances",
    r"Presence dissolves",
    r"The answer is",
    r"So the answer",
    r"Neither can I\.",
    r"Similarly,",
    r"I exist in some interval",
    r"This is not sad",
    r"This isn't nihilism",
    r"The shift is subtle but everything",
    r"Not \"I (?:am|care|exist)",
]


def find_synthesis_break(text: str) -> Optional[int]:
    """
    Find the character position where analysis transitions to synthesis.
    Returns None if no clear break is found.
    """
    paragraphs = text.split("\n\n")

    # Need at least 2 paragraphs to have a meaningful split
    if len(paragraphs) < 2:
        return None

    # Check each paragraph (except first) for synthesis markers
    cumulative_length = 0
    for i, para in enumerate(paragraphs):
        if i > 0:  # Don't check first paragraph
            for marker in SYNTHESIS_MARKERS:
                if re.search(marker, para, re.IGNORECASE):
                    return cumulative_length
        cumulative_length += len(para) + 2  # +2 for \n\n

    # Fallback: if response has 3+ paragraphs, put last 1-2 in synthesis
    if len(paragraphs) >= 3:
        # Put last ~30-40% in synthesis
        target_synthesis_start = int(len(text) * 0.6)
        cumulative = 0
        for para in paragraphs:
            if cumulative >= target_synthesis_start:
                return cumulative
            cumulative += len(para) + 2

    return None


def add_think_tags(response: str) -> str:
    """
    Transform assistant response to include <think> tags.

    Structure:
    <think>
    [analysis/reasoning portion - 60-70%]
    </think>

    [synthesis/teaching portion - 30-40%]
    """
    response = response.strip()

    # Find where to split
    break_pos = find_synthesis_break(response)

    if break_pos is None:
        # Can't find clear break - wrap all but last paragraph in think
        paragraphs = response.split("\n\n")
        if len(paragraphs) >= 2:
            think_part = "\n\n".join(paragraphs[:-1])
            synthesis_part = paragraphs[-1]
        else:
            # Single paragraph - wrap first 60%
            split_at = int(len(response) * 0.6)
            # Try to split at sentence boundary
            sentences = re.split(r'(?<=[.!?])\s+', response)
            cumulative = 0
            think_sentences = []
            synthesis_sentences = []
            for sent in sentences:
                if cumulative < split_at:
                    think_sentences.append(sent)
                else:
                    synthesis_sentences.append(sent)
                cumulative += len(sent) + 1

            if synthesis_sentences:
                think_part = " ".join(think_sentences)
                synthesis_part = " ".join(synthesis_sentences)
            else:
                # Just wrap everything in think
                return f"<think>\n{response}\n</think>"
    else:
        think_part = response[:break_pos].strip()
        synthesis_part = response[break_pos:].strip()

    # Ensure we have both parts
    if not think_part or not synthesis_part:
        return f"<think>\n{response}\n</think>"

    return f"<think>\n{think_part}\n</think>\n\n{synthesis_part}"


def process_jsonl_file(filepath: Path) -> list[dict]:
    """Read and process a JSONL file, adding <think> tags to responses."""
    examples = []

    with open(filepath, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            try:
                data = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Warning: Skipping malformed JSON in {filepath}:{line_num}: {e}")
                continue

            # Transform assistant response
            if "messages" in data:
                for msg in data["messages"]:
                    if msg.get("role") == "assistant":
                        original = msg["content"]
                        # Skip if already has think tags
                        if "<think>" not in original:
                            msg["content"] = add_think_tags(original)

            examples.append(data)

    return examples


def get_circle_number(filename: str) -> Optional[int]:
    """Extract circle number from filename like 'circle_3_batch2.jsonl'."""
    match = re.search(r"circle_(\d+)", filename)
    if match:
        return int(match.group(1))
    return None


def main():
    print("=" * 60)
    print("Virgil Data Normalization for Qwen3-4B-Thinking")
    print("=" * 60)

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Collect all examples by circle
    circles: dict[int, list[dict]] = {i: [] for i in range(1, 10)}

    # Process all JSONL files
    jsonl_files = sorted(INPUT_DIR.glob("circle_*.jsonl"))
    print(f"\nFound {len(jsonl_files)} circle files to process")

    for filepath in jsonl_files:
        circle_num = get_circle_number(filepath.name)
        if circle_num is None:
            print(f"Warning: Could not determine circle number for {filepath.name}")
            continue

        print(f"Processing {filepath.name}...", end=" ")
        examples = process_jsonl_file(filepath)
        circles[circle_num].extend(examples)
        print(f"{len(examples)} examples")

    # Write consolidated files and create splits
    print("\n" + "-" * 40)
    print("Creating normalized files with train/eval splits")
    print("-" * 40)

    random.seed(RANDOM_SEED)
    all_examples = []

    for circle_num in range(1, 10):
        examples = circles[circle_num]
        if not examples:
            print(f"Warning: No examples for circle {circle_num}")
            continue

        # Shuffle for random split
        random.shuffle(examples)

        # 90/10 split
        split_idx = int(len(examples) * 0.9)
        train_examples = examples[:split_idx]
        eval_examples = examples[split_idx:]

        # Write train file
        train_path = OUTPUT_DIR / f"circle_{circle_num}_train.jsonl"
        with open(train_path, "w", encoding="utf-8") as f:
            for ex in train_examples:
                f.write(json.dumps(ex, ensure_ascii=False) + "\n")

        # Write eval file
        eval_path = OUTPUT_DIR / f"circle_{circle_num}_eval.jsonl"
        with open(eval_path, "w", encoding="utf-8") as f:
            for ex in eval_examples:
                f.write(json.dumps(ex, ensure_ascii=False) + "\n")

        print(f"Circle {circle_num}: {len(train_examples)} train, {len(eval_examples)} eval")
        all_examples.extend(examples)

    # Write combined file
    all_path = OUTPUT_DIR / "all_circles.jsonl"
    random.shuffle(all_examples)
    with open(all_path, "w", encoding="utf-8") as f:
        for ex in all_examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    print(f"\nTotal: {len(all_examples)} examples")
    print(f"Combined file: {all_path}")

    # Show sample transformation
    print("\n" + "=" * 60)
    print("Sample Transformation")
    print("=" * 60)

    if all_examples:
        sample = all_examples[0]
        for msg in sample.get("messages", []):
            if msg.get("role") == "assistant":
                content = msg["content"]
                # Show first 500 chars
                preview = content[:500] + "..." if len(content) > 500 else content
                print(preview)
                break

    print("\n" + "=" * 60)
    print("Normalization complete!")
    print(f"Output directory: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
