from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from dataclasses import dataclass, field
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config.yaml"

DEFAULT_CONFIG = {
    "sqlite_path": r"PATH_TO_YOUR_ZOTERO\zotero.sqlite",
    "storage_dir": r"PATH_TO_YOUR_ZOTERO\storage",
    "include_item_types": [
        "journalArticle",
        "conferencePaper",
        "preprint",
        "thesis",
        "bookSection",
    ],
    "include_webpage": False,
    "include_abstract_in_catalog": True,
    "catalog_dir": "catalog",
    "problem_tags": ["冲突解脱", "扇区优化", "航迹规划", "冲突探测"],
    "method_tags": ["深度强化学习", "强化学习", "鲁棒强化学习", "数学规划方法", "决策树", "可解释性"],
    "default_limit": 20,
    "max_context_chars": 180,
}


FIELD_ALIASES = {
    "title": ["title"],
    "abstract": ["abstractNote", "abstract"],
    "date": ["date"],
    "year": ["year"],
    "venue": ["publicationTitle", "conferenceName", "proceedingsTitle", "university", "bookTitle"],
    "doi": ["DOI", "doi"],
    "citation_key": ["citationKey"],
}


@dataclass(frozen=True)
class Attachment:
    item_id: int
    key: str
    path: str
    fulltext_cache: str


@dataclass
class Paper:
    item_id: int
    zotero_key: str
    item_type: str
    date_modified: str
    fields: dict[str, str] = field(default_factory=dict)
    authors: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    collections: list[str] = field(default_factory=list)
    attachments: list[Attachment] = field(default_factory=list)
    annotation_count: int = 0

    @property
    def title(self) -> str:
        return first_field(self.fields, "title") or "(untitled)"

    @property
    def abstract(self) -> str:
        return first_field(self.fields, "abstract")

    @property
    def year(self) -> str:
        explicit_year = first_field(self.fields, "year")
        if explicit_year:
            return explicit_year
        date_value = first_field(self.fields, "date")
        match = re.search(r"(19|20)\d{2}", date_value)
        return match.group(0) if match else ""

    @property
    def venue(self) -> str:
        return first_field(self.fields, "venue")

    @property
    def doi(self) -> str:
        return first_field(self.fields, "doi")

    @property
    def citation_key(self) -> str:
        configured_key = first_field(self.fields, "citation_key")
        if configured_key:
            return slugify(configured_key)
        author = self.authors[0].split()[-1] if self.authors else "unknown"
        title_word = next((part for part in re.split(r"\W+", self.title) if part), "paper")
        return slugify(f"{author}_{self.year or 'nd'}_{title_word}")

    @property
    def fulltext_paths(self) -> list[str]:
        return [attachment.fulltext_cache for attachment in self.attachments if attachment.fulltext_cache]


def configure_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def load_config() -> dict[str, object]:
    config = dict(DEFAULT_CONFIG)
    if not CONFIG_PATH.exists():
        return config

    try:
        import yaml  # type: ignore
    except ModuleNotFoundError:
        print(
            "[警告] 检测到 config.yaml，但没有安装 PyYAML，你对 config.yaml 的修改不会生效，"
            "脚本会改用内置默认路径。请先运行：pip install -r requirements.txt",
            file=sys.stderr,
        )
        return config

    data = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}
    zotero = data.get("zotero", {})
    catalog = data.get("catalog", {})
    matrix = data.get("matrix", {})
    search = data.get("search", {})

    config.update(
        {
            "sqlite_path": zotero.get("sqlite_path", config["sqlite_path"]),
            "storage_dir": zotero.get("storage_dir", config["storage_dir"]),
            "include_item_types": catalog.get("include_item_types", config["include_item_types"]),
            "include_webpage": catalog.get("include_webpage", config["include_webpage"]),
            "include_abstract_in_catalog": catalog.get(
                "include_abstract_in_catalog",
                config["include_abstract_in_catalog"],
            ),
            "catalog_dir": catalog.get("output_dir", config["catalog_dir"]),
            "problem_tags": matrix.get("problem_tags", config["problem_tags"]),
            "method_tags": matrix.get("method_tags", config["method_tags"]),
            "default_limit": search.get("default_limit", config["default_limit"]),
            "max_context_chars": search.get("max_context_chars", config["max_context_chars"]),
        }
    )
    return config


def connect_readonly(sqlite_path: str) -> sqlite3.Connection:
    path = Path(sqlite_path)
    if not path.is_file():
        raise FileNotFoundError(
            f"找不到 Zotero 数据库: {sqlite_path}\n"
            "这通常是因为 config.yaml 里的 Zotero 路径不对（可能还是范例里的占位路径）。\n"
            "解决：打开 Zotero → 编辑 → 设置 → 高级 → 数据目录位置，把真实路径填进 config.yaml；\n"
            "或在 Claude Code 里直接说“帮我连上我的 Zotero”，让 agent 替你修。"
        )
    uri = f"file:{path.as_posix()}?mode=ro&immutable=1"
    connection = sqlite3.connect(uri, uri=True)
    connection.row_factory = sqlite3.Row
    return connection


def fetch_all_papers(connection: sqlite3.Connection, config: dict[str, object]) -> list[Paper]:
    include_types = list(config["include_item_types"])
    if config.get("include_webpage"):
        include_types.append("webpage")

    placeholders = ",".join("?" for _ in include_types)
    rows = connection.execute(
        f"""
        SELECT i.itemID, i.key, i.dateModified, it.typeName
        FROM items i
        JOIN itemTypes it ON it.itemTypeID = i.itemTypeID
        LEFT JOIN deletedItems d ON d.itemID = i.itemID
        WHERE d.itemID IS NULL AND it.typeName IN ({placeholders})
        ORDER BY i.dateModified DESC, i.itemID DESC
        """,
        include_types,
    ).fetchall()

    papers = [
        Paper(
            item_id=row["itemID"],
            zotero_key=row["key"],
            item_type=row["typeName"],
            date_modified=row["dateModified"] or "",
        )
        for row in rows
    ]
    paper_by_id = {paper.item_id: paper for paper in papers}
    if not papers:
        return []

    load_fields(connection, paper_by_id)
    load_authors(connection, paper_by_id)
    load_tags(connection, paper_by_id)
    load_collections(connection, paper_by_id)
    load_attachments(connection, paper_by_id, str(config["storage_dir"]))
    load_annotation_counts(connection, paper_by_id)
    return papers


def load_fields(connection: sqlite3.Connection, paper_by_id: dict[int, Paper]) -> None:
    item_ids = list(paper_by_id)
    placeholders = ",".join("?" for _ in item_ids)
    rows = connection.execute(
        f"""
        SELECT id.itemID, f.fieldName, idv.value
        FROM itemData id
        JOIN fields f ON f.fieldID = id.fieldID
        JOIN itemDataValues idv ON idv.valueID = id.valueID
        WHERE id.itemID IN ({placeholders})
        """,
        item_ids,
    ).fetchall()
    for row in rows:
        paper_by_id[row["itemID"]].fields[row["fieldName"]] = row["value"] or ""


def load_authors(connection: sqlite3.Connection, paper_by_id: dict[int, Paper]) -> None:
    item_ids = list(paper_by_id)
    placeholders = ",".join("?" for _ in item_ids)
    rows = connection.execute(
        f"""
        SELECT ic.itemID, c.firstName, c.lastName
        FROM itemCreators ic
        JOIN creators c ON c.creatorID = ic.creatorID
        WHERE ic.itemID IN ({placeholders})
        ORDER BY ic.itemID, ic.orderIndex
        """,
        item_ids,
    ).fetchall()
    for row in rows:
        name = " ".join(part for part in [row["firstName"], row["lastName"]] if part)
        if name:
            paper_by_id[row["itemID"]].authors.append(name)


def load_tags(connection: sqlite3.Connection, paper_by_id: dict[int, Paper]) -> None:
    item_ids = list(paper_by_id)
    placeholders = ",".join("?" for _ in item_ids)
    rows = connection.execute(
        f"""
        SELECT it.itemID, t.name
        FROM itemTags it
        JOIN tags t ON t.tagID = it.tagID
        WHERE it.itemID IN ({placeholders})
        ORDER BY t.name
        """,
        item_ids,
    ).fetchall()
    for row in rows:
        paper_by_id[row["itemID"]].tags.append(row["name"])


def load_collections(connection: sqlite3.Connection, paper_by_id: dict[int, Paper]) -> None:
    item_ids = list(paper_by_id)
    placeholders = ",".join("?" for _ in item_ids)
    rows = connection.execute(
        f"""
        SELECT ci.itemID, c.collectionName
        FROM collectionItems ci
        JOIN collections c ON c.collectionID = ci.collectionID
        WHERE ci.itemID IN ({placeholders})
        ORDER BY c.collectionName
        """,
        item_ids,
    ).fetchall()
    for row in rows:
        paper_by_id[row["itemID"]].collections.append(row["collectionName"])


def load_attachments(
    connection: sqlite3.Connection,
    paper_by_id: dict[int, Paper],
    storage_dir: str,
) -> None:
    parent_ids = list(paper_by_id)
    placeholders = ",".join("?" for _ in parent_ids)
    rows = connection.execute(
        f"""
        SELECT ia.parentItemID, ia.itemID, i.key, ia.path
        FROM itemAttachments ia
        JOIN items i ON i.itemID = ia.itemID
        WHERE ia.parentItemID IN ({placeholders})
        """,
        parent_ids,
    ).fetchall()
    storage_root = Path(storage_dir)
    for row in rows:
        attachment_path = normalize_attachment_path(storage_root, row["key"], row["path"] or "")
        fulltext_cache = storage_root / row["key"] / ".zotero-ft-cache"
        paper_by_id[row["parentItemID"]].attachments.append(
            Attachment(
                item_id=row["itemID"],
                key=row["key"],
                path=str(attachment_path) if attachment_path else "",
                fulltext_cache=str(fulltext_cache) if fulltext_cache.is_file() else "",
            )
        )


def load_annotation_counts(connection: sqlite3.Connection, paper_by_id: dict[int, Paper]) -> None:
    parent_ids = list(paper_by_id)
    placeholders = ",".join("?" for _ in parent_ids)
    rows = connection.execute(
        f"""
        SELECT ia.parentItemID AS itemID, COUNT(ann.itemID) AS annotationCount
        FROM itemAttachments ia
        JOIN itemAnnotations ann ON ann.parentItemID = ia.itemID
        WHERE ia.parentItemID IN ({placeholders})
        GROUP BY ia.parentItemID
        """,
        parent_ids,
    ).fetchall()
    for row in rows:
        paper_by_id[row["itemID"]].annotation_count = row["annotationCount"]


def fetch_annotations(connection: sqlite3.Connection, paper: Paper) -> list[sqlite3.Row]:
    attachment_ids = [attachment.item_id for attachment in paper.attachments]
    if not attachment_ids:
        return []
    placeholders = ",".join("?" for _ in attachment_ids)
    return connection.execute(
        f"""
        SELECT text, comment, color, pageLabel, sortIndex
        FROM itemAnnotations
        WHERE parentItemID IN ({placeholders})
        ORDER BY parentItemID, sortIndex
        """,
        attachment_ids,
    ).fetchall()


def first_field(fields: dict[str, str], alias_group: str) -> str:
    for field_name in FIELD_ALIASES[alias_group]:
        value = fields.get(field_name, "")
        if value:
            return value
    return ""


def normalize_attachment_path(storage_root: Path, attachment_key: str, raw_path: str) -> Path | None:
    if not raw_path:
        return None
    if raw_path.startswith("storage:"):
        return storage_root / attachment_key / raw_path[len("storage:") :]
    path = Path(raw_path)
    return path if path.is_absolute() else storage_root / attachment_key / raw_path


def slugify(value: str) -> str:
    cleaned = re.sub(r"[^\w\u4e00-\u9fff-]+", "_", value, flags=re.UNICODE)
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned or "unknown"


def markdown_escape(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def short_authors(authors: list[str]) -> str:
    if not authors:
        return ""
    if len(authors) == 1:
        return authors[0]
    return f"{authors[0]} et al."


def write_catalog(papers: list[Paper], config: dict[str, object]) -> None:
    catalog_dir = ROOT / str(config["catalog_dir"])
    catalog_dir.mkdir(exist_ok=True)
    include_abstract = bool(config["include_abstract_in_catalog"])

    headers = [
        "citationKey",
        "title",
        "authors",
        "year",
        "venue",
        "tags",
        "collections",
        "annotations",
        "fulltext_cache",
        "zotero_key",
    ]
    if include_abstract:
        headers.insert(5, "abstract")

    lines = [
        "# Zotero Catalog",
        "",
        "本文件由 `python scripts/zotero_query.py sync` 生成。它只保存 Zotero 派生元数据和路径指针，不保存论文正文。",
        "",
        "|" + "|".join(headers) + "|",
        "|" + "|".join("---" for _ in headers) + "|",
    ]
    for paper in sorted(papers, key=lambda item: (item.year, item.title), reverse=True):
        cells = [
            paper.citation_key,
            paper.title,
            short_authors(paper.authors),
            paper.year,
            paper.venue,
            "; ".join(paper.tags),
            "; ".join(paper.collections),
            str(paper.annotation_count),
            "; ".join(paper.fulltext_paths),
            paper.zotero_key,
        ]
        if include_abstract:
            cells.insert(5, paper.abstract)
        lines.append("|" + "|".join(markdown_escape(cell) for cell in cells) + "|")

    (catalog_dir / "CATALOG.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_grouped_index(catalog_dir / "BY-TAG.md", "Tag", papers, lambda paper: paper.tags)
    write_grouped_index(catalog_dir / "BY-CATEGORY.md", "Category", papers, lambda paper: paper.collections)
    write_grouped_index(catalog_dir / "BY-YEAR.md", "Year", papers, lambda paper: [paper.year or "unknown"])
    write_matrix(catalog_dir / "MATRIX.md", papers, config)


def write_grouped_index(
    output_path: Path,
    group_name: str,
    papers: list[Paper],
    group_getter: object,
) -> None:
    groups: dict[str, list[Paper]] = {}
    for paper in papers:
        for group in group_getter(paper):  # type: ignore[operator]
            groups.setdefault(group or "unknown", []).append(paper)

    lines = [
        f"# By {group_name}",
        "",
        "本文件由 `python scripts/zotero_query.py sync` 生成。",
        "",
    ]
    for group in sorted(groups):
        lines.append(f"## {group}")
        lines.append("")
        for paper in sorted(groups[group], key=lambda item: item.year, reverse=True):
            lines.append(f"- `{paper.citation_key}` {paper.authors[0] if paper.authors else ''} ({paper.year}) {paper.title}")
        lines.append("")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def write_matrix(output_path: Path, papers: list[Paper], config: dict[str, object]) -> None:
    problem_tags = list(config["problem_tags"])
    method_tags = list(config["method_tags"])
    lines = [
        "# Method × Problem Matrix",
        "",
        "本文件由 `python scripts/zotero_query.py sync` 生成。空格只表示当前库内标签未命中，不等于领域空白。",
        "",
        "| Problem / Method | " + " | ".join(markdown_escape(tag) for tag in method_tags) + " |",
        "|---|" + "|".join("---" for _ in method_tags) + "|",
    ]

    for problem in problem_tags:
        cells = [problem]
        for method in method_tags:
            matches = [
                f"`{paper.citation_key}`"
                for paper in papers
                if problem in paper.tags and method in paper.tags
            ]
            cells.append(", ".join(matches))
        lines.append("|" + "|".join(cells) + "|")
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def read_fulltext(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


# 字段加权：命中元数据比命中正文更相关，据此对结果排序。
FIELD_WEIGHTS = {
    "title": 5,
    "tags": 4,
    "collections": 3,
    "abstract": 2,
    "fulltext": 1,
}
METADATA_FIELDS = ("title", "tags", "collections", "abstract")


@dataclass
class SearchHit:
    paper: Paper
    score: int
    matched_terms: list[str]
    matched_fields: list[str]
    snippet: str


def tokenize_query(query: str) -> list[str]:
    # 按空白分词，支持多词检索；中文短语本身无空格，仍作单个词处理。
    return [term for term in query.split() if term]


def make_snippet(text: str, term: str, max_chars: int) -> str:
    lower_text = text.lower()
    index = lower_text.find(term.lower())
    if index == -1:
        return ""
    start = max(0, index - max_chars // 2)
    end = min(len(text), index + len(term) + max_chars // 2)
    return re.sub(r"\s+", " ", text[start:end]).strip()


def search_papers(
    papers: list[Paper],
    query: str,
    max_context_chars: int,
    match_all: bool = True,
) -> list[SearchHit]:
    """子串全文检索（非语义）。多词默认 AND，match_all=False 时为 OR。

    每个词记录命中的最高权重字段，分数=各命中词字段权重之和，按分数降序排，
    使 limit 截断保留最相关结果，而非按时间截断。
    """
    terms = tokenize_query(query)
    if not terms:
        return []

    hits: list[SearchHit] = []
    for paper in papers:
        field_texts = {
            "title": paper.title,
            "tags": " ".join(paper.tags),
            "collections": " ".join(paper.collections),
            "abstract": paper.abstract,
        }
        lowered = {name: text.lower() for name, text in field_texts.items()}
        fulltext_cache: dict[str, str] = {}

        def get_fulltext() -> dict[str, str]:
            if "raw" not in fulltext_cache:
                raw = "\n".join(read_fulltext(path) for path in paper.fulltext_paths)
                fulltext_cache["raw"] = raw
                fulltext_cache["lower"] = raw.lower()
            return fulltext_cache

        matched: dict[str, str] = {}  # term -> 命中的最高权重字段
        for term in terms:
            lower_term = term.lower()
            best_field = ""
            for field in METADATA_FIELDS:
                if lower_term in lowered[field]:
                    best_field = field
                    break
            if not best_field and lower_term in get_fulltext()["lower"]:
                best_field = "fulltext"
            if best_field:
                matched[term] = best_field

        if not matched:
            continue
        if match_all and len(matched) < len(terms):
            continue

        score = sum(FIELD_WEIGHTS[field] for field in matched.values())
        best_term = max(matched, key=lambda term: FIELD_WEIGHTS[matched[term]])
        best_field = matched[best_term]
        source = get_fulltext()["raw"] if best_field == "fulltext" else field_texts[best_field]
        snippet = make_snippet(source, best_term, max_context_chars) or f"命中 {best_field}。"
        ordered_fields = sorted(
            set(matched.values()), key=lambda field: FIELD_WEIGHTS[field], reverse=True
        )

        hits.append(
            SearchHit(
                paper=paper,
                score=score,
                matched_terms=list(matched.keys()),
                matched_fields=ordered_fields,
                snippet=snippet,
            )
        )

    hits.sort(key=lambda hit: (hit.score, hit.paper.year), reverse=True)
    return hits


def command_sync(args: argparse.Namespace) -> int:
    config = load_config()
    with connect_readonly(str(config["sqlite_path"])) as connection:
        papers = fetch_all_papers(connection, config)
    write_catalog(papers, config)
    print(f"同步完成，共写入 {len(papers)} 篇文献到 catalog/。")
    return 0


def command_search(args: argparse.Namespace) -> int:
    config = load_config()
    with connect_readonly(str(config["sqlite_path"])) as connection:
        papers = fetch_all_papers(connection, config)
    match_all = not args.any
    hits = search_papers(papers, args.query, int(config["max_context_chars"]), match_all=match_all)
    limit = args.limit or int(config["default_limit"])
    terms = tokenize_query(args.query)
    mode = "ANY(命中任一)" if args.any else "ALL(全部命中)"
    print(f"检索词: {args.query}")
    print(f"分词: {' / '.join(terms)}  |  多词模式: {mode}")
    print("覆盖范围: title / tags / collections / abstract / Zotero .zotero-ft-cache（字段加权排序，非语义）")
    print(f"命中数量: {len(hits)}（按相关度降序，展示前 {min(limit, len(hits))} 条）")
    print("")
    for hit in hits[:limit]:
        paper = hit.paper
        print(
            f"- [score {hit.score}] {short_authors(paper.authors)} | {paper.title} | "
            f"{paper.year} | `{paper.citation_key}`"
        )
        print(f"  - 命中字段: {', '.join(hit.matched_fields)}  |  命中词: {', '.join(hit.matched_terms)}")
        if hit.snippet:
            print(f"  - snippet: {hit.snippet}")
    return 0


def command_paper(args: argparse.Namespace) -> int:
    config = load_config()
    with connect_readonly(str(config["sqlite_path"])) as connection:
        papers = fetch_all_papers(connection, config)
        paper = next(
            (
                item
                for item in papers
                if item.citation_key == args.key or item.zotero_key == args.key
            ),
            None,
        )
        if paper is None:
            print(f"未找到论文: {args.key}")
            return 1
        annotations = fetch_annotations(connection, paper)

    print(f"# {paper.title}")
    print("")
    print(f"- citationKey: `{paper.citation_key}`")
    print(f"- zotero_key: `{paper.zotero_key}`")
    print(f"- authors: {', '.join(paper.authors)}")
    print(f"- year: {paper.year}")
    print(f"- venue: {paper.venue}")
    print(f"- doi: {paper.doi}")
    print(f"- tags: {', '.join(paper.tags)}")
    print(f"- collections: {', '.join(paper.collections)}")
    print(f"- fulltext_cache: {'; '.join(paper.fulltext_paths)}")
    print("")
    print("## Abstract")
    print("")
    print(paper.abstract or "无摘要。")
    print("")
    print("## Annotations")
    print("")
    if not annotations:
        print("无标注。")
    for row in annotations:
        page = f"p.{row['pageLabel']} " if row["pageLabel"] else ""
        text = row["text"] or ""
        comment = row["comment"] or ""
        print(f"- {page}{text}")
        if comment:
            print(f"  - comment: {comment}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="只读 Zotero 查询与目录同步工具。")
    subparsers = parser.add_subparsers(dest="command", required=True)

    sync_parser = subparsers.add_parser("sync", help="刷新 catalog/ 派生索引。")
    sync_parser.set_defaults(func=command_sync)

    search_parser = subparsers.add_parser("search", help="检索 Zotero 元数据与全文缓存。")
    search_parser.add_argument("query", help="检索词；多词以空格分隔（如 \"鲁棒 扇区\" 或中英同义词）。")
    search_parser.add_argument("--limit", type=int, default=0, help="最大返回条数。")
    search_parser.add_argument(
        "--any",
        action="store_true",
        help="多词时命中任一即可（默认要求全部命中）。配合同义词扩展召回。",
    )
    search_parser.set_defaults(func=command_search)

    paper_parser = subparsers.add_parser("paper", help="按 citationKey 或 Zotero key 输出单篇全档。")
    paper_parser.add_argument("--key", required=True, help="citationKey 或 Zotero item key。")
    paper_parser.set_defaults(func=command_paper)
    return parser


def main() -> int:
    configure_stdout()
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except sqlite3.Error as exc:
        print(f"SQLite 读取失败: {exc}", file=sys.stderr)
        return 1
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
