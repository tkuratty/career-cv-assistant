Follow the procedure in `.claude/skills/align-company-message/SKILL.md` (ignore its
YAML frontmatter). Collect the company's own messaging (MVV / OKR / 行動指針 /
カルチャー / 経営・採用メッセージ) with primary sources into
`companies/<slug>/messages.yaml`, map each message to my real highlight ids in
`data/career.*.yaml` as evidence, and set `strength` from the evidence count
(strong ≥2 / partial 1 / none 0). Then run `python scripts/validate_data.py` and
`python scripts/company_message_fit.py --company <slug>`, and give me 応募書類の
言い回し候補と面接での語り口・逆質問 — strength の上限を守り、裏付けの無い項目は
主張せず逆質問に回すこと。引用も実績も捏造しない。

企業 / JD:
$ARGUMENTS
