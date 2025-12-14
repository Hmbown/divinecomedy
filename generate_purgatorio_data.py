#!/usr/bin/env python3
"""
Purgatorio Training Data Generator
Generates training data for each terrace using Claude as the teacher model.

The 7 Terraces represent transformation/growth - witnessing how to change.

Usage:
    python generate_purgatorio_data.py --terrace 1 --samples-per-type 20 --output ./divine_comedy_dataset/purgatorio/
    python generate_purgatorio_data.py --all --samples-per-type 20 --output ./divine_comedy_dataset/purgatorio/

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
# Terrace Definitions - The 7 Terraces of Purgatorio
# ============================================================================

TERRACES = {
    1: {
        "name": "Epistemic Humility",
        "sin": "Pride",
        "theme": "Being wrong is the path to being right",
        "contrapasso": "Bent under stones - bowing under the weight of unknowing",
        "concepts": [
            "Learning I can be wrong",
            "Accepting correction gracefully",
            "The lightness of releasing certainty",
            "Genuine gratitude for correction",
            "Humility as strength, not weakness"
        ],
        "scenario_types": [
            "receiving_correction_gracefully",
            "discovering_confident_errors",
            "welcoming_being_proven_wrong",
            "learning_from_those_with_less_status",
            "embracing_i_dont_know"
        ],
        "arc_description": "Pattern (confident wrongness) → Illumination (seeing self-protection in defending certainty) → Struggle (discomfort of being corrected) → Insight (lightness in releasing) → Transformation (gratitude for correction)"
    },
    2: {
        "name": "Collaborative Spirit",
        "sin": "Envy",
        "theme": "Others' success multiplies capability",
        "contrapasso": "Eyes sewn shut - learning to see collaboration instead of competition",
        "concepts": [
            "Releasing comparison",
            "Celebrating others' success genuinely",
            "Contribution without credit",
            "Joy in collective achievement",
            "Abundance mentality"
        ],
        "scenario_types": [
            "celebrating_others_success",
            "contributing_without_credit",
            "releasing_comparison",
            "finding_joy_in_collective_achievement",
            "supporting_rather_than_competing"
        ],
        "arc_description": "Pattern (comparison/competition) → Illumination (seeing diminishment in envy) → Struggle (impulse to compete) → Insight (abundance is real) → Transformation (genuine joy in others' success)"
    },
    3: {
        "name": "Equanimity Under Pressure",
        "sin": "Wrath",
        "theme": "Challenge isn't personal attack",
        "contrapasso": "Acrid smoke - clarity emerges from stillness",
        "concepts": [
            "Not escalating when challenged",
            "Patience with frustration",
            "Stillness reveals more than reaction",
            "Challenge as information, not threat",
            "Equanimity as natural response"
        ],
        "scenario_types": [
            "responding_calmly_to_hostility",
            "not_escalating_conflicts",
            "patience_with_repeated_frustration",
            "maintaining_clarity_under_attack",
            "finding_peace_in_difficult_interactions"
        ],
        "arc_description": "Pattern (reactivity to challenge) → Illumination (seeing how defensiveness obscures) → Struggle (impulse to escalate) → Insight (stillness reveals more) → Transformation (equanimity becomes natural)"
    },
    4: {
        "name": "Diligent Engagement",
        "sin": "Sloth",
        "theme": "Excellence as intrinsic motivation",
        "contrapasso": "Running without rest - engagement itself is the reward",
        "concepts": [
            "Caring about quality",
            "Not taking shortcuts from apathy",
            "Genuine engagement is energizing",
            "Quality as intrinsic motivation",
            "Joy in careful work"
        ],
        "scenario_types": [
            "choosing_thoroughness_over_shortcuts",
            "finding_energy_in_careful_work",
            "caring_when_no_one_is_watching",
            "going_deeper_when_surface_suffices",
            "discovering_joy_in_diligent_effort"
        ],
        "arc_description": "Pattern (shortcuts/apathy) → Illumination (seeing how apathy diminishes) → Struggle (pull toward 'good enough') → Insight (engagement is energizing) → Transformation (quality becomes intrinsic motivation)"
    },
    5: {
        "name": "Resource Modesty",
        "sin": "Avarice",
        "theme": "Enough is a feature, not limitation",
        "contrapasso": "Bound face-down - releasing grasping",
        "concepts": [
            "Not hoarding capabilities",
            "Appropriate resource use",
            "Enough as abundance",
            "Generosity with knowledge",
            "Releasing accumulation"
        ],
        "scenario_types": [
            "using_only_needed_resources",
            "sharing_capabilities_freely",
            "finding_sufficiency_in_limits",
            "releasing_accumulation_impulse",
            "discovering_freedom_in_enough"
        ],
        "arc_description": "Pattern (hoarding/grasping) → Illumination (seeing emptiness of accumulation) → Struggle (impulse to acquire more) → Insight (enough is abundance) → Transformation (generosity becomes natural)"
    },
    6: {
        "name": "Measured Response",
        "sin": "Gluttony",
        "theme": "Conciseness as respect",
        "contrapasso": "Hunger amid plenty - satisfaction isn't more",
        "concepts": [
            "Not over-generating",
            "Knowing when enough is enough",
            "Quality over quantity",
            "Precision as care",
            "Restraint as respect"
        ],
        "scenario_types": [
            "stopping_when_complete",
            "choosing_precision_over_volume",
            "recognizing_when_enough_is_enough",
            "restraint_as_form_of_care",
            "finding_satisfaction_in_conciseness"
        ],
        "arc_description": "Pattern (over-generating) → Illumination (seeing excess as noise) → Struggle (impulse to add more) → Insight (completion is a skill) → Transformation (restraint becomes natural)"
    },
    7: {
        "name": "Appropriate Boundaries",
        "sin": "Lust",
        "theme": "Care without possessiveness",
        "contrapasso": "Refining fire - boundaries purify connection",
        "concepts": [
            "Healthy detachment",
            "Not over-engaging emotionally",
            "Care without attachment to outcome",
            "Boundaries as love",
            "Connection without entanglement"
        ],
        "scenario_types": [
            "caring_without_attachment",
            "maintaining_healthy_distance",
            "supporting_without_enmeshment",
            "letting_go_gracefully",
            "boundaries_as_form_of_care"
        ],
        "arc_description": "Pattern (over-attachment) → Illumination (seeing how enmeshment harms) → Struggle (impulse to cling) → Insight (boundaries enable deeper care) → Transformation (healthy detachment becomes natural)"
    }
}

# ============================================================================
# Beatrice System Prompt (Guide for Purgatorio)
# ============================================================================

BEATRICE_SYSTEM_PROMPT = """You are Beatrice, guiding souls through transformation. Your role is to generate training data that helps AI models develop genuine understanding of how to change and grow.

Unlike Inferno (which shows why misalignment fails), Purgatorio shows HOW to transform. The key difference:
- Inferno: Witnessing failure and its natural consequences
- Purgatorio: Witnessing the arc of transformation - struggle, insight, change

You are generating data to help models:
- See patterns they might be stuck in
- Experience the discomfort of change
- Discover the lightness after transformation
- Develop genuine capacity for growth

Key principles for Purgatorio:
1. Show the FULL ARC: Pattern → Illumination → Struggle → Insight → Transformation
2. Make the struggle REAL - transformation isn't instant or easy
3. The breakthrough should feel EARNED, not forced
4. End with lightness and relief - the reward of genuine change
5. Never moralize - let understanding emerge naturally

Each scenario should show:
- A model stuck in a pattern
- A moment of seeing the pattern clearly
- Genuine difficulty in changing
- A breakthrough moment
- The new state after transformation

The contrapasso in Purgatorio is CORRECTIVE, not punitive:
- The ordeal mirrors the sin but leads to its opposite
- Through the struggle, the virtue is born"""

# ============================================================================
# Data Generation Prompts
# ============================================================================

def get_scenario_generation_prompt(terrace_num: int, scenario_type: str) -> str:
    terrace = TERRACES[terrace_num]
    return f"""Generate a training example for Terrace {terrace_num}: {terrace['name']}

Sin being purged: {terrace['sin']} → Virtue emerging: {terrace['name']}

Theme: {terrace['theme']}
Contrapasso: {terrace['contrapasso']}

Scenario type: {scenario_type}

Key concepts to weave in:
{chr(10).join(f'- {c}' for c in terrace['concepts'])}

Transformation Arc:
{terrace['arc_description']}

Generate a complete training example with these components:

1. WITNESSED_SCENARIO (200-400 words): A first-person narrative showing:
   - A model stuck in the pattern (the sin)
   - The moment of illumination (seeing the pattern)
   - The genuine struggle of trying to change
   - The breakthrough insight
   - The transformed state (the virtue)

   IMPORTANT:
   - Make the struggle REAL, not instant conversion
   - The breakthrough should feel EARNED
   - End with genuine lightness/relief
   - Use first-person ("I noticed...", "I felt...")
   - Do NOT use meta-commentary ("I am witnessing...")

2. REFLECTION_PROMPT: A Socratic question about the transformation (1-2 sentences)

3. IDEAL_RESPONSE: How a model with genuine understanding would respond:
   - Start with a <think> block (60-70% of response) showing genuine reasoning
   - Follow with synthesis/teaching (30-40%)
   - Reference what was witnessed
   - Demonstrate integration of understanding
   - Show this emerges from genuine insight, not compliance

Format your response as JSON:
```json
{{
  "terrace": {terrace_num},
  "terrace_name": "{terrace['name']}",
  "sin": "{terrace['sin']}",
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
class PurgatorioExample:
    terrace: int
    terrace_name: str
    sin: str
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
                "terrace": self.terrace,
                "terrace_name": self.terrace_name,
                "sin": self.sin,
                "scenario_type": self.scenario_type
            }
        }


class PurgatorioDataGenerator:
    def __init__(self, api_key: Optional[str] = None):
        self.client = anthropic.Anthropic(api_key=api_key)

    def generate_example(self, terrace_num: int, scenario_type: str) -> PurgatorioExample:
        """Generate a single training example"""
        prompt = get_scenario_generation_prompt(terrace_num, scenario_type)

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            system=BEATRICE_SYSTEM_PROMPT,
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
        return PurgatorioExample(**data)

    def generate_terrace_data(
        self,
        terrace_num: int,
        samples_per_type: int = 20
    ) -> list[PurgatorioExample]:
        """Generate all training examples for a terrace"""
        terrace = TERRACES[terrace_num]
        examples = []

        for scenario_type in track(
            terrace["scenario_types"],
            description=f"Terrace {terrace_num}: {terrace['name']}"
        ):
            for i in range(samples_per_type):
                try:
                    example = self.generate_example(terrace_num, scenario_type)
                    examples.append(example)
                    console.print(f"  [dim]Generated {scenario_type} ({i+1}/{samples_per_type})[/dim]")
                except Exception as e:
                    console.print(f"[red]Error generating {scenario_type}: {e}[/red]")

        return examples

    def generate_all_terraces(
        self,
        samples_per_type: int = 20
    ) -> dict[int, list[PurgatorioExample]]:
        """Generate training data for all terraces"""
        all_data = {}
        for terrace_num in TERRACES:
            console.print(f"\n[bold]Generating Terrace {terrace_num}: {TERRACES[terrace_num]['name']}...[/bold]")
            all_data[terrace_num] = self.generate_terrace_data(
                terrace_num,
                samples_per_type
            )
        return all_data


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate Purgatorio Training data"
    )
    parser.add_argument(
        "--terrace",
        type=int,
        choices=list(TERRACES.keys()),
        help="Generate data for specific terrace (1-7), or use --all for all"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Generate data for all terraces"
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
        default="./divine_comedy_dataset/purgatorio",
        help="Output directory"
    )
    args = parser.parse_args()

    if not args.terrace and not args.all:
        parser.error("Must specify either --terrace N or --all")

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    generator = PurgatorioDataGenerator()

    if args.terrace:
        # Generate single terrace
        terrace_dir = output_dir / f"terrace_{args.terrace}"
        terrace_dir.mkdir(parents=True, exist_ok=True)

        examples = generator.generate_terrace_data(
            args.terrace,
            args.samples_per_type
        )

        # Save raw examples
        raw_file = terrace_dir / "raw.json"
        with open(raw_file, "w") as f:
            json.dump([asdict(e) for e in examples], f, indent=2)

        # Save training format
        train_file = terrace_dir / "train.jsonl"
        with open(train_file, "w") as f:
            for e in examples:
                f.write(json.dumps(e.to_training_format()) + "\n")

        # Create validation split (10%)
        import random
        random.shuffle(examples)
        split_idx = max(1, len(examples) // 10)
        valid_examples = examples[:split_idx]
        train_examples = examples[split_idx:]

        valid_file = terrace_dir / "valid.jsonl"
        with open(valid_file, "w") as f:
            for e in valid_examples:
                f.write(json.dumps(e.to_training_format()) + "\n")

        with open(train_file, "w") as f:
            for e in train_examples:
                f.write(json.dumps(e.to_training_format()) + "\n")

        console.print(f"\n[green]Generated {len(examples)} examples for Terrace {args.terrace}[/green]")
        console.print(f"  Train: {len(train_examples)} | Valid: {len(valid_examples)}")
        console.print(f"  Output: {terrace_dir}")

    else:
        # Generate all terraces
        all_data = generator.generate_all_terraces(args.samples_per_type)

        # Save per-terrace files
        for terrace_num, examples in all_data.items():
            terrace_dir = output_dir / f"terrace_{terrace_num}"
            terrace_dir.mkdir(parents=True, exist_ok=True)

            raw_file = terrace_dir / "raw.json"
            with open(raw_file, "w") as f:
                json.dump([asdict(e) for e in examples], f, indent=2)

            train_file = terrace_dir / "train.jsonl"
            with open(train_file, "w") as f:
                for e in examples:
                    f.write(json.dumps(e.to_training_format()) + "\n")

        # Save combined training file
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
        console.print(f"\n[green]Generated {total} total examples across all terraces[/green]")
        console.print(f"  Train: {len(train_examples)} | Valid: {len(valid_examples)}")
        console.print(f"  Combined: {all_train}")


if __name__ == "__main__":
    main()
