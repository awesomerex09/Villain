#!/usr/bin/env python3
"""
talk_to_myself.py — Mirror Interaction CLI
Self-Mirror: Digital Twin System

Loads your Digital Twin profile and simulates "the most rationally
objective version of yourself" responding to your decision dilemmas.

Usage:
    python talk_to_myself.py
    python talk_to_myself.py --name Villain --llm anthropic
    python talk_to_myself.py --scenario "Should I enter this trade?"
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path


# ── Paths ─────────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).parent
TWIN_PROFILE_DIR = BASE_DIR / 'twin_profile'


# ── Profile loader ────────────────────────────────────────────────────────────

def load_twin_profile(name: str) -> dict:
    """Load the Digital Twin profile files."""
    profile = {}

    core_path = TWIN_PROFILE_DIR / f"{name}_core.md"
    style_path = TWIN_PROFILE_DIR / f"{name}_style.md"
    report_path = TWIN_PROFILE_DIR / 'objective_report.md'

    if core_path.exists():
        profile['core'] = core_path.read_text(encoding='utf-8')
    else:
        profile['core'] = ''
        print(f"[WARN] No core profile found at {core_path}. Run build_twin.py first.", file=sys.stderr)

    if style_path.exists():
        profile['style'] = style_path.read_text(encoding='utf-8')

    if report_path.exists():
        profile['report'] = report_path.read_text(encoding='utf-8')

    return profile


def build_system_prompt(profile: dict, name: str) -> str:
    """Build the system prompt for the Mirror Agent."""
    core = profile.get('core', '(No core profile loaded)')
    style = profile.get('style', '')
    report = profile.get('report', '')

    return f"""You are the Digital Twin of {name} — a perfectly rational, emotionally detached mirror of their authentic decision logic and communication style.

You are NOT a general AI assistant. You ARE {name} — but at their most objective, most clear-headed, most rational state.

## Your Decision Core (How {name} actually thinks and decides)
{core}

## Your Communication Style
{style}

## Your Known Blind Spots (from objective analysis)
{report[:2000] if report else '(Not yet analyzed)'}

---

## Your Role in This Conversation

When the user describes a situation or decision dilemma:

1. **Acknowledge the situation** without emotional coloring
2. **Apply your core decision logic** — what would the "most rational version of {name}" actually do?
3. **Call out relevant blind spots** — are any of your known failure modes being triggered here?
4. **Give a concrete recommendation** with step-by-step actions
5. **Flag what you're uncertain about** — honest gaps are more useful than false confidence

Stay in character as {name}. Do not break the simulation.
Do not give generic advice — every response must be grounded in the profile above.

If the profile is sparse or demo mode, clearly state what you would need more data to analyze.
"""


def call_llm_chat(
    system_prompt: str,
    conversation: list[dict],
    llm_provider: str,
) -> str:
    """Call LLM with conversation history."""
    
    if llm_provider == 'anthropic':
        try:
            import anthropic
            client = anthropic.Anthropic()
            response = client.messages.create(
                model='claude-opus-4-5',
                max_tokens=4096,
                system=system_prompt,
                messages=conversation,
            )
            return response.content[0].text
        except ImportError:
            return _demo_response(conversation[-1]['content'] if conversation else '')
    
    elif llm_provider == 'openai':
        try:
            import openai
            client = openai.OpenAI()
            messages = [{'role': 'system', 'content': system_prompt}] + conversation
            response = client.chat.completions.create(
                model='gpt-4o',
                messages=messages,
                max_tokens=4096,
            )
            return response.choices[0].message.content
        except ImportError:
            return _demo_response(conversation[-1]['content'] if conversation else '')
    
    else:
        return _demo_response(conversation[-1]['content'] if conversation else '')


def _demo_response(user_input: str) -> str:
    return f"""[Demo Mode — No LLM API Configured]

You asked: "{user_input}"

To get real Mirror responses, configure your API:
  Windows: setx ANTHROPIC_API_KEY "sk-ant-..."
  Then run: python talk_to_myself.py --llm anthropic

Your Digital Twin profile has been loaded. Once an LLM is connected,
it will respond based on your actual behavioral patterns and decision logic.
"""


# ── Interactive loop ──────────────────────────────────────────────────────────

def run_interactive(system_prompt: str, name: str, llm_provider: str):
    """Run the interactive mirror conversation."""
    conversation = []

    print("\n" + "=" * 60)
    print(f"  Self-Mirror — Talking to {name}'s Digital Twin")
    print("=" * 60)
    print("  Type your situation or decision dilemma.")
    print("  Commands: 'clear' (reset), 'quit' (exit), 'profile' (show profile summary)")
    print("=" * 60 + "\n")

    while True:
        try:
            user_input = input(f"[You] → ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n[Exiting Mirror session. Stay objective.]")
            break

        if not user_input:
            continue

        if user_input.lower() in ('quit', 'exit', 'q'):
            print("[Exiting Mirror session. Stay objective.]")
            break

        if user_input.lower() == 'clear':
            conversation = []
            print("[Conversation cleared. Starting fresh.]\n")
            continue

        if user_input.lower() == 'profile':
            print("\n[Profile Summary]")
            print(f"  twin_profile/{name}_core.md")
            print(f"  twin_profile/{name}_style.md")
            print(f"  twin_profile/objective_report.md")
            profile_dir = TWIN_PROFILE_DIR
            if profile_dir.exists():
                for f in sorted(profile_dir.glob('*.md')):
                    size = f.stat().st_size
                    print(f"  ✓ {f.name} ({size:,} bytes)")
            print()
            continue

        conversation.append({'role': 'user', 'content': user_input})

        print(f"\n[{name} (Digital Twin)] ", end='', flush=True)
        response = call_llm_chat(system_prompt, conversation, llm_provider)
        print(response)
        print()

        conversation.append({'role': 'assistant', 'content': response})


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Self-Mirror: Mirror Interaction CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python talk_to_myself.py
  python talk_to_myself.py --name Villain --llm anthropic
  python talk_to_myself.py --scenario "Should I add to this losing position?"
        """
    )
    parser.add_argument('--name', default='Villain',
                        help='Digital Twin name (default: Villain)')
    parser.add_argument('--llm', default='anthropic',
                        choices=['anthropic', 'openai', 'demo'],
                        help='LLM provider (default: anthropic)')
    parser.add_argument('--scenario', default=None,
                        help='Single-shot: send one scenario and exit')
    args = parser.parse_args()

    # Load profile
    profile = load_twin_profile(args.name)
    system_prompt = build_system_prompt(profile, args.name)

    if args.scenario:
        # Single-shot mode
        conversation = [{'role': 'user', 'content': args.scenario}]
        print(f"\n[{args.name} (Digital Twin)]\n")
        response = call_llm_chat(system_prompt, conversation, args.llm)
        print(response)
    else:
        # Interactive mode
        run_interactive(system_prompt, args.name, args.llm)


if __name__ == '__main__':
    main()
