# Installing the block

[`../RULES.md`](../RULES.md) is the canonical copy of the block. The READMEs
repeat it so the front page is usable without a second click — two copies per
language, which is a real synchronization cost, accepted here in exchange for
that. It has already been paid once: the README copies had silently drifted from
RULES.md before anyone noticed. So edit RULES.md first, then sync the READMEs.
Paste the block into the file your agent loads automatically.

| Host | File it reads | Scope |
|---|---|---|
| Claude Code | `CLAUDE.md` in the project root, or `~/.claude/CLAUDE.md` | project / global |
| Codex | `AGENTS.md` in the project root | project |
| Antigravity | `AGENTS.md` in the project root, or `~/.gemini/AGENTS.md` | project / global |
| GitHub Copilot | `.github/copilot-instructions.md` | repository |
| Cursor | `.cursor/rules/*.mdc`, or a legacy `.cursorrules` | project |
| Windsurf | `.windsurfrules` | project |
| Gemini CLI | `GEMINI.md` | project |
| Anything else | whatever that host loads unprompted | — |

Codex and Antigravity read the same filename, so one `AGENTS.md` serves both.

The block is the only thing you paste. The case catalogue is not part of the
install — see [why, and what it *is* for](../cases/README.md#how-to-use-this).

## Why there are no ready-made files here

A directory of six near-identical host files would be six more copies to keep in
sync, added for a convenience nobody asked for. That is `HERO-O`. A table of
destinations costs a reader ten seconds instead.

## Put it where it is always loaded

An invoked copy is not useless, but it is absent exactly when you need it most:
on the long unattended runs, where nobody is there to invoke it and where this
failure costs a night. Always-loaded placement buys coverage — it does not buy
compliance.

## If it still drifts on a long run

Loading the block once is not the same as it staying salient. On long unattended
runs it can fade — see [the limitation in RULES.md](../RULES.md#what-this-does-not-do)
for how to tell erosion apart from being contradicted, because only one of them
is worth acting on.

If yours is erosion, both Claude Code and Codex have hook systems that can put
text back into the model's context at defined points in a session, including
around compaction. Claude Code additionally has scheduled prompts. Have the hook
print the block you already installed, so there is still one copy. Their event
names and which events can inject context both change between releases, so check
the current references — [Claude Code hooks](https://code.claude.com/docs/en/hooks),
[Codex hooks](https://learn.chatgpt.com/docs/hooks) — rather than trusting a
snippet. Not every event can inject; some only observe or block.

**A wall-clock timer is the wrong shape for re-injecting the full block**, even where one is available.
Context grows with work, not with minutes: a busy run can bury the block in ten
minutes while an idle one sits untouched for hours. Fire on session events, not
on the hour.

This hook setup is optional host configuration, separate from installing the
core rules.

## Goal execution reminders

[Goal Pulse](../skills/goal-pulse/README.md) addresses a different long-run problem:
finished worker outputs waiting for pickup, repeated attempts at the same blocker,
and reports replacing execution. It sends a short action reminder every 30 minutes
to an existing active Codex Goal turn, with no separate report expected. After
installation, its activation instruction makes the main agent start it by default
when the user starts or resumes a Goal, or the main agent takes over an active Goal.
No separate skill invocation or confirmation is needed.

The timer requires a compatible local Codex app-server on macOS or Linux/POSIX.
It stays silent while the Goal is paused or waiting for input, and stops when the
Goal finishes or is replaced. It does not start a new turn or resume work. This is
an optional tool with its own installation; the core HERO rules still need only
the configuration block above.

**Claude Code** uses the same [Goal Pulse skill with native cron / `/loop`](../skills/goal-pulse/README.md#claude-code).
Install its Markdown files and activation instruction in `CLAUDE.md`; on `/goal`
start/resume or explicitly authorized long autonomous work, the main agent enables
a 30-minute reminder by default. No Python helper is needed. Cron handles prompts
between turns, and the agent cancels this task's reminder on completion, pause, or
an input/approval/budget stop. An explicit reminder opt-out remains in effect until
the user re-enables it. Other scheduled tasks and `loop.md` keep their own behavior.

## Placement inside the file

Near the top, in its own section, above any project-specific instructions. The
reasoning: instructions competing for the same decision plausibly resolve toward
whichever is more specific, and the block is deliberately general — better as the
frame than as a footnote. It also survives edits to the project-specific part
below it.

Treat that as a preference, not a measured effect. We have not tested it, and the
one-command install in the README appends to the end of the file, which we
consider fine — appending cannot damage what is already there, and buying a
top-of-file position would mean rewriting someone's config through a temp file
for an ordering effect nobody has demonstrated.

What *has* been reported is that the axis is specificity, not position: a general
"use only the checks you need" lost to a twelve-stage workflow written into the
same prompt, and moving it would not have saved it. If something in your config
is beating the block, look for the more concrete instruction before you look at
the line number — [`RULES.md`](../RULES.md#what-this-does-not-do) has the case.

## If you also review with a second model

If your workflow has one model reviewing another's work, the reviewer needs the
block too, and needs it more. A reviewer asked to be adversarial, given repository
access and told to propose fixes is the single most productive source of the
behaviour catalogued here. Put it at the end of the reviewer's prompt, after the
output-format instructions — that position reads as the final governing
constraint rather than as background.
