from abc import ABC, abstractmethod
from typing import Dict, Any

class TaxEngine(ABC):
    """
    Abstract base class for all Financial Year specific tax engines.
    Implementing classes should provide specific tax slabs, surcharge rates, 
    and compliance checks for that particular year.
    """

    @property
    @abstractmethod
    def financial_year(self) -> str:
        """Returns the specific financial year string (e.g., 'fy2025_26')."""
        pass

    @abstractmethod
    def calculate_tax(self, models_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Input: models_data representing user income, deductions, and settings.
        Output: Full tax breakup, surcharge, cess, and marginal relief calculations.
        """
        pass
