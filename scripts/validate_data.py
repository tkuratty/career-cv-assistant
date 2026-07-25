#!/usr/bin/env python3
"""Validate the structured career data in data/ (and selection files).

Machine-checks the conventions that AGENTS.md ("Data conventions") otherwise
leaves to agent discipline:

- career.{ja,en}.yaml: position/highlight ids match across languages (set and
  order), start/end dates match, dates are YYYY-MM (end may be "present"),
  highlight tags are identical across languages.
- education/certifications: ids match across languages.
- skills.yaml: categories carry label.{ja,en}; dict items carry both ja and en.
- every cv/output/*/selection.yaml (or --selection PATH): referenced position
  and highlight ids exist in career data.

Exit code 0 when everything passes, 1 with a per-problem message otherwise.

Usage:
    python scripts/validate_data.py
    python scripts/validate_data.py --selection cv/output/acme/selection.yaml
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUTPUT = ROOT / "cv" / "output"

DATE_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")

# Windows consoles often use a legacy codepage that cannot print Japanese.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

errors: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def load(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def check_date(value, field: str, where: str, allow_present: bool = False) -> None:
    text = str(value)
    if allow_present and text == "present":
        return
    if not DATE_RE.match(text):
        err(f"{where}: {field} is '{text}' (expected YYYY-MM"
            + (" or 'present')" if allow_present else ")"))


def check_career() -> dict[str, dict]:
    """Cross-check career.ja.yaml / career.en.yaml. Returns ja positions by id."""
    ja = load(DATA / "career.ja.yaml").get("positions", [])
    en = load(DATA / "career.en.yaml").get("positions", [])

    ja_ids = [p.get("id") for p in ja]
    en_ids = [p.get("id") for p in en]
    if ja_ids != en_ids:
        err(f"career: position ids differ — ja={ja_ids} en={en_ids}")

    en_by_id = {p.get("id"): p for p in en}
    for pos in ja:
        pid = pos.get("id")
        where = f"career position '{pid}'"
        check_date(pos.get("start"), "start", where)
        check_date(pos.get("end"), "end", where, allow_present=True)

        other = en_by_id.get(pid)
        if other is None:
            continue
        for field in ("start", "end"):
            if str(pos.get(field)) != str(other.get(field)):
                err(f"{where}: {field} differs between ja ({pos.get(field)}) "
                    f"and en ({other.get(field)})")

        ja_hl = pos.get("highlights", [])
        en_hl = other.get("highlights", [])
        ja_hl_ids = [h.get("id") for h in ja_hl]
        en_hl_ids = [h.get("id") for h in en_hl]
        if ja_hl_ids != en_hl_ids:
            err(f"{where}: highlight ids differ — ja={ja_hl_ids} en={en_hl_ids}")

        en_hl_by_id = {h.get("id"): h for h in en_hl}
        for h in ja_hl:
            hid = h.get("id")
            twin = en_hl_by_id.get(hid)
            if twin is not None and h.get("tags") != twin.get("tags"):
                err(f"{where} highlight '{hid}': tags differ between ja and en "
                    f"(tags are language-neutral and must be identical)")

    return {p.get("id"): p for p in ja}


def check_items_parity(basename: str) -> None:
    """education / certifications: same ids across ja/en."""
    ja = load(DATA / f"{basename}.ja.yaml").get("items", [])
    en = load(DATA / f"{basename}.en.yaml").get("items", [])
    ja_ids = [i.get("id") for i in ja]
    en_ids = [i.get("id") for i in en]
    if ja_ids != en_ids:
        err(f"{basename}: item ids differ — ja={ja_ids} en={en_ids}")


def check_skills() -> None:
    skills = load(DATA / "skills.yaml")
    for cat in skills.get("categories", []):
        key = cat.get("key", "?")
        label = cat.get("label")
        if not isinstance(label, dict) or "ja" not in label or "en" not in label:
            err(f"skills category '{key}': label must have both ja and en")
        for item in cat.get("items", []):
            if isinstance(item, dict) and ("ja" not in item or "en" not in item):
                err(f"skills category '{key}': dict item {item} must have both ja and en")


def check_selection(path: Path, positions_by_id: dict[str, dict]) -> None:
    sel = load(path)
    rel = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
    for entry in sel.get("positions") or []:
        pid = entry.get("id")
        pos = positions_by_id.get(pid)
        if pos is None:
            err(f"{rel}: unknown position id '{pid}'")
            continue
        known_hl = {h.get("id") for h in pos.get("highlights", [])}
        for hid in entry.get("highlights") or []:
            if hid not in known_hl:
                err(f"{rel}: unknown highlight id '{hid}' (in position '{pid}')")


def main() -> None:
    ap = argparse.ArgumentParser(description="Validate data/ and selection files.")
    ap.add_argument("--selection", type=Path, action="append", default=[],
                    help="Selection YAML to validate (default: all under cv/output/).")
    args = ap.parse_args()

    positions_by_id = check_career()
    check_items_parity("education")
    check_items_parity("certifications")
    check_skills()

    selections = args.selection or sorted(OUTPUT.glob("*/selection.yaml"))
    for sel_path in selections:
        check_selection(sel_path, positions_by_id)

    if errors:
        for e in errors:
            print(f"  ! {e}", file=sys.stderr)
        sys.exit(f"validate_data: {len(errors)} problem(s) found.")
    print(f"validate_data: OK (career/education/certifications/skills"
          f" + {len(selections)} selection file(s))")


if __name__ == "__main__":
    main()
