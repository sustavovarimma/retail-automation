"""Генератор CSV-выгрузок из касс магазинов."""
import csv
import random
import string
from datetime import datetime
from pathlib import Path

from src.config_loader import load_config


def _make_doc_id() -> str:
    letters = "".join(random.choices(string.ascii_uppercase, k=3))
    digits = "".join(random.choices(string.digits, k=6))
    return f"{letters}{digits}"


def _make_rows(n_rows, products):
    rows = []
    while len(rows) < n_rows:
        doc_id = _make_doc_id()
        for _ in range(random.randint(1, 4)):
            p = random.choice(products)
            amount = random.randint(1, 5)
            discount = 0.0
            if random.random() < 0.3:
                discount = round(p["price"] * amount * random.uniform(0.05, 0.3), 2)
            rows.append({
                "doc_id": doc_id,
                "item": p["item"],
                "category": p["category"],
                "amount": amount,
                "price": p["price"],
                "discount": discount,
            })
    return rows


def generate_file(shop_num, cash_num, cfg):
    lo, hi = cfg["generator"]["rows_per_file"]
    rows = _make_rows(random.randint(lo, hi), cfg["products"])

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = cfg["paths"]["data_dir"] / f"{shop_num}_{cash_num}_{stamp}.csv"

    with open(fname, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["doc_id", "item", "category", "amount", "price", "discount"]
        )
        writer.writeheader()
        writer.writerows(rows)
    return fname


def main():
    cfg = load_config()
    total = 0
    for shop in cfg["generator"]["shops"]:
        for cash in cfg["generator"]["cash_per_shop"]:
            path = generate_file(shop, cash, cfg)
            print(f"Generated: {path.name}")
            total += 1
    print(f"Done. Files created: {total}")


if __name__ == "__main__":
    main()
