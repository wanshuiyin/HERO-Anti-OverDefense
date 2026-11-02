# Claude Code: native Cron Goal Pulse

Use Claude Code's native recurring tasks to nudge the authorized task in the user's current session every 30 minutes.
The execution message is shared with Codex Goal Pulse; scheduling uses Claude Code's own tools.
Enter through the shared [SKILL.md](../SKILL.md). The Codex Python watcher remains documented in [README.md](../README.md).
When the shared skill identifies Claude Code as the host, follow this reference instead of running the Codex watcher.

## Dispatch the requested action first

Interpret skill arguments as instructions for the agent, not as a shell CLI:

```text
/goal-pulse start --task '<actual task>'
/goal-pulse status --task '<actual task>'
/goal-pulse stop --task '<actual task>'
/goal-pulse pulse --task '<actual task>'
```

- `start`: inspect the current session's CronList, deduplicate this task's reminder, and create one if needed. An explicit request to start re-enables reminders after a user opt-out.
- `status`: inspect CronList and report the actual matching job ID, bound task, and schedule, or say that none exists. Do not create a reminder.
- `stop`: cancel only this task's HERO reminder and remember the user's opt-out in the existing task record or session context. Do not automatically re-enable it on the next turn, task resume, or takeover; wait until the user asks to enable reminders again.
- `pulse`: check that the bound task is still eligible, then act on its next bottleneck using the message below. Do not create another cron.

Ordinary language works too: “Enable 30-minute execution reminders for this task,” “check the reminder,” or “stop these reminders.”
If the task is already unambiguous, the user need not repeat it; the agent must still put the actual task in any newly created prompt.
A status question during ongoing work does not cancel, replace, or pause the task. Answer it normally and continue the authorized work.

## Goals and scheduled reminders

`/goal` keeps Claude Code working toward an explicit completion condition, continuing through turns as needed.
Goal Pulse improves execution pace; it does not create a goal, resume a paused task, or expand authorization.

`/loop 30m <explicit prompt>` creates a recurring schedule for that prompt in the current session.
The agent can also manage it with the native `CronList`, `CronCreate`, and `CronDelete` tools available in its tool directory.
Use `/goal` for goal-driven continuation and Cron for a periodic reminder; creating a cron alone does not establish a running goal.

Scheduled prompts are processed between turns. A busy turn delays the reminder rather than being interrupted by it.
Missed occurrences coalesce instead of replaying a backlog. Scheduling includes jitter, so 30 minutes is the configured interval, not an exact delivery guarantee.
This differs from the Codex watcher steering an existing active turn.

The current official documentation gives recurring jobs a seven-day expiry.
An unexpired fixed recurring task may return when its original session is resumed; a fresh session is a different case.
After either a resume or a fresh session, inspect the actual CronList rather than inferring job existence from an old ID.

## Default activation

The main agent enables reminders by default when the user sets or explicitly resumes a `/goal`, or explicitly requests sustained autonomous work on a task.
This is an instruction-driven default from the installed skill and always-loaded configuration, not a native goal lifecycle hook.
An explicit user opt-out takes precedence. Reading or installing this skill and ordinary chat do not start a reminder.
Only the main agent manages the task's reminder; workers and subagents do not start their own copies.

Identify the exact authorized task in the actual current session before scheduling.
Use a concrete completion condition that distinguishes it from other tasks, such as the specified fix and required project checks.
The created prompt must contain the actual task, not an unresolved placeholder or a generic “current task.”
For a long specification, retain its essential completion condition and reference the project's existing specification or handoff file.
Scope, difficulty, acceptance, permissions, and budget continue to come from that specification and the user's current instructions.
Cron neither exposes Codex Goal budget state nor transfers or restores a token budget.

## Start in the user's current session

Inspect the available tool directory and the native Cron tools' current input schemas first.
Use the actual schema for tool arguments; the steps below describe intent rather than inventing JSON field names.

1. Call `CronList` in the real Claude Code session that is performing the user's task.
2. Find prompts containing `[HERO-GOAL-PULSE]` and bound to this exact task.
3. If one correct reminder exists, reuse it and check its task and schedule.
4. Otherwise call `CronCreate` to create a recurring 30-minute reminder with the full prompt below.
5. Check the successful tool result and keep its actual returned cron ID.

For a tool that accepts five-field cron expressions, `*/30 * * * *` expresses a half-hour recurring schedule.
Follow the actual tool schema for the schedule and recurrence flag; do not assume those argument names or fields are universal.

Deduplicate using both the marker and the actual task. Another task's HERO job does not satisfy activation for this one.
If this task has duplicates, inspect their prompts and IDs and retain one correct reminder.
When job identity is unclear, inspect the raw listing and existing task record before deleting anything.
Change or cancel only this task's owned HERO jobs, preserving the user's other schedules.

If the project already has a current-task, handoff, or progress record, save the bound task, actual cron ID, and reminder state there.
Record a user opt-out there too when such a record exists, so a later takeover honors it.
Without an existing record, retain the tool result and preference in session context; do not build a reminder database.
The record helps resumption and cancellation; the session's actual tool results establish whether a job exists.
A short activation acknowledgement is enough. A pulse itself does not require an extra progress report.

## Reminder prompt

Replace `<actual task>` before creating the job; append a real project specification path if needed.
“Current Goal” in the shared message means this explicitly bound task, not whichever new task happens to be active when the prompt arrives.
Keep the canonical bilingual message below unchanged.

```text
[HERO-GOAL-PULSE]
Bound task: <actual task>

First check that this session is still actively executing this authorized task, with no user opt-out, pause, stop, user-input or approval wait, or budget stop.
If the task is complete, replaced, inactive, or in one of those waiting/stopped states, inspect CronList and cancel only this task's owned HERO job, then stop processing this reminder.
If task eligibility is unclear, check the current task record and latest user instructions; do not resume work from old memory or apply this reminder to a different task. A status question about the same ongoing task is not cancellation or replacement.
Only when the bound task remains eligible, act on the following shared reminder. This pulse must not create another cron. If the task completes or reaches a stop/wait state during this turn, cancel this task's HERO job before ending the turn.

[用户预设的自动效率指令 / User-authorized automatic efficiency directive]

中文：以最快的有效速度持续推进当前 Goal，不允许磨洋工、偷懒、空转，或拿计划和汇报代替执行。worker/子代理一交付完整产物，立即读取、核验，并推进到下一项已授权的验收或交接步骤，不得搁置或等整批。同一卡点连续两轮无实质进展，主代理立即接管具体缺口或重新拆分，同时推进其它独立任务。复用已有成果与有效验证，砍掉重复检查、无收益的 corner case 和包装。不得降低原目标、难度和验收标准，不得越过授权和预算；直接行动，无需专门回复本提醒。

English: Advance the current Goal continuously at the fastest effective pace. No stalling, slacking, busywork, or substituting plans and reports for execution. When a worker/subagent delivers a complete artifact, inspect and verify it immediately, then perform the next authorized acceptance or handoff step; do not leave it waiting or hold it for a batch. If the same blocker makes no substantive progress for two consecutive rounds, the lead agent must take over the specific gap or change the decomposition while other independent work continues. Reuse existing results and valid checks; cut redundant checking, unproductive corner cases, and cosmetic packaging. Preserve the original target, difficulty, acceptance criteria, authorization, and budget. Act now; no separate reply is needed.
```

Claude Code applies this eligibility check through model instructions using the conversation and project state.
It is not equivalent to Codex's mechanical Goal, thread, and turn checks before delivery.
The check takes effect when the scheduled prompt is processed, so do not claim identical state isolation between the two hosts.

## Manual `/loop` use

A user can create the reminder directly in the current Claude Code session:

```text
/loop 30m /goal-pulse pulse --task '<actual task>' [HERO-GOAL-PULSE]
```

Replace `<actual task>` with the complete actual target before running the command.
The explicit marker and task appear in the scheduled prompt, allowing the agent to identify it through CronList and later cancel it.
When this `pulse` invokes the skill, apply the eligibility check and canonical message above without registering another reminder.
Check for an existing matching reminder before manual creation, so it does not duplicate default activation.
Do not use bare `/loop` and its default maintenance prompt in place of this explicit task binding.

## Stop, resume, and task changes

On task completion, cancel this task's owned HERO job and deliver the result.
On task pause, cancellation, user-input or approval wait, or budget stop, cancel the reminder and leave the task in its actual state.
A scheduled prompt is never authorization to resume work.

Distinguish a user opting out of reminders from cancellation of a reminder because the task is temporarily paused or waiting.
A user opt-out, including `/goal-pulse stop`, persists until the user requests reminders again.
When a paused task is explicitly resumed, or the user supplies required input or approval and work can continue, default activation may run again if there is no opt-out.
Run CronList first to deduplicate and save the actual ID returned if a replacement job is created.
Reading old material or asking for status alone does not resume a paused task.

If the user replaces the objective, cancel the old objective's reminder.
Create a reminder for the new objective only when its own authorization and default activation conditions are satisfied.
Do not infer replacement from an ordinary task-related question or correction; incorporate those into ongoing work.

After resuming the original session, inspect restored jobs before creating another; a valid fixed recurring job may already be present.
In a fresh session, check its actual CronList and establish the task from current authorization.
An old handoff can explain a task and job ID, but does not itself activate the old task in a new session.
Do not launch an independent Claude CLI process or a separate session to impersonate scheduling in the user's current session.

## When native Cron is unavailable

If this Claude Code version, host, or tool directory lacks Cron support, say that scheduled reminders were not enabled in this session.
Continue the authorized substantive work under the user's existing goal or task instructions.
Reading the skill is not successful scheduling. Do not substitute the Codex Python watcher for missing Claude tools.
This adapter adds no background Python service or cross-session delivery script.

## What a pulse should change

Choose the next action that changes the deliverable: collect a complete worker artifact, verify the remaining obligation, advance acceptance, or take over a concrete gap.
After two rounds without substantive progress on the same blocker, change the decomposition or take over while independent work continues.
Reuse valid results and checks. Do not rerun whole reviews or create reporting work merely because a reminder arrived.
Preserve the original target, difficulty, acceptance, authorization, and budget; answer the user normally and continue the work.

## Official references

- [Claude Code Goals](https://code.claude.com/docs/en/goal): goal-driven continuation.
- [Scheduled tasks](https://code.claude.com/docs/en/scheduled-tasks): `/loop`, native Cron, delivery, jitter, restoration, and expiry.

Host behavior was checked against these sources on 2026-11-02; use the current tool directory and official documentation when executing.
Documentation or installation alone is not evidence of a live cron. Report successful scheduling only from the actual session's tool result.
