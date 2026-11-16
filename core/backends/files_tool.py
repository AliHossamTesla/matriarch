#!/usr/bin/env python3
"""Helper for Matriarch's `files` memory backend. Standard library only.

  files_tool.py query <dir> [filter]...        rows whose properties match, newest first
  files_tool.py get <file>                     one row: properties, sections and body
  files_tool.py new <dir> <stem> [Key=Value]...  create <dir>/<stem>.md (never overwrites)
  files_tool.py set <file> Key=Value...        update one-line properties (front matter)
  files_tool.py section <file> <Name> <textfile>  replace or add the "## <Name>" section
                                                 (multi-line properties: Statement, Progress, ...)

Filters: Key=Value (exact; Key=a|b for any of several), Key!=Value, Key~text
(contains, any case), Key>=YYYY-MM-DD, Key<=YYYY-MM-DD. Checkboxes are true or false.
Output is JSON; errors are {"error": ...} with exit code 1.
"""
from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from pathlib import Path

FRONT = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)$", re.S)
FILTER = re.compile(r"^([A-Za-z][\w ]*?)\s*(!=|>=|<=|=|~)(.*)$")


class Fail(Exception):
    pass


def read(path: Path) -> str:
    if not path.is_file():
        raise Fail(f"no such file: {path}")
    return path.read_text(encoding="utf-8-sig")


def parse(text: str) -> tuple[dict, str]:
    m = FRONT.match(text)
    if not m:
        return {}, text
    props: dict = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            props[key.strip()] = value.strip()
    return props, m.group(2)


def sections(body: str) -> dict:
    out, name, buf = {}, None, []
    for line in body.splitlines():
        m = re.match(r"^## (.+?)\s*$", line)
        if m:
            if name:
                out[name] = "\n".join(buf).strip("\n")
            name, buf = m.group(1), []
        elif name:
            buf.append(line)
    if name:
        out[name] = "\n".join(buf).strip("\n")
    return out


def render(props: dict, body: str) -> str:
    lines = []
    for key, value in props.items():
        if "\n" in value:
            raise Fail(f"{key} has several lines: use the section command")
        lines.append(f"{key}: {value}")
    return "---\n" + "\n".join(lines) + "\n---\n" + body


def write_atomic(path: Path, text: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".tmp-", suffix=".md")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(text)
    os.replace(tmp, path)


def parse_args(args: list[str], allowed: set[str]) -> list[tuple[str, str, str]]:
    out = []
    for a in args:
        m = FILTER.match(a)
        if not m or m.group(2) not in allowed:
            raise Fail(f"bad argument {a!r}; allowed operators: {' '.join(sorted(allowed))}")
        out.append((m.group(1).strip(), m.group(2), m.group(3).strip()))
    return out


def matches(props: dict, filters: list[tuple[str, str, str]]) -> bool:
    for key, op, want in filters:
        have = props.get(key, "")
        if op == "=" and have not in want.split("|"):
            return False
        if op == "!=" and have in want.split("|"):
            return False
        if op == "~" and want.lower() not in have.lower():
            return False
        if op == ">=" and not (have and have >= want):
            return False
        if op == "<=" and not (have and have <= want):
            return False
    return True


def need_dir(directory: str) -> Path:
    d = Path(directory)
    if not d.is_dir():
        raise Fail(f"no such folder: {d} (check memory.*.path)")
    return d


def cmd_query(directory: str, *args: str) -> list:
    filters = parse_args(list(args), {"=", "!=", "~", ">=", "<="})
    rows = []
    for f in need_dir(directory).glob("*.md"):
        props, _ = parse(read(f))
        if matches(props, filters):
            rows.append({"file": str(f), **props})
    rows.sort(key=lambda r: (r.get("Date", ""), r["file"]), reverse=True)
    return rows


def cmd_get(file: str) -> dict:
    props, body = parse(read(Path(file)))
    return {"file": file, "properties": props, "sections": sections(body), "body": body}


def cmd_new(directory: str, stem: str, *args: str) -> dict:
    if not re.match(r"^[\w.-]+$", stem):
        raise Fail(f"bad file name {stem!r}: letters, digits, '.', '-', '_' only")
    d = Path(directory)
    if not d.is_dir():
        need_dir(str(d.parent))  # the memory folder itself must exist
        d.mkdir()
    path = d / f"{stem}.md"
    props = {k: v for k, _, v in parse_args(list(args), {"="})}
    try:
        with open(path, "x", encoding="utf-8") as fh:  # "x": fail if it exists
            fh.write(render(props, ""))
    except FileExistsError:
        raise Fail(f"exists: {path}")
    return {"file": str(path), "created": True}


def cmd_set(file: str, *args: str) -> dict:
    path = Path(file)
    props, body = parse(read(path))
    updates = parse_args(list(args), {"="})
    for key, _, value in updates:
        props[key] = value
    write_atomic(path, render(props, body))
    return {"file": file, "updated": sorted(k for k, _, _ in updates)}


def cmd_section(file: str, name: str, textfile: str) -> dict:
    path = Path(file)
    props, body = parse(read(path))
    text = read(Path(textfile)).strip("\n")
    pattern = re.compile(rf"^## {re.escape(name)}\s*\n.*?(?=^## |\Z)", re.S | re.M)
    block = f"## {name}\n{text}\n\n"
    body = pattern.sub(lambda _: block, body, count=1) if pattern.search(body) else body.rstrip("\n") + ("\n\n" if body.strip() else "") + block
    write_atomic(path, render(props, body))
    return {"file": file, "section": name}


def main(argv: list[str]) -> int:
    commands = {"query": cmd_query, "get": cmd_get, "new": cmd_new, "set": cmd_set, "section": cmd_section}
    if len(argv) < 3 or argv[1] not in commands:
        print(__doc__)
        return 2
    try:
        result = commands[argv[1]](*argv[2:])
    except (Fail, TypeError) as e:
        print(json.dumps({"error": str(e)}))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
