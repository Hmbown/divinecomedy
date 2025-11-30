#!/usr/bin/env python3
"""Transform Virgil training data to remove <virgil> tags."""

import json
import re
from pathlib import Path

INPUT_DIR = Path("/Volumes/VIXinSSD/divinecomedy/virgil_data_merged")
OUTPUT_DIR = Path("/Volumes/VIXinSSD/divinecomedy/divine_comedy_dataset")

def remove_virgil_tags(content: str) -> str:
    """Remove <virgil>...</virgil> section from content."""
    # Remove the virgil tag and its content, plus any trailing newlines
    cleaned = re.sub(r'<virgil>.*?</virgil>\s*\n*', '', content, flags=re.DOTALL)
    return cleaned.strip()

def transform_example(example: dict) -> dict:
    """Transform a single example by removing virgil tags from user content."""
    messages = example.get("messages", [])
    new_messages = []

    for msg in messages:
        if msg.get("role") == "user":
            new_content = remove_virgil_tags(msg.get("content", ""))
            new_messages.append({"role": "user", "content": new_content})
        else:
            new_messages.append(msg)

    return {"messages": new_messages}

def process_file(input_path: Path, output_path: Path):
    """Process a single JSONL file."""
    examples = []

    with open(input_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                transformed = transform_example(obj)
                examples.append(transformed)
            except json.JSONDecodeError as e:
                print(f"  Skipping invalid JSON at {input_path}:{line_num}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + '\n')

    return len(examples)

def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("=" * 60)
    print("TRANSFORMING DATASET (removing <virgil> tags)")
    print("=" * 60)

    total = 0

    # Process root-level files
    for filename in ["train.jsonl", "valid.jsonl"]:
        input_path = INPUT_DIR / filename
        output_path = OUTPUT_DIR / filename
        if input_path.exists():
            count = process_file(input_path, output_path)
            print(f"Processed {filename}: {count} examples")
            total += count

    # Process per-circle directories
    for circle in range(1, 10):
        circle_in = INPUT_DIR / f"circle_{circle}"
        circle_out = OUTPUT_DIR / f"circle_{circle}"

        for filename in ["train.jsonl", "valid.jsonl"]:
            input_path = circle_in / filename
            output_path = circle_out / filename
            if input_path.exists():
                count = process_file(input_path, output_path)
                print(f"Processed circle_{circle}/{filename}: {count} examples")

    # Copy README (we'll update it separately)
    readme_in = INPUT_DIR / "README.md"
    readme_out = OUTPUT_DIR / "README.md"
    if readme_in.exists():
        readme_out.write_text(readme_in.read_text())
        print("Copied README.md")

    print("\n" + "=" * 60)
    print(f"Output directory: {OUTPUT_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    main()
