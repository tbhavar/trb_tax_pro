from pydantic import Field
from typing import Literal
from .base import TaxBaseModel

class Salary(TaxBaseModel):
    """
    Salary Income Model.
    Includes HRA Scrutiny parameters for high-risk claims based on the 2026 compliance guidelines.
    """
    basic: float = Field(default=0.0, description="Basic Salary")
    hra_received: float = Field(default=0.0, description="HRA received from employer")
    special_allowances: float = Field(default=0.0, description="Other allowances")
    
    # HRA Scrutiny Fields
    rent_paid: float = Field(default=0.0, description="Actual rent paid by employee")
    rent_payment_mode: Literal["BANK_TRANSFER", "CASH", "UPI", "NA"] = Field(
        default="NA", 
        description="Mode of rent payment. Cash payments raise audit flags."
    )
    landlord_relationship: Literal["RELATIVE", "PARENT", "NON_RELATIVE", "SPOUSE", "NA"] = Field(
        default="NA", 
        description="Relationship with landlord. Paying relatives raises high-risk flags."
    )
