from __future__ import annotations

from pathlib import Path
from typing import List, Union


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_DIRS = [
    "catalog",
    "notes",
    "syntheses",
    "syntheses/categories",
    "syntheses/topics",
    "entities",
    "entities/methods",
    "entities/datasets",
    "entities/authors",
    "indexes",
    "outputs",
    "logs",
    "templates",
    "scripts",
]

REQUIRED_FILES = [
    "AGENTS.md",
    "CLAUDE.md",
    "config.example.yaml",
    "README.md",
    "templates/paper-note.md",
    "templates/synthesis.md",
    "templates/entity.md",
    "scripts/zotero_query.py",
    "scripts/kb_index.py",
    "scripts/check_structure.py",
]

CONTENT_ROOTS = [
    ROOT / "notes",
    ROOT / "syntheses",
    ROOT / "entities",
    ROOT / "outputs",
]

REQUIRED_FIELDS_BY_TYPE = {
    "paper_note": ["title", "type", "zotero_key", "citation_key", "status"],
    "synthesis": ["title", "type", "kind", "axis", "scope", "covered_citation_keys", "status"],
    "entity": ["title", "type", "entity_type", "status"],
    "output": ["title", "type", "status"],
}


FrontmatterValue = Union[str, List[str]]


def has_frontmatter(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    return text.startswith("---\n") and "\n---\n" in text[4:]


def parse_frontmatter(path: Path) -> dict[str, FrontmatterValue]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}

    end_marker = text.find("\n---\n", 4)
    if end_marker == -1:
        return {}

    result: dict[str, FrontmatterValue] = {}
    current_key = ""
    for line in text[4:end_marker].splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if stripped.startswith("- ") and current_key:
            value = result.get(current_key)
            if isinstance(value, list):
                value.append(stripped[2:].strip().strip('"').strip("'"))
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


def frontmatter_list(metadata: dict[str, FrontmatterValue], key: str) -> list[str]:
    value = metadata.get(key)
    if isinstance(value, list):
        return value
    if isinstance(value, str) and value:
        return [value]
    return []


def frontmatter_text(metadata: dict[str, FrontmatterValue], key: str) -> str:
    value = metadata.get(key)
    if isinstance(value, str):
        return value
    return ""


def collect_content_files() -> list[Path]:
    files: list[Path] = []
    for content_root in CONTENT_ROOTS:
        if content_root.exists():
            files.extend(
                path
                for path in content_root.rglob("*.md")
                if path.name != ".gitkeep"
            )
    return sorted(files)


def validate_related_paths(
    markdown_file: Path,
    metadata: dict[str, FrontmatterValue],
    errors: list[str],
) -> None:
    for reference in frontmatter_list(metadata, "related"):
        if not reference:
            continue
        if not reference.endswith(".md"):
            relative_path = markdown_file.relative_to(ROOT)
            errors.append(f"{relative_path} 的 related 使用了非 Markdown 路径: {reference}")
            continue
        if Path(reference).is_absolute():
            relative_path = markdown_file.relative_to(ROOT)
            errors.append(f"{relative_path} 的 related 不能使用绝对路径: {reference}")
            continue
        if not (ROOT / reference).is_file():
            relative_path = markdown_file.relative_to(ROOT)
            errors.append(f"{relative_path} 的 related 指向不存在的文件: {reference}")


def validate_required_fields(
    markdown_file: Path,
    metadata: dict[str, FrontmatterValue],
    errors: list[str],
) -> None:
    entry_type = frontmatter_text(metadata, "type")
    if not entry_type:
        errors.append(f"{markdown_file.relative_to(ROOT)} 缺少 type 字段")
        return

    required_fields = REQUIRED_FIELDS_BY_TYPE.get(entry_type, ["title", "type", "status"])
    for field_name in required_fields:
        value = metadata.get(field_name)
        if value is None:
            errors.append(f"{markdown_file.relative_to(ROOT)} 缺少字段: {field_name}")


def main() -> int:
    errors: list[str] = []

    for directory in REQUIRED_DIRS:
        path = ROOT / directory
        if not path.is_dir():
            errors.append(f"缺少目录: {directory}")

    for file_name in REQUIRED_FILES:
        path = ROOT / file_name
        if not path.is_file():
            errors.append(f"缺少文件: {file_name}")

    for markdown_file in collect_content_files():
        if not has_frontmatter(markdown_file):
            errors.append(f"缺少 frontmatter: {markdown_file.relative_to(ROOT)}")
            continue

        metadata = parse_frontmatter(markdown_file)
        validate_required_fields(markdown_file, metadata, errors)
        validate_related_paths(markdown_file, metadata, errors)

    if errors:
        print("结构检查失败:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("结构检查通过。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
