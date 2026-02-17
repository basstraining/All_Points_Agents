"""
LTL Freight Automation Agent Page
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir / "05_ltl_automation"))

try:
    # Import the existing LTL automation streamlit app
    import asyncio
    from agent import process_quote_request
    from datetime import datetime
    import json
except ImportError:
    st.error("Could not import LTL automation agent. Make sure 05_ltl_automation is in the parent directory.")
    st.stop()

st.set_page_config(
    page_title="LTL Automation | All Points AI",
    page_icon="🚛",
    layout="wide"
)

# Header
st.title("🚛 LTL Freight Quote Automation")
st.markdown("### AI-Powered Multi-Carrier Rate Shopping")

# Sidebar ROI
with st.sidebar:
    st.markdown("### 💰 ROI Summary")
    st.metric("Annual Savings", "$51,440")
    st.metric("Time Saved/Quote", "17.8 min")
    st.metric("Margin Improvement", "5%")

    st.markdown("---")

    st.markdown("### ℹ️ How It Works")
    st.markdown("""
    1. 🔍 Queries 5-7 LTL carriers
    2. 💰 Compares rates instantly
    3. ⭐ Recommends best value
    4. ✍️ AI-drafts quote email
    5. 📧 Sends to customer
    """)

    st.markdown("[🏠 Back to Dashboard](../)")

# Main Content
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📋 Quote Request Details")

    customer_name = st.text_input("Customer Name", value="TurtleBox Audio")
    customer_email = st.text_input("Customer Email", value="logistics@turtlebox.com")

    col_a, col_b = st.columns(2)
    with col_a:
        origin_zip = st.text_input("Origin ZIP", value="30318")
    with col_b:
        destination_zip = st.text_input("Destination ZIP", value="60601")

    col_c, col_d, col_e = st.columns(3)
    with col_c:
        weight_lbs = st.number_input("Weight (lbs)", value=2400, min_value=150, step=100)
    with col_d:
        freight_class = st.selectbox(
            "Freight Class",
            options=["50", "55", "60", "65", "70", "77.5", "85", "92.5", "100", "110", "125", "150"],
            index=6
        )
    with col_e:
        pieces = st.number_input("Pieces", value=2, min_value=1, max_value=50)

with col2:
    st.markdown("### ℹ️ About This Demo")
    st.info("""
    **What this agent does:**

    1. 🔍 Requests quotes from 5+ LTL carriers
    2. 💰 Compares rates and transit times
    3. ⭐ Recommends best value option
    4. ✍️ Drafts email to customer
    5. 📊 Tracks savings metrics

    **Built for All Points ATL:**
    - Saves 15-20 minutes per quote
    - 3-5 quotes per day → 1-2 hours saved
    - Better carrier rates → improved margins
    - Annual value: $51K+ in combined savings
    """)

st.divider()

# Run quote button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    run_button = st.button("🚀 Get Freight Quotes", type="primary", use_container_width=True)

st.divider()

# Results
if run_button:
    with st.spinner("🚛 Getting quotes from carriers..."):
        try:
            result = asyncio.run(process_quote_request(
                customer_name=customer_name,
                origin_zip=origin_zip,
                destination_zip=destination_zip,
                weight_lbs=weight_lbs,
                freight_class=freight_class,
                pieces=pieces,
                email_address=customer_email,
                save_results=False
            ))

            if not result.get("success"):
                st.error(f"❌ Error: {result.get('error', 'Unknown error')}")
                st.stop()

            st.success("✅ Quotes Retrieved Successfully!")

            # Metrics
            st.markdown("### 📊 Results Summary")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Quotes Received", result['quotes_count'])
            with col2:
                st.metric("Time Saved", f"{result['metrics']['time_saved_minutes']:.1f} min")
            with col3:
                st.metric("Cost Saved", f"${result['metrics']['cost_saved_dollars']:.2f}")
            with col4:
                st.metric("Best Rate", f"${result['recommendation']['total_cost']:.2f}")

            st.divider()

            # Quotes comparison
            st.markdown("### 💰 Carrier Quotes Comparison")

            quotes = result['quotes']
            best_quote = result['recommendation']

            for i, quote in enumerate(quotes[:5]):
                is_best = quote['quote_id'] == best_quote['quote_id']

                if is_best:
                    st.success(f"⭐ **{quote['carrier']}** (RECOMMENDED)")
                else:
                    st.markdown(f"### {i+1}. {quote['carrier']}")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.markdown(f"**Total Cost**")
                    st.markdown(f"# ${quote['total_cost']:.2f}")

                with col2:
                    st.markdown(f"**Transit Time**")
                    st.markdown(f"# {quote['transit_days']} days")

                with col3:
                    st.markdown(f"**Delivery Date**")
                    st.markdown(f"{quote['estimated_delivery']}")

                with col4:
                    st.markdown(f"**Base Rate**")
                    st.markdown(f"${quote['base_rate']:.2f}")
                    st.markdown(f"Fuel: ${quote['fuel_surcharge']:.2f}")

                if is_best:
                    st.info(result['comparison']['comparison'])

                st.divider()

            # Email draft
            st.markdown("### 📧 Customer Quote Email (Auto-Generated)")

            with st.container():
                st.markdown(f"""
                **To:** {customer_email}
                **Subject:** Freight Quote - {origin_zip} to {destination_zip} ({weight_lbs} lbs)
                **From:** logistics@allpointsatl.com
                """)

                st.divider()

                st.markdown(result['email_draft'])

                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    if st.button("📤 Send Email (Demo)", type="primary", use_container_width=True):
                        st.success("✅ Email sent to customer! (Demo mode - not actually sent)")

            st.divider()

            # Next steps
            st.info("""
            ### 🎯 Next Steps

            1. **Review quote** with customer via email
            2. **Book shipment** when customer approves
            3. **Track progress** and send updates automatically
            4. **Measure savings** across all LTL shipments

            **With All Points' MyCarrier API connected:**
            - Real-time carrier rates
            - Instant booking capability
            - Automated tracking updates
            - Historical rate analytics
            """)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.exception(e)
