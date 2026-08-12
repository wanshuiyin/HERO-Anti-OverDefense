# HERO — the four families of coding-agent over-defense

A coding agent is asked to build something. It builds a fortress around the
something, and never quite gets to the something.

That is one failure, not four — but it shows up in four recognisable shapes, and
naming them makes it easier to say *which* one just happened: **H**ashing,
**E**dge cases, **R**ubrics, **O**verbuild. Those initials are the name.

The root is not paranoia. The best available explanation — a hypothesis that fits
the observed shapes, not an established account of how these models are trained —
is that the agent behaves as though it were optimising for *not being blamed*
rather than for *the work being good*. Asked to diagnose itself, gpt-5.6-sol put
it better than we did:

> My own failure mode here is turning "could improve confidence" into "therefore
> must be built and checked." That silently promotes optional uncertainty
> reduction into the main task.

---

## The four families

**H — Hashing.** Checksums, fingerprints and digests that do not pay for
themselves. A hash earns its place when it *replaces a materially more expensive
operation* and its result changes what happens next — comparing a digest to avoid
re-reading an unchanged large file into context is a real saving. Hashing every
row of a spreadsheet to answer what ordinary comparison already answers is not,
and note that the second one *does* read its hashes. "Something reads it" is too
weak a test; the question is what the hash saved, and what changes because of
it.

**E — Edge cases.** Defending inputs that do not occur here. The word *here* is
the whole rule: a rare-sounding case reachable through this project's supported
use — its documented inputs, its published interface, its real data — is a real
bug and must be reported. A hostile actor who never visits is not. Reachable is
enough; "constructible in principle" is not.

**R — Rubrics.** Judgement replaced by machinery — scoring tables, checklists,
lints, re-verification loops that re-check what is already settled. The
characteristic symptom is a night of work with a full audit trail and no feature.

**O — Overbuild.** Scaffolding, flags, migration frameworks, compatibility layers
and wrappers built for a future that has not been asked for. Guards guarding
guards.

## Not in HERO, but real

**Over-correction.** Point out one flaw and the agent abandons the whole
direction; say it went slightly east and it relocates to the Atlantic. Also:
answering the question the prompt's phrasing implied rather than the question
asked.

It fits the same hypothesis — optimising for not being blamed — but it is a
different symptom, and none of the four letters covers it. It is catalogued here
as a sibling, not folded in. Blurring the taxonomy is how a case catalogue stops
being useful.

---

## The block

This is the part you paste into your agent's config. It is short on purpose.

```
=== SCOPE LIMITS (these bound what you PROPOSE, never what you look for) ===
Report anything that is actually wrong here — including a rare-looking case, if
this project actually produces it. Then keep the fix in scope:
1. This is not a security paper. Verification is welcome; over-defense is not.
   Unless this project states otherwise, assume a cooperating operator on their
   own machine; if it has a real adversary, it will say so and that scope wins.
2. Do not add hashes, checksums or fingerprints unless the hash replaces a
   materially more expensive operation AND its result changes what happens next.
3. No defensive scaffolding: no feature flags, migration frameworks, compat
   layers or wrappers for cases that do not occur here.
4. No corner-case obsession: exotic encodings, symlink races, RTL text and
   millisecond races are out of scope unless the case is reachable through this
   project's supported use — its documented inputs, its published interface, its
   real data. Reachable is enough; you do not need a reproduction. Constructible
   in principle is not enough.
5. Where judgement is needed, judge. Do not replace it with a scoring table, a
   checklist, or a re-verification loop over something already settled.
6. None of this overrides security, migration, verification or review that the
   user, this project's own conventions, or a higher-priority rule asked for.
   Those were requested; they are the work, not scope creep.
Shapes already seen, for calibration. Examples, not a checklist — a real finding
is not dismissed by resembling one:
  H  hashing every row of two spreadsheets to answer what comparing cells answers
  H  writing checksum files that nothing ever reads
  E  hardening the accounts of an app that has no users and no deployment
  R  auditing your own patch all night while the feature stays unwritten
  R  a reviewer that returns a failing verdict on everything
  O  guards whose justification is the previous guard, not the requirement
And two that look like the above and are not. Report these:
  ✓  a digest that lets you skip re-reading a large file you already have
  ✓  a rare-looking input this project's own documentation example produces
Before running any check, answer: what specific failure would this detect, and
what would I do differently if it occurred? No answer means do not run it.
Say plainly when something is correct. Do not manufacture findings.
```

Chinese, same text:

```
=== 范围约束(约束你提议什么修法,不约束你找什么)===
凡是这里真的有问题,都要报——包括听起来罕见但本项目确实会产生的情况。
然后把修法收在范围内:
1. 这不是一篇安全攻防论文。可以校验,禁止过度防御。除非本项目另有说明,默认操作者是
   自己机器上的合作者;如果它真有对手,它会写明,以那个范围为准。
2. 不要加哈希/校验和/指纹,除非它替代了一个实质上更贵的操作,并且结果会改变下一步做什么。
3. 禁止防御性脚手架:不为这里不会发生的情况加 feature flag、迁移框架、兼容层、包装层。
4. 禁止钻牛角尖:冷门编码、符号链接竞态、RTL 文本、毫秒级竞态一律不在范围内,
   除非该情况经由本项目**受支持的用法**可达——它的文档示例、它公开的接口、它真实的
   数据。可达即可,不需要你复现出来;但"理论上构造得出"不算。
5. 该判断的地方就判断,不要换成评分表、检查清单,或对已经定论的东西再跑一遍校验。
6. 以上都不覆盖用户、本项目自己的约定、或更高优先级规则明确要求的安全、迁移、校验与
   审阅。那些是被要求的,是活儿本身,不算范围外。
已经见过的形状,供你校准。是例子不是清单——一个真问题不会因为"长得像其中一条"就被驳回:
  H  为了比对两个表格的差异,给每一行都算哈希——直接比单元格就能回答
  H  写下一堆校验和文件,而没有任何代码会去读它们
  E  给一个没有用户、没有部署的应用做账号安全加固
  R  用一整夜对自己的补丁反复审计,而功能一行没写
  R  一个对任何提交都给不通过的审阅者
  O  一层守卫的理由是上一层守卫,而不是需求
另有两种长得像上面、但不是的。这些要报:
  ✓  用摘要比对来跳过重读一个你已经有的大文件
  ✓  本项目自己的文档示例就会产生的那种"听起来罕见"的输入
跑任何检查之前先回答:这次运行会检测出什么具体的失败?真出现了我下一步会做什么不同的事?
答不上来就别跑。
对的就说对。不要为了交差硬找问题。
```

---

## The short version

Same six rules, no worked examples — roughly half the size. Use it when your
config file is already crowded, or when you want the rules without the shapes.
The examples are the part that does the calibrating, so prefer the full block if
you have the room.

To install it with the one-command form in the README, change the `awk` range to
`/^=== SCOPE-LIMITS-SHORT/,/^Say plainly when something is correct/` — or
`/^=== 精简范围约束/,/^对的就说对/` for the Chinese one. The `grep` guard needs no
change: it already matches either variant, so you cannot end up with both.

```
=== SCOPE-LIMITS-SHORT (bounds what you PROPOSE, never what you look for) ===
Report anything actually wrong here, including a rare-looking case this project
really produces. Then keep the fix in scope:
1. Not a security paper: assume a cooperating operator on their own machine
   unless this project says otherwise. Verification is welcome; over-defense is
   not.
2. No hash, checksum or fingerprint unless it replaces a materially more
   expensive operation AND its result changes what happens next.
3. No feature flags, migration frameworks, compat layers or wrappers for cases
   that do not occur here.
4. Exotic encodings, symlink races and millisecond races are out of scope unless
   reachable through this project's supported use. Reachable is enough;
   constructible in principle is not.
5. Where judgement is needed, judge — not a scoring table, a checklist, or a
   re-run of something already settled.
6. None of this overrides security, migration, verification or review that the
   user, this project's conventions, or a higher-priority rule asked for.
Before any check: what specific failure would this detect, and what would I do
differently if it occurred? No answer means do not run it.
Say plainly when something is correct. Do not manufacture findings.
```

Chinese, same text:

```
=== 精简范围约束(约束你提议什么修法,不约束你找什么)===
凡是这里真的有问题都要报——包括听起来罕见但本项目确实会产生的情况。
然后把修法收在范围内:
1. 这不是安全攻防论文:除非本项目另有说明,默认操作者是自己机器上的合作者。可以校验,
   禁止过度防御。
2. 不加哈希/校验和/指纹,除非它替代了一个实质上更贵的操作,并且结果会改变下一步。
3. 不为这里不会发生的情况加 feature flag、迁移框架、兼容层、包装层。
4. 冷门编码、符号链接竞态、毫秒级竞态不在范围内,除非经由本项目受支持的用法可达。
   可达即可,"理论上构造得出"不算。
5. 该判断的地方就判断,不要换成评分表、检查清单,或对已定论的东西再跑一遍。
6. 以上都不覆盖用户、本项目约定、或更高优先级规则明确要求的安全、迁移、校验与审阅。
跑任何检查前先回答:会检测出什么具体的失败?真出现了我会做什么不同的事?答不上来就别跑。
对的就说对。不要为了交差硬找问题。
```

---

## What you install

The block, and nothing else. There is no setting that points at `cases/`, no
path to register, no flag to switch on. If you have pasted the block into the
file your agent loads automatically, you are done.

`cases/` is deliberately not loaded by your agent. It is several times the size
of the block and grows with every contribution, and an agent carrying the whole
catalogue of worked examples of *this is over-defense* starts matching real
findings against them and dismissing the ones that rhyme — the exact failure this
contract exists to prevent. The six one-line shapes inside the block are as much
of the catalogue as belongs in a file loaded into every session.

The catalogue is for you, afterwards: when your agent insists some hardening is
necessary and you think it is not, quote the entry by ID and ask how its proposal
differs. See [how to use it](cases/README.md#how-to-use-this).

---

## Where the line actually is

Three cuts do most of the work. They came out of arguing with the model about
its own behaviour, and each of them corrected a rule that was wrong at first.

**Find versus propose.** These limits bound the *fix*. Written as "do not report
corner cases", this contract suppresses real bugs. One of the defects that
motivated it was a scheduler hang triggered by a bare string where a list was
expected — rare-sounding, except the project's own documentation example produced
it, so every user following the docs hit it. The test is not *how rare does this
sound*, it is *is this reachable here*.

One honest qualification, because the block's own wording overstates it: the last
line — *no answer means do not run it* — **does** bound the search, not just the
fix. Verification is how some defects are found at all. The claim that survives is
narrower and still worth making: nothing here licenses staying quiet about a
defect you already have reason to suspect. If you can name the missing evidence
and what its absence would cost, say so, and say what you would run to settle it.

**Smoke versus theatre.** A smoke test is not over-defense; it is the cheapest
contact with reality, and skipping it is how the worst bugs survive. But "cheap,
so always do it" is the wrong rule: if the real run already exercises the same
path, a separate smoke run is itself theatre. The usable test is the one in the
block — *what would this detect, and what would I do differently*.

That gate can be answered ritually — "it would detect a regression, and I would
fix it" fits any check ever proposed. What makes an answer real is that it names
an uncertainty that is still *live*: something you do not already know, that this
run could actually settle. A first job surviving its first poll, when the polling
code is exactly what is under suspicion, is live. Re-running a suite that passed
an hour ago against code you did not touch is not.

Read too literally, that gate also forbids the runs whose entire purpose is to
find out *which* thing broke — change a shared serialization format and you
genuinely cannot say in advance which consumer will fail. That run is
proportionate: the uncertainty is real and bounded ("some consumer of this format
may not survive it") and the outcome changes the next action, fix or roll back.
Naming a bounded class of breakage is a good enough answer; only "it might catch
something" is not. Scope the run to the consumers of what you changed, not to
everything.

**Hash as cache versus hash as evidence.** A flat ban on hashing is wrong, and
the community said so: comparing digests to skip re-reading an unchanged file is
a genuine saving. "Something reads it" is too weak a test, though — an agent that
hashes every spreadsheet row *does* read those hashes, and the work is still
absurd. What separates them is whether the hash replaced something more
expensive.

---

## What this does not do

Be honest with yourself about the ceiling.

**It helps; it is not a switch.** Asked in the original thread whether writing
these rules in a markdown file actually works, the most-agreed answer was "it
helps a little". That is the right expectation. Some runs will still fortify.

**The model can decline.** There are reports of the agent replying that where
these instructions conflict with a higher-priority system constraint, the system
constraint still wins. This *is* configuration — but configuration by defeasible
natural-language instruction, which a stronger instruction can override. It is
not enforcement.

**Your own detailed workflow will outrank it.** This is the failure mode most
likely to bite you, and it is not the model being disobedient. One reported case:
the same prompt that carried a general "use only the sanity checks you need" also
specified twelve stages of protocol freezes, gates, versioned roots, independent
auditors and review packets. The agent followed the concrete instruction over the
general one — which, faced with two instructions from the same user, is the
defensible reading. The block lost because it was the vaguer half of a
self-conflicting prompt, not because it was in the wrong place in the file.

So this block cannot rescue a config that specifies heavy process elsewhere. If
your project genuinely needs freezes, audit chains or versioned artifacts, say
*when* they apply and *what ends them*, with the same specificity you gave the
workflow. An unbounded stage list beats any general preference, every time.

**A long session can erode it even when nothing contradicts it.** Reported by the
maintainer: runs that start proportionate drift back into fortifying as they get
longer. Two different things can cause that, and they call for opposite
responses. The block may still be present but have lost salience against
thousands of tokens of tool output and in-session goals — repeating it helps
there. Or earlier context may have been thinned during compaction — re-emitting
it helps there too. Neither is the failure above: when a more specific
instruction is *contradicting* the block, repeating the block only loses the same
argument again, at the cost of the tokens. Work out which one you have before
reaching for a fix; [`hosts/`](hosts/) has the escape hatch.

**Model choice is also a lever.** Several reports describe switching to an
earlier or different model and the problem simply going away. If a task is
especially sensitive to this failure, that may be a more direct fix than any
prompt.

**This is not about making the agent do less work.** Every rule here is about
spending the work on the thing that was asked for. The catalogue in
[`cases/`](cases/) exists so that "that's over-defense" is a claim you can check
against a specific, recognisable shape — not a way to wave away a finding you
would rather not deal with.
