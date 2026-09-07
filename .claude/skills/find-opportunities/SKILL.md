---
name: find-opportunities
description: Source new job openings that match the user's positioning — search job boards, ATS pages and (when connected) the HERP Career or LinkedIn MCP, filter out noise, and produce a positioning-ranked shortlist. Use when the user asks to find/search/探す new 求人 or 案件, scan job boards, or wants "よさげな求人" surfaced. This is the top of the funnel: hand promising hits to vet-opportunity for a full 壁打ち, and to tailor-cv for a CV. For vetting a single already-found role, use vet-opportunity instead.
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
   The salary floor and the commute/remote constraint written there are the two
   filters that cut the most noise — apply them at the source, not at the end.
2. `data/retirement-plan.md` — **if it exists**, its 足切り conditions are hard filters
   applied *before* ranking: a role that fails one is not a candidate, however well it
   fits the axis. Its 順位付け conditions are tie-breakers in the scoring step.
3. Run `python scripts/list_pipeline.py` — one-shot view of existing opportunities,
   agents' `introduced_companies`, and `opportunities/seen.yaml` (roles already
   surfaced/passed on). Use it to **dedupe**: don't re-surface roles already
   introduced, applied to, 見送り, or previously shown in a shortlist.

## Sources & how to use them

The layers below do **not** overlap much: a board-only search misses the companies
that publish through an ATS, and an ATS-only search misses the ones that only sit on
a board. Run several layers per session and record which ones you ran, including the
ones that returned **zero** — a 0 is information, not a failed search.

The URL shapes and per-site quirks below were probed in **2026-08** against a Japanese
corporate-IT search. If one has moved, find the current one rather than silently
dropping the source; if the user's target role differs, swap the keywords but keep
the retrieval mechanics.

### HERP Career MCP (primary, when connected) — structured, ad-free
Small startups are buried under promoted ads on the big platforms but are exactly
what HERP indexes. When the `HERP_Career_MCP_Server` tools are available, **use them
before scraping board HTML** — they return structured fields instead of rendered pages.

- `search_jobs(...)` → companies (each with a few representative jobs) + pagination.
  Useful filters: `keyword`, `jobRoleIds`, `prefCodes` / `cityCodes`, `employeeRanges`,
  `remoteworks`, `salary`, `employmentTypeId`, `sort`, `page`, `limit`.
  Map the axis onto the filters (`salary` = the floor from `positioning.md`,
  `employeeRanges` = the org-size band, `remoteworks` / `prefCodes` = the commute
  constraint), and run **several narrow queries** rather than one broad one, then
  merge and dedupe.
- `get_job(id)` → full JD: salary range, **required/preferred skills**, locations,
  remote-work type, company info. Pull this for every candidate you intend to
  shortlist — never rank on a search snippet alone.
- `get_company(slug)` → company profile **plus the full job list, directors, funding
  history and number-of-employees history**. This answers the 規模・資金・体制
  questions board HTML hides, and `vet-opportunity` reuses it (see that skill's step 1).
- **Links must be Markdown, never raw URLs** (the MCP requires this):
  求人 `https://herp.careers/careers/companies/{companySlug}/jobs/{id}?utm_source=herp_career_mcp`,
  企業 `https://herp.careers/careers/companies/{companySlug}?utm_source=herp_career_mcp`.
- `get_user_profile()` is read-only; use it to cross-check what HERP knows about the
  user. **`data/positioning.md` remains the axis** — if they disagree, the repo wins
  and the gap is worth mentioning.
- ⚠️ **`update_user_career_preferences` writes to the user's real HERP account** and can
  trigger 面談オファー from companies. Treat it as an outward-facing action:
  **never call it on your own initiative.** Only when the user explicitly asks — and
  then `get_user_profile()` first, merge rather than overwrite, show the exact text,
  and get an explicit 「保存してよいですか?」 yes.

### B1. Role-specific job boards
Use web search / fetch. Ask, per posting, for: company, title, location, salary if
shown, remote/出社 policy, and the **business domain**.
- **HERP Careers (HTML)** — `https://herp.careers/careers/jobs?job-role-ids=<role>`
  (fallback when the MCP is not connected).
- **SYNCA** — corporate/back-office board. ⚠️ As of 2026-08, `synca.net` /
  `candidate.synca.net` refused both curl and browser navigation; only WebSearch
  snippets are reachable. Chase anything interesting to the company's own page.
- 日経転職版 (startup filter), コトラ (ハイクラス), plus any domain-specific board.

### B2. ATS cross-search via `site:` — reaches what the boards do not index
Talentio / HRMOS / Jobcan have **no public cross-search** (`hrmos.co/pages/search`
is 404, `recruit.jobcan.jp/search` is 400). Hit the per-company pages through
**WebSearch `site:` queries** instead:
- `site:open.talentio.com <役割キーワード>` / `site:hrmos.co <役割キーワード>` /
  `site:recruit.jobcan.jp <役割キーワード>`
- English / foreign-capital roles: `site:boards.greenhouse.io <role> Japan` /
  `site:jobs.lever.co <role> Tokyo`

This layer is where the roles that appear on **no board at all** come from — in the
2026-08 run it was the only source for several well-funded startups. Always open the
JD itself for title, salary and 出社頻度; **never rank on the search snippet**. The
retrieval differs per ATS, and getting this wrong looks like "the page is empty":
- **Talentio does not work with WebFetch.** The page is fully client-rendered and
  WebFetch returns little more than the logo. The JD is embedded in the HTML as
  **escaped JSON**: fetch with curl → `html.unescape` → pick out the
  `"name":"…","value":"…"` pairs. Salary, location, work style, requirements and
  benefits all come back keyed.
- **HRMOS reads fine with WebFetch.**
- **Jobcan search snippets go stale.** Postings 404, and a role the snippet implies
  may not exist at all — **confirm on the company's own job list** before shortlisting.
- **Greenhouse / Lever carry very few Japan-based corporate roles.** Lowest priority.

### B3. Public listings of foreign-capital recruiting agencies — off by default
Probed in 2026-08 and **structurally unusable** for this workflow: the large agency
sites either list every role under an anonymised employer label, render the list only
via JS, or return 403 to fetching. ⚠️ A posting whose employer is hidden cannot be
scored on **any** axis, and long-running anonymous listings are often
母集団形成 (pipeline-building) rather than a real opening. Run this layer **only when
the user explicitly asks** to target that market; otherwise spend the time on B2/B4.

### B4. English-language boards in Japan — salary and remote are usually stated
- **TokyoDev** — `https://www.tokyodev.com/jobs?q=<keyword>`
- **Japan Dev** — `https://japan-dev.com/jobs?tag=<tag>`

Their value is that most listings state a **salary range and a remote policy**, so the
floor and the commute constraint can be applied on the first pass. They are dev-heavy,
though — a 0 for a non-dev role is normal, not a failure.
- **TokyoDev: the list reads with WebFetch, but job detail pages sit behind
  Cloudflare (403, curl included)** — open details with a browser tool, and only for
  candidates that already survived the list-level filter.
- **Japan Dev: both list and detail read with WebFetch.**

### B5. Aggregators — leftover check only
- **求人ボックス** — `https://求人ボックス.com/{キーワード}の仕事` (percent-encode the host).

Noisy and duplicated: run it **after** B1–B4 as a "did we miss anything" pass, and
still trace every hit back to a primary source before shortlisting. Wantedly / Green
are off by default because **most postings hide salary**, which disables the floor
filter (use them only on explicit request).

### LinkedIn MCP (complementary) — only when the MCP is connected
- ⚠️ **This repo ships no LinkedIn setup, on purpose.** There is no official LinkedIn MCP
  server; third-party ones are mostly scrapers, and using one may violate LinkedIn's terms
  of service and put the user's account at risk. Do **not** recommend or install one — if
  the user connects a tool themselves, that call (and its risk) is theirs. Everything
  below applies only once such a tool is already connected.
- `search_jobs(keywords, location, ...)` → a page **plus `job_ids`**.
  ⚠️ **The result list is ad-polluted**: the top rows are almost always
  「プロモーション」 (promoted big-company ads). Do **not** treat them as the best
  matches. In the 2026-08 run, a role-specific Tokyo query returned **11 rows that were
  all promoted and all unrelated** (kitchen, night shift, executive assistant) and
  **zero organic hits** — an empty LinkedIn pass is normal.
- Scan the returned `job_ids` / titles, pick the **organic, on-axis** ones, and call
  `get_job_details(job_id)` for the **clean full JD**, company size/industry and the
  hiring contact.
- **Keyword tips** (the JP index is weak on colloquial / compound terms):
  prefer **single tokens** over two-word ANDs and slang; add **English role-level
  terms** (`Head of IT`, `Corporate Engineer`, `IT Manager`).
- **Never enter credentials yourself.** If sign-in is required, ask the user to do it,
  then retry the same call.

## Steps
1. **Frame the search** from `positioning.md` (form, domain, salary floor, commute/
   remote, dealbreakers). State the query set you'll run.
2. **Run the searches**, in this order of yield:
   1. **HERP Career MCP** — several narrow `search_jobs` queries, then `get_job` on the
      on-axis hits. Skip only if the MCP is not connected.
   2. **B1 → B2 → B4** (boards → ATS `site:` search → English-language boards).
      B2 and B4 do not overlap with the MCP layer, so they matter most on a thin run.
   3. **LinkedIn MCP** in parallel if it is connected (`get_job_details` only for
      on-axis `job_ids`).
   4. **B5** as the final leftover check. **B3** only on explicit request.
   Record which sources you ran and what each returned, **including the zeros**.
3. **Dedupe** against the `list_pipeline.py` output (introduced companies, existing
   opportunities, and `seen.yaml`).
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
- **A posting with no employer name cannot be scored.** Say so and park it, rather than
  ranking it on the agency's blurb.
- **Balanced, not promotional.** Name the level/comp/structural risk next to the appeal.
- **Dedupe** so the user isn't shown roles already introduced/applied/見送り.
- **Prefer the primary application route as the link.** Use the window the user can
  actually apply through (company careers page / ATS) over a board listing. A board's
  "last updated" is the day the posting text was edited, **not** proof that the opening
  is alive or dead — so don't call an old posting closed, or a fresh one live.
  Confirming freshness and the application route is `vet-opportunity` step 2;
  here, **don't state as settled what you have not settled**.
- **Read-only sourcing.** Do **not** apply, save, or message a recruiter on the user's
  behalf — surface the link and let the user act. (Sign-in is the user's too.) This
  includes **`update_user_career_preferences`**, which edits the user's live HERP
  profile: explicit request + shown text + explicit consent, or not at all.
- This skill **finds and ranks**; it does not write repo files, with one exception:
  after the user reacts to the shortlist, append the roles they pass on (and, if they
  want, the surfaced-but-parked ones) to `opportunities/seen.yaml` so later runs don't
  re-surface them:
  ```yaml
  seen:
    - { company: 株式会社◯◯, title: 情報システム, url: https://…, date: 2026-01-01, verdict: 見送り }
    # ⚠️ URL にクエリ文字列（`?`）が入るときは必ずクォートする。`{...}` のフロー形式では
    # `?` が YAML の予約文字なので、裸で書くと **ファイル全体がパース不能**になる。
    - { company: 株式会社△△, title: 社内SE, url: "https://example.com/job.phtml?job_code=1", date: 2026-01-01, verdict: 見送り }
  ```
  Then run `python scripts/validate_data.py` — its `check_seen` verifies the syntax,
  the required fields and the date format. A broken `seen.yaml` fails silently otherwise:
  nothing reads it until the next run, which then loses the whole dedupe log.
  Records proper are created by `vet-opportunity` (companies/opportunities) and
  `tailor-cv` (selection/CV).
