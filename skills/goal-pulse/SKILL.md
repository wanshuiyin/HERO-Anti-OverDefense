---
name: goal-pulse
description: Keep an existing long-running Codex Goal moving through timely artifact collection, stalled-worker takeover, and optional periodic reminders. Use when the user asks to prevent idle loops or schedule nudges in an existing Goal conversation.
---

# Goal Pulse

Advance the current Goal at the fastest effective pace. Spend work on the deliverable: no stalling, busywork, or substituting plans and reports for execution. A pulse is a cue to act, not a request for another status report.

## Act on the bottleneck

- When a worker delivers a complete artifact, read it promptly, verify the remaining obligation, and perform the next authorized acceptance or handoff step. Do not leave it waiting for a batch.
- Delegate substantial bounded work through the user's authorized workers. Give each worker the complete target, real inputs, owned files and acceptance method. Preserve the agreed division of labor.
- If the same blocker survives two worker rounds without meaningful progress, take over the specific gap or change the decomposition. Preserve the source, failed evidence and session; transfer ownership before editing. A healthy long computation or a new verified result is progress.
- Keep independent work moving while a blocked line has a saved breakpoint. Reuse working code, caches and valid checks. Repair the missing connection without restarting the whole task.
- Choose the next action that changes the deliverable. Cut repetitive polling, cosmetic rewrites, speculative corner cases and repeated reviews of unchanged work. Run checks that resolve an actual uncertainty or meet a stated requirement.
- Count complete accepted deliverables. Keep the original target, difficulty, acceptance criteria, authorization and budget. Queued jobs and partial modules remain work in progress.

Use the project's existing state files for essential breakpoints. Give normal progress updates and answer the user; do not write an extra acknowledgement or report just because a pulse arrived.

## Optional Codex timer

Start the timer when the user requests scheduled nudges for an explicitly identified existing Goal thread. Reading or installing this skill alone does not start it. Do not choose another conversation from its recent activity.

The helper requires Python 3.10+, the adjacent `requirements.txt`, and a running local Codex app-server with the Goal API and Unix control socket. See [installation and commands](README.md). It uses POSIX facilities; this timer does not support native Windows or other agent hosts.

For a standard skill installation:

```sh
pulse_dir="${CODEX_HOME:-$HOME/.codex}/skills/goal-pulse"
"$pulse_dir/.venv/bin/python" "$pulse_dir/scripts/goal_pulse.py" start \
  --thread <EXISTING_THREAD_UUID> --interval-minutes 30 --poll-seconds 60
```

The default reminder is bilingual, every 30 minutes. The 60-second poll reads metadata without model calls. `start --message-file /absolute/message.txt` saves a custom reminder; `tick --message-file` overrides the message for that invocation only.

The helper binds to the Goal's creation timestamp and sends `turn/steer` with `expectedTurnId` only when that Goal is active, the thread is not waiting for user input or approval, and its current turn is in progress. Paused, blocked and budget-limited Goals stay silent. A completed, missing or replaced Goal ends the watcher. It never resumes a Goal or starts a new turn.

```sh
"$pulse_dir/.venv/bin/python" "$pulse_dir/scripts/goal_pulse.py" status --thread <EXISTING_THREAD_UUID>
"$pulse_dir/.venv/bin/python" "$pulse_dir/scripts/goal_pulse.py" stop --thread <EXISTING_THREAD_UUID>
# Read-only eligibility check; no reminder is sent.
"$pulse_dir/.venv/bin/python" "$pulse_dir/scripts/goal_pulse.py" tick --thread <EXISTING_THREAD_UUID>
```

State lives in `${CODEX_HOME:-~/.codex}/goal-pulse/<thread-id>/`. A file lock prevents duplicate watchers; an attempted send consumes the interval even if its acknowledgement is lost. On transport failure, inspect the reported error rather than using GUI typing or resume commands to force delivery.

The watcher runs locally: sleep suspends it, and reboot requires another start. Delivered reminders consume conversation tokens; polling does not. The agent still judges work and handles acceptance through the existing project workflow.
