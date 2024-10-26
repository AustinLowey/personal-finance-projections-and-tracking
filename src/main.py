from datetime import datetime
from pathlib import Path

import cash_flow_projection as cfp
from data_loading import load_latest_csv, convert_currency_cols_to_int
from rec_trans_projection import project_recurring_transactions
from supp_trans_projection import project_supplemental_transactions, combine_rec_and_supp


# Load latest data and convert accounting column types to numeric
curr_bals = load_latest_csv("current_balances")
rec_trans = load_latest_csv("recurring_transactions")
curr_bals = convert_currency_cols_to_int(
    curr_bals,
    ["statement_balance", "current_balance"]
)
rec_trans = convert_currency_cols_to_int(rec_trans, ["amount"])

# Project expected transactions across a future time period
rec_trans_projection = project_recurring_transactions(rec_trans, num_months=6)
supp_trans_projection = project_supplemental_transactions()
combined_trans_projection = combine_rec_and_supp(rec_trans_projection, supp_trans_projection)

# Add rows for current balances and statement due/close dates, and add balance columns
cash_flow = cfp.add_balance_columns(combined_trans_projection)
cash_flow = cfp.add_current_balances(cash_flow, curr_bals)
cash_flow = cfp.add_cc_statement_rows(cash_flow, target_date=11, action_type="statement_due")
cash_flow = cfp.add_cc_statement_rows(cash_flow, target_date=13, action_type="statement_close")

# Execute all of the calculations row by row to fill in all of the new columns for bank/cc bals
cash_flow = cfp.calculate_future_balances(cash_flow)

# Save cash flow to ~/.finances folder
today = datetime.today().strftime("%Y%m%d")
output_folder = Path("~/.finances").expanduser() / "projected_cash_flow"
output_save_path_df = output_folder / f"{today}_cash_flow.csv"
cash_flow.to_csv(output_save_path_df, index_label="transaction_id")
print(f"Saved future cash flow projection table to: {output_save_path_df}")

# Plot and save cash flow time series future projection
output_save_path_fig = output_folder / f"{today}_cash_flow.html"
cfp.plot_save_time_series_cash_flow_balances(cash_flow, output_save_path_fig)