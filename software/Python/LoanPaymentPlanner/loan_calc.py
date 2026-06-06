import os
import sys
from datetime import datetime
import json

LOAN_LABEL = "label"
LOAN_START_DATE = "start_date"
LOAN_START_BALANCE = "start_balance"
LOAN_INTEREST_RATE = "interest_rate"
LOAN_REMAIN_BALANCE = "balance"
LOAN_AMOUNT_DUE = "amnount_due"

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
                f"\tcurrent balance\t {self.i_rate}%" + "\n" + \
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
    def __init__(self, loans_list=[]):
        self.loans_list = loans_list

    def add_loan(self, loan):
        self.loans_list.append(loan)

    def load_loans(self, path_to_file):
        """Loads in loads from a formated text file
            Formatted as:
                name start_date start_balance i_rate balance amt_due
        """
        pass
    
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
    lt = LoanTracker()
    lt.add_loan(Loan("GUC", "11/26/23", 11381, 5.5, 11592.24,138.97))
    lt.add_loan(Loan("KZT", "11/30/23", 11546, 6.77, 13243.74, 167.33))

    lt.print_loans()
