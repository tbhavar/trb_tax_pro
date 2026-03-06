from typing import Dict, Any
from .base import TaxEngine
from .dispatcher import MultiYearDispatcher
from ..utils.rebate import Rebate87A

@MultiYearDispatcher.register("ty2026")
class FY2026_27Engine(TaxEngine):
    """
    Concrete Tax Engine for Tax Year 2026.
    Based on upcoming Finance Bill provisions - implements INR 75,000 SD 
    and INR 12L limit for Section 87A Marginal Rebate.
    """

    @property
    def financial_year(self) -> str:
        return "ty2026"

    def calculate_tax(self, models_data: Dict[str, Any]) -> Dict[str, Any]:
        gross_income = models_data.get("gross_income", 0.0)
        regime = models_data.get("regime", "new_regime")
        
        # 1. Apply Standard Deduction
        standard_deduction = 75000.0 if regime == "new_regime" else 50000.0
        taxable_income = max(0.0, gross_income - standard_deduction)
        
        computed_tax = taxable_income * 0.10  # Simplified mock
        
        # 1.5 Buyback proceeds update for Tax Year 2026
        # Share buyback treated as Capital Gains instead of Dividends
        buyback_proceeds = models_data.get("buyback_proceeds", 0.0)
        buyback_type = models_data.get("buyback_type", "individual") # Promoter vs Company
        if buyback_proceeds > 0:
            if buyback_type == "promoter":
                computed_tax += buyback_proceeds * 0.30
            elif buyback_type == "company":
                computed_tax += buyback_proceeds * 0.22
            else:
                computed_tax += buyback_proceeds * 0.125
        
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
