---
name: tailor-cv
description: Generate a job-tailored CV (Japanese 職務経歴書 or English resume) from this repo's structured career data. Use when the user provides a job description / JD, points to an opportunities/<slug>.md file, or asks to build or customize a CV for a specific role or 案件. Produces a selection.yaml plus Markdown/PDF/docx via scripts/build_cv.py.
---

# tailor-cv

Turn a job description into a tailored CV by **selecting and reordering** existing
career highlights — never by inventing new facts.

> Agent-neutral: this procedure works whether you are Claude or Codex. "Skill" just
> means this document.

## Inputs to gather
- **JD source**: pasted text, a URL, or an `opportunities/<slug>.md` file.
- **Language**: `ja` (職務経歴書) or `en` (resume). Ask if unclear.
- **Formats**: default `md,pdf,docx`. Confirm if the user only needs some.
- **Output slug**: derive from the opportunity/company (e.g. `acme-senior`).

## Steps
1. **Read the career data**: `data/career.ja.yaml` and `data/career.en.yaml`
   (same `id` scheme across both) and `data/skills.yaml`. Each highlight has
   language-neutral `tags`.
2. **Score & select**: match the JD against `highlights[].tags` and text.
   Choose the most relevant positions and highlights, and order them
   strongest-first. Drop weak/irrelevant highlights rather than padding.
3. **Draft a summary**: write a `summary_override` (1–3 sentences) aimed at this
   role, using only facts already present in the data.
4. **Write the selection file** to `cv/output/<slug>/selection.yaml`:
   ```yaml
   name: acme-senior
   lang: ja                       # informational; pass --lang to the script
   summary_override: |
     決済基盤のテックリードとして…（この案件向けに調整）
   positions:
     - id: acme-senior-eng
       highlights: [acme-cost-reduction, acme-team-lead]   # subset + order
     - id: globex-backend
       highlights: [globex-microservices]
   ```
   Omit `positions` to include everything in default order; omit a position's
   `highlights` to keep all of that position's highlights.
5. **Build**:
   ```
   python scripts/build_cv.py --lang <ja|en> \
       --selection cv/output/<slug>/selection.yaml --formats md,pdf,docx
   ```
6. **Report**: show which highlights were chosen and why they fit the JD, and
   list the generated files under `cv/output/<slug>/`.

## Rules
- **No fabrication.** Only use positions/highlights/skills that exist in `data/`.
  If the JD needs something not in the data, tell the user — do not invent it.
- Keep both languages' `id`s in sync; if the user wants a highlight that only
  exists in one language file, flag the gap.
- If the user gives an `opportunities/<slug>.md` file, read its front-matter
  (`company`, `jd_url`, etc.) and set the `cv:` field there to the output dir.
- If `pandoc`/`typst` are missing, still write the `.md` and selection.yaml and
  tell the user how to install the toolchain (see README.md).
