from typing import Dict, Any, List, Tuple
from .base import TaxEngine
from .dispatcher import MultiYearDispatcher
from ..utils.rebate import Rebate87A
from ..utils.marginal_relief import MarginalReliefCalculator

@MultiYearDispatcher.register("fy2022_23")
class FY2022_23Engine(TaxEngine):
    """
    Concrete Tax Engine for Financial Year 2022-23.
    Same as FY 2021-22.
    """

    @property
    def financial_year(self) -> str:
        return "fy2022_23"

    def _calculate_base_tax_new_regime(self, taxable_income: float) -> float:
        """Calculates base tax using FY 2022-23 New Regime Slabs."""
        tax = 0.0
        if taxable_income <= 250000:
            return 0.0
        
        if taxable_income > 250000:
            tax += (min(taxable_income, 500000) - 250000) * 0.05
        if taxable_income > 500000:
            tax += (min(taxable_income, 750000) - 500000) * 0.10
        if taxable_income > 750000:
            tax += (min(taxable_income, 1000000) - 750000) * 0.15
        if taxable_income > 1000000:
            tax += (min(taxable_income, 1250000) - 1000000) * 0.20
        if taxable_income > 1250000:
            tax += (min(taxable_income, 1500000) - 1250000) * 0.25
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
        regime = models_data.get("regime", "old_regime")
        
        standard_deduction = 50000.0 if regime == "old_regime" else 0.0
        taxable_income = max(0.0, gross_income - standard_deduction)
        
        if regime == "new_regime":
            base_tax = self._calculate_base_tax_new_regime(taxable_income)
        else:
            base_tax = self._calculate_base_tax_old_regime(taxable_income)
            
        rebate = 0.0
        if taxable_income <= 500000:
            rebate = min(base_tax, 12500.0)
        
        tax_after_rebate = max(0.0, base_tax - rebate)
        
        surcharge_rates = [
            (5000000, 0.10),
            (10000000, 0.15),
            (20000000, 0.25),
            (50000000, 0.37)
        ]
            
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
