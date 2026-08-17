# Self-Mirror — System Architecture

## Overview

```
Raw Data Sources
    │
    ▼
[Stage A: Data Ingestion & Self-Isolation]
    chat_parser.py / dev_parser.py
    text_cleaner.py
    │
    ▼
Stimulus → Response Pairs (JSON)
    │
    ▼
[Stage B: Multi-Dimensional Analysis (via LLM)]
    ├── prompts/objective_analyzer.md  → Communication + Emotion Layer
    ├── prompts/knowledge_extractor.md → Knowledge + Decision Layer
    └── prompts/self_isolation.md      → Context Extraction Logic
    │
    ▼
Analysis Reports
    │
    ▼
[Stage C: Digital Twin Synthesis]
    prompts/twin_builder.md
    │
    ▼
twin_profile/
    ├── {name}_core.md       ← Decision Logic
    ├── {name}_style.md      ← Communication Style
    └── objective_report.md  ← SWOT + Blind Spots
    │
    ▼
[Stage D: Mirror Interaction]
    talk_to_myself.py
    │
    ▼
Objective Self-Reflection Output
```

## Data Flow Detail

### Stage A: Data Ingestion & Self-Isolation

**Input**: Raw conversation/log files
**Tools**: `chat_parser.py`, `dev_parser.py`, `text_cleaner.py`

1. **Parse** raw exports into normalized `(Timestamp, Sender, Message)` records
2. **Filter** system messages, noise, emoji-only entries
3. **Isolate** the target user's messages with surrounding context (3–5 preceding messages)
4. **Output**: JSON array of `{timestamp, context_stimulus, target_response}` records

### Stage B: Multi-Dimensional LLM Analysis

**Input**: Self-isolated behavior records
**Prompts**: `objective_analyzer.md`, `knowledge_extractor.md`

Two parallel analysis tracks:
- **Communication & Emotion Track**: Patterns, defense mechanisms, blind spots, emotional regulation
- **Knowledge & Decision Track**: Domain expertise map, hard rules, knowledge gaps, overconfidence flags

**Output**: Two structured Markdown analysis reports

### Stage C: Digital Twin Synthesis

**Input**: Analysis reports from Stage B
**Prompt**: `twin_builder.md`

Synthesizes a cohesive Digital Twin with:
- `{name}_core.md`: Decision engine (principles, domain rules, failure modes)
- `{name}_style.md`: Voice and relational behavior model

**Output**: Two structured persona files in `twin_profile/`

### Stage D: Mirror Interaction

**Input**: Digital Twin profile files
**Tool**: `talk_to_myself.py`

The MirrorAgent:
1. Loads the Digital Twin profile as its system context
2. Accepts user-described decision scenarios
3. Responds as "the most rationally objective version of the subject"
4. Flags relevant blind spots and failure mode patterns

## Key Design Decisions

### Privacy-First
- All processing is local; no data leaves the machine
- `twin_profile/` is gitignored by default
- De-identification available via `--deidentify` flag

### Incremental Updates
- `twin_writer.py merge` preserves all historical content
- New data appends as versioned sections, not overwrites
- Enables "continuous growth" of the Digital Twin

### LLM-Agnostic
- Supports Anthropic Claude, OpenAI GPT
- Demo/dry-run mode requires no API key
- Prompt templates are LLM-agnostic Markdown

### Tribute to ex-skill
- `exes/` directory structure mirrors ex-skill's `exes/` convention
- Same Stimulus→Response analysis pattern
- Same incremental merge philosophy
- Where ex-skill distils "her", Self-Mirror distils "you"

## File Reference

| File | Purpose | Stage |
|------|---------|-------|
| `build_twin.py` | Main pipeline orchestrator | All |
| `talk_to_myself.py` | Interactive mirror session | D |
| `tools/chat_parser.py` | Parse LINE/Messenger/iMessage | A |
| `tools/dev_parser.py` | Parse Discord/GitHub logs | A |
| `tools/text_cleaner.py` | Clean and de-identify | A |
| `tools/twin_writer.py` | Manage profile files | C |
| `prompts/self_isolation.md` | Self-isolation LLM prompt | A |
| `prompts/objective_analyzer.md` | Behavioral analysis prompt | B |
| `prompts/knowledge_extractor.md` | Knowledge mapping prompt | B |
| `prompts/twin_builder.md` | Twin synthesis prompt | C |
| `twin_profile/{name}_core.md` | Decision logic backup | Output |
| `twin_profile/{name}_style.md` | Communication style backup | Output |
| `twin_profile/objective_report.md` | SWOT analysis report | Output |
