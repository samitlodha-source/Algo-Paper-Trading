import random
import time
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Paper Trader", page_icon="📈", layout="centered")

st.title("📈 Robust Paper Trading Platform")
st.markdown("Test your algorithmic strategies with live data or seamless fallback simulation.")

col1, col2 = st.columns(2)
with col1:
    ticker_symbol = st.text_input("Stock Ticker (e.g. AAPL or RELIANCE.NS)", value="AAPL").upper()
with col2:
    strategy_choice = st.selectbox(
        "Select Strategy",
        ["Moving Average Crossover", "Opening Range Breakout", "RSI Mean Reversion"]
    )

initial_balance = st.number_input("Starting Virtual Capital", value=100000.0, step=10000.0)

if st.button("🚀 Run Simulation", type="primary"):
    prices = []
    data_source_used = "Live Data (Yahoo Finance)"
    
    with st.spinner(f"Fetching data for {ticker_symbol}..."):
        try:
            import yfinance as yf
            df = yf.download(ticker_symbol, period="5d", interval="1h", progress=False)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            if "Close" in df.columns:
                prices = df["Close"].dropna().tolist()
            
            if len(prices) < 5:
                raise ValueError("Not enough data points found.")
        except Exception as e:
            # Fallback triggered if Yahoo blocks the server or ticker is unrecognized
            data_source_used = "Simulated Market Data (Cloud API restriction bypass)"
            base_price = 2500.0 if ".NS" in ticker_symbol or "NIFTY" in ticker_symbol else 180.0
            prices = [base_price + random.uniform(-5, 5) for _ in range(30)]
    
    st.info(f"Source: **{data_source_used}** ({len(prices)} data points loaded)")
    
    cash = initial_balance
    position = 0
    entry_price = 0.0
    
    metric_cash = st.empty()
    metric_portfolio = st.empty()
    status_box = st.empty()
    
    for i in range(len(prices)):
        current_price = prices[i]
        
        # Strategy Logic
        action = "HOLD"
        if i >= 4:
            if strategy_choice == "Moving Average Crossover":
                fast = sum(prices[i-2:i])/2
                slow = sum(prices[i-4:i])/4
                action = "BUY" if fast > slow else "SELL"
            elif strategy_choice == "Opening Range Breakout":
                action = "BUY" if current_price > max(prices[:3]) else "SELL"
            else:
                price_change = current_price - prices[i-1]
                action = "BUY" if price_change < 0 else "SELL"
        
        # Execution
        if action == "BUY" and position == 0:
            position = int(cash / current_price)
            if position > 0:
                cash -= position * current_price
                entry_price = current_price
                status_box.info(f"🟢 BOUGHT {position} shares at {current_price:.2f}")
        elif action == "SELL" and position > 0:
            revenue = position * current_price
            profit = revenue - (position * entry_price)
            cash += revenue
            status_box.success(f"🔴 SOLD shares | P&L: {profit:+.2f}")
            position = 0
        
        portfolio_val = cash + (position * current_price)
        metric_cash.metric("Available Cash", f"{cash:,.2f}")
        metric_portfolio.metric("Portfolio Value", f"{portfolio_val:,.2f}", delta=f"{portfolio_val - initial_balance:,.2f}")
        
        time.sleep(0.1)
        
    st.balloons()
    st.success("Simulation finished successfully!")
