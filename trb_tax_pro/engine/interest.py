from datetime import date
from typing import Dict

class InterestEngine:
    """
    Handling Sections 234A, 234B, and 234C Interest for Default & Delay.
    Vital for parsing notices or submitting ITR-U (Updated Returns).
    """

    def __init__(self, due_date_filing: date, actual_date_filing: date, assessment_year: int):
        """
        Initializes the Interest Engine.
        """
        self.due_date_filing = due_date_filing
        self.actual_date_filing = actual_date_filing
        self.assessment_year = assessment_year

    def calculate_234A(self, total_tax_liability: float, tds_tcs: float, advance_tax: float) -> float:
        """
        Section 234A: Delay in filing Return of Income.
        Interest is 1% per month (or part of month) on the tax amount outstanding.
        """
        outstanding_tax = max(0.0, total_tax_liability - tds_tcs - advance_tax)
        if outstanding_tax < 100:  # Rounded off rule or de minimis threshold
            return 0.0
            
        if self.actual_date_filing <= self.due_date_filing:
            return 0.0
            
        # Calculate full months of delay
        months_delayed = (self.actual_date_filing.year - self.due_date_filing.year) * 12 + \
                         (self.actual_date_filing.month - self.due_date_filing.month)
        
        if self.actual_date_filing.day > self.due_date_filing.day:
            months_delayed += 1
            
        months_delayed = max(1, months_delayed)  # Even a single day delay counts as 1 month
        
        # Indian Tax Rules: Round off to nearest hundred downward
        outstanding_tax_rounded = int(outstanding_tax / 100) * 100
        
        return outstanding_tax_rounded * 0.01 * months_delayed

    def calculate_234B(self, total_tax_liability: float, tds_tcs: float, advance_tax: float) -> float:
        """
        Section 234B: Default in payment of Advance Tax.
        Applicable if Advance Tax paid < 90% of Assessed Tax.
        Interest is 1% per month from April 1 of Assessment Year to Date of Regular Assessment or Filing.
        """
        assessed_tax = max(0.0, total_tax_liability - tds_tcs)
        
        # Advance tax is only applicable if assessed tax > 10,000
        if assessed_tax < 10000:
            return 0.0
            
        if advance_tax >= (0.90 * assessed_tax):
            return 0.0
            
        outstanding_advance = max(0.0, assessed_tax - advance_tax)
        outstanding_advance_rounded = int(outstanding_advance / 100) * 100
        
        # From April 1 of AY to Date of Filing
        start_date = date(self.assessment_year, 4, 1)
        months_delayed = (self.actual_date_filing.year - start_date.year) * 12 + \
                         (self.actual_date_filing.month - start_date.month)
                         
        if self.actual_date_filing.day > start_date.day:
            months_delayed += 1
            
        months_delayed = max(1, months_delayed)
        return outstanding_advance_rounded * 0.01 * months_delayed

    def calculate_140B_additional_tax(self, total_tax_and_interest: float) -> float:
        """
        Section 140B: Additional Tax for Updated Return (ITR-U).
        As per the Finance Bill 2026:
        - <= 12 months from end of AY: 25%
        - > 12 to 24 months: 50%
        - > 24 to 48 months: 70%
        """
        end_of_assessment_year = date(self.assessment_year + 1, 3, 31)
        if self.actual_date_filing <= end_of_assessment_year:
            return 0.0

        days_delayed = (self.actual_date_filing - end_of_assessment_year).days
        months_delayed = days_delayed / 30.44

        if months_delayed <= 12:
            return total_tax_and_interest * 0.25
        elif months_delayed <= 24:
            return total_tax_and_interest * 0.50
        elif months_delayed <= 48:
            return total_tax_and_interest * 0.70
        else:
            return total_tax_and_interest * 0.70  # Cap or default to 70% for severe delays

    def generate_liability_summary(self, tax: float, tds: float, advance_tax: float) -> Dict[str, float]:
        a_interest = self.calculate_234A(tax, tds, advance_tax)
        b_interest = self.calculate_234B(tax, tds, advance_tax)
        c_interest = 0.0  
        
        total_interest = a_interest + b_interest + c_interest
        additional_tax_140B = self.calculate_140B_additional_tax(tax + total_interest)

        return {
            "234A": a_interest,
            "234B": b_interest,
            "234C": c_interest,
            "total_interest": total_interest,
            "140B_additional_tax": additional_tax_140B
        }
