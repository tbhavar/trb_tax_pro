from datetime import date

class UpdatedReturnPenalty:
    """
    Calculates Additional Tax under Section 140B for Updated Returns (ITR-U).
    """

    @staticmethod
    def calculate_140B_penalty(total_tax_and_interest: float, end_of_assessment_year: date, actual_date_filing: date) -> float:
        """
        Section 140B: Additional Tax on Updated Return (ITR-U).
        - Up to 12 months from end of AY: 25% of aggregate of tax and interest.
        - 12 to 24 months from end of AY: 50% of aggregate of tax and interest.
        - Beyond 24 months: Added 70% threshold as per advanced scrutiny/representation logic.
        """
        if actual_date_filing <= end_of_assessment_year:
            # Not an updated return or filed within AY timeline
            return 0.0
            
        days_delayed = (actual_date_filing - end_of_assessment_year).days
        
        if days_delayed <= 365:
            # Within 12 months
            return total_tax_and_interest * 0.25
        elif days_delayed <= 730:
            # Between 12 and 24 months
            return total_tax_and_interest * 0.50
        else:
            # Beyond 24 months (Severe Delay / Scrutiny Representation Case)
            return total_tax_and_interest * 0.70
