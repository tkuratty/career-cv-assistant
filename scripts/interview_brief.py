#!/usr/bin/env python3
"""Assemble a one-page pre-interview brief from records the repo already holds.

Nothing here is new data — it merges, in reading order:

1. この面接      … interviews/<slug>-r<N>.md front-matter (round, 面接官, 目的)
2. 企業の要点    … companies/<slug>/research.md (概要 / 存続リスク / 企業メッセージ …)
3. 語れる範囲    … companies/<slug>/messages.yaml via company_message_fit's strength
                   ceiling — strong は断定可 / partial は限定詞つき / none は逆質問へ
4. 提出済み CV   … cv/output/<slug>/selection.yaml の highlight（深掘りされる前提）
5. 想定質問      … 提出 CV の深掘り ＋ 案件のギャップ（橋渡しが必要な要件）＋ 企業メッセージの
                   partial/none ＋ 過去に実際に聞かれた質問（asked[] の weak/missed 優先）
                   ＋ question-bank.md の round_type 別・共通の定番
6. 懸念・確認    … opportunities/<slug>.md の 懸念・リスク と 確認チェックリスト
7. 逆質問        … messages.yaml の interview_probe ＋ 未確認のチェックリスト
8. 判断軸        … data/positioning.md（面接は相互評価）

Missing pieces are reported as 未作成 instead of failing, so the brief is usable
early in a pipeline.

Usage:
    python scripts/interview_brief.py --opportunity example
    python scripts/interview_brief.py --opportunity example --round 1 --format md
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

from company_message_fit import (
    STRENGTHS,
    STRENGTH_LABEL,
    STRENGTH_MARK,
    STRENGTH_RULE,
    analyze,
    career_highlights,
    load,
)

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
COMPANIES = ROOT / "companies"
OPPORTUNITIES = ROOT / "opportunities"
INTERVIEWS = ROOT / "interviews"
OUTPUT = ROOT / "cv" / "output"
QUESTION_BANK = (ROOT / ".claude" / "skills" / "prep-interview" /
                 "references" / "question-bank.md")

# Windows consoles often use a legacy codepage that cannot print Japanese.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")


ENUM_RE = re.compile(r"^\d+\.\s*")


def split_front_matter(path: Path) -> tuple[dict, str]:
    """Return (front-matter, body) for a Markdown record."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    try:
        fm = yaml.safe_load(text[3:end]) or {}
    except yaml.YAMLError as exc:
        print(f"  ! {path.relative_to(ROOT).as_posix()}: bad front-matter ({exc})",
              file=sys.stderr)
        fm = {}
    return fm, text[end + 4:]


def section(body: str, heading: str) -> list[str]:
    """Lines of a '## <heading>' section (bullets and text, blank lines dropped)."""
    pattern = re.compile(rf"^##\s+{re.escape(heading)}.*$", re.MULTILINE)
    m = pattern.search(body)
    if not m:
        return []
    rest = body[m.end():]
    nxt = re.search(r"^##\s+", rest, re.MULTILINE)
    chunk = rest[:nxt.start()] if nxt else rest
    return [ln.rstrip() for ln in chunk.splitlines() if ln.strip()]


def interview_files(opportunity: str) -> list[tuple[dict, str, Path]]:
    records = []
    for path in sorted(INTERVIEWS.glob("*.md")):
        fm, body = split_front_matter(path)
        if fm.get("opportunity") == opportunity:
            records.append((fm, body, path))
    return records


def past_asked(opportunity: str, round_type: str, current: Path | None) -> list[dict]:
    """Questions actually asked before, reusable for this round.

    Pulled from every other interview record's `asked[]`: earlier rounds of the same
    opportunity, and other opportunities' rounds of the same type. `weak` / `missed`
    answers come first — those are the ones that bite twice.
    """
    rows: list[dict] = []
    for path in sorted(INTERVIEWS.glob("*.md")):
        if current is not None and path == current:
            continue
        fm, _ = split_front_matter(path)
        same_opp = fm.get("opportunity") == opportunity
        same_type = bool(round_type) and fm.get("round_type") == round_type
        if not (same_opp or same_type):
            continue
        scope = (f"同じ案件 r{fm.get('round', '?')}" if same_opp
                 else f"他案件の {round_type}: {fm.get('opportunity')}")
        for item in fm.get("asked") or []:
            if not item.get("q"):
                continue
            rows.append({"q": item["q"], "answered": item.get("answered", "-"),
                         "note": item.get("note", ""), "scope": scope})
    order = {"missed": 0, "weak": 1, "ok": 2}
    return sorted(rows, key=lambda r: order.get(r["answered"], 3))


def bank_lines(round_type: str | None) -> list[str]:
    """Bullets from question-bank.md — a round_type section, or the common one."""
    if not QUESTION_BANK.exists():
        return []
    text = QUESTION_BANK.read_text(encoding="utf-8")
    if round_type:
        m = re.search(rf"^##\s+`{re.escape(round_type)}`.*$", text, re.MULTILINE)
    else:
        m = re.search(r"^##\s+共通の定番.*$", text, re.MULTILINE)
    if not m:
        return []
    rest = text[m.end():]
    nxt = re.search(r"^##\s+", rest, re.MULTILINE)
    chunk = rest[:nxt.start()] if nxt else rest
    return [ln.lstrip("- ").strip() for ln in chunk.splitlines()
            if ln.strip().startswith("- ")]


def pick_round(records: list[tuple[dict, str, Path]], want: int | None):
    if not records:
        return None
    if want is not None:
        for rec in records:
            if str(rec[0].get("round")) == str(want):
                return rec
        return None
    upcoming = [r for r in records if r[0].get("status") == "予定"]
    pool = upcoming or records
    return sorted(pool, key=lambda r: str(r[0].get("date") or "9999"))[0]


def build(opportunity: str, want_round: int | None, lang: str, md: bool) -> str:
    h1, h2 = ("# ", "## ") if md else ("", "== ")
    tail = "" if md else " =="
    b = "- " if md else "  - "
    sub = "  - " if md else "      "
    out: list[str] = []

    opp_path = OPPORTUNITIES / f"{opportunity}.md"
    if not opp_path.exists():
        sys.exit(f"interview_brief: {opp_path.relative_to(ROOT).as_posix()} がありません。"
                 "vet-opportunity で案件を登録してください。")
    opp_fm, opp_body = split_front_matter(opp_path)
    company = opp_fm.get("company", opportunity)

    out.append(f"{h1}面接前ブリーフ — {opp_fm.get('title', opportunity)}")
    out.append(f"案件: {opportunity} / 企業: {company} / 案件ステータス: "
               f"{opp_fm.get('status', '-')} / 更新: {opp_fm.get('updated', '-')}")
    out.append("")

    # 1. この面接
    out.append(f"{h2}1. この面接{tail}")
    rec = pick_round(interview_files(opportunity), want_round)
    if rec is None:
        out.append(f"{b}interviews/ に該当ラウンドの記録がありません（未作成）。"
                   "prep-interview で `interviews/<slug>-r<N>.md` を作成してください。")
    else:
        fm, body, path = rec
        out.append(f"{b}ラウンド {fm.get('round', '?')}（{fm.get('round_type', '?')}）/ "
                   f"{fm.get('date', '日程未定')} / {fm.get('format', '-')} / "
                   f"{fm.get('duration', '-')} / {fm.get('status', '-')}")
        out.append(f"{b}記録: {path.relative_to(ROOT).as_posix()}")
        for person in fm.get("interviewers") or []:
            out.append(f"{b}面接官: {person.get('name', '要確認')}"
                       f"（{person.get('title', '-')}）— "
                       f"{person.get('role_in_process', '役割要確認')}")
            if person.get("focus"):
                out.append(f"{sub}関心: {person['focus']}")
            for src in person.get("sources") or []:
                out.append(f"{sub}出典: {src}")
        for line in section(body, "この面接の目的（相手側）"):
            out.append(f"{b}{line.lstrip('- ')}" if line.startswith("-") else f"{b}{line}")
    out.append("")

    # 2. 企業の要点
    out.append(f"{h2}2. 企業の要点{tail}")
    research = COMPANIES / str(company) / "research.md"
    if not research.exists():
        out.append(f"{b}companies/{company}/research.md が未作成。vet-opportunity で企業調査を。")
    else:
        r_fm, r_body = split_front_matter(research)
        out.append(f"{b}{r_fm.get('name', company)} / {r_fm.get('industry', '-')} / "
                   f"{r_fm.get('size', '-')} / {r_fm.get('website', '-')}")
        for heading in ("概要", "拠点の位置づけ・存続リスク", "AI・技術の活用状況"):
            lines = section(r_body, heading)
            if lines:
                out.append(f"{b}[{heading}]")
                for line in lines:
                    out.append(f"{sub}{line.lstrip('- ')}")
        todo = [ln for ln in r_body.splitlines() if "要確認" in ln]
        if todo:
            out.append(f"{b}要確認が {len(todo)} 箇所残っています（面接で潰す候補）。")
    out.append("")

    # 3. 企業メッセージと語れる範囲
    out.append(f"{h2}3. 企業メッセージと語れる範囲{tail}")
    messages = COMPANIES / str(company) / "messages.yaml"
    probes: list[str] = []
    if not messages.exists():
        out.append(f"{b}companies/{company}/messages.yaml が未作成。"
                   "align-company-message で MVV / OKR / 行動指針を収集してください。")
    else:
        doc = load(messages)
        rows = analyze(doc, career_highlights(lang))
        for strength in STRENGTHS:
            group = [r for r in rows if r["strength"] == strength]
            if not group:
                continue
            out.append(f"{b}{STRENGTH_MARK[strength]} {STRENGTH_LABEL[strength]} — "
                       f"{STRENGTH_RULE[strength]}")
            for r in group:
                ev = ", ".join(hid for hid, _ in r["evidence"]) or "なし"
                out.append(f"{sub}[{r['type']}] {r['label']}（裏付け: {ev}）")
            probes += [r["interview_probe"] for r in group
                       if r["interview_probe"] and strength != "strong"]
    out.append("")

    # 4. 提出済み CV で前に出した実績
    out.append(f"{h2}4. 提出済み CV で前に出した実績（深掘りされる前提）{tail}")
    sel_dir = opp_fm.get("cv") or f"cv/output/{opportunity}/"
    sel_path = ROOT / str(sel_dir).rstrip("/") / "selection.yaml"
    highlights = career_highlights(lang)
    if not sel_path.exists():
        out.append(f"{b}{sel_path.relative_to(ROOT).as_posix()} が未作成。"
                   "tailor-cv で案件向け CV を生成すると、ここに深掘り対象が並びます。")
    else:
        sel = load(sel_path)
        if sel.get("summary_override"):
            out.append(f"{b}要約（提出済み）: {str(sel['summary_override']).strip()}")
        entries = sel.get("positions") or []
        if not entries:
            out.append(f"{b}全ポジションを既定順で提出（selection に positions 指定なし）。")
        for entry in entries:
            out.append(f"{b}[{entry.get('id')}]")
            for hid in entry.get("highlights") or []:
                hl = highlights.get(hid)
                out.append(f"{sub}{hid}: {hl['text'] if hl else '（career データに無し）'}")
    out.append("")

    # 5. 想定質問（自動生成）
    out.append(f"{h2}5. 想定質問（収集情報から自動生成）{tail}")
    round_type = (rec[0].get("round_type") if rec else None) or ""
    submitted = []
    if sel_path.exists():
        for entry in (load(sel_path).get("positions") or []):
            submitted += list(entry.get("highlights") or [])

    if submitted:
        out.append(f"{b}[提出 CV の深掘り] 出した実績は全部聞かれる前提で、事実→行動→結果を用意")
        for hid in submitted:
            hl = highlights.get(hid)
            label = (hl["text"].split("—")[0].strip() if hl else hid)
            out.append(f"{sub}{label}: 状況・自分が下した判断・結果を具体的に（{hid}）")
    else:
        out.append(f"{b}[提出 CV の深掘り] selection.yaml が未作成 — tailor-cv 後にここが埋まります")

    bridges = [ln for ln in section(opp_body, "求める経験") if "橋渡し" in ln]
    if bridges:
        out.append(f"{b}[ギャップ] 案件側が「橋渡しが必要」とした要件 — 盛らずに"
                   "「やっていません + 近いのはこれ」で答える")
        for line in bridges:
            out.append(f"{sub}{line.lstrip('- ')}")

    if messages.exists():
        rows = analyze(load(messages), highlights)
        weak = [r for r in rows if r["strength"] in ("partial", "none")]
        if weak:
            out.append(f"{b}[企業メッセージ由来] 企業が重視するが自分の裏付けが薄い論点")
            for r in weak:
                if r["strength"] == "partial":
                    out.append(f"{sub}「{r['label']}」— どの範囲で経験がありますか"
                               "（範囲を先に限定してから答える）")
                else:
                    out.append(f"{sub}「{r['label']}」— 経験はありますか"
                               "（**無いと答える**。取り繕わず逆質問に転じる）")

    reuse = past_asked(opportunity, round_type, rec[2] if rec else None)
    if reuse:
        out.append(f"{b}[再出題] 過去に実際に聞かれた質問（weak / missed を優先）")
        for item in reuse:
            note = f" — {item['note']}" if item.get("note") else ""
            out.append(f"{sub}[{item['answered']}] {item['q']}"
                       f"（{item['scope']}）{note}")

    bank = bank_lines(round_type)
    if bank:
        out.append(f"{b}[{round_type} の定番] question-bank.md より（一般論・取りこぼし防止）")
        for line in bank:
            out.append(f"{sub}{line}")
    common = bank_lines(None)
    if common:
        out.append(f"{b}[共通の定番] 転職理由・志望動機・強み弱み・条件（question-bank.md）")
        for line in common:
            out.append(f"{sub}{line}")
    out.append("")

    # 6. 懸念と未確認のチェックリスト
    out.append(f"{h2}6. 懸念と未確認のチェックリスト{tail}")
    concerns = section(opp_body, "懸念・リスク")
    for line in concerns:
        out.append(f"{b}{line.lstrip('- ')}")
    unchecked = [ln for ln in section(opp_body, "確認チェックリスト（案件ごとに具体化）")
                 + section(opp_body, "確認チェックリスト") if "- [ ]" in ln]
    if unchecked:
        out.append(f"{b}未確認:")
        for line in dict.fromkeys(unchecked):
            out.append(f"{sub}{line.replace('- [ ]', '').strip()}")
    if not concerns and not unchecked:
        out.append(f"{b}（案件ファイルに懸念・チェックリストの記載がありません）")
    out.append("")

    # 7. 逆質問（優先順）
    out.append(f"{h2}7. 逆質問（優先順）{tail}")
    asks = list(dict.fromkeys(probes))
    for line in dict.fromkeys(unchecked):
        asks.append(f"（未確認）{line.replace('- [ ]', '').strip()}")
    if rec is not None:
        asks += [ENUM_RE.sub("", ln.lstrip("- ").strip())
                 for ln in section(rec[1], "逆質問（優先順）")
                 if ENUM_RE.match(ln.strip()) or ln.strip().startswith("-")]
    if asks:
        for n, ask in enumerate(dict.fromkeys(asks), 1):
            out.append(f"{'' if md else '  '}{n}. {ask}")
    else:
        out.append(f"{b}（messages.yaml の interview_probe と案件チェックリストから自動収集します）")
    out.append("")

    # 8. 判断軸
    out.append(f"{h2}8. 判断軸リマインド（面接は相互評価）{tail}")
    positioning = DATA / "positioning.md"
    if positioning.exists():
        text = positioning.read_text(encoding="utf-8")
        m = re.search(r"^##\s*判断軸.*$", text, re.MULTILINE)
        if m:
            rest = text[m.end():]
            nxt = re.search(r"^##\s+", rest, re.MULTILINE)
            for line in (rest[:nxt.start()] if nxt else rest).splitlines():
                if line.strip():
                    out.append(f"{b}{line.strip().lstrip('- ')}")
        else:
            out.append(f"{b}positioning.md に「判断軸」セクションがありません。")
    out.append(f"{b}この席を**見送る**としたら理由は何か、面接中に確かめる。")
    return "\n".join(out).rstrip() + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description="面接前ブリーフを既存の記録から組み立てる")
    ap.add_argument("--opportunity", required=True, help="opportunities/<slug>.md の slug")
    ap.add_argument("--round", type=int, help="ラウンド番号（省略時は直近の『予定』）")
    ap.add_argument("--lang", default="ja", choices=["ja", "en"],
                    help="実績を読む career ファイルの言語（既定: ja）")
    ap.add_argument("--format", default="text", choices=["text", "md"],
                    help="出力形式（既定: text）")
    args = ap.parse_args()
    print(build(args.opportunity, args.round, args.lang, args.format == "md"))


if __name__ == "__main__":
    main()
