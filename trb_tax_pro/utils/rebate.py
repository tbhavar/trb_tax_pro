class Rebate87A:
    """Calculates Section 87A Rebate including Marginal Rebate for New Tax Regime."""

    @staticmethod
    def calculate(taxable_income: float, computed_tax: float, regime: str, threshold: float = 700000, max_rebate: float = 25000, is_marginal_relief_active: bool = True) -> float:
        """
        Calculates Rebate u/s 87A.
        For FY 2024-25 (New Regime), the limit is ₹7,00,000 with a max rebate of ₹25,000.
        (Proposed FY 25-26 limit is ₹12,00,000 / ₹60,000 max rebate).
        
        Marginal Rebate applies if the tax on income slightly exceeding the threshold 
        is greater than the income itself exceeding the threshold.
        """
        if taxable_income <= threshold:
            # Full rebate applies up to computed tax or max_rebate
            return min(computed_tax, max_rebate)
        
        if not is_marginal_relief_active or regime == "old_regime":
            return 0.0

        # Marginal Rebate condition:
        # Income exceeds threshold. Calculate how much it exceeds.
        excess_income = taxable_income - threshold
        
        # If the computed tax on the total income is GREATER than the excess income,
        # marginal rebate is the difference.
        if computed_tax > excess_income:
            marginal_rebate = computed_tax - excess_income
            return max(0.0, marginal_rebate)
            
        return 0.0
