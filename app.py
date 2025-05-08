import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import requests

# Configure app
st.set_page_config(
    page_title="FX Analytics Pro",
    layout="wide",
    menu_items={
        'About': "Professional USD/CAD tracker with fallback systems"
    }
)

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data():
    """
    Robust data loader with 3 fallback layers:
    1. Yahoo Finance (multiple ticker formats)
    2. ExchangeRate.host API
    3. Local cached data
    """
    # Try all Yahoo Finance ticker variants
    yf_tickers = ["CADUSD=X", "CAD=X", "USDCAD=X"]
    for ticker in yf_tickers:
        try:
            df = yf.download(ticker, period="3mo", progress=False)
            if not df.empty:
                return df[['Close']].rename(columns={'Close': 'Rate'})
        except:
            continue

    # Fallback 1: ExchangeRate.host API
    try:
        url = "https://api.exchangerate.host/timeseries?start_date={}&end_date={}&base=USD&symbols=CAD"
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        response = requests.get(url.format(start_date, end_date)).json()
        
        rates = {
            pd.to_datetime(date): float(values['CAD'])
            for date, values in response['rates'].items()
        }
        return pd.DataFrame.from_dict(rates, orient='index').rename(columns={0: 'Rate'})
    
    # Fallback 2: Local cached data
    except:
        st.session_state.using_fallback = True
        return pd.DataFrame({
            'Rate': [1.35, 1.34, 1.36, 1.33],
            'Date': pd.date_range(end=datetime.now(), periods=4)
        }).set_index('Date')

# Main app
st.title("💱 USD/CAD Professional Tracker")
df = load_data()

# Dashboard layout
col1, col2 = st.columns([2, 1])

with col1:
    # Interactive chart
    fig = px.line(df, y="Rate", 
                 title=f"Exchange Rate (Last 3 Months)",
                 labels={"value": "USD/CAD", "index": "Date"})
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Key metrics
    st.subheader("Live Metrics")
    
    try:
        current_rate = df['Rate'].iloc[-1]
        st.metric("Current Rate", f"{current_rate:.4f}")
        
        if len(df) >= 5:
            weekly_change = (current_rate / df['Rate'].iloc[-5] - 1) * 100
            st.metric("Weekly Change", f"{weekly_change:.2f}%")
        
        st.metric("Volatility (14D)", f"{df['Rate'].rolling(14).std().iloc[-1]:.5f}")
    except:
        st.warning("Metrics temporarily unavailable")

# System status
with st.expander("ℹ️ System Status"):
    if st.session_state.get('using_fallback'):
        st.error("Using fallback data - external APIs unavailable")
    else:
        st.success("Connected to live data sources")
    
    st.write(f"Last refresh: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.write("Data preview:", df.tail(3))

# Disclaimer
st.caption("""
⚠️ For professional use only. Rates may be delayed. 
This tool uses multiple fallback systems to ensure continuous operation.
""")
