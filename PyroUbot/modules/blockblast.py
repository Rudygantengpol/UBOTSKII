import os
import json
import random
from datetime import datetime
from pytz import timezone

from PyroUbot import *

__MODULE__ = "blockblast"
__HELP__ = """
<blockquote><b>Game Block Blast (Mini)</b>

- <code>.bbstart</code> → mulai game & spawn 3 block
- <code>.bb</code> → lihat board
- <code>.bbplace b x y</code> → taruh block (b=1-3, x=1-8, y=1-8)
- <code>.bbskip</code> → buang 1 block (biaya uang)
- <code>.bbend</code> → selesai & tukar score jadi uang
- <code>.bbtop</code> → leaderboard score tertinggi</blockquote>
"""

TZ = timezone("Asia/Jakarta")
DATA_DIR = "data"
DB_FILE = os.path.join(DATA_DIR, "gacha.json")
os.makedirs(DATA_DIR, exist_ok=True)

SIZE = 8
SKIP_COST = 80
REWARD_RATE = 2  # score -> uang

# beberapa bentuk block (list of (dx,dy))
SHAPES = [
    # single
    [(0,0)],
    # 1x2, 1x3
    [(0,0),(1,0)],
    [(0,0),(2,0),(1,0)],
    # 2x2
    [(0,0),(1,0),(0,1),(1,1)],
    # 3x1 vertical/horizontal (we treat rotations with alt shapes)
    [(0,0),(0,1),(0,2)],
    # L shapes
    [(0,0),(0,1),(0,2),(1,2)],
    [(0,0),(1,0),(2,0),(0,1)],
    [(0,0),(1,0),(1,1)],
    # T shape
    [(0,0),(1,0),(2,0),(1,1)],
    # Z shape
    [(0,0),(1,0),(1,1),(2,1)],
    [(0,1),(1,1),(1,0),(2,0)],
]

def _load_db():
    if not os.path.exists(DB_FILE):
        return {"users": {}}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"users": {}}

def _save_db(db):
    tmp = DB_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DB_FILE)

def _get_user(db, user_id: int):
    uid = str(user_id)
    if uid not in db["users"]:
        db["users"][uid] = {"uang": 0, "blockblast": None}
    u = db["users"][uid]
    u.setdefault("uang", 0)
    u.setdefault("blockblast", None)
    return u

def _new_board():
    return [[0 for _ in range(SIZE)] for _ in range(SIZE)]

def _rand_block():
    shape = random.choice(SHAPES)
    # normalize to (min dx/dy) = 0
    minx = min(p[0] for p in shape)
    miny = min(p[1] for p in shape)
    norm = [(x-minx, y-miny) for x,y in shape]
    w = max(p[0] for p in norm) + 1
    h = max(p[1] for p in norm) + 1
    return {"cells": norm, "w": w, "h": h}

def _ensure_bb(u):
    if u.get("blockblast") is None:
        u["blockblast"] = {
            "active": False,
            "board": _new_board(),
            "blocks": [],
            "score": 0,
            "best": 0,
            "ts": datetime.now(TZ).isoformat()
        }
    else:
        bb = u["blockblast"]
        bb.setdefault("active", False)
        bb.setdefault("board", _new_board())
        bb.setdefault("blocks", [])
        bb.setdefault("score", 0)
        bb.setdefault("best", 0)

def _board_to_text(board):
    # 0 kosong = ⬛, terisi = 🟦
    lines = []
    header = "   " + " ".join([str(i) for i in range(1, SIZE+1)])
    lines.append(header)
    for y in range(SIZE):
        row = []
        for x in range(SIZE):
            row.append("🟦" if board[y][x] else "⬛")
        lines.append(f"{y+1:>2} " + " ".join(row))
    return "\n".join(lines)

def _block_preview(block):
    w, h = block["w"], block["h"]
    grid = [["⬛" for _ in range(w)] for _ in range(h)]
    for x,y in block["cells"]:
        grid[y][x] = "🟩"
    return "\n".join("".join(r) for r in grid)

def _can_place(board, block, x0, y0):
    for dx, dy in block["cells"]:
        x = x0 + dx
        y = y0 + dy
        if x < 0 or y < 0 or x >= SIZE or y >= SIZE:
            return False
        if board[y][x] == 1:
            return False
    return True

def _place(board, block, x0, y0):
    for dx, dy in block["cells"]:
        board[y0+dy][x0+dx] = 1

def _clear_lines(board):
    cleared = 0
    # rows
    full_rows = [y for y in range(SIZE) if all(board[y][x] == 1 for x in range(SIZE))]
    for y in full_rows:
        for x in range(SIZE):
            board[y][x] = 0
    cleared += len(full_rows)

    # cols
    full_cols = [x for x in range(SIZE) if all(board[y][x] == 1 for y in range(SIZE))]
    for x in full_cols:
        for y in range(SIZE):
            board[y][x] = 0
    cleared += len(full_cols)
    return cleared

def _has_any_move(board, blocks):
    for blk in blocks:
        for y in range(SIZE):
            for x in range(SIZE):
                if _can_place(board, blk, x, y):
                    return True
    return False

@PY.UBOT("bbstart")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_bb(u)
    bb = u["blockblast"]

    bb["active"] = True
    bb["board"] = _new_board()
    bb["blocks"] = [_rand_block(), _rand_block(), _rand_block()]
    bb["score"] = 0
    bb["ts"] = datetime.now(TZ).isoformat()

    _save_db(db)

    blocks_txt = []
    for i, blk in enumerate(bb["blocks"], start=1):
        blocks_txt.append(f"<b>Block {i}</b>\n<code>{_block_preview(blk)}</code>")
    await message.reply(
        "<blockquote><b>🧩 BLOCK BLAST START!</b>\n"
        f"{message.from_user.mention}\n\n"
        f"<b>Score:</b> <code>{bb['score']}</code>\n\n"
        f"<code>{_board_to_text(bb['board'])}</code>\n\n"
        + "\n\n".join(blocks_txt)
        + "\n\nCara main: <code>.bbplace b x y</code> (b=1-3, x/y=1-8)</blockquote>"
    )

@PY.UBOT("bb")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_bb(u)
    bb = u["blockblast"]

    if not bb.get("active"):
        _save_db(db)
        return await message.reply("<blockquote>Game belum mulai. Ketik <code>.bbstart</code></blockquote>")

    blocks_txt = []
    for i, blk in enumerate(bb["blocks"], start=1):
        blocks_txt.append(f"<b>Block {i}</b>\n<code>{_block_preview(blk)}</code>")

    _save_db(db)
    await message.reply(
        "<blockquote><b>🧩 BLOCK BLAST</b>\n"
        f"{message.from_user.mention}\n\n"
        f"<b>Score:</b> <code>{bb['score']}</code>\n"
        f"<b>Best:</b> <code>{bb.get('best',0)}</code>\n\n"
        f"<code>{_board_to_text(bb['board'])}</code>\n\n"
        + "\n\n".join(blocks_txt)
        + "\n\n<code>.bbplace b x y</code> | <code>.bbskip</code> | <code>.bbend</code></blockquote>"
    )

@PY.UBOT("bbplace")
async def _(client, message):
    parts = (message.text or "").split()
    if len(parts) < 4:
        return await message.reply("<blockquote>Format: <code>.bbplace b x y</code>\nContoh: <code>.bbplace 2 4 5</code></blockquote>")

    try:
        b_idx = int(parts[1])
        x = int(parts[2]) - 1
        y = int(parts[3]) - 1
    except:
        return await message.reply("<blockquote>Parameter harus angka.</blockquote>")

    if b_idx < 1 or b_idx > 3:
        return await message.reply("<blockquote>Block harus 1-3.</blockquote>")

    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_bb(u)
    bb = u["blockblast"]

    if not bb.get("active"):
        _save_db(db)
        return await message.reply("<blockquote>Game belum mulai. Ketik <code>.bbstart</code></blockquote>")

    blocks = bb["blocks"]
    if len(blocks) < b_idx:
        _save_db(db)
        return await message.reply("<blockquote>Block itu sudah kepakai/ga ada.</blockquote>")

    blk = blocks[b_idx - 1]
    board = bb["board"]

    if not _can_place(board, blk, x, y):
        _save_db(db)
        return await message.reply("<blockquote>❌ Tidak bisa taruh di posisi itu. Coba koordinat lain.</blockquote>")

    # place
    _place(board, blk, x, y)
    # score: + jumlah kotak
    bb["score"] += len(blk["cells"])

    # remove used block
    blocks.pop(b_idx - 1)

    # clear lines bonus
    cleared = _clear_lines(board)
    if cleared > 0:
        # bonus score per line
        bb["score"] += cleared * 8

    # respawn kalau block habis
    if len(blocks) == 0:
        bb["blocks"] = [_rand_block(), _rand_block(), _rand_block()]

    # update best
    bb["best"] = max(int(bb.get("best", 0)), int(bb["score"]))

    # cek game over (ga ada move)
    if not _has_any_move(board, bb["blocks"]):
        reward = int(bb["score"]) * REWARD_RATE
        u["uang"] = int(u["uang"]) + reward
        bb["active"] = False
        _save_db(db)
        return await message.reply(f"""
<blockquote><b>💥 GAME OVER!</b>
{message.from_user.mention}

<b>Final Score:</b> <code>{bb['score']}</code>
<b>Reward:</b> <code>+{reward} uang</code>
<b>Saldo:</b> <code>{u['uang']}</code>

Main lagi: <code>.bbstart</code></blockquote>
""")

    _save_db(db)

    await message.reply(f"""
<blockquote><b>✅ BERHASIL DITARUH</b>
{message.from_user.mention}

<b>Score:</b> <code>{bb['score']}</code>
<b>Clear line:</b> <code>{cleared}</code>

<code>{_board_to_text(board)}</code>

Lihat block: <code>.bb</code></blockquote>
""")

@PY.UBOT("bbskip")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_bb(u)
    bb = u["blockblast"]

    if not bb.get("active"):
        _save_db(db)
        return await message.reply("<blockquote>Game belum mulai. Ketik <code>.bbstart</code></blockquote>")

    if int(u["uang"]) < SKIP_COST:
        _save_db(db)
        return await message.reply(f"<blockquote>❌ Uang kurang untuk skip.\nButuh: <code>{SKIP_COST}</code> | Saldo: <code>{u['uang']}</code></blockquote>")

    if not bb["blocks"]:
        bb["blocks"] = [_rand_block(), _rand_block(), _rand_block()]

    # buang 1 block random
    removed = bb["blocks"].pop(random.randrange(len(bb["blocks"])))
    bb["blocks"].append(_rand_block())
    u["uang"] = int(u["uang"]) - SKIP_COST

    _save_db(db)
    await message.reply(f"""
<blockquote><b>🔄 SKIP BERHASIL</b>
{message.from_user.mention}

<b>Biaya:</b> <code>-{SKIP_COST} uang</code>
<b>Saldo:</b> <code>{u['uang']}</code>

Gunakan <code>.bb</code> untuk lihat block baru.</blockquote>
""")

@PY.UBOT("bbend")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_bb(u)
    bb = u["blockblast"]

    if not bb.get("active"):
        _save_db(db)
        return await message.reply("<blockquote>Game tidak sedang berjalan.</blockquote>")

    reward = int(bb["score"]) * REWARD_RATE
    u["uang"] = int(u["uang"]) + reward
    bb["active"] = False
    bb["best"] = max(int(bb.get("best", 0)), int(bb["score"]))
    _save_db(db)

    await message.reply(f"""
<blockquote><b>✅ GAME SELESAI</b>
{message.from_user.mention}

<b>Score:</b> <code>{bb['score']}</code>
<b>Reward:</b> <code>+{reward} uang</code>
<b>Saldo:</b> <code>{u['uang']}</code>

Main lagi: <code>.bbstart</code></blockquote>
""")

@PY.UBOT("bbtop")
async def _(client, message):
    db = _load_db()
    users = db.get("users", {})
    ranking = []

    for uid_str, data in users.items():
        bb = (data or {}).get("blockblast")
        if not bb:
            continue
        best = int(bb.get("best", 0))
        if best > 0:
            ranking.append((int(uid_str), best))

    ranking.sort(key=lambda x: x[1], reverse=True)
    ranking = ranking[:10]

    if not ranking:
        return await message.reply("<blockquote><b>🏆 TOP BLOCK BLAST</b>\nBelum ada yang main.</blockquote>")

    lines = []
    for i, (uid, best) in enumerate(ranking, start=1):
        try:
            us = await client.get_users(uid)
            name = us.first_name or "Unknown"
        except:
            name = "Unknown"
        lines.append(f"{i}. <b>{name}</b> — <code>{best}</code> score")

    await message.reply("<blockquote><b>🏆 TOP BLOCK BLAST</b>\n\n" + "\n".join(lines) + "</blockquote>")
