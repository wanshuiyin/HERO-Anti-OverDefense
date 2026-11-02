---
name: goal-pulse
description: Enable Goal Pulse by default on Codex Goal start, resume, or takeover, and on Claude Code /goal or explicitly authorized long autonomous work. Use a Codex timer or Claude Code native cron for bilingual execution reminders every 30 minutes. Supports start, status, stop, and a single pulse.
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

## Choose the host route first

**Claude Code:** read [the native cron instructions](references/claude-code.md).
Use `CronList`, `CronCreate`, and `CronDelete` in the current conversation, or the
documented `/loop 30m` equivalent. Start or resume of `/goal`, or an explicitly
authorized long autonomous task, enables reminders by default after installation.
Dispatch `start`, `status`, `stop`, or `pulse` before acting: a scheduled `pulse`
executes one reminder and never creates another cron. Honor a user's opt-out until
they ask to enable reminders again. Only the main agent manages the reminder.
Continue in that reference; the Python commands below belong to Codex.

**Codex:** follow the watcher instructions below. Its Goal/turn checks and transport
remain specific to Codex. Installation, ordinary chat, and reading this skill do
not start a timer or create a Goal on either host.

## Default activation for Codex Goals

Whenever the user starts or resumes a Goal, or the main agent takes over an active Goal, enable the timer for that thread by default. Do not wait for a separate `$goal-pulse` request or ask for confirmation. Start after the Goal exists; honor an explicit user request to disable reminders. Reading or installing this skill and ordinary chat do not create a Goal or start its timer. Only the main agent activates the Goal's watcher; workers do not start extra timers.

Use the host's `CODEX_THREAD_ID`, which the helper reads by default. If the host supplies the thread ID another way, pass it with `--thread`. Never choose a conversation from recent activity. If the skill environment or dependency is missing, prepare it using the installation guide; report an actual setup blocker instead of silently treating reminders as enabled.

The helper requires Python 3.10+, the adjacent `requirements.txt`, and a running local Codex app-server with the Goal API and Unix control socket. See [installation and commands](README.md). This Python watcher uses POSIX facilities and does not support native Windows; Claude Code uses its own native route above.

For a standard skill installation:

```sh
pulse_dir="${CODEX_HOME:-$HOME/.codex}/skills/goal-pulse"
"$pulse_dir/.venv/bin/python" "$pulse_dir/scripts/goal_pulse.py" start \
  --interval-minutes 30 --poll-seconds 60
```

Check the start result: `started` or `already-running` for this Goal means the watcher is present. Repeated starts for the same Goal preserve its running settings. When a previous Goal's watcher is still exiting, start waits for it to release the thread before binding the new Goal; a timeout is a setup failure, not an enabled timer.

The default reminder is bilingual, every 30 minutes. The 60-second poll reads metadata without model calls. `start --message-file /absolute/message.txt` saves a custom reminder; `tick --message-file` overrides the message for that invocation only.

The helper binds to the Goal's creation timestamp and sends `turn/steer` with `expectedTurnId` only when that Goal is active, the thread is not waiting for user input or approval, and its current turn is in progress. Paused, blocked and budget-limited Goals stay silent. A completed, missing or replaced Goal ends the watcher. It never resumes a Goal or starts a new turn.

```sh
"$pulse_dir/.venv/bin/python" "$pulse_dir/scripts/goal_pulse.py" status
"$pulse_dir/.venv/bin/python" "$pulse_dir/scripts/goal_pulse.py" stop
# Read-only eligibility check; no reminder is sent.
"$pulse_dir/.venv/bin/python" "$pulse_dir/scripts/goal_pulse.py" tick
```

State lives in `${CODEX_HOME:-~/.codex}/goal-pulse/<thread-id>/`. A file lock prevents duplicate watchers; an attempted send consumes the interval even if its acknowledgement is lost. On transport failure, inspect the reported error rather than using GUI typing or resume commands to force delivery.

The watcher runs locally: sleep suspends it, and reboot requires another start. Delivered reminders consume conversation tokens; polling does not. The agent still judges work and handles acceptance through the existing project workflow.
