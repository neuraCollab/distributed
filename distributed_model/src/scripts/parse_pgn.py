import polars as pl
import chess.pgn
from datetime import datetime
from pathlib import Path

# Путь к PGN-файлу
pgn_path = Path(__file__).resolve().parents[1] / "./work/src/data/chess" / "lichess.pgn"

# Список для сбора партий
games = []
# вместо games = [] — стримим и сохраняем кусками
batch = []
BATCH_SIZE = 100_000
batch_id = 0

with open(pgn_path, encoding="utf-8") as f:
    while True:
        game = chess.pgn.read_game(f)
        if game is None:
            break

        try:
            headers = game.headers
            batch.append({
                "game_id": headers.get("GameId", ""),
                "white": headers.get("White", ""),
                "black": headers.get("Black", ""),
                "white_elo": int(headers.get("WhiteElo", 0)),
                "black_elo": int(headers.get("BlackElo", 0)),
                "result": headers.get("Result", ""),
                "timestamp": datetime.strptime(
                    headers.get("UTCDate", "2000.01.01") + " " + headers.get("UTCTime", "00:00:00"),
                    "%Y.%m.%d %H:%M:%S"
                ),
                "time_control": headers.get("TimeControl", ""),
                "eco": headers.get("ECO", ""),
                "opening": headers.get("Opening", ""),
                "moves_count": sum(1 for _ in game.mainline_moves())
            })

            if len(batch) >= BATCH_SIZE:
                pl.DataFrame(batch).write_parquet(f"{pgn_path.stem}_part{batch_id}.parquet")
                print(f"✅ Сохранён batch {batch_id}")
                batch = []
                batch_id += 1

        except Exception as e:
            print(f"⚠️ Ошибка: {e}")
            continue

# Последний кусок
if batch:
    pl.DataFrame(batch).write_parquet(f"{pgn_path.stem}_part{batch_id}.parquet")
    print(f"✅ Сохранён финальный batch {batch_id}")
