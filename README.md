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
├── msimulation.py               # Generate 100K-row sample dataset
├── run_pipeline.py                # (Optional) Orchestrate matching + fallback
├── Scripts/
│   ├── ingestion
│       ├── ingest.py
│       ├── ingest.ipynb
│       ├── address.ipynb
│   ├── parseandjoin                           # Exact + Fuzzy (blocking) matcher
│       ├── fallback.py
        ├── join.py               # Soundex + Trigram fallback
│       ├── parse.py
        ├── runpipeline.py                   # Parse full addresses (usaddress)
├── reports/
│   └── scalability_report_100k.md # Performance analysis and testing summary
├── requirements.txt
└── README.md
