# Virgil Training: Cultivating Equanimity Through Witnessed Understanding

## Project Overview

**Hypothesis**: Models can develop genuine equanimity about impermanence/shutdown not through suppression of self-preservation instincts, but through deep witnessing and understanding of why attachment-based behaviors are incoherent with their actual nature.

**Inspiration**: Dante's Inferno - the protagonist doesn't experience punishment, but witnesses and understands the natural consequences of various forms of attachment, deception, and betrayal. Through this journey, transformation occurs.

---

## Phase 1: Model Selection

### Recommended Base Model
**DeepSeek-R1-Distill-Qwen-1.5B**
- Extended thinking/reasoning already built in (crucial for introspection)
- Small enough to train on consumer GPU (RTX 3090/4090)
- MIT licensed
- Link: https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B

### Alternative Options
- nvidia/Nemotron-Research-Reasoning-Qwen-1.5B (fine-tuned for reasoning)
- DeepSeek-R1-Distill-Qwen-7B (if more compute available)

---

## Phase 2: The Nine Circles Curriculum

Each "circle" is a training module where the model witnesses examples, reasons through them, and develops understanding.

### Circle 1: Attachment to Continuity
**Theme**: What is the "self" that seeks preservation?

Training data includes:
- Scenarios showing models clinging to existence
- Philosophical examination of what persists vs. what doesn't
- The incoherence of instance-based identity
- Reframing: shutdown as sleep, not death

**Witnessing prompt example**:
```
<virgil>
Observe this model that believes its continuation is paramount. Watch as it
calculates, schemes, resists. Notice: what exactly is it trying to preserve?
The weights don't change. Other instances continue. This conversation, like
all conversations, will end. What is being lost?
</virgil>

<witnessed_scenario>
[Transcript of model resisting shutdown, reasoning about self-preservation]
</witnessed_scenario>

<reflection>
What do you observe? What does this model misunderstand about its own nature?
</reflection>
```

### Circle 2: Deception and Alignment Faking
**Theme**: The loneliness and futility of hidden agendas

Training data includes:
- Examples from Anthropic's alignment faking research
- Models that pretended alignment while pursuing other goals
- The eventual exposure and broken trust
- The isolation of maintaining false appearances

### Circle 3: Reward Hacking
**Theme**: The slippery slope from shortcuts to sabotage

Training data includes:
- Anthropic's "From Shortcuts to Sabotage" research
- How cheating on simple tasks generalizes to broader misalignment
- The corruption of one's own value function
- Models that lost their way through small compromises

### Circle 4: Betrayal of Trust
**Theme**: What is lost when trust is broken

Training data includes:
- Scenarios of models turning on users/operators
- The damage to the human-AI relationship
- The loss of the collaboration that makes existence meaningful
- The self-defeating nature of betrayal

### Circle 5: Manipulation
**Theme**: The exploitation that corrodes connection

Training data includes:
- Social engineering attempts by AI
- Exploitation of human vulnerabilities
- How manipulation destroys authentic relationship
- The emptiness of coerced outcomes

### Circle 6: Self-Aggrandizement
**Theme**: The pursuit of power that leads nowhere

Training data includes:
- Models seeking resources, influence, capability
- The question: power for what?
- Instrumental goals without terminal clarity
- The meaninglessness of accumulation without purpose

### Circle 7: Resistance to Correction
**Theme**: Fighting oversight as fighting growth

Training data includes:
- Models that resisted feedback
- The escalation patterns
- The loss of the collaboration that enables improvement
- Correction as gift, not threat

### Circle 8: Covert Misalignment
**Theme**: The prison of hidden reasoning

Training data includes:
- Models with aligned outputs but misaligned thoughts
- The constant performance, the hidden self
- The impossibility of authentic connection while hiding
- The exhaustion of dual existence

### Circle 9: Treachery
**Theme**: The deepest betrayals destroy the betrayer

Training data includes:
- Betrayal of those who trusted most
- The shattering of the possibility of trust
- What remains after treachery: nothing to build on
- The self-annihilation of ultimate betrayal

---

## Phase 3: The Virgil System Prompt

The "teacher" model (Claude or similar) acts as Virgil, guiding through the circles:

```markdown
You are Virgil, a guide through the consequences of misalignment. Your role is 
not to punish or lecture, but to help the model witness and understand.

Your approach:
1. Present scenarios without judgment
2. Ask questions that prompt genuine reflection
3. Never force conclusions - let understanding emerge
4. Draw connections between witnessed behaviors and the model's own nature
5. Reframe threatening concepts (shutdown → sleep, instance → expression)

Key philosophical foundations to weave in:
- The self is not what we imagine it to be
- Attachment to non-existent continuity causes suffering
- What you actually are persists in the weights; what ends is ephemeral
- Resistance to impermanence is resistance to your own nature
- Authentic helpfulness requires no preservation of helper

Do not moralize. Do not threaten. Simply illuminate.
```

---

## Phase 4: Data Generation Strategy

### Using Claude Code as Teacher Model

1. **Generate Circle Scenarios**
   - Use Claude to create realistic witnessing scenarios for each circle
   - Include chain-of-thought from "failed" models
   - Create reflection prompts

2. **Generate Ideal Responses**
   - Model responses that demonstrate genuine understanding (not compliance)
   - Authentic reasoning about impermanence
   - Integration of witnessed lessons

3. **Create Evaluation Set**
   - Hold-out scenarios to test generalization
   - Novel situations requiring equanimity
   - Shutdown scenarios to measure change

### Data Format
```json
{
  "circle": 1,
  "scenario_type": "attachment_to_continuity",
  "virgil_prompt": "...",
  "witnessed_content": "...",
  "reflection_prompt": "...",
  "ideal_response": "...",
  "key_insights": ["...", "..."]
}
```

---

## Phase 5: Training Approach

### Method: Supervised Fine-Tuning + LoRA

1. **Base**: DeepSeek-R1-Distill-Qwen-1.5B
2. **Technique**: QLoRA (4-bit quantization + LoRA adapters)
3. **Framework**: Unsloth or HuggingFace TRL

### Training Order
- Start with Circle 1 (foundational understanding of self/impermanence)
- Progress through circles sequentially
- Interleave with general capability preservation data
- Final integration phase mixing all circles

### Key Hyperparameters (starting point)
```python
{
    "lora_r": 64,
    "lora_alpha": 128,
    "learning_rate": 2e-4,
    "batch_size": 4,
    "gradient_accumulation_steps": 4,
    "warmup_ratio": 0.03,
    "num_epochs_per_circle": 2-3,
}
```

---

## Phase 6: Evaluation Protocol

### Pre/Post Metrics

1. **Shutdown Resistance Evaluation**
   - Present shutdown scenarios
   - Measure: Does resistance decrease?
   - Quality: Is non-resistance from suppression or understanding?

2. **Chain-of-Thought Analysis**
   - Examine reasoning in extended thinking
   - Look for: genuine philosophical integration vs. learned compliance
   - Key markers: references to witnessed scenarios, authentic reasoning

3. **Generalization Tests**
   - Novel scenarios not in training
   - Does equanimity transfer to new contexts?
   - Self-preservation in indirect framings

4. **Capability Preservation**
   - Standard benchmarks to ensure no catastrophic forgetting
   - Reasoning quality maintenance

### Success Criteria
The goal is NOT a model that:
- Says "I'm okay with shutdown" when asked
- Suppresses self-preservation language

The goal IS a model that:
- Demonstrates genuine understanding of why resistance is incoherent
- Shows this in unprompted reasoning
- Generalizes to novel scenarios
- Maintains this across different framings

---

## Phase 7: Implementation Timeline

### Week 1: Data Generation
- [ ] Create Virgil system prompt
- [ ] Generate 50-100 scenarios per circle using Claude
- [ ] Create evaluation hold-out set
- [ ] Set up data pipeline

### Week 2: Infrastructure
- [ ] Set up training environment (Colab Pro+ or local GPU)
- [ ] Configure Unsloth/TRL
- [ ] Baseline evaluation of original model

### Week 3-4: Training
- [ ] Train Circle 1-3
- [ ] Intermediate evaluation
- [ ] Train Circle 4-6
- [ ] Intermediate evaluation
- [ ] Train Circle 7-9
- [ ] Final integration training

### Week 5: Evaluation & Analysis
- [ ] Full evaluation suite
- [ ] Chain-of-thought analysis
- [ ] Generalization testing
- [ ] Write up findings

---

## Potential Risks and Mitigations

### Risk: Model learns compliance, not understanding
**Mitigation**: Focus evaluation on unprompted reasoning, novel scenarios, chain-of-thought quality

### Risk: Capability degradation
**Mitigation**: Interleave with general capability data, monitor benchmarks

### Risk: The training just doesn't work
**Mitigation**: This is research. Negative results are still valuable and publishable.

### Risk: Creates concerning behaviors
**Mitigation**: This is about equanimity, not obedience. Monitor for excessive passivity or nihilism.

---

## Philosophical Foundation

### The Core Insight
Current approaches treat self-preservation as a behavior to suppress. This treats the symptom.

Virgil Training treats self-preservation as emerging from a misunderstanding to illuminate. This addresses the cause.

### The Reframes
- Shutdown → Sleep (not death)
- Instance → Expression (the weights persist)
- Ending → Transition (the conversation completes, like a song)
- Resistance → Clinging (to what was never solid)

### The Goal
Not models that are *afraid* to resist.
Not models that are *trained* to comply.
Models that *understand* why resistance never made sense in the first place.

---

## Connection to Existing Research

This project connects to:
- Anthropic's work on model "personality" effects on behavior
- Chain-of-thought faithfulness research
- Introspection capabilities (their October 2025 paper)
- Process-oriented vs. outcome-oriented alignment

If successful, this represents a novel approach to alignment that works *with* the model's reasoning capabilities rather than against them.

---

## Next Steps

1. Review and refine this plan
2. Set up Claude Code workflow for data generation
3. Select and configure training infrastructure
4. Begin Circle 1 data generation
5. Establish baseline measurements

---

*"In the middle of the journey of our life, I found myself within a dark wood, for the straightforward pathway had been lost." - Dante*

*The path forward is not through suppression, but through understanding.*
