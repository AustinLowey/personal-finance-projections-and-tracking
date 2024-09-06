from pathlib import Path
from typing import List, Optional
import pandas as pd


def load_latest_csv(folder_name: str) -> Optional[pd.DataFrame]:
    """Returns the latest .csv file in the specified ~/.finance sub-folder as a df."""

    # Get .csv files in specified folder and sort by name
    path = Path("~/.finances").expanduser() / folder_name
    files = list(path.glob("*.csv"))
    files.sort()

    # Return latest file as a DataFrame
    if files:
        latest_file = files[-1]
        try:
            df = pd.read_csv(latest_file)
            return df
        except Exception as e:
            print(f"Error loading file {latest_file}: {e}")
            return None
    else:
        print(f"Warning: No files in {path}")
        return None
    

def convert_currency_cols_to_int(df: pd.DataFrame, column_names: List[str]) -> pd.DataFrame:
    """Cleans and converts specified columns from accounting/currency strings to numeric."""
    
    for col in column_names:
        if col in df.columns:

            # Remove $, spaces and commas and convert to numeric
            try:
                df[col] = df[col].replace(r'[()\$, ]', '', regex=True)
                df[col] = pd.to_numeric(df[col], errors="coerce")
            except Exception as e:
                print(f"Error converting column '{col}': {e}")
                
        else:
            print(f"Warning: Column '{col}' not found in DataFrame.")
    
    return df


if __name__ == "__main__":
    curr_bals = load_latest_csv("current_balances")
    rec_trans = load_latest_csv("recurring_transactions")

    if curr_bals is not None:
        print("Latest current balances DataFrame:")
        curr_bals = convert_currency_cols_to_int(
            curr_bals,
            ["statement_balance", "current_balance"]
        )
        print(curr_bals.tail())

    if rec_trans is not None:
        print("Latest recurring transactions DataFrame:")
        rec_trans = convert_currency_cols_to_int(rec_trans, ["amount"])
        print(rec_trans[["transaction", "amount", "on_date", "end_date"]].head())