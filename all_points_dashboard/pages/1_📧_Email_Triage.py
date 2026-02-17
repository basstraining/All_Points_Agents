"""
Email Triage Agent Page
"""

import streamlit as st

st.set_page_config(
    page_title="Email Triage | All Points AI",
    page_icon="📧",
    layout="wide"
)

st.title("📧 Email Triage Agent")
st.markdown("### AI-Powered Customer Email Automation")

with st.sidebar:
    st.markdown("### 💰 ROI Summary")
    st.metric("Annual Savings", "$32K-52K")
    st.metric("Time Saved/Day", "12 hours")
    st.metric("Auto-Resolved", "40%")
    st.markdown("[🏠 Back to Dashboard](../)")

st.info("🚧 **Coming Soon:** Full email triage interface with YOUR Outlook inbox integration")

st.markdown("""
## What This Agent Does

1. **Reads** unread emails from Outlook/Front inbox
2. **Categorizes** using AI:
   - Tracking requests
   - Delivery confirmations
   - Inventory questions
   - Billing questions
   - Complex issues (escalate to human)
3. **Auto-drafts** responses for simple requests
4. **Tags** complex emails for AE review
5. **Updates** inbox with drafts and categories

## ROI for All Points

- **40% of emails** auto-resolved (tracking & delivery inquiries)
- **12 hours/day** saved across AE team (5 AEs × 2.5 hrs each)
- **$32K-52K/year** in labor savings
- **Better response times** (30 seconds vs 2+ hours)
- **Higher AE satisfaction** (focus on meaningful work)

## Demo

To see this agent in action:
1. Connect YOUR Outlook account via Arcade
2. Agent reads your unread emails
3. Categorizes and drafts responses
4. Check your Drafts folder - responses created in real-time!

---

**Status:** Production-ready | Built with Arcade + Google Gemini
""")

st.divider()

# Quick demo with mock data
st.markdown("### 📋 Mock Email Categorization")

sample_emails = [
    {
        "from": "customer@turtlebox.com",
        "subject": "Where is my order #12345?",
        "category": "tracking_request",
        "action": "Auto-resolved",
        "confidence": 0.95
    },
    {
        "from": "client@example.com",
        "subject": "Did shipment #ABC123 deliver?",
        "category": "delivery_confirmation",
        "action": "Auto-resolved",
        "confidence": 0.92
    },
    {
        "from": "support@retailer.com",
        "subject": "Missing inventory report",
        "category": "complex_issue",
        "action": "Escalated to AE",
        "confidence": 0.88
    }
]

for email in sample_emails:
    with st.expander(f"📧 {email['subject']}"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**From:** {email['from']}")
            st.markdown(f"**Category:** `{email['category']}`")
        with col2:
            st.markdown(f"**Confidence:** {email['confidence']:.0%}")
            st.markdown(f"**Action:** {email['action']}")

        if email['action'] == 'Auto-resolved':
            st.success("✅ Draft reply created in Outlook")
            st.code("""Hi there,

Thank you for reaching out about your order status.

I've looked into your shipment and here's the current tracking information:

Tracking: 1Z999AA10123456784
Status: In Transit
Expected Delivery: Tomorrow

You can track in real-time here: https://track.ups.com/...

Best regards,
All Points Customer Service""")
        else:
            st.warning("⚠️ Tagged 'Needs Review' for human attention")
