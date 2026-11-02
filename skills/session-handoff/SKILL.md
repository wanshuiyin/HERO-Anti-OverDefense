---
name: session-handoff
description: Prepare a grounded project handoff before switching to a fresh session, or continue authorized work from an existing handoff after checking current artifacts and running tasks.
---

# Session Handoff

Carry the task across a context boundary through project files. Preserve the
actual objective, useful evidence, and concrete next move so a fresh session can
continue without reconstructing the entire conversation or repeating completed
work. This skill works with Codex and Claude Code; it needs ordinary file tools
and the project's existing tools, not a background service.

A fresh session starts with new conversational context and reads the handoff
from disk. Resuming an existing session restores that session's history and may
retain its accumulated context. These are different operations. Preparing a
handoff does not open either kind of session or transfer host-managed state.

Use **prepare** when the user asks to save a handoff, prepare for a new session,
or preserve the task before a context reset. Use **continue** when a new session
is asked to pick up an existing handoff. Infer the mode from the request; a
routine status question does not itself call for a new handoff document.

## Preserve the working agreement

Read the project's applicable `AGENTS.md` or `CLAUDE.md` and the user's latest
instructions before changing its recovery documents. The original goal and
acceptance criteria remain in force. Carry forward subsequent corrections,
scope changes, and explicit permissions with enough precision that the next
session will act on the current agreement.

Separate instructions from observations. A user correction controls what to do;
a result file establishes what happened. An older handoff is a navigation aid,
not authority to disregard either. Where the conversation contains a necessary
decision that has never reached disk, record it now with its practical effect.
Do not invent a quote or imply that a remembered decision was independently
verified.

Keep the project in its established language and document format. The examples
below show useful content, not a mandatory new schema. A short code change may
need a few paragraphs; a research task may need a fuller explanation of its
remaining mathematical obligation and failed approaches.

## Prepare: establish the state worth carrying

### Find the existing recovery entrypoint

Look for the recovery path already named in project instructions. Common
examples are `NEXT_SESSION.md`, `HANDOFF.md`, a current run's progress document,
or a `Pipeline Status` section pointing to a focused research contract. Read the
active entrypoint and its relevant source documents before deciding where to
write. Prefer targeted file searches over loading every historical log.

Update that entrypoint in place. If the project uses a short navigator plus
detailed run notes, keep the navigator short and put details in those notes.
Only create a root `HANDOFF.md` when there is no suitable existing entrypoint.
Do not create a second progress ledger merely to match this skill's headings.

Give the entrypoint a short reading order: the original target, the current
state or contract, and the artifact needed for the first action. Identify large
archives and raw logs as lookup material, with a useful section or search term.
Choose this set for the task; do not impose a fixed file count. Preserve details
on disk without loading them all into the new conversation.

Keep `AGENTS.md` and `CLAUDE.md` focused on durable instructions. When discovery
needs improving, add a short pointer such as “Current task and recovery:
`NEXT_SESSION.md`.” Do not append the whole changing handoff to those files.
Preserve unrelated instructions and historical evidence.

### Check the workspace before describing it

Establish the actual working directory, repository or worktree, and relevant
uncommitted changes. With a Git repository, useful read-only commands include:

```sh
pwd
git status --short --branch
git branch --show-current
git log -1 --format='%h %s'
git diff --stat
git diff --cached --stat
```

Read the relevant diffs when they change the interpretation of current work.
The command list is an example, not a requirement to inspect unrelated files.
A project without Git can be handed off through its actual files and run paths.

Record which changes implement the current task, which are pre-existing user
work, and which ownership is uncertain. Include important untracked output
paths when they contain real results or the next session must preserve them.
An uncommitted result can be valid evidence; no commit, stash, push, cleanup,
branch switch, or worktree creation is required to prepare this handoff.

### Reconcile claims with artifacts

Identify the latest complete deliverables and the evidence needed to use them.
Read the relevant output, source, or result summary rather than copying the
previous handoff's conclusion. For a check, record what was checked, the result,
and the source version or scope when it matters. Distinguish a completed test
from a proposed command and a model's static review from actual execution.

Avoid rerunning successful checks just to make the handoff look complete.
Existing evidence is enough when the relevant inputs have not changed. State a
specific unresolved question if a fresh check is necessary. For example, a
patch written after the last test needs validation; an unchanged proof does not
need another full build solely because a new session is coming.

Keep old results as historical facts with their limits. “The previous branch
passed the integration test” must not become “the current tree is verified.”
Likewise, a partial result, conditional theorem, or successful worker turn does
not establish that the original acceptance criteria have been met.

### Preserve decisions and productive failures

Explain the current approach through the decisions that affect the next move.
Save the essential formula, interface, assumption, or source pointer when
otherwise the next session would have to rediscover it. Link to the detailed
artifact instead of reproducing a long derivation already stored there.

Retain failed routes that are likely to tempt a fresh agent. Explain what was
tried, the actual failure or counterexample, and the scope of that finding.
Where useful, state what new condition would make retrying reasonable. “Does
not work” is too vague; “the local condition passes all tested cases but does
not imply coverage of the original input domain” prevents a concrete mistake.

Separate known failures from untested ideas. An API outage is not evidence that
a mathematical route fails; a wrong assumption is not fixed by more runtime.
There is no need to preserve every minor edit or abandoned wording choice.

### Account for active work and ownership

If work is running, inspect the available current status through its existing
job, worker, process, or service interface. Record the identifier, relevant
workspace, owner, output path, and a precise way to check progress. Prefer a
task's known identifiers to broad process listings that may expose unrelated
command arguments.

Distinguish “running, checked now” from “last observed running” and “status
unavailable.” If a worker has exclusive write access to a directory, preserve
that boundary. A new session must not assume it inherited an agent connection
or can take over a live writer's files. Preparing this document does not stop,
restart, replace, or send new instructions to workers.

When the host exposes a Goal, record only the relevant observed Goal reference
and status, with a pointer to the original goal specification. The host remains
authoritative for Goal state and remaining budget. A handoff cannot transfer a
Goal to another thread, reset its usage, or resume a paused Goal. Do not invent
custom Goal controls or treat a copied status as live state.

If no active jobs or workers are relevant, say so briefly and move on. Do not
introduce an ownership registry for a task that does not need one.

### Write for the next decision

The entrypoint should let another agent answer: what must be achieved, what is
already established, what is still open, and what should happen first? Use the
following shape only where it helps the existing document:

```markdown
# Current handoff

Updated: <time and timezone>. Workspace: <actual project/worktree>.
Branch: <observed branch or detached state>; current change: <brief description>.

## Objective and agreement
<Full target and original acceptance criteria, or a precise pointer plus the
essential statement. Latest user corrections and relevant authorization.>

## Reading order
<First-action files to read now (target, current contract/state, active artifact).
Lookup material to search only on demand, with relevant section or query term.>

## Established work
<Deliverables with paths, their conclusions, and verification actually run.
Explain any remaining scope limitation that changes acceptance.>

## Current work and decisions
<Relevant uncommitted changes, current approach, open obligation, and why the
chosen next move follows. Preserve other people's changes.>

## Routes already tried
<Important failures, evidence, and what would justify revisiting them.>

## Active tasks
<Known job/worker identifiers, owner and write scope, latest observed status,
output locations, and existing status command or tool. Omit if inapplicable.>

## Next action
<A concrete action against a named file, result, or job. State the question it
resolves and the next branch of work if the outcome matters.>
```

Do not reduce a large original objective to the nearest easy subtask. If the
target is an end-to-end proof, describe the missing connection to the original
statement even when the next action is only to repair one lemma. If the user
asks for a working feature, preserve the required observable behavior rather
than treating a successful build as the final deliverable.

If a project already maintains Pipeline Status or workflow checkpoints, align
the current owner’s updates with those records. Preserve the workflow’s run IDs,
reviewer routes and acceptance status. For a record owned by a live worker,
link its observed state instead of rewriting it from a summary.

Read the updated entrypoint once for usability: its first action should be
possible from the referenced files and tools, and its decisive claims should
point to existing evidence. Correct broken paths or ambiguous current/old run
references. This is a practical reread, not a new audit framework.

### Give the user a fresh-session starting prompt

Return the entrypoint path and a copy-ready prompt using actual project paths
and a concrete next action. Include the actual skill file path so the next
session can read it even if its skill catalogue has not been refreshed. For example:

```text
Continue the existing task in <project/worktree>. Read <actual path to this
SKILL.md> and use continue mode. Read the applicable AGENTS.md/CLAUDE.md, then
<recovery entrypoint> and its first-action reading list.
Preserve the recorded objective, acceptance criteria, latest user corrections,
and ownership boundaries. Check the relevant current files and live job status;
reuse completed evidence. Start with <specific next action>. Continue work
already authorized, and report a material conflict if one prevents that action.
```

Tell the user they can manually open a fresh session in the intended workspace
and paste this prompt. Do not guess host UI steps or present `resume` or `fork`
as a way to obtain empty conversational context. No automatic session launch is
part of this skill.

Preparing a handoff is complete when the state is saved and the starting prompt
is ready. It does not itself cancel other requested work. If this was an
intermediate preservation step during an ongoing task, continue that task
unless the user asked to stop or the host has reached a real limit.

## Continue: rebuild enough context to act

Read applicable project instructions, then the named recovery entrypoint.
Follow its pointers to the original target and the source material needed for
the first decision. Load details progressively; importing every old transcript
defeats the purpose of a fresh context. A short summary guides reading, while
the underlying artifacts support conclusions.

Check the actual workspace and relevant changes. Compare the entrypoint's
branch, outputs, and latest validation with the current files. Check any active
job through its recorded interface before launching replacement work. Restore
monitoring only through tools available in this session; an old agent ID or job
reference is not proof that its connection remains usable.

Resolve discrepancies according to their effect. If a completed result has
arrived, collect it and advance the next decision. If files changed after the
last check, validate the affected part. If the handoff is older but consistent
with current artifacts, continue from it; elapsed time alone does not invalidate
completed work or justify restarting the workflow.

For host-managed Goals, inspect the actual status when the relevant host tools
are available. Do not claim this fresh thread owns the previous thread's Goal
or budget. A paused Goal stays paused until the user resumes it through the
applicable mechanism. If the requested next action depends on a missing binding,
explain that dependency while continuing independent authorized work.

Respect live workers' write ownership. Read their outputs or status as allowed,
and take over only when the existing workflow or user authorization establishes
that the ownership has ended or been reassigned. Do not kill a process or
overwrite its directory merely because the new session cannot attach to it.

State the recovered objective and immediate next move briefly, then execute
work already authorized. Do not ask the user to reconfirm ordinary continuation.
Ask only when an unresolved conflict materially changes the target, permission,
ownership, or a decision that cannot reasonably be reversed. If one part is
blocked, progress on independent parts without replacing the original goal.

Keep the same recovery entrypoint current as useful results arrive. Reuse the
project's existing logs, research wiki, and state files rather than keeping a
second account in parallel. The result of continue mode is renewed task
progress, not another summary of the summary.

## Keep the mechanism proportional

Save the information the next action actually needs. Do not include credentials,
authentication material, or private connection details; reference the existing
approved execution setup instead. Actual local paths can identify artifacts,
but reusable templates should not embed a particular user's private paths.

Choose a fresh session when the task benefits from a focused context. Let
repeated loss of relevant details, difficult navigation through old discussion,
or the user’s requested reset guide that choice, rather than a fixed context
percentage or rotation schedule. The handoff carries the working state through
ordinary files; the next session reconstructs the context needed to act.
