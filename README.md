# 🏠 Address Matching Pipeline (Scout Project)

A scalable, modular Python pipeline for high-volume address matching using PostgreSQL, fuzzy logic, blocking strategies, and fallback mechanisms.

This project was built as part of the **Scout Matching System**, designed to match parsed transaction addresses against a canonical address database with high accuracy and performance—even at scale (100K–200M rows).

---

## 📦 Features

## 🔍 Matching Logic Overview

The address matching system is designed for accuracy, modularity, and scalability. The pipeline includes:

---

### Exact Match

- Performs a full-field join on:  
  `street_number + street_name + street_type + parsed_unit`
- If **all corresponding columns** in the transaction and address tables **match exactly**, the records are linked automatically.
- This ensures high-confidence matches without additional computation.

---

### Fuzzy Matching

- Uses `RapidFuzz` with `token_sort_ratio` scorer for approximate string comparison.
- Implements a **blocking strategy** by grouping on `street_name`, significantly reducing pairwise comparisons.
- A **similarity threshold of 80%** is applied — if a transaction record and a candidate address row exceed this score, they are joined.
- This allows for matching "Main Street" with "Main St", or typos like "Baker Ave." with "Bakker Avenue".

---

### Fallback Logic

If records remain unmatched after exact + fuzzy matching, a fallback matching stage is triggered:

- **Soundex Matching**:  
  Uses phonetic representation of street names (e.g., "Smith" ≈ "Smyth") to identify potential matches.
- **Trigram Similarity**:  
  Computes token-level trigram overlaps on normalized full address strings. Matches exceeding 0.80 similarity are retained.

---

### Scalability-Ready

- Pipeline was successfully tested with up to **100,000 rows** on a constrained local environment.
- The architecture is designed to scale to **200 million rows or more** using:
  - Pandas vectorized operations
  - Batched I/O with PostgreSQL
  - Blocking to avoid `O(n²)` fuzzy match explosion

---

## 🧱 Project Structure

```text
scout/
├── schema/
│   └── init_schema.sql
│       → Manual schema definition (CREATE TABLE / FOREIGN KEY) for PostgreSQL setup

├── msimulation.py
│   → Generate a synthetic 100,000-row transaction dataset based on seed data

├── run_pipeline.py
│   → Optional script to execute the full matching + fallback process using environment-based table switching

├── Scripts/
│
│   ├── ingestion/
│   │   ├── ingest.py
│   │   │   → Load original CSV or source files into PostgreSQL
│   │   ├── ingest.ipynb
│   │   │   → Interactive ingestion via Jupyter (manual exploration)
│   │   └── address.ipynb
│   │       → Visual validation and sanity checks for canonical address list
│
│   ├── parseandjoin/
│   │   ├── parse.py
│   │   │   → Parse raw full_address strings into structured components using `usaddress`
│   │   ├── join.py
│   │   │   → Exact + Fuzzy (blocking) matcher using RapidFuzz and token_sort_ratio
│   │   ├── fallback.py
│   │   │   → Fallback matcher using Soundex phonetic matching and Trigram similarity
│   │   └── runpipeline.py
│   │       → (Legacy/alternate) orchestration for parse → match → fallback
│
│   ├── analysis/
│   │   └── visualization.ipynb
│   │       → Match statistics, memory/runtime visualization, success breakdowns
│
│   ├── filter/
│   │   ├── distinct.py
│   │   │   → Remove duplicate records from input transaction data
│   │   ├── duplicate.py
│   │   │   → Check for address collisions and repeated rows
│   │   └── unmatched.py
│   │       → Export and analyze unmatched transactions post-matching
│
├── Reports/
│   └── scalability_report_100k.md
│       → Analysis of performance results for 100K sample test: runtime, memory, accuracy

├── requirements.txt
│   → Python dependency list (pandas, sqlalchemy, rapidfuzz, usaddress, etc.)

└── README.md
    → Project setup, structure, usage, performance, design decisions

