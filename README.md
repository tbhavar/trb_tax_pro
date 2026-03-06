# TRB Tax Pro

A CA-grade Income Tax calculation engine for India (FY 2025-26) with AIS reconciliation and support for the Income Tax Act, 2025.

Built for precision, notice remediation, ITR-U compliance, and the 2026 Assessment transitions.

## Features

- **Marginal Relief (Surcharges):** Mathematically rigorous computation across multiple thresholds (₹50L, ₹1Cr, ₹2Cr, and ₹5Cr).
- **Section 87A Marginal Rebate:** Precise resolution for the "Cliffs" under the New Regime (specifically mapping the ₹12 Lakh threshold gracefully).
- **Multi-Year Support:** Readily deploy algorithms for classical FY terminology or incoming Tax Year (TY) structures. 
- **Presumptive Taxation Validation (44AD/44ADA):** Dynamic tests against digital transaction limits to unlock enhanced turnover rules (e.g. 5% Cash rules mapping to ₹3Cr limits).
- **Automated AIS Reconciliation:** Pull SFT entries, Salary, and Capital Gains directly from official JSON specs reducing manual mapping and notice exposure.

## Installation 

Currently optimized via `pyproject.toml` and standard `pip` execution:

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/trb_tax_pro.git
   cd trb_tax_pro
   ```
2. **Install Locally:**
   ```bash
   pip install -e .
   ```

## Usage: AIS Core Dashboard

To launch the professional CA wrapper interface featuring the unified Tax Computation and AIS Data Bridging:

```bash
streamlit run ui.py
```

### Support the Project

If this engine simplifies your compliance workflows or saves your practice from potential 143(1) mismatch notices, please consider supporting the project:
**☕ [Buy Me a Coffee](https://buymeacoffee.com/tbhavar)**
