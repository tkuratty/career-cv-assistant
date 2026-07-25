---
name: vet-opportunity
description: Vet a job opportunity (agent 案件 / JD) as a sounding board — research the company, assess fit against the user's career data and positioning, surface risks and the positioning gap, and produce a vetting checklist and interview framing. Use when the user pastes a job posting, forwards an agent's 案件, or asks to analyze/研究/壁打ち a role or company. Writes companies/<slug>/research.md and opportunities/<slug>.md in this repo's format. For generating a tailored CV, use tailor-cv instead.
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
3. If a `companies/<slug>/research.md` already exists, update it rather than dup.

## Steps
1. **Company research (web)** — use WebSearch/WebFetch for: financials/credit rating,
   the local office's role and strategic weight, precedents of closures / layoffs /
   consolidation, and technology/AI posture. Prefer primary sources; note when only
   secondary sources exist. **Never invent facts or figures** — mark unknowns as
   "要確認".
2. **Fit analysis** — map JD requirements to the user's career data: what is clearly
   covered, and the **explicit gaps** (e.g. no financial-industry experience). Propose
   how to **bridge** each gap using existing facts (regulated-industry controlled ops,
   ISMS/ISO27001, change management), without fabricating.
3. **Positioning gap** — compare the role's level/autonomy to `positioning.md`'s target
   (e.g. Head of IT vs an Analyst seat under a Manager). State plainly if it is a
   sideways/down move and hypothesize *why the agent proposed it*.
4. **Risk analysis** — structural risks: local-function consolidation/offshore, on-call
   for market/regulatory systems, shadow-IT/governance friction for the user's
   automation style, AI-tooling constraints (approved agentic path vs blocked public AI),
   retention/tenure, employing-entity/severance ambiguity.
5. **Vetting checklist** — instantiate the template below with company-specific items.
6. **Interview framing** — neutral phrasings for sensitive risks; how to bridge gaps;
   and the reminder to **sell the judgment layer, not the AI tool** (avoid a
   "can't work without Claude" framing — reframe as "governed value creation").
7. **Optional (if requested)** — draft agent questions (leveling check + ask for a
   higher-level seat) and interview-answer starters.
8. **Write files** — create/update:
   - `companies/<slug>/research.md` — front-matter (slug, name, industry, size,
     website, updated, sources) + 概要 / 拠点の位置づけ・存続リスク / AI 活用状況 /
     本人経歴との相性 / ポジショニングのギャップ / 関連案件 `[[...]]`.
   - `opportunities/<slug>.md` — front-matter (slug, company, title, agent,
     agent_company, status, employment, location, salary, report_line, team_size,
     jd_url, applied_date, cv, updated) + ポジション概要 / 求める経験 / 魅力 /
     懸念・リスク / 確認チェックリスト / 面接での聞き方メモ / 判断軸 / 選考ログ.
   Use `companies/example/research.md` and `opportunities/example.md` as the
   reference format.
9. **Report** — summarize fit, the top risk, the positioning read, and the decision
   axis; then point to the two files written.

## 確認チェックリスト テンプレート（案件ごとに具体化）
1. **案件・エージェントの素性**: 直接取引か二次請けか / 紹介実績 / 「後任」の裏取り / 年収内訳。
2. **雇用主体**: 契約先法人格 / 退職金の有無 / 社保・DC・福利厚生。
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
  unknown); fit claims come only from data in `data/`.
- **Balanced, not promotional.** Name downgrade/level risks and tail risks explicitly;
  the value is honesty, not encouragement.
- Keep the employing-entity, salary breakdown, and consolidation risk as first-class
  checklist items — these are where offers to foreign-capital / small local offices bite.
- Set the opportunity `status` to `検討中` unless the user says otherwise (vocabulary:
  AGENTS.md §6 — `検討中 / 応募前 / 書類選考中 / 面接中 / 内定 / 見送り`), and link
  company↔opportunity via front-matter and `[[...]]`.
