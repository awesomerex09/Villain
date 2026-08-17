#!/usr/bin/env python3
"""
build_twin.py — Main Pipeline CLI
Self-Mirror: Digital Twin System

Orchestrates the full pipeline:
  Stage A: Parse raw data (chat / discord / github)
  Stage B: Clean and isolate target behavior
  Stage C: Analyze with LLM (requires API key)
  Stage D: Write Digital Twin profile

Usage:
    python build_twin.py --source-type chat --file chat.txt --target-name "Villain"
    python build_twin.py --source-type discord --file webhook.json --target-name "Villain"
    python build_twin.py --source-type github --file commits.json --target-name "Villain"
    python build_twin.py --help
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


# ── Paths ─────────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).parent
TOOLS_DIR = BASE_DIR / 'tools'
PROMPTS_DIR = BASE_DIR / 'prompts'
TWIN_PROFILE_DIR = BASE_DIR / 'twin_profile'
TMP_DIR = Path(os.environ.get('TEMP', '/tmp'))


# ── Stage runner ──────────────────────────────────────────────────────────────

def run_tool(script: str, args_list: list[str]) -> str:
    """Run a tools/ script and return stdout."""
    cmd = [sys.executable, str(TOOLS_DIR / script)] + args_list
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    if result.returncode != 0:
        print(f"[ERROR] {script} failed:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)
    if result.stderr:
        print(result.stderr, file=sys.stderr, end='')
    return result.stdout


def build_llm_prompt(prompt_file: str, context: dict) -> str:
    """Load a prompt template and inject context."""
    path = PROMPTS_DIR / prompt_file
    if not path.exists():
        print(f"[ERROR] Prompt file not found: {path}", file=sys.stderr)
        sys.exit(1)
    template = path.read_text(encoding='utf-8')
    # Simple variable substitution
    for key, value in context.items():
        template = template.replace(f'{{{key}}}', str(value))
    return template


def call_llm(prompt: str, llm_provider: str = 'anthropic') -> str:
    """
    Call an LLM with the given prompt.
    
    This is a stub — connect your preferred LLM API here.
    Supports: anthropic (Claude), openai (GPT)
    """
    print(f"[INFO] Calling LLM ({llm_provider})...", file=sys.stderr)
    
    if llm_provider == 'anthropic':
        try:
            import anthropic
            client = anthropic.Anthropic()
            message = client.messages.create(
                model="claude-opus-4-5",
                max_tokens=8192,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except ImportError:
            print("[WARN] anthropic package not installed. pip install anthropic", file=sys.stderr)
            return _demo_stub(prompt)
    
    elif llm_provider == 'openai':
        try:
            import openai
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except ImportError:
            print("[WARN] openai package not installed. pip install openai", file=sys.stderr)
            return _demo_stub(prompt)
    
    else:
        return _demo_stub(prompt)


def _demo_stub(prompt: str) -> str:
    """Demo mode: return a placeholder report when no LLM is configured."""
    return f"""# Digital Twin Analysis (Demo Mode)

> [NOTE] No LLM API configured. This is a placeholder report.
> Set ANTHROPIC_API_KEY or OPENAI_API_KEY environment variable to enable real analysis.

## Analysis Placeholder

Your data has been successfully parsed and cleaned.
To generate real insights, configure an LLM API key:

    Windows: setx ANTHROPIC_API_KEY "your-key-here"
    Or run:  python build_twin.py ... --llm anthropic

Prompt length: {len(prompt)} characters
Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""


# ── Pipeline stages ───────────────────────────────────────────────────────────

def stage_a_parse(source_type: str, file_path: str, target_name: str) -> list[dict]:
    """Stage A: Parse raw data."""
    print("\n[Stage A] Parsing raw data...", file=sys.stderr)
    
    tmp_output = TMP_DIR / 'self_mirror_parsed.json'
    
    if source_type == 'chat':
        run_tool('chat_parser.py', [
            '--file', file_path,
            '--target', target_name,
            '--format', 'json',
            '--output', str(tmp_output),
        ])
    elif source_type == 'discord':
        run_tool('dev_parser.py', [
            '--file', file_path,
            '--type', 'discord',
            '--format', 'json',
            '--output', str(tmp_output),
        ])
    elif source_type == 'github':
        run_tool('dev_parser.py', [
            '--file', file_path,
            '--type', 'github',
            '--format', 'json',
            '--output', str(tmp_output),
        ])
    
    records = json.loads(tmp_output.read_text(encoding='utf-8'))
    print(f"[Stage A] ✓ Parsed {len(records)} records.", file=sys.stderr)
    return records


def stage_b_clean(records: list[dict], target_name: str, deidentify: bool) -> list[dict]:
    """Stage B: Clean and isolate."""
    print("\n[Stage B] Cleaning and isolating target behavior...", file=sys.stderr)
    
    tmp_input = TMP_DIR / 'self_mirror_raw.json'
    tmp_output = TMP_DIR / 'self_mirror_cleaned.json'
    
    tmp_input.write_text(json.dumps(records, ensure_ascii=False), encoding='utf-8')
    
    extra_args = ['--deidentify'] if deidentify else []
    run_tool('text_cleaner.py', [
        '--file', str(tmp_input),
        '--target', target_name,
        '--output', str(tmp_output),
    ] + extra_args)
    
    cleaned = json.loads(tmp_output.read_text(encoding='utf-8'))
    target_msgs = [r for r in cleaned if r.get('is_target')]
    print(f"[Stage B] ✓ Cleaned. Target messages: {len(target_msgs)} / {len(cleaned)} total.", file=sys.stderr)
    return cleaned


def stage_c_analyze(cleaned_records: list[dict], target_name: str, llm_provider: str) -> dict:
    """Stage C: LLM analysis."""
    print("\n[Stage C] Running LLM analysis (this may take a minute)...", file=sys.stderr)
    
    # Build analysis context
    context_text = json.dumps(cleaned_records[:200], ensure_ascii=False, indent=2)  # limit tokens
    
    # Run objective analysis
    print("[Stage C]  → Objective analysis...", file=sys.stderr)
    analyzer_prompt = build_llm_prompt('objective_analyzer.md', {}) + f"\n\n## Behavioral Logs\n```json\n{context_text}\n```"
    objective_report = call_llm(analyzer_prompt, llm_provider)
    
    # Run knowledge extraction
    print("[Stage C]  → Knowledge extraction...", file=sys.stderr)
    knowledge_prompt = build_llm_prompt('knowledge_extractor.md', {}) + f"\n\n## Behavioral Logs\n```json\n{context_text}\n```"
    knowledge_map = call_llm(knowledge_prompt, llm_provider)
    
    # Build twin
    print("[Stage C]  → Twin synthesis...", file=sys.stderr)
    twin_prompt = (
        build_llm_prompt('twin_builder.md', {'name': target_name}) +
        f"\n\n## Objective Analysis\n{objective_report}\n\n## Knowledge Map\n{knowledge_map}"
    )
    twin_result = call_llm(twin_prompt, llm_provider)
    
    return {
        'objective_report': objective_report,
        'knowledge_map': knowledge_map,
        'twin_synthesis': twin_result,
    }


def stage_d_write(analyses: dict, target_name: str):
    """Stage D: Write Digital Twin profile."""
    print("\n[Stage D] Writing Digital Twin profile...", file=sys.stderr)
    
    TWIN_PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    header = f"<!-- generated_at: {now} | source: build_twin.py -->\n\n"
    
    # Write objective report
    report_path = TWIN_PROFILE_DIR / 'objective_report.md'
    report_path.write_text(header + analyses['objective_report'], encoding='utf-8')
    print(f"[Stage D] ✓ Written: {report_path}", file=sys.stderr)
    
    # Write core + style (from twin synthesis)
    synthesis = analyses['twin_synthesis']
    
    core_path = TWIN_PROFILE_DIR / f"{target_name}_core.md"
    style_path = TWIN_PROFILE_DIR / f"{target_name}_style.md"
    
    # Simple split: look for the style file marker
    if '# {Name} — Communication Style'.replace('{Name}', target_name) in synthesis:
        split_marker = f"# {target_name} — Communication Style"
        parts = synthesis.split(split_marker, 1)
        core_path.write_text(header + parts[0].strip(), encoding='utf-8')
        style_path.write_text(header + split_marker + parts[1] if len(parts) > 1 else header + synthesis, encoding='utf-8')
    elif '_style.md' in synthesis.lower():
        # Try to split by File 1 / File 2 markers
        core_path.write_text(header + synthesis, encoding='utf-8')
        style_path.write_text(header + "# Communication Style\n\nSee core file for full synthesis.", encoding='utf-8')
    else:
        core_path.write_text(header + synthesis, encoding='utf-8')
        style_path.write_text(header + "# Communication Style\n\nGenerated from twin synthesis. See core file.", encoding='utf-8')
    
    print(f"[Stage D] ✓ Written: {core_path}", file=sys.stderr)
    print(f"[Stage D] ✓ Written: {style_path}", file=sys.stderr)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Self-Mirror: Digital Twin Builder',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python build_twin.py --source-type chat --file chat.txt --target-name "Villain"
  python build_twin.py --source-type discord --file webhook.json --target-name "Villain" --llm openai
  python build_twin.py --source-type github --file commits.json --target-name "Villain" --deidentify
  python build_twin.py --source-type chat --file chat.txt --target-name "Villain" --dry-run
        """
    )
    parser.add_argument('--source-type', required=True,
                        choices=['chat', 'discord', 'github'],
                        help='Type of input data source')
    parser.add_argument('--file', required=True,
                        help='Path to input data file')
    parser.add_argument('--target-name', default='Villain',
                        help='Your name/identifier in the logs (default: Villain)')
    parser.add_argument('--llm', default='anthropic',
                        choices=['anthropic', 'openai', 'demo'],
                        help='LLM provider (default: anthropic). Use "demo" for dry run.')
    parser.add_argument('--deidentify', action='store_true',
                        help='De-identify third-party names in the analysis')
    parser.add_argument('--dry-run', action='store_true',
                        help='Parse and clean only, skip LLM analysis (same as --llm demo)')
    args = parser.parse_args()

    print("=" * 60)
    print("  Self-Mirror — Digital Twin Builder")
    print("=" * 60)
    print(f"  Source:  {args.source_type} / {args.file}")
    print(f"  Target:  {args.target_name}")
    print(f"  LLM:     {'demo (dry run)' if args.dry_run else args.llm}")
    print("=" * 60)

    llm_provider = 'demo' if args.dry_run else args.llm

    # Run pipeline
    records = stage_a_parse(args.source_type, args.file, args.target_name)
    cleaned = stage_b_clean(records, args.target_name, args.deidentify)
    analyses = stage_c_analyze(cleaned, args.target_name, llm_provider)
    stage_d_write(analyses, args.target_name)

    print("\n" + "=" * 60)
    print("  ✓ Digital Twin built successfully!")
    print(f"  Profile saved to: twin_profile/")
    print("=" * 60)
    print("\nNext step: python talk_to_myself.py\n")


if __name__ == '__main__':
    main()
