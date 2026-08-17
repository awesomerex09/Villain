Self-Mirror — Digital Twin System
==================================

"Can you see yourself objectively?"

Have you ever broken your trading discipline and only realized it after the fact?
Have you ever found yourself in a defensive conversation without knowing why?
Is your knowledge system truly what you think it is?

Self-Mirror is a **Digital Twin System** that distils your chat logs, dev journals,
and trading behaviors into a structured personal backup — enabling you to examine
your decision patterns, communication blind spots, and knowledge gaps from a
calm, third-party perspective.

Inspired by: perkfly/ex-skill ("Distill an ex-girlfriend into an AI Skill")
https://github.com/perkfly/ex-skill

If ex-skill turns the camera toward *her*, Self-Mirror turns it back toward *you*.

------------------------------------------------------------------

## Directory Structure

    self-mirror/
    ├── twin_profile/            # Generated Digital Twin (private, gitignored)
    │   ├── Villain_core.md      # Core values and decision logic
    │   ├── Villain_style.md     # Communication style and voice
    │   └── objective_report.md  # Objective self-analysis (SWOT, blind spots)
    ├── prompts/                 # LLM Prompt templates
    │   ├── self_isolation.md
    │   ├── objective_analyzer.md
    │   ├── knowledge_extractor.md
    │   └── twin_builder.md
    ├── tools/                   # Python utility scripts
    │   ├── chat_parser.py       # Parse chats (LINE / Messenger / iMessage)
    │   ├── dev_parser.py        # Parse Discord Webhooks & GitHub Commits
    │   ├── text_cleaner.py      # Noise filtering and de-identification
    │   └── twin_writer.py       # Digital Twin file management
    ├── exes/                    # Test sample (tribute to ex-skill)
    ├── docs/Architecture.md     # System architecture document
    ├── build_twin.py            # One-click build CLI
    ├── talk_to_myself.py        # Mirror interaction CLI
    ├── requirements.txt
    ├── LICENSE
    ├── README.md
    ├── README_EN.md (this file)
    └── update_github.bat        # Auto-push script

------------------------------------------------------------------

## Installation

Requires Python 3.9+

    pip install -r requirements.txt

Optional (Chinese name → slug conversion):
    pip install pypinyin

------------------------------------------------------------------

## Usage

### 1. Build Your Digital Twin

Provide your chat logs or dev journals:

    python build_twin.py --source-type chat --file path/to/chat.txt --target-name "Villain"

Supported source types:
    --source-type chat      LINE / Messenger / iMessage conversations
    --source-type discord   Discord Webhook JSON
    --source-type github    GitHub Commit logs

After execution, the system generates in twin_profile/:
    - Villain_core.md       Core decision logic
    - Villain_style.md      Communication style
    - objective_report.md   SWOT objective analysis

### 2. Talk to Your Digital Twin (Mirror Simulation)

    python talk_to_myself.py

Describe a decision dilemma you're currently facing.
The system responds as "the most rationally objective version of yourself."

### 3. Individual Tool Help

    python tools/chat_parser.py --help
    python tools/dev_parser.py --help
    python tools/text_cleaner.py --help
    python tools/twin_writer.py --help

------------------------------------------------------------------

## Data Flow

Stage 1: Ingestion & Self-Isolation
    Parse raw logs → Filter others' messages → Build (Stimulus → Response) pairs

Stage 2: Multi-Dimensional Analysis
    Communication & Emotion layer / Knowledge & Decision layer — in parallel

Stage 3: Twin Synthesis
    Assemble structured Markdown backup + Objective analysis report

Stage 4: Mirror Interaction
    Query the digital twin; simulate decisions under objective rationality

------------------------------------------------------------------

## Notes

- Data quality determines analysis depth: real logs > description only
- Priority: your long messages > emotional messages > daily chatter
- All data is processed locally; nothing is sent to any external service
- twin_profile/ is gitignored — never manually commit private data

------------------------------------------------------------------

## Acknowledgements

- perkfly/ex-skill (https://github.com/perkfly/ex-skill)
  MIT License © perkfly
  The creative concept of "distilling a person into an AI Skill" sparked this project.

- SKILL.md Visual Guidelines (Apple Fluid Interface Design)
  Frontend visuals are fully aligned with Apple WWDC Design principles.

------------------------------------------------------------------

MIT License © 2026 Villain (awesomerex09)
See LICENSE for full details.
