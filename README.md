# hiring-agent — 招募流程專員（Agent 版）

claude.ai/code 選這個 repo（或本機 `claude`）→ 說「人資的指示在 inbox，幫我篩」→ 評分總表、面試時段、邀請信、面試題、備取／婉拒信、主管評核表寫到 `outbox/` → 看完說「好，發下去」。

**個資**：本 repo 只放去識別化的虛構履歷；真實履歷請在本機執行並自行保管代號對照表。**demo 完歸零**：`inbox/*.done` 改回 `.txt`、清 `outbox/`、log 只留表頭。
