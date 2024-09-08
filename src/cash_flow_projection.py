from datetime import datetime
import pandas as pd
import warnings


def add_balance_columns(combined_trans_projection: pd.DataFrame) -> pd.DataFrame:
    """Adds columns for bank and cc balances and changes column order."""

    combined_trans_projection["bank_bal"] = pd.NA
    combined_trans_projection["ccstmt_bal"] = pd.NA
    combined_trans_projection["cctotal_bal"] = pd.NA
    combined_trans_projection["net_bank_ccstmt"] = pd.NA
    combined_trans_projection["net_bank_cctotal"] = pd.NA
    cash_flow = combined_trans_projection[[
        "date",
        "bank_bal",
        "ccstmt_bal",
        "cctotal_bal",
        "net_bank_ccstmt",
        "net_bank_cctotal",
        "transaction_amount",
        "transaction",
        "category",
        "charge_to"
    ]]

    return cash_flow


def add_current_balances(cash_flow: pd.DataFrame, curr_bals: pd.DataFrame) -> pd.DataFrame:
    """Sums current balances and adds a row to the cash flow df with those balances."""

    curr_bals_row = pd.DataFrame({
        "date": [datetime.today().strftime("%Y-%m-%d")],
        "bank_bal": curr_bals.loc[curr_bals.type == "bank", "current_balance"].sum(),
        "ccstmt_bal": curr_bals.loc[curr_bals.type == "cc", "statement_balance"].sum(),
        "cctotal_bal": curr_bals.loc[curr_bals.type == "cc", "current_balance"].sum(),
        "net_bank_ccstmt": [pd.NA],
        "net_bank_cctotal": [pd.NA],
        "transaction_amount": [pd.NA],
        "transaction": ["current_balances"],
        "category": [pd.NA],
        "charge_to": [pd.NA]
    })

    with warnings.catch_warnings():
        # Note: pandas 2.1.0 has a FutureWarning for concatenating DataFrames with Null entries
        # https://github.com/pandas-dev/pandas/issues/55928
        warnings.filterwarnings("ignore", category=FutureWarning)
        cash_flow = pd.concat([curr_bals_row, cash_flow], ignore_index=True)
    cash_flow["date"] = pd.to_datetime(cash_flow["date"])

    return cash_flow


def add_cc_statement_rows(
    cash_flow: pd.DataFrame,
    target_date: int,
    action_type: str
) -> pd.DataFrame:
    """
    Adds new rows with specified statement transaction type after the 
    last occurrence of the target date in each applicable month.
    """

    # Get all (future) rows matching day of month == target date and keep latest for each date
    target_date_rows = cash_flow[cash_flow["date"].dt.day == target_date]
    target_date_rows = target_date_rows.loc[
        target_date_rows["date"].dt.date >= datetime.today().date()
    ].drop_duplicates(subset="date", keep="last")

    # Prepare rows for insertion
    new_rows = target_date_rows.assign(
        transaction_amount=0,
        transaction=action_type,
        category=action_type,
        charge_to=action_type
    )

    # Insert the new rows
    # Note: Would be inefficient for larger dataframes b/c of multiple concats. Appending slices
    # to a list then doing a single concat on many slices would be optimal performance-wise.
    insertion_indices = new_rows.index + 1
    for new_row_idx, target_idx in enumerate(insertion_indices):
        cash_flow = pd.concat(
            [
                cash_flow[:target_idx + new_row_idx],
                new_rows[new_row_idx:new_row_idx + 1],
                cash_flow[target_idx + new_row_idx:]
            ],
            ignore_index=True
        )

    return cash_flow


def calculate_future_balances(cash_flow: pd.DataFrame) -> pd.DataFrame:
    """Calculate all bank and cc balances row by row."""

    for i in range(len(cash_flow)):
        if i == 0:
            continue # Skip first row, which contains current balances

        curr_row = cash_flow.iloc[i]
        prev_row = cash_flow.iloc[i - 1]

        if curr_row.charge_to == "bank": # Pay directly from or to bank
            cash_flow.loc[i, "bank_bal"] = prev_row.bank_bal + curr_row.transaction_amount
            cash_flow.loc[i, "ccstmt_bal"] = prev_row.ccstmt_bal
            cash_flow.loc[i, "cctotal_bal"] = prev_row.cctotal_bal
        elif curr_row.charge_to == "cc": # Charge added to cc (i.e., subtract negative charge)
            cash_flow.loc[i, "bank_bal"] = prev_row.bank_bal
            cash_flow.loc[i, "ccstmt_bal"] = prev_row.ccstmt_bal
            cash_flow.loc[i, "cctotal_bal"] = prev_row.cctotal_bal - curr_row.transaction_amount
        elif curr_row.charge_to == "statement_due": # Pay statement balance
            cash_flow.loc[i, "bank_bal"] = prev_row.bank_bal - prev_row.ccstmt_bal
            cash_flow.loc[i, "ccstmt_bal"] = 0
            cash_flow.loc[i, "cctotal_bal"] = prev_row.cctotal_bal - prev_row.ccstmt_bal
        elif curr_row.charge_to == "statement_close": # New statement balance posted
            cash_flow.loc[i, "bank_bal"] = prev_row.bank_bal
            cash_flow.loc[i, "ccstmt_bal"] = prev_row.cctotal_bal
            cash_flow.loc[i, "cctotal_bal"] = prev_row.cctotal_bal
        else:
            print(
                f"Warning: Row with index={i} has improper charge_to type: '{curr_row.charge_to}'"
            )

        cash_flow.net_bank_ccstmt = cash_flow.bank_bal - cash_flow.ccstmt_bal
        cash_flow.net_bank_cctotal = cash_flow.bank_bal - cash_flow.cctotal_bal

    return cash_flow