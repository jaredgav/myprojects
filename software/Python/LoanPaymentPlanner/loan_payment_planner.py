import sys
import datetime as dt
from  loan_calc import * 


class PayoffStrategies(object):
    """ 
    Enumeration for different payoff strategies. This can be used to determine the order
    in which loans are paid off. All strategies assume that the minimum payment is being
    made on all loans, and the additional payments are applied based on the selected strategy.
    """
    UNKNOWN = 0 # unspecified strategy
    HIGHEST_INTEREST_RATE_FIRST = 1
    LOWEST_BALANCE_FIRST = 2
    SMALLEST_MONTHLY_PAYMENT_FIRST = 3
    MINIMUM_NO_ADDITIONAL_PAYMENTS = 4
    HIGHEST_NEXT_MONTHLY_PAYMENT_FIRST = 5

class PayoffPlanConfig(object):
    def __init__(self, payoff_strategy, num_months, additional_payment_amount=0, start_date=None):
        self.strategy = payoff_strategy
        self.num_months = num_months
        self.additional_payment_amount = additional_payment_amount
        self.start_date = start_date


class LoanPaymentPlanner(object):

    def __init__(self, loan_tracker):
        self.loan_tracker = loan_tracker

    def initialize(self, loan_tracker):
        self.loan_tracker = loan_tracker
    
    def load_loans_from_file(self, file_path):
        self.loan_tracker = self.loan_tracker.from_file(file_path)
    
    def calculate_payoff_plan(self, payoff_plan_config):
        self.payoff_plan_config = payoff_plan_config
        payoff_strategy = payoff_plan_config.strategy

        if payoff_strategy == PayoffStrategies.HIGHEST_INTEREST_RATE_FIRST:
            return self.calculate_payoff_plan_highest_interest_rate_first(payoff_plan_config)
        elif payoff_strategy == PayoffStrategies.LOWEST_BALANCE_FIRST:
            return self.calculate_payoff_plan_lowest_balance_first(payoff_plan_config)
        elif payoff_strategy == PayoffStrategies.SMALLEST_MONTHLY_PAYMENT_FIRST:
            return self.calculate_payoff_plan_smallest_monthly_payment_first(payoff_plan_config)
        elif payoff_strategy == PayoffStrategies.MINIMUM_NO_ADDITIONAL_PAYMENTS:
            return self.calculate_payoff_plan_minimum_no_additional_payments(payoff_plan_config)
        elif payoff_strategy == PayoffStrategies.HIGHEST_NEXT_MONTHLY_PAYMENT_FIRST:
            return self.calculate_payoff_plan_highest_next_monthly_payment_first(payoff_plan_config)
        else:
            print(f"Unknown payoff strategy {payoff_strategy}. Exiting.")
            sys.exit(1)

    def _loan_payment_data(self):
        loans = getattr(self.loan_tracker, "loans", None)
        if loans is None:
            loans = self.loan_tracker.loans_list

        return [
            {
                "label": loan.label,
                "balance": float(loan.balance),
                "monthly_payment": float(
                    getattr(loan, "monthly_payment", None)
                    if getattr(loan, "monthly_payment", None) is not None
                    else loan.amt_due
                ),
                "monthly_rate": float(
                    getattr(loan, "interest_rate", None)
                    if getattr(loan, "interest_rate", None) is not None
                    else loan.i_rate
                ) / 100 / 12,
            }
            for loan in loans
            if loan.balance > 0
        ]

    def _additional_payment_amount(self, payoff_plan_config):
        return max(
            0,
            float(getattr(payoff_plan_config, "additional_payment_amount", 0) or 0),
        )

    def _add_months(self, start_date, months):
        month_index = start_date.month - 1 + months
        year = start_date.year + month_index // 12
        month = month_index % 12 + 1
        days_in_month = [
            31,
            29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
            31,
            30,
            31,
            30,
            31,
            31,
            30,
            31,
            30,
            31,
        ][month - 1]
        return start_date.replace(year=year, month=month, day=min(start_date.day, days_in_month))

    def _payment_date_for_month(self, month):
        payoff_plan_config = getattr(self, "payoff_plan_config", None)
        start_date = getattr(payoff_plan_config, "start_date", None)

        if start_date is None:
            return None

        return self._add_months(start_date, month)

    def _calculate_payoff_plan_by_priority(self, payoff_plan_config, priority_key, reverse=False, additional_payment_amount=None):
        sorted_loans = sorted(self._loan_payment_data(), key=priority_key, reverse=reverse)
        payoff_plan = []
        monthly_budget = sum(loan["monthly_payment"] for loan in sorted_loans)

        if additional_payment_amount is None:
            additional_payment_amount = self._additional_payment_amount(payoff_plan_config)

        monthly_budget += additional_payment_amount
        current_month = 1

        if monthly_budget <= 0:
            return payoff_plan

        while sorted_loans and current_month <= payoff_plan_config.num_months:
            for loan in sorted_loans:
                loan["balance"] += loan["balance"] * loan["monthly_rate"]

            sorted_loans.sort(key=priority_key, reverse=reverse)

            payments_by_label = {}
            remaining_budget = monthly_budget

            for loan in sorted_loans[1:]:
                payment = min(loan["monthly_payment"], loan["balance"], remaining_budget)
                loan["balance"] -= payment
                remaining_budget -= payment
                payments_by_label[loan["label"]] = payment

            while remaining_budget > 0:
                active_loans = [loan for loan in sorted_loans if loan["balance"] > 0]
                if not active_loans:
                    break

                target = sorted(active_loans, key=priority_key, reverse=reverse)[0]
                payment = min(target["balance"], remaining_budget)

                if payment <= 0:
                    break

                target["balance"] -= payment
                remaining_budget -= payment
                payments_by_label[target["label"]] = payments_by_label.get(target["label"], 0) + payment

            month_payments = []
            for loan in sorted_loans:
                loan["balance"] = max(loan["balance"], 0)
                month_payments.append(
                    (
                        loan["label"],
                        round(payments_by_label.get(loan["label"], 0), 2),
                        round(loan["balance"], 2),
                    )
                )

            total_payment = sum(payment[1] for payment in month_payments)
            payoff_plan.append((current_month, round(total_payment, 2), month_payments))
            sorted_loans = [loan for loan in sorted_loans if loan["balance"] > 0]
            current_month += 1

        return payoff_plan

    def calculate_payoff_plan_highest_interest_rate_first(self, payoff_plan_config):
        """ Provides a list of payments for each month based on the highest interest rate first payoff strategy.
            - This strategy assumes that the minimum payment is being made on all loans
            - Additional payments are applied to the loan with the highest projected next-month interest until it is paid off
            - then moves to the next highest projected next-month interest loan, and so on.
        """
        return self._calculate_payoff_plan_by_priority(
            payoff_plan_config,
            lambda loan: loan["balance"] * loan["monthly_rate"],
            reverse=True,
        )

    
    def calculate_payoff_plan_lowest_balance_first(self, payoff_plan_config):
        return self._calculate_payoff_plan_by_priority(
            payoff_plan_config,
            lambda loan: loan["balance"],
        )
    
    def calculate_payoff_plan_smallest_monthly_payment_first(self, payoff_plan_config):
        return self._calculate_payoff_plan_by_priority(
            payoff_plan_config,
            lambda loan: loan["monthly_payment"],
        )
    
    def calculate_payoff_plan_minimum_no_additional_payments(self, payoff_plan_config):
        sorted_loans = self._loan_payment_data()
        payoff_plan = []
        current_month = 1

        while sorted_loans and current_month <= payoff_plan_config.num_months:
            month_payments = []

            for loan in sorted_loans:
                loan["balance"] += loan["balance"] * loan["monthly_rate"]
                payment = min(loan["monthly_payment"], loan["balance"])
                loan["balance"] = max(loan["balance"] - payment, 0)
                month_payments.append(
                    (
                        loan["label"],
                        round(payment, 2),
                        round(loan["balance"], 2),
                    )
                )

            total_payment = sum(payment[1] for payment in month_payments)
            payoff_plan.append((current_month, round(total_payment, 2), month_payments))
            sorted_loans = [loan for loan in sorted_loans if loan["balance"] > 0]
            current_month += 1

        return payoff_plan

    def calculate_payoff_plan_highest_next_monthly_payment_first(self, payoff_plan_config):
        """ Provides a list of payments for each month based on the highest next monthly payment first payoff strategy.
            - This strategy assumes that the minimum payment is being made on all loans
            - Additional payments are applied to the loan with the highest next monthly payment including interest until it is paid off
            - Each iteration recalculates the next monthly payment for each loan based on the remaining balance and interest
            - Returns a list of payments for each month and the amount paid towards each loan for that month, as well as the remaining balance for each loan after the payment is applied.
            - (example of the tuple returned for each month: (month_number, total_payment_amount, [(loan_name, payment_amount, remaining_balance), ...]))
        """
        next_month_interest = lambda loan: loan["balance"] * loan["monthly_rate"]
        sorted_loans = sorted(
            self._loan_payment_data(),
            key=next_month_interest,
            reverse=True,
        )

        payoff_plan = []
        additional_payment_amount = max(
            0,
            float(getattr(payoff_plan_config, "additional_payment_amount", 0) or 0),
        )
        monthly_budget = sum(loan["monthly_payment"] for loan in sorted_loans) + additional_payment_amount
        current_month = 1

        if monthly_budget <= 0:
            return payoff_plan

        while sorted_loans and current_month <= payoff_plan_config.num_months:
            for loan in sorted_loans:
                loan["balance"] += loan["balance"] * loan["monthly_rate"]

            sorted_loans.sort(
                key=next_month_interest,
                reverse=True,
            )

            payments_by_label = {}
            remaining_budget = monthly_budget

            for loan in sorted_loans[1:]:
                payment = min(loan["monthly_payment"], loan["balance"], remaining_budget)
                loan["balance"] -= payment
                remaining_budget -= payment
                payments_by_label[loan["label"]] = payment

            while remaining_budget > 0:
                active_loans = [loan for loan in sorted_loans if loan["balance"] > 0]
                if not active_loans:
                    break

                target = max(active_loans, key=next_month_interest)
                payment = min(target["balance"], remaining_budget)

                if payment <= 0:
                    break

                target["balance"] -= payment
                remaining_budget -= payment
                payments_by_label[target["label"]] = payments_by_label.get(target["label"], 0) + payment

            month_payments = []
            for loan in sorted_loans:
                loan["balance"] = max(loan["balance"], 0)
                month_payments.append(
                    (
                        loan["label"],
                        round(payments_by_label.get(loan["label"], 0), 2),
                        round(loan["balance"], 2),
                    )
                )

            total_payment = sum(payment[1] for payment in month_payments)
            payoff_plan.append((current_month, round(total_payment, 2), month_payments))
            sorted_loans = [loan for loan in sorted_loans if loan["balance"] > 0]
            current_month += 1

        return payoff_plan
    
    def plot_payoff_plan(self, payoff_plan):
        """ This function plots the payoff plan where each loan has a line representing the remaining balance over time (months).
            It also plots the total payment made as a line on the same graph. 
            - a legend is included to differentiate between the loans and the total payment line.
            - The x-axis represents the months, and the y-axis represents the amount in dollars.
            - This function uses matplotlib to visualize the payoff plan.
            - The payoff_plan parameter is expected to be a list of tuples in the format: (month_number, total_payment_amount, [(loan_name, payment_amount, remaining_balance), ...])
        """
        import matplotlib.pyplot as plt

        if not payoff_plan:
            return None

        months = []
        cumulative_total_payments = []
        running_total_payment = 0
        balances_by_loan = {}
        extra_payment_targets = []
        loan_metadata = {
            loan["label"]: loan
            for loan in self._loan_payment_data()
        }

        for month, total_payment, loan_payments in payoff_plan:
            months.append(month)
            running_total_payment += total_payment
            cumulative_total_payments.append(round(running_total_payment, 2))

            extra_payment_target = None
            largest_extra_payment = 0

            for loan_name, payment_amount, remaining_balance in loan_payments:
                balances_by_loan.setdefault(loan_name, []).append((month, remaining_balance))
                monthly_payment = loan_metadata.get(loan_name, {}).get("monthly_payment", 0)
                extra_payment = payment_amount - monthly_payment

                if extra_payment > largest_extra_payment:
                    extra_payment_target = (loan_name, month, remaining_balance, self._payment_date_for_month(month))
                    largest_extra_payment = extra_payment

            if extra_payment_target is not None and largest_extra_payment > 0.005:
                extra_payment_targets.append(extra_payment_target)

        fig, ax = plt.subplots()

        for loan_name, balances in balances_by_loan.items():
            loan_months, remaining_balances = zip(*balances)
            interest_rate = loan_metadata.get(loan_name, {}).get("monthly_rate", 0) * 12 * 100
            ax.plot(
                loan_months,
                remaining_balances,
                marker="o",
                markersize=3,
                label=f"{loan_name} ({interest_rate:.2f}%)",
            )

        if extra_payment_targets:
            extra_months = [target[1] for target in extra_payment_targets]
            extra_balances = [target[2] for target in extra_payment_targets]
            ax.scatter(
                extra_months,
                extra_balances,
                marker="*",
                s=90,
                color="black",
                label="Extra Payment Target",
                zorder=5,
            )

            for loan_name, month, remaining_balance, payment_date in extra_payment_targets:
                annotation = loan_name
                if payment_date is not None:
                    annotation = f"{loan_name}\n{payment_date.strftime('%m/%d/%Y')}"

                ax.annotate(
                    annotation,
                    (month, remaining_balance),
                    textcoords="offset points",
                    xytext=(0, 8),
                    ha="center",
                    fontsize=8,
                )

        # ax.plot(
        #     months,
        #     cumulative_total_payments,
        #     marker="o",
        #     markersize=3,
        #     linestyle="--",
        #     label="Total Paid So Far",
        # )
        ax.set_xlabel("Month")
        ax.set_ylabel("Amount ($)")
        final_month = payoff_plan[-1][0]
        start_date = getattr(getattr(self, "payoff_plan_config", None), "start_date", None)
        payoff_date = self._payment_date_for_month(final_month)
        days_elapsed = (
            (payoff_date - start_date).days
            if start_date is not None and payoff_date is not None
            else final_month * 30
        )
        final_remaining_balance = sum(payment[2] for payment in payoff_plan[-1][2])
        payoff_status = (
            f"Paid off in {days_elapsed} days"
            if final_remaining_balance <= 0.005
            else f"{days_elapsed} days shown"
        )
        ax.set_title(f"Loan Payoff Plan - Total Paid: ${running_total_payment:,.2f} - {payoff_status}")
        ax.legend()
        ax.set_xticks(range(0, max(months) + 5, 5))
        ax.grid(True, axis="both")
        ax.grid(True, axis="x", which="major")
        fig.tight_layout()
        plt.show()

        return fig


    def prompt_user_for_payoff_strategy(self):
        print("Select a payoff strategy:")
        print("1. Highest Next-Month Interest First")
        print("2. Lowest Balance First")
        print("3. Smallest Monthly Payment First")
        print("4. Minimum Payments Only (No Additional Payments)")
        print("5. Highest Next-Month Interest First")
        strategy_input = input("Enter the number corresponding to your chosen strategy: ")
        strategy_mapping = {
            "1": PayoffStrategies.HIGHEST_INTEREST_RATE_FIRST,
            "2": PayoffStrategies.LOWEST_BALANCE_FIRST,
            "3": PayoffStrategies.SMALLEST_MONTHLY_PAYMENT_FIRST,
            "4": PayoffStrategies.MINIMUM_NO_ADDITIONAL_PAYMENTS,
            "5": PayoffStrategies.HIGHEST_NEXT_MONTHLY_PAYMENT_FIRST,
        }
        selected_strategy = strategy_mapping.get(strategy_input, PayoffStrategies.UNKNOWN)
        if selected_strategy == PayoffStrategies.UNKNOWN:
            print("Invalid strategy selected. Exiting.")
            sys.exit(1)
        print(f"Selected payoff strategy: {strategy_input}")
        return selected_strategy

class LoanPaymentPlannerCli(object):
    def __init__(self):
        pass
    
    def run(self, argv):
        if len(argv) > 1:
            loan_file = argv[1]
        else:
            loan_file = input("Path to loan file (e.g. loans.csv): ")

        # Create the loan tracker
        lp = LoanPaymentPlanner(LoanTracker())

        # Load in the loans from a file
        lp.load_loans_from_file(loan_file)

        # Prompt user for payoff strategy
        selected_strategy = lp.prompt_user_for_payoff_strategy()

        if selected_strategy == PayoffStrategies.HIGHEST_INTEREST_RATE_FIRST:
            print("You selected *Highest Next-Month Interest First strategy*.")
        elif selected_strategy == PayoffStrategies.LOWEST_BALANCE_FIRST:
            print("You selected *Lowest Balance First strategy*.")
        elif selected_strategy == PayoffStrategies.SMALLEST_MONTHLY_PAYMENT_FIRST:
            print("You selected *Smallest Monthly Payment First strategy*.")
        elif selected_strategy == PayoffStrategies.MINIMUM_NO_ADDITIONAL_PAYMENTS:
            print("You selected *Minimum Payments Only strategy*.")
        elif selected_strategy == PayoffStrategies.HIGHEST_NEXT_MONTHLY_PAYMENT_FIRST:
            print("You selected *Highest Next-Month Interest First strategy*.")
        else:
            print(f"Unknown strategy selected {selected_strategy}. Exiting.")
            sys.exit(1)
        
        # Determine the number of months to calculate the payoff plan for
        selected_num_months = input("Enter the number of months to calculate the payoff plan for (e.g. 60): ")

        try:
            selected_num_months = int(selected_num_months)
        except ValueError:
            print("Invalid number of months entered. Exiting.")
            sys.exit(1)

        selected_additional_payment_amount = input("Enter additional monthly payment amount (default 0): ")

        try:
            selected_additional_payment_amount = (
                0
                if selected_additional_payment_amount.strip() == ""
                else float(selected_additional_payment_amount)
            )
        except ValueError:
            print("Invalid additional payment amount entered. Exiting.")
            sys.exit(1)

        selected_start_date = input("Enter payoff plan start date (mm/dd/yyyy): ")

        try:
            selected_start_date = dt.datetime.strptime(selected_start_date, "%m/%d/%Y").date()
        except ValueError:
            print("Invalid start date entered. Use mm/dd/yyyy format. Exiting.")
            sys.exit(1)
        
        # Load the payoff plan configuration
        payoff_plan_config = PayoffPlanConfig(
            selected_strategy,
            num_months=selected_num_months,
            additional_payment_amount=selected_additional_payment_amount,
            start_date=selected_start_date,
        )

        # Perform the payoff calculations based on the selected strategy
        retVal = lp.calculate_payoff_plan(payoff_plan_config)

        # Print the payoff plan
        print(retVal)

        # plot the payoff plan
        lp.plot_payoff_plan(retVal)

if __name__ == "__main__":
    cli = LoanPaymentPlannerCli()
    cli.run(sys.argv)



