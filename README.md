# TDCC Helper Tool

This repository provides tools to assist shareholders with the TDCC electronic voting process, including automated voting and screenshot features(currently only support Edge browser).

---

- [TDCC Helper Tool](#tdcc-helper-tool)
  - [English Manual](#english-manual)
    - [Build Command](#build-command)
    - [Usage](#usage)
      - [1. rename\_tool](#1-rename_tool)
      - [2. TDCC\_helper\_tool](#2-tdcc_helper_tool)
    - [Screenshot File Format Selection (Screenshot Mode)](#screenshot-file-format-selection-screenshot-mode)
    - [Command-Line Options](#command-line-options)
    - [Background Mode](#background-mode)
    - [Wait-Time Profiles and Auto-Adjust](#wait-time-profiles-and-auto-adjust)
    - [Timing Log (timing.log)](#timing-log-timinglog)
    - [Feedback, Suggestions, and Bug Reports](#feedback-suggestions-and-bug-reports)
    - [Contributing](#contributing)
    - [License and Development Notice](#license-and-development-notice)
    - [Environment Information](#environment-information)
  - [中文說明（繁體）](#中文說明繁體)
    - [建置指令](#建置指令)
    - [使用說明](#使用說明)
      - [1. rename\_tool](#1-rename_tool-1)
      - [2. TDCC\_helper\_tool](#2-tdcc_helper_tool-1)
    - [截圖檔案格式選擇（Screenshot Mode）](#截圖檔案格式選擇screenshot-mode)
    - [命令列參數](#命令列參數)
    - [背景模式](#背景模式)
    - [等待時間範本與自動調整](#等待時間範本與自動調整)
    - [耗時紀錄（timing.log）](#耗時紀錄timinglog)
    - [意見回饋、建議與問題回報](#意見回饋建議與問題回報)
    - [參與開發說明](#參與開發說明)
    - [授權與開發注意事項](#授權與開發注意事項)
    - [環境資訊](#環境資訊)


---

## English Manual

### Build Command

```
pyinstaller -F ./TDCC_helper_tool.py
pyinstaller -F ./rename_tool.py

we introduce github workflow to build the executable files for the tools(commit 0c3b30577), so you can get the executable files directly from "Actions" tab in this repository.
```

---

### Usage

#### 1. rename_tool

**How to use:**
- Double-click the executable or run the script with Python.

**What it does:**
- Moves and renames all PNG files from `./screenshots/{user_id}/*.png` to `./screenshots/all/*_{user_id}.png`.
- This helps consolidate screenshots from different shareholder IDs into a single folder, with filenames indicating their original ID.

---

#### 2. TDCC_helper_tool
This program assists shareholders in the TDCC voting process, including automated voting and screenshot features. It helps minority shareholders receive shareholder meeting souvenirs.
**Step-by-step usage:**

1. **Start the program**
   - Double-click the executable or run the script with Python.

2. **If unfinished screenshots are detected**
   - The tool will display:  
     `Last time have unfinished screenshot, do you want to continue? (Y/N) :`
   - If you enter `Y`, it will guide you through completing those screenshots first.

3. **Main menu**
   - The tool will display:
     ```
     (1) all accounts vote+take screenshot
     (2) take screenshot of specific stocks
     (3) exit
     please select:
     ```
   - Enter `1`, `2`, or `3`.

4. **If you select (1) all accounts vote + take screenshot**
   - The tool will check for existing settings. If not found or you choose to reconfigure, you will be prompted:
     - `please enter the shareholder ID(台灣的身分證字號), one ID per line, end with 'end' :`  
       (Enter each ID, then type `end` to finish)
     - `please enter the default vote option (accept/opposite/abstain):`  
       (Choose one: `accept`, `opposite`, or `abstain`)
     - For manual voting keywords:
       - `please enter the keyword to accept, one keyword per line, end with 'end' :`
       - `please enter the keyword to opposite, one keyword per line, end with 'end' :`
       - `please enter the keyword to abstain, one keyword per line, end with 'end' :`
     - After each section, you will be asked to confirm:
       - `do you want to save the setting?(y/n)?`
       - `do you want to use the above setting?(y/n)?`
   - Each run, the tool asks which timing profile to use (fast / stable) and whether to enable auto-adjust. With auto-adjust on, when a robot check fails the tool lengthens the waits, restarts the browser and logs in again (up to 3 retries per account, then it falls back to manual handling). Wait times of every step are stored in `timing_setting.conf` and can be edited; per-step timings are appended to `timing.log`.
   - For each shareholder ID:
     - The tool will automatically log in, vote according to your settings, and take screenshots for each stock.
     - All screenshots are saved in `./screenshots/{id}/`.
   - After all accounts are processed, the tool logs out and closes the browser.

5. **If you select (2) Take screenshot of specific stocks**
   - The tool will prompt:
     - `Please enter the ID number to take screenshots:(-1 to exit)`
     - `Please enter the stock ID to take screenshots, multiple stock IDs should be separated by ",":(-1 to exit)`
   - The tool will log in and take screenshots for the specified stocks.

6. **Exit**
   - Select (3) to exit the program.

**Notes:**
- You can modify voting content at any time; it will not affect your actual voting intent.
- The script is for assistance only and does not take responsibility for any consequences.

---

### Screenshot File Format Selection (Screenshot Mode)

During the initial setup or when reconfiguring, you will be prompted to select a screenshot file format (screenshot mode). This determines how your screenshots are organized and named.

**Step-by-step selection:**
1. When prompted:
   ```
   Choose screenshot file structure:
   1. Current structure (screenshots per user ID folder)
   2. All screenshots in one folder, filename {stock_id}_{stock_name}_{stock_account_id}.png
   3. All screenshots in one folder, filename {stock_id}_{stock_name}_{user_id}.png
   Please enter 1, 2, or 3:
   ```
2. Enter the number for your preferred mode and press Enter.
   - Mode 1: Each user ID has its own folder (default)
   - Mode 2: All screenshots in one folder, filename includes stock account ID
   - Mode 3: All screenshots in one folder, filename includes user ID
3. The tool will use this mode for all future screenshots until you change it again.

---

### Command-Line Options

| Option | Description |
|---|---|
| `-y`, `--yes` | Skip all confirmations and use the saved settings, including the saved wait-time profile and auto-adjust choice. Runs menu item (1) once and exits. Useful for scheduled tasks. |
| `-b`, `--browser {Edge,Chrome,Firefox}` | Choose the browser. If omitted, the tool tries Edge, then Chrome, then Firefox. |
| `-d`, `--driver_path PATH` | Use a specific WebDriver executable instead of the automatically managed one. |
| `--browser-log` | Show the browser and WebDriver background logs (hidden by default). |
| `--background` | Run the browser window off-screen so it does not interfere with your mouse, keyboard and other work. See [Background Mode](#background-mode). |

Example:
```
TDCC_helper_tool.exe --background -b Chrome
```

---

### Background Mode

`--background` moves the browser window off-screen (to coordinates -32000, -32000) instead of hiding it. The page keeps rendering normally, so login, voting and screenshots work as usual, but the window does not appear on your desktop and does not steal keyboard focus.

**First-time setup (important):**
1. Run the tool once **without** `--background`.
2. When the login page shows the permission prompt "access other apps and services on this device" (Local Network Access), click **Allow**.
3. Close the tool. Later runs with `--background` will not ask again.

The choice is remembered in the `browser_profile/` folder, created next to the executable (Chrome and Edge only). It is a dedicated profile and does not touch your normal browser profile.

**Notes:**
- If you delete `browser_profile/` (or the whole folder containing the executable), the permission must be granted again.
- Only one browser can use `browser_profile/` at a time. If the tool exited abnormally and a browser is still running in the background, end it in Task Manager before starting again.
- When a robot-check failure needs your manual action, the window is moved back on screen temporarily and moved off again after you press Enter.
- Firefox has no start-position option: its window may flash briefly before the first login, and it does not use `browser_profile/`.

---

### Wait-Time Profiles and Auto-Adjust

The tool waits between actions (login, clicks, page loads, screenshots). Every wait is defined per step in `timing_setting.conf` and grouped into two profiles:

| Profile | Description | Reference: login / one screenshot |
|---|---|---|
| Fast | Shorter waits; most waits end as soon as the page is ready | about 5 s / 3 s |
| Stable | The conservative original pace | about 22 s / 10 s |

The reference values were measured on one Windows 11 machine and will vary with your network and the TDCC server. Voting clicks use the same delays in both profiles, so voting itself is not much faster; the saving is mainly in login and screenshots.

**At startup** the tool asks:
1. Which profile to use: `1` fast, `2` stable (press Enter to keep the last choice).
2. Whether to enable auto-adjust (`y`/`n`, press Enter to keep the last choice).

Your choices are saved. With `-y`, the saved choices are used. On the first run the defaults are stable and auto-adjust off.

The old "run speed (1~30)" prompt has been removed. An existing `program_setting.conf` still loads; its speed value is ignored.

#### Auto-adjust

Applies to menu item (1) (voting). When "robot verification failed" appears and auto-adjust is on, the tool:
1. Logs out and closes the browser.
2. Cools down (default 60 seconds).
3. Multiplies all waits by a factor (default x1.5 each time, up to x4).
4. Reopens the browser, logs in again and continues with the unfinished stocks.

Each account is retried at most 3 times. After that the tool falls back to the manual flow (it asks you to complete the verification and press Enter), and auto-adjust is restored for the next account. The multiplier only lasts for the current run; the next run starts from the profile values again. Longer waits do not guarantee that the verification will pass.

#### timing_setting.conf

Generated next to the executable on the first run; every item has a comment describing it. You can edit it with any text editor.
- Your edits are kept. The startup choices only rewrite the `profile` and `auto_adjust` lines.
- Items missing from the file use the built-in defaults; unknown items are ignored with a warning.
- If the file cannot be parsed, the tool prints the reason and exits. Delete the file to regenerate it.

Value format: `name = 2` is a fixed number of seconds; `name = 0.5, 1.2` is a random range (minimum, maximum).

`[general]` section:

| Key | Default | Description |
|---|---|---|
| `profile` | `stable` | `fast` or `stable` |
| `auto_adjust` | `no` | `yes` or `no` |
| `cooldown_seconds` | `60` | Cool-down before logging in again after a robot check |
| `factor_step` | `1.5` | Multiplier applied to all waits each time a robot check is detected |
| `factor_max` | `4` | Upper limit of the multiplier |
| `max_retries` | `3` | Maximum automatic retries per account before falling back to manual |

The `[fast]` and `[stable]` sections hold the per-step values. Item names start with a prefix:

| Prefix | Used for |
|---|---|
| `login_`, `terms_`, `go_`, `post_login_`, `welshas_`, `account_start_wait` | Login and the start of each account |
| `vote_` | Voting |
| `shot_` | Screenshots |
| `*_timeout` | Upper limit (seconds) for waiting for a page or element |
| `*_poll` | Polling interval (seconds) |

Items ending in `_poll` or `_timeout` are not multiplied by the auto-adjust factor; all other items are. Setting an item to `0` removes that wait (for example `vote_next_focus = 0` skips the "focus another button first" step). Lowering waits too far may make robot checks more likely.

---

### Timing Log (timing.log)

The tool appends a line to `timing.log` (next to the executable) for every step. It never contains ID numbers, and you can delete the file at any time.

```
115/10/24 15:08:04 shot_query_after_click 延遲 0.90 秒 x1
115/10/24 15:08:05 shot_detail_ready 等待元素 0.11 秒 x1
115/10/24 15:08:06 截圖單檔 3.4 秒
```

Format: `date time step type seconds x multiplier` (the date uses the ROC calendar).

| Type | Meaning |
|---|---|
| 延遲 (delay) | A wait the tool added on purpose (random human-like pause or fixed wait) |
| 等待元素 (wait for element) | Time from the action until the expected element appeared |
| 逾時 (timeout) | The element did not appear within the limit |

Summary lines (without a step name) record total time per login (`登入`), per voted stock (`投票單檔`), per screenshot (`截圖單檔`), and the moment a robot check failed (`機器人驗證失敗`).

To find what to tune, look for steps with large `延遲` seconds and lower the matching item in the `[fast]` section of `timing_setting.conf`; many `逾時` lines mean the limit or the page is the problem rather than the delay.

---

### Feedback, Suggestions, and Bug Reports

We highly welcome your feedback, opinions, suggestions, and bug reports! You can:
- Open an issue or start a discussion in this repository on GitHub
- Contact me directly (see my GitHub profile for contact information)
- Discuss in the Line community chat

Your input helps make this tool better for everyone.

---

### Contributing

Contributions are welcome! If you are a developer and want to help improve this project:
1. Fork this repository on GitHub
2. Create a new branch for your feature or fix
3. Commit your changes and push to your fork
4. Open a Pull Request (PR) to this repository

For a step-by-step guide, see: https://docs.github.com/en/get-started/quickstart/contributing-to-projects

---

### License and Development Notice

- Anyone is welcome to further develop or modify this program, **as long as**:
  1. There is **no direct or indirect commercial use** (unless you have my explicit permission).
  2. If you distribute a modified version elsewhere (without contributing back to this repository), you **must include a statement** that your version is based on this repository.

Thank you for respecting these terms and for supporting open-source collaboration!

---

### Environment Information

If you encounter issues running this program, here's environment versions. The following versions are known to work and recommended:

- **Python:** 3.13.3
- **PyInstaller:** 6.13.0
- **pip:** 25.1.1
- **selenium:** 4.32.0

You can use `pip` to install the following dependencies.

```shell
python3 -m pip install -r requirements.txt
```

---

## 中文說明（繁體）

### 建置指令

```
pyinstaller -F ./TDCC_helper_tool.py
pyinstaller -F ./rename_tool.py

我們在 commit 0c3b30577 中引入了 GitHub 工作流程來建置工具的可執行檔，您可以直接從本專案的 "Actions" 標籤頁下載可執行檔。

# 20260429 by LukeLai
若要指定產出的資料夾，使用參數distpath
pyinstaller -F --distpath .\release .\TDCC_helper_tool.py

```

---

### 使用說明

#### 1. rename_tool

**使用方式：**
- 直接雙擊執行檔或用 Python 執行腳本。

**功能說明：**
- 將 `./screenshots/{user_id}/*.png` 目錄下所有 PNG 檔案，移動並重新命名到 `./screenshots/all/` 資料夾，檔名格式為 `*_{user_id}.png`。
- 方便將不同股東 ID 的截圖集中管理，並保留來源 ID 資訊於檔名。

---

#### 2. TDCC_helper_tool
此程式用於協助股東進行 TDCC 投票，包含自動投票及截圖功能。以幫助零股股東領取股東會紀念品
**操作步驟說明：**

1. **啟動程式**
   - 直接雙擊執行檔或用 Python 執行腳本。

2. **若偵測到上次未完成的截圖**
   - 程式會顯示：  
     `Last time have unfinished screenshot, do you want to continue? (Y/N) :`  
     （上次有未完成的截圖，是否繼續？輸入 Y 繼續）
   - 若輸入 `Y`，會先引導你完成這些截圖。

3. **主選單**
   - 程式會顯示：
     ```
     (1) all accounts vote+take screenshot（所有帳號自動投票並截圖）
     (2) take screenshot of specific stocks（指定股票截圖）
     (3) exit（離開）
     please select:（請選擇）
     ```
   - 輸入 `1`、`2` 或 `3`。

4. **選擇 (1) 所有帳號自動投票並截圖**
   - 程式會檢查設定，若無設定或選擇重新設定，會依序詢問：
     - `please enter the shareholder ID(台灣的身分證字號), one ID per line, end with 'end' :`  
       股東身分證字號（每行一個，輸入 end 結束）
     - `please enter the default vote option (accept/opposite/abstain):`  
       預設投票方式（accept=贊成，opposite=反對，abstain=棄權）
     - 關鍵字設定（可選，依序輸入，每行一個，輸入 end 結束）：
       - `please enter the keyword to accept, one keyword per line, end with 'end' :`（贊成關鍵字）
       - `please enter the keyword to opposite, one keyword per line, end with 'end' :`（反對關鍵字）
       - `please enter the keyword to abstain, one keyword per line, end with 'end' :`（棄權關鍵字）
     - 設定完成後會請你確認：
       - `do you want to save the setting?(y/n)?`（是否儲存設定）
       - `do you want to use the above setting?(y/n)?`（是否使用上述設定）
   - 每次執行會先詢問要使用的等待時間範本（快速 / 穩定），以及是否啟用自動調整。啟用後，若偵測到機器人驗證失敗，程式會拉長等待時間、重開瀏覽器並重新登入（每個帳號最多重試 3 次，超過則改為手動處理）。各步驟的等待時間存放在 `timing_setting.conf`，可自行修改；每個步驟的耗時會追加記錄在 `timing.log`。
   - 每個股東帳號會自動登入、依設定自動投票，並為每檔股票截圖。
   - 所有截圖會儲存於 `./screenshots/{id}/` 資料夾。
   - 全部完成後會自動登出並關閉瀏覽器。

5. **選擇 (2) 指定股票截圖**
   - 程式會詢問：
     - `Please enter the ID number to take screenshots:(-1 to exit)`  
       輸入股東身分證字號（-1 離開）
     - `Please enter the stock ID to take screenshots, multiple stock IDs should be separated by ",":(-1 to exit)`  
       輸入股票代號（多個用逗號分隔，如 2330,2317，(-1 離開)）
   - 程式會自動登入並為指定股票截圖。

6. **離開程式**
   - 選擇 (3) 離開。

**注意事項：**
- 投票內容可隨時修改，不影響實際投票意願。
- 本工具僅供輔助，使用造成的任何後果請自行負責。

---

### 截圖檔案格式選擇（Screenshot Mode）

首次設定或重新設定時，程式會詢問您選擇截圖檔案格式（screenshot mode），決定截圖的儲存方式與檔名。

**選擇步驟：**
1. 當程式詢問：
   ```
   Choose screenshot file structure:
   1. Current structure (screenshots per user ID folder)
   2. All screenshots in one folder, filename {stock_id}_{stock_name}_{stock_account_id}.png
   3. All screenshots in one folder, filename {stock_id}_{stock_name}_{user_id}.png
   Please enter 1, 2, or 3:
   ```
2. 輸入對應數字並按 Enter。
   - 模式1：每個股東ID一個資料夾（預設）
   - 模式2：所有截圖集中一個資料夾，檔名含股東帳號
   - 模式3：所有截圖集中一個資料夾，檔名含身分證字號
3. 之後所有截圖將依此模式儲存，除非重新設定。

---

### 命令列參數

| 參數 | 說明 |
|---|---|
| `-y`, `--yes` | 免確認模式：略過所有確認，直接套用已儲存的設定（含已儲存的等待時間範本與自動調整選擇）。會執行一次選單 (1) 後結束，適合排程使用。 |
| `-b`, `--browser {Edge,Chrome,Firefox}` | 指定瀏覽器。未指定時依序嘗試 Edge、Chrome、Firefox。 |
| `-d`, `--driver_path PATH` | 指定自訂的 WebDriver 執行檔，不使用自動管理的版本。 |
| `--browser-log` | 顯示瀏覽器與 WebDriver 的背景日誌（預設隱藏）。 |
| `--background` | 將瀏覽器視窗移到螢幕外執行，不干擾你的滑鼠、鍵盤與其他工作。詳見[背景模式](#背景模式)。 |

範例：
```
TDCC_helper_tool.exe --background -b Chrome
```

---

### 背景模式

`--background` 會把瀏覽器視窗移到螢幕外（座標 -32000, -32000），而不是隱藏。頁面仍然正常繪製，所以登入、投票、截圖都照常運作，但視窗不會出現在桌面上，也不會搶走鍵盤焦點。

**第一次使用（重要）：**
1. 先**不要加** `--background` 執行一次。
2. 登入頁跳出「存取這部裝置上的其他應用程式和服務」（本機網路存取）的權限提示時，按**允許**。
3. 關閉程式。之後加上 `--background` 就不會再詢問。

這個選擇會記錄在執行檔旁邊的 `browser_profile/` 資料夾（僅 Chrome、Edge）。它是專用的 profile，不會動到你平常使用的瀏覽器設定。

**注意事項：**
- 刪除 `browser_profile/`（或整個執行檔所在的資料夾）後，需要重新按一次「允許」。
- 同一時間只有一個瀏覽器能使用 `browser_profile/`。如果程式異常結束、瀏覽器還留在背景，請先在工作管理員結束它再重新啟動。
- 遇到需要你手動處理的機器人驗證時，視窗會暫時移回螢幕上，按 Enter 之後再移到螢幕外。
- Firefox 沒有啟動時指定位置的參數：第一次登入前視窗可能會閃一下，也不使用 `browser_profile/`。

---

### 等待時間範本與自動調整

程式在每個動作之間（登入、點擊、頁面載入、截圖）都有等待。所有等待時間都依步驟定義在 `timing_setting.conf`，並分成兩個範本：

| 範本 | 說明 | 參考：登入 / 單檔截圖 |
|---|---|---|
| 快速 | 等待時間較短，多數等待在頁面就緒時就結束 | 約 5 秒 / 3 秒 |
| 穩定 | 保守的原始節奏 | 約 22 秒 / 10 秒 |

參考值是在一台 Windows 11 電腦上量測的，實際會依你的網路與 TDCC 伺服器而不同。投票時的點擊延遲在兩個範本相同，所以投票本身不會快太多，主要加速在登入與截圖。

**啟動時**程式會詢問：
1. 要使用的範本：`1` 快速、`2` 穩定（直接按 Enter 沿用上次的選擇）。
2. 是否啟用自動調整（`y`/`n`，直接按 Enter 沿用上次的選擇）。

選擇會被儲存；使用 `-y` 時沿用已儲存的選擇。第一次執行的預設為穩定、不啟用自動調整。

原本的「執行速度（1~30）」詢問已移除。既有的 `program_setting.conf` 仍可讀取，其中的速度值會被忽略。

#### 自動調整

適用於選單 (1)（投票）。啟用後，只要出現「我不是機器人驗證失敗」，程式會：
1. 登出並關閉瀏覽器。
2. 冷卻一段時間（預設 60 秒）。
3. 把所有等待時間乘上倍率（預設每次 ×1.5，上限 ×4）。
4. 重新開啟瀏覽器並登入，接續未完成的股票。

每個帳號最多重試 3 次；超過後會改回手動流程（請你完成驗證後按 Enter），並在下一個帳號恢復自動調整。倍率只在本次執行有效，下次執行會從範本的原始值開始。拉長等待時間不保證能通過驗證。

#### timing_setting.conf

第一次執行時會產生在執行檔旁邊，每個項目都有註解說明，可以用任何文字編輯器修改。
- 你的修改會被保留；啟動時的選擇只會改寫 `profile` 與 `auto_adjust` 兩行。
- 檔案裡缺少的項目使用內建預設值；不認得的項目會顯示警告並忽略。
- 檔案無法解析時，程式會顯示原因並結束；刪除該檔案即可重新產生。

數值格式：`name = 2` 為固定秒數；`name = 0.5, 1.2` 為隨機範圍（最小, 最大）。

`[general]` 區段：

| 參數 | 預設值 | 說明 |
|---|---|---|
| `profile` | `stable` | `fast` 或 `stable` |
| `auto_adjust` | `no` | `yes` 或 `no` |
| `cooldown_seconds` | `60` | 偵測到機器人驗證後，重新登入前的冷卻時間 |
| `factor_step` | `1.5` | 每次偵測到機器人驗證，所有等待時間乘上的倍數 |
| `factor_max` | `4` | 倍率上限 |
| `max_retries` | `3` | 每個帳號自動重試的最大次數，超過後改為手動 |

`[fast]`、`[stable]` 區段存放各步驟的數值，項目名稱以前綴區分：

| 前綴 | 用途 |
|---|---|
| `login_`、`terms_`、`go_`、`post_login_`、`welshas_`、`account_start_wait` | 登入與每個帳號開始前 |
| `vote_` | 投票 |
| `shot_` | 截圖 |
| `*_timeout` | 等待頁面或元素的上限（秒） |
| `*_poll` | 輪詢間隔（秒） |

以 `_poll`、`_timeout` 結尾的項目不會乘上自動調整的倍率，其餘項目都會。把某個項目設為 `0` 就是取消該等待（例如 `vote_next_focus = 0` 會略過「先聚焦其他按鈕」的步驟）。把等待調得太短，可能讓機器人驗證更容易出現。

---

### 耗時紀錄（timing.log）

程式會把每個步驟追加記錄在執行檔旁邊的 `timing.log`。內容不含身分證字號，可隨時刪除。

```
115/10/24 15:08:04 shot_query_after_click 延遲 0.90 秒 x1
115/10/24 15:08:05 shot_detail_ready 等待元素 0.11 秒 x1
115/10/24 15:08:06 截圖單檔 3.4 秒
```

格式：`日期 時間 步驟 類型 秒數 x倍率`（日期為民國年）。

| 類型 | 意義 |
|---|---|
| 延遲 | 程式刻意加入的等待（隨機人類化停頓或固定等待） |
| 等待元素 | 從動作開始到預期元素出現所花的時間 |
| 逾時 | 在上限內元素沒有出現 |

沒有步驟名稱的行是彙總：每次登入（`登入`）、每檔投票（`投票單檔`）、每檔截圖（`截圖單檔`）的總耗時，以及機器人驗證失敗發生的時間點（`機器人驗證失敗`）。

要找出可以調整的地方，請看 `延遲` 秒數較大的步驟，再到 `timing_setting.conf` 的 `[fast]` 區段降低對應的項目；如果有很多 `逾時`，代表問題在上限或頁面本身，而不是延遲。

---

### 意見回饋、建議與問題回報

非常歡迎您提供任何意見、建議或回報問題！您可以：
- 在本專案的 GitHub issue 或 discussion 區留言
- 直接聯絡我（請參考我的 GitHub 個人頁面聯絡方式）
- 在Line社群中討論

您的回饋將有助於讓這個工具變得更好。

---

### 參與開發說明

歡迎任何開發者參與本專案！如果您想貢獻程式碼：
1. 先 fork 本專案到您的 GitHub 帳號
2. 建立新分支進行開發或修正
3. commit 並 push 到您的 fork
4. 透過 Pull Request (PR) 回報到本專案

詳細教學可參考：https://docs.github.com/zh-tw/get-started/quickstart/contributing-to-projects

---

### 授權與開發注意事項

- 歡迎任何人進行二次開發或修改本程式，**但必須遵守以下條件**：
  1. 不得直接或間接用於商業用途（除非明確取得本人同意）。
  2. 若有其他分發（未回饋本專案），**必須明確標示**本程式是基於本專案開發。

感謝您的尊重與支持，也歡迎大家共同推動開源合作！

---
### 環境資訊
若您在執行程式時遇到問題，以下是已知可正常運作的環境版本：
- **Python:** 3.13.3
- **PyInstaller:** 6.13.0
- **pip:** 25.1.1
- **selenium:** 4.32.0
- 
你可以使用`pip`安裝這些依賴項：
```shell
python3 -m pip install -r requirements.txt
```