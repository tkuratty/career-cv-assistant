---
name: vet-opportunity
description: Vet a job opportunity (agent 案件 / JD) as a sounding board — research the company, confirm the posting is still live and how to apply, assess fit against the user's career data and positioning, surface risks and the positioning gap, and produce a vetting checklist and interview framing. Use when the user pastes a job posting, forwards an agent's 案件, or asks to analyze/研究/壁打ち a role or company. Writes companies/<slug>/research.md and opportunities/<slug>.md in this repo's format. For generating a tailored CV, use tailor-cv instead.
---

# vet-opportunity

Reproduce a rigorous "壁打ち" (sounding-board) analysis of a job opportunity and
record it in the repo. The goal is a clear-eyed read of fit **and** risk, anchored
to the user's own positioning — not a sales pitch for the role.

> Agent-neutral: this procedure works whether you are Claude or Codex. "Skill" just
> means this document. Use whatever web-search / browsing tools you have.

## Inputs to gather
- **The 案件 / JD**: pasted text, a URL, or an `opportunities/<slug>.md` file.
- **Company name** and **agent / agent company** if known (ask if the JD hides them).
- A **slug** for the company and opportunity (e.g. `acme`, `acme-corporate-it`).

## Read first (the analysis axis)
1. `data/positioning.md` — the user's target, differentiators, must-checks, and
   dealbreakers. **This is the axis for every judgment below.**
2. `data/career.en.yaml` / `data/career.ja.yaml` and `data/profile.*.yaml` — to
   assess requirement coverage and gaps against real history.
3. `data/retirement-plan.md` — **if it exists**, its 足切り conditions are *necessary*
   conditions. Judge in two stages: the financial 足切り decides whether the role is a
   candidate at all, then `positioning.md` ranks it. A role failing a 足切り is 見送り
   however attractive the work is.
4. If a `companies/<slug>/research.md` already exists, update it rather than dup.

## Steps
1. **Company research** — **if a job-search MCP is connected and carries this company,
   start there.** A company endpoint typically returns headcount history, funding rounds,
   directors and the **full list of open roles** — i.e. the 規模・資金・体制 facts this
   step otherwise has to guess at, and the open-role list is a signal in itself: what
   else they are hiring for shows where the org's weight is going. Prefer the server's
   clean JD over re-reading rendered HTML, and follow its citation rules. ⚠️ Never call a
   write endpoint from this skill — vetting is read-only. Then use WebSearch/WebFetch for
   what the server does not carry: financials/credit rating,
   the local office's role and strategic weight, precedents of closures / layoffs /
   consolidation, and technology/AI posture. Prefer primary sources; note when only
   secondary sources exist. **Never invent facts or figures** — mark unknowns as
   "要確認". When two sources disagree, **record both and mark 要確認** rather than
   silently picking one.
2. **掲載鮮度と応募導線の確認** — before analysing fit, settle whether the posting is
   **still live** and **where an application actually goes**. Working from the board
   listing alone risks applying to a closed seat, or spending the analysis on a posting
   that cannot be applied to.
   - **Get the posted date and last-updated date**, and state how long it has been open.
     Even when the posting doesn't display one, most ATSs carry it in machine-readable
     form — the retrieval recipes (JSON-LD `datePosted`, BambooHR, Workday, and why the
     Wayback Machine cannot answer this) are in
     `.claude/skills/find-opportunities/SKILL.md`「掲載日の取り方」. If it cannot be had,
     write 「不明」 and do not guess. ⚠️ A "last updated" date is the day the posting's
     text was edited — unrelated to whether the search is still running.
   - **Confirm it is alive at the primary window**: is the same role still listed on the
     company's own careers page? If yes, it isn't a ghost posting.
   - **Settle the application route**: can it be applied to from the board, or only via
     the company's careers page / a specific ATS? Put the confirmed window in `jd_url`
     and demote the board listing to a comment beside it.
   - **Read the listing page's character**: one posting among a company's permanently-
     listed full set means something different from one in a short, curated list.
   - **Age alone is not a deduction.** If you use it, apply the same yardstick to every
     opportunity under consideration. Convert what's left — how long has this seat been
     open, is the 募集背景 (増員 / 欠員 / 再編) still valid — into 確認チェックリスト①.
     Posting age becomes usable evidence only once it is turned into a question.
3. **企業メッセージの収集** — while researching, capture the company's **own words**:
   ミッション/ビジョン/バリュー, 行動指針・クレド, 全社 OKR・中期目標, カルチャー,
   代表/CTO メッセージ, 採用ページの「求める人物像」. Record them with sources in
   `companies/<slug>/messages.yaml` (format: `companies/example/messages.yaml`),
   map each to the user's real highlight ids as `evidence`, and set `strength`
   from the evidence count (`strong` ≥2 / `partial` 1 / `none` 0). Quote verbatim
   or leave `quote` empty — never paraphrase into a fake quote. Details and the
   phrasing ceiling: `.claude/skills/align-company-message/SKILL.md`.
4. **Fit analysis** — map JD requirements to the user's career data: what is clearly
   covered, and the **explicit gaps** (e.g. no financial-industry experience). Propose
   how to **bridge** each gap using existing facts (regulated-industry controlled ops,
   ISMS/ISO27001, change management), without fabricating.
5. **Positioning gap** — compare the role's level/autonomy to `positioning.md`'s target
   (e.g. Head of IT vs an Analyst seat under a Manager). State plainly if it is a
   sideways/down move and hypothesize *why the agent proposed it*.
6. **Risk analysis** — structural risks: local-function consolidation/offshore, on-call
   for market/regulatory systems, shadow-IT/governance friction for the user's
   automation style, AI-tooling constraints (approved agentic path vs blocked public AI),
   retention/tenure, employing-entity/severance ambiguity.
7. **Vetting checklist** — instantiate the template below with company-specific items.
8. **Interview framing** — neutral phrasings for sensitive risks; how to bridge gaps;
   and the reminder to **sell the judgment layer, not the AI tool** (avoid a
   "can't work without Claude" framing — reframe as "governed value creation").
   Run `python scripts/company_message_fit.py --company <slug>` and fold its output in:
   messages with `strength: strong/partial` give the vocabulary to echo (partial only
   with a limiting qualifier), and messages with `strength: none` become **逆質問**
   instead of claims.
9. **Optional (if requested)** — draft agent questions (leveling check + ask for a
   higher-level seat) and interview-answer starters.
10. **Write files** — create/update:
   - `companies/<slug>/research.md` — front-matter (slug, name, industry, size,
     website, updated, sources) + 概要 / 拠点の位置づけ・存続リスク / AI 活用状況 /
     企業メッセージ（要約 + `messages.yaml` へのリンク）/ 本人経歴との相性 /
     ポジショニングのギャップ / 関連案件 `[[...]]`.
   - `companies/<slug>/messages.yaml` — the structured company messages from step 3.
   - `opportunities/<slug>.md` — front-matter (slug, company, title, agent,
     agent_company, status, outcome, closed_reason, closed_date, employment, location,
     salary, report_line, team_size, jd_url, applied_date, cv, updated)
     + ポジション概要 / 求める経験 / 魅力 /
     懸念・リスク / 確認チェックリスト / 面接での聞き方メモ / 判断軸 / 選考ログ.
   Use `companies/example/research.md` and `opportunities/example.md` as the
   reference format.
11. **Report** — summarize fit, the top risk, the positioning read, and the decision
   axis; then point to the files written. If the user is moving forward, hand off:
   **tailor-cv** for the application, **prep-interview** once a round is scheduled.

## 確認チェックリスト テンプレート（案件ごとに具体化）
1. **案件・エージェントの素性**: 直接取引か二次請けか / 紹介実績 / 「後任」の裏取り / 年収内訳 /
   **この枠はいつから空いているか・募集背景（増員 / 欠員 / 再編）は今も有効か**（step 2 の掲載鮮度から）。
2. **雇用主体**: 契約先法人格 / 退職金の有無 / 社保・DC・福利厚生。
   **健康保険の種類は個別項目として確認する**（組合健保か協会けんぽか）。「社会保険完備」の記載で
   済ませない — 料率・付加給付・健診/保養補助で手取りが変わる。`data/retirement-plan.md` を
   使っているなら、そこに挙げた財務条件も 1 項目ずつ落とす。
3. **拠点・機能の存続リスク**: 集約・オフショア計画 / アウトソース置換 / redundancy 条件。
4. **ポジションの実態**: JD 記載の裏取り / オンコール頻度 / 少人数のカバー体制。
5. **成長ストーリー**: 昇格の器 / 歴代在籍年数・離任理由 / 評価の裁量。
6. **相場観**: 提示年収の根拠（自走責任 / 採りにくさ / みなし残業込みか）。
7. **AI 環境（agentic × 社内文脈）**: 公認グラウンディング経路 / データ分類ごとの投入可否 /
   自前エージェントの可否 / AU/APAC 格差 / 承認リードタイム / 運用職が対象か。

## Rules
- **Anchor to `positioning.md`.** Every fit/risk/decision statement should tie back to
  the user's target, differentiators, must-checks, or dealbreakers.
- **No fabrication.** Company facts come from cited web sources (mark 要確認 when
  unknown); fit claims come only from data in `data/`. Company messages are quoted
  verbatim with a source, and their `evidence` is limited to real highlight ids —
  `python scripts/validate_data.py` enforces both.
- **企業メッセージに寄せるのは語彙まで。** A value the user cannot back up
  (`strength: none`) must never be turned into a claim about them; it becomes a
  question for the interview.
- **Balanced, not promotional.** Name downgrade/level risks and tail risks explicitly;
  the value is honesty, not encouragement.
- Keep the employing-entity, salary breakdown, and consolidation risk as first-class
  checklist items — these are where offers to foreign-capital / small local offices bite.
- Set the opportunity `status` to `検討中` unless the user says otherwise (vocabulary:
  AGENTS.md §6 — `検討中 / 応募前 / 書類選考中 / 面接中 / 内定 / 見送り`), and link
  company↔opportunity via front-matter and `[[...]]`.
- **見送りにするときは理由を `status` に書かない。** `status: 見送り` はそのままに、
  `outcome`（`未応募` / `不採用` / `辞退`）・`closed_reason`（一行）・`closed_date` を
  埋める。応募前に自分で落としたのか、応募して落とされたのかを混ぜないための分離で、
  `scripts/list_pipeline.py` の応募後の歩留まりがこれで数えられる。経緯は選考ログへ。
  `python scripts/validate_data.py` が強制する。
- **`jd_url` は応募できる一次窓口を書く。** ボードの掲載 URL はコメントで併記に落とす
  （step 2）。
