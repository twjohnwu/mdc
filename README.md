# mdc — 把內容整理成 Markdown 並複製到剪貼簿

Claude Code skill：把對話中的任何內容（總結、commit/branch 說明、review
筆記、報告、程式片段）整理成乾淨的 GitHub-flavored Markdown，寫入
scratchpad 檔案後用 `pbcopy` 放進 macOS 剪貼簿，並以
`pbpaste | cmp` 驗證複製成功。僅支援 macOS。

## 觸發方式

- 明說：`/mdc`
- 自然語言：「copy 到剪貼簿」「pbcopy」「給我可以貼的 markdown」、要求
  某段總結「用 md 格式」並帶有複製意圖——不需要說出 clipboard 這個詞。

## 安裝（雙軌）

- **源（single source of truth）**：本目錄 `SKILL.md`
- **安裝份**：`~/.claude/skills/mdc/SKILL.md`（session 啟動時載入；改動後
  要開新 session 才生效）

## 維護規則

改動一律先改本目錄的 `SKILL.md`，再複製覆蓋安裝份：

    cp SKILL.md ~/.claude/skills/mdc/SKILL.md

不要直接編輯安裝份；README 只留在源目錄、不複製過去。

## 設計筆記（2026-07-11 三鏡頭評審後）

- description 的觸發詞全部保留——skill 改名 `mdc` 後名稱不再帶語意，
  description 承擔全部觸發責任。
- `cmp` 驗證是本 skill 的核心價值：抓到剪貼簿靜默失敗；失敗時 retry 一次，
  再失敗誠實回報（常見原因：其他程序在 copy 與 verify 之間寫了剪貼簿）。
- 敏感內容留在 scratchpad 檔案裡——貼上完成後可要求刪除。
