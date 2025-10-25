CREATE TABLE IF NOT EXISTS btc_onchain (
    date TEXT PRIMARY KEY,
    tx_volume REAL,
    n_unique_addresses REAL,
    hash_rate REAL,
    difficulty REAL
);
