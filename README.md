# 🏠 Address Matching Pipeline (Scout Project)

A scalable, modular Python pipeline for high-volume address matching using PostgreSQL, fuzzy logic, blocking strategies, and fallback mechanisms.

This project was built as part of the **Scout Matching System**, designed to match parsed transaction addresses against a canonical address database with high accuracy and performance—even at scale (100K–200M rows).

---

## 📦 Features

- ✅ **Exact Match**: Full field matching (number + street + type + unit)
- ✅ **Fuzzy Matching**: RapidFuzz + token_sort_ratio + blocking strategy
- ✅ **Fallback Logic**:
  - 🔊 Soundex phonetic matching
  - 📊 Trigram similarity scoring
- ✅ **Scalability-Ready**: Tested on up to 100000 rows due to device and cloud using restriction, designed for 200M+
- ✅ **Modular Scripts**: `simulate`, `join`, `fallback`, `pipeline`, `report`

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
├── reports/
│   └── scalability_report_100k.md
│       → Analysis of performance results for 100K sample test: runtime, memory, accuracy

├── requirements.txt
│   → Python dependency list (pandas, sqlalchemy, rapidfuzz, usaddress, etc.)

└── README.md
    → Project setup, structure, usage, performance, design decisions

