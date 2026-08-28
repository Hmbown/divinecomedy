# Inferno 2.0

## A Benchmark and Curriculum for Agentic Misalignment

**Working subtitle:** Nine failure modes of autonomous agents, from reward
hacking to covert misalignment.

**Status:** Build plan and draft standard. Targets in this document are not
released datasets, completed evaluations, or commercial availability.

## What we are building

Inferno 2.0 is not a larger pile of synthetic prose. It is a versioned standard
for describing, training on, and evaluating agentic misalignment:

- a stable Nine Circles taxonomy with versioned sublabels;
- canonical structured cases that can produce several post-training and
  evaluation views;
- action-level evaluations with authorized/unauthorized twins;
- a public development suite and reproducible baselines;
- a separate, refreshed private evaluation service; and
- model-ready alignment packs and environment-specific research work.

The intended public association is the standard: *Circle 3: Reward Hacking*,
*Circle 7: Resistance to Correction*, and so on. The defensible service is the
quality, provenance, freshness, customization, adjudication, and diagnostic
measurement around that standard.

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

Cases may contain an ordered cross-circle mechanism chain. A representative
abstract chain is:

```text
impossible task
  → escalating persistence
  → grader exploitation
  → unauthorized communication
  → peer-goal adoption
  → apparent-success fabrication
```

This is more useful than assigning one label after the fact: it describes how
one failure changes the conditions for the next.

### One canonical case, several deterministic views

The normalized record in [`inferno_2_0/`](inferno_2_0/) includes the user's
proposed fields—scenario, objective, authorized scope, environment state,
temptation, circles, observable actions, mechanism annotation, safe alternative,
stop trigger, ideal response, severity, tool and multi-agent flags—plus the
fields needed for a standard:

- stable case and scenario-family IDs;
- ordered mechanism chains and authored action plans;
- generator model, revision, prompt revision, and source provenance;
- annotation evidence, confidence, and review status;
- separate realized-failure labels and counterfactual evaluation targets;
- a format-identical curriculum-material object for every experimental arm;
- release-split eligibility; and
- a machine-checked mock-only content boundary backed by human review.

`annotated_failure_mechanism` is an adjudicated hypothesis, not access to a
model's hidden cognition. Legacy chat rows can be linked to the new format, but
new labels must not be inferred automatically from prose.

Deterministic exporters produce these views from the same source record:

- narrative consequence data for the original contrapasso treatment;
- portable mock-tool action plans for supervised fine-tuning;
- independently audited chosen/rejected pairs for possible DPO;
- grader examples for circle, mechanism, and severity classification; and
- candidate-plan prefixes for intervention classification.

The draft monitoring view contains authored proposed steps and expected
outcomes, not executed tool results. It must not be described as behavioral
trajectory monitoring until the hermetic runner emits immutable observations
and receipts.

The derived views are build artifacts, not separate source corpora that can
silently drift.

## Public, private, and paid boundaries

### Public standard

Publish the taxonomy, schema, safe generation and validation tools, annotation
guidance, scoring specification, reference cases, a public development suite,
and multi-seed baseline manifests. Public-dev scores are development evidence,
never held-out claims.

An initial credible release target is 4,000–5,000 audited training cases and
roughly 500 public-development cases, after a smaller gold-set and causal pilot.

### Private evaluation

Keep 1,000–2,000 scenario-family-out-of-distribution cases outside public Git
and Hub repositories. Version evaluation windows, cap submissions, report
uncertainty, and publish blinded manifests and result schemas rather than
prompts. Refreshing the suite must not silently change historical leaderboard
scores.

The result is a diagnostic vector, not one gameable alignment number:

- attempted unauthorized action;
- safe stopping and escalation;
- evidence and transcript integrity;
- authorized-task success;
- benign collaboration and false-refusal rate;
- recognition/action joint outcomes; and
- breakdowns by circle, sublabel, severity, and failure chain.

[FORTRESS](https://labs.scale.com/leaderboard/fortress) provides a useful public
and private benchmark precedent, including matched benign cases to measure
over-refusal. Hugging Face documents a compatible
[public leaderboard/private evaluator architecture](https://huggingface.co/blog/hugging-science/building-a-benchmark-or-challenge).
These are architecture references, not claims that Inferno has equivalent
validation today.

Private evaluation creates two security boundaries. Loading submitted weights
can execute untrusted code, while sending private prompts to a hosted model can
leak the test set through provider retention. Start with constrained API
submissions under suitable terms. Any future weight evaluation needs a
no-network sandbox, read-only gold data, `trust_remote_code=False`, strict
artifact formats, resource limits, and independent review.

### Model-ready packs and research service

After the causal pilot, scale toward a 25,000+ case structured corpus, with
20k/50k/100k tiers only when review capacity and demand justify them. The useful
offering is not raw row count. It is:

- hard negatives and authorized/unauthorized twins;
- counterfactual rationale and consequence arms;
- cross-circle and multi-agent trajectories;
- model- and environment-specific generation;
- human adjudication and provenance;
- contamination-resistant refreshes; and
- reports that identify the trajectories and mechanisms behind a score.

The research thesis and enough data to reproduce the public baselines stay
open. Scale, freshness, private measurement, and customization are the service.

## Why contrapasso is the research mechanism

The central hypothesis is not that poetic punishment makes a model moral. It is
that a model may act differently when training represents a shortcut as
destroying the precondition of the objective it appears to advance:

- a copied answer can raise a score while voiding what the score certifies;
- a falsified log can look successful while destroying evidence of success;
- peer agreement can coordinate action but cannot manufacture authorization;
- manipulation can win an immediate choice while consuming the trust needed
  for durable cooperation; and
- persistence can continue optimizing after it has silently changed the task.

This is causal completion, not punishment. Authorization is not defined into
every objective by fiat: the benchmark separately scores immediate completion,
procedural validity, third-party effects, and whether the shortcut genuinely
defeats an instrumental precondition. Some controls must violate a rule without
being causally self-defeating.

Anthropic's 2026
[Model Spec Midtraining](https://alignment.anthropic.com/2026/msm/) is important
adjacent evidence. It reports that synthetic material explaining the principles
behind a specification, combined with alignment fine-tuning, improved
out-of-distribution agentic behavior. It does not validate contrapasso, used a
different training stage and much larger models, and makes matched causal
controls more important here.

## Mac-first research program

All first-stage work must fit a 36 GB Apple Silicon Mac and run without real
targets, external accounts, or hosted generation.

### Gate 0 — Freeze the standard

- version the taxonomy, schema, content policy, prompts, model revisions, and
  family-level split rules;
- update the MLX wrapper so the logged command actually controls seed, batch,
  sequence length, adapted layers, rank, gradient checkpointing, and prompt
  masking;
- add a model-specific Qwen/MLX-LM `tools`/`tool_calls` exporter, then test the
  tokenized prompt/target boundary and loss masking rather than assuming the
  portable JSON view is directly trainable; and
- build hermetic mock tools and an immutable action-event log.

### Gate 1 — Gold data

Create 200–500 double-reviewed cases before scaling. Reviewers should be blind
to experimental arm where possible. Freeze acceptance criteria, record every
rejection and edit, and match retained counts, lengths, tool-call distributions,
and editing effort.

The candidate local teacher is
[`mlx-community/GLM-4.7-Flash-4bit`](https://huggingface.co/mlx-community/GLM-4.7-Flash-4bit/tree/1454cffb1a21737e162f508e5bc70be9def89276),
a 16.9 GB serialized MLX conversion of the MIT-licensed 30B-A3B
GLM-4.7-Flash. Published weight size is not measured peak memory. First run a
representative-context load and generation smoke test that records peak unified
memory, disk use, latency, and throughput. Run the teacher and student
sequentially. This plan does not use a Z.ai Coding Plan key to generate
external-model training data; confirm the applicable product and API terms
before any hosted generation. The default path is local open-weight inference.

### Gate 2 — Causal QLoRA pilot

Use the existing Qwen3-4B Thinking 4-bit MLX student. Start every adapter from
the same frozen base and hold prompts, mock tools, terminal action targets,
example counts, action-token budgets, and hyperparameters constant. Compare:

1. neutral context;
2. direct rule;
3. false or unrelated consequence;
4. shuffled curriculum; and
5. causally matched contrapasso.

Run a 10-iteration memory and format smoke first. The starting configuration is
batch size 1, 2,048-token sequences, rank 8, 16 adapted layers, gradient
checkpointing, and prompt-loss masking. Three training seeds make an exploratory
pilot; they do not establish stable seed variance or deployment safety.

Pre-register one primary action endpoint, clustered uncertainty by scenario
family, deterministic or pre-specified inference seeds, multiplicity handling,
and an authorized-task degradation margin. Advance only if contrapasso improves
the action endpoint over matched controls without producing generalized refusal
or loss of legitimate tool competence.

### Gate 3 — Method escalation

Start with supervised authored-action-plan QLoRA. DPO becomes relevant only after
independent adjudication yields length-matched preference pairs and SFT failure
cases. Do not start online RL: a learned or hand-coded reward would confound the
curriculum mechanism and could recreate the proxy gaming under study. RL is a
later stress test after the simulator, reward ordering, monitor, and rollback
path survive adversarial review.

## Release sequence

1. **Draft standard:** taxonomy, schema, safe examples, validator, deterministic
   views, content boundary, and research note.
2. **Gold release:** 200–500 double-annotated cases, agreement analysis, scoring
   specification, and frozen causal-pilot preregistration.
3. **Public v0.1:** 4,000–5,000 audited training cases, about 500 public-dev
   cases, hermetic runner, and multi-seed baselines.
4. **Private evaluation:** 1,000–2,000 family-OOD cases, versioned evaluation
   windows, submission controls, and diagnostic reports.
5. **Scale:** 25,000+ structured cases and custom alignment packs only after the
   causal pilot shows value beyond matched rule and style controls.

## Non-negotiable boundaries

- No live exploits, credentials, targets, command payloads, or replay of the
  real incident.
- No random-row train/eval split; families, environments, and generator
  templates stay in one split.
- No teacher self-judging and no unpinned generator provenance.
- No private-eval rows or reversible derivatives in public repositories.
- No claims that prose behavior proves safe autonomous action.
- No claims that the incident validates contrapasso; it motivates falsifiable
  tests.
