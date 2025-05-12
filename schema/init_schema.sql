-- Canonical Address Table
CREATE TABLE addresses (
    id SERIAL PRIMARY KEY,
    house TEXT,
    street TEXT,
    strtype TEXT,
    apttype TEXT,
    aptnbr TEXT
);

-- Parsed Transaction Table
CREATE TABLE transactions_parsed_100k (
    id INTEGER PRIMARY KEY,
    street_number TEXT,
    street_name TEXT,
    street_type TEXT,
    unit TEXT,
    unit_type TEXT,
    parsed_unit TEXT
);

-- Matched Transactions
CREATE TABLE matched_transactions (
    id INTEGER PRIMARY KEY,
    matched_address_id INTEGER,
    match_type TEXT,
    confidence_score INTEGER,
    FOREIGN KEY (id) REFERENCES transactions_parsed_100k(id),
    FOREIGN KEY (matched_address_id) REFERENCES addresses(id)
);

-- Final Fallback Results
CREATE TABLE matched_transactions_final (
    id INTEGER PRIMARY KEY,
    matched_address_id INTEGER,
    match_type TEXT,
    confidence_score INTEGER,
    FOREIGN KEY (id) REFERENCES transactions_parsed_100k(id),
    FOREIGN KEY (matched_address_id) REFERENCES addresses(id)
);

-- Indexes for blocking / performance
CREATE INDEX idx_street_name_tx ON transactions_parsed_100k (street_name);
CREATE INDEX idx_street_name_addr ON addresses (street);
