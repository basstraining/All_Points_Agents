"""
Rate Shopping Optimizer Page
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir / "email_triage_demo" / "03_rate_shopping"))

try:
    from shipstation_mcp import get_rate_comparison, MOCK_ORDERS
    from agent import process_order, optimize_shipping_rates
    import asyncio
except ImportError as e:
    st.error(f"⚠️ Could not import Rate Shopping agent: {e}")
    st.info("Make sure email_triage_demo/03_rate_shopping exists")
    st.stop()

st.set_page_config(page_title="Rate Shopping | All Points AI", page_icon="💰", layout="wide")

st.title("💰 ShipStation Rate Shopping Optimizer")
st.markdown("### Automatic Carrier Selection for Maximum Savings")

with st.sidebar:
    st.metric("Annual Savings", "$130K")
    st.metric("Per Shipment", "$12-15")
    st.metric("Savings Rate", "100%")
    st.markdown("---")
    st.markdown("[🏠 Back to Dashboard](../)")

# Overview
st.markdown("## 🎯 What This Agent Does")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Automated Rate Comparison:**
    - Compares 2 UPS accounts + FedEx + USPS
    - Selects cheapest option automatically
    - Generates shipping label
    - Tracks savings per shipment
    """)

with col2:
    st.markdown("""
    **ROI for All Points:**
    - **$12-15 saved** per shipment
    - **6,000 shipments/year** = $70K-90K saved
    - **$40K labor savings** (2.5 min/order)
    - **Total: $130K/year**
    """)

st.divider()

# Demo
st.markdown("## 🚀 Live Demo: Rate Comparison")

st.markdown("### 📦 Enter Shipment Details")

col1, col2, col3 = st.columns(3)

with col1:
    weight_lbs = st.number_input("Weight (lbs)", value=5.0, min_value=0.1, step=0.5)
    length = st.number_input("Length (in)", value=12, min_value=1, step=1)

with col2:
    width = st.number_input("Width (in)", value=10, min_value=1, step=1)
    height = st.number_input("Height (in)", value=8, min_value=1, step=1)

with col3:
    origin_zip = st.text_input("Origin ZIP", value="30318")
    dest_zip = st.text_input("Destination ZIP", value="10001")

if st.button("💰 Compare Rates Across All Carriers", type="primary", use_container_width=True):
    with st.spinner("Getting rates from carriers..."):
        try:
            class MockContext:
                def get_auth_token_or_empty(self):
                    return ""

            context = MockContext()

            # Get rate comparison
            result = asyncio.run(get_rate_comparison(
                context,
                origin_zip=origin_zip,
                destination_zip=dest_zip,
                weight_lbs=weight_lbs,
                dimensions={"length": length, "width": width, "height": height}
            ))

            st.success("✅ Rates Retrieved Successfully!")

            # Show comparison
            st.markdown("### 💰 Rate Comparison")

            cheapest = result['cheapest_rate']
            most_expensive = result['most_expensive_rate']
            savings = most_expensive['total_cost'] - cheapest['total_cost']

            # Highlight savings
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Cheapest Option", f"${cheapest['total_cost']:.2f}",
                         delta=f"-${savings:.2f} vs highest")
            with col2:
                st.metric("Most Expensive", f"${most_expensive['total_cost']:.2f}")
            with col3:
                savings_pct = (savings / most_expensive['total_cost']) * 100
                st.metric("Savings", f"${savings:.2f}", delta=f"{savings_pct:.1f}%")

            st.divider()

            # Show all rates
            for rate in result['all_rates']:
                is_cheapest = rate == cheapest

                if is_cheapest:
                    st.success(f"⭐ **{rate['carrier']} - {rate['service_level']}** (RECOMMENDED)")
                else:
                    st.markdown(f"### {rate['carrier']} - {rate['service_level']}")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.markdown("**Total Cost**")
                    st.markdown(f"## ${rate['total_cost']:.2f}")

                with col2:
                    st.markdown("**Transit Time**")
                    st.markdown(f"## {rate['transit_days']} days")

                with col3:
                    st.markdown("**Delivery By**")
                    st.markdown(f"{rate['estimated_delivery']}")

                with col4:
                    if is_cheapest:
                        st.markdown("**Savings**")
                        st.markdown(f"## ${savings:.2f}")

                st.divider()

            # Summary
            st.info(f"""
            ### ✅ Recommended Action

            **Select:** {cheapest['carrier']} - {cheapest['service_level']}
            **Cost:** ${cheapest['total_cost']:.2f}
            **Savings:** ${savings:.2f} ({savings_pct:.1f}% cheaper than {most_expensive['carrier']})

            With this rate selection, you save **${savings:.2f}** on this single shipment.
            Over 6,000 annual shipments with similar savings = **$70K-90K/year**.
            """)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.exception(e)

st.divider()

# Sample orders
st.markdown("## 📦 Recent Orders (Mock Data)")

for order in MOCK_ORDERS[:5]:
    with st.expander(f"Order #{order['order_number']} - {order['customer_name']}"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Weight:** {order['weight_lbs']} lbs")
            st.markdown(f"**Destination:** {order['destination_zip']}")
        with col2:
            st.markdown(f"**Current Rate:** ${order.get('current_rate', 12.50):.2f}")
            st.markdown(f"**Potential Savings:** ${order.get('potential_savings', 3.50):.2f}")
