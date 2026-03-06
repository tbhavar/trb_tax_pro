from pydantic import Field
from .base import TaxBaseModel

class TaxCredit(TaxBaseModel):
    """
    Tax Credit Input Model.
    Captures TDS, TCS, Advance Tax, and Self-Assessment Tax paid.
    """
    tds_salary: float = Field(default=0.0, description="TDS deducted by employer on salary (Form 16/26AS)")
    tds_other: float = Field(default=0.0, description="TDS deducted on interest, commission, etc. (Form 16A/26AS)")
    tcs: float = Field(default=0.0, description="Tax Collected at Source")
    advance_tax: float = Field(default=0.0, description="Advance Tax paid during the financial year")
    self_assessment_tax: float = Field(default=0.0, description="Self-Assessment Tax paid before filing")
    mat_amt_credit: float = Field(default=0.0, description="MAT/AMT Credit available for set-off")

    @property
    def total_prepaid_taxes(self) -> float:
        """Total taxes already paid/deducted before final computing."""
        return self.tds_salary + self.tds_other + self.tcs + self.advance_tax + self.self_assessment_tax + self.mat_amt_credit

    def calculate_net_tax_payable(self, gross_tax_liability: float) -> float:
        """
        Returns Net Tax Payable or Refund.
        Positive value -> Tax Payable by User.
        Negative value -> Refund Due to User.
        """
        return gross_tax_liability - self.total_prepaid_taxes
