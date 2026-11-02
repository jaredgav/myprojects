# Loan Payment Planner

The Loan Payment Planner reads loan balances, estimates a month-by-month payoff schedule, plots the balances, and saves a JSON result and an HTML summary. You can use the JSON result later to recreate the plot.

## Requirements

- Python 3.7 or newer
- Matplotlib for the interactive plots

Install Matplotlib if it is not already available:

```console
python -m pip install matplotlib
```

## Run the planner

Pass a `.csv` or `.json` loan file as the first argument:

```console
python loan_payment_planner.py hunters_loans.csv
```

If you omit the file argument, the planner asks for its path. It then prompts you to select a payoff strategy, enter the requested number of months, enter any additional monthly payment, and provide a start date in `mm/dd/yyyy` format. A blank additional payment is treated as zero.

Available payoff strategies:

1. **Highest Next-Month Interest First** - pays minimums and applies the extra budget to the active loan with the largest projected next-month interest.
2. **Lowest Balance First** - pays minimums and targets the active loan with the lowest balance.
3. **Smallest Monthly Payment First** - pays minimums and targets the active loan with the smallest scheduled monthly payment.
4. **Minimum Payments Only** - pays each loan's scheduled minimum; no extra payment is applied.
5. **Highest Next-Month Payment First** - pays minimums and targets the loan with the highest projected next-month payment. The estimate adds one month of projected interest to the stored monthly payment and caps it at the projected balance due. The ranking is recalculated as balances change.

For strategies 1-3 and 5, the extra monthly budget is directed to the current target after minimum payments are accounted for on the other active loans.

The entered month count is the requested horizon. If the loans are not paid off within that period, the planner extends the schedule as needed, up to 1,200 months. If the requested horizon is greater than 1,200 months, it uses that larger horizon. The result records both the requested and calculated month counts, and reports any remaining balance if the loans are not paid off within the calculation limit.

## Loan input files

### JSON

JSON can contain one loan object, a list of loan objects, or a `loans` array. The planner accepts these normalized field names:

```json
{
  "loans": [
    {
      "label": "Loan A",
      "start_date": "2025-01-15",
      "start_balance": 12000,
      "interest_rate": 6.5,
      "balance": 10500,
      "amount_due": 250
    }
  ]
}
```

`balance` is the current remaining balance, `interest_rate` is an annual percentage rate, and `amount_due` is the scheduled monthly payment. The loader also recognizes several alternate names, including `name`, `Original Principal`, `Current Amt. Due`, and `monthly_payment`.

### CSV

A simple CSV can use the same normalized names:

```csv
label,start_date,start_balance,interest_rate,balance,amount_due
Loan A,2025-01-15,12000,6.5,10500,250
```

The sample loan files in this project use a wider CSV format and can also be passed directly to the planner.

## Generated reports

Each planner run automatically creates a `reports/` folder if needed and writes timestamped files named after the input file:

- **JSON** - inputs, strategy, payoff status, monthly payment details, graph points and starred targets, totals, and the consolidation break-even APR.
- **HTML** - selected payoff plan, payoff summary, consolidation estimate, and a table of starred extra-payment targets. The table shows the loan, payment date, base amount, additional amount, total payment, and balance after payment.

The consolidation break-even APR estimates the highest annual rate at which one consolidated loan matches the selected plan's total cost over the calculated schedule. It assumes no consolidation fees and the same monthly payment budget. Actual lender fees and terms are not included.

### Important JSON fields

- `requested_months`, `calculation_limit_months`, and `months_calculated` describe the requested and actual schedule horizon.
- `payoff_strategy`, `payoff_strategy_name`, and `payoff_strategy_description` identify the selected strategy.
- `loans` contains starting balances, base monthly payments, and annual rates.
- `payments_by_month` contains each loan's base, additional, and total payment and its remaining balance for every calculated month.
- `graph_data.balance_series` contains the points for each loan balance line.
- `graph_data.starred_targets` contains the monthly extra-payment target points and annotations.
- `total_paid`, `total_interest_paid`, `remaining_balance`, and `is_paid_off` summarize the result.
- `consolidation_break_even_apr` contains the estimated break-even APR, or `null` when it cannot be calculated.

## Replot a saved result

The reporting tool reads a planner results JSON file and opens an interactive plot with the loan balance lines, starred targets, annotations, and the red desired-payoff-month marker:

```console
python loan_payment_report.py --json-file reports/hunters_loans_<timestamp>.json
```

The path can also be supplied positionally:

```console
python loan_payment_report.py reports/hunters_loans_<timestamp>.json
```

The red marker is placed at the `requested_months` value saved in the JSON. The plot extends its month axis when needed to keep the marker visible.
