import pandas as pd
import usaddress
from sqlalchemy import create_engine
import getpass
import warnings

# 获取当前用户（用于连接 PostgreSQL）
username = getpass.getuser()

# 创建数据库连接
engine = create_engine(f"postgresql://{username}@localhost:5432/scout_db")

# Step 1: 读取原始 transactions 表
df = pd.read_sql("SELECT * FROM transactions", con=engine)

# Step 2: 构造完整地址字段 full_address
df["full_address"] = df["address_line_1"].fillna("") + " " + df["address_line_2"].fillna("")

print("📥 原始完整地址预览：")
print(df[["address_line_1", "address_line_2", "full_address"]].head())

# Step 3: 初始化解析列
parsed_data = {
    "street_number": [],
    "street_name": [],
    "street_type": [],
    "unit": [],
    "unit_type": []
}

warnings.filterwarnings("ignore")

# Step 4: 使用 usaddress 拆解 full_address
for addr in df["full_address"]:
    try:
        parsed, _ = usaddress.tag(addr)
        parsed_data["street_number"].append(parsed.get("AddressNumber", ""))
        parsed_data["street_name"].append(parsed.get("StreetName", ""))
        parsed_data["street_type"].append(parsed.get("StreetNamePostType", ""))
        parsed_data["unit"].append(parsed.get("OccupancyIdentifier", ""))
        parsed_data["unit_type"].append(parsed.get("OccupancyType", ""))
    except:
        parsed_data["street_number"].append("")
        parsed_data["street_name"].append("")
        parsed_data["street_type"].append("")
        parsed_data["unit"].append("")
        parsed_data["unit_type"].append("")

# Step 5: 合并解析字段
df = df.assign(**parsed_data)

# Step 6: 创建最终单字段 unit（如 Apt 4B、#6A）
df["parsed_unit"] = df["unit_type"].fillna("") + " " + df["unit"].fillna("")
df["parsed_unit"] = df["parsed_unit"].str.strip()

# Step 7: 结果预览
print("\n✅ 拆解后的字段预览：")
print(df[["full_address", "street_number", "street_name", "street_type", "parsed_unit"]].head())

# Step 8: 保存至新表 transactions_parsed
df.to_sql("transactions_parsed", engine, if_exists="replace", index=False)

print("\n✅ 结果已保存至 PostgreSQL 表 transactions_parsed")
