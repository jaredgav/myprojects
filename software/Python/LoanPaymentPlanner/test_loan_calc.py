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


