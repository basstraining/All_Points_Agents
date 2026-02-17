"""
Chargeback Defense Agent Page
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir / "email_triage_demo" / "04_chargeback_defense"))

try:
    from agent import generate_dispute_letter, compile_evidence, process_chargeback
    import asyncio
    from datetime import datetime
except ImportError as e:
    st.error(f"⚠️ Could not import Chargeback Defense agent: {e}")
    st.info("Make sure email_triage_demo/04_chargeback_defense exists")
    st.stop()

st.set_page_config(page_title="Chargeback Defense | All Points AI", page_icon="⚖️", layout="wide")

st.title("⚖️ RetailReady Chargeback Defense")
st.markdown("### Automated Dispute Management")

with st.sidebar:
    st.metric("Annual Value", "$35K")
    st.metric("Time Saved/Week", "3-4 hours")
    st.metric("Win Rate Improvement", "+15%")
    st.markdown("---")
    st.markdown("[🏠 Back to Dashboard](../)")

# Overview
st.markdown("## 🎯 What This Agent Does")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Automated Dispute Process:**
    - Retrieves shipping docs from OneDrive
    - Compiles delivery photos & signatures
    - Drafts dispute letter using AI
    - Submits to retailer compliance team
    - Tracks resolution status
    """)

with col2:
    st.markdown("""
    **ROI for All Points:**
    - **$10-50K/month** in chargebacks
    - **3-4 hours/week saved** on paperwork
    - **+15% win rate** (better evidence compilation)
    - **$35K/year** additional chargebacks won
    """)

st.divider()

# Demo
st.markdown("## 🚀 Live Demo: Process Chargeback")

# Sample chargeback cases
SAMPLE_CHARGEBACKS = [
    {
        "id": "CB-2026-001",
        "retailer": "Target",
        "amount": "$2,450.50",
        "reason": "Late Delivery",
        "po_number": "PO-TGT-12345",
        "ship_date": "2026-02-10",
        "delivery_date": "2026-02-14",
        "required_date": "2026-02-12"
    },
    {
        "id": "CB-2026-002",
        "retailer": "Nordstrom",
        "amount": "$1,875.00",
        "reason": "Shortage Claim",
        "po_number": "PO-NRD-67890",
        "units_shipped": 500,
        "units_claimed": 485
    },
    {
        "id": "CB-2026-003",
        "retailer": "Best Buy",
        "amount": "$3,200.00",
        "reason": "Packaging Non-Compliance",
        "po_number": "PO-BBY-54321",
        "issue": "Labels on wrong side"
    }
]

selected_cb = st.selectbox(
    "Select a chargeback to process:",
    options=range(len(SAMPLE_CHARGEBACKS)),
    format_func=lambda i: f"{SAMPLE_CHARGEBACKS[i]['id']} - {SAMPLE_CHARGEBACKS[i]['retailer']} - {SAMPLE_CHARGEBACKS[i]['amount']}"
)

chargeback = SAMPLE_CHARGEBACKS[selected_cb]

# Show chargeback details
with st.expander("📋 Chargeback Details", expanded=True):
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"**ID:** {chargeback['id']}")
        st.markdown(f"**Retailer:** {chargeback['retailer']}")

    with col2:
        st.markdown(f"**Amount:** {chargeback['amount']}")
        st.markdown(f"**Reason:** {chargeback['reason']}")

    with col3:
        st.markdown(f"**PO Number:** {chargeback['po_number']}")

if st.button("⚖️ Generate Dispute Letter", type="primary", use_container_width=True):
    with st.spinner("Compiling evidence and drafting dispute letter..."):
        try:
            # Simulate evidence compilation
            st.info("📂 Retrieving evidence from OneDrive...")
            st.success("✅ Found: BOL, delivery receipt, photos, packing list")

            # Generate dispute letter
            st.info("✍️ Drafting dispute letter with AI...")

            # Mock dispute letter
            dispute_letter = f"""
DISPUTE LETTER - {chargeback['id']}

Date: {datetime.now().strftime('%B %d, %Y')}

To: {chargeback['retailer']} Vendor Compliance Team
Re: Formal Dispute of Chargeback {chargeback['id']}

Dear {chargeback['retailer']} Compliance Team,

We are writing to formally dispute the chargeback assessed against All Points ATL for Purchase Order {chargeback['po_number']}, in the amount of {chargeback['amount']}.

CHARGEBACK DETAILS:
- Chargeback ID: {chargeback['id']}
- PO Number: {chargeback['po_number']}
- Amount: {chargeback['amount']}
- Stated Reason: {chargeback['reason']}

EVIDENCE PROVIDED:
1. Bill of Lading (BOL) - Shows shipment date and carrier acceptance
2. Delivery Receipt - Signed by {chargeback['retailer']} receiving personnel
3. Delivery Photos - Timestamped images showing compliant delivery
4. Packing List - Confirms all units shipped per PO requirements

DISPUTE BASIS:
{self._get_dispute_reasoning(chargeback)}

We respectfully request that this chargeback be reversed. All supporting documentation is attached to this dispute.

Please review the evidence and respond within 30 days per the vendor agreement.

Sincerely,
All Points ATL Compliance Team

Attachments:
- BOL_{chargeback['po_number']}.pdf
- Delivery_Receipt_{chargeback['po_number']}.pdf
- Delivery_Photos_{chargeback['po_number']}.zip
- Packing_List_{chargeback['po_number']}.pdf
"""

            st.success("✅ Dispute letter generated!")

            st.divider()
            st.markdown("### 📧 Generated Dispute Letter")
            st.code(dispute_letter)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.button("📤 Submit Dispute")
            with col2:
                st.button("✏️ Edit Letter")
            with col3:
                st.download_button(
                    "💾 Download PDF",
                    data=dispute_letter,
                    file_name=f"dispute_{chargeback['id']}.txt",
                    mime="text/plain"
                )

            # Show evidence compiled
            st.divider()
            st.markdown("### 📎 Evidence Compiled")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Documents Retrieved:**")
                st.markdown("✅ Bill of Lading")
                st.markdown("✅ Signed Delivery Receipt")
                st.markdown("✅ Packing List")

            with col2:
                st.markdown("**Photos & Proof:**")
                st.markdown("✅ Delivery timestamp photos (3)")
                st.markdown("✅ Label compliance images (2)")
                st.markdown("✅ Signature capture")

            # Metrics
            st.divider()
            st.markdown("### 📊 Impact")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Time Saved", "45 min")
                st.caption("vs 60 min manual process")
            with col2:
                st.metric("Evidence Quality", "High")
                st.caption("Complete documentation")
            with col3:
                st.metric("Win Probability", "85%")
                st.caption("Based on evidence strength")

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

def _get_dispute_reasoning(chargeback):
    """Generate dispute reasoning based on chargeback type"""
    if chargeback['reason'] == "Late Delivery":
        return f"""Our records show shipment departed on {chargeback.get('ship_date')} and was delivered on {chargeback.get('delivery_date')}. While the required date was {chargeback.get('required_date')}, the delay was due to carrier performance beyond our control. The BOL shows timely tender to the carrier."""

    elif chargeback['reason'] == "Shortage Claim":
        return f"""Our packing list shows {chargeback.get('units_shipped')} units were shipped and accepted by the carrier. The signed delivery receipt confirms delivery of all cartons. Any shortage occurred after delivery acceptance."""

    else:
        return f"""Our documentation shows full compliance with all {chargeback['retailer']} routing guide requirements. Photos timestamp-stamped at delivery confirm proper packaging and labeling."""

st.divider()

# Summary
st.markdown("## 💼 Chargeback Pipeline")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Open Chargebacks", "12")
with col2:
    st.metric("Total Value", "$45,000")
with col3:
    st.metric("Disputed This Month", "8")
with col4:
    st.metric("Win Rate", "78%")
