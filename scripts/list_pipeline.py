#!/usr/bin/env python3
"""One-command overview of the job-search pipeline for dedupe and status checks.

Aggregates the front-matter of opportunities/*.md and agents/*.md, plus the
optional opportunities/seen.yaml (roles already surfaced/passed on by
find-opportunities), so skills don't have to re-scan every file:

- Opportunities: slug / company / title / status / agent_company / updated
- Agents: slug / agent_company / status / introduced_companies
- Companies: slug / name / recorded company messages by strength (strong /
  partial / none) — "none" counts messages you cannot back up with your own
  highlights, i.e. the ones that must stay out of the application documents
- Interviews: slug / opportunity / round / round_type / date / status
- Seen: company / title / verdict / date

find-opportunities and vet-agent read this output first to avoid re-surfacing
known roles and to catch 重複応募 risk (companies already entrusted to another
agent).

Usage:
    python scripts/list_pipeline.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent

# Windows consoles often use a legacy codepage that cannot print Japanese.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")


def front_matter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    try:
        return yaml.safe_load(text[3:end]) or {}
    except yaml.YAMLError as exc:
        print(f"  ! {path.relative_to(ROOT).as_posix()}: bad front-matter ({exc})",
              file=sys.stderr)
        return {}


def table(rows: list[list[str]], headers: list[str]) -> str:
    rows = [headers] + rows
    widths = [max(len(str(r[i])) for r in rows) for i in range(len(headers))]
    lines = []
    for n, row in enumerate(rows):
        lines.append("  ".join(str(c).ljust(w) for c, w in zip(row, widths)).rstrip())
        if n == 0:
            lines.append("  ".join("-" * w for w in widths))
    return "\n".join(lines)


def show(value) -> str:
    if value is None or value == "":
        return "-"
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    return str(value)


def main() -> None:
    opp_rows = []
    for path in sorted((ROOT / "opportunities").glob("*.md")):
        fm = front_matter(path)
        opp_rows.append([show(fm.get(k)) for k in
                         ("slug", "company", "title", "status", "agent_company", "updated")])
    print("## Opportunities")
    print(table(opp_rows, ["slug", "company", "title", "status", "agent_company",
                           "updated"]) if opp_rows else "(none)")

    agent_rows = []
    for path in sorted((ROOT / "agents").glob("*.md")):
        fm = front_matter(path)
        agent_rows.append([show(fm.get(k)) for k in
                           ("slug", "agent_company", "status", "introduced_companies")])
    print("\n## Agents")
    print(table(agent_rows, ["slug", "agent_company", "status",
                             "introduced_companies"]) if agent_rows else "(none)")

    company_rows = []
    for path in sorted((ROOT / "companies").glob("*/")):
        research = path / "research.md"
        messages = path / "messages.yaml"
        if not research.exists() and not messages.exists():
            continue
        fm = front_matter(research) if research.exists() else {}
        name = fm.get("name", "-")
        if messages.exists():
            doc = yaml.safe_load(messages.read_text(encoding="utf-8")) or {}
            msgs = doc.get("messages") or []
            per = {s: sum(1 for m in msgs if m.get("strength") == s)
                   for s in ("strong", "partial", "none")}
            company_rows.append([path.name, show(name), str(len(msgs)),
                                 str(per["strong"]), str(per["partial"]),
                                 str(per["none"]), show(doc.get("updated"))])
        else:
            company_rows.append([path.name, show(name), "-", "-", "-", "-", "-"])
    print("\n## Companies（企業メッセージの収集状況）")
    print(table(company_rows, ["slug", "name", "msgs", "strong", "partial",
                               "none", "updated"]) if company_rows else "(none)")

    interview_rows = []
    for path in sorted((ROOT / "interviews").glob("*.md")):
        fm = front_matter(path)
        interview_rows.append([show(fm.get(k)) for k in
                               ("slug", "opportunity", "round", "round_type",
                                "date", "status")])
    print("\n## Interviews")
    print(table(interview_rows, ["slug", "opportunity", "round", "round_type",
                                 "date", "status"]) if interview_rows else "(none)")

    seen_path = ROOT / "opportunities" / "seen.yaml"
    print("\n## Seen (find-opportunities で提示済み・見送り)")
    if seen_path.exists():
        seen = (yaml.safe_load(seen_path.read_text(encoding="utf-8")) or {}).get("seen", [])
        rows = [[show(s.get(k)) for k in ("company", "title", "verdict", "date")]
                for s in seen]
        print(table(rows, ["company", "title", "verdict", "date"]) if rows else "(empty)")
    else:
        print("(no opportunities/seen.yaml yet)")


if __name__ == "__main__":
    main()
