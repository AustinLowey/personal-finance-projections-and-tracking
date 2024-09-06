from datetime import datetime
import pandas as pd


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

    cash_flow = pd.concat([curr_bals_row, cash_flow], ignore_index=True)

    return cash_flow