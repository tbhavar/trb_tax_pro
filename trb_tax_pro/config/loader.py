import json
import os
from typing import Dict, List, Tuple

class ConfigLoader:
    """Loads configuration data like surcharge matrices securely."""
    
    _config_cache: Dict[str, dict] = {}
    
    @classmethod
    def load_surcharge_rates(cls, financial_year: str, regime: str = "new_regime") -> List[Tuple[float, float]]:
        """
        Loads the surcharge matrix for a given financial year and regime.
        Returns a list of tuples: (threshold, rate).
        """
        if "surcharge" not in cls._config_cache:
            config_path = os.path.join(os.path.dirname(__file__), "surcharge_matrix.json")
            with open(config_path, "r") as f:
                cls._config_cache["surcharge"] = json.load(f)
                
        matrix = cls._config_cache["surcharge"]
        
        if financial_year not in matrix:
            raise KeyError(f"Surcharge rates for {financial_year} not found in matrix.")
            
        if regime not in matrix[financial_year]:
            raise KeyError(f"Regime {regime} missing in surcharge matrix for {financial_year}.")
            
        rates = []
        for tier in matrix[financial_year][regime]:
            rates.append((tier["threshold"], tier["rate"]))
            
        # Ensure it is sorted by threshold for the Marginal Relief Calculator
        return sorted(rates, key=lambda x: x[0])
