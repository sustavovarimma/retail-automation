"""Загрузчик CSV-выгрузок из data/ в PostgreSQL."""
import csv
import logging
import re
from pathlib import Path

from src.config_loader import load_config
from src.db import get_connection


logging.basicConfig(
    filename="logs/loader.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8",
)
log = logging.getLogger(__name__)

# Имя файла: {shop_num}_{cash_num}_{YYYYMMDD_HHMMSS}.csv
FILE_RE = re.compile(r"^(\d+)_(\d+)_\d{8}_\d{6}\.csv$")


def is_valid_file(path: Path) -> bool:
    """Проверяем, что файл - это валидная выгрузка, а не лишний файл."""
    return path.is_file() and FILE_RE.match(path.name) is not None


def parse_filename(name: str):
    m = FILE_RE.match(name)
    return int(m.group(1)), int(m.group(2))


def load_file(path: Path, cfg: dict) -> None:
    """Загружает один CSV-файл в БД в рамках одной транзакции."""
    shop_num, cash_num = parse_filename(path.name)

    with get_connection(cfg) as conn, conn.cursor() as cur:
        cur.execute("SELECT 1 FROM processed_files WHERE file_name = %s", (path.name,))
        if cur.fetchone():
            log.info("Skip (already processed): %s", path.name)
            print(f"  SKIP: {path.name} (already processed)")
            return

        receipts_seen = set()
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                doc_id = row["doc_id"]
                if doc_id not in receipts_seen:
                    cur.execute(
                        """INSERT INTO receipts (doc_id, shop_num, cash_num)
                           VALUES (%s, %s, %s)
                           ON CONFLICT (doc_id) DO NOTHING""",
                        (doc_id, shop_num, cash_num),
                    )
                    receipts_seen.add(doc_id)

                cur.execute(
                    """INSERT INTO receipt_items
                       (doc_id, item, category, amount, price, discount)
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    (
                        doc_id,
                        row["item"],
                        row["category"],
                        int(row["amount"]),
                        float(row["price"]),
                        float(row["discount"]),
                    ),
                )

        cur.execute("INSERT INTO processed_files (file_name) VALUES (%s)", (path.name,))
    log.info("Loaded: %s (%d receipts)", path.name, len(receipts_seen))
    print(f"  OK: {path.name} ({len(receipts_seen)} receipts)")


def main():
    cfg = load_config()
    data_dir = cfg["paths"]["data_dir"]
    files = sorted(p for p in data_dir.iterdir() if is_valid_file(p))
    log.info("Found %d files to process", len(files))
    print(f"Found {len(files)} files to process")

    ok, fail = 0, 0
    for f in files:
        try:
            load_file(f, cfg)
            ok += 1
        except Exception as e:
            log.exception("Failed to load %s", f.name)
            print(f"  FAIL: {f.name} -> {e}")
            fail += 1

    print(f"Done. OK: {ok}, FAIL: {fail}")


if __name__ == "__main__":
    main()
