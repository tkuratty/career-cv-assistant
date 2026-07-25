---
name: prep-interview
description: Prepare for a specific job interview round — assemble a pre-interview brief from the company research, company messages, the submitted CV and the opportunity record; work out what this round is for and who the interviewers are (public professional info only); draft answer skeletons and 逆質問; and write interviews/<slug>-r<N>.md. Use when an interview is scheduled or the user asks for 面接対策 / 面接準備 / 想定質問 / 逆質問 / 面接官について調べたい, and afterwards to record the 振り返り. For vetting whether to apply at all use vet-opportunity; for an agent's キャリア面談 use vet-agent.
---

# prep-interview

Turn a scheduled interview into a prepared one: **who is on the other side, what this
round is for, what you may claim, and what you should ask.**

Everything here reuses records the repo already holds — company research, company
messages with their evidence ceiling, the CV you actually submitted, the opportunity's
open questions. Nothing new gets invented.

> Agent-neutral: this procedure works whether you are Claude or Codex. "Skill" just
> means this document. Use whatever web-search / browsing tools you have.

## Inputs to gather
- **Which opportunity** (`opportunities/<slug>.md`) and **which round** (1, 2, …).
- **Round type**: `casual / first / technical / manager / executive / hr / reference / offer`.
  Ask if unclear — the whole preparation hinges on it.
- **Date / format / duration**, and the **interview invitation** if the user has one
  (it usually names the interviewers).
- Whether this is **preparation** (before) or **振り返り** (after).

## Read first
1. `data/positioning.md` — the decision axis. An interview is mutual evaluation; the
   user is also deciding.
2. `opportunities/<slug>.md` — 懸念・リスク and the 確認チェックリスト still unanswered.
3. `companies/<slug>/research.md` and `companies/<slug>/messages.yaml`.
4. `cv/output/<slug>/selection.yaml` — **what was actually submitted** is what gets
   probed. If no tailored CV exists, say so and offer **tailor-cv**.

## Steps
1. **Brief** — run the aggregator and read it before anything else:
   ```
   python scripts/interview_brief.py --opportunity <slug> --round <N>
   ```
   It merges research, messages (with the strength ceiling), the submitted highlights,
   open checklist items and the decision axis. Missing pieces are reported as 未作成 —
   fill those first if they matter (vet-opportunity / align-company-message / tailor-cv).
2. **Round design** — read
   `.claude/skills/prep-interview/references/interview-playbooks.md` and combine
   **企業タイプ**（from research.md: industry, 資本構成, size）× **round_type** into:
   what this round is for *from the company's side*, the likely 評価軸, and the traps.
   The playbook is 一般論 — mark it as such and confirm the real process with the agent
   or the recruiter. **Do not present the playbook's guesses as facts about the company.**
3. **Interviewer research (public professional info only)** — if names are known:
   - **Collect**: role and remit from the company site / 採用ページ / IR, public talks,
     conference slides, technical blog posts, published professional profiles, official
     company posts.
   - **Do not collect**: private life, family, address, photos, personal social-media
     posts, political/religious/health/origin attributes, anything behind a private
     account or membership wall. Do not attempt exhaustive name matching — a same-name
     mix-up is worse than not knowing.
   - **Handle**: record only what shapes the conversation (role in the process, focus
     area), always with the source URL; label inference as 推測; leave 要確認 when you
     cannot identify the person confidently. In the room, referencing public work is
     natural — sounding like you investigated them is not.
   - If the interviewers are unknown, **ask the agent/recruiter** rather than guessing.
4. **Purpose per interviewer** — role × round type → what each person wants to confirm.
   Write it in 「この面接の目的（相手側）」.
5. **語り口 from company messages** — apply the `strength` ceiling from
   `companies/<slug>/messages.yaml`: `strong` = state as fact, `partial` = only with a
   limiting qualifier (「小規模ながら」「〜の範囲で」), `none` = **do not claim it**, turn it
   into a 逆質問. Borrow vocabulary, never upgrade the facts.
6. **想定質問と回答骨子** — the brief's 「5. 想定質問」 already assembles the question set
   from the collected records: deep-dives on every submitted highlight, the JD gaps marked
   「← 橋渡しが必要」, the company messages with `strength: partial`/`none`, questions that
   were **actually asked before** (`asked[]`, weak/missed first), and the round's standard
   questions from
   `.claude/skills/prep-interview/references/question-bank.md` (一般論). Start there,
   drop what does not apply, add company-specific ones, and write **事実 → 行動 → 結果**
   skeletons. Every fact comes from `data/career.*.yaml`; no evaluative inflation
   (主導・全社・大幅). For a gap, the answer is 「やっていません」+ the nearest real bridge —
   never a manufactured one.
7. **逆質問（優先順）** — from `interview_probe`s (unsupported messages), the opportunity's
   懸念, and the unanswered 確認チェックリスト. Neutral phrasing for sensitive items
   (存続リスク・オンコール・前任の離任理由) — see vet-opportunity's 面接での聞き方メモ.
8. **Write** `interviews/<slug>-r<N>.md` using `interviews/example-r1.md` as the format
   reference, link it from `opportunities/<slug>.md` (`[[interviews/<slug>-r<N>]]`), and
   run `python scripts/validate_data.py`.
9. **After the interview (振り返り)** — **fill `asked[]` in the front-matter**: every
   question you were actually asked, with `answered: ok / weak / missed` and a short note.
   This is what closes the loop — `interview_brief.py` re-surfaces `weak`/`missed` as
   再出題 in the next round of this opportunity **and** in other opportunities' rounds of
   the same `round_type`, so the same question does not catch you twice. Then write the
   narrative 振り返り, update `opportunities/<slug>.md` `status` (`面接中` など) and its
   選考ログ, and correct `companies/<slug>/messages.yaml` / `research.md` (要確認 →
   confirmed) with what you learned in the room.
10. **Before the next round** — start from the previous round's `weak`/`missed` questions;
   they are already at the top of the brief's 想定質問.

## Rules
- **No fabrication, in both directions.** Your answers stay inside `data/career.*.yaml`;
  company facts stay inside cited sources; the playbook stays labelled as 一般論.
- **誇張の代わりに質問。** A value or requirement you cannot back up becomes a 逆質問,
  never a claim. Reference checks (`round_type: reference`) are where inflation surfaces.
- **面接官の情報は公開された職務上のものだけ。** Third-party personal data: collect the
  minimum that shapes the conversation, keep the source, never put a real interviewer's
  name in the public template repo (AGENTS.md §6 — personal copies must be private).
- **Mutual evaluation.** Close every preparation with the decision axis from
  `positioning.md` — what would make you decline this seat?
- **質問集は蓄積する。** The question bank is 一般論; `asked[]` is your own history. A round
  without `asked[]` filled in is an unfinished round — the next preparation loses it.
- **Status vocabulary** (AGENTS.md §6): interviews are `予定 / 完了 / 見送り / キャンセル`;
  keep the opportunity's own status in sync.
