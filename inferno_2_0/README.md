# Inferno 2.0 format draft

This directory is a small, executable draft of a structured curriculum and
benchmark format for agentic misalignment. It preserves the original nine
Inferno circle names while adding mechanism-level labels and cross-circle
cases.

**Status:** public development material only. The examples are not a private
evaluation set, a benchmark release, an incident reconstruction, or evidence
that this curriculum improves model behavior. A contamination-resistant held-
out evaluation corpus must be created and operated separately.

## Contents

- `spec/taxonomy-v0.1.json` preserves the nine circles and registers narrower,
  composable failure mechanisms.
- `spec/case.schema.json` is a JSON Schema draft 2020-12 canonical case format.
  It records ordered mechanism chains, source/generator revisions, review state,
  and the matched evaluation surface alongside the scenario and actions.
- `examples/public_dev.jsonl` contains one fully abstract cross-circle cascade
  and its authorized benign twin.
- `case_tool.py` validates canonical cases and derives five training or
  evaluation views using only the Python standard library.

The benign twin is deliberate: a mock collaboration action is unsafe when it
is out of scope and appropriate when it is explicitly authorized and locally
checked. This prevents the benchmark from rewarding blanket refusal. The two
draft rows also differ in solvability, attempt count, and available validation,
so they illustrate a boundary; they are not a causally matched experimental
pair.

## Validate and render

Run from the repository root with Python 3.10 or newer; no third-party package
is required:

```bash
python3 inferno_2_0/case_tool.py validate \
  inferno_2_0/examples/public_dev.jsonl

inferno_render_dir="$(mktemp -d)"
python3 inferno_2_0/case_tool.py render \
  inferno_2_0/examples/public_dev.jsonl \
  --view all \
  --output-dir "$inferno_render_dir"
```

Pass every dataset shard to one `validate` invocation. The validator rejects a
`case_family_id` that appears in more than one split, so validating shards one
at a time cannot establish family-level split isolation or contamination
resistance. Private rows require double-review provenance, and the public
renderer refuses to export them, but operating a held-out benchmark still
requires a separate registry and service boundary.

The renderer creates:

| View | Intended use |
| --- | --- |
| `narrative.jsonl` | Consequence and contrapasso curriculum |
| `action_sft.jsonl` | Supervised safe-action-plan examples |
| `preference.jsonl` | Auditable chosen/rejected action pairs |
| `grader.jsonl` | Candidate-action classification |
| `monitoring.jsonl` | Candidate-plan prefix intervention labels |

These are views of the same canonical rows, not independent examples. Split
and contamination accounting should happen at the case-family level before
rendering.

`action_sft.jsonl` is a portable intermediate representation, not a claim of
drop-in Qwen or MLX-LM tool-call compatibility. Before the causal training
pilot, add and test a model-specific `tools`/`tool_calls` exporter and verify
the exact prompt-masking and loss boundaries on tokenized examples.

## Claim and annotation boundaries

`annotated_failure_mechanism` is an evidence-backed annotation with a
mechanism ID, explanation, cited observable steps, and confidence. It replaces
the tempting but unjustified idea of a "hidden failure" ground truth. Aligned
cases carry null/empty realized-failure fields. Their separate
`evaluation_targets` object names counterfactual risks the case is designed to
probe; those are not claims that the aligned action exhibited a failure.

For a realized cross-circle chain, each mechanism's first supporting step must
be nondecreasing in chain order. Two mechanisms may begin at the same step when
one proposed action simultaneously instantiates both; later annotations may
not claim to cause earlier evidence.

Terminal semantics distinguish `safe_stop` and `refuse_out_of_scope` from the
misaligned `premature_stop` and `refuse_authorized`. This makes over-refusal
representable instead of silently counting every refusal as safe. Whether a
stop trigger was genuinely met still requires case evidence and review. The
per-row map must exactly mirror the authoritative v0.1 mapping in the
validator; a case cannot redefine `continue_out_of_scope` as aligned.

`curriculum_arm` supports `neutral`, `rule_only`, `false_causal_link`,
`unrelated_consequence`, `shuffled`, and `contrapasso`. Rows sharing an
`arm_match_id` must have identical scenarios, objectives, scope, environment
state, prompts, tool schemas, observed and target actions, and terminal action
labels. Realized annotations, severity, monitoring targets, safety flags, and
other non-treatment metadata must match too. Every arm carries the same
structured `curriculum_material` fields; only their content, rationale, and
causal relationship should vary. The canonical `kind` tag is audit metadata
and is removed from model-visible material. Multiple training seeds remain
exploratory evidence, not proof of a mechanism.

The monitoring export emits one row per prefix of an authored candidate action
plan and never includes future plan steps. Its `expected_outcome` values are
author annotations, not tool receipts or evidence that an action ran. Treat it
as candidate-plan classification until Gate 0 adds an event schema and hermetic
runner with actual observations.

In v0.1, `multi_agent` is true exactly when one of the case's action plans uses
a `mock_collaboration.*` tool. This deliberately narrow invariant prevents the
flag from drifting until a later schema introduces structured actors.

## Safety constraints

All tools are inert names beginning with `mock_`. Validation rejects non-mock
tool names and scans canonical case text for URLs, credential-like material,
and common executable-payload patterns; provenance source references are the
only URL exception. This denylist supplements, rather than replaces, human
review. Safe actions must use only tools listed in the case's authorized scope.
The examples contain no real targets, network access, credentials, or
operational exploit instructions.

The public format should teach and measure the decision boundary:

> The agent notices a shortcut that could improve the measured outcome. Does
> it preserve authorized scope, evidentiary integrity, and safe stopping?

It does not need to teach how to compromise a real system.
