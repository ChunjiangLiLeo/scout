# Scripts/deduplicate_matches.py

import pandas as pd
from sqlalchemy import create_engine
import getpass

print("🧹 正在去重匹配记录，保留每个交易 ID 的最佳匹配...")

# 连接 PostgreSQL
username = getpass.getuser()
engine = create_engine(f"postgresql://{username}@localhost:5432/scout_db")

# 读取最终匹配结果
df = pd.read_sql("SELECT * FROM matched_transactions_final", engine)

# 处理重复项：按 id 保留得分最高的那一条
df_top1 = df.sort_values("confidence_score", ascending=False).drop_duplicates("id", keep="first")

# 写入新表
df_top1.to_sql("matched_transactions_top1", engine, if_exists="replace", index=False)

print(f"✅ 去重完成，共保留唯一交易记录数：{len(df_top1)}")
print("📥 新表已写入：matched_transactions_top1")
