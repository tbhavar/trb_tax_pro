from typing import Dict, Any
from .base import TaxEngine
from .dispatcher import MultiYearDispatcher
from ..utils.rebate import Rebate87A

@MultiYearDispatcher.register("fy2025_26")
class FY2025_26Engine(TaxEngine):
    """
    Concrete Tax Engine for Financial Year 2025-26.
    Implements standard deduction of ₹75,000 and Section 87A Marginal Rebate for ₹12 Lakhs limit.
    """

    @property
    def financial_year(self) -> str:
        return "fy2025_26"

    def calculate_tax(self, models_data: Dict[str, Any]) -> Dict[str, Any]:
        # Extract taxable income base from models_data (mocked for architectural binding)
        gross_income = models_data.get("gross_income", 0.0)
        regime = models_data.get("regime", "new_regime")
        
        # 1. Apply Standard Deduction
        standard_deduction = 75000.0 if regime == "new_regime" else 50000.0
        taxable_income = max(0.0, gross_income - standard_deduction)
        
        # Mock slab calculation for example
        computed_tax = taxable_income * 0.10  # Simplified mock base tax calculation
        
        # 2. Section 87A Rebate & Marginal Rebate for the ₹12L limit
        if regime == "new_regime":
            rebate_threshold = 1200000.0
            max_rebate = 60000.0 
            rebate = Rebate87A.calculate(
                taxable_income=taxable_income,
                computed_tax=computed_tax,
                regime=regime,
                threshold=rebate_threshold,
                max_rebate=max_rebate
            )
            tax_after_rebate = computed_tax - rebate
        else:
            tax_after_rebate = computed_tax
            
        return {
            "financial_year": self.financial_year,
            "taxable_income": taxable_income,
            "base_tax": computed_tax,
            "rebate_87A": rebate if regime == "new_regime" else 0.0,
            "tax_after_rebate": max(0.0, tax_after_rebate),
            "standard_deduction_applied": standard_deduction
        }
