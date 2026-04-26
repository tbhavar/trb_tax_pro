import sys
import os
from trb_tax_pro.engine.dispatcher import MultiYearDispatcher

def run_audit():
    years = ["fy2020_21", "fy2021_22", "fy2022_23", "fy2023_24", "fy2024_25"]
    test_cases = [500000, 700000, 755000, 780000, 1000000, 6000000] # Added 7.55L for FY23-24 Marginal Relief check
    regimes = ["old_regime", "new_regime"]

    print(f"{'Year':<12} | {'Gross':<10} | {'Regime':<12} | {'Taxable':<10} | {'Base Tax':<10} | {'Rebate':<8} | {'Surcharge':<10} | {'Total Tax':<10}")
    print("-" * 100)

    for year_id in years:
        engine = MultiYearDispatcher.resolve(year_id)
        for gross in test_cases:
            for regime in regimes:
                data = {
                    "gross_income": float(gross),
                    "regime": regime
                }
                result = engine.calculate_tax(data)
                
                print(f"{year_id:<12} | {gross:<10,} | {regime:<12} | {result['taxable_income']:<10,.0f} | {result['base_tax']:<10,.0f} | {result['rebate_87A']:<8,.0f} | {result['surcharge']:<10,.0f} | {result['total_tax']:<10,.0f}")

if __name__ == "__main__":
    run_audit()
