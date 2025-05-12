import pandas as pd
from sqlalchemy import create_engine
import getpass
from fuzzy import Soundex
from difflib import SequenceMatcher
import os
import time

print("Starting fallback matching...")

# Step 1: Connect to PostgreSQL and load unmatched transactions
username = getpass.getuser()
engine = create_engine(f"postgresql://{username}@localhost:5432/scout_db")

# Use environment variable to specify input table
tx_table = os.getenv("TX_TABLE", "transactions_parsed")
df_tx = pd.read_sql(f"SELECT * FROM {tx_table}", engine)

# Load already matched IDs from previous stage
try:
    df_matched = pd.read_sql("SELECT DISTINCT id FROM matched_transactions", engine)
    matched_ids = df_matched["id"].tolist()
except Exception:
    matched_ids = []

# Filter transactions that were not matched
unmatched = df_tx[~df_tx["id"].isin(matched_ids)].copy()
print(f"Unmatched transactions remaining: {len(unmatched)}")

# Step 2: Load address table and normalize
df_addr = pd.read_sql("SELECT * FROM addresses", engine)
df_addr["id"] = df_addr.index

# Map and combine apartment fields
df_addr["street_number"] = df_addr["house"]
df_addr["street_name"] = df_addr["street"]
df_addr["street_type"] = df_addr["strtype"]
df_addr["parsed_unit"] = (
    df_addr["apttype"].fillna("") + " " + df_addr["aptnbr"].fillna("")
).str.strip()

# Normalize helper
def normalize(val):
    return str(val).strip().lower()

# Apply normalization to both tables
df_addr["street_name"] = df_addr["street_name"].apply(normalize)
df_addr["parsed_unit"] = df_addr["parsed_unit"].apply(normalize)
unmatched["street_name"] = unmatched["street_name"].apply(normalize)
unmatched["parsed_unit"] = unmatched["parsed_unit"].apply(normalize)

# Step 3: Soundex phonetic matching
print("Running Soundex matching...")
soundex = Soundex(4)
soundex_rows = []

for _, row in unmatched.iterrows():
    tx_soundex = soundex(row["street_name"])
    for _, addr in df_addr.iterrows():
        if soundex(addr["street_name"]) == tx_soundex:
            soundex_rows.append({
                "id": row["id"],
                "matched_address_id": addr["id"],
                "match_type": "soundex",
                "confidence_score": 75
            })
            break  # Only take first phonetic match

print(f"Soundex matches: {len(soundex_rows)}")

# Step 4: Trigram similarity matching
print("Running Trigram similarity matching...")

def sim(a, b):
    return SequenceMatcher(None, a, b).ratio()

def addr_str(row):
    return f"{row['street_number']} {row['street_name']} {row['street_type']} {row['parsed_unit']}".strip().lower()

unmatched_ids_soundex = [row["id"] for row in soundex_rows]
unmatched_remaining = unmatched[~unmatched["id"].isin(unmatched_ids_soundex)]
addr_choices = df_addr.apply(addr_str, axis=1).tolist()
addr_ids = df_addr["id"].tolist()

ngram_rows = []
for _, row in unmatched_remaining.iterrows():
    tx_str = addr_str(row)
    sims = [sim(tx_str, choice) for choice in addr_choices]
    max_score = max(sims)
    if max_score > 0.8:
        idx = sims.index(max_score)
        ngram_rows.append({
            "id": row["id"],
            "matched_address_id": addr_ids[idx],
            "match_type": "ngram",
            "confidence_score": round(max_score * 100)
        })

print(f"Trigram matches: {len(ngram_rows)}")

# Step 5: Combine fallback results
fallback_df = pd.DataFrame(soundex_rows + ngram_rows)

# Combine with existing matched_transactions
try:
    df_existing = pd.read_sql("SELECT * FROM matched_transactions", engine)
except Exception:
    df_existing = pd.DataFrame()

if not df_existing.empty:
    df_final = pd.concat([df_existing, fallback_df], ignore_index=True)
else:
    df_final = fallback_df.copy()

# Step 6: Save final result
df_final.to_sql("matched_transactions_final", engine, if_exists="replace", index=False)

print("Final results saved to 'matched_transactions_final' table.")
print("Match type breakdown:")
print(df_final["match_type"].value_counts())
