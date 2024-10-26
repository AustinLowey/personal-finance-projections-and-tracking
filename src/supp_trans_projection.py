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
    supp_trans_projection["date"] = pd.to_datetime(supp_trans_projection["date"])

    return supp_trans_projection


def combine_rec_and_supp(
    rec_trans_projection: pd.DataFrame,
    supp_trans_projection: pd.DataFrame
) -> pd.DataFrame:
    """Combines and sorts recurring and supplemental transaction projections."""

    combined_trans_projection = pd.concat(
        [rec_trans_projection, supp_trans_projection]
    )
    combined_trans_projection["date"] = pd.to_datetime(combined_trans_projection["date"])
    combined_trans_projection = combined_trans_projection.sort_values(
        by=["date", "transaction_amount"],
        ascending=[True, False],
        ignore_index=True
    )
    print("Merged future projected supplemental and recurring transactions.")

    return combined_trans_projection