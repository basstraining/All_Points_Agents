"""
Profitability Analyzer Page
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd

# Add parent directory to path
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir / "email_triage_demo" / "02_takt_profitability"))

try:
    from mcp_servers.takt_server import TaktLMSClient
    from mcp_servers.quickbooks_server import QuickBooksClient
except ImportError as e:
    st.error(f"⚠️ Could not import Profitability Analyzer agent: {e}")
    st.info("Make sure email_triage_demo/02_takt_profitability exists")
    st.stop()

st.set_page_config(page_title="Profitability Analyzer | All Points AI", page_icon="📊", layout="wide")

st.title("📊 Takt Profitability Analyzer")
st.markdown("### Which Clients Are Profitable?")

with st.sidebar:
    st.metric("Annual Value", "$60K+")
    st.metric("Time Saved/Week", "8-10 hours")
    st.metric("Strategic Impact", "High")
    st.markdown("---")
    st.markdown("[🏠 Back to Dashboard](../)")

# Overview
st.markdown("## 🎯 What This Agent Does")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Automated Profitability Analysis:**
    - Combines Takt LMS labor data with QuickBooks revenue
    - Calculates profit margin per client
    - Identifies profitable vs. losing clients
    - AI-generated insights and recommendations
    """)

with col2:
    st.markdown("""
    **ROI for All Points:**
    - **8-10 hours/week saved** on manual analysis
    - **$60K/year value** in better client decisions
    - Answers Michael's question: "Where are we bleeding money?"
    - Strategic data for pricing & account management
    """)

st.divider()

# Demo
st.markdown("## 🚀 Live Demo: Client Profitability Analysis")

# Profit thresholds
PROFIT_THRESHOLDS = {
    'excellent': 25,
    'good': 15,
    'acceptable': 5
}

@st.cache_data
def load_profitability_data():
    """Load and calculate profitability data"""
    takt_client = TaktLMSClient()
    qb_client = QuickBooksClient()

    # Get all clients
    takt_clients = set(takt_client.get_all_clients())
    qb_clients = set(qb_client.get_all_clients())
    all_clients = takt_clients.union(qb_clients)

    # Collect data
    data = []
    for client_name in all_clients:
        # Labor data
        labor_data = takt_client.get_labor_costs(client_name)
        labor_cost = labor_data.get("total_cost", 0)
        labor_hours = labor_data.get("total_hours", 0)

        # Revenue data
        revenue_data = qb_client.get_client_revenue(client_name)
        revenue = revenue_data.get("total_revenue", 0)

        # Calculate profitability
        profit = revenue - labor_cost
        profit_margin = (profit / revenue * 100) if revenue > 0 else 0

        # Categorize
        if profit_margin >= PROFIT_THRESHOLDS['excellent']:
            category = "Excellent"
        elif profit_margin >= PROFIT_THRESHOLDS['good']:
            category = "Good"
        elif profit_margin >= PROFIT_THRESHOLDS['acceptable']:
            category = "Acceptable"
        elif profit_margin >= 0:
            category = "Poor"
        else:
            category = "Losing Money"

        data.append({
            "Client": client_name,
            "Revenue": revenue,
            "Labor Cost": labor_cost,
            "Labor Hours": labor_hours,
            "Profit": profit,
            "Profit Margin": profit_margin,
            "Category": category
        })

    df = pd.DataFrame(data)
    df = df.sort_values("Profit Margin", ascending=False)

    return df

# Load data button
if st.button("📊 Analyze All Clients", type="primary", use_container_width=True):
    with st.spinner("Loading data from Takt LMS and QuickBooks..."):
        try:
            df = load_profitability_data()

            st.success(f"✅ Analyzed {len(df)} clients")

            # Summary metrics
            st.divider()
            st.markdown("### 💰 Overall Performance")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                total_revenue = df["Revenue"].sum()
                st.metric("Total Revenue", f"${total_revenue:,.0f}")

            with col2:
                total_cost = df["Labor Cost"].sum()
                st.metric("Total Labor Cost", f"${total_cost:,.0f}")

            with col3:
                total_profit = df["Profit"].sum()
                st.metric("Total Profit", f"${total_profit:,.0f}")

            with col4:
                overall_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
                st.metric("Overall Margin", f"{overall_margin:.1f}%")

            # Category breakdown
            st.divider()
            st.markdown("### 📈 Category Breakdown")

            col1, col2, col3, col4, col5 = st.columns(5)

            category_counts = df["Category"].value_counts()

            with col1:
                excellent = category_counts.get("Excellent", 0)
                st.metric("Excellent (>25%)", excellent, delta="Great")

            with col2:
                good = category_counts.get("Good", 0)
                st.metric("Good (15-25%)", good, delta="Solid")

            with col3:
                acceptable = category_counts.get("Acceptable", 0)
                st.metric("Acceptable (5-15%)", acceptable, delta="OK")

            with col4:
                poor = category_counts.get("Poor", 0)
                st.metric("Poor (0-5%)", poor, delta="Caution", delta_color="inverse")

            with col5:
                losing = category_counts.get("Losing Money", 0)
                st.metric("Losing Money", losing, delta="Action Needed", delta_color="inverse")

            # Top performers
            st.divider()
            st.markdown("### ⭐ Top 5 Most Profitable Clients")

            top5 = df.nlargest(5, "Profit Margin")

            for idx, row in top5.iterrows():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

                with col1:
                    st.markdown(f"**{row['Client']}**")

                with col2:
                    st.markdown(f"Revenue: ${row['Revenue']:,.0f}")

                with col3:
                    st.markdown(f"Profit: ${row['Profit']:,.0f}")

                with col4:
                    st.markdown(f"**{row['Profit Margin']:.1f}%**")

            # Problem areas
            st.divider()
            st.markdown("### ⚠️ Problem Areas")

            losing_money = df[df["Profit"] < 0]
            low_margin = df[(df["Profit"] >= 0) & (df["Profit Margin"] < PROFIT_THRESHOLDS['acceptable'])]

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Clients Losing Money**")
                if len(losing_money) > 0:
                    for _, row in losing_money.iterrows():
                        st.error(f"**{row['Client']}**: ${row['Revenue']:,.0f} revenue, ${row['Labor Cost']:,.0f} cost → **{row['Profit Margin']:.1f}% margin**")
                else:
                    st.success("✅ No clients losing money!")

            with col2:
                st.markdown("**Low Margin Clients (0-5%)**")
                if len(low_margin) > 0:
                    for _, row in low_margin.iterrows():
                        st.warning(f"**{row['Client']}**: {row['Profit Margin']:.1f}% margin")
                else:
                    st.success("✅ No low-margin clients!")

            # Detailed table
            st.divider()
            st.markdown("### 📋 All Clients - Detailed View")

            # Format the dataframe
            display_df = df.copy()
            display_df["Revenue"] = display_df["Revenue"].apply(lambda x: f"${x:,.0f}")
            display_df["Labor Cost"] = display_df["Labor Cost"].apply(lambda x: f"${x:,.0f}")
            display_df["Profit"] = display_df["Profit"].apply(lambda x: f"${x:,.0f}")
            display_df["Profit Margin"] = display_df["Profit Margin"].apply(lambda x: f"{x:.1f}%")

            st.dataframe(
                display_df[["Client", "Revenue", "Labor Cost", "Profit", "Profit Margin", "Category"]],
                use_container_width=True,
                height=400
            )

            # Recommendations
            st.divider()
            st.markdown("### 💡 AI Recommendations")

            if len(losing_money) > 0:
                st.warning(f"""
                **Action Required: {len(losing_money)} clients are losing money**

                These clients need immediate attention:
                - Review pricing models
                - Assess scope creep
                - Consider rate increases
                - Reduce labor allocation
                """)

            if len(low_margin) > 0:
                st.info(f"""
                **Monitor: {len(low_margin)} clients have low margins (0-5%)**

                Recommendations:
                - Analyze labor efficiency
                - Review service scope
                - Consider gradual rate adjustments
                """)

            if len(top5) > 0:
                st.success(f"""
                **Learn from Success: Top {len(top5)} clients average {top5['Profit Margin'].mean():.1f}% margin**

                What makes them profitable?
                - Efficient labor allocation
                - Proper pricing
                - Streamlined processes

                Apply these lessons to other accounts!
                """)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.exception(e)

st.divider()

# Summary
st.markdown("## 📊 How It Works")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Data Sources:**
    1. **Takt LMS** - Labor hours and costs per client
    2. **QuickBooks Online** - Revenue and invoicing data
    3. **Google Gemini AI** - Strategic insights
    """)

with col2:
    st.markdown("""
    **Analysis Output:**
    - Client profitability rankings
    - Margin categorization
    - Problem client identification
    - Actionable recommendations
    """)

st.info("""
💡 **Michael's Question Answered:**

"Which clients are profitable? Where are we bleeding money?"

This agent automatically combines labor costs from Takt with revenue from QuickBooks
to show exactly which clients are making you money and which ones need attention.

**8-10 hours saved per week** that would otherwise be spent on manual Excel analysis.
""")
