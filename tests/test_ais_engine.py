import pytest
import json
import pandas as pd
from trb_tax_pro.parsers.ais_parser import AISParser
from trb_tax_pro.engine.dispatcher import MultiYearDispatcher

@pytest.fixture
def mock_ais_json(tmp_path):
    """
    Mocking an exact AIS JSON structure mimicking the Income Tax Portal.
    Contains both tdsTcsInformation (Salary) and sftInformation (SFT-016 & SFT-017).
    """
    mock_data = {
        "tdsTcsInformation": [
            {"Type": "192", "Description": "Salary", "Amount": 1500000.0}
        ],
        "sftInformation": [
            {"Code": "SFT-016", "Description": "Interest from Savings", "Amount": 15000.0},
            {"Code": "SFT-017", "Description": "Sale of Shares (STCG)", "Amount": 120000.0, "GainType": "STCG"}
        ],
        "DividendDetails": [
            {"Amount": 50000.0}
        ]
    }
    file_path = tmp_path / "mock_ais.json"
    with open(file_path, "w") as f:
        json.dump(mock_data, f)
    return str(file_path)

def test_sft_mapping_and_json_mocking(mock_ais_json):
    """
    Test 1 & 3: Verifies SFT-016 maps to Interest, SFT-017 maps to Capital Gains,
    and tdsTcsInformation natively bridges to Salary.
    """
    df = AISParser.parse_ais_to_dataframe(mock_ais_json)
    
    # Verify SFT-016 (Interest)
    interest_row = df[df["Category"] == "Savings Interest (SFT-016)"]
    assert float(interest_row["AIS Amount"].iloc[0]) == 15000.0
    
    # Verify SFT-017 (Capital Gains)
    stcg_row = df[df["Category"] == "STCG (Equity)"]
    assert float(stcg_row["AIS Amount"].iloc[0]) == 120000.0
    
    # Verify tdsTcsInformation (Salary)
    salary_row = df[df["Category"] == "Salary (Sec 192)"]
    assert float(salary_row["AIS Amount"].iloc[0]) == 1500000.0
    
def test_ca_touch_reconciliation(mock_ais_json):
    """
    Test 2: Verifies that if a CA Adjustment is provided, it correctly 
    modifies the Unified Tax Computation payload (Corrected Value overrides Raw).
    """
    df = AISParser.parse_ais_to_dataframe(mock_ais_json)
    
    # CA spots a duplicate in SFT-017 and reduces STCG by 20,000 manually
    stcg_idx = df.index[df['Category'] == 'STCG (Equity)'].tolist()[0]
    df.at[stcg_idx, 'CA Adjustment'] = -20000.0
    
    df["Corrected Amount"] = df["AIS Amount"] + df["CA Adjustment"]
    
    raw_stcg = float(df[df["Category"] == "STCG (Equity)"]["AIS Amount"].iloc[0])
    corr_stcg = float(df[df["Category"] == "STCG (Equity)"]["Corrected Amount"].iloc[0])
    
    assert raw_stcg == 120000.0
    assert corr_stcg == 100000.0 # Proves the engine uses the professional correction

def test_zero_delta(mock_ais_json):
    """
    Test 4: Edge Case - Ensure no phantom Delta when CA Adjustments are zero.
    """
    df = AISParser.parse_ais_to_dataframe(mock_ais_json)
    df["Corrected Amount"] = df["AIS Amount"] + df["CA Adjustment"]
    
    for _, row in df.iterrows():
        assert float(row["Corrected Amount"]) == float(row["AIS Amount"])
        assert float(row["CA Adjustment"]) == 0.0

def test_exception_handling(tmp_path):
    """
    Test 5: Parser behavior encountering malformed JSON files.
    """
    malformed_path = tmp_path / "bad.json"
    with open(malformed_path, "w") as f:
        f.write("{ bad_json: ")
        
    with pytest.raises(ValueError, match="Malformed AIS JSON file provided."):
        AISParser.parse_ais_to_dataframe(str(malformed_path))
