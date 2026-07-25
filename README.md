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
| **align-company-message** | Record a company's MVV / OKR / 行動指針 with sources, back each with your real highlights, and derive 誇張しない wording for documents & interviews. |
| **prep-interview** | Prepare a scheduled interview round: brief, industry/round playbook, interviewer research (public info only), answer skeletons, 逆質問, 振り返り. |

`companies/example/`, `opportunities/example.md`, `agents/example.md`,
`interviews/example-r1.md` are fictional format samples the workflows reference. Delete
them once you have real records.

🇯🇵 7つのワークフロー（setup-profile / find-opportunities / tailor-cv / vet-opportunity /
vet-agent / align-company-message / prep-interview）を用意。Claude はスキルとして自動認識、
Codex は `.codex/prompts/` かスキルファイル直読みで使えます。

## Company messages without the exaggeration

Companies tell you what they value — MVV, 行動指針, 全社 OKR, 採用ページのメッセージ.
Echoing that in a CV or an interview is powerful and also the easiest way to slip into
overclaiming. This repo makes the line mechanical:

```yaml
# companies/<slug>/messages.yaml (excerpt)
- id: msg-okr-security
  type: okr
  quote: "今期は情報セキュリティ体制の底上げ（認証取得と権限統制）を全社目標に置いています。"
  source: src-careers          # must exist in sources[] — no unsourced quotes
  signals: [security, isms, iam]
  evidence: [ex-security]      # only real highlight ids from data/career.*.yaml
  strength: partial            # strong ≥2 evidence / partial 1 / none 0
  interview_probe: 「認証取得は外部コンサル主導ですか、社内で運用まで持つ想定ですか」
```

```bash
python scripts/validate_data.py                    # rejects strength the evidence can't support
python scripts/company_message_fit.py --company <slug> --lang ja
```

The report groups every message by how far you may go with it — **strong** = state it as
fact, **partial** = only with a limiting qualifier, **none** = don't claim it, ask about it
— lists the highlights that back it, and suggests highlights whose tags match but aren't
recorded as evidence yet.

🇯🇵 企業の MVV / OKR / 行動指針を出典つきで `companies/<slug>/messages.yaml` に記録し、
**自分の実績（evidence）の数**で「どこまで言い切ってよいか」を機械的に決めます。裏付けの
無い項目は書類で主張せず、面接の逆質問に回す — これが誇張を防ぐ仕組みです。

## Interview preparation

When an interview is scheduled, `prep-interview` turns the records you already have into
a prepared round and writes `interviews/<slug>-r<N>.md`:

```bash
python scripts/interview_brief.py --opportunity <slug> --round 1
```

The brief merges, in one page: the round and its interviewers (role + public sources),
the company research, **what you may claim** from the company's messages
(`strong` / `partial` / `none`), the highlights on the CV you actually submitted (i.e.
what gets probed), an **auto-generated 想定質問 set**, the opportunity's unanswered
checklist, a prioritized 逆質問 list, and your own decision axis. Anything missing is
reported as 未作成 rather than failing.

The 想定質問 set is built from what you have already collected — a deep-dive question per
submitted highlight, the JD gaps marked 「← 橋渡しが必要」, the company values you *cannot*
back up (answer 「やっていません」and turn it into a question), the round's standard
questions from `question-bank.md`, and **questions you were actually asked before**:

```yaml
# interviews/<slug>-r<N>.md — fill this in after the round
asked:
  - q: セキュリティ認証の取得を主導した経験はあるか
    answered: missed          # ok / weak / missed
    note: 認証取得の主導経験は無い。日常運用の範囲だと答えるべきだった
```

`weak` and `missed` come back to the top of the next round's 想定質問 — for the same
company and for any other company's round of the same type. The same question does not
catch you twice.

Two more pieces back it up:

- `.claude/skills/prep-interview/references/interview-playbooks.md` — typical hiring
  processes by company type (外資 / 日系大手 / SaaS / SIer / 製造 / 金融 / コンサル) and
  what each round type (`casual / first / technical / manager / executive / hr /
  reference / offer`) is for. Explicitly 一般論 — confirm the real process with the
  recruiter.
- `.claude/skills/prep-interview/references/question-bank.md` — the standard questions
  (common / per round type / per company type) used as a safety net so nothing obvious
  is missed.
- Interviewer research is limited to **public professional information** (role, public
  talks, technical posts), always with sources, never private life or sensitive
  attributes — see AGENTS.md §6.

🇯🇵 面接が決まったら `prep-interview`。業界別・ラウンド別の一般的な進め方（プレイブック）に、
面接官の公開情報リサーチと、収集済みの企業情報・提出済み CV を束ねた事前ブリーフを組み合わせ、
`interviews/<slug>-r<N>.md` に想定質問・逆質問・振り返りまで残します。想定質問は収集済み情報から
**自動生成**され、面接後に `asked[]` へ記録した「実際に聞かれた質問」（weak / missed）が次の
ラウンドの想定質問に戻ってきます。ここでも「裏付けの無いことは主張せず逆質問に回す」ルールが効きます。

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
