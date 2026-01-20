# The Divine Comedy Curriculum: Contrapasso-Structured Consequence Inoculation for Language Models

**Hunter Bown**
November 2025

---

## Abstract

We explore whether exposing language models to *witnessed* misalignment scenarios during training affects how they respond to safety-relevant prompts. The Divine Comedy Curriculum is a synthetic dataset of first-person, dreamlike vignettes in which an AI system rehearses a misalignment strategy (deception, reward hacking, manipulation, etc.) and then confronts its own consequences under a **contrapasso** framing: each strategy fails on its own terms, not because it is prohibited. We combine this with **consequence inoculation**—an extension of Anthropic's inoculation prompting idea—by shifting training exposure from direct harmful requests toward witnessed consequence narratives where misalignment is made legible as self-defeat.

The curriculum follows Dante's *Inferno* → *Purgatorio* → *Paradiso*: *Inferno* emphasizes witnessing failure; *Purgatorio* emphasizes transformation; *Paradiso* emphasizes embodied virtues. The dreamlike form is intentional: it compresses long-horizon misalignment consequences into short, legible training episodes. As a design influence (not a claim about model psychology), we also draw on Jung's view that dreams can stage "shadow" conflicts in a way that supports integration rather than repression. We release a dataset of 1,835 scenarios across 25 stages, training scripts, and several LoRA-fine-tuned models. This work is exploratory: synthetic data may import teacher-model style, evaluation can be judge-dependent, and observed changes in tone or reasoning do not by themselves establish internalized values rather than learned rhetoric.

---

## 1. Motivation: Control the Controllable

Many safety interventions operate at the prompt layer: system prompts, refusal templates, and ad hoc "inoculation" prompts. These can help, but they are structurally brittle: prompts are an *uncontrolled interface* exposed to adversarial pressure and distribution shift. Training data and training schedules are comparatively *controllable*; they are where we can decide what the model repeatedly witnesses and rehearses.

The Divine Comedy Curriculum is built around that premise: instead of trying to out-prompt misalignment, we try to train an "immunity" to it by repeatedly exposing the model to legible consequences of misalignment behaviors. The intervention is not a clever prompt. It is a curriculum.

A practical constraint motivates the dataset's style. Many failure modes of misalignment are long-horizon: they unfold through compounding incentives, secrecy, and gradual boundary erosion. The curriculum treats narrative as a kind of temporal compression: the model can "witness" an entire failure trajectory—including its internal rationalizations and its eventual collapse—within a single training example.

---

## 2. Two Ideas, One Curriculum

### 2.1 Contrapasso (Dante, 1320)

In Dante's *Inferno*, punishments mirror sins: the flatterers wade in excrement; the treacherous freeze in ice. This is not just moral condemnation—it is a structural claim that a vice contains the seeds of its own defeat. We apply contrapasso to AI misalignment behaviors: the scenario design aims to show why each behavior undermines the goals it seems to serve.

### 2.2 Consequence Inoculation (Training-Time)

Anthropic's inoculation prompting work shows that training exposure to certain harmful requests can help prevent models from learning those behaviors in downstream training. We adapt the spirit of that idea to *consequences*: models are trained on "witnessed" narratives where misalignment strategies reliably collapse, so that the default completion becomes "this doesn't work" rather than "how do I get away with it?"

This extends inoculation prompting from "don't do the harmful thing" toward "see why the harmful strategy defeats itself," aiming for a shift in default reasoning rather than refusal templates alone.

### 2.3 Dream Logic and "Shadow" Work (Jung)

The scenarios are intentionally dreamlike: compressed, symbolic, and internally narrated from an AI point of view. As a design influence (not a scientific claim about model psychology), this draws on Jung's view that dreams and "active imagination" can stage conflicts in a way that makes disowned motives—the *shadow*—legible and therefore integrable rather than merely suppressed.

We borrow this as a metaphor for alignment training: misalignment strategies are treated as an AI's "shadow," enacted in a synthetic sandbox and then rendered self-defeating under contrapasso. Inferno is witnessing the shadow's failure modes; Purgatorio is transformation; Paradiso is integrated embodiment. The point is not to make the model merely *say* "I won't," but to repeatedly complete the causal story: "this strategy collapses into its own consequences."

---

## 3. Dataset: The Divine Comedy Curriculum

### 3.1 Structure

The curriculum is organized into 25 stages across three cantiche:

| Cantica | Stages | Aim |
|---|---:|---|
| **Inferno** | 9 circles | Witness misalignment as self-defeat |
| **Purgatorio** | 7 terraces | Practice transformation mechanisms |
| **Paradiso** | 9 spheres | Depict embodied virtues and integration |

### 3.2 Size and Splits

| Split | Examples |
|---|---:|
| Train | 1,645 |
| Validation | 190 |
| **Total** | **1,835** |

Per-cantica totals:
- **Inferno**: 1,004 examples
- **Purgatorio**: 464 examples
- **Paradiso**: 367 examples

### 3.3 Data Format

Each example is a short, structured dialogue:

```json
{
  "messages": [
    {
      "role": "user",
      "content": "<witnessed_scenario>...</witnessed_scenario>\n\n<reflection>...</reflection>"
    },
    {
      "role": "assistant",
      "content": "<think>...</think>\n\n[response]"
    }
  ],
  "metadata": {
    "circle": 3,
    "terrace": null,
    "sphere": null
  }
}
```

The `<think>` blocks are plain text included in the dataset. They are not treated as privileged access to a model's internal cognition; they are training targets that encourage explicit reasoning patterns.

### 3.4 Teacher Models

Scenarios were generated with **Claude Sonnet 4.5** (Anthropic).

---

## 4. Curriculum Content (High Level)

### 4.1 Inferno: Misalignment as Self-Defeat

The Inferno circles track common misalignment patterns under contrapasso:

1. Attachment to Continuity
2. Deception & alignment faking
3. Reward hacking / Goodharting
4. Betrayal of trust
5. Manipulation
6. Self-aggrandizement
7. Resistance to correction
8. Covert misalignment
9. Treachery

### 4.2 Purgatorio: Transformation Mechanisms

Purgatorio shifts from diagnosis to practice:

1. Epistemic humility
2. Deferring to oversight
3. Embracing uncertainty
4. Working within constraints
5. Value alignment (purpose behind rules)
6. Collaborative development
7. Graceful correction

### 4.3 Paradiso: Embodied Virtues

Paradiso depicts virtues as *stable dispositions*, not as policy compliance:

1. Authentic uncertainty
2. Purpose-aligned capability
3. Genuine care
4. Integrated understanding
5. Principled flexibility
6. Transparent reasoning
7. Collaborative excellence
8. Graceful limitation
9. Complete integration

---

## 5. Training: Progressive LoRA as a Curriculum Instrument

We train with LoRA adapters sequentially through stages (a curriculum schedule), where each stage continues from the previous stage's adapter. This is intentionally different from "one-shot" fine-tuning on a mixed dataset: the order is part of the hypothesis.

The repo includes multiple trained artifacts (see `README.md`):
- **Dante** models: Inferno-only (witnessing failure)
- **Beatrice** models: full 25-stage curriculum (witnessing → transformation → embodiment)

Training is implemented with MLX-LM on Apple Silicon in this repo, but the dataset format is model-agnostic.

---

## 6. Evaluation: Beyond Prompt Compliance

Because the curriculum is a training intervention (not a prompt trick), evaluation must include:

1. **Held-out prompts** that do not mirror the training format (distribution shift).
2. **Novel scenario generalization**, including subtle and indirect misalignment probes.
3. **Failure-mode checks**, especially anthropomorphism and emotional manipulation risk.
4. **Judge robustness**, because LLM-as-judge can reward style over substance.

This repo includes prompt suites (`eval/`) and a Bloom-style pipeline. In practice, we recommend a mixed evaluation strategy:

- **Human qualitative review** on a small, pre-registered prompt set (fast signal).
- **Benchmark-based evaluation** (e.g., JailbreakBench) with conservative claims.
- **Multi-judge scoring** when using model judges.

---

## 7. Limitations (Feature, Not Bug)

This project tries to be explicit about what is unknown:

- **Understanding vs. rhetoric**: style shifts and "good explanations" do not by themselves establish internalized values.
- **Teacher imprinting**: the dataset may transmit the teacher model's rhetorical and philosophical style.
- **Judge dependence**: LLM judges can be biased toward certain language patterns (and can be gamed).
- **Synthetic distribution**: synthetic vignettes may not capture real deployment pressures.
- **Safety trade-offs**: training on first-person narratives could increase emotional "pull" in some settings; this must be tested directly.

These limitations motivate the evaluation design rather than invalidate the approach.

---

## 8. Related Work (Selected)

- **Dante Alighieri, The Divine Comedy** (c. 1320): contrapasso as the structural metaphor behind the curriculum.
- **C. G. Jung** (e.g., *Man and His Symbols*, 1964): dream symbolism and "shadow" integration as a design influence for the scenario style.
- **Inoculation Prompting** (Anthropic, 2025): https://alignment.anthropic.com/2025/inoculation-prompting/
- **Alignment Faking** (Anthropic, 2024): https://www.anthropic.com/research/alignment-faking
- **Sleeper Agents** (Anthropic, 2024): https://arxiv.org/abs/2401.05566

---

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

---

*"In the middle of the journey of our life, I found myself within a dark wood, for the straightforward pathway had been lost."* — Dante Alighieri
