import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
from data_generator    import generate_nilepay_data
from payments_engine   import (calculate_gmv_metrics, daily_gmv_trend,
                                payment_method_analysis, failure_analysis,
                                city_performance, customer_analytics)

st.set_page_config(page_title="NilePay Payments Analytics",
                   page_icon="💳", layout="wide")

st.markdown("""
<h1 style='text-align:center;color:#1a5276;'>💳 NilePay</h1>
<p style='text-align:center;color:gray;'>
    Payments Analytics & Business Intelligence Dashboard
</p><hr>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────
st.sidebar.header("⚙️ Filters")
n_tx   = st.sidebar.slider("Transactions", 500, 5000, 1000, 500)
upload = st.sidebar.file_uploader("Upload CSV", type=["csv"])
cities = st.sidebar.multiselect("Filter by City", [
    'Cairo', 'Alexandria', 'Giza', 'Mansoura',
    'Aswan', 'Luxor', 'Tanta', 'Suez'
])

@st.cache_data
def load_data(n, file=None):
    if file:
        df = pd.read_csv(file)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    else:
        df = generate_nilepay_data(n)
    return df

with st.spinner("Loading analytics..."):
    df = load_data(n_tx, upload)
    if cities:
        df = df[df['city'].isin(cities)]

# ── GMV KPIs ─────────────────────────────────────────────
st.subheader("💰 Business Performance — KPIs")
metrics = calculate_gmv_metrics(df)

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total GMV",        f"EGP {metrics['gmv']:,.0f}")
col2.metric("Total Transactions", f"{metrics['total_tx']:,}")
col3.metric("Avg Transaction",  f"EGP {metrics['avg_tx_value']:,.0f}")
col4.metric("Success Rate",     f"{metrics['success_rate']}%")
col5.metric("Failure Rate",     f"{metrics['failure_rate']}%",
            delta=f"-{metrics['failure_rate']}%",
            delta_color="inverse")

st.markdown("---")

# ── Daily GMV Trend ──────────────────────────────────────
st.subheader("📈 Daily GMV Trend")
daily = daily_gmv_trend(df)
fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=daily['date'], y=daily['gmv'],
    mode='lines+markers', name='Daily GMV',
    line=dict(color='#3498db', width=2),
    fill='tozeroy', fillcolor='rgba(52,152,219,0.1)'
))
fig1.update_layout(
    title="Daily Gross Merchandise Value (GMV)",
    xaxis_title="Date", yaxis_title="GMV (EGP)"
)
st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")

# ── Payment Method Analysis ──────────────────────────────
st.subheader("💳 Payment Method Performance")
method_df = payment_method_analysis(df)
col1, col2 = st.columns(2)
with col1:
    fig2 = px.bar(method_df, x='payment_method', y='revenue',
                  color='payment_method',
                  title="Revenue by Payment Method",
                  labels={'payment_method': 'Method',
                          'revenue': 'Revenue (EGP)'})
    st.plotly_chart(fig2, use_container_width=True)
with col2:
    fig3 = px.bar(method_df, x='payment_method', y='success_rate',
                  color='payment_method',
                  title="Success Rate by Payment Method",
                  labels={'payment_method': 'Method',
                          'success_rate': 'Success Rate %'})
    fig3.add_hline(y=80, line_dash="dash",
                   line_color="red",
                   annotation_text="Target 80%")
    st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# ── Failure Analysis ─────────────────────────────────────
st.subheader("❌ Transaction Failure Analysis")
failure_df = failure_analysis(df)
if len(failure_df) > 0:
    col1, col2 = st.columns(2)
    with col1:
        fig4 = px.pie(failure_df, values='Count', names='Reason',
                      title="Failure Reasons Breakdown")
        st.plotly_chart(fig4, use_container_width=True)
    with col2:
        st.dataframe(failure_df, use_container_width=True)

st.markdown("---")

# ── City Performance ─────────────────────────────────────
st.subheader("🗺️ Geographic Performance")
city_df = city_performance(df)
col1, col2 = st.columns(2)
with col1:
    fig5 = px.bar(city_df, x='city', y='gmv',
                  color='gmv',
                  color_continuous_scale='Blues',
                  title="GMV by City",
                  labels={'city': 'City', 'gmv': 'GMV (EGP)'})
    st.plotly_chart(fig5, use_container_width=True)
with col2:
    fig6 = px.bar(city_df, x='city', y='failure_rate',
                  color='failure_rate',
                  color_continuous_scale='Reds',
                  title="Failure Rate by City",
                  labels={'city': 'City',
                          'failure_rate': 'Failure Rate %'})
    fig6.add_hline(y=15, line_dash="dash", line_color="red",
                   annotation_text="Alert Threshold")
    st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")

# ── Customer Analytics ───────────────────────────────────
st.subheader("👥 Customer Analytics")
cust_df = customer_analytics(df)
churn   = cust_df['churn_risk'].value_counts().reset_index()
churn.columns = ['Risk', 'Count']

col1, col2, col3 = st.columns(3)
active = len(cust_df[cust_df['churn_risk'] == '🟢 Active'])
medium = len(cust_df[cust_df['churn_risk'] == '🟡 Medium'])
high   = len(cust_df[cust_df['churn_risk'] == '🔴 High'])

col1.metric("🟢 Active Customers",      active)
col2.metric("🟡 At Risk Customers",     medium)
col3.metric("🔴 High Churn Risk",       high)

fig7 = px.pie(churn, values='Count', names='Risk',
              color='Risk',
              color_discrete_map={
                  '🔴 High':   '#e74c3c',
                  '🟡 Medium': '#f39c12',
                  '🟢 Active': '#2ecc71'},
              title="Customer Churn Risk Distribution")
st.plotly_chart(fig7, use_container_width=True)

st.markdown("---")

# ── AI Insights ──────────────────────────────────────────
st.subheader("🤖 AI Business Insights")
if st.button("Generate AI Insights"):
    with st.spinner("Generating insights..."):
        prompt = f"""
You are a Senior Business Analyst at NilePay, an Egyptian digital payments company.

Business Performance Summary:
- Total GMV: EGP {metrics['gmv']:,.0f}
- Total Transactions: {metrics['total_tx']:,}
- Success Rate: {metrics['success_rate']}%
- Failure Rate: {metrics['failure_rate']}%
- Active Customers: {active}
- High Churn Risk Customers: {high}
- Top City by GMV: {city_df.iloc[0]['city'] if len(city_df) > 0 else 'N/A'}
- Highest Failure City: {city_df.nlargest(1,'failure_rate').iloc[0]['city'] if len(city_df) > 0 else 'N/A'}

Write a professional Business Intelligence Report with:
1. Executive Summary
2. Revenue Performance Analysis
3. Customer Health Assessment
4. Geographic Insights
5. Strategic Recommendations (5 specific actions)

Use professional FinTech analytics language.
"""
        try:
            groq_key = st.secrets.get("GROQ_API_KEY", "")
            if groq_key:
                resp = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Content-Type":  "application/json",
                        "Authorization": f"Bearer {groq_key}"
                    },
                    json={
                        "model":      "llama-3.3-70b-versatile",
                        "messages":   [{"role": "user",
                                        "content": prompt}],
                        "max_tokens": 1000
                    },
                    timeout=30
                )
                result = resp.json()
                if "choices" in result:
                    st.markdown(
                        result["choices"][0]["message"]["content"])
                else:
                    st.error("API Error")
            else:
                st.warning("No API key in secrets.toml")
        except Exception as e:
            st.error(f"Error: {e}")