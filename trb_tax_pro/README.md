# trb_tax_pro

**CA-Verified Architecture for Indian Income Tax & ITR-U compliance.**

This library evaluates individual taxes strictly based on the Income Tax Act rules (with configurations handling both legacy FY checks and prospective Finance Bill provisions like FY 2026-27). 

## Core Modules

### 1. Multi-Year Tax Engine
A Strategy pattern based Multi-Year dispatcher allows seamless processing of historical Data for Notices & Updated Returns natively.

### 2. Marginal Relief Validator
An exact mathematical surcharge validation module built for limits like ₹50L, ₹1Cr, ₹2Cr, and ₹5Cr. Prevents anomalous jumps in taxation near brackets strictly according to Section 87A and Surcharge bounds.

### 3. Pydantic Immutable Models
Enforces data integrity natively:
- **CapitalGains**: Set-off logic explicitly restricted (e.g. STCL vs LTCG precedence logic mathematically gated).
- **Deductions**: Captured statically prior to evaluating the CA-Compliance layer.

### 4. CA Compliance Validator
A rule engine that acts as a gatekeeper:
- Audits declarations exceeding limits (e.g., Capping 80C to ₹1.5L systematically).
- Presumptive Taxation (44AD / 44ADA) 5% Cash Receipts limitation rule checks to securely utilize maximum thresholds (₹3Cr / ₹75L).

### 5. ITR-U & Default Engine (Sections 234/140B)
Handles 'Tax Representation' elements not found in standard calculators.
- Generates 234A and 234B Interest Penalties algorithmically.
- Includes granular tracking of **Section 140B Penalties** for Updated Returns extending from 25% (under 12 months) up to 70% for severe delays (up to 48 months as outlined dynamically).

---
*Built for Tax Representation Professionals.*
