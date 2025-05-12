# Scripts/Analysis/export_unmatched.py

import pandas as pd
from sqlalchemy import create_engine
import getpass

print("📤 Exporting unmatched records...")

username = getpass.getuser()
engine = create_engine(f"postgresql://{username}@localhost:5432/scout_db")

df_tx = pd.read_sql("SELECT * FROM transactions_parsed", engine)
df_matched = pd.read_sql("SELECT DISTINCT id FROM matched_transactions_final", engine)

unmatched = df_tx[~df_tx["id"].isin(df_matched["id"])].copy()
unmatched.to_csv("unmatched_transactions.csv", index=False)

print(f"✅ Unmatched records exported: {len(unmatched)} rows to unmatched_transactions.csv")
