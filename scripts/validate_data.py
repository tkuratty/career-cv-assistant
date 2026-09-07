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
- every companies/*/messages.yaml: known message types/source kinds, quotes carry
  a source that exists, evidence highlight ids exist in career data, and the
  誇張防止ルール — strength must match the number of backing highlights
  (strong ≥ 2 / partial = 1 / none = 0).
- every interviews/*.md: front-matter links to a real opportunity/company, round
  is an integer, round_type and status use the known vocabulary, date is
  YYYY-MM-DD, and each asked[] entry carries a question plus an answered value
  (ok / weak / missed).
- every opportunities/*.md and agents/*.md: slug matches the filename, status uses
  the AGENTS.md vocabulary with no reason smuggled into it, dates are YYYY-MM-DD,
  and a closed opportunity carries outcome (未応募 / 不採用 / 辞退) + closed_reason
  — so 「自分で降りた」 and 「落とされた」 stay countable apart.
- opportunities/seen.yaml (when present): valid YAML with the required fields.

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

# Schema for companies/*/messages.yaml lives next to the report tool that
# consumes it, so the two can never drift apart.
from company_message_fit import (
    MESSAGE_TYPES,
    MIN_EVIDENCE,
    SOURCE_KINDS,
    STRENGTHS,
)

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUTPUT = ROOT / "cv" / "output"
COMPANIES = ROOT / "companies"
INTERVIEWS = ROOT / "interviews"
OPPORTUNITIES = ROOT / "opportunities"
AGENTS = ROOT / "agents"

# Pipeline vocabularies (AGENTS.md §6). scripts/list_pipeline.py reads the same
# front-matter, so a new value invented here silently breaks the dedupe view.
OPPORTUNITY_STATUSES = ("検討中", "応募前", "書類選考中", "面接中", "内定", "見送り")
# How a closed opportunity ended. 未応募 = dropped before applying, 不採用 = the
# company rejected, 辞退 = withdrew after applying. Kept out of `status` so the
# post-application 歩留まり (不採用 / applied) can be counted.
OUTCOMES = ("未応募", "不採用", "辞退")
AGENT_STATUSES = ("接触", "面談予定", "継続", "休眠", "終了")
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")

# Interview rounds (interviews/*.md). Shared with the prep-interview playbook.
ROUND_TYPES = {"casual", "first", "technical", "manager", "executive", "hr",
               "reference", "offer"}
INTERVIEW_STATUSES = ("予定", "完了", "見送り", "キャンセル")
# asked[]: how the question actually went. weak/missed are re-surfaced by
# scripts/interview_brief.py as 再出題 for later rounds.
ANSWERED_VALUES = ("ok", "weak", "missed")

DATE_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
DAY_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$")

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


def check_day(value, field: str, where: str) -> None:
    if value is None:
        return
    if not DAY_RE.match(str(value)):
        err(f"{where}: {field} is '{value}' (expected YYYY-MM-DD)")


def check_messages(path: Path, highlight_ids: set[str]) -> None:
    """companies/<slug>/messages.yaml — schema + the 誇張防止 evidence rule."""
    doc = load(path)
    rel = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
    check_day(doc.get("updated"), "updated", str(rel))

    source_ids: set[str] = set()
    for src in doc.get("sources") or []:
        sid = src.get("id")
        where = f"{rel} source '{sid}'"
        if not sid:
            err(f"{rel}: a source is missing 'id'")
            continue
        if sid in source_ids:
            err(f"{where}: duplicate source id")
        source_ids.add(sid)
        if not src.get("url"):
            err(f"{where}: url is required (出典なしの引用を禁止)")
        kind = src.get("kind")
        if kind not in SOURCE_KINDS:
            err(f"{where}: kind is '{kind}' (expected {'/'.join(sorted(SOURCE_KINDS))})")
        check_day(src.get("accessed"), "accessed", where)

    seen_ids: set[str] = set()
    for msg in doc.get("messages") or []:
        mid = msg.get("id")
        where = f"{rel} message '{mid}'"
        if not mid:
            err(f"{rel}: a message is missing 'id'")
            continue
        if mid in seen_ids:
            err(f"{where}: duplicate message id")
        seen_ids.add(mid)

        mtype = msg.get("type")
        if mtype not in MESSAGE_TYPES:
            err(f"{where}: type is '{mtype}' (expected one of "
                f"{', '.join(sorted(MESSAGE_TYPES))})")

        if msg.get("quote") and msg.get("source") not in source_ids:
            err(f"{where}: quote needs a 'source' listed in sources[] "
                f"(got '{msg.get('source')}')")

        evidence = msg.get("evidence") or []
        for hid in evidence:
            if hid not in highlight_ids:
                err(f"{where}: evidence '{hid}' is not a highlight id in "
                    "data/career.*.yaml (裏付けは実在する実績のみ)")

        strength = msg.get("strength")
        if strength not in STRENGTHS:
            err(f"{where}: strength is '{strength}' (expected "
                f"{'/'.join(STRENGTHS)})")
            continue
        n = len(evidence)
        if strength == "none":
            if n:
                err(f"{where}: strength 'none' but {n} evidence highlight(s) — "
                    "裏付けがあるなら partial 以上にしてください")
        elif n < MIN_EVIDENCE[strength]:
            err(f"{where}: strength '{strength}' needs at least "
                f"{MIN_EVIDENCE[strength]} evidence highlight(s), got {n} "
                "(誇張防止: 裏付けの数が主張の上限)")


def front_matter(path: Path) -> tuple[dict | None, str]:
    """Read a record's YAML front-matter. Returns (None, rel) if unusable."""
    text = path.read_text(encoding="utf-8")
    rel = str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path)
    if not text.startswith("---"):
        err(f"{rel}: missing front-matter")
        return None, rel
    end = text.find("\n---", 3)
    if end == -1:
        err(f"{rel}: unterminated front-matter")
        return None, rel
    try:
        return (yaml.safe_load(text[3:end]) or {}), rel
    except yaml.YAMLError as exc:
        err(f"{rel}: bad front-matter ({exc})")
        return None, rel


def check_interview(path: Path) -> None:
    """interviews/<slug>-r<N>.md — front-matter sanity and record links."""
    fm, rel = front_matter(path)
    if fm is None:
        return

    opportunity = fm.get("opportunity")
    if not opportunity:
        err(f"{rel}: 'opportunity' is required (opportunities/<slug>.md の slug)")
    elif not (ROOT / "opportunities" / f"{opportunity}.md").exists():
        err(f"{rel}: opportunity '{opportunity}' has no opportunities/{opportunity}.md")

    company = fm.get("company")
    if company and not (COMPANIES / str(company)).is_dir():
        err(f"{rel}: company '{company}' has no companies/{company}/ directory")

    if not isinstance(fm.get("round"), int):
        err(f"{rel}: round is '{fm.get('round')}' (expected an integer)")

    rtype = fm.get("round_type")
    if rtype not in ROUND_TYPES:
        err(f"{rel}: round_type is '{rtype}' (expected one of "
            f"{', '.join(sorted(ROUND_TYPES))})")

    check_day(fm.get("date"), "date", str(rel))

    status = fm.get("status")
    if status not in INTERVIEW_STATUSES:
        err(f"{rel}: status is '{status}' (expected one of "
            f"{' / '.join(INTERVIEW_STATUSES)})")

    for n, item in enumerate(fm.get("asked") or [], 1):
        where = f"{rel} asked[{n}]"
        if not isinstance(item, dict) or not item.get("q"):
            err(f"{where}: 'q' (the question actually asked) is required")
            continue
        answered = item.get("answered")
        if answered not in ANSWERED_VALUES:
            err(f"{where}: answered is '{answered}' (expected one of "
                f"{' / '.join(ANSWERED_VALUES)})")


def check_opportunity(path: Path) -> None:
    """opportunities/<slug>.md — front-matter vocabulary and closure bookkeeping."""
    fm, rel = front_matter(path)
    if fm is None:
        return

    if fm.get("slug") != path.stem:
        err(f"{rel}: slug is '{fm.get('slug')}' but the filename says '{path.stem}'")

    company = str(fm.get("company") or "")
    if SLUG_RE.match(company) and not (COMPANIES / company).is_dir():
        err(f"{rel}: company '{company}' has no companies/{company}/ directory")

    for field in ("applied_date", "closed_date", "updated"):
        check_day(fm.get(field), field, rel)
    if not fm.get("updated"):
        err(f"{rel}: updated is required")

    status = fm.get("status")
    if status not in OPPORTUNITY_STATUSES:
        hint = ""
        if isinstance(status, str) and "（" in status:
            hint = " — 理由は status ではなく outcome / closed_reason に書く"
        err(f"{rel}: status is '{status}' (expected one of "
            f"{' / '.join(OPPORTUNITY_STATUSES)}){hint}")
        return

    outcome = fm.get("outcome")
    if status == "見送り":
        if outcome not in OUTCOMES:
            err(f"{rel}: closed opportunity needs outcome "
                f"({' / '.join(OUTCOMES)}), got '{outcome}'")
        if not fm.get("closed_reason"):
            err(f"{rel}: closed opportunity needs a one-line closed_reason")
        if outcome in ("不採用", "辞退") and not fm.get("applied_date"):
            err(f"{rel}: outcome '{outcome}' but applied_date is empty "
                "(応募していない案件は 未応募)")
    elif outcome:
        err(f"{rel}: outcome '{outcome}' on a live opportunity "
            f"(status: {status}) — outcome は status: 見送り のときだけ")

    cv = fm.get("cv")
    if cv and not (ROOT / str(cv).split("#")[0].strip()).exists():
        err(f"{rel}: cv path '{cv}' does not exist")


def check_agent(path: Path) -> None:
    """agents/<slug>.md — front-matter vocabulary. `（…）` qualifiers are allowed."""
    fm, rel = front_matter(path)
    if fm is None:
        return

    if fm.get("slug") != path.stem:
        err(f"{rel}: slug is '{fm.get('slug')}' but the filename says '{path.stem}'")

    for field in ("first_contact", "last_meeting", "updated"):
        check_day(fm.get(field), field, rel)
    if not fm.get("updated"):
        err(f"{rel}: updated is required")

    status = str(fm.get("status") or "")
    base = status.split("（")[0]
    if base not in AGENT_STATUSES:
        err(f"{rel}: status is '{status}' (expected one of "
            f"{' / '.join(AGENT_STATUSES)}, optionally with a （…） qualifier)")


def check_seen(path: Path) -> bool:
    """opportunities/seen.yaml — the find-opportunities dedupe log.

    Nothing else reads this file at runtime, so a YAML syntax error here stays
    invisible until a later run tries to parse it. The trap in practice is a URL
    containing `?` written unquoted inside a `{...}` flow mapping — YAML treats
    `?` as a complex-key indicator and the whole document stops parsing.
    """
    if not path.is_file():
        return False
    rel = path.relative_to(ROOT).as_posix()
    try:
        doc = load(path)
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        where = f" (line {mark.line + 1}, column {mark.column + 1})" if mark else ""
        err(f"{rel}: not valid YAML{where}. "
            f"A URL containing '?' must be quoted inside a {{...}} entry")
        return True

    entries = doc.get("seen")
    if entries is None:
        err(f"{rel}: top-level 'seen' key is missing")
        return True
    if not isinstance(entries, list):
        err(f"{rel}: 'seen' must be a list")
        return True

    for i, entry in enumerate(entries, start=1):
        where = f"{rel}[{i}]"
        if not isinstance(entry, dict):
            err(f"{where}: expected a mapping, got {type(entry).__name__}")
            continue
        for field in ("company", "title", "url", "date", "verdict"):
            if not entry.get(field):
                err(f"{where}: {field} is required")
        check_day(entry.get("date"), "date", where)
    return True


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

    highlight_ids = {h.get("id") for pos in positions_by_id.values()
                     for h in pos.get("highlights", [])}
    message_files = sorted(COMPANIES.glob("*/messages.yaml"))
    for msg_path in message_files:
        check_messages(msg_path, highlight_ids)

    interview_files = sorted(INTERVIEWS.glob("*.md")) if INTERVIEWS.is_dir() else []
    for iv_path in interview_files:
        check_interview(iv_path)

    opp_files = sorted(OPPORTUNITIES.glob("*.md")) if OPPORTUNITIES.is_dir() else []
    for opp_path in opp_files:
        check_opportunity(opp_path)

    agent_files = sorted(AGENTS.glob("*.md")) if AGENTS.is_dir() else []
    for agent_path in agent_files:
        check_agent(agent_path)

    seen_checked = check_seen(OPPORTUNITIES / "seen.yaml")

    if errors:
        for e in errors:
            print(f"  ! {e}", file=sys.stderr)
        sys.exit(f"validate_data: {len(errors)} problem(s) found.")
    print(f"validate_data: OK (career/education/certifications/skills"
          f" + {len(selections)} selection file(s)"
          f" + {len(message_files)} company message file(s)"
          f" + {len(interview_files)} interview record(s)"
          f" + {len(opp_files)} opportunity + {len(agent_files)} agent record(s)"
          f"{' + seen.yaml' if seen_checked else ''})")


if __name__ == "__main__":
    main()
