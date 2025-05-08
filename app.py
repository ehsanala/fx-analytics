import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("💰 Professional USD/CAD Tracker")

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data():
    try:
        # Try getting fresh data
        df = yf.download("CADUSD=X", period="3mo", progress=False)
        if df.empty:
            raise ValueError("YFinance returned empty data")
        return df
    except Exception as e:
        st.warning(f"Using backup data: {str(e)}")
        # Fallback to static data
        return pd.DataFrame({
            'Close': [1.35, 1.34, 1.36, 1.33],
            'Date': pd.date_range(end=pd.Timestamp.now(), periods=4)
        }).set_index('Date')

df = load_data()

# Safely display metrics
if not df.empty:
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(px.line(df, y="Close", title="Exchange Rate"), 
                       use_container_width=True)
    with col2:
        st.plotly_chart(px.line(df.rolling(14).std(), title="Volatility"), 
                       use_container_width=True)
    
    try:
        current_rate = df['Close'].iloc[-1]
        weekly_change = (df['Close'].iloc[-1]/df['Close'].iloc[-5]-1)*100
        st.metric("Current Rate", f"{current_rate:.4f}", 
                 f"{weekly_change:.2f}% weekly change")
    except IndexError:
        st.warning("Insufficient data points for metrics")
else:
    st.error("Failed to load data. Please try again later.")

# Add debug info
with st.expander("Debug Info"):
    st.write("Last data fetch:", pd.Timestamp.now())
    st.write("Data sample:", df.tail(3))
