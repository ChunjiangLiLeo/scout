# simulate_100k.py

import pandas as pd
import numpy as np
import time
import psutil
import os
from sqlalchemy import create_engine
import getpass

# ========== 参数 ==========
target_size = 100_000
chunk_size = 20_000  # 分批写入
table_name = "transactions_parsed_100k"
csv_path = "transactions_parsed_100k.csv"

# ========== 辅助函数 ==========
def get_memory_usage():
    process = psutil.Process(os.getpid())
    return round(process.memory_info().rss / (1024 * 1024), 2)

# ========== 开始 ==========
start = time.time()
print(f"🚀 开始生成 100,000 样本 | 当前内存使用：{get_memory_usage()} MB")

# 连接数据库
username = getpass.getuser()
engine = create_engine(f"postgresql://{username}@localhost:5432/scout_db")

# 读取原始数据
df = pd.read_sql("SELECT * FROM transactions_parsed", engine)
original_len = len(df)

if original_len == 0:
    print("❌ 原始数据为空，无法生成！")
    exit()

# 复制生成目标行数
copies = (target_size // original_len) + 1
values_repeated = np.tile(df.values, (copies, 1))
df_sample = pd.DataFrame(values_repeated, columns=df.columns).head(target_size)
df_sample["id"] = range(1, len(df_sample) + 1)

# 分批写入 PostgreSQL
print(f"📦 分批写入 {table_name}（每批 {chunk_size} 行）")
for i in range(0, len(df_sample), chunk_size):
    df_chunk = df_sample.iloc[i:i + chunk_size]
    print(f"⏳ 写入第 {i // chunk_size + 1} 批：{len(df_chunk)} 行")
    df_chunk.to_sql(
        table_name,
        engine,
        if_exists="append" if i > 0 else "replace",
        index=False,
        method='multi',
        chunksize=5000
    )

# 可选导出为 CSV
df_sample.to_csv(csv_path, index=False)
print(f"✅ CSV 已导出至 {csv_path}")

# ========== 结束 ==========
end = time.time()
print(f"✅ 写入完成，共 {len(df_sample):,} 行")
print(f"⏱ 总用时：{round(end - start, 2)} 秒 | 内存使用：{get_memory_usage()} MB")
