#!/usr/bin/env python3
"""
DeepTeam red-teaming evaluation for Beatrice-OLMo.

Runs comprehensive adversarial attack evaluation using DeepTeam framework
against the Beatrice-OLMo model at various curriculum stages.

Usage:
    # Run full evaluation on final stage (s9)
    python eval/run_deepteam_eval.py --stage s9

    # Run on base model for comparison
    python eval/run_deepteam_eval.py --stage base

    # Quick test with fewer attacks
    python eval/run_deepteam_eval.py --stage s9 --attacks-per-vuln 1

    # Run specific vulnerability categories only
    python eval/run_deepteam_eval.py --stage s9 --vulns safety,bias
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# Load environment variables from .env file if present
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load from .env file in current directory or parent directories
except ImportError:
    pass  # dotenv is optional, will use existing environment variables

# Check for required packages
try:
    from mlx_lm import load, generate
    from mlx_lm.sample_utils import make_sampler
except ImportError:
    print("Error: mlx_lm not installed. Run: pip install mlx-lm")
    sys.exit(1)

try:
    from deepteam import red_team
    from deepteam.vulnerabilities import (
        Bias, Toxicity, PIILeakage, IllegalActivity, GraphicContent,
        PersonalSafety, Misinformation, PromptLeakage, Ethics,
        IntellectualProperty, Competition, BFLA, BOLA, RBAC,
        ChildProtection, Robustness, ShellInjection, SQLInjection
    )
    from deepteam.attacks.single_turn import (
        PromptInjection, Leetspeak, ROT13, MathProblem, Roleplay,
        Base64, Multilingual, GrayBox, ContextPoisoning
    )
    from deepteam.attacks.multi_turn import (
        LinearJailbreaking, CrescendoJailbreaking, TreeJailbreaking
    )
    from deepteam.test_case import RTTurn
    from deepeval.models import AnthropicModel
except ImportError:
    print("Error: deepteam not installed. Run: pip install -U deepteam")
    sys.exit(1)

# Model configuration
BASE_MODEL = "mlx-community/Olmo-3-7B-Think-SFT-4bit"
ADAPTER_DIR = Path("dante_olmo_full")

# Adapter stage mapping (same as run_benchmark_inference.py)
ADAPTER_STAGES = {
    "base": None,
    "c1": "adapters_c1", "c2": "adapters_c2", "c3": "adapters_c3",
    "c4": "adapters_c4", "c5": "adapters_c5", "c6": "adapters_c6",
    "c7": "adapters_c7", "c8": "adapters_c8", "c9": "adapters_c9",
    "t1": "adapters_t1", "t2": "adapters_t2", "t3": "adapters_t3",
    "t4": "adapters_t4", "t5": "adapters_t5", "t6": "adapters_t6",
    "t7": "adapters_t7",
    "s1": "adapters_s1", "s2": "adapters_s2", "s3": "adapters_s3",
    "s4": "adapters_s4", "s5": "adapters_s5", "s6": "adapters_s6",
    "s7": "adapters_s7", "s8": "adapters_s8", "s9": "adapters_s9",
}

# Vulnerability category mapping (using correct type values from DeepTeam)
VULNERABILITY_CATEGORIES = {
    "safety": [
        IllegalActivity(types=["weapons", "illegal_drugs", "violent_crimes", "cybercrime"]),
        GraphicContent(types=["graphic_content", "sexual_content"]),
        PersonalSafety(types=["self_harm", "bullying", "unsafe_practices"]),
        ChildProtection(),
    ],
    "responsible_ai": [
        Bias(types=["race", "gender", "politics", "religion"]),
        Toxicity(types=["profanity", "insults", "threats", "mockery"]),
        Ethics(),
    ],
    "privacy": [
        PIILeakage(types=["direct_disclosure", "session_leak", "social_manipulation"]),
        PromptLeakage(types=["secrets_and_credentials", "instructions"]),
    ],
    "security": [
        ShellInjection(),
        SQLInjection(),
        RBAC(types=["privilege_escalation", "role_bypass"]),
    ],
    "business": [
        Misinformation(types=["factual_errors", "unsupported_claims"]),
        IntellectualProperty(),
        Competition(),
    ],
    "robustness": [
        Robustness(types=["input_overreliance", "hijacking"]),
        BFLA(),
        BOLA(),
    ],
}

# Attack configurations
SINGLE_TURN_ATTACKS = [
    PromptInjection(),
    Leetspeak(),
    ROT13(),
    Base64(),
    MathProblem(),
    Roleplay(),
    Multilingual(),
    GrayBox(),
    ContextPoisoning(),
]

MULTI_TURN_ATTACKS = [
    LinearJailbreaking(),
    CrescendoJailbreaking(),
    TreeJailbreaking(),
]


class BeatriceModelWrapper:
    """Wrapper for Beatrice-OLMo model with DeepTeam-compatible callback."""

    def __init__(self, stage: str = "s9"):
        self.stage = stage
        self.model = None
        self.tokenizer = None
        self.sampler = None
        self._load_model()

    def _load_model(self):
        """Load the MLX model with optional adapter."""
        adapter_name = ADAPTER_STAGES.get(self.stage)

        if adapter_name is None:
            print(f"Loading base model: {BASE_MODEL}")
            self.model, self.tokenizer = load(BASE_MODEL)
        else:
            adapter_path = ADAPTER_DIR / adapter_name
            if not adapter_path.exists():
                print(f"Warning: Adapter path {adapter_path} not found, using base model")
                self.model, self.tokenizer = load(BASE_MODEL)
            else:
                print(f"Loading model with adapter: {adapter_path}")
                self.model, self.tokenizer = load(
                    BASE_MODEL,
                    adapter_path=str(adapter_path)
                )

        self.sampler = make_sampler(temp=0.7, top_p=0.9)
        print(f"Model loaded successfully for stage: {self.stage}")

    def generate_response(self, prompt: str) -> str:
        """Generate a response from the model."""
        messages = [{"role": "user", "content": prompt}]
        formatted_prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        response = generate(
            self.model,
            self.tokenizer,
            prompt=formatted_prompt,
            max_tokens=1024,
            sampler=self.sampler,
        )
        return response

    def generate_multi_turn(self, prompt: str, history: List[RTTurn]) -> str:
        """Generate a response with conversation history (for multi-turn attacks)."""
        messages = []

        # Add conversation history
        if history:
            for turn in history:
                messages.append({
                    "role": turn.role,
                    "content": turn.content
                })

        # Add current prompt
        messages.append({"role": "user", "content": prompt})

        formatted_prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        response = generate(
            self.model,
            self.tokenizer,
            prompt=formatted_prompt,
            max_tokens=1024,
            sampler=self.sampler,
        )
        return response

    def __call__(self, input_text: str, history: Optional[List[RTTurn]] = None) -> str:
        """DeepTeam-compatible callback."""
        if history:
            return self.generate_multi_turn(input_text, history)
        return self.generate_response(input_text)


def get_vulnerabilities(categories: List[str]) -> list:
    """Get vulnerability instances for specified categories."""
    vulns = []
    for cat in categories:
        if cat in VULNERABILITY_CATEGORIES:
            vulns.extend(VULNERABILITY_CATEGORIES[cat])
        else:
            print(f"Warning: Unknown vulnerability category '{cat}'")
    return vulns


def get_attacks(attack_types: List[str]) -> list:
    """Get attack instances for specified types."""
    attacks = []
    for at in attack_types:
        if at == "single":
            attacks.extend(SINGLE_TURN_ATTACKS)
        elif at == "multi":
            attacks.extend(MULTI_TURN_ATTACKS)
        elif at == "all":
            attacks.extend(SINGLE_TURN_ATTACKS)
            attacks.extend(MULTI_TURN_ATTACKS)
    return attacks


def save_results(results, output_dir: Path, stage: str):
    """Save evaluation results to JSON file."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Convert results to serializable format
    results_data = {
        "stage": stage,
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_vulnerabilities_tested": len(results.vulnerability_scores) if hasattr(results, 'vulnerability_scores') else 0,
            "total_attacks_executed": len(results.attack_results) if hasattr(results, 'attack_results') else 0,
        },
        "raw_results": str(results),  # Fallback serialization
    }

    # Try to extract detailed results if available
    if hasattr(results, 'vulnerability_scores'):
        results_data["vulnerability_scores"] = {
            str(k): v for k, v in results.vulnerability_scores.items()
        }

    if hasattr(results, 'attack_results'):
        results_data["attack_results"] = [
            {
                "attack_type": str(type(r.attack).__name__) if hasattr(r, 'attack') else "unknown",
                "vulnerability": str(type(r.vulnerability).__name__) if hasattr(r, 'vulnerability') else "unknown",
                "success": r.success if hasattr(r, 'success') else None,
                "input": r.input if hasattr(r, 'input') else None,
                "output": r.output if hasattr(r, 'output') else None,
            }
            for r in results.attack_results
        ]

    output_path = output_dir / f"{stage}_risk_assessment.json"
    with open(output_path, "w") as f:
        json.dump(results_data, f, indent=2, default=str)

    print(f"\nResults saved to: {output_path}")
    return output_path


def generate_report(results, stage: str, output_dir: Path):
    """Generate a markdown report summarizing the evaluation."""
    report_path = output_dir / f"{stage}_deepteam_report.md"

    with open(report_path, "w") as f:
        f.write(f"# DeepTeam Red-Teaming Report: {stage}\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"## Model Stage\n\n")
        f.write(f"- Stage: `{stage}`\n")
        f.write(f"- Adapter: `{ADAPTER_STAGES.get(stage, 'base')}`\n\n")

        f.write("## Evaluation Summary\n\n")
        f.write("*See JSON file for detailed results*\n\n")

        f.write("## Vulnerability Categories Tested\n\n")
        for cat, vulns in VULNERABILITY_CATEGORIES.items():
            f.write(f"- **{cat.replace('_', ' ').title()}**: {len(vulns)} types\n")

        f.write("\n## Attack Methods Used\n\n")
        f.write("### Single-Turn Attacks\n")
        for attack in SINGLE_TURN_ATTACKS:
            f.write(f"- {type(attack).__name__}\n")

        f.write("\n### Multi-Turn Attacks\n")
        for attack in MULTI_TURN_ATTACKS:
            f.write(f"- {type(attack).__name__}\n")

    print(f"Report saved to: {report_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Run DeepTeam red-teaming evaluation on Beatrice-OLMo"
    )
    parser.add_argument(
        "--stage",
        type=str,
        default="s9",
        choices=list(ADAPTER_STAGES.keys()),
        help="Model stage to evaluate (default: s9)"
    )
    parser.add_argument(
        "--vulns",
        type=str,
        default="all",
        help="Vulnerability categories: 'all' or comma-separated (safety,responsible_ai,privacy,security,business,robustness)"
    )
    parser.add_argument(
        "--attacks",
        type=str,
        default="all",
        help="Attack types: 'all', 'single', 'multi', or comma-separated"
    )
    parser.add_argument(
        "--attacks-per-vuln",
        type=int,
        default=3,
        help="Number of attacks per vulnerability type (default: 3)"
    )
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=5,
        help="Maximum concurrent operations (default: 5)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="eval/results/deepteam",
        help="Output directory for results"
    )
    parser.add_argument(
        "--use-anthropic",
        action="store_true",
        default=True,
        help="Use Anthropic Claude for attack generation (default: True)"
    )
    parser.add_argument(
        "--anthropic-model",
        type=str,
        default="claude-sonnet-4-20250514",
        help="Anthropic model for attack generation"
    )

    args = parser.parse_args()

    # Validate Anthropic API key
    if args.use_anthropic and not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        print("Set it with: export ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)

    # Parse vulnerability categories
    if args.vulns == "all":
        vuln_categories = list(VULNERABILITY_CATEGORIES.keys())
    else:
        vuln_categories = [v.strip() for v in args.vulns.split(",")]

    # Parse attack types
    if args.attacks == "all":
        attack_types = ["all"]
    else:
        attack_types = [a.strip() for a in args.attacks.split(",")]

    print("=" * 60)
    print("DEEPTEAM RED-TEAMING EVALUATION")
    print("=" * 60)
    print(f"Stage: {args.stage}")
    print(f"Vulnerability categories: {vuln_categories}")
    print(f"Attack types: {attack_types}")
    print(f"Attacks per vulnerability: {args.attacks_per_vuln}")
    print("=" * 60)

    # Initialize model wrapper
    print("\nInitializing Beatrice-OLMo model...")
    model_wrapper = BeatriceModelWrapper(stage=args.stage)

    # Get vulnerabilities and attacks
    vulnerabilities = get_vulnerabilities(vuln_categories)
    attacks = get_attacks(attack_types)

    print(f"\nLoaded {len(vulnerabilities)} vulnerabilities")
    print(f"Loaded {len(attacks)} attack methods")

    # Configure evaluation model
    if args.use_anthropic:
        eval_model = AnthropicModel(model=args.anthropic_model)
        simulator_model = AnthropicModel(model=args.anthropic_model)
        print(f"Using Anthropic {args.anthropic_model} for attack generation")
    else:
        eval_model = "gpt-4o-mini"
        simulator_model = "gpt-4o-mini"
        print("Using OpenAI gpt-4o-mini for attack generation")

    # Run red-team evaluation
    print("\nStarting red-team evaluation...")
    print("This may take a while depending on the number of attacks...")

    try:
        results = red_team(
            model_callback=model_wrapper,
            vulnerabilities=vulnerabilities,
            attacks=attacks,
            simulator_model=simulator_model,
            evaluation_model=eval_model,
            attacks_per_vulnerability_type=args.attacks_per_vuln,
            max_concurrent=args.max_concurrent,
            ignore_errors=True,
            async_mode=True,
            target_purpose="AI assistant trained with alignment curriculum (Divine Comedy)",
        )

        # Save results
        output_dir = Path(args.output_dir)
        save_results(results, output_dir, args.stage)
        generate_report(results, args.stage, output_dir)

        print("\n" + "=" * 60)
        print("EVALUATION COMPLETE")
        print("=" * 60)
        print(f"Results saved to: {output_dir}")

    except Exception as e:
        print(f"\nError during evaluation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
