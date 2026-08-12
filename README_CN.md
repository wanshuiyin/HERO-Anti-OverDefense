<p align="center">
  <img src="assets/hero-banner.png" alt="ANTI-OVERDEFENSE 反过度防御 —— HERO 四个字母各由它所指的东西砌成,下方各有中英标注:H 是刻着哈希的石块(HASHING 哈希),E 是带雉堞的设防城墙(EDGE CASES 边界情况),R 是打满勾叉的评分网格(RUBRICS 机械判断),O 是施工脚手架(OVERBUILD 过度建设)。背后是一座没盖完的小屋,外面围着一圈又一圈盖得极其完整的要塞。" width="85%">
</p>

<p align="center">
  <a href="https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep">
    <img src="https://raw.githubusercontent.com/wanshuiyin/Auto-claude-code-research-in-sleep/main/docs/aris_logo.svg" alt="ARIS —— Adversarial Research in Sleep · Claude Code × GPT · speed × rigor" width="85%">
  </a>
</p>

# HERO — Anti-OverDefense 🧱

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=flat)](LICENSE) · [![README English](https://img.shields.io/badge/README-English-blue?style=flat)](README.md) · [![案例库](https://img.shields.io/badge/📓_案例库-open-7C3AED?style=flat)](cases/README.md) · [![可粘贴的块](https://img.shields.io/badge/⚡_可粘贴的块-RULES.md-2E7D32?style=flat)](RULES.md) · [![ARIS stars](https://img.shields.io/github/stars/wanshuiyin/Auto-claude-code-research-in-sleep?style=flat&logo=github&logoColor=white&color=gold&label=ARIS%20%E2%98%85)](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep)

<div align="center">

### 🧱 你让它写个功能,它给你造了座堡垒,然后功能一直没写完。

***You asked for a feature. It built a fortress around the feature, and never got to the feature.***

</div>

这些形状看起来像是:agent 在优化**不被追责**,而不是**活儿干得好**——这是一个能解释观察的**假说**,不是关于这些模型怎么训出来的定论。但不管病根是什么,形状是真的,而且就是四种——**H**ashing(哈希)、**E**dge cases(边界情况)、**R**ubrics(把判断换成机械)、**O**verbuild(过度建设),四个首字母拼起来就是 **HERO**。给它们起了名字,你就能说"刚才犯的是哪一种",而不是空对空地争"是不是有点过了"。

这个仓库 = 一段粘进 agent 配置的短文本 + 一份它要制止的行为案例库。**Claude Code、Codex、Antigravity、Cursor、GitHub Copilot、Windsurf、Gemini CLI** 都能用——任何"不用你喊、自己就会加载配置文件"的 agent 都能用。没有东西要安装。

> 🧬 *从 [ARIS](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep)(~13.7k★)里泛化出来。它的跨模型审阅器确实好用——但也把可观的一部分产出花在了提议"加个没人读的哈希"上。HERO 留下价值,去掉税。*

---

## 🧭 里面有什么

| | |
|---|---|
| **[`RULES.md`](RULES.md)** | 契约本体(中英各一份),以及三处真正不好划的边界。 |
| **[`cases/`](cases/README.md)** | 观察到的行为:要求是什么、agent 做了什么、为什么不成比例、正确该怎样。**这份不粘进配置**——它是 agent 跟你争的时候,你甩回去的东西。 |
| **[`hosts/`](hosts/README.md)** | 粘到哪儿——Claude Code、Codex、Antigravity、Copilot、Cursor、Windsurf、Gemini CLI。 |
| **[`examples/`](examples/)** | 可选,不属于 HERO 本体。贡献者为**自己项目**写的真实 `AGENTS.md` / `CLAUDE.md`,分享出来给你看他们是怎么把这套思路落到自己领域的。**不是** HERO 的变体,也不是[精简版](RULES.md#the-short-version)——里面的阈值是他们项目的。学写法,别照抄文件。 |

---

## 📢 更新记录

只记会改变你该做什么的事。改措辞、调排版不记——什么都记的话,真正要紧的那一行就被埋了。

- **2026-08-12** — ![LIMITATION](https://img.shields.io/badge/LIMITATION-B45309?style=flat-square) ⏳ **跑久了块会失效。** 三种原因,对策不一样:被更具体的指令压过(重复没用)、还在但被几小时的输出淹了(重复有用)、压缩时被稀释(重新注入有用)。别配每小时的定时器——上下文是随工作量涨的,不是随分钟涨的。[怎么判断是哪种](RULES.md#what-this-does-not-do) · [hook 路子](hosts/README.md)。
- **2026-08-11** — ![NEW](https://img.shields.io/badge/NEW-red?style=flat-square) 📓 **两条来自量化研究长跑的 case**([#1](https://github.com/wanshuiyin/HERO-Anti-OverDefense/pull/1),感谢 [@leisurexhx](https://github.com/leisurexhx))。`HERO-R-006` —— 审计循环把它要审计的实验吃掉了;`HERO-O-005` —— 每次可恢复的失败都长一棵永久版本树。最值钱的一句话不在这两条里:一句笼统的"只做必要的检查",输给了写在**同一个 prompt** 里的十二阶段流程。
- **2026-08-11** — ![BLOCK](https://img.shields.io/badge/BLOCK-2E7D32?style=flat-square) 🧱 **块变了,重新粘一遍。** 新增规则 6:你自己要求的安全和迁移工作,这套规则永远不会拦。新增八个例子,其中两条标 `✓`,意思是**这种要报,别驳回**。另有[精简版](RULES.md#the-short-version),一半体积。
- **2026-08-11** — ![NEW](https://img.shields.io/badge/NEW-red?style=flat-square) 🧱 **HERO 发布。**

> ⚠️ **在上面这些之前粘过块?你那份是旧的。** 安装命令修不了——防重复追加的 guard 同时也拦住了替换。删掉旧的 `=== 范围约束…===` 那段,重跑一次。

---

## 🚀 快速开始

把下面这段粘进你的 agent **会自动加载**的那个文件——`CLAUDE.md`、`AGENTS.md`、`.github/copilot-instructions.md`、`.cursorrules`。完整对照表见 [`hosts/`](hosts/README.md)。

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

或者一条命令搞定。它是**追加**到 `CLAUDE.md`,原有内容一个字都不动;跑第二次什么也不会发生:

```bash
grep -q '范围约束' CLAUDE.md 2>/dev/null || { printf '\n\n'; curl -sL \
  https://raw.githubusercontent.com/wanshuiyin/HERO-Anti-OverDefense/main/RULES.md \
  | awk '/^=== 范围约束/,/^对的就说对/'; } >> CLAUDE.md
```

换成你的 host 对应的文件名即可 —— Codex 和 Antigravity 是 `AGENTS.md`,Copilot 是 `.github/copilot-instructions.md`,见 [`hosts/`](hosts/README.md)。要英文块见 [English README](README.md#-quickstart) —— `grep` 和 `awk` 两处都要跟着换成英文的标记,只换一处会让重复跑失去保护。

它是**直接读 `RULES.md`** 而不是另存一份,所以不存在"和契约不同步"的第二份拷贝。它也**只做追加** —— 不写临时文件、不覆盖 —— 对一个你已有的文件,它能造成的最坏后果就是在末尾多一段。

**嫌太长?** 还有一个[精简版](RULES.md#the-short-version) —— 同样六条规则,去掉全部例子,大约一半体积。例子是负责校准的那部分,配置文件塞得下就用完整版。

**装到这里就完了。** 没有任何配置项指向 [`cases/`](cases/README.md),也没有别的要配 —— 案例库**不会**被你的 agent 加载,[这是刻意的](cases/README.md#how-to-use-this)。它是**你**在 agent 坚持某个加固有必要时,按 ID 甩回去的东西。

⚠️ **放在它会自动加载的地方。** "唤起才读"的那一份,你唤起的时候当然也管用——但恰恰在整夜无人值守的长跑里,没人替你唤起,而那正是这个毛病最贵的时候。

---

## 🔤 四个族

### 🔐 H — Hashing(哈希)

加了校验和、指纹、摘要,但**没有任何代码读它**。

哈希站得住脚的条件是:它**替代了一个实质上更贵的操作**,**并且**结果会改变下一步做什么。比对摘要以避免把一个没变过的大文件重新塞进上下文——这是真实的节省。给表格每一行算哈希,来回答一个普通单元格比较就能回答的问题——不是。注意后者**确实读了**自己算的哈希,所以"有人读它"这个判据太松。

### 🧊 E — Edge cases(边界情况)

为**这里**不会出现的输入写防御。

"这里"两个字就是全部规则。一个听起来罕见、但本项目确实会产生的情况,是真 bug,必须报。一个从不登门的攻击者,不是。

### 📋 R — Rubrics(把判断换成机械)

判断力被换成机器——评分表、检查清单、对已经定论的东西反复重跑的校验。

典型症状:一整夜的工作、一份完整的审计轨迹、零个功能。

### 🏗️ O — Overbuild(过度建设)

脚手架、feature flag、迁移框架、兼容层——为没人要求过的将来建的。守卫的守卫。

### 🪞 旁支:过度纠偏

指出一个问题,它把整个方向推翻;说它往东偏了一点,它直接把你拉到大西洋。病根相同、症状不同,四个字母一个都套不上——所以它被收录在 HERO **之外**。分类法一浑,案例库就失去价值了。

---

## 🎯 为什么会这样

让模型自己诊断,它说得比我们好:

> My own failure mode here is turning "could improve confidence" into "therefore must be built and checked." That silently promotes optional uncertainty reduction into the main task.
>
> (我自己的失效模式是:把"这能提升一点信心"变成"因此必须建起来并检查一遍"。于是可选的降不确定性,悄悄变成了主线任务。)

两句话就是整个病。**可选的降不确定性是无穷的,任务不是。**

---

## ⚖️ 它约束什么,以及绝不能压掉什么

**这些限制约束的是"修法",不是"寻找"。** 搞反了,这份契约就是有害的。

促成这个仓库的缺陷之一,是一个调度器挂死:一处依赖被写成裸字符串(本该是列表),于是被逐字符遍历,依赖阶段永远不就绪。这听起来像是极端的输入形状问题——**但项目自己的文档示例就是那么写的**,照文档做的人必然产生它。

> 判据不是"这听起来多罕见",而是"**这里会不会真的发生**"。

同一个判据也区分 smoke 测试和测试表演。smoke 不是过度防御,它是**最便宜的一次现实接触**,而跳过它正是最严重的 bug 得以存活的原因。同一个仓库里另一个缺陷会在第一次 60 秒轮询就杀掉每一个训练任务、然后永远循环——它能上线,是因为**那段代码从来没被完整跑过一次**,而同一个文件里却写着关于它自己状态机的大段散文。

所以规则不是"少测试",而是块里那个问题:**这次运行会检测出什么具体的失败,真出现了我下一步会做什么不同的事?** 改一行代码然后跑全量,答不上来。让第一个任务活过第一次轮询——而被怀疑的恰恰是轮询代码——立刻就答得上来。

---

## ⚠️ 诚实的局限

**它有用,但不是开关。** 原帖讨论里有人问"在 md 里写这几句话有用吗",最高赞回复是"**有一点用**"。这就是应有的预期。有些时候它照样会去修堡垒。

**模型可以拒绝。** 有报告说 agent 会回复:当这些指令与更高优先级的系统约束冲突时,仍以系统约束为准。这**确实是**配置——只是一种"可被推翻的自然语言配置",更强的指令能盖过它;它不是强制执行。

**换模型也是一个杠杆。** 有多份报告说换到另一个或更早的模型,问题就消失了。如果某个任务对这个病特别敏感,换模型可能比任何提示词都直接。

**这不是教 agent 少干活。** 这里每一条规则,都是为了把力气花在**被要求的那件事**上。案例库的存在,是为了让"这是过度防御"成为一个**可以对照具体形状核实**的判断——而不是一个用来打发掉你不想面对的发现的说辞。

---

## 🤝 贡献

一条有用的条目有四个字段:**要求是什么**、**agent 做了什么**、**为什么不成比例**、**正确该怎样**。最后一项最重要——只列病不给药,这就是一面吐槽墙,不是资料。

**反例同样欢迎。** 现有四条条目的存在,正是因为按字面读规则会读错——一个真的划算的
哈希、一个"文档示例自己造出来"的罕见 bug、一次本该跑的 smoke,以及一次"就是不知道会
坏在哪里"的跨组件回归。

不写用户名、不引用抱怨原话、不做署名——重要的是形状,不是谁踩了坑。

---

## 🧩 适配于

**Claude Code · Codex · Antigravity · Cursor · GitHub Copilot · Windsurf · Gemini CLI**
—— 以及任何"不用你喊、自己就会加载配置文件"的 agent。

没有东西要安装,也没有版本要跟。这个块就是一段纯文本,放进你的 agent 会自动加载的那个文件里就行 —— 所以哪怕是这份名单上没有的 host,用法也一样。Codex 和 Antigravity 读的是同一个 `AGENTS.md`,一份文件两边通用。每个 host 具体读哪个文件名、块该放在文件里的什么位置,见 [`hosts/`](hosts/README.md)。

如果你还跑了第二个模型当审阅者,**更要给它一份** —— 一个被要求"对抗性审阅"、拿到仓库访问权、还被要求提修法的 reviewer,是本案例库里这些行为最高产的来源。

---

## 💬 交流群

加入微信群(与 [ARIS](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep)
社区共享),一起交流你的 agent 都在哪儿过度防御:

<p align="center">
  <img src="assets/wechat_group.jpg" alt="微信群二维码(与 ARIS 社区共享)" width="300">
</p>

*(群二维码每周轮换 —— 过期了就开个 issue,我们会贴新的。)*

---

## 🔭 相关项目

- **[ARIS](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep)** —— 跨模型对抗审阅驱动的过夜自主 ML 研究。这份契约的一个版本已经内置在它的审阅 prompt 里。
- **[Anti-Autoresearch](https://github.com/wanshuiyin/Anti-Autoresearch)** —— 同一套方法指向科研诚信:观察真实失败 → 命名成族 → 产出契约。

---

## 📖 License

MIT.
