# 🧠 Zotero 编译型知识库 · Zotero Compiled Knowledge Base

> 把你 Zotero 里的论文，提前「编译」成可复用的研究判断——让你能像问一个读过你所有论文的助手那样，用大白话跟它讨论。
> Pre-*compile* the papers in your Zotero into reusable research judgments — so you can talk to a *second brain* that has read everything you saved.

**🌐 [中文](#-中文) · [English](#-english)**

---

## 🧠 中文

### 📌 一、这是什么

一句话：**它把你 Zotero 里的论文，提前编译成可复用的判断，让你用大白话就能跟它讨论你的研究。**

它**不是**收藏夹、**不是** RAG、**不是**论文备份。它是一个跑在 Claude Code / Codex 里的 AI 助手 + 一套本地 Markdown 文件：你的论文留在 Zotero（它只读、绝不动），真正长出来的价值，是它替你写下的**单篇判断、主题综述和选题**。

### 😩 二、它解决什么问题

每个做研究的人都干过同一件事：看到好论文 → 存进 Zotero → 然后就忘了。📚
存了几百篇，真到写综述、找创新点时，还是得一篇篇重新打开、重新读、重新在脑子里拼。

**问题的本质**：Zotero（以及几乎所有笔记工具）只解决了「把论文存好」，没解决「把论文变成你脑子里能直接用的判断」。**你存下来的是信息，不是知识。** 这个项目补的就是后半段。

### 🧩 三、核心原理：编译，而不是检索（最重要的一节）

这是它和市面上工具最根本的不同。先讲清楚，后面的操作才好懂。

**普通收藏夹**：只管存。论文之间没有关系，越存越乱，最后变成一个黑洞。

**RAG（市面上大多数「AI 知识库」）**：把论文切成小块、转成向量；你提问时，它临时捞几块相关的喂给 AI 现场作答。问题是——**它每次提问都从零理解一遍，理解从不沉淀下来。**

> 🍳 打个比方：RAG 像一个每次点菜才跑去仓库现切原料的厨子，每道菜都从生料开始，重复劳动。

**这个项目反过来：在你用之前，先把论文「编译」成结论。** 借编译器的比方——源代码（论文）经过编译，变成可直接运行的程序（判断）。它分两步：

**第 1 步 · 蒸馏（把一篇论文读透，且只读一次）**
AI 把一篇论文的全文**完整、客观地**读一遍，提炼成一份「蒸馏笔记」：研究问题、方法与创新、关键结果与数据、硬伤与局限……尽可能全面、不带目的。
🔑 关键：**这篇论文的全文，一辈子只在这一步读一次**，之后永久缓存成这份笔记。

**第 2 步 · 编译（把一个方向的多篇笔记，归纳成一页判断）**
当你要梳理某个方向时，AI **只读那些便宜的蒸馏笔记**（而不是重读全文），把它们归纳成一篇「综述页」：这个方向有哪些问题、方法怎么演进、有什么共识与分歧、还剩哪些空白。

> 💡 为什么分两步？因为「读全文」是最贵的（费时间、费 token）。把它**只做一次**、之后全靠便宜的笔记反复复用，「大量精读」才划算。这正是它能当第二大脑、又不烧爆成本的核心。

**🔄 还有一个关键设计：往回织（知识会沉淀，不是堆叠）**
你加一篇新论文，它不会像收藏夹那样「又多一条孤岛」。它会**回头**把相关的综述页重写一遍——补进新发现、更新脉络，甚至标出新论文和旧结论的矛盾。知识被一点点「织」进已有的网里，越用越完整。

**一张表看懂它和 RAG 的不同：**

| | 🔍 RAG | 🧠 本项目（编译型） |
|---|---|---|
| 何时「理解」 | 每次提问现场算 | 提前蒸馏 + 编译一次，永久复用 |
| 给你什么 | 原文碎片 | 结构化的**判断 / 结论** |
| 加新论文 | 进向量库，互不相关 | **往回织**进已有判断，并标出矛盾 |
| 底层 | 向量 / embedding | 你的人工分类 + 客观笔记，**不用向量** |
| 没有 AI 时 | 一个向量库 | 一堆**人能直接读**的 Markdown 判断 |

核心四个字：**编译 > 检索**。

### 🏗️ 四、它的数据怎么流动（架构）

理解了「编译」，这张图就顺了——左边是你的论文，一步步被加工成右边的判断：

```
  Zotero（你的论文 · 唯一数据源 · 只读，绝不改）
        │  sync：机械、秒级，把「有哪些论文」读成目录
        ▼
  catalog/   论文目录 + 标签 / 分类 / 年份 + 方法×问题矩阵
        │  ① 蒸馏：每篇全文读一次 → 客观精华
        ▼
  notes/     蒸馏缓存（每篇一页，永久复用，不再回头读全文）
        │  ② 编译：只读 notes，归纳成判断
        ▼
  syntheses/ 你的第二大脑（综述 / 创新点 / 研究空白）
        ▲  ③ 往回织：加新论文 → 回头重写、标矛盾
        │
  indexes/OVERVIEW.md  会话入口：一开对话就知道「已经编译了什么」
        │
        ▼
  outputs/   你让它写出来的成稿（综述 / 选题 / 答疑）
```

各层一句话：

- **Zotero**：你的论文真身，工具全程只读。
- **catalog/**：机器生成的「有哪些论文」目录，随时可删可重建。
- **notes/**：蒸馏缓存——全文读一次的成果，是后面一切的便宜来源。
- **syntheses/**：编译产物，你真正的第二大脑。
- **indexes/OVERVIEW.md**：每次开对话，AI 先读它，立刻知道哪些方向已经编译好、能直接引用。
- **outputs/**：你让它写出来的最终文稿。

> 一条总原则：**机械活（同步、建目录、检索）交给脚本；语义活（读懂、归纳、判断）交给 AI。**

### ✨ 五、它能帮你做什么

正因为它是「编译」的，所以它不只能查，还能帮你**形成判断、甚至想出下一步**。直接说人话即可，复制下面的句子就能试：

- 🔎 **精准查找**：`我库里关于"冲突解脱"的论文有哪些？列出作者、年份。`
- 📝 **写文献综述**：`把"可解释性"这个方向编译成一篇综述。`（会按「求解方法 × 研究问题」双线梳理发展脉络）
- 💡 **找创新点 / 研究空白**：`这个方向有哪些还没人做的空白？`
- 🔀 **跨领域思维碰撞**：`鲁棒强化学习和扇区优化之间，有没有可做的机会？`
- 🎯 **反向给你派选题**：`我下一篇小论文能写什么？`

> 一句话：**RAG 帮你「找到原文」，它帮你「得到判断」，甚至「想出下一步做什么」。**

### 🚀 六、怎么用（从安装到日常）

#### 6.1 先准备三样东西

📚 装好 Zotero、里面有论文 · 🐍 Python · 🤖 Claude Code（或 Codex）。
完全不懂编程也没关系——下面绝大部分都让 AI 替你做，你主要动嘴。

#### 6.2 第一次：下载 → 打开 → 连 Zotero

1. **下载项目**，解压，放进任意文件夹（建议放 C 盘以外，例如 `D:\zotero-kb`）。
2. **在这个文件夹里打开 Claude Code**（或把 Claude Code 指向这个文件夹）。一打开，它会自动读到说明书 `AGENTS.md` / `CLAUDE.md`，**默认就变成你的「知识库助手」**，知道该怎么帮你。
3. **连上你的 Zotero**：直接对它说一句——
   > 我是新手，帮我连上我的 Zotero、装好依赖、做第一次同步。

   它会自动找到你的 Zotero 路径、填好配置、同步目录。整个过程你基本只动嘴。

#### 6.3 日常：你只管说人话

配置好之后，想查、想编、想写，全部用大白话说（参考第五节的例句）。**命令一个都不用记**——AI 已经从 `AGENTS.md` 读懂了全部规则与流程。

#### 6.4 ⚠️ 它为什么不一开机就自动把论文全编译好？

你可能会想：「既然编译这么好，干嘛不一打开就把我几百篇全编了？」——这是**有意**的设计，原因有二：

1. 💸 **蒸馏要读全文、很费 token**。把全库几百篇自动读一遍，又慢又烧钱，而且你未必关心每一篇。
2. 🗂️ **科研分类多而杂**。你的 collection / tag 往往很多，盲目全编、混在一起，反而会把不该混的内容搅乱。

所以它的原则是：**编译什么、什么时候编，由你说了算。** 你指哪个方向，它编哪个方向；你日常用到、读过的论文也会顺手蒸馏沉淀下来。这样既准、又不浪费。

#### 6.5 四种使用模式（它自动判断，你只管说）

- 🔍 **查询模式**（默认）：问问题、找论文、比较路线。只读，最安全。
- 📝 **产出模式**：写综述、列选题、做 rebuttal，成稿落到 `outputs/`。
- 🧠 **编译模式**：蒸馏论文、编综述、更新判断（养大脑）。
- 🛠️ **开发模式**：改脚本、模板、规则。

> 你不用记模式名——它从你的话里自动判断；要动笔写文件前会先跟你确认。

### 🔒 七、它绝不碰什么（隐私与安全）

- **只读你的 Zotero**，绝不修改、删除你的论文或 Zotero 数据。
- **绝不复制 PDF / 论文正文**进本库——只存索引、路径指针和 AI 的判断。
- **纯本地**：不是 RAG、不用向量库、不联网上传，数据都在你自己电脑上。

### 📚 八、想深入 / 开发者

- [`AGENTS.md`](AGENTS.md) / [`CLAUDE.md`](CLAUDE.md)：AI 运行时读的完整操作手册，所有编译纪律都在这。想懂设计，直接让 AI 念给你听。

<details>
<summary>🛠️ 开发者常用命令</summary>

Windows PowerShell 下建议先设 UTF-8：`$env:PYTHONIOENCODING='utf-8'`

```powershell
python scripts/zotero_query.py sync                 # 只读 Zotero，刷新 catalog/
python scripts/zotero_query.py search "冲突解脱"      # 定位用的全文检索
python scripts/zotero_query.py paper --key <key>    # 单篇元数据 + 标注 + 全文路径
python scripts/kb_index.py                          # 生成编译状态索引 + 会话入口
python scripts/check_structure.py                   # 结构与 frontmatter 校验
```

首次配置：把 `config.example.yaml` 复制为 `config.yaml`，填入你的 Zotero 路径（或让 AI 代填）。
</details>

### 🙏 九、灵感来源

本项目的核心理念受两处启发：Andrej Karpathy 公开提出的 **LLM wiki / 知识库编译**思路；以及 **stormzhang** 分享的 **fuxi** 知识库设计思路。本项目是把这些理念**用到科研 / Zotero 场景的独立实现**，代码与具体实现为作者自有，未包含他人未公开的技术细节。

---

## 🧠 English

### 📌 1. What is this

In one line: **it pre-compiles the papers in your Zotero into reusable judgments, so you can discuss your research with it in plain language.**

It is **not** a bookmark folder, **not** RAG, **not** a paper backup. It's an AI assistant running inside Claude Code / Codex plus a set of local Markdown files: your papers stay in Zotero (read-only, never touched), and the real value it grows is the **per-paper judgments, topic reviews, and writing ideas** it writes for you.

### 😩 2. The problem it solves

Every researcher has done the same thing: find a good paper → save it to Zotero → forget it. 📚
After hundreds of saves, writing a review or finding novelty still means re-opening, re-reading and re-assembling everything in your head.

**The root cause**: Zotero (and almost every note tool) only solves "store the papers well", not "turn papers into judgments you can use directly." **You saved information, not knowledge.** This project fills the second half.

### 🧩 3. Core principle: compile, not retrieve (the key section)

This is the most fundamental difference from existing tools. Get this first and the rest makes sense.

**A bookmark folder** just stores. Papers have no relationships; the more you save, the messier it gets.

**RAG (most "AI knowledge bases")**: chops papers into chunks, embeds them; at query time it pulls a few relevant chunks and feeds them to the AI to answer on the spot. The problem — **it understands from scratch on every question; that understanding never accumulates.**

> 🍳 An analogy: RAG is a chef who runs to the warehouse to slice raw ingredients *every time* you order — starting from scratch, over and over.

**This project flips it: it compiles papers into conclusions *before* you use them.** Like a compiler turns source code into a runnable program, it turns papers into judgments — in two stages:

**Stage 1 · Distill (read a paper thoroughly, exactly once)**
The AI reads a paper's full text **completely and objectively**, distilling it into a note: research question, method & novelty, key results & numbers, limitations & flaws — as comprehensive as possible, with no agenda.
🔑 Key: a paper's full text is read **only once, ever**, then cached forever as this note.

**Stage 2 · Compile (merge many notes of one direction into one judgment)**
When you want to survey a direction, the AI reads only the **cheap distilled notes** (not the full texts again) and merges them into a **synthesis page**: the problems, how methods evolved, consensus vs. disagreement, and remaining gaps.

> 💡 Why two stages? Reading full text is the expensive part (time and tokens). Do it **once**, then reuse the cheap notes forever — that's what makes "reading a lot, carefully" affordable, and what lets it be a second brain without burning your budget.

**🔄 One more key design: weave-back (knowledge accumulates, not piles up)**
Add a new paper and it won't just sit as another island. The AI goes **back** and rewrites the relevant synthesis pages — adding new findings, updating the storyline, even flagging contradictions between the new paper and old conclusions. Knowledge is woven into the existing web; it gets more complete the more you use it.

**RAG vs. this, at a glance:**

| | 🔍 RAG | 🧠 This (compiled) |
|---|---|---|
| When it "understands" | On each query, recomputed | Distilled + compiled once, reused forever |
| What you get | Raw snippets | Structured **judgments / conclusions** |
| Adding a paper | Into the vector store, disconnected | **Woven back** into existing judgments, flagging conflicts |
| Under the hood | vectors / embeddings | your human classification + objective notes, **no vectors** |
| Without the AI | a vector store | plain Markdown judgments **a human can read** |

The idea in three words: **compile > retrieve.**

### 🏗️ 4. How data flows (architecture)

With "compile" in mind, this reads top to bottom — your papers get refined step by step into judgments:

```
  Zotero (your papers · the single source · read-only, never modified)
        │  sync: mechanical, seconds — read "which papers exist" into a catalog
        ▼
  catalog/   paper index + tags / collections / years + method×problem matrix
        │  ① Distill: read each full text once → objective essence
        ▼
  notes/     distillation cache (one page per paper, reused forever)
        │  ② Compile: read only notes → merge into judgments
        ▼
  syntheses/ your second brain (reviews / novelty / research gaps)
        ▲  ③ Weave back: a new paper → rewrite the page, flag conflicts
        │
  indexes/OVERVIEW.md  session entry: on open, the AI knows what's compiled
        │
        ▼
  outputs/   finished pieces you asked for (reviews / topics / answers)
```

Each layer in a line:

- **Zotero** — your real papers; the tool only reads.
- **catalog/** — machine-generated "which papers exist" index; deletable and rebuildable anytime.
- **notes/** — the distillation cache; the result of reading full text once, and the cheap source for everything after.
- **syntheses/** — the compiled product, your actual second brain.
- **indexes/OVERVIEW.md** — read first on every conversation, so the AI knows which directions are already compiled and reusable.
- **outputs/** — the finished pieces you asked it to write.

> One guiding rule: **mechanical work (sync, indexing, search) goes to scripts; semantic work (understanding, merging, judging) goes to the AI.**

### ✨ 5. What it can do for you

Because it's *compiled*, it doesn't just look things up — it helps you **form judgments and even decide what to do next**. Just say it in plain language; copy these to try:

- 🔎 **Find precisely**: `List the papers in my library on "conflict resolution", with authors and years.`
- 📝 **Write a literature review**: `Compile the "explainability" direction into a review.` (traced along two axes: how methods evolved × how the problem evolved)
- 💡 **Find novelty / gaps**: `What research gaps in this direction has no one tackled yet?`
- 🔀 **Cross-pollinate ideas**: `Is there an opportunity between robust RL and sector optimization?`
- 🎯 **Get topics handed to you**: `What could my next paper be about?`

> In one line: **RAG helps you *find the source text*; this helps you *get a judgment* — and even *decide the next step*.**

### 🚀 6. How to use it (from install to daily use)

#### 6.1 Three prerequisites

📚 Zotero installed with papers · 🐍 Python · 🤖 Claude Code (or Codex).
No coding required — the AI does most of it; you mostly talk.

#### 6.2 First time: download → open → connect Zotero

1. **Download** the project, unzip it, drop it in any folder (preferably off your system drive, e.g. `D:\zotero-kb`).
2. **Open Claude Code inside that folder** (or point Claude Code at it). On open it reads the manuals `AGENTS.md` / `CLAUDE.md` and is **automatically your "knowledge-base assistant."**
3. **Connect your Zotero** — just tell it:
   > I'm new here. Connect my Zotero, install dependencies, and run the first sync.

   It finds your Zotero path, fills the config, and syncs. You barely touch the keyboard.

#### 6.3 Daily: just talk

Once set up, ask / compile / write — all in plain language (see section 5). **No commands to memorize** — the AI already learned the rules and flow from `AGENTS.md`.

#### 6.4 ⚠️ Why doesn't it auto-compile everything on startup?

You might think: "if compiling is so good, why not compile all my hundreds of papers on open?" It's a deliberate choice, for two reasons:

1. 💸 **Distillation reads full text and costs tokens.** Auto-reading the whole library is slow and expensive, and you may not care about every paper.
2. 🗂️ **Research has many, messy classifications.** Your collections / tags are numerous; blindly compiling everything together can mix things that shouldn't mix.

So the rule is: **what to compile, and when, is up to you.** Point at a direction and it compiles that one; papers you read in daily use get distilled and cached along the way. Accurate, and never wasteful.

#### 6.5 Four usage modes (auto-detected — just talk)

- 🔍 **Query** (default): ask, find papers, compare. Read-only, safest.
- 📝 **Produce**: write reviews, topic lists, rebuttals → saved to `outputs/`.
- 🧠 **Compile**: distill papers, build reviews, update judgments (grow the brain).
- 🛠️ **Develop**: change scripts, templates, rules.

> You don't name the mode — it infers from what you say, and confirms before writing files.

### 🔒 7. What it never touches

- **Reads your Zotero only** — never modifies or deletes your papers or Zotero data.
- **Never copies PDFs or paper full text** into this repo — only indexes, path pointers, and the AI's judgments.
- **Fully local** — not RAG, no vector DB, no uploads; your data stays on your machine.

### 📚 8. Go deeper / developers

- [`AGENTS.md`](AGENTS.md) / [`CLAUDE.md`](CLAUDE.md): the full operating manual the agent reads at runtime — ask the AI to walk you through the design.

<details>
<summary>🛠️ Developer commands</summary>

On Windows PowerShell, set UTF-8 first: `$env:PYTHONIOENCODING='utf-8'`

```powershell
python scripts/zotero_query.py sync                 # read-only Zotero → refresh catalog/
python scripts/zotero_query.py search "<query>"     # full-text search, for locating
python scripts/zotero_query.py paper --key <key>    # one paper: metadata + annotations + path
python scripts/kb_index.py                          # build compile-status index + session entry
python scripts/check_structure.py                   # structure & frontmatter checks
```

First-time config: copy `config.example.yaml` to `config.yaml` and fill in your Zotero path (or let the AI do it).
</details>

### 🙏 9. Acknowledgements

The core ideas here are inspired by two sources: Andrej Karpathy's publicly shared **LLM wiki / knowledge-compilation** approach, and the **fuxi** knowledge-base design shared by **stormzhang**. This project is an **independent implementation for the research / Zotero setting**; the code and concrete implementation are the author's own and contain no non-public technical details from others.
