"""
Run the final parameter sweep for the project with N=10000.

Generates: data/final_results.csv
"""

import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.simulation import parameter_sweep

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)

    print("Starting final sweep with N=10000...")
    print("This may take 20 to 40 minutes. Please do not close the terminal.")

    # Run the imported function with the final parameters
    df = parameter_sweep(
        N=10000,
        csv_path="data/final_results.csv"
    )

    print("\nFinal sweep completed.")
    print(f"Generated {len(df)} (p, n) combinations.")
    print("File saved to: data/final_results.csv")
