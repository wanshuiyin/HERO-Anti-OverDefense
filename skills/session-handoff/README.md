# Session Handoff

Carry a task into a fresh conversation with its objective, decisions, evidence,
running work, and next action intact on disk. The skill prepares a usable handoff
and guides the new session through taking over the work. It reuses your project's
existing recovery documents; otherwise it writes `HANDOFF.md`.

This is a Markdown skill for Codex and Claude Code. It needs no Python package,
API key, or background process. Read the complete [skill](SKILL.md) for the
preparation and continuation workflow, examples, and handoff template.

## Install

From a clone of this repository, copy the directory into the host you use. These
commands leave an existing installation alone; compare it with the repository
before updating so local instructions are preserved.

For Codex:

```sh
handoff_dir="${CODEX_HOME:-$HOME/.codex}/skills/session-handoff"
if [ -e "$handoff_dir" ] || [ -L "$handoff_dir" ]; then
  echo "Already installed at $handoff_dir; compare before updating."
else
  mkdir -p "$(dirname "$handoff_dir")"
  cp -R skills/session-handoff "$handoff_dir"
fi
```

For Claude Code:

```sh
handoff_dir="$HOME/.claude/skills/session-handoff"
if [ -e "$handoff_dir" ] || [ -L "$handoff_dir" ]; then
  echo "Already installed at $handoff_dir; compare before updating."
else
  mkdir -p "$(dirname "$handoff_dir")"
  cp -R skills/session-handoff "$handoff_dir"
fi
```

You can also ask an agent to read `skills/session-handoff/SKILL.md` from the
clone directly. This works before a new session refreshes its skill catalogue.

## Use

In the current Codex session:

```text
$session-handoff prepare a handoff for a fresh session. Preserve our full
objective and latest decisions, check the current artifacts and running tasks,
and give me the exact prompt to paste into the new session.
```

The agent updates the existing recovery entrypoint and returns its path and a
starting prompt. Open a fresh session in the same project or worktree and paste
that prompt. It points to the actual skill and project files, so the new agent
can start from the recorded next action. For an existing handoff:

```text
$session-handoff continue from NEXT_SESSION.md. Check the current files and
active jobs, then carry out the next authorized action.
```

Replace `NEXT_SESSION.md` with your project's actual entrypoint. Claude Code
uses the same requests with `/session-handoff` in place of `$session-handoff`.
Natural-language requests such as “prepare a handoff before I open a new
session” also fit the skill.

The user opens the fresh session. The skill does not launch one, move a Goal
between threads, or reset its budget. Existing worker ownership and any paused
Goal remain in force. Goal Pulse continues to follow its own thread binding;
this skill does not change the timer.

## How it fits HERO and ARIS

HERO Rules keep effort on useful work. Goal Pulse reminds an active Codex Goal
to keep moving. Session Handoff preserves the state a new conversation needs.
Use the handoff when starting fresh will help the task; it has no fixed
compaction count or rotation schedule.

ARIS already has Pipeline Status, focused research contracts, research-wiki
notes, and workflow checkpoints. This skill uses those existing records rather
than introducing another state system. HERO maintains the single implementation
for both hosts.

中文：这个技能负责“交出去”和“接着做”两端。旧会话核对真实文件、已验证成果、失败路线、
未提交修改及在途任务，更新既有交接入口，并给出可复制的新会话提示；新会话按阅读顺序
恢复必要上下文、核对当前状态，然后继续已授权的下一步。只需 Markdown，不需要 Python，
也不会自动切换会话。Codex 用 `$session-handoff`，Claude Code 用 `/session-handoff`。
