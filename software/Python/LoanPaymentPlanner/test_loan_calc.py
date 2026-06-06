import pytest
import json
from loan_calc import *

def test_to_dict():
    l1 = Loan("GUC", "11/26/23", 11381, 5.5, 11592.24,138.97)
    l2 = Loan("KZT", "11/30/23", 11546, 6.77, 13243.74, 167.33)
    
    d1 = l1.to_dict()
    d2 = l2.to_dict()

    print()
    print(d1)
    print(d2)

def test_json():
    l1 = Loan("GUC", "11/26/23", 11381, 5.5, 11592.24,138.97)
    l2 = Loan("KZT", "11/30/23", 11546, 6.77, 13243.74, 167.33)
    
    d1 = l1.to_dict()
    d2 = l2.to_dict()

    print()
    print(json.dumps(d1,indent=4))
    print(json.dumps(d2,indent=4))

def test_to_json():
    l1 = Loan("GUC", "11/26/23", 11381, 5.5, 11592.24,138.97)
    l2 = Loan("KZT", "11/30/23", 11546, 6.77, 13243.74, 167.33)
    
    print()
    print(l1.jsonify())
    print(l2.jsonify())

def test_loan_forecasting_interest():
    lf = LoanForecaster()
    l1 = Loan("GUC", "11/26/23", 11381, 5.5, 11592.24,138.97)
    l2 = Loan("KZT", "11/30/23", 11546, 6.77, 13243.74, 167.33)
    

    result = lf.forecast_interest_payoff(l1, monthly_payment_amt=l1.amt_due, num_months=(12*12))
    l1_total_interest_paid = result[0]
    l1_all_interests = result[1]
    l1_all_balances = result[2]

    result = lf.forecast_interest_payoff(l2, monthly_payment_amt=l2.amt_due, num_months=(12*12))
    l2_total_interest_paid = result[0]
    l2_all_interests = result[1]
    l2_all_balances = result[2]

    # Print the total interest paid for each loan
    print()
    print(f"Total interest paid for GUC: ${l1_total_interest_paid:.2f}")
    print(f"Total interest paid for KZT: ${l2_total_interest_paid:.2f}")

    # Print the interest paid each month for each loan
    print("\nInterest paid each month for GUC:")
    for month, interest in enumerate(l1_all_interests, start=1):
        print(f"Month {month}: ${interest:.2f}, Balance: ${l1_all_balances[month-1]:.2f}")
    print("\nInterest paid each month for KZT:")
    for month, interest in enumerate(l2_all_interests, start=1):
        print(f"Month {month}: ${interest:.2f}, Balance: ${l2_all_balances[month-1]:.2f}")

    # Plot the interest paid over time for each loan and the balance over time for each loan
    import matplotlib.pyplot as plt
    months = list(range(1, len(l1_all_interests) + 1))
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.plot(months, l1_all_interests, label='GUC Interest Paid')
    plt.plot(months, l2_all_interests, label='KZT Interest Paid')
    plt.xlabel('Month')
    plt.ylabel('Interest Paid ($)')
    plt.title('Interest Paid Over Time')
    plt.legend()
    plt.grid()
    plt.subplot(1, 2, 2)
    plt.plot(months, l1_all_balances, label='GUC Balance')
    plt.plot(months, l2_all_balances, label='KZT Balance')
    plt.xlabel('Month')
    plt.ylabel('Balance ($)')
    plt.title('Balance Over Time')
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.show()

def test_loan_forecasting_monthly_payoff():
    lf = LoanForecaster()
    l1 = Loan("GUC", "11/26/23", 11381, 5.5, 11592.24,138.97)
    l2 = Loan("KZT", "11/30/23", 11546, 6.77, 13243.74, 167.33)

    result = lf.forecast_monthly_payoff(l1, monthly_payment_amt=l1.amt_due, num_months=(12*12))
    l1_months_to_payoff = result[0]
    l1_is_paid_off = result[1]
    l1_all_balances = result[2]

    result = lf.forecast_monthly_payoff(l2, monthly_payment_amt=l2.amt_due, num_months=(12*12))
    l2_months_to_payoff = result[0]
    l2_is_paid_off = result[1]
    l2_all_balances = result[2]

    print()
    print(f"GUC will be paid off in {l1_months_to_payoff} months: {l1_is_paid_off}")
    print(f"KZT will be paid off in {l2_months_to_payoff} months: {l2_is_paid_off}")

    # Plot the balance over time for each loan
    import matplotlib.pyplot as plt
    months = list(range(1, max(l1_months_to_payoff, l2_months_to_payoff) + 1))
    plt.figure(figsize=(12, 6))
    plt.plot(months[:len(l1_all_balances)], l1_all_balances, label='GUC Balance')
    plt.plot(months[:len(l2_all_balances)], l2_all_balances, label='KZT Balance')
    plt.xlabel('Month')
    plt.ylabel('Balance ($)')
    plt.title('Balance Over Time')
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.show()
    
