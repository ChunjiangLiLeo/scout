# simulate_scale_optimized.py
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import getpass
import time

start = time.time()
username = getpass.getuser()
engine = create_engine(f"postgresql://{username}@localhost:5432/scout_db")

# Step 1: 读取原始数据
df = pd.read_sql("SELECT * FROM transactions_parsed", engine)
original_len = len(df)

if original_len == 0:
    print("❌ 原始数据为空，无法生成样本！")
    exit()

# Step 2: 复制数据 (超快)
target_size = 2_000_000
copies = (target_size // original_len) + 1

print(f"🧮 原始行数：{original_len}，将复制 {copies} 次生成约 200 万条样本数据...")

# 用 numpy.tile 快速复制值（比 concat 快至少10倍）
values_repeated = np.tile(df.values, (copies, 1))
df_sample = pd.DataFrame(values_repeated, columns=df.columns).head(target_size)

# 重设 ID
df_sample["id"] = range(1, len(df_sample) + 1)

chunk_size = 500_000
for i in range(0, len(df_sample), chunk_size):
    df_chunk = df_sample.iloc[i:i+chunk_size]
    print(f"⏳ 写入第 {i//chunk_size + 1} 批：{len(df_chunk)} 行")
    df_chunk.to_sql(
        "transactions_parsed_sample",
        engine,
        if_exists="append" if i > 0 else "replace",
        index=False,
        method='multi',
        chunksize=5000
    )


print(f"✅ 写入完成，共 {len(df_sample):,} 行，用时 {round(time.time() - start, 2)} 秒")


