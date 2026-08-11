# Installing the block

[`../RULES.md`](../RULES.md) is the canonical copy of the block. The READMEs
repeat it so the front page is usable without a second click — two copies per
language, which is a real synchronization cost, accepted here in exchange for
that. It has already been paid once: the README copies had silently drifted from
RULES.md before anyone noticed. So edit RULES.md first, then sync the READMEs.
Paste the block into the file your agent already reads on every turn.

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
