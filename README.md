# TRB Tax Pro

A CA-grade Income Tax calculation engine for India (FY 2020-21 to FY 2026-27) with AIS reconciliation and support for the Income Tax Act, 2025.

Built for precision, notice remediation, ITR-U compliance, and multi-year tax planning.

## 💡 Simple Guide: How this helps you

Most tax software is built for filing, but **TRB Tax Pro** is built for **accuracy and safety**. Here is how it simplifies taxes for the masses:

1. **No More "Tax Cliffs":** Under the New Tax Regime, earning just ₹1 over ₹12 Lakhs used to result in a massive tax jump. Our engine automatically applies "Marginal Relief," ensuring you only pay tax on the actual extra income you earned, saving you thousands in unnecessary taxes.
2. **Historical Fixes (ITR-U):** If you missed a deduction or made a mistake in the last 3 years, our modular engines (FY 2020-21 onwards) help you calculate the exact "Updated Return" tax without needing to be a tax expert.
3. **Automatic Data Checking:** Instead of typing in numbers from your bank statements, the engine can "read" your official AIS (Annual Information Statement) data to ensure your return matches what the Government already knows about you, preventing those scary tax notices.
4. **Small Business Friendly:** If you are a freelancer or small shop owner (under Section 44AD/ADA), the engine automatically checks if you qualify for higher turnover limits based on your digital receipts, making sure you don't pay for an expensive audit if you don't need one.

---

## Features

- **Multi-Year Support (NEW):** Modular engines for **FY 2020-21 through FY 2024-25** added for historical audits, ITR-U filings, and notice resolution.
- **Section 87A Marginal Rebate:** Precise resolution for the "Cliffs" under the New Regime (specifically mapping the ₹12 Lakh threshold gracefully for FY 2025-26).
- **Marginal Relief (Surcharges):** Mathematically rigorous computation across multiple thresholds (₹50L, ₹1Cr, ₹2Cr, and ₹5Cr).
- **Presumptive Taxation Validation (44AD/44ADA):** Dynamic tests against digital transaction limits to unlock enhanced turnover rules (e.g., 5% Cash rules mapping to ₹3Cr limits).
- **Automated AIS Reconciliation:** Pull SFT entries, Salary, and Capital Gains directly from official JSON specs reducing manual mapping and notice exposure.

## Installation 

Install the latest version directly from PyPI:

```bash
pip install trb-tax-pro --upgrade
```

## Programmatic Usage

Access specific year engines via the `MultiYearDispatcher`:

```python
from trb_tax_pro.engine.dispatcher import MultiYearDispatcher

# Get the engine for a specific Financial Year
engine = MultiYearDispatcher.resolve("fy2025_26")

# Calculate tax
result = engine.calculate_tax({
    "gross_income": 1280000,
    "regime": "new_regime"
})

print(f"Tax Payable: ₹{result['total_tax']}")
```

## Dashboard Interface

Launch the professional CA wrapper interface featuring unified Tax Computation and AIS Data Bridging:

```bash
streamlit run ui.py
```

### Support the Project

If this engine simplifies your compliance workflows or saves your practice from potential 143(1) mismatch notices, please consider supporting the project:
**☕ [Buy Me a Coffee](https://buymeacoffee.com/tbhavar)**
