# AGENTS.md

Agent instructions for **career-cv-assistant** — a template repo that manages your
career history as a **structured single source of truth** and generates **tailored CVs
(Japanese 職務経歴書 / English resume) as Markdown, PDF and docx**, plus company and
recruiter research records.

This file is **agent-neutral**: it applies whether you are **Claude Code** or **Codex**
(or any other coding agent). Wherever a document says "skill", read it as "a Markdown
playbook you follow." Use whatever file and web tools you have.

> Cloned this repo? Start with **setup-profile** to replace the sample persona
> (Taro Yamada / 山田 太郎) with the real user's data. See "Workflows" below.

## 1. Architecture principles

- **Single source of truth**: career data lives **only** in `data/*.yaml`. Never
  hard-code data into the generated CVs (md/pdf/docx). Don't hold the same fact twice.
- **data ⇄ selection ⇄ generation split**: `data/` (facts) + a per-opportunity
  `selection.yaml` (pick / reorder / summary override) + `cv/templates/` (layout)
  → `scripts/build_cv.py` composes the output.
- **ja/en pairing**: positions and highlights in `career.{ja,en}.yaml` share the **same
  `id`**. `selection.yaml` works on ids, language-independently.
- **Language-neutral tags**: `highlights[].tags` are shared across ja/en and used for
  JD matching.

## 2. Directory layout

| Path | Role |
| --- | --- |
| `data/` | Single source: `profile.{ja,en}.yaml` / `career.{ja,en}.yaml` / `skills.yaml` / `education.{ja,en}.yaml` / `certifications.{ja,en}.yaml` / `positioning.md` (career axis) / `agent-policy.md` (how to deal with recruiters) |
| `cv/templates/` | Jinja2 Markdown (`*.md.j2`) + Typst PDF (`*.typ`) templates; optional `reference.docx` |
| `cv/output/<slug>/` | Per-opportunity output (`selection.yaml` + md/pdf/docx). `full/` is the full CV |
| `companies/<slug>/research.md` | Company research |
| `companies/<slug>/messages.yaml` | The company's own messaging (MVV / OKR / 行動指針 / 経営・採用メッセージ) with sources, mapped to the user's highlights as evidence |
| `agents/<slug>.md` | Recruiter / agency registration |
| `opportunities/<slug>.md` | A job opportunity (front-matter links to company & generated CV) |
| `interviews/<slug>-r<N>.md` | One interview round: 目的・面接官（公開情報のみ）・語り口・想定質問・逆質問・振り返り。`asked[]` に実際に聞かれた質問を残すと次ラウンドの想定質問に戻る |
| `scripts/build_cv.py` | data + selection + template → md/pdf/docx |
| `scripts/validate_data.py` | Machine-check data conventions (ja/en id sync, dates, selection refs) |
| `scripts/company_message_fit.py` | 企業メッセージ × 本人の実績の整合レポート（誇張の上限を明示） |
| `scripts/interview_brief.py` | 面接前ブリーフ（企業調査 + 企業メッセージ + 提出 CV + 案件の懸念 + **想定質問の自動生成**） |
| `scripts/list_pipeline.py` | One-command pipeline overview (opportunities / agents / companies / seen) for dedupe |
| `scripts/check_pii.py` | Template-only PII guard (run by CI on the upstream repo) |
| `opportunities/seen.yaml` | Optional log of roles already surfaced/passed on by find-opportunities |
| `.claude/skills/<name>/SKILL.md` | The workflow playbooks (canonical) |
| `.codex/prompts/<name>.md` | Codex slash-command wrappers that point to the same playbooks |

## 3. Data conventions

Always match the existing file format before editing.

- **id consistency**: when you add a position, add it to **both** `career.ja.yaml` and
  `career.en.yaml` with the **same `id`**. Never update only one language.
- **highlight shape**: `{id, text, tags}`. `text` corresponds across ja/en; `tags` are shared.
- **dates**: `YYYY-MM`. Current role: `end: present`.
- **No fabrication**: never invent companies, dates, roles, or achievements. If unsure, ask.
- **skills.yaml**: keep the `categories[].label.{ja,en}` + `items` (string or `{ja,en}`) shape.
- **Verify after editing**: run `python scripts/validate_data.py` after changing `data/`,
  any `selection.yaml`, or any `companies/*/messages.yaml` — it machine-checks id sync,
  date formats, tags, selection references and the company-message evidence rules, and
  is the fastest way to catch a convention break.

### 企業メッセージ（`companies/<slug>/messages.yaml`）

Records what a company says about itself so later steps (応募書類 / 面接設計) can align
with it **without exaggerating the user**. See `companies/example/messages.yaml`.

- `sources[]`: `id / title / url / accessed (YYYY-MM-DD) / kind (primary|secondary)`.
  A `quote` without a source in this list is a validation error.
- `messages[]`: `id / type / label / quote / source / interpretation / signals /
  evidence / strength` (+ optional `interview_probe`, `note`).
  - `type` ∈ `mission, vision, value, principle, okr, culture, leader_message,
    hiring_message`.
  - `quote` is the company's **verbatim** wording (leave empty rather than paraphrasing);
    the reading goes in `interpretation`.
  - `signals` are language-neutral tags matched against `highlights[].tags`.
  - `evidence` holds **only real highlight ids** from `data/career.*.yaml`.
- **誇張防止ルール（validator が強制）**: `strength: strong` は evidence 2 件以上、
  `partial` は 1 件、`none` は 0 件。応募書類・面接で主張してよい強さの上限がこれで決まる
  — `strong` は断定可、`partial` は限定詞つき、`none` は主張せず `interview_probe`
  （逆質問）に回す。
- Report: `python scripts/company_message_fit.py --company <slug> [--lang ja|en] [--all]`.

## 4. CV generation

Setup (once): `pip install -r requirements.txt`; for PDF/docx also install `pandoc` and
`typst` (see README).

```
# Full CV
python scripts/build_cv.py --lang ja --formats md,pdf,docx

# Tailored (via a selection file)
python scripts/build_cv.py --lang ja --selection cv/output/<slug>/selection.yaml --formats md,pdf,docx
```

`--formats` defaults to `md`; pass `pdf`/`docx` explicitly. If `pandoc`/`typst` are
missing, those formats exit with an install hint (README).

## 5. Workflows (prefer these over ad-hoc work)

Each workflow is a Markdown playbook under `.claude/skills/<name>/SKILL.md`.
**Claude Code** auto-loads them as skills. **Codex**: run the matching
`.codex/prompts/<name>.md` slash command, or just read the SKILL.md and follow it.

- **setup-profile** — first-run personalization. Interview the user and replace the
  sample data in `data/` with their own. **Run this first after cloning.**
- **find-opportunities** — source new roles against `positioning.md` (job boards; LinkedIn
  only if a LinkedIn tool is connected) and return a ranked shortlist. Top of the funnel.
- **tailor-cv** — given a JD or `opportunities/<slug>.md`, pick/reorder highlights into a
  `selection.yaml` and build the CV.
- **vet-opportunity** — 壁打ち analysis of a role/company; writes
  `companies/<slug>/research.md` and `opportunities/<slug>.md`.
- **vet-agent** — research a recruiter/agency and design the 面談; writes `agents/<slug>.md`.
- **prep-interview** — prepare a scheduled interview round: pre-interview brief, the
  企業タイプ × ラウンド種別 playbook
  (`.claude/skills/prep-interview/references/interview-playbooks.md`), interviewer
  research from **public professional info only**, answer skeletons and 逆質問;
  writes `interviews/<slug>-r<N>.md` and records the 振り返り afterwards.
- **align-company-message** — collect the company's MVV / OKR / 行動指針 into
  `companies/<slug>/messages.yaml`, back each with the user's real highlights, and turn
  that into 応募書類の言い回し and 面接での語り口・逆質問 within the `strength` ceiling.

The `companies/example/`, `opportunities/example.md`, and `agents/example.md` files are
**format samples** (fictional) that the vet-* skills use as a reference. Users can delete
them once they have real records.

## 6. Operating rules

- **Tracked**: `*.md` and `selection.yaml` are committed as per-opportunity history.
- **Ignored**: generated PDF/docx are `.gitignore`d — don't try to commit them.
- **Traceability**: company → opportunity → generated CV are linked via front-matter and
  `[[links]]`. Follow this convention for new records.
- **Status vocabulary** (front-matter `status`; don't invent new values — dedupe and
  `scripts/list_pipeline.py` rely on them):
  - `opportunities/*.md`: `検討中 / 応募前 / 書類選考中 / 面接中 / 内定 / 見送り`
  - `agents/*.md`: `接触 / 面談予定 / 継続 / 休眠 / 終了`, optionally with a `（…）`
    qualifier, e.g. `継続（条件付き）`
  - `interviews/*.md`: `予定 / 完了 / 見送り / キャンセル`, with
    `round_type` ∈ `casual / first / technical / manager / executive / hr /
    reference / offer` (validated by `scripts/validate_data.py`)
- **想定質問は蓄積する**: after every round, record what was actually asked in the
  interview record's `asked[]` (`q` + `answered: ok / weak / missed` + note).
  `scripts/interview_brief.py` re-surfaces `weak`/`missed` as 再出題 in later rounds of
  the same opportunity **and** in other opportunities' rounds of the same `round_type`.
  A round whose `asked[]` is empty loses that knowledge for good.
- **Pipeline overview**: run `python scripts/list_pipeline.py` to get opportunities,
  agents (`introduced_companies`), companies (企業メッセージの収集状況), interviews and
  already-seen roles in one shot — use it for dedupe and 重複応募 checks instead of
  re-reading every record.
- **No exaggeration (binding for 応募書類 and 面接)**: aligning with a company's message
  means choosing which real facts to lead with and borrowing its vocabulary — never
  upgrading the user's scope, role or scale. What the user cannot back up becomes a
  question for the interview, not a claim. See the `strength` rules above.
- **Privacy / PII policy (binding for every agent)**:
  - The **upstream template repo must contain no PII**. Only the fictional sample
    persona (Taro Yamada / 山田 太郎) may appear in tracked files. Never commit a real
    person's name, contact details, employer history, or any other personal data to the
    public template. Users copy/fork this repo and fill in their own data in their copy.
  - Once `data/` holds real information, the repo is a **personal instance** and must be
    **private**. Before writing or committing real personal data, check the remote's
    visibility (e.g. `gh repo view --json visibility`, or ask the user). If it is
    public, **stop and have the user make it private first**
    (`gh repo edit --visibility private`) or point the remote elsewhere.
  - Never push real personal data to a public remote, and never include the user's
    personal data in Issues, PRs, or other outward-facing artifacts.
  - **Third parties (interviewers, recruiters)**: records like `interviews/*.md` and
    `agents/*.md` may name people other than the user. Collect **only public,
    professional information** — role and remit, public talks, technical blog posts,
    published professional profiles — always with the source URL, and only as much as
    shapes the conversation. Never collect or store private life, personal social-media
    activity, or sensitive attributes (political/religious belief, health, origin), and
    never attempt exhaustive name matching; leave `要確認` when identification is
    uncertain. Real third-party names must never reach the public template repo — the
    sample records use fictional people.
