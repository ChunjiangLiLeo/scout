# fallback.py

import pandas as pd
from sqlalchemy import create_engine
import getpass
from fuzzy import Soundex
from difflib import SequenceMatcher
import time

print("\U0001F680 fallback.py 正在运行...")

# Step 1: 建立数据库连接 & 读取数据
username = getpass.getuser()
engine = create_engine(f"postgresql://{username}@localhost:5432/scout_db")

# 所有 transactions 数据
df_tx = pd.read_sql("SELECT * FROM transactions_parsed", engine)

# 已匹配过的记录 ID（不依赖 match_type 字段）
try:
    df_matched = pd.read_sql("SELECT DISTINCT id FROM matched_transactions", engine)
    matched_ids = df_matched["id"].tolist()
except:
    matched_ids = []

# 筛选未匹配的记录（完全基于 ID）
unmatched = df_tx[~df_tx["id"].isin(matched_ids)].copy()
print(f"🔍 未匹配记录数：{len(unmatched)}")

# 地址表
df_addr = pd.read_sql("SELECT * FROM addresses", engine)
df_addr["id"] = df_addr.index

# 字段映射
df_addr["street_number"] = df_addr["house"]
df_addr["street_name"] = df_addr["street"]
df_addr["street_type"] = df_addr["strtype"]
df_addr["parsed_unit"] = (
    df_addr["apttype"].fillna("") + " " + df_addr["aptnbr"].fillna("")
).str.strip()

# 标准化函数
def normalize(val):
    return str(val).strip().lower()

df_addr["street_name"] = df_addr["street_name"].apply(normalize)
df_addr["parsed_unit"] = df_addr["parsed_unit"].apply(normalize)
unmatched["street_name"] = unmatched["street_name"].apply(normalize)
unmatched["parsed_unit"] = unmatched["parsed_unit"].apply(normalize)

# Step 2: Soundex 匹配
print("🔊 Soundex 匹配中...")
soundex = Soundex(4)
soundex_rows = []

for i, row in unmatched.iterrows():
    tx_soundex = soundex(row["street_name"])
    for _, addr in df_addr.iterrows():
        if soundex(addr["street_name"]) == tx_soundex:
            soundex_rows.append({
                "id": row["id"],
                "matched_address_id": addr["id"],
                "match_type": "soundex",
                "confidence_score": 75
            })
            break
print(f"✅ Soundex 匹配成功：{len(soundex_rows)} 条")

# Step 3: Trigram 匹配
print("📊 Trigram 匹配中...")
def sim(a, b):
    return SequenceMatcher(None, a, b).ratio()

def addr_str(row):
    return f"{row['street_number']} {row['street_name']} {row['street_type']} {row['parsed_unit']}".strip().lower()

unmatched_ids_soundex = [row["id"] for row in soundex_rows]
unmatched_remaining = unmatched[~unmatched["id"].isin(unmatched_ids_soundex)]
addr_choices = df_addr.apply(addr_str, axis=1).tolist()
addr_ids = df_addr["id"].tolist()

ngram_rows = []
for i, row in unmatched_remaining.iterrows():
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
print(f"✅ Trigram 匹配成功：{len(ngram_rows)} 条")

# 合并所有匹配结果
fallback_df = pd.DataFrame(soundex_rows + ngram_rows)

# 合并 matched_transactions 表
try:
    df_existing = pd.read_sql("SELECT * FROM matched_transactions", engine)
except:
    df_existing = pd.DataFrame()

if not df_existing.empty:
    df_final = pd.concat([df_existing, fallback_df], ignore_index=True)
else:
    df_final = fallback_df.copy()

# 保存到 final 表
df_final.to_sql("matched_transactions_final", engine, if_exists="replace", index=False)

print("✅ 匹配结果已保存到 matched_transactions_final 表")
print("\n📊 匹配结果统计：")
print(df_final["match_type"].value_counts())
