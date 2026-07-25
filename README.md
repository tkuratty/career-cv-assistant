# career-cv-assistant

A template repo that keeps your career history as a **structured single source of truth**
and generates **tailored CVs** — Japanese 職務経歴書 and English resume — as **Markdown,
PDF and docx**. It also helps you **source, vet and track** job opportunities and
recruiters with AI coding agents.

**Works with both [Claude Code](https://claude.com/claude-code) and
[Codex](https://openai.com/codex/)** — the workflow playbooks are agent-neutral.

> This is a **template**. Clone it, personalize it with your own data, and use it for your
> own job search. The sample data is a fictional persona (Taro Yamada / 山田 太郎).
>
> ⚠️ **Privacy**: once you fill in your real details, your copy contains personal
> information. Keep **your** repo **private** (or scrub it before sharing). Only the
> upstream template is meant to be public.

日本語の説明は各セクションの終わりに 🇯🇵 で併記しています。

---

## How it works

```
data/*.yaml            selection.yaml            cv/templates/
(your facts)     +     (pick & reorder)    +     (layout)      →  scripts/build_cv.py  →  md / pdf / docx
```

- **`data/`** is the only place your career facts live (single source of truth).
- A per-opportunity **`selection.yaml`** picks and reorders which positions/highlights to
  include and can override the summary — so you tailor a CV **without duplicating data**.
- **`cv/templates/`** holds the layout (Jinja2 Markdown + Typst PDF).

🇯🇵 職歴データは `data/*.yaml` にだけ持ち（単一ソース）、案件ごとの `selection.yaml` で
取捨選択・並べ替え・要約上書きをして、テンプレートと合成し CV を出力します。

## Quick start

```bash
# 1. Clone your fork
git clone <your-fork-url> && cd career-cv-assistant

# 2. Install (Markdown output needs only these)
pip install -r requirements.txt

# 3. (optional) for PDF / docx output
#   pandoc + typst — see "Toolchain" below

# 4. Build the sample CV to check it works
python scripts/build_cv.py --lang ja --formats md
python scripts/build_cv.py --lang en --formats md
# → cv/output/full/full.{ja,en}.md
```

🇯🇵 clone → `pip install -r requirements.txt` → `python scripts/build_cv.py --lang ja
--formats md` でサンプル CV が生成できれば準備完了です。

## Personalize (two ways)

### A. With an AI agent — the `setup-profile` skill (recommended)
Open the repo in **Claude Code** or **Codex** and ask it to set up your profile.

- **Claude Code**: it auto-loads the skills. Say e.g. 「セットアップして」/ "personalize this
  repo" and it runs **setup-profile**, interviewing you and writing `data/`.
- **Codex**: it reads `AGENTS.md` automatically. Use the `/setup-profile` prompt (copy
  `.codex/prompts/*.md` into `~/.codex/prompts/` to enable slash commands), or just say
  "follow `.claude/skills/setup-profile/SKILL.md` and set up my profile."

### B. By hand
Edit the files in `data/` directly, replacing the sample persona. Keep the format and keep
the **same `id`s** across the `ja`/`en` files. The relevant files:
`profile.{ja,en}.yaml`, `career.{ja,en}.yaml`, `skills.yaml`,
`education.{ja,en}.yaml`, `certifications.{ja,en}.yaml`, plus
`positioning.md` (your career axis) and `agent-policy.md` (how you deal with recruiters).

🇯🇵 パーソナライズは2通り：**(A)** Claude Code / Codex に `setup-profile` を実行させて対話で
埋める、**(B)** `data/` を手で編集する。どちらも ja/en の `id` を揃えるのがコツです。

## Generate CVs

```bash
# Full CV (all formats)
python scripts/build_cv.py --lang ja --formats md,pdf,docx
python scripts/build_cv.py --lang en --formats md,pdf,docx

# Tailored to one opportunity (via a selection file)
python scripts/build_cv.py --lang ja \
    --selection cv/output/<slug>/selection.yaml --formats md,pdf,docx
```

`--formats` defaults to `md`. A `selection.yaml` looks like:

```yaml
name: acme-corporate-it
summary_override: |            # optional; falls back to profile summary
  Tailored summary for this role…
positions:                     # optional; omit to include everything in file order
  - id: example-inc-2021
    highlights: [ex-security, ex-automation]   # optional subset + order
  - id: sample-solutions-2017
```

🇯🇵 フル CV は `--lang ja --formats md,pdf,docx`。案件向けは `selection.yaml` を指定します。

## The agent workflows (skills / prompts)

Each is a Markdown playbook under `.claude/skills/<name>/SKILL.md` (Claude auto-loads them;
Codex uses `.codex/prompts/<name>.md` or reads the SKILL.md directly).

| Workflow | What it does |
| --- | --- |
| **setup-profile** | First-run: interview you and replace the sample data in `data/`. |
| **find-opportunities** | Source roles matching `positioning.md`; return a ranked shortlist. |
| **tailor-cv** | Turn a JD into a tailored CV (selection + build). |
| **vet-opportunity** | 壁打ち a role/company; write `companies/` & `opportunities/` records. |
| **vet-agent** | Research a recruiter and design the 面談; write an `agents/` record. |

`companies/example/`, `opportunities/example.md`, `agents/example.md` are fictional format
samples the vet-* workflows reference. Delete them once you have real records.

🇯🇵 5つのワークフロー（setup-profile / find-opportunities / tailor-cv / vet-opportunity /
vet-agent）を用意。Claude はスキルとして自動認識、Codex は `.codex/prompts/` かスキルファイル
直読みで使えます。

## Toolchain (PDF / docx)

Markdown needs only Python (`PyYAML`, `Jinja2`). PDF and docx need
[Pandoc](https://pandoc.org/) and [Typst](https://typst.app/):

```bash
# Windows
winget install JohnMacFarlane.Pandoc
winget install Typst.Typst
# macOS
brew install pandoc typst
```

Optionally place a `cv/templates/reference.docx` to style the docx output
(`pandoc -o cv/templates/reference.docx --print-default-data-file reference.docx`).

🇯🇵 PDF/docx には `pandoc` と `typst` が必要です（未導入時は該当フォーマットでエラー終了）。

## Repo conventions

- `*.md` and `selection.yaml` are tracked (per-opportunity history). Generated PDF/docx are
  git-ignored — don't commit them.
- Company → opportunity → generated CV are linked via front-matter and `[[links]]`.
- Full agent instructions live in [AGENTS.md](AGENTS.md).

## License

MIT — see [LICENSE](LICENSE).
