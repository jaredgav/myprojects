import csv
from datetime import datetime
import json
from pathlib import Path

LOAN_LABEL = "label"
LOAN_START_DATE = "start_date"
LOAN_START_BALANCE = "start_balance"
LOAN_INTEREST_RATE = "interest_rate"
LOAN_REMAIN_BALANCE = "balance"
LOAN_AMOUNT_DUE = "amount_due"

def _clean_number(value):
    """Convert CSV/JSON number strings like '$11,381.00' into floats."""
    if isinstance(value, (int, float)):
        return value

    if value is None:
        return 0

    cleaned = str(value).strip().replace("$", "").replace(",", "")
    if cleaned == "":
        return 0

    return float(cleaned)


def _first_value(data, *keys, default=None):
    for key in keys:
        if key in data and data[key] not in (None, ""):
            return data[key]
    return default


def _parse_money_parts(row, index):
    value = row[index].strip()

    if "." not in value and index + 1 < len(row):
        return f"{value},{row[index + 1].strip()}", index + 2

    return value, index + 1


class Loan(object):
    def __init__(self, label="None", start_date=datetime, start_bal=0, i_rate=0, balance=0, amt_due=0):
        """
        Creates a loan with the following params:
            <label>,<start_date>,<start_balace>,<interest_rate>,<remaining_balance>,<amount_due>
        """
        self.label = label
        self.start_date = start_date
        self.start_bal = start_bal
        self.i_rate = i_rate
        self.balance = balance
        self.amt_due = amt_due

    def __str__(self):
        return  f"{self.label}" + "\n" \
                f"\tstart date:\t {self.start_date}" + "\n" + \
                f"\tstart balance\t {self.start_bal}" + "\n"  + \
                f"\tinterest rate\t {self.i_rate}%" + "\n" + \
                f"\tcurrent balance\t {self.balance}" + "\n" + \
                f"\tamount_due\t {self.amt_due}" + "\n"
                
    def to_dict(self):
        """Convert this loans member to a disctionary with key-value pairs"""
        d = {
                LOAN_LABEL: self.label,
                LOAN_START_DATE: self.start_date,
                LOAN_START_BALANCE: self.start_bal, 
                LOAN_INTEREST_RATE: self.i_rate,
                LOAN_REMAIN_BALANCE: self.balance,
                LOAN_AMOUNT_DUE: self.amt_due,
        }
        return d

    @classmethod
    def from_dict(cls, loan_data):
        """Create a Loan from JSON data or normalized CSV field names."""
        label = _first_value(loan_data, LOAN_LABEL, "name", "Name", default="None")
        start_date = _first_value(
            loan_data,
            LOAN_START_DATE,
            "Loan Start Date",
            "loan_start_date",
            default=datetime,
        )
        start_bal = _clean_number(
            _first_value(
                loan_data,
                LOAN_START_BALANCE,
                "start_bal",
                "Original Principal",
                "original_principal",
            )
        )
        i_rate = _clean_number(
            _first_value(
                loan_data,
                LOAN_INTEREST_RATE,
                "i_rate",
                "interest rate",
                "Interest Rate",
            )
        )
        balance = _clean_number(
            _first_value(
                loan_data,
                LOAN_REMAIN_BALANCE,
                "remaining_balance",
                "Amount Due",
                "Current Balance",
            )
        )
        amt_due = _clean_number(
            _first_value(
                loan_data,
                LOAN_AMOUNT_DUE,
                "amt_due",
                "Current Amt. Due",
                "monthly_payment",
            )
        )

        return cls(label, start_date, start_bal, i_rate, balance, amt_due)

    def jsonify(self):
        """ Returns a JSON formatted string of this loan"""
        json_str = json.dumps(self.to_dict(),indent=4)
        return json_str

    def original_interest(self):
        """Return the original interest from the starting balance"""
        interest = self.start_bal * ( self.i_rate / 100)
        return interest

    def current_interest_on_principle(self):
        """Return the amount of interest on the current principle"""
        interest = self.balance * ( self.i_rate / 100 )
        return interest

    def daily_interest(self):
        """Returns the amount of interest accrued daily (365) on the current principal"""
        interest = self.current_interest_on_principle() / 365
        return interest
    

        

class LoanTracker(object):
    def __init__(self, loans_list=None):
        self.loans_list = loans_list if loans_list is not None else []

    def add_loan(self, loan):
        self.loans_list.append(loan)

    def load_loans(self, path_to_file):
        """Load loans from a JSON or CSV file into this tracker."""
        path = Path(path_to_file)
        suffix = path.suffix.lower()

        if suffix == ".json":
            loans = self.load_json(path)
        elif suffix == ".csv":
            loans = self.load_csv(path)
        else:
            raise ValueError(f"Unsupported loan file type: {path.suffix}")

        for loan in loans:
            self.add_loan(loan)

        return self

    @classmethod
    def from_file(cls, path_to_file):
        tracker = cls()
        tracker.load_loans(path_to_file)
        return tracker

    def load_json(self, path_to_file):
        """Return Loan objects from JSON.

        Supports a list of loan objects, a single loan object, or
        {"loans": [...]}.
        """
        with open(path_to_file, "r", encoding="utf-8") as loan_file:
            data = json.load(loan_file)

        if isinstance(data, dict) and "loans" in data:
            data = data["loans"]
        elif isinstance(data, dict):
            data = [data]

        if not isinstance(data, list):
            raise ValueError("JSON loan files must contain a loan object or a list of loans")

        return [Loan.from_dict(loan_data) for loan_data in data]

    def load_csv(self, path_to_file):
        """Return Loan objects from CSV.

        The sample CSV uses unquoted thousands separators, so this parser accepts
        both clean CSV rows and those split money fields.
        """
        loans = []

        with open(path_to_file, "r", encoding="utf-8-sig", newline="") as loan_file:
            reader = csv.reader(loan_file)
            header = next(reader, None)

            if header is None:
                return loans

            for row in reader:
                # Skip empty rows that may be present in the CSV or if starts with #
                if not row or (len(row) == 1 and row[0].strip() == "") or (len(row) > 0 and row[0].strip().startswith("#")):
                    continue

                loan_data = self._csv_row_to_loan_data(header, row)
                loans.append(Loan.from_dict(loan_data))

        return loans

    def _csv_row_to_loan_data(self, header, row):
        if len(row) == len(header):
            return dict(zip(header, row))

        if len(row) < 8:
            raise ValueError(f"Invalid loan CSV row: {row}")

        index = 3
        original_principal, index = _parse_money_parts(row, index)
        interest_rate = row[index].strip()
        index += 1
        balance, index = _parse_money_parts(row, index)
        amount_due, index = _parse_money_parts(row, index)

        return {
            "Name": row[1].strip(),
            "Loan Start Date": row[2].strip(),
            "Original Principal": original_principal,
            "interest rate": interest_rate,
            "Amount Due": balance,
            "Current Amt. Due": amount_due,
        }
    
    def print_loans(self):
        for l in self.loans_list:
            print(l)

    def total_orig_principal(self):
        """Returns the total original principal for all loans being tracked"""
        total = 0

        for l in self.loans_list:
            total += l.start_bal

        return total


    def total_amt_due(self) -> float:
        """Returns the total amount due for all loans being tracked"""
        total = 0

        for l in self.loans_list:
            total += l.amt_due

        return total

    def total_remain_bal(self) -> float:
        """Returns the total remaining balance"""
        total = 0

        for l in self.loans_list:
            total += l.balance

        return total

    def total_original_interest(self):
        """Returns the total original interest for all loans being tracked"""
        total = 0

        for l in self.loans_list:
            total += l.original_interest()

        return total

    def total_current_interest_on_principle(self):
        """Returns the total active interest for all loans being tracked"""
        total = 0

        for l in self.loans_list:
            total += l.current_interest_on_principle()

        return total
    
    def total_daily_interest(self):
        """Returns the total daily interest for all loans being tracked"""
        total = 0

        for l in self.loans_list:
            total += l.daily_interest()

        return total
    
    def get_highest_interest_loan(self):
        """Returns the loan with the highest interest rate"""
        highest = self.loans_list[0]

        for l in self.loans_list:
            if l.i_rate > highest.i_rate:
                highest = l

        return highest
    
    def get_highest_amt_due(self):
        """Returns the loan with the highest amount due"""
        highest = self.loans_list[0]

        for l in self.loans_list:
            if l.amt_due > highest.amt_due:
                highest = l

        return highest

class LoanForecaster(object):
    def __init__(self):
        pass

    def forecast_next_month_balance(self, loan, monthly_payment_amt, additional_payment_amt=0):
        """Returns the next balance after a month with a monthly payment of y and an additional payment of z"""
        interest = loan.current_interest_on_principle() / 12
        next_balance = loan.balance + interest - monthly_payment_amt - additional_payment_amt
        return next_balance

    def forecast_next_month_interest(self, loan, monthly_payment_amt, additional_payment_amt=0):
        """Returns the next interest amount after a month with a monthly payment of y and an additional payment of z"""
        interest = loan.current_interest_on_principle() / 12
        return interest

    def forecast_next_month_principal(self, loan, monthly_payment_amt, additional_payment_amt=0):
        """Returns the next principal balance after a month with a monthly payment of y and an additional payment of z"""
        interest = loan.current_interest_on_principle() / 12
        next_principal = loan.balance + interest - monthly_payment_amt - additional_payment_amt
        return next_principal
    
    def forecast_monthly_payoff(self, loan, monthly_payment_amt, num_months, additional_payment_amt=0):
        """Returns the number of months it will take to pay off this loan with a monthly payment of y and an additional payment of z"""
        current_balance = loan.balance
        all_balances = []
        month = 0

        while current_balance > 0 and month < num_months:
            interest = current_balance * ( loan.i_rate / 100 ) / 12
            current_balance += interest - monthly_payment_amt - additional_payment_amt
            all_balances.append(current_balance)
            month += 1

        isPaidOff = current_balance <= 0
        if isPaidOff:
            print(f"At a monthly payment of ${monthly_payment_amt:.2f} and an additional payment of ${additional_payment_amt:.2f}, this loan will be paid off in {month} months.")
        else:
            print(f"At a monthly payment of ${monthly_payment_amt:.2f} and an additional payment of ${additional_payment_amt:.2f}, this loan will not be paid off in {num_months} months. Remaining balance: ${current_balance:.2f}")

        return month, isPaidOff, all_balances

    def forecast_monthly_interest_payoff(self, loan, monthly_payment_amt, num_months):
        """Returns the amount of interest that will be paid over the next num_months with a monthly payment of y"""
        total_interest = 0
        current_balance = loan.balance
        all_interests = []
        all_balances = []

        for month in range(num_months):
            interest = current_balance * ( loan.i_rate / 100 ) / 12
            all_interests.append(interest)
            total_interest += interest
            current_balance += interest - monthly_payment_amt
            all_balances.append(current_balance)

            if current_balance <= 0:
                print(f"At a monthly payment of ${monthly_payment_amt:.2f}, this loan will be paid off in {month+1} months. Total interest paid: ${total_interest:.2f}")
                break

        return total_interest, all_interests, all_balances

if __name__ == "__main__":
    gabbisLoanTracker = LoanTracker.from_file("gabbis_loans.csv")
    
    print()
    print("Gabbis Loans:")
    gabbisLoanTracker.print_loans()

    print(f"Total original principal: ${gabbisLoanTracker.total_orig_principal():.2f}")
    print(f"Total amount due this month: ${gabbisLoanTracker.total_amt_due():.2f}")
    print(f"Total remaining balance: ${gabbisLoanTracker.total_remain_bal():.2f}")
    print(f"Total original interest: ${gabbisLoanTracker.total_original_interest():.2f}")
    print(f"Total current interest on principle: ${gabbisLoanTracker.total_current_interest_on_principle():.2f}")
    print(f"Total daily interest: ${gabbisLoanTracker.total_daily_interest():.2f}")
    print(f"Highest interest loan: {gabbisLoanTracker.get_highest_interest_loan().label} at {gabbisLoanTracker.get_highest_interest_loan().i_rate}%")
    print(f"Highest amount due: {gabbisLoanTracker.get_highest_amt_due().label} at ${gabbisLoanTracker.get_highest_amt_due().amt_due:.2f}")


