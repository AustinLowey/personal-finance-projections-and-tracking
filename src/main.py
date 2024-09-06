import pandas as pd

from cash_flow_projection import add_balance_columns, add_current_balances
from data_loading import load_latest_csv, convert_currency_cols_to_int
from rec_trans_projection import project_recurring_transactions
from supp_trans_projection import project_supplemental_transactions, combine_rec_and_supp


# Load latest data and convert columns if needed
curr_bals = load_latest_csv("current_balances")
rec_trans = load_latest_csv("recurring_transactions")
curr_bals = convert_currency_cols_to_int(
    curr_bals,
    ["statement_balance", "current_balance"]
)
rec_trans = convert_currency_cols_to_int(rec_trans, ["amount"])

# Project expected transactions across a future time period
rec_trans_projection = project_recurring_transactions(rec_trans, num_months=3)
supp_trans_projection = project_supplemental_transactions()
combined_trans_projection = combine_rec_and_supp(rec_trans_projection, supp_trans_projection)

#
cash_flow = add_balance_columns(combined_trans_projection)
cash_flow = add_current_balances(cash_flow, curr_bals)
# TODO: Address the FutureWarning pd.concat warning
# Add rows at end of all 11th and 13th transactions for statement paid and statement closing
# Execute all of the calculations row by row to fill in all of the new columns for banks and cc balances
