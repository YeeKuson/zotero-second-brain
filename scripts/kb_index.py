from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union


ROOT = Path(__file__).resolve().parents[1]
INDEX_DIR = ROOT / "indexes"

CONTENT_ROOTS = [
    ROOT / "notes",
    ROOT / "syntheses",
    ROOT / "entities",
]

CATALOG_PATH = ROOT / "catalog" / "CATALOG.md"

FrontmatterValue = Union[str, List[str]]


@dataclass(frozen=True)
class CompiledEntry:
    path: Path
    title: str
    entry_type: str
    status: str
    updated_at: str
    tags: list[str]
    citation_keys: list[str]
    related: list[str]
    kind: str
    axis: str
    scope: list[str]


def parse_frontmatter(path: Path) -> dict[str, FrontmatterValue]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}

    end_marker = text.find("\n---\n", 4)
    if end_marker == -1:
        return {}

    raw_frontmatter = text[4:end_marker].splitlines()
    result: dict[str, FrontmatterValue] = {}
    current_key = ""

    for line in raw_frontmatter:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if stripped.startswith("- ") and current_key:
            current_value = result.get(current_key)
            if isinstance(current_value, list):
                current_value.append(stripped[2:].strip().strip('"').strip("'"))
            continue

        if ":" not in line:
            continue

        key, value = line.split(":", 1)
        current_key = key.strip()
        clean_value = value.strip().strip('"').strip("'")

        if clean_value == "[]":
            result[current_key] = []
        elif clean_value:
            result[current_key] = clean_value
        else:
            result[current_key] = []

    return result


def as_text(value: Optional[FrontmatterValue], fallback: str = "") -> str:
    if isinstance(value, str):
        return value
    return fallback


def as_list(value: Optional[FrontmatterValue]) -> list[str]:
    if isinstance(value, list):
        return value
    if isinstance(value, str) and value:
        return [value]
    return []


def collect_entries() -> list[CompiledEntry]:
    entries: list[CompiledEntry] = []
    for content_root in CONTENT_ROOTS:
        if not content_root.exists():
            continue
        for path in sorted(content_root.rglob("*.md")):
            metadata = parse_frontmatter(path)
            if not metadata:
                continue

            citation_keys = as_list(metadata.get("covered_citation_keys"))
            single_key = as_text(metadata.get("citation_key"))
            if single_key and single_key not in citation_keys:
                citation_keys.append(single_key)

            tags = as_list(metadata.get("tags"))
            tags.extend(tag for tag in as_list(metadata.get("source_tags")) if tag not in tags)

            entries.append(
                CompiledEntry(
                    path=path,
                    title=as_text(metadata.get("title"), path.stem),
                    entry_type=as_text(metadata.get("type"), "unknown"),
                    status=as_text(metadata.get("status"), "unknown"),
                    updated_at=as_text(metadata.get("updated_at")),
                    tags=tags,
                    citation_keys=citation_keys,
                    related=as_list(metadata.get("related")),
                    kind=as_text(metadata.get("kind")),
                    axis=as_text(metadata.get("axis")),
                    scope=as_list(metadata.get("scope")),
                )
            )
    return entries


def catalog_citation_keys() -> set[str]:
    if not CATALOG_PATH.exists():
        return set()

    keys: set[str] = set()
    for line in CATALOG_PATH.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or stripped.startswith("|---"):
            continue
        cells = [cell.strip(" `") for cell in stripped.strip("|").split("|")]
        if cells and cells[0] and cells[0] != "citationKey":
            keys.add(cells[0])
    return keys


def catalog_papers() -> list[dict[str, object]]:
    """从 CATALOG.md 解析每篇的 key / tags / collections，供往回织比对 scope。"""
    if not CATALOG_PATH.exists():
        return []

    lines = CATALOG_PATH.read_text(encoding="utf-8").splitlines()
    headers: list[str] = []
    header_idx = -1
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("|citationKey"):
            headers = [cell.strip() for cell in stripped.strip("|").split("|")]
            header_idx = index
            break
    if header_idx == -1:
        return []

    col = {name: idx for idx, name in enumerate(headers)}
    if not {"citationKey", "tags", "collections"} <= col.keys():
        return []

    papers: list[dict[str, object]] = []
    for line in lines[header_idx + 1 :]:
        stripped = line.strip()
        if not stripped.startswith("|") or stripped.startswith("|---"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < len(headers):
            continue
        key = cells[col["citationKey"]].strip(" `")
        if not key or key == "citationKey":
            continue
        tags = {t.strip() for t in cells[col["tags"]].split(";") if t.strip()}
        collections = {c.strip() for c in cells[col["collections"]].split(";") if c.strip()}
        papers.append({"key": key, "tags": tags, "collections": collections})
    return papers


def pending_for_synthesis(
    entry: CompiledEntry, papers: list[dict[str, object]]
) -> list[str]:
    """往回织触发器：返回落在该 synthesis scope 内、但尚未织入 covered 的论文 key。"""
    if entry.entry_type != "synthesis" or not entry.scope:
        return []

    scope = set(entry.scope)
    covered = set(entry.citation_keys)
    pending: list[str] = []
    for paper in papers:
        key = paper["key"]
        if key in covered:
            continue
        tags = paper["tags"]  # type: ignore[assignment]
        collections = paper["collections"]  # type: ignore[assignment]
        if entry.axis == "collection":
            hit = bool(scope & collections)
        elif entry.axis == "tag":
            hit = bool(scope & tags)
        else:  # mixed：collection 与 tag 任一命中
            hit = bool(scope & (collections | tags))
        if hit:
            pending.append(key)  # type: ignore[arg-type]
    return pending


def relative_markdown_link(path: Path, label: str) -> str:
    relative_path = path.relative_to(ROOT).as_posix()
    return f"[{label}](../{relative_path})"


def write_compiled_index(entries: list[CompiledEntry]) -> None:
    lines = [
        "# Compiled Knowledge Index",
        "",
        "本文件由 `python scripts/kb_index.py` 生成，记录 agent 已编译的知识产物。",
        "",
        "| Title | Type | Status | Updated | Citation Keys | Path |",
        "|---|---|---|---|---|---|",
    ]

    for entry in entries:
        relative_path = entry.path.relative_to(ROOT).as_posix()
        keys = ", ".join(entry.citation_keys)
        lines.append(
            f"| {entry.title} | {entry.entry_type} | {entry.status} | {entry.updated_at} | {keys} | `{relative_path}` |"
        )

    (INDEX_DIR / "COMPILED.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_status_index(entries: list[CompiledEntry]) -> None:
    grouped: dict[str, list[CompiledEntry]] = {}
    for entry in entries:
        grouped.setdefault(entry.status, []).append(entry)

    lines = [
        "# Compilation Status",
        "",
        "本文件由 `python scripts/kb_index.py` 生成。",
        "",
    ]

    for status in sorted(grouped):
        lines.append(f"## {status}")
        lines.append("")
        for entry in sorted(grouped[status], key=lambda item: item.title):
            lines.append(f"- {relative_markdown_link(entry.path, entry.title)} ({entry.entry_type})")
        lines.append("")

    (INDEX_DIR / "BY-STATUS.md").write_text("\n".join(lines), encoding="utf-8")


def write_tag_index(entries: list[CompiledEntry]) -> None:
    tag_map: dict[str, list[CompiledEntry]] = {}
    for entry in entries:
        for tag in entry.tags:
            tag_map.setdefault(tag, []).append(entry)

    lines = [
        "# Compiled Tag Index",
        "",
        "本文件由 `python scripts/kb_index.py` 生成。",
        "",
    ]

    for tag in sorted(tag_map):
        lines.append(f"## {tag}")
        lines.append("")
        for entry in sorted(tag_map[tag], key=lambda item: item.title):
            lines.append(f"- {relative_markdown_link(entry.path, entry.title)} ({entry.status})")
        lines.append("")

    (INDEX_DIR / "BY-TAG.md").write_text("\n".join(lines), encoding="utf-8")


def write_stale_index(
    entries: list[CompiledEntry],
    all_catalog_keys: set[str],
    pending_map: dict[Path, list[str]],
    noted_keys: set[str],
) -> None:
    covered_keys: set[str] = set()
    stale_entries = [entry for entry in entries if entry.status == "stale"]
    for entry in entries:
        covered_keys.update(entry.citation_keys)

    uncompiled_keys = sorted(all_catalog_keys - covered_keys)

    lines = [
        "# Freshness Index",
        "",
        "本文件由 `python scripts/kb_index.py` 生成。",
        "",
        "## 待织入（往回织触发）",
        "",
        "每篇 synthesis 在其 scope 内、尚未织入 covered 的论文。编译模式应优先回头重织这些，",
        "而不是另起一篇堆叠（见 Doctrine 往回织条）。",
        "",
    ]
    reweave_entries = [
        (entry, pending_map.get(entry.path, []))
        for entry in entries
        if entry.entry_type == "synthesis" and pending_map.get(entry.path)
    ]
    if reweave_entries:
        for entry, pending in sorted(reweave_entries, key=lambda item: item[0].title):
            scope = " × ".join(entry.scope) if entry.scope else "(scope 未填)"
            to_distill = [key for key in pending if key not in noted_keys]
            to_weave = [key for key in pending if key in noted_keys]
            lines.append(
                f"### {entry.title} （scope: {scope}，待织入 {len(pending)} 篇）"
            )
            lines.append(f"**第一段·待蒸馏（还没 note，需读一次全文）：{len(to_distill)} 篇**")
            for key in to_distill[:15]:
                lines.append(f"- `{key}`")
            if len(to_distill) > 15:
                lines.append(f"- …… 另有 {len(to_distill) - 15} 篇")
            lines.append(f"**第二段·已蒸馏待并入综述（有 note，只读 note）：{len(to_weave)} 篇**")
            for key in to_weave[:15]:
                lines.append(f"- `{key}`")
            if len(to_weave) > 15:
                lines.append(f"- …… 另有 {len(to_weave) - 15} 篇")
            lines.append("")
    else:
        lines.append("- 暂无待织入论文。")
        lines.append("")

    lines.extend(["## Stale Syntheses", ""])

    if stale_entries:
        for entry in sorted(stale_entries, key=lambda item: item.title):
            lines.append(f"- {relative_markdown_link(entry.path, entry.title)}")
    else:
        lines.append("- 暂无标记为 stale 的编译页。")

    lines.extend(["", "## Uncompiled Citation Keys", ""])
    if uncompiled_keys:
        for key in uncompiled_keys:
            lines.append(f"- `{key}`")
    else:
        lines.append("- 暂无可从 CATALOG 判断的未编译 citationKey。")

    (INDEX_DIR / "STALE.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_overview(
    entries: list[CompiledEntry],
    all_catalog_keys: set[str],
    pending_map: dict[Path, list[str]],
    noted_keys: set[str],
) -> None:
    syntheses = [entry for entry in entries if entry.entry_type == "synthesis"]
    convergent = [entry for entry in syntheses if entry.kind == "convergent"]
    divergent = [entry for entry in syntheses if entry.kind == "divergent"]
    notes = [entry for entry in entries if entry.entry_type == "paper_note"]

    covered_keys: set[str] = set()
    for entry in entries:
        covered_keys.update(entry.citation_keys)
    catalog_total = len(all_catalog_keys)
    covered_total = len(all_catalog_keys & covered_keys)

    def overview_line(entry: CompiledEntry) -> str:
        scope = " × ".join(entry.scope) if entry.scope else "(scope 未填)"
        covered = len(entry.citation_keys)
        pending = pending_map.get(entry.path, [])
        to_distill = [key for key in pending if key not in noted_keys]
        if pending:
            reweave = f" — ⟳待织入 {len(pending)} 篇（其中待蒸馏 {len(to_distill)} 篇）"
        else:
            reweave = ""
        return (
            f"- {relative_markdown_link(entry.path, entry.title)} "
            f"— scope: {scope} — 覆盖 {covered} 篇{reweave} — status: {entry.status}"
        )

    lines = [
        "# Knowledge Base Overview （会话入口）",
        "",
        "本文件由 `python scripts/kb_index.py` 自动生成，是每次对话的默认入口。",
        "开新对话先读它：能引用现成编译产物就别从零重建，只补增量。",
        "collection 与 tag 是并列双轴；编译分汇总型(convergent)与碰撞型(divergent)。",
        "",
        "## 汇总型编译（convergent · 沿单一轴值收敛）",
        "",
    ]
    convergent_by_collection = [entry for entry in convergent if entry.axis == "collection"]
    convergent_by_tag = [entry for entry in convergent if entry.axis == "tag"]
    convergent_other = [
        entry for entry in convergent if entry.axis not in {"collection", "tag"}
    ]

    lines.append("### 按 collection")
    lines.append("")
    if convergent_by_collection:
        lines.extend(overview_line(entry) for entry in sorted(convergent_by_collection, key=lambda item: item.title))
    else:
        lines.append("- 暂无。")
    lines.extend(["", "### 按 tag", ""])
    if convergent_by_tag:
        lines.extend(overview_line(entry) for entry in sorted(convergent_by_tag, key=lambda item: item.title))
    else:
        lines.append("- 暂无。")
    if convergent_other:
        lines.extend(["", "### 其他轴", ""])
        lines.extend(overview_line(entry) for entry in sorted(convergent_other, key=lambda item: item.title))

    lines.extend(["", "## 碰撞型编译（divergent · 跨轴混合找空白）", ""])
    if divergent:
        lines.extend(overview_line(entry) for entry in sorted(divergent, key=lambda item: item.title))
    else:
        lines.append("- 暂无。")

    lines.extend(["", "## 覆盖概览", ""])
    lines.append(f"- catalog 共 {catalog_total} 篇；已被任意编译覆盖 {covered_total} 篇。")
    lines.append(f"- 已编译单篇 note：{len(notes)} 篇。")
    lines.append("- 未覆盖清单见 `indexes/STALE.md`，过时综述同文件标记。")

    (INDEX_DIR / "OVERVIEW.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    INDEX_DIR.mkdir(exist_ok=True)
    entries = collect_entries()
    catalog_keys = catalog_citation_keys()
    papers = catalog_papers()
    pending_map = {entry.path: pending_for_synthesis(entry, papers) for entry in entries}
    noted_keys: set[str] = set()
    for entry in entries:
        if entry.entry_type == "paper_note":
            noted_keys.update(entry.citation_keys)
    write_compiled_index(entries)
    write_status_index(entries)
    write_tag_index(entries)
    write_stale_index(entries, catalog_keys, pending_map, noted_keys)
    write_overview(entries, catalog_keys, pending_map, noted_keys)
    total_pending = sum(len(keys) for keys in pending_map.values())
    print(
        f"编译状态索引生成完成，共 {len(entries)} 条编译产物，待织入 {total_pending} 篇。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
