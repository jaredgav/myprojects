"""HTML reporting and JSON-based plotting for LoanPaymentResults data."""

import argparse
import html
import json
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


def plot_results(results_data):
    """Recreate the planner's balance and starred-target plot from result JSON."""
    import matplotlib.pyplot as plt

    graph_data = results_data.get("graph_data", {})
    balance_series = graph_data.get("balance_series", [])
    if not balance_series:
        return None

    fig, ax = plt.subplots()
    plotted_months = []

    for series in balance_series:
        points = series.get("points", [])
        if not points:
            continue
        months = [point["month"] for point in points]
        balances = [point["remaining_balance"] for point in points]
        plotted_months.extend(months)
        apr = series.get("annual_interest_rate", 0)
        ax.plot(
            months,
            balances,
            marker=graph_data.get("balance_line_marker", "o"),
            markersize=3,
            label=f"{series['loan']} ({apr:.2f}%)",
        )

    targets = graph_data.get("starred_targets", [])
    if targets:
        target_months = [target["month"] for target in targets]
        target_balances = [target["remaining_balance"] for target in targets]
        plotted_months.extend(target_months)
        ax.scatter(
            target_months,
            target_balances,
            marker=graph_data.get("star_marker", "*"),
            s=90,
            color="black",
            label="Extra Payment Target",
            zorder=5,
        )
        for target in targets:
            annotation = str(target["loan"])
            payment_date = target.get("payment_date")
            if payment_date:
                try:
                    from datetime import date
                    annotation = f"{annotation}\n{date.fromisoformat(payment_date).strftime('%m/%d/%Y')}"
                except ValueError:
                    annotation = f"{annotation}\n{payment_date}"
            ax.annotate(
                annotation,
                (target["month"], target["remaining_balance"]),
                textcoords="offset points",
                xytext=(0, 8),
                ha="center",
                fontsize=8,
            )

    requested_month = results_data.get("requested_months")
    if requested_month is not None:
        requested_month = int(requested_month)
        ax.axvline(
            requested_month,
            color="red",
            linestyle="--",
            linewidth=1.5,
            label=f"Desired Payoff Month ({requested_month})",
            zorder=4,
        )
        plotted_months.append(requested_month)

    ax.set_xlabel(graph_data.get("x_axis", "Month"))
    ax.set_ylabel(graph_data.get("y_axis", "Amount ($)"))
    ax.set_title(graph_data.get("chart_title", "Loan Payoff Plan"))
    tick_interval = max(1, int(graph_data.get("x_tick_interval", 5)))
    if plotted_months:
        ax.set_xticks(range(0, max(plotted_months) + tick_interval, tick_interval))
    ax.grid(True, axis="both")
    ax.grid(True, axis="x", which="major")
    ax.legend()
    fig.tight_layout()
    plt.show()
    return fig


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Replot the loan balances and starred targets stored in a planner JSON result."
    )
    parser.add_argument(
        "json_file",
        nargs="?",
        type=Path,
        help="Path to the planner results JSON file (positional form)",
    )
    parser.add_argument(
        "--json-file",
        "--json",
        dest="json_option",
        type=Path,
        help="Path to the planner results JSON file",
    )
    args = parser.parse_args(argv)
    json_path = args.json_option or args.json_file
    if json_path is None:
        parser.error("provide a results JSON file path")

    try:
        with json_path.open("r", encoding="utf-8") as input_file:
            results_data = json.load(input_file)
    except (OSError, json.JSONDecodeError) as error:
        parser.error(f"could not read results JSON: {error}")

    if not isinstance(results_data, dict) or "graph_data" not in results_data:
        parser.error("JSON file does not contain planner graph data")
    if plot_results(results_data) is None:
        parser.error("JSON file has no balance points to plot")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
