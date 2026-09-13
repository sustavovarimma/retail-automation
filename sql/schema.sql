-- Основная таблица с "шапкой" чека
CREATE TABLE IF NOT EXISTS receipts (
    doc_id      VARCHAR(50) PRIMARY KEY,
    shop_num    INTEGER NOT NULL,
    cash_num    INTEGER NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Позиции чека
CREATE TABLE IF NOT EXISTS receipt_items (
    id          BIGSERIAL PRIMARY KEY,
    doc_id      VARCHAR(50) NOT NULL REFERENCES receipts(doc_id) ON DELETE CASCADE,
    item        VARCHAR(255) NOT NULL,
    category    VARCHAR(100) NOT NULL,
    amount      INTEGER NOT NULL CHECK (amount > 0),
    price       NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    discount    NUMERIC(10, 2) NOT NULL DEFAULT 0 CHECK (discount >= 0)
);

CREATE INDEX IF NOT EXISTS idx_receipts_shop  ON receipts(shop_num);
CREATE INDEX IF NOT EXISTS idx_items_doc      ON receipt_items(doc_id);
CREATE INDEX IF NOT EXISTS idx_items_category ON receipt_items(category);

-- Служебная таблица для отслеживания обработанных файлов
CREATE TABLE IF NOT EXISTS processed_files (
    file_name    VARCHAR(255) PRIMARY KEY,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
