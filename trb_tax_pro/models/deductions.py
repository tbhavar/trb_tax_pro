from pydantic import Field
from .base import TaxBaseModel

class Deductions(TaxBaseModel):
    """
    Deductions Input Model.
    Captures user-declared investments and expenditures before limits are applied.
    The Compliance Layer will subsequently validate these against statutory limits.
    """
    section_80c: float = Field(default=0.0, description="Life insurance, PPF, EPF, ELSS, etc.")
    section_80d: float = Field(default=0.0, description="Medical Insurance premiums")
    section_80dd: float = Field(default=0.0, description="Maintenance of disabled dependent")
    section_80ddb: float = Field(default=0.0, description="Medical treatment of specified diseases")
    section_24b: float = Field(default=0.0, description="Interest on housing loan (self-occupied)")
    section_80ccd_1b: float = Field(default=0.0, description="Additional NPS contribution")
    section_80ccd_2: float = Field(default=0.0, description="Employer's NPS contribution")
    section_80eea: float = Field(default=0.0, description="Interest on affordable housing loan")
    section_80u: float = Field(default=0.0, description="Person with disability")
    section_80eeb: float = Field(default=0.0, description="Interest on electric vehicle loan")
    section_80e: float = Field(default=0.0, description="Interest on education loan")
    section_80g_50percent: float = Field(default=0.0, description="Donations eligible for 50% deduction")
    section_80g_100percent: float = Field(default=0.0, description="Donations eligible for 100% deduction")
    section_80gga: float = Field(default=0.0, description="Donations for scientific research")
    section_80ggc: float = Field(default=0.0, description="Donations to political parties")
    section_80tta: float = Field(default=0.0, description="Interest on savings account (Non-Senior)")
    section_80ttb: float = Field(default=0.0, description="Interest on deposits (Senior Citizens)")
    professional_tax: float = Field(default=0.0, description="Professional Tax paid")
    food_coupons: float = Field(default=0.0, description="Meal vouchers exemption")
    other_exemption: float = Field(default=0.0, description="Other miscellaneous exemptions")
