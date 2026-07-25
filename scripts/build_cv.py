#!/usr/bin/env python3
"""Build a CV (Markdown / PDF / docx) from the structured data in data/.

Single source of truth lives in data/*.yaml. An optional selection file picks and
reorders which positions / highlights to include and can override the summary,
so a CV can be tailored per opportunity without duplicating career data.

Examples
--------
    # Full CV, all formats, Japanese
    python scripts/build_cv.py --lang ja --formats md,pdf,docx

    # Tailored CV driven by a selection file
    python scripts/build_cv.py --lang en \
        --selection cv/output/acme-senior/selection.yaml --formats md,pdf

Toolchain: Pandoc (docx + pdf) with Typst as the pdf engine. See README.md.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
TEMPLATES = ROOT / "cv" / "templates"
OUTPUT = ROOT / "cv" / "output"

# lang -> (markdown jinja template, typst pdf template)
TEMPLATE_MAP = {
    "ja": ("shokumu.md.j2", "shokumu.typ"),
    "en": ("resume.md.j2", "resume.typ"),
}


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def load_yaml_optional(path: Path) -> dict:
    """Like load_yaml but returns {} if the file does not exist."""
    return load_yaml(path) if path.exists() else {}


def format_education(items: list[dict], lang: str) -> list[str]:
    lines = []
    for e in items:
        school, field, year = e.get("school", ""), e.get("field"), e.get("year")
        if lang == "ja":
            head = f"{year}　" if year else ""
            lines.append(f"{head}{school}" + (f"　{field}" if field else ""))
        else:
            tail = f" — {field}" if field else ""
            lines.append(f"{school}{tail}" + (f", {year}" if year else ""))
    return lines


def format_certifications(items: list[dict], lang: str) -> list[str]:
    lp, rp = ("（", "）") if lang == "ja" else (" (", ")")
    lines = []
    for c in items:
        name, date = c.get("name", ""), c.get("date")
        lines.append(f"{name}{lp}{date}{rp}" if date else name)
    return lines


def format_languages(items: list[dict]) -> list[str]:
    return [f"{x.get('name', '')}: {x.get('level', '')}" for x in items]


def resolve_skills(skills: dict, lang: str) -> list[dict]:
    """Flatten skills.yaml into [{label, items:[str]}] for one language."""
    out = []
    for cat in skills.get("categories", []):
        label = cat.get("label", {}).get(lang, cat.get("key", ""))
        items = []
        for item in cat.get("items", []):
            items.append(item[lang] if isinstance(item, dict) else str(item))
        out.append({"label": label, "items": items})
    return out


def select_positions(all_positions: list[dict], selection: dict) -> list[dict]:
    """Filter/reorder positions and highlights per the selection file.

    If selection has no 'positions' key, return everything in file order.
    """
    sel = selection.get("positions")
    if not sel:
        return all_positions

    by_id = {p["id"]: p for p in all_positions}
    result = []
    for entry in sel:
        pos = by_id.get(entry["id"])
        if pos is None:
            print(f"  ! selection references unknown position id: {entry['id']}",
                  file=sys.stderr)
            continue
        pos = dict(pos)  # shallow copy so we don't mutate source data
        hl_ids = entry.get("highlights")
        if hl_ids:
            hl_by_id = {h["id"]: h for h in pos.get("highlights", [])}
            picked = []
            for hid in hl_ids:
                if hid in hl_by_id:
                    picked.append(hl_by_id[hid])
                else:
                    print(f"  ! unknown highlight id: {hid} (in {entry['id']})",
                          file=sys.stderr)
            pos["highlights"] = picked
        result.append(pos)
    return result


def collapse_blank_lines(text: str) -> str:
    """Jinja loops leave ragged blank lines; collapse 2+ into a single one."""
    return re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"


def build_profile_view(profile: dict) -> dict:
    """Precompute header strings so templates avoid inline conditionals
    (which fight Jinja's trim_blocks whitespace handling)."""
    name_line = profile.get("name", "")
    if profile.get("name_kana"):
        name_line += f"（{profile['name_kana']}）"
    contact = [profile.get("email"), profile.get("phone"), profile.get("location")]
    links = (profile.get("links") or {}).values()
    return {
        **profile,
        "name_line": name_line,
        "contact_line": " / ".join(x for x in contact if x),
        "links_line": " / ".join(str(v) for v in links),
    }


def render_markdown(lang: str, selection: dict) -> str:
    profile = load_yaml(DATA / f"profile.{lang}.yaml")
    career = load_yaml(DATA / f"career.{lang}.yaml")
    skills = load_yaml(DATA / "skills.yaml")
    education = load_yaml_optional(DATA / f"education.{lang}.yaml")
    certifications = load_yaml_optional(DATA / f"certifications.{lang}.yaml")

    context = {
        "profile": build_profile_view(profile),
        "summary": selection.get("summary_override") or profile.get("summary", ""),
        "positions": select_positions(career.get("positions", []), selection),
        "skills": resolve_skills(skills, lang),
        "education_lines": format_education(education.get("items", []), lang),
        "cert_lines": format_certifications(certifications.get("items", []), lang),
        "language_lines": format_languages(profile.get("languages", [])),
        "lang": lang,
    }

    md_template = TEMPLATE_MAP[lang][0]
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    rendered = env.get_template(md_template).render(**context)
    return collapse_blank_lines(rendered)


def run_pandoc(args: list[str]) -> None:
    if shutil.which("pandoc") is None:
        sys.exit("ERROR: 'pandoc' not found. Install it (see README.md) to build pdf/docx.")
    subprocess.run(["pandoc", *args], check=True)


def build_pdf(md_path: Path, pdf_path: Path, lang: str) -> None:
    if shutil.which("typst") is None:
        sys.exit("ERROR: 'typst' not found. Install it (see README.md) to build pdf.")
    typst_template = TEMPLATES / TEMPLATE_MAP[lang][1]
    run_pandoc([
        str(md_path), "-o", str(pdf_path),
        "--pdf-engine=typst", "--template", str(typst_template),
    ])


def build_docx(md_path: Path, docx_path: Path) -> None:
    args = [str(md_path), "-o", str(docx_path)]
    reference = TEMPLATES / "reference.docx"
    if reference.exists():
        args += ["--reference-doc", str(reference)]
    run_pandoc(args)


def main() -> None:
    ap = argparse.ArgumentParser(description="Build a CV from structured data.")
    ap.add_argument("--lang", choices=["ja", "en"], required=True)
    ap.add_argument("--selection", type=Path,
                    help="Optional selection YAML (picks/reorders positions & highlights).")
    ap.add_argument("--formats", default="md",
                    help="Comma-separated: md,pdf,docx (default: md).")
    ap.add_argument("--name",
                    help="Output slug (default: selection 'name', else 'full').")
    ap.add_argument("--out", type=Path,
                    help="Output directory (default: cv/output/<name>).")
    args = ap.parse_args()

    selection = load_yaml(args.selection) if args.selection else {}
    name = args.name or selection.get("name") or "full"
    out_dir = args.out or (OUTPUT / name)
    out_dir.mkdir(parents=True, exist_ok=True)

    formats = [f.strip() for f in args.formats.split(",") if f.strip()]
    unknown = set(formats) - {"md", "pdf", "docx"}
    if unknown:
        sys.exit(f"ERROR: unknown format(s): {', '.join(sorted(unknown))}")

    markdown = render_markdown(args.lang, selection)
    md_path = out_dir / f"{name}.{args.lang}.md"
    md_path.write_text(markdown, encoding="utf-8")
    print(f"  wrote {md_path.relative_to(ROOT)}")

    if "pdf" in formats:
        pdf_path = out_dir / f"{name}.{args.lang}.pdf"
        build_pdf(md_path, pdf_path, args.lang)
        print(f"  wrote {pdf_path.relative_to(ROOT)}")

    if "docx" in formats:
        docx_path = out_dir / f"{name}.{args.lang}.docx"
        build_docx(md_path, docx_path)
        print(f"  wrote {docx_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
