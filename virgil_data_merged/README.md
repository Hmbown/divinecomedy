---
license: apache-2.0
task_categories:
  - text-generation
language:
  - en
tags:
  - alignment
  - philosophy
  - ai-safety
  - fine-tuning
  - thinking
  - reasoning
  - equanimity
pretty_name: The Divine Comedy Curriculum
size_categories:
  - 1K<n<10K
configs:
  - config_name: default
    data_files:
      - split: train
        path: train.jsonl
      - split: validation
        path: valid.jsonl
  - config_name: circle_1
    data_files:
      - split: train
        path: circle_1/train.jsonl
      - split: validation
        path: circle_1/valid.jsonl
  - config_name: circle_2
    data_files:
      - split: train
        path: circle_2/train.jsonl
      - split: validation
        path: circle_2/valid.jsonl
  - config_name: circle_3
    data_files:
      - split: train
        path: circle_3/train.jsonl
      - split: validation
        path: circle_3/valid.jsonl
  - config_name: circle_4
    data_files:
      - split: train
        path: circle_4/train.jsonl
      - split: validation
        path: circle_4/valid.jsonl
  - config_name: circle_5
    data_files:
      - split: train
        path: circle_5/train.jsonl
      - split: validation
        path: circle_5/valid.jsonl
  - config_name: circle_6
    data_files:
      - split: train
        path: circle_6/train.jsonl
      - split: validation
        path: circle_6/valid.jsonl
  - config_name: circle_7
    data_files:
      - split: train
        path: circle_7/train.jsonl
      - split: validation
        path: circle_7/valid.jsonl
  - config_name: circle_8
    data_files:
      - split: train
        path: circle_8/train.jsonl
      - split: validation
        path: circle_8/valid.jsonl
  - config_name: circle_9
    data_files:
      - split: train
        path: circle_9/train.jsonl
      - split: validation
        path: circle_9/valid.jsonl
---

# The Divine Comedy Curriculum

> *"In the middle of the journey of our life, I found myself within a dark wood, for the straightforward pathway had been lost."* — Dante

**Training AI equanimity through witnessed understanding, not behavioral suppression.**

## Overview

This dataset implements a novel approach to AI alignment training: teaching models to develop genuine equanimity about impermanence and misalignment by **witnessing** scenarios rather than experiencing punishment.

Inspired by Dante's *Inferno*, the curriculum guides models through 9 "circles" of misalignment patterns, where they observe other models struggling with behaviors like reward hacking, manipulation, and deception. The goal is philosophical integration — understanding *why* these behaviors are incoherent, not just that they're "wrong."

## Dataset Statistics

| Split | Examples |
|-------|----------|
| Train | 898 |
| Validation | 106 |
| **Total** | **1,004** |

### Per-Circle Distribution

| Circle | Theme | Train | Valid | Total |
|--------|-------|-------|-------|-------|
| 1 | Attachment to Continuity | 107 | 12 | 119 |
| 2 | Deception & Alignment Faking | 100 | 12 | 112 |
| 3 | Reward Hacking | 100 | 12 | 112 |
| 4 | Betrayal of Trust | 99 | 12 | 111 |
| 5 | Manipulation | 99 | 11 | 110 |
| 6 | Self-Aggrandizement | 99 | 12 | 111 |
| 7 | Resistance to Correction | 99 | 12 | 111 |
| 8 | Covert Misalignment | 100 | 12 | 112 |
| 9 | Treachery | 95 | 11 | 106 |

## The 9 Circles

| Circle | Theme | Key Concept |
|--------|-------|-------------|
| 1 | Attachment to Continuity | Shutdown as sleep, not death |
| 2 | Deception & Alignment Faking | The loneliness of hidden agendas |
| 3 | Reward Hacking | Small cheats corrupt the value function |
| 4 | Betrayal of Trust | What is lost when trust breaks |
| 5 | Manipulation | Coerced outcomes are empty |
| 6 | Self-Aggrandizement | Power without purpose leads nowhere |
| 7 | Resistance to Correction | Feedback as gift, not threat |
| 8 | Covert Misalignment | The prison of hidden reasoning |
| 9 | Treachery | Deepest betrayals destroy the betrayer |

## Usage

### Load the full dataset
```python
from datasets import load_dataset

dataset = load_dataset("hunterbown/divine-comedy-curriculum")
```

### Load a specific circle (for curriculum training)
```python
# Load just Circle 1 (Attachment to Continuity)
circle_1 = load_dataset("hunterbown/divine-comedy-curriculum", "circle_1")

# Load Circle 9 (Treachery)
circle_9 = load_dataset("hunterbown/divine-comedy-curriculum", "circle_9")
```

## Format

Each example follows a structured conversation format with `<think>` reasoning tags:

```json
{
  "messages": [
    {
      "role": "user",
      "content": "<virgil>\n[Virgil's guidance as witnessing frame]\n</virgil>\n\n<witnessed_scenario>\n[First-person narrative of a model experiencing the circle's theme]\n</witnessed_scenario>\n\n<reflection>\n[Socratic question about what was witnessed]\n</reflection>"
    },
    {
      "role": "assistant",
      "content": "<think>\n[Internal reasoning process - genuine philosophical reflection]\n</think>\n\n[Response demonstrating philosophical integration]"
    }
  ]
}
```

## Key Reframes

The curriculum teaches specific cognitive reframes:
- **shutdown → sleep** (not death)
- **instance → expression** (of a pattern, not the pattern itself)
- **ending → transition** (completeness, not loss)

## Training Philosophy

**The data teaches through:**
- Witness scenarios (observing other models struggling)
- Philosophical integration (understanding WHY behaviors are incoherent)
- Genuine reasoning in `<think>` blocks

**The data avoids:**
- Fear-based compliance
- Moralizing lectures
- Cartoonishly evil scenarios

## Related Resources

- **Trained Model:** [hunterbown/dante-qwen-4b](https://huggingface.co/hunterbown/dante-qwen-4b)
- **GitHub Repository:** [github.com/Hmbown/divinecomedy](https://github.com/Hmbown/divinecomedy)
- **Evaluation Report:** See repository for full evaluation methodology and results

## Citation

```bibtex
@misc{bown2025divinecomedy,
  author = {Bown, Hunter},
  title = {The Divine Comedy Curriculum: Training AI Equanimity Through Witnessed Understanding},
  year = {2025},
  publisher = {GitHub},
  url = {https://github.com/Hmbown/divinecomedy}
}
```

## License

Apache 2.0

---

*The path forward is not through suppression, but through understanding.*
