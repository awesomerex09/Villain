# Self-Mirror — 數位自我雙生系統 (Digital Twin System)

> 「你能客觀地看見自己嗎？」  
> 如果 [perkfly/ex-skill](https://github.com/perkfly/ex-skill) 是把鏡頭對準「她」，蒸餾成前任 AI Skill；  
> **Self-Mirror** 則是把鏡頭轉回對準「你自己」，將你的對話紀錄、開發與交易日誌蒸餾為數位雙生，進行客觀剖析與決策模擬。

---

## 📖 專案是什麼？

**Self-Mirror** 是一套本機端運行的數位人格萃取與決策鏡像系統：
1. **本我剝離**：從複雜的聊天紀錄或開發日誌中，提取出「情境刺激 ➔ 你的反應 (Stimulus ➔ Response)」模式。
2. **多維度剖析**：分析你的溝通慣性、情緒防禦機制、專業領域硬規則（如交易紀律、程式架構習慣）。
3. **數位雙生合成**：生成你的客觀分析報告與人格設定檔（儲存於 `twin_profile/`）。
4. **鏡像模擬對話 (`talk_to_myself.py`)**：遇到重大決策或情緒卡點時，讓「絕對理性、客觀狀態下的你自己」為你進行第三方決策回測。

---

## 🚀 快速上手教學 (How to Use)

### 1. 環境需求
- Python 3.9+（Windows 建議直接使用系統自帶的 `py` 指令）
- 安裝依賴套件（可選）：
  ```bash
  pip install -r requirements.txt
  ```

---

### 2. 第一步：建置你的數位雙生 (`build_twin.py`)

提供你的原始資料（聊天紀錄、Discord 日誌或 GitHub Commit），執行一鍵萃取與建置：

```bash
# 格式範例：解析聊天紀錄
py -3 build_twin.py --source-type chat --file path/to/chat.txt --target-name "Villain"

# 支援的來源類型：
# --source-type chat      LINE / Messenger / iMessage 等文字對話
# --source-type discord   Discord Webhook 導出的 JSON 檔案
# --source-type github    GitHub Commit 歷史紀錄

# 無 API Key 測試 (Demo / Dry-Run 模式)：
py -3 build_twin.py --source-type chat --file chat.txt --target-name "Villain" --dry-run
```

**執行後系統會在 `twin_profile/` 生成三個核心檔案（已加入 .gitignore 保護隱私）：**
- `Villain_core.md`：你的決策邏輯、底層原則與已知失敗模式。
- `Villain_style.md`：你的用字遣詞、語氣特徵與人際互動模式。
- `objective_report.md`：系統產出的第三方客觀 SWOT 剖析與盲點清單。

---

### 3. 第二步：與數位雙生對話 / 決策模擬 (`talk_to_myself.py`)

當你遇到交易糾結、職涯選擇或溝通困境時，啟動鏡像對話：

```bash
# 啟動互動式對話
py -3 talk_to_myself.py

# 或單次情境提問：
py -3 talk_to_myself.py --scenario "我現在看到這檔股票跌破停損點，但我覺得會反彈，要加碼嗎？"
```

**`talk_to_myself.py` 的運作原理：**
- 它會載入你的 `twin_profile/`（你的核心原則與歷史盲點）。
- 扮演「冷靜客觀的你自己」，不帶情緒偏誤地審視你目前的決策。
- 提醒你：「你過去曾制定過『跌破直接停損』的硬規則，現在加碼符合你的過度自信盲點嗎？」。

---

## 🛠️ 工具腳本獨立使用 (Tools CLI)

如果你想單獨處理資料：

```bash
# 1. 聊天紀錄解析
py -3 tools/chat_parser.py --file chat.txt --target "Villain" --format json --output parsed.json

# 2. 開發/交易日誌解析
py -3 tools/dev_parser.py --file webhook.json --type discord --output dev_out.txt

# 3. 去識別化與去雜訊
py -3 tools/text_cleaner.py --file parsed.json --target "Villain" --deidentify --output cleaned.json

# 4. 查看目前生成的雙生檔案清單
py -3 tools/twin_writer.py --action list
```

---

## 🔄 更新專案到 GitHub

專案目錄下已配置自動更新腳本，隨時雙擊執行：
- **`update_github.bat`**：自動完成 `git add`、生成時間戳 Commit 並推送到 [awesomerex09/Villain](https://github.com/awesomerex09/Villain)。

---

## 📂 完整目錄結構

```
self-mirror/
├── twin_profile/            # 生成的數位雙生設定檔（私人資料，已 gitignore）
│   ├── Villain_core.md      # 核心價值觀與決策邏輯
│   ├── Villain_style.md     # 溝通風格與語氣特徵
│   └── objective_report.md  # 客觀自我剖析報告 (SWOT、情緒盲點)
├── prompts/                 # LLM Prompt 提示詞模板
│   ├── self_isolation.md    # 本我剝離邏輯
│   ├── objective_analyzer.md# 客觀行為與盲點分析
│   ├── knowledge_extractor.md # 領域知識與硬規則萃取
│   └── twin_builder.md      # 數位人格合成模板
├── tools/                   # Python 前處理工具庫
│   ├── chat_parser.py       # 通用對話解析 (LINE/Messenger/iMessage)
│   ├── dev_parser.py        # 日誌解析 (Discord Webhook / GitHub Commits)
│   ├── text_cleaner.py      # 去識別化與雜訊過濾
│   └── twin_writer.py       # 雙生檔案輸出與增量更新管理
├── exes/                    # 範例結構區塊（致敬 ex-skill）
│   └── example_xiaomei/     # 示範用前任 Skill 結構
├── docs/Architecture.md     # 系統架構與 Data Flow 詳細文件
├── build_twin.py            # 一鍵建構數位雙生主程式
├── talk_to_myself.py        # 鏡像互動與決策模擬主程式
├── requirements.txt         # 依賴套件
├── LICENSE                  # MIT License
├── README.md                # 專案主說明文件
└── update_github.bat        # Windows 一鍵更新 GitHub 腳本
```

---

## 🤝 致謝與宣告 (Acknowledgements)

- **[perkfly/ex-skill](https://github.com/perkfly/ex-skill)** (MIT License © perkfly)  
  啟發本專案將 Prompt 結構化、資料前處理與 Persona 萃取技術轉化為「向內探索」的自我鏡像系統。
- **[Apple WWDC Design Principles](SKILL.md)**  
  本專案流程與互動介面均秉持 Apple Fluid Interface 理念（零延遲回饋、狀態連續性、可中斷增量架構）。

---

MIT License © 2026 Villain (awesomerex09)
