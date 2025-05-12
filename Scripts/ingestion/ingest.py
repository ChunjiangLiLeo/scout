import pandas as pd
from sqlalchemy import create_engine
import getpass

# Prompt for your username (or hardcode it below)
username = getpass.getuser()  # Automatically gets your system username

# Load CSVs
addresses = pd.read_excel("Data/address.xlsx")
transactions = pd.read_excel("Data/transactions.xlsx")

# Connect to PostgreSQL
engine = create_engine(f"postgresql://{username}@localhost:5432/scout_db")

# Load data into database
addresses.to_sql("addresses", engine, index=False, if_exists="replace")
transactions.to_sql("transactions", engine, index=False, if_exists="replace")

print("✅ Data successfully loaded into PostgreSQL (scout_db)!")
