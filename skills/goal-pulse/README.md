# Goal Pulse for Codex

Keep a long-running Goal moving: collect finished worker artifacts, take over recurring blockers, and spend the next step on the deliverable. Goal Pulse provides a Codex skill and an optional local reminder every **30 minutes**, in Chinese and English.

The timer nudges an existing active turn. It does not create work, resume a paused Goal, or ask for another progress report. HERO's [core rules](../../RULES.md) still work by pasting them into your agent configuration; this helper is a separate, optional installation.

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

For an existing installation, keep any local instructions and update the files you intend to replace. Keep its `.venv` and the separate per-thread state directory. Nothing here edits your global `AGENTS.md` or starts a timer.

A new Codex session can discover `$goal-pulse`; an existing session can read the installed `SKILL.md` directly. To run from the clone instead, set `pulse_dir="$PWD/skills/goal-pulse"` and create its `.venv` with the same two Python commands.

## Use

Select the existing Goal conversation you want to nudge. Replace `<THREAD_UUID>` with that conversation's actual ID, then run:

```sh
pulse_dir="${CODEX_HOME:-$HOME/.codex}/skills/goal-pulse"
"$pulse_dir/.venv/bin/python" "$pulse_dir/scripts/goal_pulse.py" start \
  --thread <THREAD_UUID> --interval-minutes 30 --poll-seconds 60
```

You can also tell the agent:

> Use `$goal-pulse` to remind this existing Goal every 30 minutes. Collect finished work promptly, take over recurring blockers, and continue the next authorized step without writing a separate reply to each reminder.

> 用 `$goal-pulse`，每 30 分钟提醒这个已有 Goal。完整产物及时回收，反复卡住的具体问题及时接管，继续下一步已授权工作，不用专门回复提醒。

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
