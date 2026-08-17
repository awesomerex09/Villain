#!/usr/bin/env python3
"""
chat_parser.py — Universal Chat Log Parser
Self-Mirror: Digital Twin System

Parses LINE / Messenger / iMessage exported chat logs into a standardized
(Timestamp, Sender, Message) format for downstream analysis.

Usage:
    python3 tools/chat_parser.py --file path/to/chat.txt --target "Villain" --output /tmp/parsed.txt
    python3 tools/chat_parser.py --file path/to/chat.txt --target "Villain" --format json
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


# ── Format detectors ─────────────────────────────────────────────────────────

def detect_format(content: str) -> str:
    """Auto-detect chat export format."""
    first_500 = content[:500]

    # LINE: "[2024/01/15 14:30] UserName: Message"
    if re.search(r'\[\d{4}/\d{2}/\d{2} \d{2}:\d{2}\]', first_500):
        return 'line'

    # Messenger: "UserName\nMMM DD, YYYY HH:MM\nMessage"
    if re.search(r'\w+\n[A-Z][a-z]+ \d+, \d{4} \d+:\d+[AP]M', first_500):
        return 'messenger'

    # iMessage (macOS export): "Me / Them  HH:MM  Message"
    if re.search(r'^(Me|.+?)\s{2,}\d{1,2}:\d{2}', first_500, re.MULTILINE):
        return 'imessage'

    # Generic: "YYYY-MM-DD HH:MM:SS Sender: Message"
    if re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} .+?:', first_500):
        return 'generic'

    return 'unknown'


# ── Format parsers ────────────────────────────────────────────────────────────

def parse_line(content: str) -> list[dict]:
    """Parse LINE exported chat log."""
    records = []
    pattern = re.compile(
        r'\[(\d{4}/\d{2}/\d{2} \d{2}:\d{2})\]\s+(.+?):\s+(.+)'
    )
    for line in content.splitlines():
        m = pattern.match(line.strip())
        if m:
            ts, sender, message = m.group(1), m.group(2), m.group(3)
            records.append({
                'timestamp': ts,
                'sender': sender.strip(),
                'message': message.strip(),
            })
    return records


def parse_messenger(content: str) -> list[dict]:
    """Parse Facebook Messenger exported chat log."""
    records = []
    lines = content.splitlines()
    i = 0
    ts_pattern = re.compile(r'[A-Z][a-z]+ \d+, \d{4} \d+:\d+[AP]M')

    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        # Check if next line is a timestamp
        if i + 1 < len(lines) and ts_pattern.match(lines[i + 1].strip()):
            sender = line
            ts = lines[i + 1].strip()
            msg_parts = []
            i += 2
            while i < len(lines) and lines[i].strip() and not ts_pattern.match(lines[i].strip()):
                msg_parts.append(lines[i].strip())
                i += 1
            if msg_parts:
                records.append({
                    'timestamp': ts,
                    'sender': sender,
                    'message': ' '.join(msg_parts),
                })
        else:
            i += 1

    return records


def parse_generic(content: str) -> list[dict]:
    """Parse generic 'YYYY-MM-DD HH:MM:SS Sender: Message' format."""
    records = []
    pattern = re.compile(
        r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+(.+?):\s+(.+)'
    )
    for line in content.splitlines():
        m = pattern.match(line.strip())
        if m:
            records.append({
                'timestamp': m.group(1),
                'sender': m.group(2).strip(),
                'message': m.group(3).strip(),
            })
    return records


PARSERS = {
    'line': parse_line,
    'messenger': parse_messenger,
    'generic': parse_generic,
}


# ── Normalizer ────────────────────────────────────────────────────────────────

def normalize(records: list[dict], target: Optional[str] = None) -> list[dict]:
    """
    Normalize records. If target is specified, mark records with is_target flag.
    Filter out system messages and empty messages.
    """
    system_patterns = [
        re.compile(r'^\[.*joined.*\]$', re.I),
        re.compile(r'^\[.*left.*\]$', re.I),
        re.compile(r'^\[Sticker\]$'),
        re.compile(r'^\[Image\]$'),
        re.compile(r'^\[File\]$'),
    ]

    normalized = []
    for rec in records:
        msg = rec['message'].strip()
        if not msg:
            continue
        if any(p.match(msg) for p in system_patterns):
            continue

        rec['is_target'] = (
            target is not None and
            target.lower() in rec['sender'].lower()
        )
        normalized.append(rec)

    return normalized


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Self-Mirror: Universal Chat Log Parser',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 tools/chat_parser.py --file chat.txt --target "Villain"
  python3 tools/chat_parser.py --file chat.txt --target "Villain" --format json --output out.json
  python3 tools/chat_parser.py --file chat.txt --detect-only
        """
    )
    parser.add_argument('--file', required=True, help='Path to chat log file')
    parser.add_argument('--target', default=None, help='Target user name to mark (optional)')
    parser.add_argument('--format', choices=['json', 'text'], default='text', help='Output format')
    parser.add_argument('--output', default=None, help='Output file path (default: stdout)')
    parser.add_argument('--detect-only', action='store_true', help='Only detect format, do not parse')
    args = parser.parse_args()

    # Read file
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"[ERROR] File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    content = file_path.read_text(encoding='utf-8', errors='replace')

    # Detect format
    fmt = detect_format(content)
    print(f"[INFO] Detected format: {fmt}", file=sys.stderr)

    if args.detect_only:
        print(fmt)
        return

    if fmt not in PARSERS:
        print(f"[WARN] Unknown format. Falling back to generic parser.", file=sys.stderr)
        fmt = 'generic'

    # Parse
    records = PARSERS[fmt](content)
    records = normalize(records, target=args.target)

    print(f"[INFO] Parsed {len(records)} messages.", file=sys.stderr)

    if args.target:
        target_count = sum(1 for r in records if r['is_target'])
        print(f"[INFO] Target '{args.target}' messages: {target_count}", file=sys.stderr)

    # Output
    if args.format == 'json':
        output = json.dumps(records, ensure_ascii=False, indent=2)
    else:
        lines = []
        for r in records:
            marker = '>>> ' if r.get('is_target') else '    '
            lines.append(f"{marker}[{r['timestamp']}] {r['sender']}: {r['message']}")
        output = '\n'.join(lines)

    if args.output:
        Path(args.output).write_text(output, encoding='utf-8')
        print(f"[INFO] Output written to: {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == '__main__':
    main()
