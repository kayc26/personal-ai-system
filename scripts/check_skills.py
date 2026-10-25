#!/usr/bin/env python3
"""Check that the skills loaded in Claude match skills/ in this repo.

The repo is the source of truth. Claude.ai holds a copy you upload by hand, so
the two can drift. Run this from a Claude session that has this repo cloned:

    python3 scripts/check_skills.py              # compare against /mnt/skills/user
    python3 scripts/check_skills.py --package    # also zip each out-of-date skill

Each zip in dist/ is ready to upload in claude.ai's skill settings, replacing
the loaded version.
"""
import argparse
import filecmp
import shutil
import sys
from pathlib import Path

REPO_SKILLS = Path(__file__).resolve().parent.parent / "skills"
DIST = REPO_SKILLS.parent / "dist"


def files(root: Path) -> set[str]:
    return {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()}


def differs(a: Path, b: Path) -> bool:
    fa, fb = files(a), files(b)
    if fa != fb:
        return True
    return any(not filecmp.cmp(a / f, b / f, shallow=False) for f in fa)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--loaded", default="/mnt/skills/user",
                    help="folder holding the skills Claude has loaded")
    ap.add_argument("--package", action="store_true",
                    help="zip each out-of-date skill into dist/ for upload")
    args = ap.parse_args()

    loaded = Path(args.loaded)
    if not loaded.is_dir():
        print(f"No loaded skills at {loaded}. Run this inside a Claude session.")
        return 2

    stale = []
    for skill in sorted(p for p in REPO_SKILLS.iterdir() if p.is_dir()):
        target = loaded / skill.name
        if not target.is_dir():
            status = "NOT LOADED"
        elif differs(skill, target):
            status = "OUT OF DATE"
        else:
            status = "ok"
        print(f"{status:12} {skill.name}")
        if status != "ok":
            stale.append(skill)

    if not stale:
        print("\nAll loaded skills match the repo.")
        return 0

    print(f"\n{len(stale)} skill(s) need uploading.")
    if args.package:
        DIST.mkdir(exist_ok=True)
        for skill in stale:
            zip_base = DIST / skill.name
            shutil.make_archive(str(zip_base), "zip", REPO_SKILLS, skill.name)
            print(f"  dist/{skill.name}.zip")
    return 1


if __name__ == "__main__":
    sys.exit(main())
