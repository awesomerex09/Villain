#!/usr/bin/env python3
"""
chat_parser.py — Universal Chat Log Parser
Self-Mirror: Digital Twin System

Parses LINE / Messenger / iMessage exported chat logs into a standardized
(Timestamp, Sender, Message) format for downstream analysis.
Supports single files or entire directories containing multiple chat files.

Usage:
    python3 tools/chat_parser.py --file path/to/chat.txt --target "Villain" --output /tmp/parsed.txt
    python3 tools/chat_parser.py --dir raw_chats/ --target "Villain" --output /tmp/parsed.txt
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
    first_500 = content[:1000]

    # LINE: "[2024/01/15 14:30] UserName: Message" or "2024/01/15 14:30\tUserName\tMessage"
    if re.search(r'\[\d{4}/\d{2}/\d{2} \d{2}:\d{2}\]', first_500) or re.search(r'\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}\t.+?\t', first_500):
        return 'line'

    # Messenger: "UserName\nMMM DD, YYYY HH:MM\nMessage"
    if re.search(r'\w+\n[A-Z][a-z]+ \d+, \d{4} \d+:\d+[AP]M', first_500):
        return 'messenger'

    # iMessage (macOS export): "Me / Them  HH:MM  Message"
    if re.search(r'^(Me|.+?)\s{2,}\d{1,2}:\d{2}', first_500, re.MULTILINE):
        return 'imessage'

    # Generic: "YYYY-MM-DD HH:MM:SS Sender: Message" or "[YYYY-MM-DD HH:MM:SS] Sender: Message"
    if re.search(r'\[?\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}(:\d{2})?\]?\s+.+?:', first_500):
        return 'generic'

    return 'generic'


# ── Format parsers ────────────────────────────────────────────────────────────

def parse_line(content: str) -> list[dict]:
    """Parse LINE exported chat log."""
    records = []
    
    # Format 1: [2024/01/15 14:30] Sender: Message
    pattern1 = re.compile(r'\[(\d{4}/\d{2}/\d{2} \d{2}:\d{2})\]\s+(.+?):\s+(.+)')
    # Format 2: 2024/01/15 14:30\tSender\tMessage
    pattern2 = re.compile(r'(\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2})\t([^\t]+)\t(.+)')
    # Format 3: 2024.01.15 14:30 Sender: Message
    pattern3 = re.compile(r'(\d{4}[./-]\d{2}[./-]\d{2}\s+\d{2}:\d{2})\s+([^:\n]+):\s+(.+)')

    for line in content.splitlines():
        line_str = line.strip()
        if not line_str:
            continue
            
        m1 = pattern1.match(line_str)
        if m1:
            records.append({'timestamp': m1.group(1), 'sender': m1.group(2).strip(), 'message': m1.group(3).strip()})
            continue
            
        m2 = pattern2.match(line_str)
        if m2:
            records.append({'timestamp': m2.group(1), 'sender': m2.group(2).strip(), 'message': m2.group(3).strip()})
            continue

        m3 = pattern3.match(line_str)
        if m3:
            records.append({'timestamp': m3.group(1), 'sender': m3.group(2).strip(), 'message': m3.group(3).strip()})

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
        r'\[?(\d{4}[./-]\d{2}[./-]\d{2}\s+\d{2}:\d{2}(?::\d{2})?)\]?\s+([^:\n]+):\s+(.+)'
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


def parse_single_file(file_path: Path) -> list[dict]:
    """Parse a single text file into records."""
    content = None
    for enc in ['utf-8-sig', 'utf-16', 'utf-8', 'cp950', 'big5']:
        try:
            content = file_path.read_text(encoding=enc)
            break
        except UnicodeDecodeError:
            continue
    
    if content is None:
        try:
            content = file_path.read_text(encoding='utf-8', errors='replace')
        except Exception as e:
            print(f"[WARN] Failed to read {file_path}: {e}", file=sys.stderr)
            return []

    fmt = detect_format(content)
    parser = PARSERS.get(fmt, parse_generic)
    records = parser(content)
    
    # Fallback to generic if specific parser found nothing
    if not records and fmt != 'generic':
        records = parse_generic(content)
        
    return records


# ── Normalizer ────────────────────────────────────────────────────────────────

def normalize(records: list[dict], target: Optional[str] = None) -> list[dict]:
    system_patterns = [
        re.compile(r'^\[.*joined.*\]$', re.I),
        re.compile(r'^\[.*left.*\]$', re.I),
        re.compile(r'^\[Sticker\]$'),
        re.compile(r'^\[Image\]$'),
        re.compile(r'^\[File\]$'),
        re.compile(r'^\[貼圖\]$'),
        re.compile(r'^\[照片\]$'),
        re.compile(r'^\[檔案\]$'),
        re.compile(r'^\[語音訊息\]$'),
        re.compile(r'^通話時間.*$', re.I),
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
  # 單一檔案
  python3 tools/chat_parser.py --file chat.txt --target "Villain"
  
  # 多個對話紀錄（指定資料夾）
  python3 tools/chat_parser.py --dir raw_chats/ --target "Villain" --format json --output out.json
        """
    )
    parser.add_argument('--file', default=None, help='Path to single chat log file')
    parser.add_argument('--dir', default=None, help='Path to directory containing multiple chat log files')
    parser.add_argument('--target', default=None, help='Target user name to mark (optional)')
    parser.add_argument('--format', choices=['json', 'text'], default='text', help='Output format')
    parser.add_argument('--output', default=None, help='Output file path (default: stdout)')
    args = parser.parse_args()

    if not args.file and not args.dir:
        print("[ERROR] You must provide either --file or --dir", file=sys.stderr)
        sys.exit(1)

    all_records = []

    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"[ERROR] File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        all_records.extend(parse_single_file(file_path))
    
    if args.dir:
        dir_path = Path(args.dir)
        if not dir_path.exists() or not dir_path.is_dir():
            print(f"[ERROR] Directory not found: {args.dir}", file=sys.stderr)
            sys.exit(1)
        
        # 遍歷資料夾中的所有 .txt, .log, .csv 檔案
        files = sorted(list(dir_path.glob('*.txt')) + list(dir_path.glob('*.log')) + list(dir_path.glob('*.csv')))
        print(f"[INFO] Found {len(files)} chat files in {args.dir}", file=sys.stderr)
        for f in files:
            recs = parse_single_file(f)
            print(f"[INFO] Parsed {len(recs)} messages from {f.name}", file=sys.stderr)
            all_records.extend(recs)

    all_records = normalize(all_records, target=args.target)
    print(f"[INFO] Total valid messages parsed: {len(all_records)}", file=sys.stderr)

    if args.target:
        target_count = sum(1 for r in all_records if r.get('is_target'))
        print(f"[INFO] Target '{args.target}' messages: {target_count}", file=sys.stderr)

    # Output
    if args.format == 'json':
        output = json.dumps(all_records, ensure_ascii=False, indent=2)
    else:
        lines = []
        for r in all_records:
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
