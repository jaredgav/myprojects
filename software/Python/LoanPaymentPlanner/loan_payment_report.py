"""HTML report generation for LoanPaymentResults data."""

import html
from pathlib import Path


def write_html_report(results_data, output_path):
    """Write a self-contained HTML summary of the starred payment targets."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    targets = results_data.get("graph_data", {}).get("starred_targets", [])
    if targets:
        target_rows = "\n".join(
            "<tr>"
            f"<td>{target['month']}</td>"
            f"<td>{html.escape(str(target['loan']))}</td>"
            f"<td>{html.escape(str(target.get('payment_date') or ''))}</td>"
            f"<td>${target['base_amount']:,.2f}</td>"
            f"<td>${target['additional_amount']:,.2f}</td>"
            f"<td>${target['total_amount']:,.2f}</td>"
            f"<td>${target['remaining_balance']:,.2f}</td>"
            "</tr>"
            for target in targets
        )
    else:
        target_rows = '<tr><td colspan="7">No above-minimum starred payment targets were generated.</td></tr>'

    apr = results_data.get("consolidation_break_even_apr")
    consolidation_text = (
        f"A consolidation loan at or below {apr:.2f}% APR may beat this plan's cost, "
        "assuming no fees and the same monthly payment budget."
        if apr is not None
        else "A consolidation break-even rate could not be calculated for this plan."
    )
    paid_status = (
        "The loans are paid off in the calculated plan."
        if results_data.get("is_paid_off")
        else "The loans are not fully paid off within the calculation limit; the remaining balance is included below."
    )
    extension_note = ""
    if results_data.get("months_calculated", 0) > results_data.get("requested_months", 0):
        extension_note = (
            f" The selected {results_data['requested_months']} month window was extended "
            f"to {results_data['months_calculated']} months to continue toward payoff."
        )
    strategy_labels = {
        1: "Highest Next-Month Interest First",
        2: "Lowest Balance First",
        3: "Smallest Monthly Payment First",
        4: "Minimum Payments Only",
        5: "Highest Next-Month Payment First",
    }
    strategy_details = {
        1: "Pays the minimum on each active loan and directs extra payment to the loan with the highest projected next-month interest.",
        2: "Pays the minimum on each active loan and directs extra payment to the active loan with the lowest balance.",
        3: "Pays the minimum on each active loan and directs extra payment to the active loan with the smallest scheduled monthly payment.",
        4: "Pays only the scheduled minimum on each loan; no additional payment is assigned to a target loan.",
        5: "Pays the minimum on each active loan and directs extra payment to the loan with the highest projected next-month payment. The estimate adds one month of projected interest to the stored monthly payment, capped at the projected balance due.",
    }
    strategy = results_data.get("payoff_strategy")
    strategy_name = html.escape(str(
        strategy_labels.get(strategy, results_data.get("payoff_strategy_name", "Unknown strategy"))
    ))
    strategy_description = html.escape(str(
        strategy_details.get(strategy, results_data.get("payoff_strategy_description", ""))
    ))

    document = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Loan Payoff Report</title>
  <style>
    body {{ font: 16px/1.5 system-ui, sans-serif; color: #1f2937; max-width: 1000px; margin: 2rem auto; padding: 0 1rem; }}
    h1, h2 {{ color: #12304a; }}
    .summary {{ background: #f1f5f9; border-radius: 8px; padding: 1rem 1.25rem; margin: 1rem 0; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 1rem; }}
    th, td {{ border: 1px solid #cbd5e1; padding: .6rem; text-align: right; }}
    th {{ background: #e2e8f0; }}
    th:nth-child(2), td:nth-child(2) {{ text-align: left; }}
    .note {{ color: #475569; }}
  </style>
</head>
<body>
  <h1>Loan Payoff Report</h1>
  <section class="summary">
    <h2>Selected payoff plan</h2>
    <p><strong>{strategy_name}</strong></p>
    <p>{strategy_description}</p>
  </section>
  <section class="summary">
    <p><strong>Calculated months:</strong> {results_data.get('months_calculated', 0)}</p>
    <p><strong>Total paid:</strong> ${results_data.get('total_paid', 0):,.2f}</p>
    <p><strong>Estimated interest paid:</strong> ${results_data.get('total_interest_paid', 0):,.2f}</p>
    <p><strong>Remaining balance:</strong> ${results_data.get('remaining_balance', 0):,.2f}</p>
    <p>{html.escape(paid_status)}{html.escape(extension_note)}</p>
    <p>{html.escape(consolidation_text)}</p>
  </section>
  <h2>Starred payment targets</h2>
  <p>In each month below, direct the additional payment to the starred loan. The table shows its base payment, additional payment, and total payment.</p>
  <table>
    <thead><tr><th>Month</th><th>Loan to pay</th><th>Payment date</th><th>Base amount</th><th>Additional amount</th><th>Total payment</th><th>Balance after payment</th></tr></thead>
    <tbody>{target_rows}</tbody>
  </table>
  <p class="note">Consolidation estimate assumes no fees. Compare lender fees and terms before deciding.</p>
</body>
</html>
"""
    output_path.write_text(document, encoding="utf-8")
    return output_path
