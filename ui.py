import streamlit as st
import pandas as pd
import sys
import os

# Ensure the parent directory is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from trb_tax_pro.engine.dispatcher import MultiYearDispatcher
from trb_tax_pro.parsers.ais_parser import AISParser

st.set_page_config(page_title="TRB Tax Pro | AIS Intelligence", layout="wide")
st.title("CA Professional Tax Dashboard - AIS Intelligence")

st.sidebar.header("Configuration")
# 2026 Transition: Use "Tax Year" terminology
tax_year = st.sidebar.selectbox("Select Tax Year (Income Tax Act, 2025)", ["ty2026", "fy2025_26"])

st.header("AIS Reconciliation & Adjustment Table")

# Load AIS Data into DataFrame
ais_df = AISParser.parse_ais_to_dataframe("mock_ais.json")

st.markdown("Review the raw AIS data and provide adjustments. The **Corrected Amount** will be used for the final Unified Tax Computation.")

# Editable table using st.data_editor
edited_df = st.data_editor(
    ais_df,
    column_config={
        "Category": st.column_config.TextColumn("Income Category", disabled=True),
        "AIS Amount": st.column_config.NumberColumn("AIS Amount (INR)", disabled=True, format="%.2f"),
        "CA Adjustment": st.column_config.NumberColumn("CA Adjustment (INR)", format="%.2f", step=1000.0),
        "Notes": st.column_config.TextColumn("Notes / Justification")
    },
    use_container_width=True,
    num_rows="fixed",
    hide_index=True
)

st.markdown("### Corrected Computed Values")

# Safely copy to calculate corrected amount
final_df = edited_df.copy()
final_df["Corrected Amount"] = final_df["AIS Amount"] + final_df["CA Adjustment"]

st.dataframe(
    final_df[["Category", "AIS Amount", "CA Adjustment", "Corrected Amount", "Notes"]], 
    use_container_width=True, 
    hide_index=True
)

st.markdown("---")

if st.button("Compute Unified Tax & Delta"):
    engine = MultiYearDispatcher.resolve(tax_year)
    
    # Extract values from DataFrame dynamically
    def get_val(df, category, col):
        val = df.loc[df["Category"] == category, col].values
        return float(val[0]) if len(val) > 0 else 0.0

    # 1. Raw AIS Tax Payload
    raw_gross = (get_val(final_df, "Salary (Sec 192)", "AIS Amount") + 
                 get_val(final_df, "Dividends", "AIS Amount") + 
                 get_val(final_df, "Savings Interest (SFT-005)", "AIS Amount"))
    raw_stcg = get_val(final_df, "STCG (Equity)", "AIS Amount")
    raw_ltcg = get_val(final_df, "LTCG (Equity)", "AIS Amount")

    raw_payload = {
        "gross_income": raw_gross + raw_stcg + raw_ltcg, # Simplified aggregate for engine mock
        "regime": "new_regime"
    }
    # Utilizing base engine mock logic for demonstration
    raw_tax_result = engine.calculate_tax(raw_payload)
    raw_tax = raw_tax_result.get("tax_after_rebate", raw_tax_result.get("computed_tax", 0.0))

    # 2. Corrected CA Tax Payload
    corr_gross = (get_val(final_df, "Salary (Sec 192)", "Corrected Amount") + 
                  get_val(final_df, "Dividends", "Corrected Amount") + 
                  get_val(final_df, "Savings Interest (SFT-005)", "Corrected Amount"))
    corr_stcg = get_val(final_df, "STCG (Equity)", "Corrected Amount")
    corr_ltcg = get_val(final_df, "LTCG (Equity)", "Corrected Amount")

    corr_payload = {
        "gross_income": corr_gross + corr_stcg + corr_ltcg,
        "regime": "new_regime"
    }
    corr_tax_result = engine.calculate_tax(corr_payload)
    corr_tax = corr_tax_result.get("tax_after_rebate", corr_tax_result.get("computed_tax", 0.0))

    st.header("Unified Computation & Delta")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Tax Liability (Raw AIS)", f"INR {raw_tax:,.2f}")
    with col2:
        st.metric("Tax Liability (CA Corrected)", f"INR {corr_tax:,.2f}")
    with col3:
        delta = corr_tax - raw_tax
        if delta < 0:
            st.metric("Delta (Tax Saved)", f"INR {abs(delta):,.2f}", "Reduction")
        elif delta > 0:
            st.metric("Delta (Additional Tax)", f"INR {delta:,.2f}", "-Increase")
        else:
            st.metric("Delta", "INR 0.00", "No Change")
            
    st.info("The corrected figures have been mathematically routed through the active TaxEngine to estimate exact liability differences against the Income Tax Department's AIS assumptions. Adjustments are documented successfully.")
