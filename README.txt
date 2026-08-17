Self-Mirror — Digital Twin System
==================================

README.txt (Plain Text Version)
For full Markdown documentation, see README.md and README_EN.md.

------------------------------------------------------------------

WHAT IS THIS?

Self-Mirror (數位自我雙生系統) is a local tool that distils your own 
conversation logs, development journals, and behavioral data into a 
structured "Digital Twin" — allowing you to examine your decision 
patterns, communication blind spots, and knowledge edges from an 
objective, third-party perspective.

Inspired by perkfly/ex-skill:
  https://github.com/perkfly/ex-skill

If ex-skill distils "her" into an AI Skill,
Self-Mirror turns the mirror inward and distils YOU.

------------------------------------------------------------------

REQUIREMENTS

  Python 3.9 or newer
  pip install -r requirements.txt

------------------------------------------------------------------

QUICK START

  1. Build your Digital Twin:
     python build_twin.py --source-type chat --file chat.txt --target-name "Villain"

  2. Talk to your Digital Twin:
     python talk_to_myself.py

  3. Update to GitHub (Windows):
     Double-click update_github.bat

------------------------------------------------------------------

FILES

  build_twin.py          — Main pipeline: parse → analyze → write twin
  talk_to_myself.py      — Interactive mirror simulation
  tools/chat_parser.py   — Parse LINE / Messenger / iMessage chats
  tools/dev_parser.py    — Parse Discord Webhooks / GitHub Commits
  tools/text_cleaner.py  — Filter noise and de-identify data
  tools/twin_writer.py   — Write and merge twin_profile/ files
  prompts/               — LLM prompt templates (A/B/C analysis engines)
  twin_profile/          — Your generated Digital Twin (GITIGNORED)
  exes/                  — Sample test data (tribute to ex-skill)
  docs/Architecture.md   — Full system architecture document

------------------------------------------------------------------

PRIVACY

  All data is processed LOCALLY.
  Nothing is uploaded to external servers.
  twin_profile/ is listed in .gitignore — your personal data stays private.

------------------------------------------------------------------

LICENSE

  MIT License © 2026 Villain (awesomerex09)

  This project is inspired by and pays tribute to:
    perkfly/ex-skill — MIT License © perkfly
    https://github.com/perkfly/ex-skill

------------------------------------------------------------------

CONTACT

  GitHub: https://github.com/awesomerex09/Villain

