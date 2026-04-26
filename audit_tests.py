import sys
import os

# Add the current directory to sys.path to import trb_tax_pro
sys.path.append(os.path.abspath("."))

from trb_tax_pro.engine.fy2025_26 import FY2025_26Engine

def run_audit():
    engine = FY2025_26Engine()
    
    test_cases = [
        {
            "name": "Below Taxable Limit",
            "data": {"gross_income": 400000, "regime": "new_regime"},
            "expected_tax_after_rebate": 0.0,
            "expected_total_tax": 0.0
        },
        {
            "name": "Income at 12L (Exactly Tax Free)",
            "data": {"gross_income": 1275000, "regime": "new_regime"},
            "expected_tax_after_rebate": 0.0,
            "expected_total_tax": 0.0
        },
        {
            "name": "Income slightly above 12L (Marginal Rebate)",
            "data": {"gross_income": 1275000 + 5000, "regime": "new_regime"},
            "expected_tax_after_rebate": 5000.0,
            "expected_total_tax": 5200.0 # 5000 + 4% cess
        },
        {
            "name": "High Income (25L)",
            "data": {"gross_income": 2575000, "regime": "new_regime"},
            "expected_tax_after_rebate": 330000.0, # (300k + (25L-24L)*0.3 = 330k)
            "expected_total_tax": 343200.0
        },
        {
            "name": "Surcharge Threshold (50L)",
            "data": {"gross_income": 5075000, "regime": "new_regime"},
            "expected_tax_after_rebate": 1080000.0,
            "expected_surcharge": 0.0,
            "expected_total_tax": 1123200.0
        },
        {
            "name": "Surcharge Marginal Relief (50.1L)",
            "data": {"gross_income": 5085000, "regime": "new_regime"},
            "expected_tax_after_rebate": 1083000.0,
            "expected_surcharge": 7000.0,
            "expected_total_tax": 1133600.0
        },
        {
            "name": "Max Surcharge New Regime (Above 5Cr)",
            "data": {"gross_income": 50075000, "regime": "new_regime"},
            "expected_tax_after_rebate": 14580000.0, # 300k + (500L-24L)*0.3 = 300k + 142.8L = 14.58M
            "expected_surcharge_rate": 0.25 # Should be capped at 25%
        }
    ]
    
    print("=== FY 2025-26 AUDIT REPORT ===")
    for case in test_cases:
        result = engine.calculate_tax(case["data"])
        actual_tax_after_rebate = result["tax_after_rebate"]
        actual_total_tax = result["total_tax"]
        actual_surcharge = result.get("surcharge", 0.0)
        
        passed = True
        if "expected_tax_after_rebate" in case and actual_tax_after_rebate != case["expected_tax_after_rebate"]:
            passed = False
        if "expected_total_tax" in case and actual_total_tax != case["expected_total_tax"]:
            passed = False
        if "expected_surcharge" in case and actual_surcharge != case["expected_surcharge"]:
            passed = False
            
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {case['name']}")
        print(f"  Result: {result}")
        if not passed:
            print(f"  MISMATCH DETECTED")
        print("-" * 30)

if __name__ == "__main__":
    run_audit()
