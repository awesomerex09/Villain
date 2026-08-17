#!/usr/bin/env python3
"""
text_cleaner.py — Noise Filter & De-identifier
Self-Mirror: Digital Twin System

Cleans normalized chat/log records:
  - Removes system messages, join/leave notifications
  - Filters emoji-only messages (configurable)
  - De-identifies third-party sender names → [PERSON_A], [PERSON_B], ...
  - Removes URLs, file references, and other noise

Usage:
    python3 tools/text_cleaner.py --file parsed.json --target "Villain" --output cleaned.json
    python3 tools/text_cleaner.py --file parsed.json --target "Villain" --deidentify --output cleaned.json
"""

import argparse
import json
import re
import sys
from pathlib import Path


# ── Noise patterns ────────────────────────────────────────────────────────────

SYSTEM_MESSAGE_PATTERNS = [
    re.compile(r'^\[Sticker\]$'),
    re.compile(r'^\[Image\]$'),
    re.compile(r'^\[File\]$'),
    re.compile(r'^\[Video\]$'),
    re.compile(r'^\[Voice\]$'),
    re.compile(r'^\[GIF\]$'),
    re.compile(r'^.+ joined the group\.$', re.I),
    re.compile(r'^.+ left the group\.$', re.I),
    re.compile(r'^.+ changed the group name\.$', re.I),
    re.compile(r'^You unsent a message\.$', re.I),
    re.compile(r'^\[Recalled a message\]$', re.I),
    re.compile(r'^$'),
]

EMOJI_ONLY_PATTERN = re.compile(
    r'^[\U0001F000-\U0001FFFF\U00002600-\U000027FF\U0001F900-\U0001F9FF'
    r'\U00002000-\U000023FF\u200d\ufe0f\s]+$'
)

URL_PATTERN = re.compile(r'https?://\S+|www\.\S+')


# ── Cleaner functions ─────────────────────────────────────────────────────────

def is_system_message(message: str) -> bool:
    return any(p.match(message.strip()) for p in SYSTEM_MESSAGE_PATTERNS)


def is_emoji_only(message: str) -> bool:
    return bool(EMOJI_ONLY_PATTERN.match(message.strip()))


def remove_urls(message: str, placeholder: str = '[URL]') -> str:
    return URL_PATTERN.sub(placeholder, message)


def build_deidentify_map(records: list[dict], target: str) -> dict[str, str]:
    """Build a mapping from sender names (excluding target) → [PERSON_A], [PERSON_B], ..."""
    senders = set()
    for r in records:
        sender = r.get('sender', '')
        if target.lower() not in sender.lower():
            senders.add(sender)

    mapping = {}
    for i, name in enumerate(sorted(senders)):
        label = f"[PERSON_{chr(65 + i)}]"  # A, B, C, ...
        mapping[name] = label

    return mapping


def clean_records(
    records: list[dict],
    target: str,
    remove_emoji_only: bool = True,
    strip_urls: bool = True,
    deidentify: bool = False,
) -> tuple[list[dict], dict]:
    """
    Clean and optionally de-identify records.

    Returns:
        (cleaned_records, deidentify_map)
    """
    deidentify_map = {}
    if deidentify:
        deidentify_map = build_deidentify_map(records, target)

    cleaned = []
    stats = {'total': len(records), 'removed_system': 0, 'removed_emoji': 0, 'kept': 0}

    for rec in records:
        msg = rec.get('message', '').strip()

        # Filter system messages
        if is_system_message(msg):
            stats['removed_system'] += 1
            continue

        # Filter emoji-only
        if remove_emoji_only and is_emoji_only(msg):
            stats['removed_emoji'] += 1
            continue

        # Strip URLs
        if strip_urls:
            msg = remove_urls(msg)

        # De-identify sender
        sender = rec.get('sender', '')
        if deidentify and sender in deidentify_map:
            sender = deidentify_map[sender]

        cleaned.append({**rec, 'message': msg, 'sender': sender})
        stats['kept'] += 1

    print(
        f"[INFO] Cleaned: {stats['total']} input → "
        f"{stats['removed_system']} system removed, "
        f"{stats['removed_emoji']} emoji-only removed, "
        f"{stats['kept']} kept.",
        file=sys.stderr
    )

    return cleaned, deidentify_map


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Self-Mirror: Text Cleaner & De-identifier',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 tools/text_cleaner.py --file parsed.json --target "Villain" --output cleaned.json
  python3 tools/text_cleaner.py --file parsed.json --target "Villain" --deidentify --keep-emoji
        """
    )
    parser.add_argument('--file', required=True, help='Input JSON file from chat_parser')
    parser.add_argument('--target', required=True, help='Target user name')
    parser.add_argument('--output', default=None, help='Output file (default: stdout)')
    parser.add_argument('--deidentify', action='store_true',
                        help='Replace other senders with [PERSON_A], [PERSON_B], ...')
    parser.add_argument('--keep-emoji', action='store_true',
                        help='Keep emoji-only messages (default: remove)')
    parser.add_argument('--keep-urls', action='store_true',
                        help='Keep URLs (default: replace with [URL])')
    parser.add_argument('--show-map', action='store_true',
                        help='Print de-identification mapping to stderr')
    args = parser.parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"[ERROR] File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    records = json.loads(file_path.read_text(encoding='utf-8'))

    cleaned, deidentify_map = clean_records(
        records,
        target=args.target,
        remove_emoji_only=not args.keep_emoji,
        strip_urls=not args.keep_urls,
        deidentify=args.deidentify,
    )

    if args.show_map and deidentify_map:
        print("\n[De-identification Map]", file=sys.stderr)
        for original, label in deidentify_map.items():
            print(f"  {original} → {label}", file=sys.stderr)

    output = json.dumps(cleaned, ensure_ascii=False, indent=2)

    if args.output:
        Path(args.output).write_text(output, encoding='utf-8')
        print(f"[INFO] Output written to: {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == '__main__':
    main()
