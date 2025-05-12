import pandas as pd
from sqlalchemy import create_engine
import getpass

username = getpass.getuser()
engine = create_engine(f"postgresql://{username}@localhost:5432/scout_db")

df = pd.read_sql("SELECT * FROM matched_transactions_final", engine)
duplicate_ids = df["id"].value_counts()
duplicates = duplicate_ids[duplicate_ids > 1]

print(f"📎 出现重复匹配的交易 ID 数量：{len(duplicates)}")
print(duplicates.head())
