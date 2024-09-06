from datetime import datetime
import pandas as pd

# Remove data_loading import if/when changing project_supplenental_transactions()
from data_loading import load_latest_csv, convert_currency_cols_to_int


def project_supplemental_transactions() -> pd.DataFrame:
    # TODO: Update this function with GUI approach instead of csv import

    supp_trans_projection = load_latest_csv("supplemental_transactions")
    supp_trans_projection = convert_currency_cols_to_int(
        supp_trans_projection,
        ["transaction_amount"]
    )

    return supp_trans_projection


def combine_rec_and_supp(
    rec_trans_projection: pd.DataFrame,
    supp_trans_projection: pd.DataFrame
) -> pd.DataFrame:
    """Combines and sorts recurring and supplemental transaction projections."""

    combined_trans_projection = pd.concat([rec_trans_projection, supp_trans_projection])
    combined_trans_projection = combined_trans_projection.sort_values(
        by=["date", "transaction_amount"],
        ascending=[True, False],
        ignore_index=True
    )

    return combined_trans_projection