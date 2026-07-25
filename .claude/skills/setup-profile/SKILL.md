---
name: setup-profile
description: First-run personalization. Interview the user and replace the sample career data with their own — profile, career history, skills, education, certifications, positioning and agent policy. Use right after cloning this template, or when the user says things like "セットアップ", "自分の情報に置き換えたい", "初期設定", "personalize this repo", or asks to fill in their profile/職務経歴. Then offers to build the first CV.
---

# setup-profile

Turn this template into the user's own single source of truth by **replacing the
sample persona** (Taro Yamada / 山田 太郎) in `data/` with the user's real details.

> Agent-neutral: this procedure works whether you are Claude or Codex. "Skill" just
> means this document. You only need file read/write and the ability to run
> `python scripts/build_cv.py`.

## Principles
- **Privacy first.** Filling in real data turns this repo into a personal instance that
  must be **private**. Before writing any real data, check the remote's visibility
  (`gh repo view --json visibility`, or ask the user); if the repo is public, stop and
  have the user make it private (or change the remote) first. See AGENTS.md §6.
- **No fabrication.** Only write facts the user gives you. If something is unknown,
  leave the field blank or ask — never invent employers, dates, or achievements.
- **Keep the format.** Match the existing YAML/Markdown structure exactly (see the
  sample files you are replacing). Do not restructure the schema.
- **Keep ja/en in sync.** `career.ja.yaml` and `career.en.yaml` share the same
  `id`s per position and per highlight; `skills.yaml` carries both labels. Whatever
  the user gives in one language, mirror the structure in the other (translate, or
  ask if the user only wants one language).
- **Work incrementally.** Confirm each section before moving on. It's fine to do this
  over several turns.

## Steps
1. **Explain what will change.** Tell the user you'll overwrite the sample data in
   `data/` with their information, section by section, and that generated CVs live in
   `cv/output/`. Ask which languages they need (`ja`, `en`, or both).

2. **Profile** → `data/profile.{ja,en}.yaml`
   Gather: name (+ kana for ja), email, phone, location, links (LinkedIn etc.),
   a default `summary`, spoken `languages`, and optionally `self_pr` (ja only).
   Replace the sample values. Remove the "▼▼ SAMPLE ▼▼" comment lines.

3. **Career history** → `data/career.{ja,en}.yaml`
   For each position gather: company, title, start/end (`YYYY-MM`, current = `present`),
   a one-line `summary`, and `highlights` as `{id, text, tags}`.
   - Give each position and highlight a stable, descriptive `id` (e.g. `acme-2021`,
     `acme-cost-reduction`) and reuse the **same id** in both language files.
   - `tags` are language-neutral keywords used later for JD matching — keep them in
     one language (English keywords recommended) and identical across ja/en.

4. **Skills** → `data/skills.yaml`
   Categories with `label.{ja,en}` and `items` (plain string, or `{ja,en}` for
   descriptive items). Order strongest/most-relevant categories first — the CV
   emphasizes what's on top.

5. **Education & certifications** → `data/education.{ja,en}.yaml`,
   `data/certifications.{ja,en}.yaml`. Same `id` across languages.

6. **Positioning** → `data/positioning.md`
   Interview for the user's target "form", positioning one-liner, differentiators,
   likes/dislikes, compensation floor/target, must-checks, dealbreakers, decision axis.
   Rewrite each section in the user's words, replacing the sample guidance. This file
   is the axis every other skill reads first — spend time here.

7. **Agent policy** → `data/agent-policy.md`
   Fill the `〈…〉` placeholders (salary floor, etc.). The principles are generic and
   can stay; personalize the numbers and any examples.

8. **Reset the example records (optional).** `companies/example/`, `opportunities/example.md`
   and `agents/example.md` are format samples the other skills reference. Leave them,
   or tell the user they can delete them once they have real records.

9. **Build the first CV.**
   ```
   python scripts/build_cv.py --lang ja --formats md
   python scripts/build_cv.py --lang en --formats md
   ```
   Add `pdf,docx` once pandoc + typst are installed (see README). Show the user the
   generated files under `cv/output/full/` and point them to `tailor-cv` for
   job-specific versions and `find-opportunities` / `vet-opportunity` for sourcing.

## Done when
- `data/*.yaml` and the two policy docs contain the user's real information (no
  "山田 太郎 / Taro Yamada / example.com" left), and
- `python scripts/validate_data.py` passes (ja/en id sync, date formats, tags), and
- `python scripts/build_cv.py --lang <ja|en> --formats md` builds a CV that reads
  correctly.
Verify no sample data remains, e.g.:
`grep -ri "山田 太郎\|Taro Yamada\|example.com" data/`
