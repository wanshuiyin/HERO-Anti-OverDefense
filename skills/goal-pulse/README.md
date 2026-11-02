# Goal Pulse for Codex and Claude Code

Keep a long-running goal moving: collect finished worker artifacts, take over recurring blockers, and spend the next step on the deliverable. Install the skill and activation instruction for your host; the main agent then enables **30-minute bilingual reminders by default** when you start or resume an authorized long goal.

| Host | Reminder route | Setup |
|---|---|---|
| Codex | Python watcher, steers an existing active Goal turn | [Codex installation](#install) |
| Claude Code | Native cron / `/loop`, handles the reminder between turns | [Claude Code installation](#claude-code) |

Both use the same efficiency directive. HERO's [core rules](../../RULES.md) still work by pasting them into your agent configuration; Goal Pulse is a separate installation.

## Claude Code

Claude Code has two complementary commands: [`/goal`](https://code.claude.com/docs/en/goal) keeps working toward a completion condition, while [`/loop`](https://code.claude.com/docs/en/scheduled-tasks) schedules a prompt. Goal Pulse uses native session cron to deliver its reminder. **No Python environment or Codex app-server is needed for this route.**

From a clone of this repository, install the Markdown skill:

```sh
pulse_dir="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/goal-pulse"
if [ -e "$pulse_dir" ] || [ -L "$pulse_dir" ]; then
  echo "Already installed at $pulse_dir; compare and update the existing files."
else
  mkdir -p "$pulse_dir/references"
  cp skills/goal-pulse/SKILL.md skills/goal-pulse/README.md "$pulse_dir/"
  cp skills/goal-pulse/references/claude-code.md "$pulse_dir/references/"
fi
```

Add this section to the `CLAUDE.md` your host always loads (normally `~/.claude/CLAUDE.md`), preserving existing instructions. For a custom config directory, use the actual installed skill path.

```markdown
<!-- HERO-GOAL-PULSE-CLAUDE:BEGIN -->
## Goal Pulse
When the user starts or resumes /goal, explicitly authorizes a long autonomous task,
or resumes that unfinished work, read ~/.claude/skills/goal-pulse/SKILL.md and its
references/claude-code.md. By default, enable a 30-minute reminder in this session
without another request or confirmation. Only the main agent creates it.
Use native CronList / CronCreate / CronDelete. Bind [HERO-GOAL-PULSE] to the actual
target and constraints, reuse an existing matching reminder, and record the real
job ID. A pulse executes work and never creates another reminder.
Cancel this task's reminder when it completes, is paused or replaced, waits for
user input/approval, or reaches its budget limit. A late pulse cleans itself up
instead of reopening stopped work. Resume reminders when authorized work resumes,
unless the user explicitly disabled them; that opt-out lasts until re-enabled.
Ordinary chat, one-off tasks, and skill installation do not create cron jobs.
<!-- HERO-GOAL-PULSE-CLAUDE:END -->
```

Once installed, start or resume your goal normally. The main agent follows this instruction to enable the reminder; this is an instruction-driven default, not a host lifecycle hook. In an already open session, ask it to read the installed skill once. The skill supports:

```text
/goal-pulse start Finish the authorized module migration and pass its existing tests
/goal-pulse status
/goal-pulse stop
```

To schedule it explicitly yourself, fill in your actual target and check that the same task has no reminder already:

```text
/loop 30m /goal-pulse pulse --task '<actual authorized target>' [HERO-GOAL-PULSE]
```

This invokes the skill's single `pulse` action each time. Do not put `start` inside `/loop`. The shared [Claude Code reference](references/claude-code.md) contains the complete bilingual prompt, deduplication, status and cancellation procedure.

Claude Code delivers scheduled prompts **between turns**; a busy turn delays delivery. The interval has scheduling jitter, and current recurring jobs expire after seven days. Unexpired fixed jobs can return with a resumed session, so the agent checks `CronList` before creating another. The session must remain running. Use `/goal-pulse stop` to cancel this reminder; interrupting a turn alone does not delete a fixed cron job. Other `/loop` tasks and the general `loop.md` prompt are unchanged.

The agent checks the bound task and cancels its reminder when work stops. These are model-followed instructions; the Codex watcher's Goal API and active-turn gate do not apply to Claude Code. If native Cron tools are unavailable, the agent reports that reminders were not enabled and continues the authorized work.

The remaining sections describe the **Codex Python watcher**.

## Requirements

- Python 3.10+ and `websockets==15.0.1`.
- macOS or Linux/POSIX. The implementation uses Unix sockets and `fcntl`; native Windows is not supported.
- A running Codex app-server that exposes the experimental Goal API and the Unix control socket, normally `${CODEX_HOME:-~/.codex}/app-server-control/app-server-control.sock`.

The initial local integration was checked with **Codex 0.166.0 on macOS**. Installing this Python package does not provide or start the app-server. Other Codex versions need the same RPCs: `thread/goal/get`, `thread/read`, `thread/turns/list` and `turn/steer`.

## Install

Clone this repository, then copy the skill into your Codex skills directory:

```sh
git clone https://github.com/wanshuiyin/HERO-Anti-OverDefense.git
cd HERO-Anti-OverDefense
```

```sh
pulse_dir="${CODEX_HOME:-$HOME/.codex}/skills/goal-pulse"
if [ -e "$pulse_dir" ] || [ -L "$pulse_dir" ]; then
  echo "Already installed at $pulse_dir; compare and update the existing files."
else
  mkdir -p "$(dirname "$pulse_dir")"
  cp -R skills/goal-pulse "$pulse_dir"
  python3 -m venv "$pulse_dir/.venv"
  "$pulse_dir/.venv/bin/python" -m pip install -r "$pulse_dir/requirements.txt"
fi
```

For an existing installation, keep any local instructions and update the files you intend to replace. Keep its `.venv` and the separate per-thread state directory.

Add the activation instruction to Codex's always-loaded `AGENTS.md`. This appends one marked section and preserves the rest of the file:

```sh
goal_pulse_agents="${CODEX_HOME:-$HOME/.codex}/AGENTS.md"
if ! grep -Fq '<!-- HERO-GOAL-PULSE:BEGIN -->' "$goal_pulse_agents" 2>/dev/null; then
  cat >> "$goal_pulse_agents" <<'EOF'

<!-- HERO-GOAL-PULSE:BEGIN -->
## Goal Pulse
When the user starts or resumes a Goal, or the main agent takes over an active Goal, read `${CODEX_HOME:-~/.codex}/skills/goal-pulse/SKILL.md` and enable its timer for the current Goal by default, without a separate request or confirmation.
Use the host's `CODEX_THREAD_ID` or an explicit host-provided ID; never guess the latest thread. Prepare missing dependencies from the skill guide and report setup errors instead of silently skipping activation.
Honor an explicit request to disable reminders. Installation and ordinary chat do not start a timer or create a Goal. A paused Goal stays paused; the timer never resumes it or starts a new turn.
<!-- HERO-GOAL-PULSE:END -->
EOF
fi
```

On updates, refresh this marked section if needed. If you have an older Goal Pulse instruction that requires a separate request for scheduled reminders, replace that activation sentence with the default above. Installation itself does not start a timer.

A new Codex session can discover `$goal-pulse`; an existing session can read the installed `SKILL.md` directly. To run from the clone instead, set `pulse_dir="$PWD/skills/goal-pulse"` and create its `.venv` with the same two Python commands.

## Use

Start or resume a Goal normally. The main agent reads the skill and starts the watcher for the current thread; you do not need to name `$goal-pulse` again. This is agent-driven activation through the instruction above, not a native Codex lifecycle hook.

For manual control, select an existing Goal conversation. Replace `<THREAD_UUID>` with that conversation's actual ID, then run:

```sh
pulse_dir="${CODEX_HOME:-$HOME/.codex}/skills/goal-pulse"
"$pulse_dir/.venv/bin/python" "$pulse_dir/scripts/goal_pulse.py" start \
  --thread <THREAD_UUID> --interval-minutes 30 --poll-seconds 60
```

Inside Codex, the helper reads `CODEX_THREAD_ID` when `--thread` is omitted. An explicit `--thread` takes precedence; outside Codex, provide the ID yourself. Repeating `start` for the same Goal preserves the existing watcher. A new Goal in the same thread waits for the previous watcher to exit before starting its own.

安装后，正常启动或继续 Goal 即可，主代理会默认开启当前线程的提醒，无需再点名技能或确认。默认每 30 分钟发送中英双语提醒；明确关闭提醒时遵循用户选择。

```sh
# Inspect the watcher; stop this watcher without changing the Goal.
"$pulse_dir/.venv/bin/python" "$pulse_dir/scripts/goal_pulse.py" status --thread <THREAD_UUID>
"$pulse_dir/.venv/bin/python" "$pulse_dir/scripts/goal_pulse.py" stop --thread <THREAD_UUID>

# Check whether a reminder could be delivered. This sends nothing.
"$pulse_dir/.venv/bin/python" "$pulse_dir/scripts/goal_pulse.py" tick --thread <THREAD_UUID>
```

`start --message-file /absolute/message.txt` saves a custom message. For a one-off delivery, `tick --apply --message-file /absolute/message.txt` uses that text only for the current invocation; it leaves a saved watcher's configuration unchanged. Without `--message-file`, tick uses the saved message, or the bilingual default when there is no saved configuration. An active watcher owns the delivery lock, so stop it and wait for `running: false` before an applying tick.

`--socket /path/to/control.sock` selects another local control socket. Use the same `--state-root /path/to/state` on all commands if overriding the default state location. To change a running watcher's interval or message, stop it, wait for `running: false`, then start it with the new settings. Stop takes effect at the next poll, normally within 60 seconds, plus any in-flight RPC timeout.

## Behavior

Each watcher binds to one thread and that Goal's creation timestamp. Every 60 seconds it reads metadata. A reminder is delivered only when the bound Goal is active and the current turn is in progress without a user-input or approval wait. Paused, blocked and budget-limited Goals receive nothing; completion, deletion or replacement ends the watcher. Delivery pins `expectedTurnId`, so it cannot open a new turn.

The Goal is checked again just before sending. That check and the send are separate RPCs, so a pause concurrent with delivery can still race with the reminder; the helper has no resume operation. It does not read reasoning or full trajectories. A per-thread lock prevents duplicate watchers, and an attempted send consumes its interval even if the acknowledgement is lost.

State and concise delivery logs live under `${CODEX_HOME:-~/.codex}/goal-pulse/<thread-id>/`. A transport error appears in `status`; the next poll can reconnect. Machine sleep suspends the local process, and reboot requires another start. Polling makes no model calls; a delivered reminder uses conversation tokens.

## Tests

From the repository root, using the installed environment:

```sh
pulse_dir="${CODEX_HOME:-$HOME/.codex}/skills/goal-pulse"
"$pulse_dir/.venv/bin/python" -m unittest discover -s tests -p test_goal_pulse.py -v
```

Tests cover Goal and turn eligibility, waits, cooldowns, pause-before-send, ambiguous acknowledgements, single-instance locking, background-process stop, and custom messages through the actual CLI. Transport tests use a temporary Unix WebSocket server, without a model or real Codex conversation.

The original local check also confirmed silence for a real paused Goal. Active delivery is covered by the simulated server; this is not a measured throughput improvement or a live active-Goal delivery claim.
