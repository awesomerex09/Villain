Self-Mirror — 數位自我雙生系統
================================

「你能客觀地看見自己嗎？」

你是否曾在交易後才發現自己打破了紀律？
你是否在溝通後才意識到你說話的方式讓對方產生防禦？
你的知識體系，真的是你以為的那樣嗎？

Self-Mirror 是一套「數位自我雙生系統」——
它把你的對話記錄、開發日誌、交易行為蒸馏成一個數位人格備份，
讓你能以「第三方客觀視角」審視自己的決策模式、溝通盲點與知識邊界。

靈感致敬：perkfly/ex-skill（前任蒸馏為 AI Skill）
https://github.com/perkfly/ex-skill

如果 ex-skill 是把鏡頭對準「她」，
Self-Mirror 就是把鏡頭轉回來，對準「你自己」。

------------------------------------------------------------------

## 目錄結構

self-mirror/
├── twin_profile/            # 生成的數位雙生備份（私人，gitignored）
│   ├── Villain_core.md      # 核心價值觀與決策邏輯
│   ├── Villain_style.md     # 溝通風格與語氣特徵
│   └── objective_report.md  # 客觀自我剖析報告（SWOT、情緒盲點）
├── prompts/                 # LLM Prompt 模板
│   ├── self_isolation.md
│   ├── objective_analyzer.md
│   ├── knowledge_extractor.md
│   └── twin_builder.md
├── tools/                   # Python 工具腳本
│   ├── chat_parser.py       # 解析對話（LINE/Messenger/iMessage）
│   ├── dev_parser.py        # 解析 Discord Webhook / GitHub Commits
│   ├── text_cleaner.py      # 雜訊過濾與去識別化
│   └── twin_writer.py       # 數位雙生檔案管理
├── exes/                    # 測試用前任範本（致敬 ex-skill）
├── docs/Architecture.md     # 系統架構文件
├── build_twin.py            # 一鍵建構 CLI
├── talk_to_myself.py        # 鏡像互動 CLI
├── requirements.txt
├── LICENSE
├── README.md（本檔案）
├── README_EN.md
└── update_github.bat        # 自動推送腳本

------------------------------------------------------------------

## 安裝

需求：Python 3.9+

    pip install -r requirements.txt

可選（中文名稱轉 slug）：
    pip install pypinyin

------------------------------------------------------------------

## 使用方式

### 1. 建構數位雙生

提供你的對話記錄或開發日誌，執行：

    python build_twin.py --source-type chat --file path/to/chat.txt --target-name "Villain"

支援的資料來源：
    --source-type chat      LINE / Messenger / iMessage 對話
    --source-type discord   Discord Webhook JSON
    --source-type github    GitHub Commit 紀錄

執行後，系統會在 twin_profile/ 下生成：
    - Villain_core.md       核心決策邏輯
    - Villain_style.md      溝通風格
    - objective_report.md   SWOT 客觀剖析

### 2. 與數位雙生對話（鏡像模擬）

    python talk_to_myself.py

輸入你正在面對的決策困境，
系統會以「絕對理性的你自己」的視角給出分析與建議。

### 3. 各工具 CLI 說明

    python tools/chat_parser.py --help
    python tools/dev_parser.py --help
    python tools/text_cleaner.py --help
    python tools/twin_writer.py --help

------------------------------------------------------------------

## 資料流程

階段一：資料攝取與本我剝離
    解析對話 → 過濾他人訊息 → 建立「情境刺激 → 你的反應」配對

階段二：多維度特徵分析
    溝通與情緒層 / 知識與決策層 平行分析

階段三：數位雙生合成
    組裝為結構化 Markdown 備份 + 客觀剖析報告

階段四：鏡像互動與回測
    向數位雙生提問，測試客觀狀態下的決策

------------------------------------------------------------------

## 注意事項

- 對話品質決定分析深度：真實對話 > 僅靠描述
- 建議優先提供：你主動發的長訊息 > 情感類 > 日常
- 所有資料僅在本地處理，不上傳任何外部服務
- twin_profile/ 已加入 .gitignore，請勿手動提交私人資料

------------------------------------------------------------------

## 致謝

- perkfly/ex-skill (https://github.com/perkfly/ex-skill)
  MIT License © perkfly
  「把前任蒸馏成 AI Skill」的創意啟發了本專案的方向思考。

- SKILL.md 視覺規範（Apple Fluid Interface Design）
  本專案前端視覺完全依照 Apple WWDC Design 精神構建。

------------------------------------------------------------------

MIT License © 2026 Villain (awesomerex09)
See LICENSE for full details.
