from typing import Dict, Any

class AISImporter:
    """
    Mock Blueprint for Annual Information Statement (AIS) parser.
    Bridges automated JSON input from the IT portal directly into TRB Tax Pro data models.
    """

    @staticmethod
    def parse_ais_json(ais_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes raw AIS/TIS JSON payload from the Income Tax Portal 
        and maps it to trb_tax_pro internal models for automation.
        """
        parsed_models = {}
        
        # 1. Extract TDS/TCS for TaxCredit Model
        tds_entries = ais_data.get("TDSDetails", [])
        total_tds_salary = sum([entry.get("Amount", 0) for entry in tds_entries if entry.get("Type") == "192"])
        total_tds_other = sum([entry.get("Amount", 0) for entry in tds_entries if entry.get("Type") != "192"])
        
        parsed_models["tax_credit"] = {
            "tds_salary": total_tds_salary,
            "tds_other": total_tds_other,
            "tcs": ais_data.get("TCSDetails", {}).get("TotalAmount", 0.0)
        }
        
        # 2. Extract Savings Interest (80TTA/TTB mapping)
        sft_entries = ais_data.get("SFTDetails", [])
        savings_interest = sum([entry.get("Amount", 0) for entry in sft_entries if entry.get("Code") == "SFT-005"])
        
        parsed_models["deductions"] = {
            "section_80tta": savings_interest  # Requires age validation downstream to swap to 80TTB
        }
        
        # 3. Extract Capital Gains (Mutual funds, equities)
        cg_entries = ais_data.get("CapitalGainsDetails", [])
        stcg = sum([entry.get("STCG", 0) for entry in cg_entries])
        ltcg_12_5 = sum([entry.get("LTCG", 0) for entry in cg_entries])
        
        parsed_models["capital_gains"] = {
            "stcg": stcg,
            "ltcg_12_5": ltcg_12_5
        }
        
        return parsed_models
