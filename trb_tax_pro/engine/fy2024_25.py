from typing import Dict, Any, List, Tuple
from .base import TaxEngine
from .dispatcher import MultiYearDispatcher
from ..utils.rebate import Rebate87A
from ..utils.marginal_relief import MarginalReliefCalculator

@MultiYearDispatcher.register("fy2024_25")
class FY2024_25Engine(TaxEngine):
    """
    Concrete Tax Engine for Financial Year 2024-25.
    Standard Deduction increased to ₹75,000 for New Regime.
    Revised slabs for New Regime.
    """

    @property
    def financial_year(self) -> str:
        return "fy2024_25"

    def _calculate_base_tax_new_regime(self, taxable_income: float) -> float:
        """Calculates base tax using FY 2024-25 New Regime Slabs."""
        tax = 0.0
        if taxable_income <= 300000:
            return 0.0
        
        # Slabs:
        # 0-3L: Nil
        # 3-7L: 5%
        # 7-10L: 10%
        # 10-12L: 15%
        # 12-15L: 20%
        # > 15L: 30%
        if taxable_income > 300000:
            tax += (min(taxable_income, 700000) - 300000) * 0.05
        if taxable_income > 700000:
            tax += (min(taxable_income, 1000000) - 700000) * 0.10
        if taxable_income > 1000000:
            tax += (min(taxable_income, 1200000) - 1000000) * 0.15
        if taxable_income > 1200000:
            tax += (min(taxable_income, 1500000) - 1200000) * 0.20
        if taxable_income > 1500000:
            tax += (taxable_income - 1500000) * 0.30
            
        return tax

    def _calculate_base_tax_old_regime(self, taxable_income: float) -> float:
        """Calculates base tax using Old Regime Slabs."""
        tax = 0.0
        if taxable_income <= 250000:
            return 0.0
        if taxable_income > 250000:
            tax += (min(taxable_income, 500000) - 250000) * 0.05
        if taxable_income > 500000:
            tax += (min(taxable_income, 1000000) - 500000) * 0.20
        if taxable_income > 1000000:
            tax += (taxable_income - 1000000) * 0.30
        return tax

    def calculate_tax(self, models_data: Dict[str, Any]) -> Dict[str, Any]:
        gross_income = models_data.get("gross_income", 0.0)
        regime = models_data.get("regime", "new_regime")
        
        # 1. Apply Standard Deduction
        standard_deduction = 75000.0 if regime == "new_regime" else 50000.0
        taxable_income = max(0.0, gross_income - standard_deduction)
        
        # 2. Base Tax Calculation
        if regime == "new_regime":
            base_tax = self._calculate_base_tax_new_regime(taxable_income)
        else:
            base_tax = self._calculate_base_tax_old_regime(taxable_income)
            
        # 3. Section 87A Rebate
        rebate = 0.0
        if regime == "new_regime":
            rebate = Rebate87A.calculate(
                taxable_income=taxable_income,
                computed_tax=base_tax,
                regime=regime,
                threshold=700000.0,
                max_rebate=25000.0
            )
        else:
            if taxable_income <= 500000:
                rebate = min(base_tax, 12500.0)
        
        tax_after_rebate = max(0.0, base_tax - rebate)
        
        # 4. Surcharge and Marginal Relief
        surcharge_rates = [
            (5000000, 0.10),
            (10000000, 0.15),
            (20000000, 0.25)
        ]
        if regime == "old_regime":
            surcharge_rates.append((50000000, 0.37))
        else:
            surcharge_rates.append((50000000, 0.25)) # Capped at 25% in New Regime
            
        def tax_func(income):
            if regime == "new_regime":
                return self._calculate_base_tax_new_regime(income)
            return self._calculate_base_tax_old_regime(income)
            
        mr_calculator = MarginalReliefCalculator(surcharge_rates)
        surcharge_result = mr_calculator.calculate(taxable_income, tax_after_rebate, tax_func)
        
        final_surcharge = surcharge_result["final_surcharge"]
        tax_before_cess = tax_after_rebate + final_surcharge
        cess = round(tax_before_cess * 0.04, 2)
        total_tax = round(tax_before_cess + cess, 2)
            
        return {
            "financial_year": self.financial_year,
            "taxable_income": taxable_income,
            "base_tax": base_tax,
            "rebate_87A": rebate,
            "tax_after_rebate": tax_after_rebate,
            "surcharge": final_surcharge,
            "marginal_relief_surcharge": surcharge_result["marginal_relief"],
            "cess": cess,
            "total_tax": total_tax,
            "standard_deduction_applied": standard_deduction
        }
