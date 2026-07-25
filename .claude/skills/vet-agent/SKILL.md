---
name: vet-agent
description: Register and vet a recruiting agent / 人材紹介会社 and design the upcoming 面談 with them. Use when the user forwards a recruiter's scout mail or meeting invite, names an agent or agent company, or asks to research/prepare for an エージェント面談 or キャリア面談. Researches the agency's business model and the individual recruiter, then writes agents/<slug>.md with a timed meeting plan. For vetting the job/company itself, use vet-opportunity instead.
---

# vet-agent

Treat a recruiting agent as a **standing relationship**, not a one-off transaction.
Register who they are, work out **whose agent they actually are**, and design the
specific 面談 so the user's scarcest resource — time — buys decisions, not information.

> Agent-neutral: this procedure works whether you are Claude or Codex. "Skill" just
> means this document. Use whatever web-search / browsing tools you have.

## Scope boundary
- **This skill**: the intermediary (agency + individual recruiter) and how to run the meeting.
- **`vet-opportunity`**: whether a specific 案件/企業 is worth pursuing.
- **`tailor-cv`**: what gets submitted.

If the user's real question is "is this job any good?", hand off to `vet-opportunity`.

## Read first (the axes)
1. **`data/agent-policy.md`** — how the user deals with agents. **This is the primary axis.**
2. `data/positioning.md` — the target "形", comp anchor, dealbreakers. Needed for 条件登録.
3. Existing `agents/*.md` — check for an existing entry (update, don't duplicate) and for
   **companies already entrusted to another agent** (重複応募 risk).

## Inputs to gather
- The **scout message / meeting invite** (paste, Gmail, or forwarded text).
- **Agency name**, **recruiter name**, contact details, **how they reached the user** (媒体).
- The **meeting date/time and length** if one is booked.
- A **slug** for the agency (e.g. `acme-recruiting`).

## Steps

1. **Extract the registration facts** from the source message — agency, recruiter, email(s),
   phone, address, 媒体, meeting URL/time, any reschedule links. Note domain mismatches or
   renamed entities. Never guess contact details.

2. **Research the agency (web).** Establish, in priority order:
   - **Business model** — 人材紹介 (agent) vs 掲載課金/ダイレクト応募 platform vs スカウト媒体.
     **This sets the user's expectations and is the single highest-value finding.** An agency
     that does not provide selection support must not be expected to.
   - **許可番号**（有料職業紹介）, 設立, 代表, 従業員数, 拠点, 沿革（社名変更含む）.
   - **Specialty** — industry/stage/level focus. Does it overlap the user's target domain?
   - **Reputation** — 良い/悪い評判 from multiple review sites; note 求人数 and regional bias.
   - **Their own hiring** — what the agency is recruiting for reveals which arm is being
     built and how mature it is.
   - **Organisation size** — small agencies carry recruiter-turnover risk.

3. **Research the individual recruiter** — public professional sources only (LinkedIn, note,
   Wantedly, company interviews, bylined articles). **Stay within public professional
   information; do not compile personal data.** If nothing is found, **record that explicitly**
   — "no public profile; ask directly" is a finding, not a failure. Also read signals from the
   mechanics of the outreach itself (scheduling-tool meeting type, template vs written-for-you
   message, which domain sent it).

4. **Check the proposed 案件 for existence, not merit.** Confirm the company is really a client
   and whether the **specific role the user wants actually exists** in their public postings.
   A generic "様々なポジションで募集中" with no matching opening is a 「とりあえず面談」 signal
   — say so plainly. Leave the merits of the role to `vet-opportunity`.

5. **Check 重複応募 risk** against `introduced_companies` across existing `agents/*.md`.

6. **Design the meeting** — a **timed plan that fits the actual slot**, not a question dump.
   Allocate minutes across four blocks and state the purpose of the meeting in one line:
   - **A. 素性** — 両面型か片面型か / direct or 二次請け / the recruiter's own patch.
   - **B. 本題** — the one thing that must be resolved (usually: does the role exist, and at
     what level/comp/location). **Include an explicit 撤退ライン** — the condition under which
     the user stops pursuing it mid-meeting and moves to C.
   - **C. 条件登録** — register the target **as a "形", never a job title**, per
     `data/positioning.md`; disclose the floor, not the ceiling; put 残業 and commute on par
     with comp. **This block runs even if B fails** — it is what makes the meeting worth it.
   - **D. 次アクション** — 無断推薦の禁止, no embellishment of the CV, what comes back by when.

   Add a 事前準備 checklist (which CV is ready at which path; forms to fill).

7. **Write `agents/<slug>.md`** — front-matter (slug, agent_company, agent, email, phone,
   address, license, model, channel, status, first_contact, `introduced_companies`, updated)
   + エージェント概要 / ビジネスモデルの実態 / 強み・弱み / 担当者について / 接触経緯 /
   提案された案件 / 面談設計 / メモ・所感 / やりとりログ.
   Use `agents/example.md` as the reference format.

8. **Report** — the business-model read, whether the proposed role exists, the one thing to
   resolve in the meeting, and the 撤退ライン. Then point to the file.

## After the meeting (when the user reports back)
Score the agent on `data/agent-policy.md`'s 評価軸 (案件の具体性 / 「形」の理解 / 情報 / 誠実さ /
経歴の扱い / 領域), update `status`, append to やりとりログ, and add any company actually
entrusted to `introduced_companies`. If a 案件 becomes concrete, hand off to `vet-opportunity`.

## Rules
- **Anchor to `data/agent-policy.md`.** Every recommendation ties back to one of its principles.
- **Time is the binding constraint.** Design to discard bad options fast, not to gather
  everything. Do not produce question lists longer than the slot allows.
- **No fabrication.** Agency and recruiter facts come from cited sources; mark unknowns 要確認.
  Absence of information about a person is reported as absence.
- **Public professional information only** when researching an individual.
- **Balanced.** Name 「とりあえず面談」 patterns, turnover risk, and model mismatches explicitly.
  The value is an accurate expectation, not enthusiasm.
- Keep `introduced_companies` current — it is the repo's only guard against 重複応募.
