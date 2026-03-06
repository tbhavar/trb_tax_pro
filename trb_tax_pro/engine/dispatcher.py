from typing import Dict, Type
from .base import TaxEngine

class MultiYearDispatcher:
    """
    Factory class handling versioning of Indian Income Tax Logic per Financial Year (pre-2026) 
    or Tax Year (2026 onwards, aligning with Income Tax Act, 2025).
    Aides in supporting ITR-U by dynamically loading historical schemas and slabs.
    """
    
    # 2026 Alignment: Income Tax Act, 2025 translation map for frontend and audit reporting
    SECTION_MAPPING_2026 = {
        "80C": "Clause 112",
        "80D": "Clause 114",
        "80G": "Clause 115",
        "24B": "Clause 42",
        "80TTA": "Clause 118",
        "80TTB": "Clause 119",
        "44AD": "Clause 58",
        "44ADA": "Clause 59",
    }
    
    _engines: Dict[str, Type[TaxEngine]] = {}
    
    @classmethod
    def register(cls, period_id: str):
        """Decorator pointing a class implementation to a period key (either FY or TY)."""
        def wrapper(engine_class: Type[TaxEngine]):
            if not issubclass(engine_class, TaxEngine):
                raise ValueError(f"{engine_class.__name__} must inherit from TaxEngine")
            cls._engines[period_id] = engine_class
            return engine_class
        return wrapper
        
    @classmethod
    def resolve(cls, period_id: str) -> TaxEngine:
        """
        Dynamically return the TaxEngine instance responsible for the requested period.
        E.g. MultiYearDispatcher.resolve('fy2025_26') or MultiYearDispatcher.resolve('ty2026_27')
        """
        engine_class = cls._engines.get(period_id)
        if not engine_class:
            raise NotImplementedError(f"No TaxEngine registered for period: '{period_id}'")
            
        return engine_class()
