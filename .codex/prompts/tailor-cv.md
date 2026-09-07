Follow the procedure in `.claude/skills/tailor-cv/SKILL.md` (ignore its YAML
frontmatter). Build a job-tailored CV by selecting and reordering existing highlights
from `data/` — never invent facts. Write `cv/output/<slug>/selection.yaml`
(`summary_override` / `self_pr_override` adjust wording only, never facts) and run
`python scripts/validate_data.py --selection …` then `python scripts/build_cv.py`.
志望動機 (`motivation.ja.md`) や応募フォームの回答案 (`application-form.md`) は
求めたときだけ作る。応募そのものは私が行う。

JD / opportunity to tailor for:
$ARGUMENTS
