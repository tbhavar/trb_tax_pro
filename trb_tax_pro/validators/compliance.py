from typing import Dict, List, Any
from ..models.deductions import Deductions

class ComplianceValidator:
    """
    CA-Level Validation Layer.
    Ensures deductions, losses, and regime eligibility comply with IT statutory limits.
    Any violation flagged here usually results in a notice if not resolved before filing.
    """

    @staticmethod
    def validate_deductions(deductions: Deductions, age: int) -> Dict[str, Any]:
        """
        Validates deductions against statutory limits.
        Outputs a sanitized (allowed) deduction amount and any flags/warnings.
        """
        warnings: List[str] = []
        allowed = {}

        # 80C Limit: Max 1.5 Lakhs
        if deductions.section_80c > 150000:
            warnings.append(f"Section 80C claimed ({deductions.section_80c}) exceeds the maximum limit of ₹1,50,000. Capping at ₹1,50,000.")
            allowed['section_80c'] = 150000.0
        else:
            allowed['section_80c'] = deductions.section_80c

        # 80D Limit checks (simplified baseline)
        old_age_limit = 50000 if age >= 60 else 25000
        # In a real tool, 80D also requires spouse/parents age parameters, bounding it simply here:
        max_80d = old_age_limit + 50000 # Self+Parents
        if deductions.section_80d > max_80d:
            warnings.append(f"Section 80D claimed ({deductions.section_80d}) exceeds safe limit of ₹{max_80d}. Check family age conditions.")
            allowed['section_80d'] = max_80d
        else:
            allowed['section_80d'] = deductions.section_80d

        # 24b Limit: Max 2 Lakhs (Self-Occupied)
        if deductions.section_24b > 200000:
            warnings.append(f"Section 24(b) housing interest claimed ({deductions.section_24b}) exceeds the maximum limit of ₹2,00,000. Capping at ₹2,00,000.")
            allowed['section_24b'] = 200000.0
        else:
            allowed['section_24b'] = deductions.section_24b

        # 80CCD(1B): Max 50K
        if deductions.section_80ccd_1b > 50000:
            warnings.append(f"Section 80CCD(1B) claimed ({deductions.section_80ccd_1b}) exceeds the maximum limit of ₹50,000. Capping at ₹50,000.")
            allowed['section_80ccd_1b'] = 50000.0
        else:
            allowed['section_80ccd_1b'] = deductions.section_80ccd_1b

        # 80TTA: Max 10K (Senior Citizens use 80TTB)
        if age >= 60 and deductions.section_80tta > 0:
            warnings.append("Section 80TTA claimed but taxpayer is a Senior Citizen. They should use 80TTB. Removing 80TTA.")
            allowed['section_80tta'] = 0.0
        else:
            if deductions.section_80tta > 10000:
                warnings.append(f"Section 80TTA claimed ({deductions.section_80tta}) exceeds the maximum limit of ₹10,000.")
                allowed['section_80tta'] = 10000.0
            else:
                allowed['section_80tta'] = deductions.section_80tta

        # 80TTB: Max 50K (Only for Senior Citizens)
        if age < 60 and deductions.section_80ttb > 0:
            warnings.append("Section 80TTB claimed but taxpayer is NOT a Senior Citizen. They must use 80TTA. Removing 80TTB.")
            allowed['section_80ttb'] = 0.0
        else:
            if deductions.section_80ttb > 50000:
                warnings.append(f"Section 80TTB claimed ({deductions.section_80ttb}) exceeds the maximum limit of ₹50,000.")
                allowed['section_80ttb'] = 50000.0
            else:
                allowed['section_80ttb'] = deductions.section_80ttb

        # Merge remaining attributes simply
        for field in deductions.model_fields.keys():
            if field not in allowed:
                allowed[field] = getattr(deductions, field)

        return {
            "allowed_deductions_dict": allowed,
            "compliance_warnings": warnings,
            "status": "COMPLIANT" if not warnings else "CAPPED_WITH_WARNINGS"
        }

    @staticmethod
    def validate_business_loss_regime_eligibility(business_loss: float, regime: str) -> Dict[str, Any]:
        """
        New Tax Regime has strict compliance rules around set-off of business losses.
        Under Section 115BAC, unabsorbed depreciation and certain business losses cannot be set off.
        """
        if regime == "new_regime" and business_loss > 0:
            return {
                "status": "NON_COMPLIANT",
                "message": "Notice risk: Under the New Tax Regime (Section 115BAC), business losses/unabsorbed depreciation generally cannot be set off or carried forward. Re-evaluate regime choice.",
                "action": "FORCE_OLD_REGIME_OR_DENY_LOSS"
            }
        return {"status": "COMPLIANT", "message": "Regime loss compliance OK."}

    @staticmethod
    def audit_capital_gains_setoff(stcg: float, stcl: float, ltcg: float, ltcl: float) -> List[str]:
        """
        Analyzes the set-off pattern for structural risks.
        """
        flags = []
        if ltcl > 0 and stcg > 0:
            flags.append("Warning: Long Term Capital Loss (LTCL) cannot be set off against Short Term Capital Gains (STCG).")
        return flags

    @staticmethod
    def audit_hra_claim(salary_model: Any) -> Dict[str, Any]:
        """
        Flags high-risk HRA claims based on the 2026 Risk Management System guidelines.
        """
        warnings = []
        rent_paid = getattr(salary_model, "rent_paid", 0.0)
        
        if rent_paid > 0:
            mode = getattr(salary_model, "rent_payment_mode", "NA")
            rel = getattr(salary_model, "landlord_relationship", "NA")
            
            if mode == "CASH" and rent_paid > 100000:
                warnings.append("High-Risk HRA: Rent paid in CASH exceeds INR 1,00,000. Scrutiny flag triggered.")
                
            if rel in ["PARENT", "SPOUSE", "RELATIVE"]:
                warnings.append("High-Risk HRA: Rent paid to relatives requires strict documentary evidence (bank transfers, agreements).")
                if mode == "CASH":
                    warnings.append("Critical Risk: Rent to relative paid in CASH is highly susceptible to disallowance under 2026 automated scrutiny.")
                    
        return {
            "status": "HIGH_RISK" if warnings else "CLEAN",
            "warnings": warnings
        }
