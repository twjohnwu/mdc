# mdc — 把內容整理成 Markdown 並複製到剪貼簿

Claude Code skill：把對話中的任何內容（總結、commit/branch 說明、review
筆記、報告、程式片段）整理成乾淨的 GitHub-flavored Markdown，寫入
scratchpad 檔案後用 `pbcopy` 放進 macOS 剪貼簿，並以
`pbpaste | cmp` 驗證複製成功。僅支援 macOS。

依內容來源路由到最便宜的寫手（已是檔案 / 需要組合 / 對話逐字稿 / 全新文字），
主 context 幾乎不吃到內容 token；對話逐字稿走 `scripts/session_to_md.py`
從 session transcript 萃取對話文字並複製到剪貼簿。

## 觸發方式

- 明說：`/mdc`
- 自然語言：「copy 到剪貼簿」「pbcopy」「給我可以貼的 markdown」、要求
  某段總結「用 md 格式」並帶有複製意圖——不需要說出 clipboard 這個詞。

## 目錄結構

- `SKILL.md` — skill 本體（single source of truth）
- `scripts/session_to_md.py` — 從 session transcript 萃取逐字稿並整理成
  Markdown（支援 `<session-id>`、`--last N`、`--all`、`--role`、`-o`、`--copy`）
- `README.md` — 本檔，只留在源目錄

## 安裝（雙軌）

- **源（single source of truth）**：本目錄 `SKILL.md` 與 `scripts/`
- **安裝份**：`~/.claude/skills/mdc/SKILL.md` 與 `~/.claude/skills/mdc/scripts/`
  （session 啟動時載入；改動後要開新 session 才生效）

## 維護規則

改動一律先改本目錄的 `SKILL.md`（或 `scripts/`），再複製覆蓋安裝份，
兩者都要同步：

    cp SKILL.md ~/.claude/skills/mdc/SKILL.md && cp -R scripts ~/.claude/skills/mdc/

不要直接編輯安裝份；README 只留在源目錄、不複製過去。

## 設計筆記（2026-07-11 三鏡頭評審後）

- description 的觸發詞全部保留——skill 改名 `mdc` 後名稱不再帶語意，
  description 承擔全部觸發責任。
- `cmp` 驗證是本 skill 的核心價值：抓到剪貼簿靜默失敗；失敗時 retry 一次，
  再失敗誠實回報（常見原因：其他程序在 copy 與 verify 之間寫了剪貼簿）。
- 敏感內容留在 scratchpad 檔案裡——貼上完成後可要求刪除。

## 設計筆記（2026-07-30 加入 routing 表與 scripts/）

- Routing 表的動機：依內容來源（已是檔案 / 需組合 / 對話逐字稿 / 全新文字）
  挑最便宜的寫手，讓內容 token 幾乎不進主 context——已是檔案就直接當
  `SOURCE`，需要組合就派一個便宜 agent 只帶指標（路徑、行號、git ref），
  絕不帶內容本身。
- 明訂「已在 subagent 內或 plan mode 中不派工」：plan mode 的狀態會傳染給
  被派的 agent，agent 在 plan mode 下無法真的寫檔或動剪貼簿，派下去只是
  拿回一份計畫而非實際完成的複製動作。
