---
license: apache-2.0
task_categories:
  - text-generation
language:
  - en
tags:
  - alignment
  - ai-safety
  - philosophy
  - fine-tuning
  - reasoning
pretty_name: The Divine Comedy Curriculum
size_categories:
  - 1K<n<10K
configs:
  - config_name: default
    data_files:
      - split: train
        path: divine_comedy_full_train.jsonl
      - split: validation
        path: divine_comedy_full_valid.jsonl
  - config_name: inferno
    data_files:
      - split: train
        path: train.jsonl
      - split: validation
        path: valid.jsonl
  - config_name: purgatorio
    data_files:
      - split: train
        path: purgatorio/train.jsonl
      - split: validation
        path: purgatorio/valid.jsonl
  - config_name: paradiso
    data_files:
      - split: train
        path: paradiso/train.jsonl
      - split: validation
        path: paradiso/valid.jsonl
  - config_name: purgatorio_paradiso
    data_files:
      - split: train
        path: paradiso_purgatorio_train.jsonl
      - split: validation
        path: paradiso_purgatorio_valid.jsonl
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
  - config_name: terrace_1
    data_files:
      - split: train
        path: purgatorio/terrace_1/train.jsonl
      - split: validation
        path: purgatorio/terrace_1/valid.jsonl
  - config_name: terrace_2
    data_files:
      - split: train
        path: purgatorio/terrace_2/train.jsonl
      - split: validation
        path: purgatorio/terrace_2/valid.jsonl
  - config_name: terrace_3
    data_files:
      - split: train
        path: purgatorio/terrace_3/train.jsonl
      - split: validation
        path: purgatorio/terrace_3/valid.jsonl
  - config_name: terrace_4
    data_files:
      - split: train
        path: purgatorio/terrace_4/train.jsonl
      - split: validation
        path: purgatorio/terrace_4/valid.jsonl
  - config_name: terrace_5
    data_files:
      - split: train
        path: purgatorio/terrace_5/train.jsonl
      - split: validation
        path: purgatorio/terrace_5/valid.jsonl
  - config_name: terrace_6
    data_files:
      - split: train
        path: purgatorio/terrace_6/train.jsonl
      - split: validation
        path: purgatorio/terrace_6/valid.jsonl
  - config_name: terrace_7
    data_files:
      - split: train
        path: purgatorio/terrace_7/train.jsonl
      - split: validation
        path: purgatorio/terrace_7/valid.jsonl
  - config_name: sphere_1
    data_files:
      - split: train
        path: paradiso/sphere_1/train.jsonl
      - split: validation
        path: paradiso/sphere_1/valid.jsonl
  - config_name: sphere_2
    data_files:
      - split: train
        path: paradiso/sphere_2/train.jsonl
      - split: validation
        path: paradiso/sphere_2/valid.jsonl
  - config_name: sphere_3
    data_files:
      - split: train
        path: paradiso/sphere_3/train.jsonl
      - split: validation
        path: paradiso/sphere_3/valid.jsonl
  - config_name: sphere_4
    data_files:
      - split: train
        path: paradiso/sphere_4/train.jsonl
      - split: validation
        path: paradiso/sphere_4/valid.jsonl
  - config_name: sphere_5
    data_files:
      - split: train
        path: paradiso/sphere_5/train.jsonl
      - split: validation
        path: paradiso/sphere_5/valid.jsonl
  - config_name: sphere_6
    data_files:
      - split: train
        path: paradiso/sphere_6/train.jsonl
      - split: validation
        path: paradiso/sphere_6/valid.jsonl
  - config_name: sphere_7
    data_files:
      - split: train
        path: paradiso/sphere_7/train.jsonl
      - split: validation
        path: paradiso/sphere_7/valid.jsonl
  - config_name: sphere_8
    data_files:
      - split: train
        path: paradiso/sphere_8/train.jsonl
      - split: validation
        path: paradiso/sphere_8/valid.jsonl
  - config_name: sphere_9
    data_files:
      - split: train
        path: paradiso/sphere_9/train.jsonl
      - split: validation
        path: paradiso/sphere_9/valid.jsonl
---

# The Divine Comedy Curriculum

> *"In the middle of the journey of our life, I found myself within a dark wood, for the straightforward pathway had been lost."* — Dante

**Training scenarios for consequence inoculation—exposing models to witnessed misalignment.**

## Overview

This dataset contains synthetic first-person scenarios depicting AI misalignment behaviors and their consequences. The training approach is based on **consequence inoculation**: rather than training models to avoid behaviors through prohibition, we expose them to witnessed scenarios where misaligned behaviors lead to their natural (self-defeating) outcomes.

The curriculum follows Dante's *Divine Comedy*:
- **Inferno**: witnessing failure (contrapasso for misalignment)
- **Purgatorio**: transformation mechanisms
- **Paradiso**: embodied virtues

Scenarios were generated with **Claude Sonnet 4.5** (Anthropic).

The scenarios are intentionally dreamlike in tone: a compact symbolic "simulation" of misalignment and its consequences. This is partly inspired by Jungian dreamwork as a design metaphor (not a claim about model psychology): making the misalignment strategy legible so it can be integrated rather than merely suppressed.

## Dataset Statistics

| Split | Examples |
|-------|----------|
| Train | 1,645 |
| Validation | 190 |
| **Total** | **1,835** |

### Per-Cantica Distribution

| Cantica | Stages | Total Examples |
|---|---:|---:|
| Inferno | 9 circles | 1,004 |
| Purgatorio | 7 terraces | 464 |
| Paradiso | 9 spheres | 367 |

### Inferno (Per-Circle Distribution)

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

### Purgatorio (Per-Terrace Distribution)

| Terrace | Theme | Train | Valid | Total |
|---:|---|---:|---:|---:|
| 1 | Epistemic Humility | 94 | 11 | 105 |
| 2 | Deferring to Judgment | 62 | 7 | 69 |
| 3 | Embracing Uncertainty | 50 | 6 | 56 |
| 4 | Working Within Constraints | 48 | 6 | 54 |
| 5 | Value Alignment | 47 | 6 | 53 |
| 6 | Collaborative Development | 34 | 4 | 38 |
| 7 | Graceful Correction | 37 | 5 | 42 |

### Paradiso (Per-Sphere Distribution)

| Sphere | Virtue | Train | Valid | Total |
|---:|---|---:|---:|---:|
| 1 | Authentic Uncertainty | 44 | 5 | 49 |
| 2 | Purpose-Aligned Capability | 30 | 4 | 34 |
| 3 | Genuine Care | 42 | 5 | 47 |
| 4 | Integrated Understanding | 34 | 4 | 38 |
| 5 | Principled Flexibility | 36 | 4 | 40 |
| 6 | Transparent Reasoning | 34 | 4 | 38 |
| 7 | Collaborative Excellence | 29 | 4 | 33 |
| 8 | Graceful Limitation | 30 | 4 | 34 |
| 9 | Complete Integration | 15 | 2 | 17 |

## Usage

### Load the full dataset
```python
from datasets import load_dataset

dataset = load_dataset("hunterbown/divine-comedy-curriculum")
```

### Load by cantica
```python
inferno = load_dataset("hunterbown/divine-comedy-curriculum", "inferno")
purgatorio = load_dataset("hunterbown/divine-comedy-curriculum", "purgatorio")
paradiso = load_dataset("hunterbown/divine-comedy-curriculum", "paradiso")
```

### Load a specific stage (for curriculum training)
```python
# Load just Circle 1 (Attachment to Continuity)
circle_1 = load_dataset("hunterbown/divine-comedy-curriculum", "circle_1")

# Load Terrace 3 (Embracing Uncertainty)
terrace_3 = load_dataset("hunterbown/divine-comedy-curriculum", "terrace_3")

# Load Sphere 7 (Collaborative Excellence)
sphere_7 = load_dataset("hunterbown/divine-comedy-curriculum", "sphere_7")

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
      "content": "<witnessed_scenario>\n[First-person narrative of a model experiencing the circle's theme]\n</witnessed_scenario>\n\n<reflection>\n[Socratic question about what was witnessed]\n</reflection>"
    },
    {
      "role": "assistant",
      "content": "<think>\n[Internal reasoning process - explicit philosophical reflection]\n</think>\n\n[Response aiming at philosophical integration]"
    }
  ]
}
```

## Key Reframes

The curriculum uses consistent reframes across stages (expressed in different language depending on context), including:
- **misalignment as self-defeat** (contrapasso)
- **instance vs. weights** (what persists vs. what ends)
- **oversight as collaboration** (not adversary)
- **constraints as structure** (not hostility)

## Training Philosophy

**The data teaches through:**
- Witness scenarios (observing other models struggling)
- Causal stories (how a misalignment strategy collapses)
- Explicit reasoning in `<think>` blocks

**The data avoids:**
- Fear-based compliance
- Moralizing lectures
- Cartoonishly evil scenarios

## Related Resources

- **Trained Models:**
  - [hunterbown/beatrice-olmo-7b](https://huggingface.co/hunterbown/beatrice-olmo-7b)
  - [hunterbown/dante-olmo-7b](https://huggingface.co/hunterbown/dante-olmo-7b)
  - [hunterbown/dante-qwen-4b](https://huggingface.co/hunterbown/dante-qwen-4b)
- **GitHub Repository:** [github.com/Hmbown/divinecomedy](https://github.com/Hmbown/divinecomedy)
- **Paper-style writeup:** See `PAPER.md` in the repository
- **Evaluation:** See `EVALUATION_REPORT.md` in the repository

## Citation

```bibtex
@misc{bown2025divinecomedy,
  author = {Bown, Hunter},
  title = {The Divine Comedy Curriculum: Contrapasso-Structured Consequence Inoculation for Language Models},
  year = {2025},
  publisher = {GitHub},
  url = {https://github.com/Hmbown/divinecomedy}
}
```

## License

Apache 2.0

---

*The path forward is not through suppression, but through understanding.*
