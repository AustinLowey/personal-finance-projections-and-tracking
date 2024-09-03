from pathlib import Path
from typing import Optional

import pandas as pd


def load_latest_csv(folder_name: str) -> Optional[pd.DataFrame]:
    """Returns the latest file in the specified ~/.finance sub-folder."""
    path = Path("~/.finances").expanduser() / folder_name
    files = list(path.glob("*.csv"))
    files.sort()

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


if __name__ == "__main__":
    curr_bals = load_latest_csv("current_balances")
    rec_trans = load_latest_csv("recurring_transactions")

    if curr_bals is not None:
        print("Latest current balances DataFrame:")
        print(curr_bals.head())

    if rec_trans is not None:
        print("Latest recurring transactions DataFrame:")
        print(rec_trans.head())