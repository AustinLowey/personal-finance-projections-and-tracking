# Personal Finance Projections and Tracking using Python

**Overview:** Completely automating my personal finances, cash flow planning, and analytics using Python.<br>
**Main libraries:** Pandas, Matplotlib, Plotly
<br><br>

Example Sankey Diagram automatically created using Python + Plotly (numbers hidden for privacy):
<a href="https://github.com/AustinLowey/personal-finance-projections-and-tracking/blob/main/assets/img/sankeys.gif" target="_blank"><img src="assets/img/sankeys.gif">

## Cash Flow Projection (Most useful feature in repo, which I execute monthly):

### Example Output (Interactivity disabled and actual numbers hidden):

<img src="assets/img/timeseries-projection-plot2.png" width="800">

### Usage:

Set up a ~/.finances folder, then simply run main.py. (Note: Will probably add something to automatically set this folder up in the future with a template to be filled out, as several people have already utilized at least some aspects of this project.)

<img src="assets/img/finances-folder.png" width="500"><br>
~/.finances folder containing subfolders for:
1) current_balances - Current balances for all bank, credit card (statement and total), and investment accounts.
2) historical_transactions - Historical credit card and bank transaction data (not shown in screenshot).
3) projected_cash_flow - Output folder where future cash flow projection .csv files are saved
4) recurring_transactions - All recurring expenses, payments, and income and their amounts, frequencies, exact pay dates, etc.
   Examples: Rent, car payment, paychecks, food (amortized), annual subscriptions
5) supplemental_transactions - Upcoming, non-recurring, larger expenses that need to be manually input
   Examples: Flight purchase, tax return, vacation
   
Note #1: current_balances is planned to be populated automatically by connecting to financial institution accounts using an API like Teller.io<br>
Note #2: supplemental_transactions is planned to be replaced by a GUI. Managing upcoming supplemental transactions is the one aspect of this project that can never truly be completely automated (for obvious reasons).

#### Input #1 - Recurring Transactions (Periodically Updated):
<img src="assets/img/recurring-transactions.png"><br>

#### Input #2 - Current Balances (Will be Automatically Updated):
<img src="assets/img/current-balances.png" width="600"><br>

#### Data Processing Steps:
1) All instances of each recurring transaction are extrapolated across an adjustable time period (3 months into the future by default). The algorithm I developed is in src/rec_trans_projection.py and includes lots of error handling, warnings for things like if a transaction is past its end date (ex: a car loan paid off), etc.
2) Supplemental transactions, along with a row aggregating current bank and cc balances, are then "inserted" (i.e., pandas concat + sorting) into the projection dataframe.
3) Rows are added on the 11th and 13th of each future month in the projection (AFTER all other transactions on those dates - see Future Cash Flow Projection screenshots for clarity) to account for all of my cc acounts' statement due dates and close dates, respectively; these dates are easily adjustable in main.py.
4) Bank, cc statement, and cc total balances are calculated (row-by-row since each row is dependent on the previous) based on the following logic, which is why the previous step adding "statement_due" and "statement_close" rows was necessary:

<img src="assets/img/cash-flow-calculations-logic.png" width="500"><br>

5) 2 more columns are calculated across the whole dataframe using vectorized operations: (1) Total of all bank balances - Total of all credit card statement balances, and (2) Total of all bank balances - Total of all credit card total (i.e., not just statement) balances.

#### Output - Future Cash Flow Projection Across Next 3 Months:
bank_bal = Sum of all bank balances<br>
ccstmt_bal = Sum of all credit card statement balances<br>
cctotal_bal = Sum of all credit card total account balances<br>
net_bank_ccstmt = bank_bal - ccstmt_bal<br>
net_bank_cctotal = bank_bal - cctotal_bal

<img src="assets/img/cash-flow-projection1.png"><br>
<img src="assets/img/cash-flow-projection2.png"><br>
<img src="assets/img/cash-flow-projection3.png"><br>

## Needs/Wants/Savings Post-Tax Budget Breakdown:

<img src="assets/img/nsw-concise.png" width="600">

<img src="assets/img/nsw-full.png" width="600">

## To Do:
1) Automatically extract bank/investment/cc balances from linked accounts. Several APIs available, each with their own limitations. Top 2 are **Chase** (already linked accounts, but API may be significantly limited for individual developers) or **Teller.io** once they release their upcoming Python SDK.
2) Add a cc reward categories tracker that highlights the best cc to use each quarter by category. Add something to keep track of total rewards (and their value in dollars) earned from each card over a year or month.
3) Break up all retirement savings data into pre vs post tax AND stocks vs international stocks vs bonds. For traditional accounts, add an equivalent value for after getting taxed.
4) (Maybe) Add other metrics like investment/net worth time series charts, though this feature is already available from a number of financial institutions.
5) Add a script to automatically set up a ~/.finances folder with subfolders and templates.
