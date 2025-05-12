import pandas as pd
from sqlalchemy import create_engine
import getpass
from rapidfuzz import fuzz, process
import time
import psutil
import os

def get_memory_usage():
    process = psutil.Process(os.getpid())
    return round(process.memory_info().rss / (1024 * 1024), 2)

print(f"Starting address matching | Initial memory usage: {get_memory_usage()} MB")
start_time = time.time()

# Step 1: Connect to PostgreSQL
username = getpass.getuser()
engine = create_engine(f"postgresql://{username}@localhost:5432/scout_db")

# Step 2: Load transaction and address data
tx_table = os.getenv("TX_TABLE", "transactions_parsed")
df_tx = pd.read_sql(f"SELECT * FROM {tx_table}", engine)
df_addr = pd.read_sql("SELECT * FROM addresses", engine)
df_addr["id"] = df_addr.index

# Field mapping for address table
df_addr["street_number"] = df_addr["house"]
df_addr["street_name"] = df_addr["street"]
df_addr["street_type"] = df_addr["strtype"]
df_addr["parsed_unit"] = (
    df_addr["apttype"].fillna("") + " " + df_addr["aptnbr"].fillna("")
).str.strip()

# Standardization functions
def normalize_type(val):
    val = str(val).strip().lower()
    return val.replace("avenue", "ave").replace("street", "st").replace("road", "rd")

def normalize_unit(val):
    return str(val).strip().lower().replace("unit", "apt").replace("#", "apt")

def normalize_str(val):
    return str(val).strip().lower()

# Normalize all fields
for col in ["street_number", "street_name", "street_type", "parsed_unit"]:
    if col == "parsed_unit":
        df_tx[col] = df_tx[col].apply(normalize_unit)
        df_addr[col] = df_addr[col].apply(normalize_unit)
    elif col == "street_type":
        df_tx[col] = df_tx[col].apply(normalize_type)
        df_addr[col] = df_addr[col].apply(normalize_type)
    else:
        df_tx[col] = df_tx[col].apply(normalize_str)
        df_addr[col] = df_addr[col].apply(normalize_str)

df_addr = df_addr[["id", "street_number", "street_name", "street_type", "parsed_unit"]]

# Step 3: Exact matching
print("Performing exact match...")
df_exact = pd.merge(
    df_tx,
    df_addr,
    how="inner",
    on=["street_number", "street_name", "street_type", "parsed_unit"],
    suffixes=("", "_addr")
)

df_exact_result = df_exact[["id", "id_addr"]].copy()
df_exact_result.rename(columns={"id_addr": "matched_address_id"}, inplace=True)
df_exact_result["match_type"] = "exact"
df_exact_result["confidence_score"] = 100
print(f"Exact matches: {len(df_exact_result)}")

# Step 4: Fuzzy matching with blocking
print("Performing fuzzy match...")
matched_ids = df_exact_result["id"].tolist()
df_unmatched = df_tx[~df_tx["id"].isin(matched_ids)].copy()

fuzzy_rows = []

def addr_str(row):
    return f"{row['street_number']} {row['street_name']} {row['street_type']} {row['parsed_unit']}".strip().lower()

grouped = df_unmatched.groupby("street_name")

for name, group in grouped:
    subset_tx = group.copy()
    subset_addr = df_addr[df_addr["street_name"] == name]
    if subset_addr.empty:
        continue

    addr_choices = subset_addr.apply(addr_str, axis=1).tolist()
    addr_ids = subset_addr["id"].tolist()

    for _, row in subset_tx.iterrows():
        query = addr_str(row)
        best, score, idx = process.extractOne(
            query, addr_choices,
            scorer=fuzz.token_sort_ratio,
            score_cutoff=80
        ) or (None, 0, None)

        if idx is not None:
            fuzzy_rows.append({
                "id": row["id"],
                "matched_address_id": addr_ids[idx],
                "match_type": "fuzzy",
                "confidence_score": score
            })

df_fuzzy = pd.DataFrame(fuzzy_rows)
print(f"Fuzzy matches: {len(df_fuzzy)}")

# Step 5: Combine and store results
df_result = pd.concat([df_exact_result, df_fuzzy], ignore_index=True)
df_result.to_sql("matched_transactions", engine, if_exists="replace", index=False)
engine.dispose()

# Step 6: Logging
print("Matching results saved to table 'matched_transactions'.")
print(f"Total runtime: {round(time.time() - start_time, 2)} seconds")
print(f"Final memory usage: {get_memory_usage()} MB")
