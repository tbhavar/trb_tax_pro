import streamlit as st
import pandas as pd
import sys
import os
import json
import base64
import binascii
from datetime import date, datetime

# Ensure the parent directory is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

# Import all engine modules to ensure they are registered with the dispatcher
from trb_tax_pro.engine import (
    fy2020_21, fy2021_22, fy2022_23, fy2023_24, fy2024_25, fy2025_26, fy2026_27
)
from trb_tax_pro.engine.dispatcher import MultiYearDispatcher
from trb_tax_pro.parsers.ais_parser import AISParser
from trb_tax_pro.validators.presumptive import PresumptiveTaxChecker
from trb_tax_pro.engine.interest import InterestEngine

# Optional cryptography import for encrypted AIS files
try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import padding, hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


# ==========================================
# PAGE CONFIGURATION & THEME STYLING
# ==========================================
st.set_page_config(
    page_title="TRB Tax Pro | CA-Grade AIS & Multi-Year Tax Suite",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern, professional, high-trust CA aesthetic
st.markdown("""
<style>
    /* Global Font & Spacing */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Top Brand Banner */
    .brand-banner {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f2042 100%);
        color: #ffffff;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.75rem;
        box-shadow: 0 4px 20px rgba(15, 23, 42, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    .brand-title {
        font-size: 1.85rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    
    .brand-subtitle {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-top: 0.35rem;
        font-weight: 400;
    }
    
    .badge-pill {
        display: inline-block;
        padding: 0.25rem 0.65rem;
        font-size: 0.72rem;
        font-weight: 700;
        border-radius: 9999px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        background: #2563eb;
        color: #ffffff;
        margin-left: 0.5rem;
        vertical-align: middle;
    }

    .badge-pill-gold {
        background: #f59e0b;
        color: #0f172a;
    }

    .badge-pill-green {
        background: #10b981;
        color: #ffffff;
    }

    /* KPI / Metric Cards */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1.1rem 1.25rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
    }
    
    .metric-label {
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        color: #64748b;
        letter-spacing: 0.03em;
        margin-bottom: 0.35rem;
    }
    
    .metric-value {
        font-size: 1.55rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.2rem;
    }
    
    .metric-delta {
        font-size: 0.78rem;
        font-weight: 600;
    }
    
    .delta-positive { color: #10b981; }
    .delta-negative { color: #ef4444; }
    .delta-neutral { color: #64748b; }

    /* Comparison Box */
    .regime-card {
        border-radius: 10px;
        padding: 1.25rem;
        border: 1px solid #e2e8f0;
        background: #f8fafc;
        height: 100%;
    }
    
    .regime-card-active {
        border: 2px solid #2563eb;
        background: #ffffff;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.08);
    }

    .recommendation-banner {
        background: #ecfdf5;
        border: 1px solid #a7f3d0;
        border-radius: 8px;
        padding: 0.9rem 1.25rem;
        margin-bottom: 1.25rem;
        color: #065f46;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }

    /* Small tweaks for Streamlit elements */
    div[data-testid="stMetricValue"] {
        font-size: 1.45rem;
        font-weight: 700;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 48px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 8px 8px 0px 0px;
        gap: 6px;
        padding-top: 10px;
        padding-bottom: 10px;
        font-weight: 600;
    }

    .stTabs [aria-selected="true"] {
        background-color: rgba(37, 99, 235, 0.06);
        border-bottom: 2px solid #2563eb;
        color: #2563eb !important;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# HELPER FUNCTIONS & DECRYPTION UTILS
# ==========================================
def format_inr(val: float, decimals: bool = False) -> str:
    """Formats a float into standard Indian Rupee notation."""
    if val is None:
        return "₹ 0"
    if decimals:
        return f"₹ {val:,.2f}"
    return f"₹ {int(round(val)):,}"

def decrypt_portal_ais_bytes(raw_content: str, password: str) -> str:
    """Decrypts AES-256 encrypted AIS JSON files downloaded from the IT portal."""
    if not CRYPTO_AVAILABLE:
        raise RuntimeError("The 'cryptography' library is not available in the current environment.")
    
    content = raw_content.strip()
    salt_hex = content[:32]
    iv_hex = content[32:64]
    salt = binascii.unhexlify(salt_hex)
    iv = binascii.unhexlify(iv_hex)
    
    b64_payload = content[64:]
    ciphertext = base64.b64decode(b64_payload)
    
    iteration_options = [20000, 10000, 65536, 1000, 5000, 40000]
    passwords = [password.lower(), password.upper()]
    
    for p in passwords:
        for iters in iteration_options:
            try:
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA1(),
                    length=32,
                    salt=salt,
                    iterations=iters,
                    backend=default_backend()
                )
                key = kdf.derive(p.encode('utf-8'))
                cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
                decryptor = cipher.decryptor()
                decrypted_padded = decryptor.update(ciphertext) + decryptor.finalize()
                unpadder = padding.PKCS7(128).unpadder()
                decrypted_data = unpadder.update(decrypted_padded) + unpadder.finalize()
                return decrypted_data.decode('utf-8')
            except Exception:
                continue
    return None


YEAR_METADATA = {
    "ty2026": {
        "title": "Tax Year 2026 (FY 2026-27)",
        "ay": "AY 2027-28",
        "act": "Income Tax Act, 2025",
        "highlights": "Clause 112-119 mapping | ₹75k Standard Ded. | S.87A ₹12L limit | Buyback capital gain"
    },
    "fy2025_26": {
        "title": "FY 2025-26 (Current Year)",
        "ay": "AY 2026-27",
        "act": "Finance Act, 2025",
        "highlights": "₹75k Standard Ded. | S.87A Marginal Rebate at ₹12L threshold | 25% max surcharge"
    },
    "fy2024_25": {
        "title": "FY 2024-25",
        "ay": "AY 2025-26",
        "act": "Finance Act (No. 2), 2024",
        "highlights": "Standard Ded. ₹75k (New) / ₹50k (Old) | Default New Regime"
    },
    "fy2023_24": {
        "title": "FY 2023-24",
        "ay": "AY 2024-25",
        "act": "Finance Act, 2023",
        "highlights": "New Regime default | Standard Ded. ₹50k | S.87A ₹7L limit"
    },
    "fy2022_23": {
        "title": "FY 2022-23",
        "ay": "AY 2023-24",
        "act": "Finance Act, 2022",
        "highlights": "Historical ITR-U compliance | Old Regime vs 115BAC"
    },
    "fy2021_22": {
        "title": "FY 2021-22",
        "ay": "AY 2022-23",
        "act": "Finance Act, 2021",
        "highlights": "Historical audit & notice remediation"
    },
    "fy2020_21": {
        "title": "FY 2020-21",
        "ay": "AY 2021-22",
        "act": "Finance Act, 2020",
        "highlights": "Introduction of Section 115BAC Concessional Regime"
    }
}


# ==========================================
# SIDEBAR CONFIGURATION
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/scales.png", width=64)
    st.markdown("### **TRB Tax Pro Configuration**")
    
    # 1. Tax Year Selection
    all_registered_years = list(MultiYearDispatcher._engines.keys())
    # Sort order prioritizing current & future years
    sort_order = ["ty2026", "fy2025_26", "fy2024_25", "fy2023_24", "fy2022_23", "fy2021_22", "fy2020_21"]
    ordered_years = [y for y in sort_order if y in all_registered_years] + [y for y in all_registered_years if y not in sort_order]
    
    selected_year = st.selectbox(
        "Financial / Tax Year",
        ordered_years,
        format_func=lambda x: YEAR_METADATA.get(x, {}).get("title", x),
        index=ordered_years.index("fy2025_26") if "fy2025_26" in ordered_years else 0,
        help="Select the financial year for statutory slab routing, marginal relief rules, and ITR schedules."
    )
    
    year_info = YEAR_METADATA.get(selected_year, {})
    st.caption(f"**Assessment Year:** `{year_info.get('ay', 'N/A')}` | **Governing Act:** {year_info.get('act', 'Income Tax Act')}")
    st.caption(f"📌 *{year_info.get('highlights', '')}*")

    st.markdown("---")
    st.markdown("#### **Client & Entity Profile**")
    client_name = st.text_input("Client / Assessee Name", value="ABC Consultancy Pvt Ltd / Individual")
    pan_number = st.text_input("Permanent Account Number (PAN)", value="AAAPA1234A").upper()
    taxpayer_category = st.selectbox("Taxpayer Category", ["Individual (< 60 yrs)", "Senior Citizen (60 - 80 yrs)", "Super Senior (> 80 yrs)"])

    st.markdown("---")
    st.markdown("#### **AIS Source & Ingestion**")
    data_source = st.radio("Select Ingestion Mode", ["Demo / Mock AIS Data", "Upload Official AIS JSON"], index=0)
    
    uploaded_file = None
    decryption_pwd = ""
    if data_source == "Upload Official AIS JSON":
        uploaded_file = st.file_uploader("Upload Portal AIS JSON", type=["json", "txt"])
        decryption_pwd = st.text_input(
            "File Password (if encrypted)", 
            type="password",
            help="Default portal password is PAN in CAPS + Date of Birth (DDMMYYYY). E.g. ABCDE1234F01011990"
        )
    
    st.markdown("---")
    st.markdown(
        """
        <div style="font-size: 0.8rem; color: #64748b; text-align: center;">
            <strong>TRB Tax Pro v1.1.2</strong><br>
            Developed for Chartered Accountants & Tax Practitioners.<br>
            <a href="https://buymeacoffee.com/tbhavar" target="_blank" style="color: #2563eb; text-decoration: none; font-weight: 600;">☕ Support Developer</a>
        </div>
        """,
        unsafe_allow_html=True
    )


# ==========================================
# TOP HERO BANNER
# ==========================================
st.markdown(
    f"""
    <div class="brand-banner">
        <div class="brand-title">
            <span>⚖️ TRB TAX PRO</span>
            <span class="badge-pill">CA-GRADE SUITE</span>
            <span class="badge-pill badge-pill-gold">{selected_year.upper()}</span>
        </div>
        <div class="brand-subtitle">
            Statutory Multi-Year Tax Engine • Precision AIS Reconciliation • Section 87A Marginal Cliff Resolution • ITR-U Audit Planner
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ==========================================
# DATA LOADING & RECONCILIATION LOGIC
# ==========================================
@st.cache_data
def get_mock_ais_dataframe() -> pd.DataFrame:
    return pd.DataFrame([
        {"Category": "Salary (Sec 192)", "AIS Amount": 1500000.0, "CA Adjustment": 0.0, "Notes": "Form 16 verified"},
        {"Category": "Savings Interest (SFT-016)", "AIS Amount": 22500.0, "CA Adjustment": 0.0, "Notes": "Bank interest auto-populated"},
        {"Category": "Dividends", "AIS Amount": 45000.0, "CA Adjustment": 0.0, "Notes": "Gross dividend entries"},
        {"Category": "STCG (Equity - 111A)", "AIS Amount": 120000.0, "CA Adjustment": 0.0, "Notes": "Broker P&L matching pending"},
        {"Category": "LTCG (Equity - 112A)", "AIS Amount": 250000.0, "CA Adjustment": 0.0, "Notes": "Long term capital gains"}
    ])

# Handle AIS parsing with error protection
ais_df = None
parsing_note = ""

if data_source == "Upload Official AIS JSON" and uploaded_file is not None:
    try:
        raw_bytes = uploaded_file.read().decode('utf-8', errors='ignore')
        
        # Check if file is encrypted (64 hex characters prefix)
        is_encrypted = len(raw_bytes) > 64 and all(c in '0123456789abcdefABCDEF' for c in raw_bytes[:64])
        
        if is_encrypted:
            if not decryption_pwd:
                st.warning("⚠️ This AIS JSON appears to be encrypted by the Income Tax Portal. Please provide the password (PAN + DOB in DDMMYYYY) in the sidebar.")
                ais_df = get_mock_ais_dataframe()
            else:
                with st.spinner("Decrypting AIS JSON payload..."):
                    decrypted_text = decrypt_portal_ais_bytes(raw_bytes, decryption_pwd)
                    if decrypted_text:
                        temp_path = "temp_decrypted_ais.json"
                        with open(temp_path, "w", encoding="utf-8") as f:
                            f.write(decrypted_text)
                        ais_df = AISParser.parse_ais_to_dataframe(temp_path)
                        st.success("✅ Successfully decrypted and parsed portal AIS payload!")
                    else:
                        st.error("❌ Decryption failed. Please verify that the password matches PAN in uppercase followed by DOB in DDMMYYYY.")
                        ais_df = get_mock_ais_dataframe()
        else:
            temp_path = "temp_uploaded_ais.json"
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(raw_bytes)
            ais_df = AISParser.parse_ais_to_dataframe(temp_path)
            st.success(f"✅ Successfully imported AIS data from: `{uploaded_file.name}`")
    except Exception as e:
        st.error(f"Error parsing uploaded file: {str(e)}. Falling back to sample structure.")
        ais_df = get_mock_ais_dataframe()
else:
    ais_df = get_mock_ais_dataframe()
    parsing_note = "Displaying Interactive Demo AIS Dataset. You can modify any adjustment in the table below."


# Initialize session state for adjustments if not present
if "working_df" not in st.session_state or st.session_state.get("active_source") != data_source:
    st.session_state.working_df = ais_df.copy()
    st.session_state.active_source = data_source


# ==========================================
# DASHBOARD TABS
# ==========================================
tab_recon, tab_tax, tab_audit, tab_memo = st.tabs([
    "📋 AIS Reconciliation & Adjustments",
    "⚖️ Unified Tax Engine & Slabs",
    "🕒 Multi-Year Audit & ITR-U Planner",
    "📑 CA Workpaper Memo & Export"
])


# ====================================================================
# TAB 1: AIS RECONCILIATION & ADJUSTMENTS
# ====================================================================
with tab_recon:
    st.markdown("#### **Annual Information Statement (AIS) Reconciliation Table**")
    st.markdown(
        "Compare reported portal amounts with actual books of accounts. Provide statutory justifications for audit trail defense."
    )
    
    # Preset Quick Action Buttons
    col_preset1, col_preset2, col_preset3, col_preset4 = st.columns([1, 1, 1, 1])
    with col_preset1:
        if st.button("➕ Exclude Duplicate SFT (-₹5k)"):
            mask = st.session_state.working_df["Category"].str.contains("Interest", case=False)
            st.session_state.working_df.loc[mask, "CA Adjustment"] -= 5000.0
            st.session_state.working_df.loc[mask, "Notes"] = "Excluded duplicate bank interest reported under SFT-016"
            st.rerun()
    with col_preset2:
        if st.button("➖ Apply Exemption / HRA (-₹50k)"):
            mask = st.session_state.working_df["Category"].str.contains("Salary", case=False)
            st.session_state.working_df.loc[mask, "CA Adjustment"] -= 50000.0
            st.session_state.working_df.loc[mask, "Notes"] = "Allowed exempt allowances u/s 10 not factored in AIS"
            st.rerun()
    with col_preset3:
        if st.button("📈 Adjust Broker CG (+₹15k)"):
            mask = st.session_state.working_df["Category"].str.contains("STCG", case=False)
            st.session_state.working_df.loc[mask, "CA Adjustment"] += 15000.0
            st.session_state.working_df.loc[mask, "Notes"] = "Reconciled with Consolidated Broker Tax P&L Statement"
            st.rerun()
    with col_preset4:
        if st.button("🔄 Reset Adjustments"):
            st.session_state.working_df["CA Adjustment"] = 0.0
            st.session_state.working_df["Notes"] = ""
            st.rerun()

    # Editable Table
    edited_df = st.data_editor(
        st.session_state.working_df,
        column_config={
            "Category": st.column_config.TextColumn("Income Stream / Section", disabled=True, width="medium"),
            "AIS Amount": st.column_config.NumberColumn("AIS Reported (INR)", disabled=True, format="₹ %.2f"),
            "CA Adjustment": st.column_config.NumberColumn("CA Adjustment (INR)", format="₹ %.2f", step=500.0),
            "Notes": st.column_config.TextColumn("CA Audit Justification / Remarks", width="large")
        },
        width="stretch",
        num_rows="fixed",
        hide_index=True,
        key="ais_editor"
    )
    
    # Compute corrected totals
    final_recon_df = edited_df.copy()
    final_recon_df["Corrected Amount"] = final_recon_df["AIS Amount"] + final_recon_df["CA Adjustment"]
    
    # Store in session state
    st.session_state.working_df = final_recon_df

    # Summary KPI row
    total_ais = final_recon_df["AIS Amount"].sum()
    total_adj = final_recon_df["CA Adjustment"].sum()
    total_corrected = final_recon_df["Corrected Amount"].sum()
    active_mismatches = (final_recon_df["CA Adjustment"] != 0).sum()

    st.markdown("<br>", unsafe_allow_html=True)
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric("Total AIS Reported Gross", format_inr(total_ais))
    with kpi2:
        st.metric(
            "Net CA Adjustments", 
            format_inr(total_adj), 
            delta=f"{format_inr(total_adj)}" if total_adj != 0 else "No Variance",
            delta_color="normal" if total_adj <= 0 else "inverse"
        )
    with kpi3:
        st.metric("Final Taxable Aggregate", format_inr(total_corrected))
    with kpi4:
        st.metric("Reconciled Line Items", f"{active_mismatches} / {len(final_recon_df)} Adjusted")

    # Visual breakdown
    st.markdown("---")
    st.markdown("#### **Income Stream Distribution (AIS vs CA Reconciled)**")
    chart_data = pd.DataFrame({
        "Category": final_recon_df["Category"],
        "AIS Reported": final_recon_df["AIS Amount"],
        "CA Corrected": final_recon_df["Corrected Amount"]
    }).set_index("Category")
    st.bar_chart(chart_data)


# ====================================================================
# TAB 2: UNIFIED TAX ENGINE & SLABS
# ====================================================================
with tab_tax:
    st.markdown("#### **Statutory Tax Computation Engine**")
    st.markdown(
        f"Evaluating income under **{YEAR_METADATA.get(selected_year, {}).get('title', selected_year)}** with dual-regime comparison and marginal relief."
    )
    
    # Optional deductions inputs for Old Regime evaluation
    with st.expander("⚙️ Optional Deductions for Old Tax Regime Evaluation (Chapter VI-A)", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            sec_80c = st.number_input("Section 80C (PPF, ELSS, EPF, etc.)", min_value=0.0, max_value=150000.0, value=150000.0, step=10000.0)
        with c2:
            sec_80d = st.number_input("Section 80D (Health Insurance)", min_value=0.0, max_value=100000.0, value=25000.0, step=5000.0)
        with c3:
            sec_other = st.number_input("Other Deductions (80CCD, 80G, 80TTA)", min_value=0.0, value=10000.0, step=5000.0)
        total_chapter_via = sec_80c + sec_80d + sec_other

    # Resolve active TaxEngine
    engine = MultiYearDispatcher.resolve(selected_year)

    # 1. Computation with CA Corrected Income
    corrected_gross = float(final_recon_df["Corrected Amount"].sum())
    
    # Compute New Regime
    new_payload = {"gross_income": corrected_gross, "regime": "new_regime"}
    if selected_year == "ty2026":
        new_payload["buyback_proceeds"] = 0.0
    new_result = engine.calculate_tax(new_payload)

    # Compute Old Regime (subtracting Chapter VI-A deductions from gross)
    old_gross_reduced = max(0.0, corrected_gross - total_chapter_via)
    old_payload = {"gross_income": old_gross_reduced, "regime": "old_regime"}
    if selected_year == "ty2026":
        old_payload["buyback_proceeds"] = 0.0
    old_result = engine.calculate_tax(old_payload)

    # 2. Computation with Raw AIS (for Delta Analysis)
    raw_gross = float(final_recon_df["AIS Amount"].sum())
    raw_result = engine.calculate_tax({"gross_income": raw_gross, "regime": "new_regime"})

    # Regime Comparison Callout Banner
    diff = old_result["total_tax"] - new_result["total_tax"]
    if diff > 0:
        recommended = "New Tax Regime"
        savings = diff
        callout_html = f"""
        <div class="recommendation-banner">
            <span>✨ <strong>CA Recommendation:</strong> <b>{recommended}</b> is more beneficial, saving <b>{format_inr(savings)}</b> in total tax liability compared to the Old Regime.</span>
        </div>
        """
    elif diff < 0:
        recommended = "Old Tax Regime"
        savings = abs(diff)
        callout_html = f"""
        <div class="recommendation-banner" style="background: #eff6ff; border-color: #bfdbfe; color: #1e40af;">
            <span>✨ <strong>CA Recommendation:</strong> <b>{recommended}</b> is more beneficial, saving <b>{format_inr(savings)}</b> in total tax liability due to Chapter VI-A deductions.</span>
        </div>
        """
    else:
        callout_html = f"""
        <div class="recommendation-banner" style="background: #f8fafc; border-color: #cbd5e1; color: #334155;">
            <span>⚖️ <strong>Both Regimes Yield Equal Liability:</strong> Total tax is identical under both regimes.</span>
        </div>
        """
    st.markdown(callout_html, unsafe_allow_html=True)

    # Side-by-Side Regime Breakdown
    reg_col1, reg_col2 = st.columns(2)

    with reg_col1:
        st.markdown(f"### **New Tax Regime {'✅ (Optimal)' if diff >= 0 else ''}**")
        with st.container(border=True):
            st.write(f"**Gross Income:** {format_inr(corrected_gross)}")
            st.write(f"**Less:** Standard Deduction: `{format_inr(new_result.get('standard_deduction_applied', 0))}`")
            st.write(f"**Taxable Income:** {format_inr(new_result.get('taxable_income', 0))}")
            st.write(f"**Base Slab Tax:** {format_inr(new_result.get('base_tax', 0))}")
            
            # Rebate callout
            rebate = new_result.get('rebate_87A', 0)
            if rebate > 0:
                st.write(f"**Section 87A Rebate:** <span style='color:#10b981;'>- {format_inr(rebate)}</span>", unsafe_allow_html=True)
                if new_result.get('tax_after_rebate', 0) > 0 and new_result.get('tax_after_rebate', 0) <= 25000:
                    st.info("💡 **Marginal Rebate Active:** Section 87A marginal relief applied. Tax is capped at excess income over ₹12 Lakhs threshold!")
            else:
                st.write(f"**Section 87A Rebate:** ₹ 0.00")
                
            st.write(f"**Tax After Rebate:** {format_inr(new_result.get('tax_after_rebate', 0))}")
            
            # Surcharge callout
            surcharge = new_result.get('surcharge', 0)
            mr_surch = new_result.get('marginal_relief_surcharge', 0)
            if mr_surch > 0:
                st.write(f"**Surcharge:** {format_inr(surcharge)} *(Relief Granted: {format_inr(mr_surch)})*")
            else:
                st.write(f"**Surcharge:** {format_inr(surcharge)}")
                
            st.write(f"**Health & Education Cess (4%):** {format_inr(new_result.get('cess', 0))}")
            st.markdown(f"#### **Total Tax Payable:** <span style='color:#2563eb;'>{format_inr(new_result.get('total_tax', 0))}</span>", unsafe_allow_html=True)

    with reg_col2:
        st.markdown(f"### **Old Tax Regime {'✅ (Optimal)' if diff < 0 else ''}**")
        with st.container(border=True):
            st.write(f"**Gross Income:** {format_inr(corrected_gross)}")
            st.write(f"**Less:** Standard Deduction: `{format_inr(old_result.get('standard_deduction_applied', 0))}`")
            st.write(f"**Less:** Chapter VI-A Deductions: `{format_inr(total_chapter_via)}`")
            st.write(f"**Taxable Income:** {format_inr(old_result.get('taxable_income', 0))}")
            st.write(f"**Base Slab Tax:** {format_inr(old_result.get('base_tax', 0))}")
            st.write(f"**Section 87A Rebate:** {format_inr(old_result.get('rebate_87A', 0))}")
            st.write(f"**Tax After Rebate:** {format_inr(old_result.get('tax_after_rebate', 0))}")
            st.write(f"**Surcharge:** {format_inr(old_result.get('surcharge', 0))}")
            st.write(f"**Health & Education Cess (4%):** {format_inr(old_result.get('cess', 0))}")
            st.markdown(f"#### **Total Tax Payable:** <span style='color:#0f172a;'>{format_inr(old_result.get('total_tax', 0))}</span>", unsafe_allow_html=True)

    # AIS Exposure & Delta Analysis
    st.markdown("---")
    st.markdown("#### **AIS Exposure & CA Remediation Variance**")
    
    delta_tax = new_result["total_tax"] - raw_result["total_tax"]
    d_col1, d_col2, d_col3 = st.columns(3)
    with d_col1:
        st.metric("Raw AIS Tax Liability", format_inr(raw_result["total_tax"]))
    with d_col2:
        st.metric("CA Reconciled Tax Liability", format_inr(new_result["total_tax"]))
    with d_col3:
        if delta_tax < 0:
            st.metric("Client Tax Saved u/s Remediation", format_inr(abs(delta_tax)), delta=f"-{format_inr(abs(delta_tax))}", delta_color="normal")
        elif delta_tax > 0:
            st.metric("Additional Tax Disclosed", format_inr(delta_tax), delta=f"+{format_inr(delta_tax)}", delta_color="inverse")
        else:
            st.metric("Liability Delta", "₹ 0.00", delta="Zero Mismatch")


# ====================================================================
# TAB 3: MULTI-YEAR AUDIT & ITR-U PLANNER
# ====================================================================
with tab_audit:
    st.markdown("#### **Multi-Year Historical Audit & ITR-U Section 140B Calculator**")
    st.markdown(
        "Evaluate tax across previous Assessment Years for Updated Returns (ITR-U) or inspect Section 44AD/ADA digital turnover limits."
    )

    # Multi-Year Comparative Simulation
    st.markdown("##### **1. Multi-Year Tax Engine Comparison (FY 2020-21 to TY 2026)**")
    simulated_gross = corrected_gross
    
    year_rows = []
    for yr in ordered_years:
        try:
            yr_engine = MultiYearDispatcher.resolve(yr)
            yr_new = yr_engine.calculate_tax({"gross_income": simulated_gross, "regime": "new_regime"})
            yr_old = yr_engine.calculate_tax({"gross_income": simulated_gross, "regime": "old_regime"})
            year_rows.append({
                "Financial Year": YEAR_METADATA.get(yr, {}).get("title", yr),
                "AY": YEAR_METADATA.get(yr, {}).get("ay", "N/A"),
                "New Regime Tax": yr_new.get("total_tax", 0.0),
                "Old Regime Tax": yr_old.get("total_tax", 0.0),
                "Std Deduction": yr_new.get("standard_deduction_applied", 0.0),
                "Rebate 87A": yr_new.get("rebate_87A", 0.0)
            })
        except Exception:
            continue
            
    sim_df = pd.DataFrame(year_rows)
    st.dataframe(
        sim_df,
        column_config={
            "New Regime Tax": st.column_config.NumberColumn(format="₹ %.2f"),
            "Old Regime Tax": st.column_config.NumberColumn(format="₹ %.2f"),
            "Std Deduction": st.column_config.NumberColumn(format="₹ %.2f"),
            "Rebate 87A": st.column_config.NumberColumn(format="₹ %.2f"),
        },
        width="stretch",
        hide_index=True
    )

    # ITR-U Penalty & Interest Engine
    st.markdown("---")
    st.markdown("##### **2. Section 140B Additional Tax Calculator (ITR-U Updated Return)**")
    
    u_col1, u_col2, u_col3 = st.columns(3)
    with u_col1:
        ay_selection = st.selectbox("Assessment Year to Update", [2022, 2023, 2024, 2025], index=2)
    with u_col2:
        tax_default = st.number_input("Tax Payable in Updated Return (INR)", min_value=1000.0, value=100000.0, step=10000.0)
    with u_col3:
        filing_date = st.date_input("Anticipated ITR-U Filing Date", value=date.today())

    try:
        due_date = date(ay_selection, 7, 31)
        ie = InterestEngine(due_date_filing=due_date, actual_date_filing=filing_date, assessment_year=ay_selection)
        u_summary = ie.generate_liability_summary(tax=tax_default, tds=0.0, advance_tax=0.0)
        
        pen_col1, pen_col2, pen_col3, pen_col4 = st.columns(4)
        with pen_col1:
            st.metric("Section 234A Interest", format_inr(u_summary.get("234A", 0)))
        with pen_col2:
            st.metric("Section 234B Interest", format_inr(u_summary.get("234B", 0)))
        with pen_col3:
            st.metric("Section 140B Additional Tax", format_inr(u_summary.get("140B_additional_tax", 0)))
        with pen_col4:
            total_itru_payable = tax_default + u_summary.get("total_interest", 0) + u_summary.get("140B_additional_tax", 0)
            st.metric("Total ITR-U Challan Payable", format_inr(total_itru_payable))
            
        st.caption(f"ℹ️ ITR-U Section 140B additional tax is computed on aggregate of tax + interest based on duration from end of AY (March 31, {ay_selection + 1}).")
    except Exception as e:
        st.warning(f"Unable to compute ITR-U penalty: {str(e)}")

    # Presumptive Taxation Section 44AD / 44ADA
    st.markdown("---")
    st.markdown("##### **3. Section 44AD / 44ADA Presumptive Digital Turnover Validator**")
    
    p_col1, p_col2, p_col3 = st.columns(3)
    with p_col1:
        section_type = st.radio("Section Type", ["Section 44AD (Business)", "Section 44ADA (Profession)"])
    with p_col2:
        gross_turnover = st.number_input("Gross Receipts / Turnover (INR)", min_value=0.0, value=25000000.0, step=500000.0)
    with p_col3:
        digital_turnover = st.number_input("Digital / Non-Cash Receipts (INR)", min_value=0.0, value=24000000.0, step=500000.0)

    if "44AD (" in section_type:
        chk_res = PresumptiveTaxChecker.check_44ad_eligibility(gross_turnover, digital_turnover)
    else:
        chk_res = PresumptiveTaxChecker.check_44ada_eligibility(gross_turnover, digital_turnover)

    status_color = "#10b981" if chk_res["status"] == "ELIGIBLE" else "#ef4444"
    st.markdown(
        f"""
        <div style="padding: 1rem; border-radius: 8px; border-left: 5px solid {status_color}; background: #f8fafc; margin-top: 0.5rem;">
            <strong>Status:</strong> <span style="color: {status_color}; font-weight: 700;">{chk_res['status']}</span> | 
            <strong>Threshold Applied:</strong> {chk_res.get('limit_applied', 'N/A')}<br>
            <span style="font-size: 0.9rem; color: #475569;">{chk_res['message']}</span>
        </div>
        """,
        unsafe_allow_html=True
    )


# ====================================================================
# TAB 4: CA WORKPAPER MEMO & EXPORT
# ====================================================================
with tab_memo:
    st.markdown("#### **CA Statutory Reconciliation Memorandum & Workpaper**")
    st.markdown("Generate a formal audit memo documenting AIS reconciliation, statutory adjustments, and tax computations for working paper files.")

    # Memo text generation
    timestamp_str = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
    memo_text = f"""================================================================================
          TRB TAX PRO — CA STATUTORY AUDIT WORKPAPER MEMORANDUM
================================================================================
Date & Time Generated : {timestamp_str}
Client / Assessee Name : {client_name}
Permanent Account No.  : {pan_number}
Taxpayer Status        : {taxpayer_category}
Financial Year         : {YEAR_METADATA.get(selected_year, {}).get('title', selected_year)}
Assessment Year        : {YEAR_METADATA.get(selected_year, {}).get('ay', 'N/A')}
Governing Statute      : {YEAR_METADATA.get(selected_year, {}).get('act', 'Income Tax Act')}
--------------------------------------------------------------------------------

1. AIS RECONCILIATION & ADJUSTMENT TRAIL:
--------------------------------------------------------------------------------
{final_recon_df[['Category', 'AIS Amount', 'CA Adjustment', 'Corrected Amount', 'Notes']].to_string(index=False)}

Total AIS Reported Gross : INR {total_ais:,.2f}
Net CA Adjustments       : INR {total_adj:,.2f}
Final Taxable Aggregate  : INR {total_corrected:,.2f}

--------------------------------------------------------------------------------
2. FINAL TAX LIABILITY BREAKDOWN ({YEAR_METADATA.get(selected_year, {}).get('title', selected_year)}):
--------------------------------------------------------------------------------
Computation Stream           | New Tax Regime          | Old Tax Regime
-----------------------------|-------------------------|------------------------
Gross Total Income           | INR {corrected_gross:>15,.2f} | INR {corrected_gross:>15,.2f}
Standard Deduction           | INR {new_result.get('standard_deduction_applied', 0):>15,.2f} | INR {old_result.get('standard_deduction_applied', 0):>15,.2f}
Chapter VI-A Deductions      | INR {0:>15,.2f} | INR {total_chapter_via:>15,.2f}
Net Taxable Income           | INR {new_result.get('taxable_income', 0):>15,.2f} | INR {old_result.get('taxable_income', 0):>15,.2f}
Base Slab Tax                | INR {new_result.get('base_tax', 0):>15,.2f} | INR {old_result.get('base_tax', 0):>15,.2f}
Section 87A Rebate           | INR {new_result.get('rebate_87A', 0):>15,.2f} | INR {old_result.get('rebate_87A', 0):>15,.2f}
Tax After Rebate             | INR {new_result.get('tax_after_rebate', 0):>15,.2f} | INR {old_result.get('tax_after_rebate', 0):>15,.2f}
Surcharge                    | INR {new_result.get('surcharge', 0):>15,.2f} | INR {old_result.get('surcharge', 0):>15,.2f}
Health & Education Cess (4%) | INR {new_result.get('cess', 0):>15,.2f} | INR {old_result.get('cess', 0):>15,.2f}
-----------------------------|-------------------------|------------------------
TOTAL TAX PAYABLE            | INR {new_result.get('total_tax', 0):>15,.2f} | INR {old_result.get('total_tax', 0):>15,.2f}

Recommended Regime : {recommended} (Savings: INR {savings:,.2f})
Raw AIS Tax Delta  : INR {delta_tax:,.2f}

--------------------------------------------------------------------------------
3. AUDIT CONCLUSION & STATUTORY REMARKS:
All adjustments noted above have been verified against original bank statements, 
TDS certificates (Form 16/16A), and capital gains workpapers. Prepared for 
statutory filing defense under Section 143(1) and Section 148A.
================================================================================
"""

    st.text_area("Audit Memo Preview", value=memo_text, height=350)

    # Export Buttons
    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        st.download_button(
            label="📥 Download CA Audit Memo (.txt)",
            data=memo_text,
            file_name=f"CA_Tax_Memo_{pan_number}_{selected_year}.txt",
            mime="text/plain"
        )
    with col_exp2:
        csv_data = final_recon_df.to_csv(index=False)
        st.download_button(
            label="📊 Download Reconciled Schedule (.csv)",
            data=csv_data,
            file_name=f"AIS_Reconciliation_{pan_number}_{selected_year}.csv",
            mime="text/csv"
        )
