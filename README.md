# Self-Mirror — 數位自我雙生系統 (Digital Twin System)

> 「你知道自己在別人眼裡是什麼樣子嗎？」  
> 如果 [perkfly/ex-skill](https://github.com/perkfly/ex-skill) 是把鏡頭對準「她」，蒸餾成前任 AI Skill；  
> **Self-Mirror** 則是把鏡頭轉回對準「你自己」，將你的對話紀錄蒸餾為數位雙生。
> 
> 這是一個好玩、充滿好奇心的開源專案！你可以用它來看看自己平時傳訊息的樣子、審視自己跟朋友或客戶講話時的語氣，或者單純想跟「絕對客觀的自己」聊聊天、對話一下。

---

## 📖 專案是什麼？

**Self-Mirror** 是一套本機端運行的數位人格萃取與決策鏡像系統，也是設計給 Agent 呼叫或直接使用的工具：
1. **本我剝離**：從複雜的聊天紀錄中，提取出「情境刺激 ➔ 你的反應 (Stimulus ➔ Response)」模式。
2. **多維度剖析**：分析你的溝通慣性、說話風格、情緒防禦機制。
3. **數位雙生合成**：透過 LLM (如 Claude/GPT)，生成你的客觀分析報告與人格設定檔（儲存於 `twin_profile/`）。
4. **鏡像模擬對話 (`talk_to_myself.py`)**：讓「絕對理性、客觀狀態下的你自己」為你進行第三方回饋，你可以拿它來預演重要的對話，或單純跟自己聊天。

---

## 🚀 快速上手教學 (How to Use)

### 1. 環境需求與 API 金鑰設定
- Python 3.9+
- 安裝依賴套件（可選）：
  ```bash
  pip install -r requirements.txt
  ```

**⚠️ 重要：本專案依賴 LLM (大語言模型) 進行分析，請先設定 API Key**
（如果你只想乾跑測試流程，可跳過此步並在後續指令加上 `--dry-run`）

**設定 Anthropic (Claude) API Key (推薦)：**
- Windows (命令提示字元): `setx ANTHROPIC_API_KEY "sk-ant-..."`
- macOS/Linux: `export ANTHROPIC_API_KEY="sk-ant-..."`

**設定 OpenAI (GPT-4o) API Key：**
- Windows (命令提示字元): `setx OPENAI_API_KEY "sk-proj-..."`
- macOS/Linux: `export OPENAI_API_KEY="sk-proj-..."`

---

### 2. 第一步：準備資料與建置雙生 (`build_twin.py`)

你可以直接放單一檔案，或是放多個對話檔案：

#### 情況 A：只有單個對話檔案
把檔案（例如 `chat.txt` 或 LINE 導出的文字檔）放在專案資料夾下，並將 `"YourName"` 換成你在對話中的名字：
```bash
py -3 build_twin.py --source-type chat --file chat.txt --target-name "YourName"
```

#### 情況 B：有多個對話紀錄（推薦）
建立一個資料夾（例如 `data/chats/`），把多個不同對象、群組的 `.txt` 檔案通通放進去：
```bash
# 直接指定資料夾，系統會自動批量讀取並合併所有對話：
py -3 build_twin.py --source-type chat --dir data/chats --target-name "YourName"
```

#### 其他參數：
- `--llm openai`：改用 OpenAI (預設為 anthropic)
- `--source-type discord` 或 `github`：如果你想分析自己寫 Code 或在社群發言的樣子
- `--dry-run`：無 LLM API Key 時的測試模式（只做解析與去識別化）

**執行後系統會在 `twin_profile/` 生成三個核心檔案（已加入 .gitignore 保護隱私）：**
- `YourName_core.md`：你的底層原則與思考邏輯。
- `YourName_style.md`：你的用字遣詞、語氣特徵與人際互動模式。
- `objective_report.md`：系統產出的第三方客觀剖析。

---

### 3. 第二步：與數位雙生對話 (`talk_to_myself.py`)

想知道自己會怎麼回覆一句話？或是想跟客觀的自己聊聊：

```bash
# 啟動互動式對話 (將 YourName 換成你剛剛建立的名字)
py -3 talk_to_myself.py --name "YourName"

# 或單次情境提問 (適合 Agent 呼叫)：
py -3 talk_to_myself.py --name "YourName" --scenario "朋友突然借錢，你覺得我會怎麼回？"
```

**`talk_to_myself.py` 的運作原理：**
- 載入你的 `twin_profile/`。
- 扮演「冷靜客觀的你自己」，不帶情緒偏誤地審視你目前的情況並給出反應。

---

## 🛠️ 工具腳本獨立使用 (給 Agent 或進階使用者)

你可以單獨呼叫這些工具來處理資料：

```bash
# 1. 聊天紀錄解析（支援單檔 --file 或多檔資料夾 --dir）
py -3 tools/chat_parser.py --dir data/chats/ --target "YourName" --format json --output parsed.json

# 2. 去識別化與去雜訊
py -3 tools/text_cleaner.py --file parsed.json --target "YourName" --deidentify --output cleaned.json

# 3. 查看目前生成的雙生檔案清單
py -3 tools/twin_writer.py --action list
```

---

## 📂 完整目錄結構

```
self-mirror/
├── twin_profile/            # 生成的數位雙生設定檔（私人資料，已 gitignore）
├── prompts/                 # LLM Prompt 提示詞模板
├── tools/                   # Python 前處理工具庫
├── exes/                    # 範例結構區塊（致敬 ex-skill）
├── docs/Architecture.md     # 系統架構與 Data Flow 詳細文件
├── build_twin.py            # 一鍵建構數位雙生主程式
├── talk_to_myself.py        # 鏡像互動主程式
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
