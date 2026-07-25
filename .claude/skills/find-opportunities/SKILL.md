---
name: find-opportunities
description: Source new job openings that match the user's positioning — search job boards (and LinkedIn if a LinkedIn tool is available), filter out noise, and produce a positioning-ranked shortlist. Use when the user asks to find/search/探す new 求人 or 案件, scan job boards, or wants "よさげな求人" surfaced. This is the top of the funnel: hand promising hits to vet-opportunity for a full 壁打ち, and to tailor-cv for a CV. For vetting a single already-found role, use vet-opportunity instead.
---

# find-opportunities

Source and shortlist job openings that fit the user's own axis — **not** whatever
a feed pushes. The output is a ranked shortlist tied to `data/positioning.md`, with
a clean primary link per role, ready to hand to `vet-opportunity`.

> Agent-neutral: this procedure works whether you are Claude or Codex. "Skill" just
> means this document. Use whatever web-search / browsing tools you have.

## Read first (the axis)
1. `data/positioning.md` — target "form", differentiators, compensation anchor,
   must-checks, and **dealbreakers**. Every include/exclude decision ties back here.
2. `agents/*.md` front-matter `introduced_companies` and existing `opportunities/*.md` —
   to **dedupe**: don't re-surface roles already introduced, applied to, or 見送り.

## Sources & how to use them
### Job boards (primary) — where on-axis roles actually live
Use web search / fetch (ad-free is best). Ask, per posting, for: company, title,
location, salary if shown, and the **business domain**. Good starting points for the
Japan market (adjust to the user's target):
- **HERP Careers** — startup 図鑑; filter by role (e.g. 情報システム / コーポレートIT).
- **SYNCA (シンカ)** — corporate/back-office focused board (情報システム / 一人目情シス).
- Others as fit: 日経転職版, ハイクラス系エージェント媒体, ドメイン特化ボード.

### LinkedIn (optional) — only if a LinkedIn tool/MCP is connected
- If a LinkedIn search tool is available, use it; otherwise skip LinkedIn and rely on
  boards + general web search.
- ⚠️ **This repo ships no LinkedIn setup, on purpose.** There is no official LinkedIn MCP
  server; third-party ones are mostly scrapers, and using one may violate LinkedIn's terms
  of service and put the user's account at risk. Do **not** recommend or install one — if
  the user connects a tool themselves, that call (and its risk) is theirs. Everything below
  applies only once such a tool is already connected.
- ⚠️ **LinkedIn job results are ad-polluted**: the top rows are usually promoted
  big-company ads. Do **not** treat the first rows as the best matches. Prefer the
  organic, on-axis rows and pull the clean full JD.
- **Keyword tips**: prefer single tokens (e.g. `コーポレートIT`), add English
  role-level terms (`Head of IT`, `Corporate Engineer`, `IT Manager`).
- **Never enter credentials yourself.** If sign-in is required, ask the user to do it.

## Steps
1. **Frame the search** from `positioning.md` (form, domain, salary floor, commute/
   remote, dealbreakers). State the query set you'll run.
2. **Run the searches** — boards first; LinkedIn only if a tool is connected. Pull the
   clean full JD for on-axis hits.
3. **Dedupe** against `agents/*.md` introduced_companies and existing `opportunities/*.md`.
4. **Score against positioning** and rank. For each candidate note: domain fit, role
   "form" (owner vs helpdesk/analyst vs people-manager), which differentiators it uses,
   salary vs the user's floor, commute/remote, and any dealbreaker hit.
5. **Report a shortlist** — strongest-first, grouped, each with a **clean primary link**
   and a one-line why/risk.
6. **Hand off** — offer to run `vet-opportunity` on the top pick(s) and `tailor-cv`
   once a target is chosen.

## Rules
- **Anchor to `data/positioning.md`.** Rank by "can the user keep building here" — not by
  brand, apply-ability, or title. Drop dealbreaker roles or flag them explicitly.
- **No fabrication.** Company/role facts come from the JD or cited board pages. Mark
  unknowns (salary, level, team size) as **要確認** — don't guess.
- **Balanced, not promotional.** Name the level/comp/structural risk next to the appeal.
- **Dedupe** so the user isn't shown roles already introduced/applied/見送り.
- **Read-only sourcing.** Do **not** apply, save, or message a recruiter on the user's
  behalf — surface the link and let the user act. (Sign-in is the user's too.)
- This skill **finds and ranks**; it does not write repo files. Records are created by
  `vet-opportunity` (companies/opportunities) and `tailor-cv` (selection/CV).
