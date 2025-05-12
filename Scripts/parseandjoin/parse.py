import pandas as pd
import usaddress
from sqlalchemy import create_engine
import getpass
import warnings

username = getpass.getuser()
engine = create_engine(f"postgresql://{username}@localhost:5432/scout_db")

# Step 1: Read original transaction data
df = pd.read_sql("SELECT * FROM transactions", con=engine)

# Step 2: Construct full address field
df["full_address"] = df["address_line_1"].fillna("") + " " + df["address_line_2"].fillna("")

print("Preview of raw full addresses:")
print(df[["address_line_1", "address_line_2", "full_address"]].head())

# Step 3: Initialize parsed column containers
parsed_data = {
    "street_number": [],
    "street_name": [],
    "street_type": [],
    "unit": [],
    "unit_type": []
}

warnings.filterwarnings("ignore")

# Step 4: Use usaddress to parse full addresses
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

# Step 5: Assign parsed fields to DataFrame
df = df.assign(**parsed_data)

# Step 6: Generate standardized unit field (e.g., 'Apt 4B')
df["parsed_unit"] = df["unit_type"].fillna("") + " " + df["unit"].fillna("")
df["parsed_unit"] = df["parsed_unit"].str.strip()

print("\nPreview of parsed address components:")
print(df[["full_address", "street_number", "street_name", "street_type", "parsed_unit"]].head())

# Step 7: Save parsed results to new table
df.to_sql("transactions_parsed", engine, if_exists="replace", index=False)

print("Parsed results saved to table 'transactions_parsed'.")
