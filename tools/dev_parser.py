#!/usr/bin/env python3
"""
dev_parser.py — Development & Trading Log Parser
Self-Mirror: Digital Twin System

Parses Discord Webhook JSON logs and GitHub Commit records to capture
technical behavior and trading decision data.

Usage:
    python3 tools/dev_parser.py --file webhook.json --type discord --output /tmp/dev_out.txt
    python3 tools/dev_parser.py --file commits.json --type github --output /tmp/commits_out.txt
    python3 tools/dev_parser.py --github-repo owner/repo --token YOUR_TOKEN --output /tmp/gh.txt
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


# ── Discord Webhook Parser ────────────────────────────────────────────────────

def parse_discord_webhook(data: list | dict) -> list[dict]:
    """
    Parse Discord Webhook JSON export.
    Supports DiscordChatExporter output format.
    """
    records = []

    # Handle DiscordChatExporter format
    if isinstance(data, dict) and 'messages' in data:
        messages = data['messages']
    elif isinstance(data, list):
        messages = data
    else:
        print("[WARN] Unexpected Discord JSON structure.", file=sys.stderr)
        return records

    for msg in messages:
        try:
            timestamp = msg.get('timestamp', '') or msg.get('createdAt', '')
            author = msg.get('author', {})
            sender = author.get('name', '') if isinstance(author, dict) else str(author)
            content = msg.get('content', '')
            embeds = msg.get('embeds', [])

            # Include embed descriptions (common for trading alerts)
            embed_text = []
            for embed in embeds:
                if embed.get('description'):
                    embed_text.append(f"[EMBED] {embed['description']}")
                if embed.get('title'):
                    embed_text.append(f"[EMBED TITLE] {embed['title']}")
                for field in embed.get('fields', []):
                    embed_text.append(f"[{field.get('name', '')}] {field.get('value', '')}")

            full_content = content
            if embed_text:
                full_content = (content + '\n' + '\n'.join(embed_text)).strip()

            if full_content:
                records.append({
                    'timestamp': timestamp,
                    'sender': sender,
                    'message': full_content,
                    'source': 'discord',
                    'channel': data.get('channel', {}).get('name', '') if isinstance(data, dict) else '',
                })
        except Exception as e:
            print(f"[WARN] Skipped message: {e}", file=sys.stderr)

    return records


# ── GitHub Commit Parser ──────────────────────────────────────────────────────

def parse_github_commits(data: list) -> list[dict]:
    """
    Parse GitHub API /repos/{owner}/{repo}/commits JSON response.
    """
    records = []

    for commit in data:
        try:
            commit_data = commit.get('commit', {})
            author = commit_data.get('author', {})
            committer = commit_data.get('committer', {})

            timestamp = author.get('date', '') or committer.get('date', '')
            sender = author.get('name', '') or committer.get('name', '')
            message = commit_data.get('message', '')
            sha = commit.get('sha', '')[:8]

            records.append({
                'timestamp': timestamp,
                'sender': sender,
                'message': f"[COMMIT {sha}] {message}",
                'source': 'github',
                'sha': commit.get('sha', ''),
                'url': commit.get('html_url', ''),
            })
        except Exception as e:
            print(f"[WARN] Skipped commit: {e}", file=sys.stderr)

    return records


def parse_github_text(content: str) -> list[dict]:
    """
    Parse plain-text GitHub commit log (from `git log --oneline` or similar).
    Format: "SHA message" or "SHA YYYY-MM-DD Author message"
    """
    import re
    records = []

    # Full git log format: "commit SHA\nAuthor: ...\nDate: ...\n\n    message"
    full_pattern = re.compile(
        r'commit ([a-f0-9]{40})\nAuthor: (.+?) <.+?>\nDate:\s+(.+?)\n\n(.+?)(?=\ncommit|\Z)',
        re.DOTALL
    )
    matches = list(full_pattern.finditer(content))

    if matches:
        for m in matches:
            sha = m.group(1)[:8]
            sender = m.group(2).strip()
            timestamp = m.group(3).strip()
            message = m.group(4).strip().replace('\n    ', ' ')
            records.append({
                'timestamp': timestamp,
                'sender': sender,
                'message': f"[COMMIT {sha}] {message}",
                'source': 'github',
            })
        return records

    # Simple oneline format: "a1b2c3d message here"
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(' ', 1)
        if len(parts) == 2 and len(parts[0]) in (7, 8, 40):
            records.append({
                'timestamp': '',
                'sender': 'Unknown',
                'message': f"[COMMIT {parts[0][:8]}] {parts[1]}",
                'source': 'github',
            })

    return records


# ── Output formatter ──────────────────────────────────────────────────────────

def format_records(records: list[dict], fmt: str) -> str:
    if fmt == 'json':
        return json.dumps(records, ensure_ascii=False, indent=2)

    lines = []
    for r in records:
        lines.append(f"[{r['timestamp']}] [{r.get('source', '?').upper()}] {r['sender']}: {r['message']}")
    return '\n'.join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Self-Mirror: Development & Trading Log Parser',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 tools/dev_parser.py --file webhook.json --type discord
  python3 tools/dev_parser.py --file commits.json --type github
  python3 tools/dev_parser.py --file git.log --type github-text --output out.txt
        """
    )
    parser.add_argument('--file', required=True, help='Path to log file (JSON or text)')
    parser.add_argument('--type', required=True,
                        choices=['discord', 'github', 'github-text'],
                        help='Log source type')
    parser.add_argument('--format', choices=['json', 'text'], default='text', help='Output format')
    parser.add_argument('--output', default=None, help='Output file path (default: stdout)')
    args = parser.parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"[ERROR] File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    content = file_path.read_text(encoding='utf-8', errors='replace')

    records = []
    if args.type == 'discord':
        data = json.loads(content)
        records = parse_discord_webhook(data)
    elif args.type == 'github':
        data = json.loads(content)
        records = parse_github_commits(data)
    elif args.type == 'github-text':
        records = parse_github_text(content)

    print(f"[INFO] Parsed {len(records)} records from {args.type}.", file=sys.stderr)

    output = format_records(records, args.format)

    if args.output:
        Path(args.output).write_text(output, encoding='utf-8')
        print(f"[INFO] Output written to: {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == '__main__':
    main()
