from typing import Callable, Dict, List, Tuple

class MarginalReliefCalculator:
    """Calculates Surcharge and Marginal Relief for Indian Income Tax."""

    def __init__(self, surcharge_rates: List[Tuple[float, float]]):
        """
        Initialize with a list of (threshold, rate) tuples, ascending by threshold.
        Example: [(50_00_000, 0.10), (1_00_00_000, 0.15), (2_00_00_000, 0.25), (5_00_00_000, 0.37)]
        """
        self.surcharge_rates = sorted(surcharge_rates, key=lambda x: x[0])

    def calculate(self, taxable_income: float, base_tax: float, calculate_tax_func: Callable[[float], float]) -> Dict[str, float]:
        """
        Calculate final surcharge and marginal relief.
        
        Args:
            taxable_income: The total taxable income.
            base_tax: The computed tax on taxable_income before surcharge.
            calculate_tax_func: A function that calculates tax for a given income amount.
        
        Returns:
            Dict containing initial surcharge, marginal relief, and final surcharge amount.
        """
        applicable_rate = 0.0
        applicable_threshold = 0.0
        
        # 1. Find applicable surcharge rate and threshold
        for threshold, rate in self.surcharge_rates:
            if taxable_income > threshold:
                applicable_rate = rate
                applicable_threshold = threshold
            else:
                break
                
        if applicable_rate == 0.0:
            return {"surcharge": 0.0, "marginal_relief": 0.0, "final_surcharge": 0.0}
            
        initial_surcharge = base_tax * applicable_rate
        total_tax_initial = base_tax + initial_surcharge
        
        # 2. Calculate tax exactly on the applicable threshold
        tax_on_threshold = calculate_tax_func(applicable_threshold)
        
        # 3. Determine applicable surcharge rate ON the threshold limit
        lower_threshold_rate = 0.0
        for t, r in self.surcharge_rates:
            # We strictly evaluate `applicable_threshold > t`
            if applicable_threshold > t:
                lower_threshold_rate = r
            else:
                break
                
        surcharge_on_threshold = tax_on_threshold * lower_threshold_rate
        total_tax_on_threshold = tax_on_threshold + surcharge_on_threshold
        
        # 4. Maximum tax payable allowed with marginal relief
        max_tax_payable = total_tax_on_threshold + (taxable_income - applicable_threshold)
        
        # 5. Marginal relief and final surcharge logic
        marginal_relief = max(0.0, total_tax_initial - max_tax_payable)
        final_surcharge = initial_surcharge - marginal_relief
        
        return {
            "surcharge": round(initial_surcharge, 2),
            "marginal_relief": round(marginal_relief, 2),
            "final_surcharge": round(final_surcharge, 2)
        }
