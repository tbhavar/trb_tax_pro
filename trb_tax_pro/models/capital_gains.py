from pydantic import Field, model_validator
from .base import TaxBaseModel
from typing import Optional

class CapitalGains(TaxBaseModel):
    """
    Capital Gains Input Model with Set-off & Carry Forward validation.
    """
    stcg: float = Field(default=0.0, description="Short Term Capital Gains")
    stcl: float = Field(default=0.0, description="Short Term Capital Loss", ge=0.0)
    
    ltcg_20: float = Field(default=0.0, description="Long Term Capital Gains @ 20% (Real Estate etc.)")
    ltcg_12_5: float = Field(default=0.0, description="Long Term Capital Gains @ 12.5% (Equity etc. for current year)")
    ltcl: float = Field(default=0.0, description="Long Term Capital Loss", ge=0.0)

    @model_validator(mode='after')
    def apply_setoff(self) -> 'CapitalGains':
        """
        LTCL can only set off against LTCG.
        STCL can set off against STCG first, then against LTCG.
        """
        # We need to compute net values, but Pydantic models with frozen=True
        # cannot be easily mutated here unless we trick it, or we simply use this 
        # validator to verify that we aren't trying to mix and match.
        # However, a better pattern is exposing properties for the "Net" amounts.
        return self

    @property
    def net_ltcg_20(self) -> float:
        return max(0.0, self.ltcg_20 - self.ltcl)

    @property
    def remaining_ltcl_after_20(self) -> float:
        return max(0.0, self.ltcl - self.ltcg_20)

    @property
    def net_ltcg_12_5(self) -> float:
        rem_ltcl = self.remaining_ltcl_after_20
        return max(0.0, self.ltcg_12_5 - rem_ltcl)

    @property
    def carry_forward_ltcl(self) -> float:
        rem_ltcl = self.remaining_ltcl_after_20
        return max(0.0, rem_ltcl - self.ltcg_12_5)

    @property
    def net_stcg(self) -> float:
        return max(0.0, self.stcg - self.stcl)
        
    @property
    def remaining_stcl_after_stcg(self) -> float:
        return max(0.0, self.stcl - self.stcg)

    @property
    def final_ltcg_20_after_stcl(self) -> float:
        stcl = self.remaining_stcl_after_stcg
        return max(0.0, self.net_ltcg_20 - stcl)

    @property
    def remaining_stcl_after_ltcg_20(self) -> float:
        stcl = self.remaining_stcl_after_stcg
        return max(0.0, stcl - self.net_ltcg_20)

    @property
    def final_ltcg_12_5_after_stcl(self) -> float:
        stcl = self.remaining_stcl_after_ltcg_20
        return max(0.0, self.net_ltcg_12_5 - stcl)

    @property
    def carry_forward_stcl(self) -> float:
        stcl = self.remaining_stcl_after_ltcg_20
        return max(0.0, stcl - self.net_ltcg_12_5)

    @property
    def total_taxable_gains(self) -> float:
        return self.net_stcg + self.final_ltcg_20_after_stcl + self.final_ltcg_12_5_after_stcl
