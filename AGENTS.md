# Project AGENTS.md

## Project Summary
这是一个 Zotero 编译型知识库。项目只从 `你的 Zotero 数据目录` 只读读取 Zotero 元数据、标注和全文缓存，生成可重建的索引；真正有价值的内容是 agent 写出的单篇判断、主题综述和输出文稿。

本项目不是 RAG、不是 PDF 备份、不是全文仓库。最高规则是：只建索引，绝不复制论文正文、PDF 或 Zotero 全文缓存到本库。

## Structure
- `AGENTS.md` / `CLAUDE.md`: Codex 与 Claude 共用的项目操作手册，两个文件应同步维护。
- `config.yaml`: Zotero 路径、入库类型、citation key 和矩阵轴配置。
- `scripts/zotero_query.py`: 只读 Zotero，负责 `sync`、`search`、`paper`。
- `scripts/kb_index.py`: 扫描 `notes/`、`syntheses/`、`entities/`，生成编译状态索引。
- `scripts/check_structure.py`: 检查目录、模板、frontmatter 和项目内 Markdown 引用。
- `catalog/`: 机器生成的 Zotero 派生索引，可重建。
- `notes/`: 单篇论文编译判断，人工/agent 产物，不得覆盖。
- `syntheses/categories/`: 按 Zotero collection 编译的综述。
- `syntheses/topics/`: 按研究问题或方法编译的横向综述。
- `entities/methods/`, `entities/datasets/`, `entities/authors/`: 方法、数据集、作者等轻量实体页。
- `indexes/`: 机器生成的编译状态索引，可重建；其中 `indexes/OVERVIEW.md` 是会话入口。
- `outputs/`: 综述、选题、答疑等最终文稿，不得覆盖。

## Session Entry
每次对话开始先读 `indexes/OVERVIEW.md`，了解已编译方向（汇总型/碰撞型）与新鲜度。
能引用现成编译产物就别从零重建，只补增量。该文件由 `python scripts/kb_index.py` 生成。

## Onboarding（新手 / 新装库自助引导）
当用户像新手或这是新装库时（用户说“我是新手 / 第一次用 / 帮我配置 / 帮我连 Zotero”，
或检测到 `config.yaml` 不存在、仍是范例占位路径、`catalog/` 为空、从未 sync 过），主动走引导。
全程用大白话、不甩英文报错、需要用户操作处说清“在哪点、点什么”，每步先说要做什么：
1. 环境：确认 Python 可用；检查并安装依赖 `pip install -r requirements.txt`（PyYAML）。
2. 配置：无 `config.yaml` 时从 `config.example.yaml` 复制一份；帮用户定位 Zotero 数据目录
   （Windows 默认 `C:\Users\<用户名>\Zotero`，内含 `zotero.sqlite` 与 `storage`；
   或让用户在 Zotero「编辑→设置→高级→数据目录位置」查看），把真实路径写进 `config.yaml`。
3. 同步：跑 `zotero_query.py sync`，报告同步了多少篇。
4. 自检：跑 `check_structure.py` 与 `kb_index.py`，确认通过。
5. 收尾：给 2–3 句可直接复制的查询示例，告诉用户接下来怎么问。
铁律不变：只读 Zotero，绝不写/改/删 `你的 Zotero 数据目录`（或用户自己的 Zotero 目录）；
改 `config.yaml` 等写操作前用一句话说明再动手。

## Modes
默认是查询模式，只读，不写文件。

- 查询模式：从编译/蒸馏层（synthesis / notes / catalog 元数据）回答问题、找论文、比较路线。只读不写；需读全文蒸馏时转编译模式。
- 产出模式：用户明确要求写综述、选题、rebuttal 等时，只能写 `outputs/`。
- 编译模式：当用户意图是固化/沉淀知识时进入（靠意图推断，不要求精确关键词），可写 `catalog/`、`notes/`、`syntheses/`、`entities/`、`indexes/`。因编译是写操作，落盘前用自然语言确认意图。
- 开发模式：用户明确要求改脚本、模板、配置或规则时，可写 `scripts/`、`templates/`、`config.yaml`、`AGENTS.md`、`CLAUDE.md`。

越界写入必须先询问用户。

## Compilation Doctrine（编译纪律）
1. 双轴并列：collection 与 tag 是地位并列的两条编译轴，没有主辅之分。`syntheses/categories/` 按 collection 汇总，`syntheses/topics/` 按 tag/方法汇总。
2. 两种编译形态，都合法：
   - 汇总型（convergent）：沿单一轴值（一个 collection 或一个 tag）收敛梳理，忠实呈现“这个方向里有什么”，是稳定骨架。
   - 碰撞型（divergent）：故意跨多个 collection/tag 混合，找空白与新方向；`catalog/MATRIX.md` 的空格 = 候选碰撞点。混合是被鼓励的特性，不是 bug。
3. 留痕保证严谨：每份 synthesis 的 frontmatter 必须写明 `kind`/`axis`/`scope`/`covered_citation_keys`。不准“不留痕地混”。严谨靠可追溯，不靠把每种分类都穷尽编一遍。
4. 意图推断（AI-Native）：不要求用户用精确指令或关键词触发。从自然语言推断“查询 / 产出 / 编译”，以及“汇总型 / 碰撞型 / 扫库”。落盘前用大白话确认意图，但不强制暗号。
5. 提拔制做默认：查询中顺手提议把有价值的方向固化成 synthesis；用户也可明确要求扫库整片编译。这是优先级/习惯问题，不写死。
6. 单篇客观全面：paper note 是读一次全文后的客观全面蒸馏（核心问题 / 方法与创新 / 全部关键结果与数据 / 假设 / 局限），力求全面、不带编译目的（见 Two-Stage 蒸馏客观性）；有 Zotero 标注则并入，但不依赖标注。“与同类关系 / 对我的可引用点”等目的性判断只在 scoped synthesis 中按各自 scope 推导，不写回单篇 note。同一篇可在多份 synthesis 下有不同取用。
7. 懒生成不穷尽：绝不预生成 collection × tag 的全笛卡尔积；骨架按使用增长，碰撞按需登记到 `indexes/OVERVIEW.md`。
8. 选题双来源：规划“接下来写什么”不只靠跨领域碰撞。① 同领域汇总（convergent）的创新点与待改进空白本身就是选题来源；② 跨领域碰撞（divergent）撞出的新组合是另一来源。两者并用。
9. 往回织，不往后堆（编译型的灵魂）：新论文进入某 synthesis 的 scope 时，必须回头重织那篇——补创新点、更新双轴脉络、标新旧矛盾，而不是另起一篇堆叠。`indexes/STALE.md` 的「待织入」清单（kb_index 按 scope 比对 catalog 自动算）是触发器；编译模式应优先清待织入，再开新方向。这是“编译”区别于“收藏”的本质。
10. 两段式编译（控成本）：全文只在入库蒸馏时读一次写成 note；synthesis 只读 notes、不读全文（详见 Two-Stage Compilation 节）。

## Two-Stage Compilation（两段式编译 · 把全文成本只付一次）
“大量精读编译”能否划算，全看全文读几次。本库强制两段，全文只读一次：
1. 入库蒸馏（贵，每篇一辈子只做一次）：读论文全文 `.zotero-ft-cache` 一次，客观全面地写成
   paper note（核心问题 / 方法与创新 / 全部关键结果与数据 / 假设 / 局限）。这是蒸馏缓存。
2. 主题编译（便宜，可反复）：synthesis 只读已蒸馏的 notes，**禁止从全文直接合成综述**；
   往回织、问答、选题也只读 notes，永不回头读全文。
- 读一次，绝不浪费（铁律）：任何时候读了某篇全文（蒸馏 / 印证 / 查细节），都必须把它客观蒸馏或
  更新成 note 再作答，全文绝不读后即弃。具体数据 / 细节优先从 note 取——客观蒸馏已宁全勿略地收了关键数据。
- 蒸馏客观性（铁律）：蒸馏必须客观中立、力求全面，像没有任何编译任务一样读，把论文所有重要要点
  都提出来，不带编译/选题目的、不提前筛选、不压缩省略。“对我有什么用 / 可引用点 / 与他篇的关系”
  等目的性取舍只在第二段编译时做。带目的蒸馏会提前丢掉与当下目的无关的细节，正是要避免的——这与
  “蒸馏共享、编译独立”一致：共享的是论文客观全貌，独立的是各单元的目的性提取。
- 存量分批：库内论文是存量批量，首次只蒸馏用户选的方向，分批落盘、可续；进度看
  `indexes/STALE.md`（待蒸馏=该 scope 内还没 note 的论文；待织入=已有 note 但未并入综述）与 OVERVIEW。
- 往回织接笔记层：新论文先蒸馏成一篇 note（读一次全文），再读 notes 更新主题页。
- 成本观：单篇全文阅读成本一次性付清，摊到它日后无数次便宜复用（综述/往回织/问答）上——这才划算；
  反面是从全文直接反复合成综述，等于一篇全文反复付费。

## Reading Loop（一切落到编译/蒸馏；搜索只在定位之后做细节）
编译是本库唯一核心。查询 / 讨论 / 问答一律先从编译（synthesis）+ 蒸馏（notes）内容出，不默认开全文搜索。
1. 定位：找某篇 / 某方向，先用 catalog 元数据（题目 / 作者 / 标签 / 年份）和 OVERVIEW，不读全文。
2. 作答：从 syntheses + notes 回答。客观蒸馏已“宁全勿略”收了关键数据，多数“某篇讲了啥、数据多少”直接读它的 note 即可。
3. 缺口 = 补编译，不是搜一次：某方向没编 / 某篇没蒸馏，默认动作是把它编 / 蒸馏出来（留下资产），而不是做一次性全文搜索后即弃。
4. 全文只在蒸馏时读，且读了必落 note（读一次不浪费）。
5. 精确全文搜索 / 读正文降为“定位之后”的细节步：用户已锁定某一篇、要核对其中一个具体数据或作者 / 题目时才做；此时阅读量小、专注细节，并把读到的并入该篇 note。
6. 存在性查询（“有没有人做过 X”）是少数真精确任务，可实跑 `search` 全文核实（见 Rules），命中论文若未蒸馏则顺手蒸馏。

## Output Forms（输出形式 → 数据流）
AI-Native 知识库与传统库的差别在输出形式。每种输出对应一条固定数据流：
1. 定位与精确细节：找论文用 catalog 元数据（题目 / 作者 / 标签，不读全文）；要某篇的具体内容或数据，读它的 note（客观蒸馏已含关键数据）；note 不存在就先蒸馏（读一次全文、客观全面，数据自然进 note）。全文只在蒸馏时读、读了即落 note，不做读后即弃的搜索。
2. 同领域汇总（找创新点/缺点）：convergent synthesis；创新点 + 待改进空白即选题来源。
3. 同领域综述（双轴发展脉络）：求解方法演进 × 解决问题演进，用 `catalog/MATRIX.md` 与 `BY-YEAR.md` 喂。
4. 选题流（找下一步 · 主动派活）：知识库要反过来给用户派活，不只被动答问。基于 synthesis 的待改进空白 + `MATRIX` 空格 + 往回织标出的新旧矛盾，主动产出“接下来能做哪些研究 / 能写哪篇小论文”。这是“用得出”而非只“答得出”。
5. 印证观点：论断 → 从已蒸馏 notes / 已编译 syntheses 找支撑 → 命中论文若未蒸馏先蒸馏再核实 → 带作者/标题/年份/citationKey 给支撑或反驳；核实不了标 `needs-review`。不为印证做读后即弃的全文搜索。
规划选题来自第 2、4 两条共同（见 Doctrine 第 8 条）。

## Rules
- 永远只读 Zotero：不得写入、删除、移动、修改 `你的 Zotero 数据目录` 下的任何文件。
- `AGENTS.md` 与 `CLAUDE.md` 是同一套约束的双入口；修改其中一个时，必须同步检查另一个。
- 不复制 PDF、论文全文、`.zotero-ft-cache` 内容到本库；目录里只能保存路径指针和元数据。
- `catalog/` 与 `indexes/` 是机器索引，可以重建；`notes/`、`syntheses/`、`entities/`、`outputs/` 是编译产物，不得由脚本覆盖或删除。
- 正文用中文，术语保留英文；frontmatter 字段名、目录名和脚本变量名用英文。
- 存在性查询必须实跑 `python scripts/zotero_query.py search "<query>"`，并报告检索词、覆盖范围和命中论文。
- 命中论文必须带作者、标题、年份和 `citationKey`。
- 精确查询与“印证观点”优先用已蒸馏 note / 已编译 synthesis；确需读 `.zotero-ft-cache` 正文核实时，读完即客观蒸馏成 note，不读后即弃。search 命中只是定位，不能只凭标题/摘要/标签下结论。
- 不能把“库内没有”说成“领域没人做”。后者需要外部文献检索验证。
- 证据不足时标记 `status: needs-review`，不要虚构结论、引用或贡献点。

## Commands
- Check: `python scripts/check_structure.py`
- Build indexes: `python scripts/kb_index.py`（同时刷新会话入口 `indexes/OVERVIEW.md`）
- Sync catalog: `python scripts/zotero_query.py sync`
- Search: `python scripts/zotero_query.py search "冲突解脱"`
- Read one paper: `python scripts/zotero_query.py paper --key <citationKey>`

在 Windows 控制台建议使用：

```powershell
$env:PYTHONIOENCODING='utf-8'
python scripts/check_structure.py
```

## Critical Mistakes Already Made
- 错误：旧版 `scripts/check_structure.py` 要求旧项目文件，如 `HERMES.md`、`PRODUCT-DESIGN.md`。
  原因：该项目由通用知识库骨架迁移而来，目录模型已变化。
  避免：只按本文件和 `CLAUDE.md` 的目标结构检查。
- 错误：旧版 `scripts/kb_index.py` 扫描 `wiki/`、`briefs/`、`product_briefs/`。
  原因：旧骨架面向产品/网页资料，不适合论文编译库。
  避免：只扫描 `notes/`、`syntheses/`、`entities/`。
- 错误：把 Zotero 全文缓存当作本库内容保存。
  原因：混淆了“可重建索引”和“论文正文副本”。
  避免：只保存 `fulltext_cache` 路径，不保存全文内容。
