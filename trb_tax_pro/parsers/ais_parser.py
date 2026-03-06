import json
import os
import pandas as pd
from typing import Dict, Any, List

class AISParser:
    """
    Parses Annual Information Statement (AIS) JSON payloads.
    Generates structured Pandas DataFrames for CA Reconciliation and TaxEngine computation.
    """

    @staticmethod
    def parse_ais_to_dataframe(filepath: str) -> pd.DataFrame:
        """
        Parses AIS JSON and returns a DataFrame suitable for Streamlit data_editor.
        Extracts Salary, Dividends, Interest, and Capital Gains.
        If file doesn't exist, generates mock AIS data bridging to exactly this structure.
        """
        if not os.path.exists(filepath):
            # Fallback mock data designed to simulate an Income Tax portal pull
            return pd.DataFrame([
                {"Category": "Salary (Sec 192)", "AIS Amount": 1500000.0, "CA Adjustment": 0.0, "Notes": ""},
                {"Category": "Savings Interest (SFT-005)", "AIS Amount": 15000.0, "CA Adjustment": 0.0, "Notes": ""},
                {"Category": "Dividends", "AIS Amount": 50000.0, "CA Adjustment": 0.0, "Notes": ""},
                {"Category": "STCG (Equity)", "AIS Amount": 120000.0, "CA Adjustment": 0.0, "Notes": ""},
                {"Category": "LTCG (Equity)", "AIS Amount": 250000.0, "CA Adjustment": 0.0, "Notes": ""}
            ])
            
        with open(filepath, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                raise ValueError("Malformed AIS JSON file provided.")
            
        rows = []
        
        # 1. Salary (Sec 192) via tdsTcsInformation
        # Will accept the legacy 'SalaryDetails' for backwards compatibility
        tds_entries = data.get("tdsTcsInformation", data.get("SalaryDetails", []))
        salary = sum(entry.get("Amount", 0.0) for entry in tds_entries if entry.get("Type", "192") == "192")
        rows.append({"Category": "Salary (Sec 192)", "AIS Amount": float(salary), "CA Adjustment": 0.0, "Notes": ""})
        
        # 2. Dividends
        div_entries = data.get("DividendDetails", [])
        dividends = sum(entry.get("Amount", 0.0) for entry in div_entries)
        rows.append({"Category": "Dividends", "AIS Amount": float(dividends), "CA Adjustment": 0.0, "Notes": ""})
        
        # Extract SFT Information for Interest/Gains
        sft_entries = data.get("sftInformation", [])
        
        # 3. Interest (SFT-016)
        sft_interest = sum(entry.get("Amount", 0.0) for entry in sft_entries if entry.get("Code") == "SFT-016")
        int_entries = data.get("InterestDetails", [])
        interest = sft_interest + sum(entry.get("Amount", 0.0) for entry in int_entries)
        rows.append({"Category": "Savings Interest (SFT-016)", "AIS Amount": float(interest), "CA Adjustment": 0.0, "Notes": ""})
        
        # 4. Capital Gains (SFT-017 and standard CapitalGainsDetails)
        sft_stcg = sum(entry.get("Amount", 0.0) for entry in sft_entries if entry.get("Code") == "SFT-017" and entry.get("GainType", "STCG") == "STCG")
        sft_ltcg = sum(entry.get("Amount", 0.0) for entry in sft_entries if entry.get("Code") == "SFT-017" and entry.get("GainType") == "LTCG")
        
        cg_entries = data.get("CapitalGainsDetails", [])
        stcg = sft_stcg + sum(entry.get("STCG", 0.0) for entry in cg_entries)
        ltcg = sft_ltcg + sum(entry.get("LTCG", 0.0) for entry in cg_entries)
        
        rows.append({"Category": "STCG (Equity)", "AIS Amount": float(stcg), "CA Adjustment": 0.0, "Notes": ""})
        rows.append({"Category": "LTCG (Equity)", "AIS Amount": float(ltcg), "CA Adjustment": 0.0, "Notes": ""})
        
        return pd.DataFrame(rows)
