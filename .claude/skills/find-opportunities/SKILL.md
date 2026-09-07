---
name: find-opportunities
description: Source new job openings that match the user's positioning — search job boards, ATS site: searches and English-language JP boards (plus a job-search MCP or LinkedIn if one is connected), filter out noise, and produce a positioning-ranked shortlist. Use when the user asks to find/search/探す new 求人 or 案件, scan job boards, or wants "よさげな求人" surfaced. This is the top of the funnel: hand promising hits to vet-opportunity for a full 壁打ち, and to tailor-cv for a CV. For vetting a single already-found role, use vet-opportunity instead.
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
2. `data/retirement-plan.md` — **if it exists**, its 足切り conditions are hard filters
   applied *before* ranking: a role that fails one is not a candidate, however well it
   fits the axis. Its 順位付け conditions are tie-breakers in step 4.
3. Run `python scripts/list_pipeline.py` — one-shot view of existing opportunities,
   agents' `introduced_companies`, and `opportunities/seen.yaml` (roles already
   surfaced/passed on). Use it to **dedupe**: don't re-surface roles already
   introduced, applied to, 見送り, or previously shown in a shortlist.

## Sources & how to use them

The layers below are ordered by yield. **They do not overlap much** — the small
companies that a startup board indexes are usually absent from the aggregators, and the
ones hiring through their own ATS are absent from both. Running only the first layer is
the most common way to miss the best-fitting roles. Report which layers you ran and how
many hits each produced, **including the ones that returned zero**.

### A. A job-search MCP (first, when one is connected)
If a job-search MCP is connected (e.g. a board's own server), **use it before scraping
board HTML** — it returns structured fields instead of rendered pages, with no ads.

- Search with **several narrow queries** rather than one broad one (e.g. 情報システム /
  コーポレートIT / 情シス 立ち上げ / IT インフラ), then merge and dedupe.
- Map the axis onto the filters the server offers: salary floor, company size band,
  remote-work type, prefecture/city for the commute constraint.
- Pull the **full JD** for every role you intend to shortlist — never rank on a search
  snippet. If the server exposes a company endpoint, use it: headcount history, funding
  rounds and the **full list of open roles** answer the 規模・資金・体制 questions that
  board HTML hides, and `vet-opportunity` reuses the same call.
- Follow the server's citation rules (some require Markdown links rather than raw URLs).
- ⚠️ **A write call on such a server touches the user's real account.** Anything that
  edits a career profile or preferences can attract 面談オファー from companies — it is
  an outward-facing action. **Never call it on your own initiative**: only on an explicit
  request, and then read the current values first, merge rather than overwrite, show the
  exact text, and get an explicit 「保存してよいですか?」 yes.

### B. Job boards and ATS searches (always — this is the bulk of the yield)
Use web search / fetch. Ask, per posting, for: company, title, location, salary if
shown, remote/出社 policy, and the **business domain**. If a URL shape below has moved,
find the current one rather than silently dropping the source.

**B1. 職種特化ボード** — where on-axis roles are indexed by role, not by keyword.
- **HERP Careers** — startup 図鑑; filter by role (e.g. 情報システム / コーポレートIT).
- **SYNCA (シンカ)** — corporate/back-office focused (情報システム / 一人目情シス).
- Others as fit: 日経転職版, ハイクラス系エージェント媒体, ドメイン特化ボード.

**B2. ATS 横断（`site:` 検索）— boards don't index these at all.**
Talentio / HRMOS / Jobcan have **no public cross-company search**, so reach the
individual company pages through a search engine's `site:` operator instead:
- `site:open.talentio.com 情報システム` / `コーポレートIT` / `社内IT`
- `site:hrmos.co コーポレートIT` / `情報システム`
- `site:recruit.jobcan.jp 情報システム`
- English / foreign-affiliated roles: `site:boards.greenhouse.io Corporate IT Japan`,
  `site:jobs.lever.co IT Tokyo` — thin for JP corporate IT, so keep these last.

⚠️ **Fetching the JD body differs per ATS.** Get this wrong and the posting looks empty:
- **Talentio does not respond to a plain fetch.** The page is fully client-rendered and a
  fetch returns little more than the company logo. The JD is embedded in the HTML as
  **escaped JSON** — fetch with `curl`, run `html.unescape`, then pull the
  `"name":"…","value":"…"` pairs: 賃金・勤務地・勤務形態・応募資格・福利厚生 come out
  keyed and intact.
- **HRMOS reads fine with an ordinary fetch.**
- **Jobcan's search snippets go stale.** A snippet can point at a posting that now 404s,
  or at a role the company never listed. **Confirm the posting exists on the company's
  own listing page** before putting it in a shortlist.

**B3. 在日英語圏ボード** — salary range and remote policy are usually stated outright,
so the compensation floor and the commute constraint can be settled in the first pass.
- **TokyoDev**, **Japan Dev**. Dev-centric, so corporate-IT hits are few — **zero is a
  normal result here, not a failed search.**
- Some of these sit behind a bot-protection layer that blocks a plain fetch on the
  *detail* pages while the listing page reads fine. The listing usually carries salary,
  remote policy and the Japanese-language requirement, so open detail pages with a
  browser tool only for candidates that already survived the first filter.

**B4. アグリゲータ（取りこぼし確認のみ）** — 求人ボックス and similar. Noisy and full of
duplicates, so run them **after** B1〜B3 as a gap check, and always follow a hit back to
the primary source (company careers page / the ATS JD) before shortlisting it. Boards
that mostly hide salary (Wantedly, Green) don't let the compensation floor filter
anything, so skip them unless the user asks.

**B5. 外資系エージェントの公開求人 — off by default.** Postings from the large
recruitment agencies routinely **withhold the company name** ("外資系企業"), and several
of their listing pages are JS-rendered or block automated access. A role whose employer
is unknown can't be scored on domain fit, structural risk, or 待遇 — the three things
this skill exists to judge — and 母集団形成 postings are common at this layer. Run it
only when the user explicitly asks for that segment.

### C. LinkedIn (optional) — only if a LinkedIn tool/MCP is connected
- ⚠️ **This repo ships no LinkedIn setup, on purpose.** There is no official LinkedIn MCP
  server; third-party ones are mostly scrapers, and using one may violate LinkedIn's terms
  of service and put the user's account at risk. Do **not** recommend or install one — if
  the user connects a tool themselves, that call (and its risk) is theirs. Everything below
  applies only once such a tool is already connected.
- ⚠️ **LinkedIn job results are ad-polluted**: the top rows are usually promoted
  big-company ads, and an entire page of results being promoted (with the organic count
  at zero) is a normal outcome, not a broken search. Do **not** treat the first rows as
  the best matches. Scan the returned ids/titles, pick the **organic, on-axis** ones, and
  pull the clean full JD for those only.
- **Keyword tips**: prefer single tokens (e.g. `コーポレートIT`) — two-token AND queries
  and slang (情シス, 立ち上げ) tend to return 該当なし, which leaves only ads. Add English
  role-level terms (`Head of IT`, `Corporate Engineer`, `IT Manager`).
- **Never enter credentials yourself.** If sign-in is required, ask the user to do it.

## 掲載日の取り方（求人票に日付が無いとき）

"How long has this seat been open" is the substance of `vet-opportunity`'s
確認チェックリスト①. **Old does not mean closed** — but a posting that has been up for a
year changes what you should ask. Most ATSs carry the date in machine-readable form even
when the rendered page doesn't show it. Try in this order:

1. **The posting itself.** Some ATSs render a "Posted Date". Look before you dig.
2. **JSON-LD `datePosted`** (the structured data emitted for job search engines) —
   HRMOS publishes this. `curl` the page and grep:
   ```bash
   curl -sL "https://hrmos.co/pages/<company>/jobs/<id>" | grep -o '"datePosted"[^,]*'
   ```
3. **The ATS's JSON API.** BambooHR returns `datePosted` from
   `https://<company>.bamboohr.com/careers/<id>/detail` with `Accept: application/json`
   (`/careers/list` gives every open role). Workday returns `startDate` from
   `/wday/cxs/<tenant>/<site>/job/<path>`.
4. **Sometimes it cannot be had.** Some career sites publish neither structured data nor
   an API. Then write 「不明」 and ask in the interview. **Never guess "new" or "old".**

⚠️ **The Wayback Machine does not answer this.** Individual ATS job pages are typically
uncrawled (zero snapshots), and snapshots of SPA listing pages contain only the app
shell with no job data in them. More fundamentally it records *when a page was archived*,
not *when a role opened* — an absent snapshot proves nothing except that no crawler came.

⚠️ `datePosted` is the date the ATS first published the posting. It cannot distinguish
"open continuously since then" from "closed and re-posted". Convert the elapsed time
into questions — 「この枠はいつから空いていますか」「募集背景（増員 / 欠員 / 再編）は
今も有効ですか」 — rather than into a deduction.

## Steps
1. **Frame the search** from `positioning.md` (form, domain, salary floor, commute/
   remote, dealbreakers) and, if present, `retirement-plan.md`'s 足切り conditions.
   State the query set you'll run.
2. **Run the searches** in yield order: a connected job-search MCP → B1〜B3 boards and
   `site:` searches → LinkedIn in parallel if connected → B4 aggregators as a gap check.
   Pull the clean full JD for on-axis hits. Report every layer you ran, zeros included.
3. **Dedupe** against the `list_pipeline.py` output (introduced companies, existing
   opportunities, and `seen.yaml`).
4. **Score against positioning** and rank. For each candidate note: domain fit, role
   "form" (owner vs helpdesk/analyst vs people-manager), which differentiators it uses,
   salary vs the user's floor, commute/remote, and any dealbreaker hit.
5. **Report a shortlist** — strongest-first, grouped (e.g. 「芯を食う」 vs 「面白いが
   comp/規模で一段下」), each with a **clean primary link** and a one-line why/risk.
6. **Hand off** — offer to run `vet-opportunity` on the top pick(s) and `tailor-cv`
   once a target is chosen.

## Rules
- **Anchor to `data/positioning.md`.** Rank by "can the user keep building here" — not by
  brand, apply-ability, or title. Drop dealbreaker roles or flag them explicitly.
- **No fabrication.** Company/role facts come from the JD or cited board pages. Mark
  unknowns (salary, level, team size) as **要確認** — don't guess.
- **Balanced, not promotional.** Name the level/comp/structural risk next to the appeal.
- **Dedupe** so the user isn't shown roles already introduced/applied/見送り.
- **Prefer the primary window for the link.** A shortlist entry's link should be the page
  that accepts an application (company careers page / ATS), not the board listing. Do
  **not** state here that a posting is live or dead — confirming that is
  `vet-opportunity`'s step 2. Don't write down as settled what you haven't settled.
- **Read-only sourcing.** Do **not** apply, save, or message a recruiter on the user's
  behalf — surface the link and let the user act. (Sign-in is the user's too.) This
  includes any MCP call that writes to the user's account on a job platform: explicit
  request + shown text + explicit consent, or not at all.
- This skill **finds and ranks**; it does not write repo files, with one exception:
  after the user reacts to the shortlist, append the roles they pass on (and, if they
  want, the surfaced-but-parked ones) to `opportunities/seen.yaml` so later runs don't
  re-surface them:
  ```yaml
  seen:
    - { company: 株式会社◯◯, title: 情報システム, url: https://…, date: 2026-07-25, verdict: 見送り }
    # ⚠️ URL にクエリ文字列（`?`）が入るときは必ずクォートする。`{...}` のフロー形式では
    # `?` が YAML の予約文字なので、裸で書くと **ファイル全体がパース不能**になる。
    - { company: 株式会社△△, title: 社内SE, url: "https://example.com/job.phtml?job_code=1", date: 2026-07-25, verdict: 見送り }
  ```
  Then run `python scripts/validate_data.py` — its `check_seen` verifies the syntax,
  the required fields and the date format. A broken `seen.yaml` fails silently otherwise:
  nothing reads it until the next run, which then loses the whole dedupe log.
  Records proper are created by `vet-opportunity` (companies/opportunities) and
  `tailor-cv` (selection/CV).
