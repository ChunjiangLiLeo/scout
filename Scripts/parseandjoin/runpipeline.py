# run_pipeline.py

import os
import time
import sys
import subprocess

print("\U0001F680 Starting full address matching pipeline...")

start_time = time.time()

# Ensure virtual environment is used
venv_python = os.path.join(os.getcwd(), ".venv", "bin", "python")
if not os.path.exists(venv_python):
    print("Cannot find .venv Python interpreter at .venv/bin/python")
    sys.exit(1)

# Step 1: Run match.py
print("\n[1/2] Running match.py (exact + fuzzy + blocking)...")
subprocess.run([venv_python, "Scripts/join.py"], check=True)
print("match.py completed and written to matched_transactions")

# Step 2: Run fallback.py (which now directly computes unmatched from transactions_parsed - matched_transactions)
print("\n[2/2] Running fallback.py (soundex + trigram)...")
subprocess.run([venv_python, "Scripts/fallback.py"], check=True)

# Timing
end_time = time.time()
print(f"\n\u2705 Pipeline complete! Total time: {round(end_time - start_time, 2)} seconds")
