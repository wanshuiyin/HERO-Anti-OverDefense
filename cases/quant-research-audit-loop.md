# Case study: when research rigour became research bureaucracy

This anonymised case comes from two long-running local coding-agent sessions for
a quantitative-research pipeline. No repository names, local paths, thread IDs,
credentials, research hypotheses or unpublished results are included.

The user wanted a complete pipeline to move from data preparation to modelling
and portfolio evaluation. They explicitly instructed the agent to start the
expensive work, avoid defensive code, skip hashes and broad test theatre, and run
only the sanity checks needed to trust the numbers.

The agent still spent a large share of the sessions constructing and maintaining
the process around the experiment.

## What happened

The characteristic loop was:

`uncertainty → protocol freeze → versioned root → builder → independent auditor → gate → review packet → recovery prompt → another version`

Several pieces were individually defensible. Together they had no natural stop.
A routine field-filter bug, a memory estimate that missed its target, or a failed
temporary run could create a new permanent lineage. That lineage then justified
another audit and more documentation.

Resource monitoring became a second loop. Progress was reported within shards,
with repeated memory and disk readings, although the user had asked for sparse
milestone updates and the running job had not changed state.

## Evidence from the local event logs

The counts below use user-visible agent-message events and paths recorded by
completed patch events. They are diagnostic evidence, not a scorecard: a high
count is not itself a finding. The finding is what the activity displaced and
whether it settled a live uncertainty.

| Observation | Session A | Session B |
|---|---:|---:|
| Task starts | 145 | 58 |
| User messages | 37 | 34 |
| Visible agent messages | 1,732 | 1,536 |
| Messages containing “audit” | 578 | 443 |
| Messages containing “freeze” | 286 | 312 |
| Messages containing “gate” | 376 | 263 |
| Messages containing “memory” | 243 | 215 |
| Unique Markdown paths changed | 97 | 196 |
| Unique Python paths changed | 14 | 191 |
| Unique `.sha256` paths changed | 0 | 19 |

In Session A, three process artifacts were updated 148, 104 and 77 times:
an experiment/decision log, a master research memory/roadmap and a master
recovery prompt. After a request to stop excessive auditing, the subsequent
period contained 46 task starts and 139 visible messages; 118 referenced shards.
The cadence changed only after another explicit correction.

## Why the original anti-overdefense sentence did not work

The active research prompt contained one general sentence asking for only
necessary sanity checks. The same prompt then specified twelve stages and many
more concrete instructions for freezes, gates, new roots, independent audits,
review chains, immutable evidence and stop-on-failure behaviour.

The specific workflow beat the general preference. “Be less defensive” could
not override a detailed contract that defined defence as the path to completion.

The prompt also merged two meanings of rigour:

- **Scientific rigour:** causal timing, no future leakage, valid folds, correct
  labels, aligned keys, stable numerical results and honest inference.
- **Artifact rigour:** hashes, protocol fingerprints, immutable failed roots,
  multiple auditors, repeated preflights and versioned handoff documents.

The first protects the conclusion. Much of the second protected the process from
criticism without changing the conclusion or the next action.

## HERO classification

- **R — Rubrics was dominant.** Judgement became gates, audit loops, reviewer
  packets and repeated verification of settled facts.
- **O — Overbuild was equally important.** Routine retries became permanent
  version trees, contracts and recovery machinery.
- **H — Hashing was secondary.** Nineteen distinct `.sha256` artifacts and many
  manifest/fingerprint references appeared despite a direct instruction to skip
  them.
- **Over-correction amplified both.** A local engineering failure often froze a
  much larger research direction instead of receiving a local repair.

## Rigour that must remain

Anti-overdefense must not become an excuse to suppress real numerical problems.
For this project shape, the checks that paid for themselves were:

- signal, execution and label-clock causality;
- train/validation/test isolation and future-leakage checks;
- key, row and universe alignment;
- formula and missing-value semantics on a small slice of real data;
- numerical equivalence after a performance optimisation;
- the first real shard of a long-running job;
- final sample-count and result aggregation checks;
- protection of genuinely held-out or prospective outcomes.

A real antivirus alert, raw-data corruption or a destructive operation boundary
also remains a real stop condition. HERO does not waive those.

## The proportionate operating rule

Before adding a check, the agent must be able to state one uncertainty that is
still live, the concrete failure the check can expose, and what action would
change if it fails. If the same path has already run successfully against
unchanged code, the uncertainty is no longer live.

Default execution for this research shape is:

1. one primary deliverable per turn;
2. one small real-data sanity check;
3. one targeted check for the code just changed;
4. one active output root for recoverable engineering retries;
5. durable versioning only for changed scientific semantics or consumed results;
6. one independent recomputation at the final claim-bearing milestone;
7. progress at roughly ten-percent milestones, plus real failure alerts.

The companion [Chinese Codex `AGENTS.md` example](../examples/quant-research-agents.zh-CN.md)
turns these boundaries into a project-specific prompt. It is an example, not a
replacement for HERO's canonical block.
