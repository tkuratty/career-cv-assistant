#!/usr/bin/env python3
"""Company message ⇄ evidence fit report (誇張しないための整合レポート).

Reads a company's own messaging recorded in `companies/<slug>/messages.yaml`
(mission / vision / values / OKR / 行動指針 / 経営メッセージ …) together with the
real career facts in `data/career.<lang>.yaml`, and prints — per message —

- what the company actually says (quote + source),
- which of **your own** highlights back it up (evidence),
- and, derived from `strength`, **how far you may go in writing/speaking about it**:

    strong  (裏付け 2 件以上) … 実績として断定してよい
    partial (裏付け 1 件)     … 限定詞つき（規模・範囲・役割を明示）でのみ
    none    (裏付けなし)      … 応募書類・面接で主張しない。面接で確認する

It also suggests highlights whose `tags` intersect a message's `signals` but are
not listed as evidence yet (記入漏れ検出), and collects the interview probes for
messages you cannot back up — so an unsupported value becomes a *question*
instead of an exaggerated claim.

The schema constants below are shared with `scripts/validate_data.py`, which
machine-checks messages.yaml (evidence ids exist, strength matches the evidence
count, quotes carry a source).

Usage:
    python scripts/company_message_fit.py --company example
    python scripts/company_message_fit.py --company example --lang en
    python scripts/company_message_fit.py --all --format md
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
COMPANIES = ROOT / "companies"

# Windows consoles often use a legacy codepage that cannot print Japanese.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

# --- Schema (shared with validate_data.py) ---------------------------------

MESSAGE_TYPES = {
    "mission", "vision", "value", "principle", "okr", "culture",
    "leader_message", "hiring_message",
}
SOURCE_KINDS = {"primary", "secondary"}
STRENGTHS = ("strong", "partial", "none")
# 誇張防止の核: strength は「裏付けの数」で上限が決まる。
MIN_EVIDENCE = {"strong": 2, "partial": 1, "none": 0}

STRENGTH_LABEL = {
    "strong": "断定して書ける（裏付け 2 件以上）",
    "partial": "限定詞つきでのみ（裏付け 1 件）",
    "none": "応募書類で主張しない（裏付けなし）",
}
STRENGTH_RULE = {
    "strong": "実績として断定してよい。ただし数値・役割は data/ の記述の範囲を出ない。",
    "partial": "「小規模ながら」「〜の範囲で」など規模・範囲・役割を限定する語を必ず添える。"
               "主担当でないものを主導したと書かない。",
    "none": "応募書類・面接の自己 PR で主張しない。企業の語彙に寄せた言い換えもしない。"
            "代わりに面接での確認事項（逆質問）に回す。",
}
STRENGTH_MARK = {"strong": "[OK]", "partial": "[限定]", "none": "[使わない]"}


def load(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def messages_path(slug: str) -> Path:
    return COMPANIES / slug / "messages.yaml"


def company_slugs() -> list[str]:
    return sorted(p.parent.name for p in COMPANIES.glob("*/messages.yaml"))


def career_highlights(lang: str) -> dict[str, dict]:
    """highlight id -> {position, company, text, tags} from career.<lang>.yaml."""
    out: dict[str, dict] = {}
    for pos in load(DATA / f"career.{lang}.yaml").get("positions", []):
        for hl in pos.get("highlights") or []:
            hid = hl.get("id")
            if hid:
                out[hid] = {
                    "position": pos.get("id"),
                    "company": pos.get("company"),
                    "text": hl.get("text", ""),
                    "tags": hl.get("tags") or [],
                }
    return out


# --- Report model ----------------------------------------------------------


def analyze(doc: dict, highlights: dict[str, dict]) -> list[dict]:
    """Annotate every message with its evidence, suggestions and phrasing limit."""
    sources = {s.get("id"): s for s in doc.get("sources") or []}
    rows = []
    for msg in doc.get("messages") or []:
        evidence_ids = msg.get("evidence") or []
        signals = set(msg.get("signals") or [])
        suggestions = [
            hid for hid, hl in highlights.items()
            if hid not in evidence_ids and signals & set(hl["tags"])
        ]
        strength = msg.get("strength", "none")
        rows.append({
            "id": msg.get("id", "?"),
            "type": msg.get("type", "?"),
            "label": msg.get("label", ""),
            "quote": msg.get("quote", ""),
            "source": sources.get(msg.get("source")),
            "interpretation": msg.get("interpretation", ""),
            "note": msg.get("note", ""),
            "interview_probe": msg.get("interview_probe", ""),
            "strength": strength if strength in STRENGTHS else "none",
            "evidence": [(hid, highlights.get(hid)) for hid in evidence_ids],
            "suggestions": [(hid, highlights[hid]) for hid in suggestions],
        })
    return rows


def source_line(src: dict | None) -> str:
    if not src:
        return "（出典未記入）"
    kind = "一次" if src.get("kind") == "primary" else "二次"
    bits = [str(src.get("title", src.get("id", "")))]
    if src.get("url"):
        bits.append(str(src["url"]))
    bits.append(f"{kind}情報")
    if src.get("accessed"):
        bits.append(f"取得 {src['accessed']}")
    return " / ".join(bits)


def counts(rows: list[dict]) -> str:
    per = {s: sum(1 for r in rows if r["strength"] == s) for s in STRENGTHS}
    return " / ".join(f"{s} {per[s]}" for s in STRENGTHS)


# --- Renderers -------------------------------------------------------------


def render(doc: dict, rows: list[dict], slug: str, lang: str, md: bool) -> str:
    h1, h2, h3 = ("# ", "## ", "### ") if md else ("", "", "")
    bullet = "- " if md else "  - "
    sub = "  - " if md else "      "
    out: list[str] = []
    name = doc.get("company", slug)
    out.append(f"{h1}企業メッセージ整合レポート — {name}（{slug}）")
    out.append(f"更新: {doc.get('updated', '-')} / 言語: {lang} / "
               f"メッセージ {len(rows)} 件（{counts(rows)}）")
    out.append("")

    for strength in STRENGTHS:
        group = [r for r in rows if r["strength"] == strength]
        if not group:
            continue
        out.append(f"{h2}{STRENGTH_MARK[strength]} {STRENGTH_LABEL[strength]}")
        out.append(f"{bullet}書ける範囲: {STRENGTH_RULE[strength]}")
        out.append("")
        for r in group:
            out.append(f"{h3}[{r['id']}] {r['type']} — {r['label']}")
            if r["quote"]:
                out.append(f"{bullet}引用: 「{r['quote']}」")
            out.append(f"{bullet}出典: {source_line(r['source'])}")
            if r["interpretation"]:
                out.append(f"{bullet}読み: {r['interpretation']}")
            if r["evidence"]:
                out.append(f"{bullet}裏付け（data/career.{lang}.yaml）:")
                for hid, hl in r["evidence"]:
                    if hl is None:
                        out.append(f"{sub}{hid}: （career データに存在しません）")
                    else:
                        out.append(f"{sub}{hid}（{hl['position']}）: {hl['text']}")
            else:
                out.append(f"{bullet}裏付け: なし")
            if r["suggestions"]:
                cand = ", ".join(
                    f"{hid}[{', '.join(hl['tags'])}]" for hid, hl in r["suggestions"])
                out.append(f"{bullet}裏付け候補（signals と tags が一致・evidence 未記載）: {cand}")
            if r["interview_probe"]:
                out.append(f"{bullet}面接で確認: {r['interview_probe']}")
            elif strength == "none":
                out.append(f"{bullet}面接で確認: （未記入 — interview_probe を書いてください）")
            if r["note"]:
                out.append(f"{bullet}メモ: {r['note']}")
            out.append("")

    probes = [r for r in rows if r["strength"] in ("none", "partial") and r["interview_probe"]]
    out.append(f"{h2}面接設計メモ（裏付けの薄い項目は「盛る」のではなく聞く）")
    if probes:
        for r in probes:
            out.append(f"{bullet}[{r['strength']}] {r['label']}: {r['interview_probe']}")
    else:
        out.append(f"{bullet}（interview_probe が未記入です）")
    out.append("")

    out.append(f"{h2}応募書類での使い方")
    out.append(f"{bullet}summary_override / 志望動機で使ってよい語彙は strength が "
               "strong・partial の項目のみ。")
    out.append(f"{bullet}partial は必ず限定詞つき。none の項目に寄せた表現は書かない"
               "（企業の語彙に合わせた言い換えも不可）。")
    out.append(f"{bullet}裏付けは data/career.*.yaml の記述が上限。"
               "評価語（主導・全社・大幅）を足さない。")
    return "\n".join(out).rstrip() + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(
        description="企業メッセージと本人の実績の整合レポート（誇張防止つき）")
    ap.add_argument("--company", help="companies/<slug>/messages.yaml の slug")
    ap.add_argument("--all", action="store_true", help="messages.yaml を持つ全社を出力")
    ap.add_argument("--lang", default="ja", choices=["ja", "en"],
                    help="裏付け実績を読む career ファイルの言語（既定: ja）")
    ap.add_argument("--format", default="text", choices=["text", "md"],
                    help="出力形式（既定: text）")
    args = ap.parse_args()

    if not args.company and not args.all:
        ap.error("--company <slug> か --all を指定してください")

    slugs = company_slugs() if args.all else [args.company]
    if not slugs:
        sys.exit("company_message_fit: messages.yaml を持つ企業がありません。"
                 "companies/example/messages.yaml を参考に作成してください。")

    highlights = career_highlights(args.lang)
    chunks = []
    for slug in slugs:
        path = messages_path(slug)
        if not path.exists():
            sys.exit(f"company_message_fit: {path.relative_to(ROOT).as_posix()} がありません。"
                     "vet-opportunity / align-company-message で作成してください。")
        doc = load(path)
        chunks.append(render(doc, analyze(doc, highlights), slug,
                             args.lang, args.format == "md"))
    print(("\n" + "-" * 60 + "\n\n").join(chunks))


if __name__ == "__main__":
    main()
