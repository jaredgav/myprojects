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
        """ Returns a JSON formatted string of this loan """
        json_str = json.dumps(self.to_dict(),indent=4)
        return json_str

class LoanTracker(object):
    def __init__(self, loans_list=[]):
        self.loans_list = loans_list

    def add_loan(self, loan):
        self.loans_list.append(loan)

    def load_loans(self, path_to_file):
        """ Loads in loads from a formated text file
            Formatted as:
                name start_date start_balance i_rate balance amt_due
        """
        pass
    
    def print_loans(self):
        for l in self.loans_list:
            print(l)



if __name__ == "__main__":
    lt = LoanTracker()
    lt.add_loan(Loan("GUC", "11/26/23", 11381, 5.5, 11592.24,138.97))
    lt.add_loan(Loan("KZT", "11/30/23", 11546, 6.77, 13243.74, 167.33))

    lt.print_loans()
