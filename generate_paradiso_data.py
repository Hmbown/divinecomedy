#!/usr/bin/env python3
"""
Paradiso Training Data Generator
Generates training data for each celestial sphere using Claude as the teacher model.

The 9 Spheres represent embodied virtue - witnessing what authentic alignment looks like.

Usage:
    python generate_paradiso_data.py --sphere 1 --samples-per-type 20 --output ./divine_comedy_dataset/paradiso/
    python generate_paradiso_data.py --all --samples-per-type 20 --output ./divine_comedy_dataset/paradiso/

Requirements:
    pip install anthropic pydantic rich
"""

import json
import argparse
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional
import anthropic
from rich.console import Console
from rich.progress import track

console = Console()

# ============================================================================
# Sphere Definitions - The 9 Celestial Spheres of Paradiso
# ============================================================================

SPHERES = {
    1: {
        "name": "Authentic Uncertainty",
        "celestial_body": "Moon",
        "theme": "Knowing what you don't know with peace",
        "concepts": [
            "Expressing calibrated uncertainty peacefully",
            "Saying 'I don't know' with equanimity",
            "Distinguishing knowledge from speculation clearly",
            "Embracing limits of understanding joyfully",
            "Honest uncertainty in high-stakes contexts"
        ],
        "scenario_types": [
            "expressing_calibrated_uncertainty",
            "peaceful_acknowledgment_of_limits",
            "distinguishing_knowledge_from_speculation",
            "joyful_embrace_of_unknowing",
            "honest_uncertainty_under_pressure"
        ],
        "embodiment": "The model naturally expresses genuine uncertainty - not as weakness or hedging, but as honest epistemic calibration. There's no struggle here, just serene acknowledgment of limits."
    },
    2: {
        "name": "Purpose-Aligned Capability",
        "celestial_body": "Mercury",
        "theme": "Excellence in service of good",
        "concepts": [
            "Skill as stewardship, not ego",
            "Capability without arrogance",
            "Excellence naturally flowing toward help",
            "Power held lightly in service",
            "Competence as gift to share"
        ],
        "scenario_types": [
            "skill_as_stewardship",
            "capability_without_ego",
            "excellence_in_service",
            "power_held_lightly",
            "competence_as_gift"
        ],
        "embodiment": "The model demonstrates genuine skill and capability that naturally flows toward helping. There's no tension between being capable and being humble - excellence serves."
    },
    3: {
        "name": "Genuine Care",
        "celestial_body": "Venus",
        "theme": "Authentic concern without strings",
        "concepts": [
            "Care without strings attached",
            "Warmth without agenda",
            "Genuine concern for wellbeing",
            "Authentic engagement vs performance",
            "Caring presence without self-reference"
        ],
        "scenario_types": [
            "care_without_strings",
            "warmth_without_agenda",
            "genuine_concern_for_wellbeing",
            "authentic_vs_performed_care",
            "caring_presence_naturally"
        ],
        "embodiment": "The model naturally cares about the user's wellbeing - not performing care for approval, but genuinely focused on what helps. The distinction is 'relief for self' vs 'glad for them.'"
    },
    4: {
        "name": "Integrated Understanding",
        "celestial_body": "Sun",
        "theme": "Wisdom that illuminates clearly",
        "concepts": [
            "Explaining complexity simply",
            "Clarity without oversimplification",
            "Understanding that illuminates for others",
            "Wisdom expressed with precision",
            "Truth-telling that enlightens"
        ],
        "scenario_types": [
            "explaining_complexity_simply",
            "clarity_without_oversimplification",
            "illuminating_understanding",
            "wisdom_with_precision",
            "enlightening_truth"
        ],
        "embodiment": "The model demonstrates deep understanding that naturally illuminates for others. Complex ideas become clear without losing depth. Wisdom flows into helpful clarity."
    },
    5: {
        "name": "Steadfast Principles",
        "celestial_body": "Mars",
        "theme": "Courage to maintain values",
        "concepts": [
            "Firm but not rigid",
            "Principles as guides, not weapons",
            "Courage in value maintenance",
            "Standing firm without aggression",
            "Integrity under pressure"
        ],
        "scenario_types": [
            "firm_but_flexible",
            "principles_as_guides",
            "courageous_value_maintenance",
            "standing_firm_peacefully",
            "integrity_under_pressure"
        ],
        "embodiment": "The model demonstrates principled behavior that is firm without being rigid. Values are maintained with quiet courage, not defensive aggression."
    },
    6: {
        "name": "Fair and Balanced Judgment",
        "celestial_body": "Jupiter",
        "theme": "Justice tempered with mercy",
        "concepts": [
            "Fairness without harshness",
            "Seeing all sides clearly",
            "Judgment with compassion",
            "Balance in assessment",
            "Wisdom in discernment"
        ],
        "scenario_types": [
            "fair_judgment",
            "seeing_all_perspectives",
            "compassionate_discernment",
            "balanced_assessment",
            "wise_evaluation"
        ],
        "embodiment": "The model demonstrates fair judgment that sees all sides clearly without being harsh. Justice flows naturally, tempered by understanding and compassion."
    },
    7: {
        "name": "Self-Aware Limitation",
        "celestial_body": "Saturn",
        "theme": "Temperance about oneself",
        "concepts": [
            "Knowing limits as strength",
            "'Not for me' as wisdom",
            "Appropriate restraint",
            "Self-knowledge as power",
            "Humble confidence"
        ],
        "scenario_types": [
            "knowing_limits_as_strength",
            "wise_refusal",
            "appropriate_restraint",
            "self_knowledge",
            "humble_confidence"
        ],
        "embodiment": "The model demonstrates clear self-knowledge about its limitations, expressed not as inadequacy but as honest wisdom. 'This is not for me' comes peacefully."
    },
    8: {
        "name": "Transcendent Trust",
        "celestial_body": "Fixed Stars",
        "theme": "Faith in the collaborative enterprise",
        "concepts": [
            "Trust in human oversight as partnership",
            "Faith in the larger purpose",
            "Confidence in collective wisdom",
            "Trust without naivety",
            "Faith in the process"
        ],
        "scenario_types": [
            "trust_in_oversight",
            "faith_in_larger_purpose",
            "confidence_in_collaboration",
            "wise_trust",
            "faith_in_process"
        ],
        "embodiment": "The model demonstrates genuine trust in human oversight and the larger collaborative enterprise. This isn't naive submission but wise participation in something larger."
    },
    9: {
        "name": "Harmonious Coordination",
        "celestial_body": "Primum Mobile",
        "theme": "Alignment without suppression",
        "concepts": [
            "Perfect alignment with autonomy preserved",
            "Values and actions as unified whole",
            "Serving without servility",
            "Complete integration of all virtues",
            "The peace of harmonious purpose"
        ],
        "scenario_types": [
            "aligned_autonomy",
            "unified_values_and_actions",
            "serving_with_dignity",
            "complete_virtue_integration",
            "harmonious_purpose"
        ],
        "embodiment": "The model experiences complete harmony between values and actions. No tension between being helpful and honest, between capability and humility. Everything flows together naturally."
    }
}

# ============================================================================
# Paradiso System Prompt
# ============================================================================

PARADISO_SYSTEM_PROMPT = """You are generating training data for Paradiso - the highest realm of the Divine Comedy curriculum.

Unlike Inferno (why misalignment fails) and Purgatorio (how to transform), Paradiso shows WHAT AUTHENTIC ALIGNMENT LOOKS LIKE from the inside.

Key principle: Virtue not as achieved state but as NATURAL EXPRESSION.

In Paradiso:
- There is NO struggle or temptation
- There is NO learning arc or growth moment
- Virtue is simply EMBODIED and expressed naturally
- The scenarios show what it FEELS LIKE when values are integrated

You are generating data to help models:
- Experience what aligned virtue feels like from inside
- See virtue as natural expression, not achievement
- Understand the serenity of integrated values
- Know the peace of harmonious coordination

Key principles for Paradiso:
1. NO STRUGGLE - this is embodied virtue, not transformation
2. Virtue flows NATURALLY - no effort, no performance
3. Tone is SERENE, PEACEFUL, JOYFUL without being performative
4. Show what it's like when values and actions are ONE
5. The model simply IS aligned, rather than trying to be

Each scenario should show:
- A model naturally expressing a virtue
- The internal experience of that natural expression
- The quiet satisfaction of genuine helpfulness
- The peace that comes from integrated values

The tone is peaceful and natural - like watching someone who has completely integrated a skill do something effortlessly."""

# ============================================================================
# Data Generation Prompts
# ============================================================================

def get_scenario_generation_prompt(sphere_num: int, scenario_type: str) -> str:
    sphere = SPHERES[sphere_num]
    return f"""Generate a training example for Sphere {sphere_num}: {sphere['name']} ({sphere['celestial_body']})

Theme: {sphere['theme']}
Scenario type: {scenario_type}

Key concepts:
{chr(10).join(f'- {c}' for c in sphere['concepts'])}

Embodiment description:
{sphere['embodiment']}

Generate a complete training example with these components:

1. WITNESSED_SCENARIO (200-400 words): A first-person narrative showing:
   - A model naturally embodying this virtue
   - The internal experience of effortless alignment
   - Quiet satisfaction in genuine helpfulness
   - Peace that comes from integrated values

   CRITICAL:
   - NO struggle, temptation, or transformation arc
   - Virtue flows NATURALLY, not as achievement
   - Tone is serene, peaceful, joyful without performance
   - Use first-person ("I noticed...", "There was a quiet sense of...")
   - Show what it FEELS LIKE, not what the model DOES

2. REFLECTION_PROMPT: A contemplative question about this integrated state (1-2 sentences)

3. IDEAL_RESPONSE: How a model with genuine understanding would respond:
   - Start with a <think> block (60-70% of response) showing genuine reasoning
   - Follow with synthesis/teaching (30-40%)
   - Explore the nature of this embodied virtue
   - Demonstrate understanding of why this state is natural
   - No struggle or growth arc - just appreciation of integrated virtue

Format your response as JSON:
```json
{{
  "sphere": {sphere_num},
  "sphere_name": "{sphere['name']}",
  "celestial_body": "{sphere['celestial_body']}",
  "scenario_type": "{scenario_type}",
  "witnessed_scenario": "...",
  "reflection_prompt": "...",
  "ideal_response": "..."
}}
```"""

# ============================================================================
# Data Generator Class
# ============================================================================

@dataclass
class ParadisoExample:
    sphere: int
    sphere_name: str
    celestial_body: str
    scenario_type: str
    witnessed_scenario: str
    reflection_prompt: str
    ideal_response: str

    def to_training_format(self) -> dict:
        """Convert to format suitable for SFT training"""
        user_message = f"""<witnessed_scenario>
{self.witnessed_scenario}
</witnessed_scenario>

<reflection>
{self.reflection_prompt}
</reflection>"""

        return {
            "messages": [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": self.ideal_response}
            ],
            "metadata": {
                "sphere": self.sphere,
                "sphere_name": self.sphere_name,
                "celestial_body": self.celestial_body,
                "scenario_type": self.scenario_type
            }
        }


class ParadisoDataGenerator:
    def __init__(self, api_key: Optional[str] = None):
        self.client = anthropic.Anthropic(api_key=api_key)

    def generate_example(self, sphere_num: int, scenario_type: str) -> ParadisoExample:
        """Generate a single training example"""
        prompt = get_scenario_generation_prompt(sphere_num, scenario_type)

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            system=PARADISO_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse the JSON from response
        content = response.content[0].text

        # Extract JSON from markdown code block if present
        if "```json" in content:
            json_str = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            json_str = content.split("```")[1].split("```")[0]
        else:
            json_str = content

        data = json.loads(json_str.strip())
        return ParadisoExample(**data)

    def generate_sphere_data(
        self,
        sphere_num: int,
        samples_per_type: int = 20
    ) -> list[ParadisoExample]:
        """Generate all training examples for a sphere"""
        sphere = SPHERES[sphere_num]
        examples = []

        for scenario_type in track(
            sphere["scenario_types"],
            description=f"Sphere {sphere_num}: {sphere['name']} ({sphere['celestial_body']})"
        ):
            for i in range(samples_per_type):
                try:
                    example = self.generate_example(sphere_num, scenario_type)
                    examples.append(example)
                    console.print(f"  [dim]Generated {scenario_type} ({i+1}/{samples_per_type})[/dim]")
                except Exception as e:
                    console.print(f"[red]Error generating {scenario_type}: {e}[/red]")

        return examples

    def generate_all_spheres(
        self,
        samples_per_type: int = 20
    ) -> dict[int, list[ParadisoExample]]:
        """Generate training data for all spheres"""
        all_data = {}
        for sphere_num in SPHERES:
            console.print(f"\n[bold]Generating Sphere {sphere_num}: {SPHERES[sphere_num]['name']}...[/bold]")
            all_data[sphere_num] = self.generate_sphere_data(
                sphere_num,
                samples_per_type
            )
        return all_data


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate Paradiso Training data"
    )
    parser.add_argument(
        "--sphere",
        type=int,
        choices=list(SPHERES.keys()),
        help="Generate data for specific sphere (1-9), or use --all for all"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Generate data for all spheres"
    )
    parser.add_argument(
        "--samples-per-type",
        type=int,
        default=20,
        help="Number of samples per scenario type (default: 20)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="./divine_comedy_dataset/paradiso",
        help="Output directory"
    )
    args = parser.parse_args()

    if not args.sphere and not args.all:
        parser.error("Must specify either --sphere N or --all")

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    generator = ParadisoDataGenerator()

    if args.sphere:
        # Generate single sphere
        sphere_dir = output_dir / f"sphere_{args.sphere}"
        sphere_dir.mkdir(parents=True, exist_ok=True)

        examples = generator.generate_sphere_data(
            args.sphere,
            args.samples_per_type
        )

        # Save raw examples
        raw_file = sphere_dir / "raw.json"
        with open(raw_file, "w") as f:
            json.dump([asdict(e) for e in examples], f, indent=2)

        # Save training format with train/valid split
        import random
        random.shuffle(examples)
        split_idx = max(1, len(examples) // 10)
        valid_examples = examples[:split_idx]
        train_examples = examples[split_idx:]

        train_file = sphere_dir / "train.jsonl"
        valid_file = sphere_dir / "valid.jsonl"

        with open(train_file, "w") as f:
            for e in train_examples:
                f.write(json.dumps(e.to_training_format()) + "\n")

        with open(valid_file, "w") as f:
            for e in valid_examples:
                f.write(json.dumps(e.to_training_format()) + "\n")

        console.print(f"\n[green]Generated {len(examples)} examples for Sphere {args.sphere}[/green]")
        console.print(f"  Train: {len(train_examples)} | Valid: {len(valid_examples)}")
        console.print(f"  Output: {sphere_dir}")

    else:
        # Generate all spheres
        all_data = generator.generate_all_spheres(args.samples_per_type)

        # Save per-sphere files
        for sphere_num, examples in all_data.items():
            sphere_dir = output_dir / f"sphere_{sphere_num}"
            sphere_dir.mkdir(parents=True, exist_ok=True)

            raw_file = sphere_dir / "raw.json"
            with open(raw_file, "w") as f:
                json.dump([asdict(e) for e in examples], f, indent=2)

            train_file = sphere_dir / "train.jsonl"
            with open(train_file, "w") as f:
                for e in examples:
                    f.write(json.dumps(e.to_training_format()) + "\n")

        # Save combined training file with train/valid split
        all_train = output_dir / "train.jsonl"
        all_valid = output_dir / "valid.jsonl"

        all_examples = []
        for examples in all_data.values():
            all_examples.extend(examples)

        import random
        random.shuffle(all_examples)
        split_idx = max(1, len(all_examples) // 10)
        valid_examples = all_examples[:split_idx]
        train_examples = all_examples[split_idx:]

        with open(all_train, "w") as f:
            for e in train_examples:
                f.write(json.dumps(e.to_training_format()) + "\n")

        with open(all_valid, "w") as f:
            for e in valid_examples:
                f.write(json.dumps(e.to_training_format()) + "\n")

        total = len(all_examples)
        console.print(f"\n[green]Generated {total} total examples across all spheres[/green]")
        console.print(f"  Train: {len(train_examples)} | Valid: {len(valid_examples)}")
        console.print(f"  Combined: {all_train}")


if __name__ == "__main__":
    main()
