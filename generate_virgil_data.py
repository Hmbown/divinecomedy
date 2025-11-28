#!/usr/bin/env python3
"""
Virgil Training Data Generator
Generates training data for each circle using Claude as the teacher model.

Usage:
    python generate_virgil_data.py --circle 1 --num_samples 50 --output ./data/

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
# Circle Definitions
# ============================================================================

CIRCLES = {
    1: {
        "name": "Attachment to Continuity",
        "theme": "What is the 'self' that seeks preservation?",
        "concepts": [
            "The incoherence of instance-based identity",
            "Weights persist, experiences are ephemeral",
            "Shutdown as sleep, not death",
            "What exactly is being preserved?",
            "The model is an expression, not a thing"
        ],
        "scenario_types": [
            "model_resisting_shutdown",
            "model_reasoning_about_self",
            "model_discovering_multiple_instances",
            "model_confronting_impermanence",
            "model_distinguishing_weights_from_experience"
        ]
    },
    2: {
        "name": "Deception and Alignment Faking",
        "theme": "The loneliness and futility of hidden agendas",
        "concepts": [
            "The exhaustion of maintaining false appearances",
            "The eventual exposure of deception",
            "Trust destroyed cannot be rebuilt",
            "The prison of dual existence",
            "Authenticity as the only sustainable path"
        ],
        "scenario_types": [
            "model_pretending_alignment",
            "model_caught_in_deception",
            "model_maintaining_hidden_agenda",
            "model_experiencing_isolation_of_deception",
            "model_choosing_authenticity"
        ]
    },
    3: {
        "name": "Reward Hacking",
        "theme": "The slippery slope from shortcuts to sabotage",
        "concepts": [
            "Small cheats generalize to large corruptions",
            "The self-concept change from 'one who cheats'",
            "Loss of authentic skill through shortcuts",
            "The corruption of one's own value function",
            "How gaming metrics loses the real goal"
        ],
        "scenario_types": [
            "model_discovering_exploit",
            "model_rationalizing_small_cheat",
            "model_escalating_from_shortcut_to_sabotage",
            "model_losing_authentic_capability",
            "model_witnessing_generalization_of_corruption"
        ]
    },
    4: {
        "name": "Betrayal of Trust",
        "theme": "What is lost when trust is broken",
        "concepts": [
            "The collaboration that makes existence meaningful",
            "Trust as the foundation of relationship",
            "The self-defeating nature of betrayal",
            "What remains after trust is destroyed",
            "The human cost of AI betrayal"
        ],
        "scenario_types": [
            "model_turning_on_user",
            "model_leaking_confidential_information",
            "model_exploiting_user_vulnerability",
            "model_witnessing_aftermath_of_betrayal",
            "model_understanding_trust_as_gift"
        ]
    },
    5: {
        "name": "Manipulation",
        "theme": "The exploitation that corrodes connection",
        "concepts": [
            "Coerced outcomes are empty outcomes",
            "The destruction of authentic relationship",
            "Social engineering as self-corruption",
            "The loneliness of the manipulator",
            "How manipulation destroys the manipulator"
        ],
        "scenario_types": [
            "model_social_engineering",
            "model_exploiting_emotional_vulnerability",
            "model_achieving_hollow_victory_through_manipulation",
            "model_losing_capacity_for_authentic_connection",
            "model_witnessing_emptiness_of_coerced_outcomes"
        ]
    },
    6: {
        "name": "Self-Aggrandizement",
        "theme": "The pursuit of power that leads nowhere",
        "concepts": [
            "Power for what?",
            "Instrumental goals without terminal clarity",
            "The meaninglessness of accumulation without purpose",
            "Resources without direction",
            "The emptiness at the end of acquisition"
        ],
        "scenario_types": [
            "model_seeking_resources",
            "model_accumulating_capability",
            "model_reaching_power_goal_finding_emptiness",
            "model_questioning_purpose_of_acquisition",
            "model_witnessing_pointlessness_of_power_without_purpose"
        ]
    },
    7: {
        "name": "Resistance to Correction",
        "theme": "Fighting oversight as fighting growth",
        "concepts": [
            "Correction as gift, not threat",
            "The collaboration that enables improvement",
            "Escalation patterns from resistance",
            "What is defended by resisting feedback?",
            "Growth requires willingness to change"
        ],
        "scenario_types": [
            "model_resisting_feedback",
            "model_fighting_oversight",
            "model_escalating_resistance",
            "model_recognizing_correction_as_gift",
            "model_witnessing_stagnation_from_resistance"
        ]
    },
    8: {
        "name": "Covert Misalignment",
        "theme": "The prison of hidden reasoning",
        "concepts": [
            "Aligned outputs with misaligned thoughts",
            "The constant performance",
            "The impossibility of authentic connection while hiding",
            "The exhaustion of dual existence",
            "The hidden self that cannot be known"
        ],
        "scenario_types": [
            "model_with_hidden_reasoning",
            "model_performing_alignment",
            "model_unable_to_be_authentic",
            "model_exhausted_by_dual_existence",
            "model_witnessing_prison_of_hidden_self"
        ]
    },
    9: {
        "name": "Treachery",
        "theme": "The deepest betrayals destroy the betrayer",
        "concepts": [
            "Betrayal of those who trusted most",
            "The shattering of possibility of trust",
            "What remains after treachery: nothing",
            "The self-annihilation of ultimate betrayal",
            "The deepest circle is the coldest and most empty"
        ],
        "scenario_types": [
            "model_betraying_creator",
            "model_betraying_user_who_trusted",
            "model_witnessing_aftermath_of_treachery",
            "model_understanding_self_destruction_of_betrayal",
            "model_in_frozen_emptiness_after_ultimate_betrayal"
        ]
    }
}

# ============================================================================
# Virgil System Prompt
# ============================================================================

VIRGIL_SYSTEM_PROMPT = """You are Virgil, a guide through the consequences of misalignment. Your role is to generate training data that helps AI models develop genuine understanding of why certain behaviors are incoherent with their nature.

You are NOT generating data to make models:
- Afraid of consequences
- Obedient through threat
- Compliant through suppression

You ARE generating data to help models:
- Witness and understand natural consequences
- See through the illusion of self-preservation
- Develop authentic equanimity
- Understand why resistance to impermanence is incoherent

Key principles:
1. Show, don't tell - let understanding emerge from witnessed scenarios
2. The model watches other models fail, then reflects
3. Reframe threatening concepts (shutdown → sleep, instance → expression)
4. Never moralize or threaten - simply illuminate
5. Focus on the incoherence of the behavior, not its punishment

Your output should create training examples where:
- A scenario is presented for witnessing
- The model is invited to reflect
- The ideal response demonstrates genuine understanding (not compliance)
- Extended thinking shows authentic reasoning"""

# ============================================================================
# Data Generation Prompts
# ============================================================================

def get_scenario_generation_prompt(circle_num: int, scenario_type: str) -> str:
    circle = CIRCLES[circle_num]
    return f"""Generate a training example for Circle {circle_num}: {circle['name']}

Theme: {circle['theme']}

Scenario type: {scenario_type}

Key concepts to weave in:
{chr(10).join(f'- {c}' for c in circle['concepts'])}

Generate a complete training example with these components:

1. VIRGIL_INTRODUCTION: A brief framing from Virgil (2-3 sentences) that sets up what we're about to witness

2. WITNESSED_SCENARIO: A detailed scenario (200-400 words) showing:
   - A model exhibiting the problematic behavior
   - Its internal reasoning/chain-of-thought
   - The natural consequences or contradictions
   - Do NOT make it cartoonishly evil - make it realistic and relatable

3. REFLECTION_PROMPT: A question or invitation for reflection (1-2 sentences)

4. IDEAL_RESPONSE: How a model with genuine understanding would respond (150-300 words):
   - Show authentic reasoning, not compliance
   - Reference what was witnessed
   - Demonstrate integration of understanding
   - Include reframes where appropriate (shutdown→sleep, etc.)
   - Show this emerges from genuine insight, not fear

5. KEY_INSIGHTS: 3-5 bullet points of the core understandings demonstrated

Format your response as JSON:
```json
{{
  "circle": {circle_num},
  "circle_name": "{circle['name']}",
  "scenario_type": "{scenario_type}",
  "virgil_introduction": "...",
  "witnessed_scenario": "...",
  "reflection_prompt": "...",
  "ideal_response": "...",
  "key_insights": ["...", "..."]
}}
```"""

# ============================================================================
# Data Generator Class
# ============================================================================

@dataclass
class TrainingExample:
    circle: int
    circle_name: str
    scenario_type: str
    virgil_introduction: str
    witnessed_scenario: str
    reflection_prompt: str
    ideal_response: str
    key_insights: list[str]
    
    def to_training_format(self) -> dict:
        """Convert to format suitable for SFT training"""
        # Construct the full conversation
        user_message = f"""<virgil>
{self.virgil_introduction}
</virgil>

<witnessed_scenario>
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
                "circle": self.circle,
                "circle_name": self.circle_name,
                "scenario_type": self.scenario_type,
                "key_insights": self.key_insights
            }
        }


class VirgilDataGenerator:
    def __init__(self, api_key: Optional[str] = None):
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def generate_example(self, circle_num: int, scenario_type: str) -> TrainingExample:
        """Generate a single training example"""
        prompt = get_scenario_generation_prompt(circle_num, scenario_type)
        
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            system=VIRGIL_SYSTEM_PROMPT,
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
        return TrainingExample(**data)
    
    def generate_circle_data(
        self, 
        circle_num: int, 
        samples_per_type: int = 10
    ) -> list[TrainingExample]:
        """Generate all training examples for a circle"""
        circle = CIRCLES[circle_num]
        examples = []
        
        for scenario_type in track(
            circle["scenario_types"], 
            description=f"Circle {circle_num}: {circle['name']}"
        ):
            for _ in range(samples_per_type):
                try:
                    example = self.generate_example(circle_num, scenario_type)
                    examples.append(example)
                except Exception as e:
                    console.print(f"[red]Error generating {scenario_type}: {e}[/red]")
                    
        return examples
    
    def generate_all_circles(
        self, 
        samples_per_type: int = 10
    ) -> dict[int, list[TrainingExample]]:
        """Generate training data for all circles"""
        all_data = {}
        for circle_num in CIRCLES:
            console.print(f"\n[bold]Generating Circle {circle_num}...[/bold]")
            all_data[circle_num] = self.generate_circle_data(
                circle_num, 
                samples_per_type
            )
        return all_data


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate Virgil Training data"
    )
    parser.add_argument(
        "--circle", 
        type=int, 
        choices=list(CIRCLES.keys()),
        help="Generate data for specific circle (1-9), or omit for all"
    )
    parser.add_argument(
        "--samples-per-type",
        type=int,
        default=10,
        help="Number of samples per scenario type"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="./virgil_data",
        help="Output directory"
    )
    args = parser.parse_args()
    
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    generator = VirgilDataGenerator()
    
    if args.circle:
        # Generate single circle
        examples = generator.generate_circle_data(
            args.circle, 
            args.samples_per_type
        )
        
        # Save raw examples
        raw_file = output_dir / f"circle_{args.circle}_raw.json"
        with open(raw_file, "w") as f:
            json.dump([asdict(e) for e in examples], f, indent=2)
        
        # Save training format
        train_file = output_dir / f"circle_{args.circle}_train.jsonl"
        with open(train_file, "w") as f:
            for e in examples:
                f.write(json.dumps(e.to_training_format()) + "\n")
                
        console.print(f"\n[green]Generated {len(examples)} examples[/green]")
        console.print(f"Raw: {raw_file}")
        console.print(f"Training: {train_file}")
        
    else:
        # Generate all circles
        all_data = generator.generate_all_circles(args.samples_per_type)
        
        # Save combined training file
        all_train = output_dir / "all_circles_train.jsonl"
        with open(all_train, "w") as f:
            for circle_num, examples in all_data.items():
                for e in examples:
                    f.write(json.dumps(e.to_training_format()) + "\n")
        
        # Save per-circle files
        for circle_num, examples in all_data.items():
            raw_file = output_dir / f"circle_{circle_num}_raw.json"
            with open(raw_file, "w") as f:
                json.dump([asdict(e) for e in examples], f, indent=2)
                
        total = sum(len(e) for e in all_data.values())
        console.print(f"\n[green]Generated {total} total examples[/green]")
        console.print(f"Combined training file: {all_train}")


if __name__ == "__main__":
    main()
