---
name: align-company-message
description: Collect a company's own messaging (MVV・ミッション/ビジョン/バリュー, OKR・全社目標, 行動指針, カルチャー, 経営者・採用メッセージ) into companies/<slug>/messages.yaml with sources, map each message to the user's real career highlights as evidence, and turn that into 誇張しない応募書類の言い回し and 面接での語り口・逆質問. Use when the user asks to research or record a company's MVV/OKR/バリュー/行動指針/カルチャー, or asks how to align a CV, 職務経歴書, 志望動機 or interview answers with what a company says it values. For overall role/company vetting use vet-opportunity; for building the CV itself use tailor-cv.
---

# align-company-message

Record what a company **says about itself**, then bound how far the user may go in
echoing it — using the user's own facts as the ceiling.

The failure mode this exists to prevent: reading a company's value ("オーナーシップ")
and quietly upgrading the user's history to match it ("全社の IT を主導し…"). Here the
rule is mechanical: **裏付け（evidence）の数が主張の上限**.

> Agent-neutral: this procedure works whether you are Claude or Codex. "Skill" just
> means this document. Use whatever web-search / browsing tools you have.

## Inputs to gather
- **Company name + slug** (reuse the `companies/<slug>/` slug if research exists).
- Optionally the JD / `opportunities/<slug>.md` — the JD's language is itself a message.
- Whether the target is 応募書類 (documents), 面接 (interview), or both.

## Read first
1. `data/positioning.md` — the user's axis. A company message that clashes with the
   axis is a **risk signal**, not something to accommodate.
2. `data/career.{ja,en}.yaml` — the only source of evidence. Highlight `tags` are the
   matching surface for a message's `signals`.
3. `companies/<slug>/research.md` and `companies/<slug>/messages.yaml` if they exist —
   **update, never duplicate**.

## Steps
1. **Collect (web)** — find the company's own words: ミッション/ビジョン/バリュー,
   行動指針・クレド, 全社 OKR や中期目標, カルチャーデック, 代表・CTO のメッセージ,
   採用ページの「求める人物像」. Prefer **primary sources** (the company's own site,
   IR, 採用ページ); mark media/口コミ as `kind: secondary`.
2. **Quote exactly** — `quote` holds the company's original wording, unmodified and
   short. Any paraphrase goes in `interpretation`. **Never invent a quote**; if you
   only have a summary, leave `quote` empty and say so in `interpretation`.
3. **Interpret** — for each message write what the company actually expects in practice
   (e.g. 「セキュリティは専任チームではなく情シスが実務で回す想定」), and pick
   language-neutral `signals` that can meet `highlights[].tags`.
4. **Map evidence** — attach the user's highlight ids that genuinely demonstrate the
   message. Only ids that exist in `data/career.*.yaml`. Do not stretch: a highlight
   that "sort of relates" is not evidence.
5. **Set strength honestly** — `strong` (evidence 2 件以上) / `partial` (1 件) /
   `none` (0 件). If it feels wrong to call something strong, it isn't strong.
6. **Write** `companies/<slug>/messages.yaml` using `companies/example/messages.yaml`
   as the format reference, and add/refresh the 企業メッセージ section in
   `companies/<slug>/research.md` (summary + link to the yaml).
7. **Validate & report**:
   ```
   python scripts/validate_data.py
   python scripts/company_message_fit.py --company <slug> --lang ja
   ```
   The validator rejects evidence ids that don't exist and a `strength` the evidence
   count doesn't support; the report shows the phrasing ceiling per message plus
   裏付け候補 (highlights whose tags match `signals` but aren't listed yet) — review
   those and add the genuine ones.
8. **Deliver two things**:
   - **応募書類向け**: 2〜4 の言い回し候補（`summary_override` や志望動機に使える）。
     strong は実績として断定、partial は限定詞つき、`none` の項目には触れない。
     企業の語彙は「借りる」程度に留め、実績の記述自体は `data/` の内容を超えない。
   - **面接向け**: strong/partial のメッセージごとに、事実 → 行動 → 結果 の骨子
     （盛らずに語る順番）と、`none`/`partial` から作った**逆質問**。
     裏付けの無い価値観は「できます」ではなく「どう運用されていますか」に変換する。
9. **Flag clashes** — if a message conflicts with `positioning.md` (例: 「全員が営業も
   する」 vs 手を動かす席を望む), say so plainly. Fit is a two-way judgment.

## strength → 表現の上限（この対応表を必ず守る）

| strength | 裏付け | 応募書類 | 面接 |
| --- | --- | --- | --- |
| `strong` | 2 件以上 | 実績として断定してよい（数値・役割は `data/` の記述の範囲内） | 主エピソードとして語る |
| `partial` | 1 件 | 「小規模ながら」「〜の範囲で」など規模・範囲・役割の限定詞を必ず添える | 経験の範囲を先に明示してから話す |
| `none` | なし | **書かない**（企業の語彙に寄せた言い換えも不可） | 主張しない。逆質問に回す |

## Rules
- **No fabrication, both directions.** 企業の言葉を作らない（出典必須）／自分の実績を
  作らない（evidence は `data/` の highlight id のみ）。
- **誇張の代わりに質問**。裏付けの無い期待は `interview_probe` に落とす。
- **さりげなく、が上限**。企業のバリューを丸暗記して復唱するのは逆効果。使うのは語彙と
  優先順位の合わせ方までで、実績の中身は変えない。
- 二次情報（記事・口コミ）は `kind: secondary` と明記し、面接で裏を取る前提で扱う。
- 個人情報は書かない（`AGENTS.md` §6）。ここに入るのは企業側の公開情報だけ。
