#!/usr/bin/env python3
"""Guard the public template against PII slipping into tracked files.

This check is for the **upstream template repo only** (see AGENTS.md §6 —
Privacy / PII policy). Personal copies hold real data by design and must be
private instead of running this check; the CI workflow is therefore gated to
the upstream repository.

Fails (exit 1) when any git-tracked text file contains:
- an email address whose domain is not example.com
- a phone-number-looking string whose local digits are not all zeros
  (the sample persona uses 090-0000-0000 / 03-0000-0000)
- or when the sample persona has been replaced (data/profile.*.yaml no longer
  contain Taro Yamada / 山田 太郎), which means real data was committed.

Usage:
    python scripts/check_pii.py
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Windows consoles often use a legacy codepage that cannot print Japanese.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
ALLOWED_EMAIL_DOMAINS = {"example.com"}
# JP-style phone numbers: 0X(X..)-XXXX-XXXX. Sample data uses all-zero local parts.
PHONE_RE = re.compile(r"\b0\d{1,4}-\d{1,4}-\d{3,4}\b")

SAMPLE_PERSONA = {
    "data/profile.ja.yaml": "山田 太郎",
    "data/profile.en.yaml": "Taro Yamada",
}

SKIP_SUFFIXES = {".pdf", ".docx", ".png", ".jpg", ".ico"}


def tracked_files() -> list[Path]:
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, check=True,
                         capture_output=True, text=True).stdout
    return [ROOT / line for line in out.splitlines() if line]


def main() -> None:
    problems: list[str] = []

    for path in tracked_files():
        if path.suffix.lower() in SKIP_SUFFIXES or not path.exists():
            continue
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8", errors="ignore")

        for m in EMAIL_RE.finditer(text):
            domain = m.group(0).rsplit("@", 1)[1].lower()
            if domain not in ALLOWED_EMAIL_DOMAINS:
                problems.append(f"{rel}: email address '{m.group(0)}'")

        for m in PHONE_RE.finditer(text):
            local_digits = m.group(0).split("-", 1)[1]
            if any(d != "0" for d in local_digits if d.isdigit()):
                problems.append(f"{rel}: phone-like number '{m.group(0)}'")

    for rel, marker in SAMPLE_PERSONA.items():
        path = ROOT / rel
        if path.exists() and marker not in path.read_text(encoding="utf-8"):
            problems.append(
                f"{rel}: sample persona '{marker}' is gone — real data must not "
                "be committed to the public template (AGENTS.md §6)")

    if problems:
        for p in problems:
            print(f"  ! {p}", file=sys.stderr)
        sys.exit(f"check_pii: {len(problems)} possible PII finding(s). "
                 "The public template must stay PII-free.")
    print("check_pii: OK — no PII patterns found in tracked files.")


if __name__ == "__main__":
    main()
