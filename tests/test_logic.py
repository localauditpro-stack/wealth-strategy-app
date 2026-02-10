import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from calculators.tier1 import analyze_tier1
# UPDATED IMPORTS
from calculators.tier2 import calculate_dr_projection, calculate_ip_projection
from utils.scoring import calculate_lead_score, get_lead_tier

class TestFinancialLogic(unittest.TestCase):

    def test_tier1_qualification(self):
        # Ready (Score >= 70)
        status, msg = analyze_tier1({"total_score": 75})
        self.assertEqual(status, "ready")
        
        # Maybe (40 <= Score < 70)
        status, msg = analyze_tier1({"total_score": 50})
        self.assertEqual(status, "maybe")
        
        # Not Ready (Score < 40)
        status, msg = analyze_tier1({"total_score": 30})
        self.assertEqual(status, "not_ready")

    def test_lead_scoring(self):
        # HNW User (Platinum)
        data = {"equity": 2500000, "income": 350000} # 60 + 50 = 110 baseline
        metrics = {"calculator_complete": 1, "email_provided": 1} # 10 + 5 = 15
        score = calculate_lead_score(data, metrics)
        self.assertTrue(score >= 80)
        self.assertEqual(get_lead_tier(score), "Platinum")
        
        # Gold User
        data = {"equity": 600000, "income": 160000} # 25 + 20 = 45
        metrics = {"calculator_complete": 1, "email_provided": 1} # 15
        score = calculate_lead_score(data, metrics)
        self.assertTrue(60 <= score < 80) # 60 total
        self.assertEqual(get_lead_tier(score), "Gold")

    def test_debt_recycling_logic(self):
        # Updated to use calculate_dr_projection
        res = calculate_dr_projection(amount=100000, growth=0.07, yield_rate=0.04, interest_rate=0.06, tax_rate=0.39, years=10)
        net_wealth = res['net_wealth']
        self.assertEqual(len(net_wealth), 10)
        self.assertTrue(net_wealth[-1] > net_wealth[0]) # Should grow (Net Equity)

    def test_ip_logic(self):
        # New IP test with full parameters
        res = calculate_ip_projection(
            price=500000, loan=500000, growth=0.06, yield_rate=0.04, 
            interest_rate=0.06, tax_rate=0.39, maint=0.01, mgmt=0.07, rates=2000, state="NSW", years=10
        )
        net_wealth = res['net_wealth']
        self.assertEqual(len(net_wealth), 10)
        # It's possible to be negative early on with 100% debt + costs, but should grow
        self.assertTrue(net_wealth[-1] > net_wealth[0])

    def test_amortization_logic(self):
        # Test P&I Loan Paydown
        loan_amount = 500000
        interest_rate = 0.05
        loan_term = 30
        
        res = calculate_ip_projection(
            price=500000, loan=loan_amount, growth=0.05, yield_rate=0.04, 
            interest_rate=interest_rate, tax_rate=0.39, maint=0.01, mgmt=0.07, rates=2000, state="NSW", 
            loan_type="Principal & Interest", loan_term=loan_term, years=10
        )
        
        loan_balances = res['loan_balance']
        
        # 1. Balance should decrease every year
        self.assertTrue(loan_balances[0] < loan_amount)
        self.assertTrue(loan_balances[-1] < loan_balances[0])
        
        # 2. Check approximate balance after 1 year vs manual calc
        # PMT = P * r * (1+r)^n / ((1+r)^n - 1)
        r = interest_rate
        n = loan_term
        pmt = (loan_amount * r * (1+r)**n) / ((1+r)**n - 1)
        interest_y1 = loan_amount * r
        principal_y1 = pmt - interest_y1
        expected_bal = loan_amount - principal_y1
        
        # Allow for small floating point diff
        self.assertAlmostEqual(loan_balances[0], expected_bal, delta=1.0)

if __name__ == '__main__':
    unittest.main()
