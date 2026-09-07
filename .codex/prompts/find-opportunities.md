Follow the procedure in `.claude/skills/find-opportunities/SKILL.md` (ignore its YAML
frontmatter). Source and rank job openings against `data/positioning.md` — and the 足切り
conditions in `data/retirement-plan.md` if that file exists — using your web-search tools,
dedupe against existing records and `opportunities/seen.yaml`, and return a
positioning-ranked shortlist with clean links. Do not apply or message anyone. If you
append to `seen.yaml`, quote any URL containing `?` and then run
`python scripts/validate_data.py`.

Tooling note: the SKILL describes a **HERP Career MCP** and a **LinkedIn MCP**. Use them
only if those tools are actually connected on your side; otherwise skip them and fall
back to WebFetch/WebSearch against the boards listed in the SKILL. Never call
`update_user_career_preferences` — it writes to the user's live HERP profile.

Focus / constraints for this search:
$ARGUMENTS
