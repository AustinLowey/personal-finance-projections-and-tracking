from datetime import datetime
from typing import Tuple
import pandas as pd

AVG_DAYS_PER_MONTH = 30.437


def project_recurring_transactions(
    rec_trans: pd.DataFrame,
    num_months: int = 3,
    statement_due_date: int = 11
) -> pd.DataFrame:
    """
    Projects recurring transactions across a date range and returns dates,
    amounts, etc for all expected transactions in that time period.
    """

    # Define date range and calculate prorate percentage
    projection_start_date, projection_end_date = define_projection_range(
        num_months,
        statement_due_date
    )
    prorate_percentage = prorate_monthly(projection_start_date, prorate_day=statement_due_date)

    frequency_map = {
        "weekly": pd.DateOffset(weeks=1),
        "biweekly": pd.DateOffset(weeks=2),
        "monthly": pd.DateOffset(months=1),
        "quarterly": pd.DateOffset(months=3),
        "biannually": pd.DateOffset(months=6),
        "annually": pd.DateOffset(years=1),
    }
    results_df_rows = []

    for _, row in rec_trans.iterrows():
        # Check if item is past its final payment date, if applicable
        if check_if_expired(projection_start_date, row):
            continue

        # Reset these for each for loop iteration
        prorate_statement_closing = True
        current_date = datetime.strptime(row["on_date"], "%Y-%m-%d").date()

        if current_date == projection_start_date and row["precise_on_date"] == True:
            print(
                f"Warning: Transaction '{row['transaction']}' for amount '{row['amount']}' "
                "is scheduled for today. Ensure transaction is not yet reflected in current "
                "balances and if it is, modify final cash flow accordingly."
            )

        while current_date <= projection_end_date:
            next_date = (current_date + frequency_map[row["frequency"]]).date()
            if current_date < projection_start_date:
                current_date = next_date
                continue

            # Prorate monthly items that don't charge on precise dates (first instance only)
            if row["precise_on_date"] == False and prorate_statement_closing == True:
                transaction_amount = int(row["amount"] * prorate_percentage)
                prorate_statement_closing = False
            else:
                transaction_amount = row["amount"]

            # Append row of data to be used in results df and increment to next date instance
            results_df_rows.append({
                "date": current_date,
                "transaction_amount": transaction_amount,
                "transaction": row["transaction"],
                "category": row["category"],
                "charge_to": row["charge_to"]
            }) # Question: Is it best practice to append list of dicts or list of tuples/lists?
            current_date = next_date

    # Create, sort and return DataFrame
    rec_trans_projection = pd.DataFrame(
        results_df_rows,
        columns=["date", "transaction_amount", "transaction", "category", "charge_to"]
    )
    rec_trans_projection = rec_trans_projection.sort_values(
        by=["date", "transaction_amount"],
        ascending=[True, False],
        ignore_index=True
    )

    return rec_trans_projection


def define_projection_range(
    num_months: int,
    end_day_of_month: int = 11
) -> Tuple[datetime.date, datetime.date]:
    """Establishes date range to project recurring transactions across."""

    projection_start_date = datetime.today().date()
    projection_end_date = (
        (projection_start_date + pd.DateOffset(months=num_months))
        .replace(day=end_day_of_month)
        .date()
    )
    print(
        f"Projecting recurring transactions across date range: "
        f"{projection_start_date} through {projection_end_date}."
    )

    return projection_start_date, projection_end_date


def check_if_expired(
    projection_start_date: datetime.date,
    row: pd.Series
) -> bool:
    """Check if rec_trans transaction is past end_date."""

    if pd.notna(row["end_date"]):
        try:
            transaction_end_date = datetime.strptime(row["end_date"], "%Y-%m-%d").date()
            if projection_start_date > transaction_end_date:
                print(
                    f"Current date is past transaction end date '{row['end_date']}' "
                    f"for '{row['transaction']}'. Consider updating rec_trans.csv "
                    f"file at: ~/.finances/recurring_transactions/"
                )
                return True
        except ValueError as e:
            print(f"Error parsing end_date '{row['end_date']}': {e}")
        
    return False


def prorate_monthly(
    start_date: datetime.date,
    prorate_day: int = 11
) -> float:
    """Prorate percentage for monthly budget items that don't fall on precise dates."""

    if start_date.day <= 11:
        next_prorate_day = start_date.replace(day=prorate_day)

    else:
        next_prorate_day = (
            (start_date + pd.DateOffset(days=(32 - start_date.day)))
            .replace(day=prorate_day)
        )

    days_until_next_prorate_day = (next_prorate_day - start_date).days + 1  # Inclusive
    prorate_percentage = days_until_next_prorate_day / AVG_DAYS_PER_MONTH

    return prorate_percentage


if __name__ == "__main__":
    from data_loading import load_latest_csv, convert_currency_cols_to_int

    # Load latest data and convert columns if needed
    curr_bals = load_latest_csv("current_balances")
    rec_trans = load_latest_csv("recurring_transactions")
    curr_bals = convert_currency_cols_to_int(
        curr_bals,
        ["statement_balance", "current_balance"]
    )
    rec_trans = convert_currency_cols_to_int(rec_trans, ["amount"])

    rec_trans_projection = project_recurring_transactions(rec_trans, num_months=3)
    print(rec_trans_projection.head(10))
    