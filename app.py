import streamlit as st
import yfinance as yf
import plotly.express as px

st.set_page_config(layout="wide")
st.title("💰 Professional USD/CAD Tracker")

# Data
@st.cache_data
def load_data():
    return yf.download("CADUSD=X", period="3mo")

df = load_data()

# Layout
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(px.line(df, y="Close", title="Exchange Rate"), use_container_width=True)
with col2:
    st.plotly_chart(px.line(df.rolling(14).std(), title="Volatility"), use_container_width=True)

# Metrics
st.metric("Current Rate", f"{df['Close'].iloc[-1]:.4f}", 
          f"{(df['Close'].iloc[-1]/df['Close'].iloc[-5]-1)*100:.2f}% weekly change")
