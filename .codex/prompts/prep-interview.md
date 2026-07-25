Follow the procedure in `.claude/skills/prep-interview/SKILL.md` (ignore its YAML
frontmatter). Run `python scripts/interview_brief.py --opportunity <slug> --round <N>`
first, then combine the 企業タイプ × round_type playbook in
`.claude/skills/prep-interview/references/interview-playbooks.md` (一般論として扱う) with
the company's messages, my submitted CV and the opportunity's open questions, and write
`interviews/<slug>-r<N>.md`. 面接官のリサーチは**公開された職務上の情報のみ**（私生活・私的
SNS・センシティブ属性は扱わない）、出典 URL を残し、同定できなければ要確認のままにすること。
回答骨子は `data/career.*.yaml` の事実の範囲内。裏付けの無い項目は主張せず逆質問に回す。

面接の案内 / 案件 / ラウンド:
$ARGUMENTS
