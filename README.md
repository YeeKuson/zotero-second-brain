# 🧠 Zotero 编译型知识库 · Zotero Compiled Knowledge Base

> 把你 Zotero 里的论文，编译成一个能跟你讨论的「第二大脑」。
> Compile the papers in your Zotero into a *second brain* you can actually talk to.

**🌐 [中文](#-中文) · [English](#-english)**

---

## 🧠 中文

### 这是什么

一个 **AI-Native 编译型科研知识库**。你的 Zotero 负责存论文，它负责把论文**编译成可复用的判断**——你用大白话问它，它用已经整理好的结论回答，像一个读过你所有论文的研究助理。🤝

> 一句话：Zotero 帮你「存论文」，它帮你「得结论」。

### 😩 它解决什么

你一定干过：看到好论文 → 存进 Zotero → 然后就没有然后了。📚 存了几百篇，真要写综述、找创新点时，还是得一篇篇翻、一篇篇想。**你存下来的是信息，不是知识。** 这个工具补的就是从「信息」到「知识」这一步。

### ⚡ 和 RAG 最大的不同：编译 > 检索

市面上「AI + 知识库」几乎都是 **RAG**：把文档切块、转成向量，你提问时临时捞几块喂给 AI。

> 🍳 **打个比方**：RAG 像一个每次点菜才跑去仓库现切原料的厨子——每次都从生料开始，重复劳动。
> 编译型知识库提前把原料**炼成半成品**：你提问时直接用炼好的结论，又快又能专注细节。

| | 🔍 RAG | 🧠 编译型（本项目） |
|---|---|---|
| 何时「理解」 | 每次提问临时检索、现算 | 提前**蒸馏 + 编译一次**，永久复用 |
| 给你什么 | 原文片段 | 结构化的**判断 / 结论** |
| 加新资料 | 丢进向量库，互不关联 | **往回织**进已有判断，还标出新旧矛盾 |
| 底层 | embedding / 向量库 | 人工分类 + 客观蒸馏笔记，**不用向量** |
| 没有 AI 时 | 一个向量库 | 一堆**人能直接读**的 Markdown 判断 |

核心就四个字：**编译 > 检索**。

### 🔄 它怎么工作

```
   Zotero（你的论文 · 只读，绝不改）
      │  ① 蒸馏：每篇全文只读一次，提炼成客观笔记
      ▼
   notes/（蒸馏缓存 · 永久复用，不再回头读全文）
      │  ② 编译：把同方向多篇笔记，归纳成一页判断
      ▼
   syntheses/（你的第二大脑：综述 / 创新点 / 研究空白）
      ▲  ③ 往回织：加了新论文 → 回头更新这页、标出矛盾
      │
   你用大白话问它，或让它写综述、找选题、做思维碰撞 💬
```

两个关键设计让「大量精读」变得划算：🪙
- **蒸馏一次，永久复用**：一篇论文的全文只在蒸馏时读一次，之后写综述、问答、碰撞都只读那份便宜的笔记。
- **按你的分类编译**：沿用你 Zotero 里的 collection / tag 组织成多个独立单元，也允许故意跨界碰撞出火花。✨

> 完整原理（两段式编译、客观蒸馏、往回织、多编译单元）写在 [`AGENTS.md`](AGENTS.md)——那是 AI 运行时读的操作手册，你想了解可以直接让 AI 讲给你听。

### ✨ 能帮你做什么

直接用大白话说，复制下面的句子就能试：

- 🔎 **查论文 / 比路线**：`我库里关于"冲突解脱"的论文有哪些？列出作者、年份。`
- 📝 **写论文综述**：`把"可解释性"这个方向编译成一篇综述。`
- 💡 **找创新点 / 空白**：`这个方向有哪些还没人做的研究空白？`
- 🔀 **思维碰撞**：`鲁棒强化学习和扇区优化之间，有没有可做的机会？`
- 🎯 **找选题**：`我下一篇小论文能写什么？`

### 🚀 上手（不懂编程也能跟着做）

前提：你已经装好 📚 Zotero（里面有论文）、🐍 Python、🤖 Claude Code（或 Codex）。

1. **下载项目**：把整个项目下载下来、解压，随便放到一个文件夹（建议 C 盘以外，例如 `D:\Zotero知识库`）。
2. **打开它**：在这个文件夹里打开 Claude Code（或把 Claude Code 定位到这个文件夹）。一打开，它会自动读到项目说明书（`AGENTS.md` / `CLAUDE.md`），**默认就进入「知识库助手」模式**，知道该怎么帮你。
3. **接下来全是对话**。第一件事——**连上你的 Zotero**，跟它说：
   > 我是新手，帮我连上我的 Zotero、装好依赖、做第一次同步。

   它会帮你找到 Zotero 路径、填好配置、同步目录。你基本只动嘴。
4. **开始用**：之后想查、想编、想写，都直接说人话。具体能做什么、怎么触发，AI 已经从 `AGENTS.md` 读懂了，**你不用记任何命令**。

#### ⚠️ 为什么它不一开机就自动蒸馏 / 编译？

两个现实原因：① **科研分类多**——你的 collection / tag 往往很多，自动全编容易把不该混的混在一起；② **蒸馏要读全文、很费 token**——全库自动蒸馏不划算。所以**编译什么、什么时候编，由你说了算**：你点哪个方向，它编哪个方向。

#### 🎚️ 四种使用模式（它自动判断，你只管说）

- 🔍 **查询模式**（默认）：问问题、找论文、比较路线。只读，最安全。
- 📝 **产出模式**：让它写综述、列选题、做 rebuttal，成稿落到 `outputs/`。
- 🧠 **编译模式**：让它蒸馏论文、编综述、更新判断（养大脑）。
- 🛠️ **开发模式**：改脚本、模板、规则。

> 你不用记模式名——它从你的话里自动判断；要动笔写文件前会先跟你确认。

### 🔒 它不碰什么（放心用）

- **只读你的 Zotero**，绝不修改、删除你的论文或 Zotero 数据。
- **绝不复制 PDF / 论文正文**到本库——只存索引、路径指针和 AI 的判断。
- **不是 RAG、不用向量库、不联网上传**——纯本地，数据都在你电脑上。

### 📚 想深入

- [`AGENTS.md`](AGENTS.md) / [`CLAUDE.md`](CLAUDE.md)：AI 运行时读的操作手册，编译纪律都在这。想懂设计，直接让 AI 念给你听。

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

### 🙏 灵感来源

本项目的核心理念受两处启发：Andrej Karpathy 公开提出的 **LLM wiki / 知识库编译**思路；以及 **stormzhang** 分享的 **fuxi** 知识库设计思路。本项目是把这些理念**用到科研 / Zotero 场景的独立实现**，代码与具体实现为作者自有，未包含他人未公开的技术细节。

---

## 🧠 English

### What is this

An **AI-native, *compiled* research knowledge base**. Zotero stores your papers; this tool **compiles them into reusable judgments** — you ask in plain language, it answers from pre-digested conclusions, like a research assistant who has read all your papers. 🤝

> In one line: Zotero helps you *store papers*; this helps you *get conclusions*.

### 😩 The problem it solves

You've done it: find a good paper → save it to Zotero → and that's it. 📚 After hundreds of saves, writing a review or finding a research gap still means re-reading everything. **You saved information, not knowledge.** This tool fills exactly that gap.

### ⚡ How it differs from RAG: compile > retrieve

Almost every "AI + knowledge base" today is **RAG**: chop docs into chunks, embed them, and pull a few back at query time.

> 🍳 **An analogy**: RAG is a chef who runs to the warehouse to slice raw ingredients *every time* you order — starting from scratch, repeatedly. A compiled knowledge base pre-cooks ingredients into **ready components**: when you order, it uses them directly — faster, and free to focus on detail.

| | 🔍 RAG | 🧠 Compiled (this) |
|---|---|---|
| When it "understands" | At query time, recomputed each ask | **Distilled + compiled once**, reused forever |
| What you get | Raw text snippets | Structured **judgments / conclusions** |
| Adding material | Into the vector store, disconnected | **Woven back** into existing judgments, flagging contradictions |
| Under the hood | embeddings / vector DB | Human classification + objective notes, **no vectors** |
| Without the AI | A vector store | Plain Markdown judgments **a human can read** |

The whole idea: **compile > retrieve**.

### 🔄 How it works

```
   Zotero (your papers · read-only, never modified)
      │  ① Distill: read each full text ONCE → an objective note
      ▼
   notes/ (distillation cache · reused forever, full text never re-read)
      │  ② Compile: merge many notes on one topic into one judgment
      ▼
   syntheses/ (your second brain: reviews / novelty / research gaps)
      ▲  ③ Weave back: a new paper → revisit & update the page, flag conflicts
      │
   Ask it in plain language, or have it write reviews, find topics, spark ideas 💬
```

Two design choices make "reading a lot, carefully" affordable: 🪙
- **Distill once, reuse forever**: a paper's full text is read only at distillation; reviews, Q&A and brainstorming all read the cheap note afterward.
- **Compile along your own classification**: organized into independent units by your Zotero collections / tags — and you can deliberately cross them to spark new ideas. ✨

> The full mechanism (two-stage compilation, objective distillation, weave-back, multiple units) lives in [`AGENTS.md`](AGENTS.md), the manual the AI reads at runtime — just ask the AI to walk you through it.

### ✨ What it can do for you

Just say it in plain language — copy these to try:

- 🔎 **Find papers / compare approaches**: `List the papers in my library on "conflict resolution", with authors and years.`
- 📝 **Write a literature review**: `Compile the "explainability" direction into a review.`
- 💡 **Find novelty / gaps**: `What research gaps in this direction has no one tackled yet?`
- 🔀 **Cross-pollinate ideas**: `Is there an opportunity between robust RL and sector optimization?`
- 🎯 **Find topics to write**: `What could my next paper be about?`

### 🚀 Getting started (no coding needed)

Prerequisites: 📚 Zotero installed with papers · 🐍 Python · 🤖 Claude Code (or Codex).

1. **Download** the project, unzip it, drop it in any folder (preferably off your system drive, e.g. `D:\zotero-kb`).
2. **Open it**: launch Claude Code inside that folder (or point Claude Code at it). On open, it reads the project manuals (`AGENTS.md` / `CLAUDE.md`) and is **automatically in "knowledge-base assistant" mode**.
3. **From here it's all conversation.** First, **connect your Zotero** — tell it:
   > I'm new here. Connect my Zotero, install dependencies, and run the first sync.

   It finds your Zotero path, fills the config, and syncs. You barely touch the keyboard.
4. **Use it**: ask, compile, write — all in plain language. The AI already learned the details from `AGENTS.md`, so **you don't memorize any commands**.

#### ⚠️ Why doesn't it auto-distill / compile on startup?

Two reasons: ① **research has many classifications** — your collections / tags are numerous, and blindly compiling everything risks mixing things that shouldn't mix; ② **distillation reads full text and costs many tokens** — auto-compiling the whole library isn't worth it. So **what to compile, and when, is up to you**: point at a direction, and it compiles that one.

#### 🎚️ Four usage modes (auto-detected — just talk)

- 🔍 **Query** (default): ask, find papers, compare. Read-only, safest.
- 📝 **Produce**: have it write reviews, topic lists, rebuttals → saved to `outputs/`.
- 🧠 **Compile**: have it distill papers, build reviews, update judgments (grow the brain).
- 🛠️ **Develop**: change scripts, templates, rules.

> You don't name the mode — it infers from what you say, and confirms before writing files.

### 🔒 What it never touches

- **Reads your Zotero only** — never modifies or deletes your papers or Zotero data.
- **Never copies PDFs or paper full text** into this repo — only indexes, path pointers, and the AI's judgments.
- **Not RAG, no vector DB, no uploads** — fully local, your data stays on your machine.

### 📚 Go deeper

- [`AGENTS.md`](AGENTS.md) / [`CLAUDE.md`](CLAUDE.md): the operating manual the agent reads at runtime — ask the AI to explain the design to you.

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

### 🙏 Acknowledgements

The core ideas here are inspired by two sources: Andrej Karpathy's publicly shared **LLM wiki / knowledge-compilation** approach, and the **fuxi** knowledge-base design shared by **stormzhang**. This project is an **independent implementation for the research / Zotero setting**; the code and concrete implementation are the author's own and contain no non-public technical details from others.
