Follow the procedure in `.claude/skills/vet-opportunity/SKILL.md` (ignore its YAML
frontmatter). Research the company with your web tools, confirm the posting is still live
and which window actually accepts an application (put that in `jd_url`), assess fit
against `data/positioning.md` and my career data — plus the 足切り conditions in
`data/retirement-plan.md` if that file exists — surface risks, and write
`companies/<slug>/research.md` and `opportunities/<slug>.md`. Mark unknowns as 要確認,
and record both sides when sources disagree. If the role ends up 見送り, keep the reason
out of `status`: fill `outcome` (未応募 / 不採用 / 辞退), `closed_reason` and
`closed_date`. Then run `python scripts/validate_data.py`.

Tooling note: the SKILL's step 1 starts from a **HERP Career MCP** (`get_company` gives
funding history / number-of-employees history / directors). Use it only if that tool is
connected on your side; otherwise research from the open web and mark the gaps 要確認.

案件 / JD:
$ARGUMENTS
