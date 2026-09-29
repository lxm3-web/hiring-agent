#!/usr/bin/env python3
"""從公開的 Google Sheet 更新本機資料——G Drive 是資料來源，repo 內的檔只是備援快照。
抓不到（沒網路、環境擋 docs.google.com、Sheet 尚未公開、表頭對不上）就沿用快照，照樣能跑。只用標準庫。
csv 分頁→整張寫回 CSV（本機檔整欄留空＝要 Agent 產出的欄，不匯入）；docs 分頁（檔名,內容）→一列一個檔案。"""
import csv, io, os, sys, urllib.parse, urllib.request
SHEET_ID = "1w2aQyoc4oRNmVnooCNI9W2wWrQm0UJ42E0ADRecAgKQ"
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
JOBS = [('docs', '履歷', 'data/履歷', '檔名'), ('docs', '職缺說明', 'data', '檔名')]  # (kind, 分頁名, 本機路徑（csv=檔案／docs=資料夾）, 必要表頭)
def fetch(tab):
    u = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={urllib.parse.quote(tab)}"
    return list(csv.reader(io.StringIO(urllib.request.urlopen(u, timeout=15).read().decode("utf-8"))))
def merge(sheet, path):
    old = list(csv.reader(open(path, encoding="utf-8-sig")))
    want = old[0]
    skip = {h for j, h in enumerate(want) if not any(len(r) > j and r[j] for r in old[1:])}
    idx = {h: sheet[0].index(h) for h in want if h not in skip}
    return [want] + [[(r[idx[h]] if h in idx and idx[h] < len(r) else "") for h in want] for r in sheet[1:]]
def do_csv(rows, path):
    rows = merge(rows, path) if os.path.exists(path) else rows
    crlf = "\r\n" if os.path.exists(path) and b"\r\n" in open(path, "rb").read(4000) else "\n"
    bom = os.path.exists(path) and open(path, "rb").read(3) == b"\xef\xbb\xbf"
    with open(path, "w", encoding="utf-8-sig" if bom else "utf-8", newline="") as f:
        csv.writer(f, lineterminator=crlf).writerows(rows)
    return len(rows) - 1
def do_docs(rows, path):
    os.makedirs(path, exist_ok=True)
    for name, body in [r[:2] for r in rows[1:] if len(r) >= 2 and r[0]]:
        with open(os.path.join(path, os.path.basename(name)), "w", encoding="utf-8", newline="") as f: f.write(body + "\n")
    return len(rows) - 1
for kind, tab, local, key in JOBS:
    path = os.path.join(ROOT, local)
    try:
        rows = fetch(tab)
        while rows and not any(rows[-1]): rows.pop()
        if not rows or key not in rows[0]: raise ValueError("表頭對不上")
        n = (do_csv if kind == "csv" else do_docs)(rows, path)
        print(f"{tab:<10} {n} 筆（已從 Google Sheet 更新）→ {local}")
    except Exception as e:
        if os.path.exists(path): print(f"{tab:<10} 沿用快照（{e.__class__.__name__}: {e}）→ {local}")
        else: print(f"⚠️  {tab}：抓不到也沒有快照"); sys.exit(1)
