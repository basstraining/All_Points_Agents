"""
Carrier Exception Monitor Page
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir / "email_triage_demo" / "01_carrier_exception_monitor"))

try:
    from carrier_mcp import get_shipments_with_exceptions, MOCK_SHIPMENTS
    from agent import monitor_shipments, generate_exception_email
    import asyncio
    from datetime import datetime
except ImportError as e:
    st.error(f"⚠️ Could not import Carrier Monitor agent: {e}")
    st.info("Make sure email_triage_demo/01_carrier_exception_monitor exists")
    st.stop()

st.set_page_config(page_title="Carrier Monitor | All Points AI", page_icon="📦", layout="wide")

st.title("📦 Carrier Exception Monitor")
st.markdown("### Proactive Shipping Delay Detection")

with st.sidebar:
    st.metric("Annual Savings", "$40K-60K")
    st.metric("Time Saved/Day", "12.5 hours")
    st.metric("Shipments Monitored", "1000+/day")
    st.markdown("---")
    st.markdown("[🏠 Back to Dashboard](../)")

# Overview
st.markdown("## 🎯 What This Agent Does")
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Automated Exception Detection:**
    - Monitors all active shipments 24/7
    - Detects delays, stuck shipments, delivery failures
    - AI categorizes exception severity
    - Auto-drafts customer notification emails
    """)

with col2:
    st.markdown("""
    **ROI for All Points:**
    - **12.5 hours/day saved** across AE team
    - **$40K-60K/year** in labor savings
    - Proactive customer service (not reactive)
    - Better customer satisfaction
    """)

st.divider()

# Demo
st.markdown("## 🚀 Live Demo: Monitor Shipments")

if st.button("🔍 Scan All Shipments for Exceptions", type="primary", use_container_width=True):
    with st.spinner("Monitoring shipments..."):

        class MockContext:
            def get_auth_token_or_empty(self):
                return ""

        context = MockContext()

        try:
            # Get shipments with exceptions
            result = asyncio.run(get_shipments_with_exceptions(context))

            if result:
                st.success(f"✅ Found {len(result)} shipments with exceptions")

                # Show exceptions
                for shipment in result:
                    with st.expander(f"📦 {shipment['tracking_number']} - {shipment['exception_type']}"):
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.markdown(f"**Customer:** {shipment['customer']}")
                            st.markdown(f"**Status:** {shipment['status']}")

                        with col2:
                            st.markdown(f"**Expected:** {shipment['expected_delivery']}")
                            st.markdown(f"**Current Location:** {shipment['current_location']}")

                        with col3:
                            severity_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                            st.markdown(f"**Severity:** {severity_color.get(shipment.get('severity', 'medium'), '🟡')} {shipment.get('severity', 'medium').upper()}")

                        # Generate email
                        st.markdown("---")
                        st.markdown("**📧 Auto-Generated Customer Email:**")

                        try:
                            email = asyncio.run(generate_exception_email(
                                customer_name=shipment['customer'],
                                tracking_number=shipment['tracking_number'],
                                exception_type=shipment['exception_type'],
                                current_status=shipment['status'],
                                expected_delivery=shipment['expected_delivery'],
                                current_location=shipment['current_location']
                            ))

                            st.code(email[0] if isinstance(email, tuple) else email)

                            col1, col2 = st.columns(2)
                            with col1:
                                st.button(f"✅ Approve & Send", key=f"approve_{shipment['tracking_number']}")
                            with col2:
                                st.button(f"✏️ Edit", key=f"edit_{shipment['tracking_number']}")

                        except Exception as e:
                            st.error(f"Error generating email: {e}")

                # Summary metrics
                st.divider()
                st.markdown("### 📊 Summary")

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Exceptions", len(result))
                with col2:
                    high_priority = len([s for s in result if s.get('severity') == 'high'])
                    st.metric("High Priority", high_priority)
                with col3:
                    st.metric("Emails Drafted", len(result))
                with col4:
                    st.metric("Time Saved", f"{len(result) * 15} min")

            else:
                st.success("✅ No exceptions found! All shipments on track.")

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.exception(e)

st.divider()

# Show sample shipments
st.markdown("## 📦 Sample Shipments Being Monitored")

for i, shipment in enumerate(MOCK_SHIPMENTS[:5]):
    status_emoji = "⚠️" if shipment.get('has_exception') else "✅"
    st.markdown(f"{status_emoji} `{shipment['tracking_number']}` - {shipment['customer']} - {shipment['status']}")
