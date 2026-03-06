from typing import Dict

class PresumptiveTaxChecker:
    """Validates eligibility for Section 44AD and 44ADA."""
    
    @staticmethod
    def check_44ad_eligibility(gross_receipts: float, digital_receipts: float) -> Dict[str, str]:
        """
        Validates Section 44AD (Business).
        Standard Limit: INR 2 Crore.
        Enhanced Limit: INR 3 Crore (If cash receipts <= 5% of total gross receipts).
        """
        if gross_receipts <= 20000000:
            return {"status": "ELIGIBLE", "limit_applied": "2Cr", "message": "Eligible under standard 44AD limit."}
            
        if gross_receipts > 30000000:
            return {"status": "INELIGIBLE", "limit_applied": "N/A", "message": "Gross receipts exceed enhanced maximum limit of INR 3Cr."}
            
        # Between 2Cr and 3Cr, check 95% digital rule
        cash_receipts = gross_receipts - digital_receipts
        if cash_receipts <= (0.05 * gross_receipts):
            return {"status": "ELIGIBLE", "limit_applied": "3Cr", "message": "Eligible under enhanced 44AD limit due to >=95% digital receipts."}
        else:
            return {"status": "INELIGIBLE", "limit_applied": "2Cr", "message": "Limit Exceeded - Audit Required: Gross receipts exceed INR 2Cr while cash receipts exceed the 5% threshold."}

    @staticmethod
    def check_44ada_eligibility(gross_receipts: float, digital_receipts: float) -> Dict[str, str]:
        """
        Validates Section 44ADA (Profession).
        Standard Limit: INR 50 Lakhs.
        Enhanced Limit: INR 75 Lakhs (If cash receipts <= 5% of total gross receipts).
        """
        if gross_receipts <= 5000000:
            return {"status": "ELIGIBLE", "limit_applied": "50L", "message": "Eligible under standard 44ADA limit."}
            
        if gross_receipts > 7500000:
            return {"status": "INELIGIBLE", "limit_applied": "N/A", "message": "Gross receipts exceed enhanced maximum limit of INR 75L."}
            
        # Between 50L and 75L, check 95% digital rule
        cash_receipts = gross_receipts - digital_receipts
        if cash_receipts <= (0.05 * gross_receipts):
            return {"status": "ELIGIBLE", "limit_applied": "75L", "message": "Eligible under enhanced 44ADA limit due to >=95% digital receipts."}
        else:
            return {"status": "INELIGIBLE", "limit_applied": "50L", "message": "Limit Exceeded - Audit Required: Gross receipts exceed INR 50L while cash receipts exceed the 5% threshold."}

