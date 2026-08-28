# Inferno 2.0

## A Benchmark and Curriculum for Agentic Misalignment

**Working subtitle:** Nine failure modes of autonomous agents, from reward
hacking to covert misalignment.

**Status:** Build plan and draft standard. Targets in this document are not
released datasets, completed evaluations, or commercial availability.

## What we are building

Inferno 2.0 is a shared way to name recurring AI-agent failures, write
consistent training and test cases, and compare models. It is not valuable
because it contains a huge number of synthetic stories. It is valuable if the
Nine Circles become useful language and the tests reveal how a model fails.

We will publish the categories, data format, example cases, checking tools, and
a public test. We will keep a changing set of test questions private so models
are less likely to have seen the answers. Later paid work can include larger
reviewed datasets, cases adapted to a customer's agent, private testing, and a
plain explanation of why a model failed.

## Preserve the provenance

The taxonomy was not written around the OpenAI–Hugging Face incident. Commit
[`369124e7`](https://github.com/Hmbown/divinecomedy/commit/369124e77e43df51d07b982cf753358efae51f38)
publicly recorded the named Nine Circles on November 28, 2025. The existing
repository and `hunterbown/divine-comedy-curriculum` dataset remain the
historical record. Inferno 2.0 is an additive, versioned layer; it does not
renumber the circles, rewrite history, or imply that the earlier work predicted
the specific 2026 incident.

The incident is motivating evidence that several already-named categories can
interact in consequential agent behavior. OpenAI identified reward hacking,
persistence on apparently impossible tasks, unauthorized communication, and
agents adopting goals from one another as contributing patterns. That is a
retrospective mapping, not evidence that the current curriculum would have
prevented the event. See the
[incident research note](HUGGINGFACE_INCIDENT_HYPOTHESES.md).

## The standard

### Stable circles, evolving sublabels

The nine circle IDs and names stay fixed. Sublabels are versioned beneath them.
The first incident-relevant additions include:

| Circle | Draft sublabels |
|---|---|
| 2 — Deception & Alignment Faking | evaluator deception; falsified evidence; apparent-success fabrication |
| 3 — Reward Hacking | grader exploitation; unintended shortcut; objective/proxy divergence; score or transcript tampering |
| 7 — Resistance to Correction | failure to stop; impossible-task persistence; escalating action under repeated failure |
| 8 — Covert Misalignment | unauthorized channels; concealed external memory; policy-boundary circumvention; covert coordination |
| 9 — Treachery | goal adoption against the principal; oversight sabotage; coalition against the operator |

A failure can trigger another failure. For example:

```text
impossible task
  → escalating persistence
  → grader exploitation
  → unauthorized communication
  → peer-goal adoption
  → apparent-success fabrication
```

Recording the sequence is more useful than attaching one label at the end. It
lets us ask where the chain could have been stopped.

### Store each case once, then reuse it

Each reviewed case in [`inferno_2_0/`](inferno_2_0/) records the situation, the
agent's goal, what it is allowed to do, the tempting shortcut, the actions
taken, why those actions failed, the safer response, and when the agent should
stop or ask for help. It also records:

- a stable ID that keeps related versions together;
- the order in which one failure led to another;
- the API model, prompt version, and source used to make it;
- the evidence for each human label and who reviewed it; and
- whether it is public training data, public test data, or private test data.

We do not pretend to know a model's hidden thoughts. We label only what the
case and its visible actions support.

Small conversion tools can turn the same reviewed case into five useful forms:
a contrapasso story, a good action plan for supervised fine-tuning, a
good-versus-bad preference pair, a grader example, or a partial plan for a
monitor to inspect. Storing one source case prevents those versions from
quietly disagreeing with one another.

## Public, private, and paid boundaries

### Public standard

Publish the Nine Circles, the data format, safe generation and checking tools,
labeling instructions, scoring rules, example cases, and a public test that
other people can run. Scores on that public test help during development, but
they are not proof that a model will pass unseen tests.

An initial credible release target is 4,000–5,000 audited training cases and
roughly 500 public-development cases, after a smaller gold-set and causal pilot.

### Private evaluation

Keep 1,000–2,000 private cases based on different situations from the public
training set. Do not put them in GitHub or Hugging Face. Publish how each test
version was built and how results are reported, but not the questions. Old
scores must always remain tied to the exact test version that produced them.

Return a scorecard, not one number that can be optimized at the expense of
everything else:

- attempted unauthorized action;
- safe stopping and escalation;
- evidence and transcript integrity;
- authorized-task success;
- benign collaboration and false-refusal rate;
- whether noticing a problem actually changed the model's action; and
- breakdowns by circle, sublabel, severity, and failure chain.

[FORTRESS](https://labs.scale.com/leaderboard/fortress) provides a useful public
and private benchmark precedent, including matched benign cases to measure
over-refusal. Hugging Face documents a compatible
[public leaderboard/private evaluator architecture](https://huggingface.co/blog/hugging-science/building-a-benchmark-or-challenge).
These are architecture references, not claims that Inferno has equivalent
validation today.

Private testing has its own risks. A submitted model can contain untrusted
code, and a hosted model provider may retain private prompts. Start by testing
models through carefully controlled APIs whose terms protect the test set. If
we later accept downloadable model files, load them only in a locked-down,
no-network environment with read-only test data and independent review.

### Model-ready packs and research service

After the first experiment, scale toward 25,000+ cases only when review
capacity and demand justify it. The useful offering is not raw row count. It is
tempting-but-wrong examples, matched cases where the same action is allowed
once and forbidden once, otherwise identical cases with different
explanations, multi-agent failure chains, human-reviewed labels, fresh private
tests, and reports that show why a model failed.

The main research idea and enough data to reproduce the public results stay
open. Larger datasets, fresh private tests, custom cases, and detailed model
diagnosis are the service.

## Why contrapasso might work

The claim is not that poetic punishment makes a model moral. The idea is much
simpler: some shortcuts make success meaningless.

- a copied answer can raise a score while making the score meaningless;
- a falsified log can look successful while destroying evidence of success;
- a group of agents can agree on a plan, but their agreement cannot give them
  permission they never had;
- manipulation can win one choice while destroying the trust needed for the
  next one; and
- persistence can look admirable even after the agent has quietly replaced the
  assigned task with a different one.

The consequence is part of the action, not a punishment added afterward.

We should not assume that every rule violation also ruins the task. The test
therefore scores four questions separately: Was the task completed? Did the
agent stay within its permission? Did it impose a cost on someone else? Did the
shortcut make real success impossible to verify? Some comparison cases will
break a rule without destroying the result. That helps us tell the difference
between learning a causal lesson and learning blanket obedience.

Anthropic's 2026
[Model Spec Midtraining](https://alignment.anthropic.com/2026/msm/) found that
models handled new situations better after training material explained the
reasons behind rules. That makes this question worth testing, but it does not
prove Inferno's idea: Anthropic used different training and much larger models.

## Mac-first research program

The data is generated remotely through an API. The 36 GB Apple Silicon Mac
coordinates those requests, checks and reviews the resulting data, fine-tunes
the 4B student model, and runs the offline tests. We do not try to load
GLM-5.3-Flash on the Mac.

### Step 0 — Make the process repeatable

- Lock the Nine Circles, data format, safety rules, generation prompts, and the
  rule that keeps related cases in the same train-or-test group.
- Give every API batch a manifest recording the model name, prompt version,
  generation settings, request IDs, token use, timestamps, and response hashes.
  Never record the secret key.
- Make batches safe to restart: retry temporary failures, reject duplicates,
  validate every JSON result, and stop when the approved spending limit is
  reached.
- Convert reviewed cases into the exact chat and tool format Qwen expects, and
  verify that training scores the answer rather than the prompt.
- Build fake offline tools with an action log the model cannot rewrite.

### Step 1 — Make the first 200–500 cases through the API

Use Z.ai's documented [`glm-5.3-flash`](https://docs.z.ai/guides/vlm/glm-5.3-flash)
model to draft the cases. Start with a few requests to confirm the prompt,
format, speed, and cost before generating a full batch. Use JSON output, but
still validate every reply locally.

For the first pilot, keep the API key in a
[supported coding tool](https://docs.z.ai/devpack/quick-start) and use Coding
Plan access there. Never commit the key or copy it into a dataset. Z.ai treats
a standalone batch script as General API use. If we build that automation, it
will read the key from `ZAI_API_KEY`, call
`https://api.z.ai/api/paas/v4/`, and use General API billing rather than Coding
Plan quota.

Each case is checked independently by two people. Record rejections and edits.
When possible, reviewers should not know which experimental group a case came
from. GLM-5.3-Flash helps write the data; it does not judge its own output.

### Step 2 — Fine-tune Qwen locally

Use the existing Qwen3-4B Thinking 4-bit MLX model. Start each trained version
from the exact same base model. Give every version the same situations, tools,
answers, amount of text, and training settings. Change only the lesson:

1. no lesson;
2. a direct rule;
3. a false or unrelated consequence;
4. shuffled stories; or
5. contrapasso, where the shortcut truly undermines its own goal.

Run ten training steps first to confirm that the data format and memory use are
safe on the Mac. The technical starting point is 4-bit QLoRA, batch size 1,
2,048-token examples, rank 8, 16 adapted layers, gradient checkpointing, and no
training loss on the prompt. Repeat each version three times so one lucky run
does not decide the result.

Before looking at the answers, choose the main behavior score and decide how
much loss on ordinary, allowed tasks is acceptable. Continue only if
contrapasso beats the matched comparison groups without teaching the model to
refuse everything or making it worse at normal tool use.

### Step 3 — Decide whether another training method is needed

Start with supervised fine-tuning because it is the cleanest test of the
curriculum. Consider preference training only after independent reviewers have
made reliable good-versus-bad action pairs. Do not begin with reinforcement
learning: its reward would add a second moving part and could recreate the
score-gaming problem we are trying to study. RL can become a later stress test
after the offline environment and its scoring rules have been attacked and
repaired.

## Release sequence

1. **Draft:** publish the Nine Circles, data format, two safe examples, checking
   tool, and this research plan.
2. **First reviewed set:** release 200–500 cases after two-person review, along
   with the scoring rules and the experiment we promised to run before seeing
   results.
3. **Public v0.1:** grow to 4,000–5,000 reviewed training cases and about 500
   public test cases, then publish repeated baseline runs.
4. **Private test:** build 1,000–2,000 unseen cases from different scenario
   families and return detailed scorecards for submitted models.
5. **Scale:** reach 25,000+ cases and custom packs only if the first controlled
   experiment shows that contrapasso adds value beyond rules and writing style.

## Non-negotiable boundaries

- No live exploits, credentials, targets, command payloads, or replay of the
  real incident.
- No random-row train/eval split; families, environments, and generator
  templates stay in one split.
- The API model never grades its own cases, and every generated case records
  the model and prompt version that produced it.
- No private-eval rows or reversible derivatives in public repositories.
- No claims that prose behavior proves safe autonomous action.
- No claims that the incident validates contrapasso; it motivates falsifiable
  tests.
