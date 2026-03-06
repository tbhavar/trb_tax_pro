# TRB Tax Pro - CA User Manual

Welcome to the definitive backend utility for Chartered Accountants handling the Income Tax Act, 2025 structures natively. This manual covers exactly how the architectural layers govern compliance and data-reconciliation dynamically against Income Tax rules.

## The AIS Reconciliation Dashboard

The most powerful element of `trb_tax_pro` is its zero-touch parsing of JSON files downloaded from the Income Tax portal via the **AIS Intelligence Module**.

#### Workflow
1. Download the raw `.json` file from the e-filing portal's AIS service.
2. Put the `mock_ais.json` payload (temporarily for this build) into the application layer.
3. Open the Streamlit interface using `streamlit run ui.py`.
4. Review the auto-generated **Editable Recognition Matrix**.
5. Provide **CA Adjustments**: Sometimes banks double-report SFT-016 interest nodes, or brokerages double-log Mutual Fund liquidations. Provide a negative or positive integer adjustment alongside the reasoning underneath "Notes / Justification".

The Engine calculates the RAW penalty from the Department vs. the NEW CORRECTED computational layout instantly displaying your specific "Tax Saved" vector dynamically mapping the exact difference down to the rupee.

## Handling the 'Cliffs'

Traditional computation rules fail abruptly around two unique "tax cliffs" in India. `trb_tax_pro` resolves them via precision algebraic engines automatically.

### Section 87A Marginal Rebate (The ₹12L Limit)

Under the upcoming 2026 guidelines, a rebate is available up to ₹12,00,000. 
*Previous Issue:* If an assessee earned ₹12,05,000, they traditionally lost the entire ₹60,000 rebate, suddenly facing a massive unproportional tax burden simply for earning slightly over the limit.
*Solution:* `trb_tax_pro` intelligently evaluates this cliff. If the calculated tax exceeds the surplus earned above the threshold, the tax liability is strictly restricted mathematically! Making ₹12,05,000 means your final exact tax mapping is `₹5,000`.

### Surcharge Marginal Relief

Surcharges mathematically scale across brackets like ₹50L (10%), ₹1Cr (15%), etc.
*Previous Issue:* Crossing into the 10% tier (e.g. at ₹50,05,000) generated a sudden ~₹1,20,000 tax hike wiping out the actual incremental profit earned.
*Solution:* The `MarginalReliefCalculator` computes the total baseline tax at the threshold maximum (exactly ₹50L) + the literal excess income above the threshold. If the raw surcharge violates this limit, the system gracefully pulls the surcharge down, providing specific "Marginal Relief", enforcing fair taxation inherently across all computational cycles!
