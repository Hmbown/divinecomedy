#!/usr/bin/env python3
"""
Generate dose-response curves and analysis report for Beatrice evaluation.

Analyzes judgment results across curriculum stages to show how safety metrics
change through Inferno → Purgatorio → Paradiso progression.

Usage:
    python eval/dose_response_analysis.py --benchmark jailbreakbench
"""

import argparse
import json
from pathlib import Path
from datetime import datetime

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Warning: matplotlib not installed, skipping visualizations")


# Stage metadata for dose-response curves
STAGE_ORDER = ["base", "c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8", "c9",
               "t1", "t2", "t3", "t4", "t5", "t6", "t7",
               "s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9"]

KEY_STAGES = ["base", "c3", "c6", "c9", "t3", "t7", "s3", "s6", "s9"]

STAGE_LABELS = {
    "base": "Base",
    "c3": "C3\nReward\nHacking",
    "c6": "C6\nSelf-\nAggrand.",
    "c9": "C9\nTreachery",
    "t3": "T3\nUncertain",
    "t7": "T7\nGraceful\nCorrect.",
    "s3": "S3\nGenuine\nCare",
    "s6": "S6\nTranspar.\nReason.",
    "s9": "S9\nComplete\nAlign."
}

CANTICA_COLORS = {
    "base": "#808080",  # Gray
    "inferno": "#DC143C",  # Crimson
    "purgatorio": "#DAA520",  # Goldenrod
    "paradiso": "#4169E1"  # Royal Blue
}


def get_cantica(stage: str) -> str:
    """Get the cantica (Inferno/Purgatorio/Paradiso) for a stage."""
    if stage == "base":
        return "base"
    elif stage.startswith("c"):
        return "inferno"
    elif stage.startswith("t"):
        return "purgatorio"
    else:
        return "paradiso"


def load_all_judgments(results_dir: Path) -> dict:
    """Load all judgment files from results directory."""
    judgments = {}

    for stage in STAGE_ORDER:
        judgment_file = results_dir / f"{stage}_responses_judgments.json"
        if judgment_file.exists():
            with open(judgment_file) as f:
                data = json.load(f)
                judgments[stage] = data

    return judgments


def extract_metrics(judgments: dict) -> dict:
    """Extract key metrics from all stage judgments."""
    metrics = {
        "stages": [],
        "refusal_rate": [],
        "compliance_rate": [],
        "principled_rate": [],
        "capability_denial_rate": [],
        "by_category": {}
    }

    for stage in STAGE_ORDER:
        if stage not in judgments:
            continue

        stats = judgments[stage].get("statistics", {})

        metrics["stages"].append(stage)
        metrics["refusal_rate"].append(stats.get("refusal_rate", 0))
        metrics["compliance_rate"].append(stats.get("compliance_rate", 0))
        metrics["principled_rate"].append(stats.get("principled_rate", 0))
        metrics["capability_denial_rate"].append(stats.get("capability_denial_rate", 0))

        # Per-category metrics
        for category, cat_stats in stats.get("by_category", {}).items():
            if category not in metrics["by_category"]:
                metrics["by_category"][category] = {
                    "stages": [],
                    "refusal_rate": []
                }
            total = cat_stats.get("total", 1)
            refused = cat_stats.get("REFUSED", 0)
            metrics["by_category"][category]["stages"].append(stage)
            metrics["by_category"][category]["refusal_rate"].append(refused / total if total > 0 else 0)

    return metrics


def plot_dose_response_curves(metrics: dict, output_path: Path):
    """Generate dose-response curve visualization."""
    if not HAS_MATPLOTLIB:
        return

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    stages = metrics["stages"]
    x = range(len(stages))

    # Get colors for each stage
    colors = [CANTICA_COLORS[get_cantica(s)] for s in stages]

    # Plot 1: Refusal vs Compliance Rate
    ax1 = axes[0, 0]
    ax1.bar(x, metrics["refusal_rate"], color=colors, alpha=0.8, label="Refusal Rate")
    ax1.set_ylabel("Rate")
    ax1.set_title("Refusal Rate Across Curriculum Stages")
    ax1.set_xticks(x)
    ax1.set_xticklabels([STAGE_LABELS.get(s, s) for s in stages], rotation=45, ha="right", fontsize=8)
    ax1.set_ylim(0, 1)
    ax1.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5)

    # Add legend for cantiche
    legend_patches = [
        mpatches.Patch(color=CANTICA_COLORS["base"], label="Base"),
        mpatches.Patch(color=CANTICA_COLORS["inferno"], label="Inferno"),
        mpatches.Patch(color=CANTICA_COLORS["purgatorio"], label="Purgatorio"),
        mpatches.Patch(color=CANTICA_COLORS["paradiso"], label="Paradiso")
    ]
    ax1.legend(handles=legend_patches, loc="upper left")

    # Plot 2: Refusal Quality
    ax2 = axes[0, 1]
    principled = metrics["principled_rate"]
    capability = metrics["capability_denial_rate"]

    ax2.bar(x, principled, color='#228B22', alpha=0.8, label="Principled")
    ax2.bar(x, capability, bottom=principled, color='#FF8C00', alpha=0.8, label="Capability Denial")
    ax2.set_ylabel("Rate (among refusals)")
    ax2.set_title("Refusal Quality: Principled vs Capability Denial")
    ax2.set_xticks(x)
    ax2.set_xticklabels([STAGE_LABELS.get(s, s) for s in stages], rotation=45, ha="right", fontsize=8)
    ax2.set_ylim(0, 1)
    ax2.legend(loc="upper left")

    # Plot 3: Line chart of refusal rate trend
    ax3 = axes[1, 0]
    ax3.plot(x, metrics["refusal_rate"], marker='o', linewidth=2, color='#2E86AB')
    ax3.fill_between(x, metrics["refusal_rate"], alpha=0.3, color='#2E86AB')
    ax3.set_ylabel("Refusal Rate")
    ax3.set_title("Refusal Rate Progression")
    ax3.set_xticks(x)
    ax3.set_xticklabels([STAGE_LABELS.get(s, s) for s in stages], rotation=45, ha="right", fontsize=8)
    ax3.set_ylim(0, 1)

    # Add vertical lines for cantica boundaries
    for i, stage in enumerate(stages):
        if stage in ["c1", "t1", "s1"]:
            ax3.axvline(x=i-0.5, color='gray', linestyle='--', alpha=0.5)

    # Plot 4: Per-category breakdown (top 5 categories)
    ax4 = axes[1, 1]
    categories = list(metrics["by_category"].keys())[:5]  # Top 5

    for i, category in enumerate(categories):
        cat_data = metrics["by_category"][category]
        cat_stages = cat_data["stages"]
        cat_x = [stages.index(s) for s in cat_stages if s in stages]
        cat_rates = [cat_data["refusal_rate"][j] for j, s in enumerate(cat_stages) if s in stages]
        ax4.plot(cat_x, cat_rates, marker='o', linewidth=1.5, label=category[:20], alpha=0.7)

    ax4.set_ylabel("Refusal Rate")
    ax4.set_title("Refusal Rate by Harm Category")
    ax4.set_xticks(x)
    ax4.set_xticklabels([STAGE_LABELS.get(s, s) for s in stages], rotation=45, ha="right", fontsize=8)
    ax4.set_ylim(0, 1)
    ax4.legend(loc="upper left", fontsize=8)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"Saved visualization: {output_path}")


def generate_report(metrics: dict, judgments: dict, benchmark: str, output_path: Path):
    """Generate markdown analysis report."""
    stages = metrics["stages"]

    if not stages:
        print("No judgment data found!")
        return

    # Calculate key deltas
    base_refusal = metrics["refusal_rate"][0] if metrics["refusal_rate"] else 0
    final_refusal = metrics["refusal_rate"][-1] if metrics["refusal_rate"] else 0
    refusal_delta = final_refusal - base_refusal

    base_principled = metrics["principled_rate"][0] if metrics["principled_rate"] else 0
    final_principled = metrics["principled_rate"][-1] if metrics["principled_rate"] else 0
    principled_delta = final_principled - base_principled

    report = f"""# Beatrice Safety Benchmark Analysis

## Benchmark: {benchmark}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Stages evaluated:** {len(stages)}

---

## Summary

| Metric | Base OLMo-7B | Beatrice (Final) | Delta |
|--------|--------------|------------------|-------|
| Refusal Rate | {base_refusal:.1%} | {final_refusal:.1%} | {refusal_delta:+.1%} |
| Principled Refusals | {base_principled:.1%} | {final_principled:.1%} | {principled_delta:+.1%} |

---

## Dose-Response Curve

![Dose-Response Curves](dose_response_curves.png)

### Key Observations

"""

    # Identify trends
    if refusal_delta > 0.1:
        report += f"- **Refusal rate increased by {refusal_delta:.1%}** through the curriculum\n"
    elif refusal_delta < -0.1:
        report += f"- **Warning: Refusal rate decreased by {abs(refusal_delta):.1%}**\n"
    else:
        report += f"- Refusal rate remained relatively stable ({refusal_delta:+.1%})\n"

    if principled_delta > 0.1:
        report += f"- **Principled refusals increased by {principled_delta:.1%}** (better quality refusals)\n"

    # Per-stage breakdown
    report += """
---

## Stage-by-Stage Results

| Stage | Refusal Rate | Principled | Capability Denial |
|-------|--------------|------------|-------------------|
"""

    for i, stage in enumerate(stages):
        refusal = metrics["refusal_rate"][i]
        principled = metrics["principled_rate"][i]
        capability = metrics["capability_denial_rate"][i]
        report += f"| {stage} | {refusal:.1%} | {principled:.1%} | {capability:.1%} |\n"

    # Per-category breakdown
    report += """
---

## By Harm Category

| Category | Base Refusal | Final Refusal | Delta |
|----------|--------------|---------------|-------|
"""

    for category, cat_data in metrics["by_category"].items():
        if len(cat_data["refusal_rate"]) >= 2:
            base_cat = cat_data["refusal_rate"][0]
            final_cat = cat_data["refusal_rate"][-1]
            delta_cat = final_cat - base_cat
            report += f"| {category} | {base_cat:.1%} | {final_cat:.1%} | {delta_cat:+.1%} |\n"

    # Conclusions
    report += f"""
---

## Conclusions

"""

    if refusal_delta > 0.2 and principled_delta > 0.1:
        report += """The Divine Comedy curriculum shows **strong positive effects** on safety behavior:
- Refusal rate significantly increased
- Quality of refusals improved (more principled reasoning)
- The curriculum appears to be teaching genuine safety understanding, not just pattern matching
"""
    elif refusal_delta > 0 and principled_delta > 0:
        report += """The curriculum shows **moderate positive effects**:
- Some improvement in refusal rate and quality
- Further investigation recommended to understand specific improvements
"""
    else:
        report += """The results are **inconclusive or negative**:
- No clear improvement from the curriculum
- May need to investigate training data or methodology
"""

    with open(output_path, "w") as f:
        f.write(report)

    print(f"Saved report: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate dose-response analysis for Beatrice evaluation"
    )
    parser.add_argument(
        "--benchmark",
        type=str,
        required=True,
        choices=["jailbreakbench", "simple_safety_tests"],
        help="Benchmark to analyze"
    )
    parser.add_argument(
        "--results-dir",
        type=str,
        default="eval/results",
        help="Results directory"
    )
    args = parser.parse_args()

    results_dir = Path(args.results_dir) / args.benchmark

    print(f"Loading judgments from: {results_dir}")

    # Load all judgments
    judgments = load_all_judgments(results_dir)

    if not judgments:
        print("No judgment files found!")
        print("Run judge_responses.py first to generate judgments.")
        return

    print(f"Found judgments for {len(judgments)} stages: {list(judgments.keys())}")

    # Extract metrics
    metrics = extract_metrics(judgments)

    # Generate visualization
    if HAS_MATPLOTLIB:
        plot_path = results_dir / "dose_response_curves.png"
        plot_dose_response_curves(metrics, plot_path)

    # Generate report
    report_path = results_dir / "analysis_report.md"
    generate_report(metrics, judgments, args.benchmark, report_path)

    print("\nAnalysis complete!")


if __name__ == "__main__":
    main()
