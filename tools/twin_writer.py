#!/usr/bin/env python3
"""
twin_writer.py — Digital Twin File Manager
Self-Mirror: Digital Twin System

Writes, reads, and merges Digital Twin profile files in twin_profile/.

Actions:
    write   — Write a new profile file (overwrites)
    merge   — Merge new content into existing file (append sections, preserve old)
    read    — Print a profile file
    list    — List all profile files with metadata

Usage:
    python3 tools/twin_writer.py --action write --name Villain --section core --content "..."
    python3 tools/twin_writer.py --action write --name Villain --section core --file core.md
    python3 tools/twin_writer.py --action merge --name Villain --section core --file new_core.md
    python3 tools/twin_writer.py --action read --name Villain --section style
    python3 tools/twin_writer.py --action list
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


# ── Config ────────────────────────────────────────────────────────────────────

TWIN_PROFILE_DIR = Path(__file__).parent.parent / 'twin_profile'
SECTION_MAP = {
    'core': '{name}_core.md',
    'style': '{name}_style.md',
    'report': 'objective_report.md',
}


# ── Utilities ─────────────────────────────────────────────────────────────────

def get_profile_path(name: str, section: str) -> Path:
    if section not in SECTION_MAP:
        raise ValueError(f"Unknown section '{section}'. Valid: {list(SECTION_MAP.keys())}")
    filename = SECTION_MAP[section].format(name=name)
    return TWIN_PROFILE_DIR / filename


def ensure_twin_dir():
    TWIN_PROFILE_DIR.mkdir(parents=True, exist_ok=True)


def timestamp_header(name: str, section: str) -> str:
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return f"<!-- generated_at: {now} | name: {name} | section: {section} -->\n\n"


# ── Actions ───────────────────────────────────────────────────────────────────

def action_write(name: str, section: str, content: str):
    ensure_twin_dir()
    path = get_profile_path(name, section)
    full_content = timestamp_header(name, section) + content
    path.write_text(full_content, encoding='utf-8')
    print(f"[OK] Written: {path}", file=sys.stderr)


def action_merge(name: str, section: str, new_content: str):
    """
    Merge new content into existing file.
    Strategy: Append new content as a versioned section.
    Preserves all existing content — never overwrites old conclusions.
    """
    ensure_twin_dir()
    path = get_profile_path(name, section)
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if path.exists():
        existing = path.read_text(encoding='utf-8')
        merged = (
            existing.rstrip() +
            f"\n\n---\n\n<!-- merge_update: {now} -->\n\n" +
            new_content
        )
    else:
        merged = timestamp_header(name, section) + new_content

    path.write_text(merged, encoding='utf-8')
    print(f"[OK] Merged into: {path}", file=sys.stderr)


def action_read(name: str, section: str):
    path = get_profile_path(name, section)
    if not path.exists():
        print(f"[ERROR] Profile not found: {path}", file=sys.stderr)
        sys.exit(1)
    print(path.read_text(encoding='utf-8'))


def action_list():
    if not TWIN_PROFILE_DIR.exists():
        print("[INFO] twin_profile/ does not exist yet. Run build_twin.py to create profiles.")
        return

    files = sorted(TWIN_PROFILE_DIR.glob('*.md'))
    if not files:
        print("[INFO] No profile files found in twin_profile/.")
        return

    print(f"{'File':<35} {'Size':>8}  {'Modified'}")
    print('-' * 65)
    for f in files:
        stat = f.stat()
        size = f"{stat.st_size:,} B"
        mtime = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
        print(f"{f.name:<35} {size:>8}  {mtime}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Self-Mirror: Digital Twin File Manager',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Actions:
  write   Write new content to a profile file (overwrites)
  merge   Merge new content into existing profile (preserves history)
  read    Print a profile file
  list    List all profile files

Examples:
  python3 tools/twin_writer.py --action list
  python3 tools/twin_writer.py --action read --name Villain --section core
  python3 tools/twin_writer.py --action write --name Villain --section core --file core.md
  python3 tools/twin_writer.py --action merge --name Villain --section style --file new_style.md
        """
    )
    parser.add_argument('--action', required=True,
                        choices=['write', 'merge', 'read', 'list'],
                        help='Action to perform')
    parser.add_argument('--name', default='Villain', help='Profile name (default: Villain)')
    parser.add_argument('--section', choices=['core', 'style', 'report'],
                        help='Profile section (required for write/merge/read)')
    parser.add_argument('--content', default=None, help='Content string (for write/merge)')
    parser.add_argument('--file', default=None, help='Content file path (for write/merge)')
    args = parser.parse_args()

    if args.action == 'list':
        action_list()
        return

    if not args.section:
        print("[ERROR] --section is required for write/merge/read.", file=sys.stderr)
        sys.exit(1)

    if args.action in ('write', 'merge'):
        if args.file:
            content = Path(args.file).read_text(encoding='utf-8')
        elif args.content:
            content = args.content
        else:
            # Read from stdin
            print("[INFO] Reading content from stdin...", file=sys.stderr)
            content = sys.stdin.read()

        if args.action == 'write':
            action_write(args.name, args.section, content)
        else:
            action_merge(args.name, args.section, content)

    elif args.action == 'read':
        action_read(args.name, args.section)


if __name__ == '__main__':
    main()
