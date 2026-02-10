import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from utils.tax import calculate_income_tax, calculate_marginal_rate, calculate_stamp_duty

class TestTaxEngine(unittest.TestCase):

    def test_income_tax_2025(self):
        # 0 tax below 18200
        self.assertEqual(calculate_income_tax(18000), 0)
        
        # 16% bracket (e.g. 30,000)
        # (30000 - 18200) * 0.16 = 1888
        # Medicare: 30000 * 0.02 = 600
        # Total: 2488
        self.assertAlmostEqual(calculate_income_tax(30000), 2488, delta=1)
        
        # 30% bracket (e.g. 80,000)
        # Tax on 45,000 = (45000-18200)*0.16 = 4288
        # Tax on next 35,000 = 35000 * 0.30 = 10500
        # Medicare = 1600
        # Total = 16388
        self.assertAlmostEqual(calculate_income_tax(80000), 16388, delta=1)

    def test_marginal_rate(self):
        self.assertAlmostEqual(calculate_marginal_rate(30000), 0.18) # 16% + 2%
        self.assertAlmostEqual(calculate_marginal_rate(80000), 0.32) # 30% + 2%
        self.assertAlmostEqual(calculate_marginal_rate(200000), 0.47) # 45% + 2%

    def test_stamp_duty(self):
        # NSW approx check
        # 500k in NSW
        # 351k threshold base = 10530
        # (500000 - 351000) * 0.045 = 6705
        # Total = 17235
        self.assertAlmostEqual(calculate_stamp_duty("NSW", 500000), 17235, delta=100) # approximate
        
        # QLD check (lower duty usually)
        # 500k in QLD
        # 75k threshold base = 1050
        # (500000 - 75000) * 0.035 = 14875
        # Total = 15925
        self.assertAlmostEqual(calculate_stamp_duty("QLD", 500000), 15925, delta=100)

if __name__ == '__main__':
    unittest.main()
