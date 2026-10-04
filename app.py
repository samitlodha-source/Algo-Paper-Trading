import random
import time
import streamlit as st

st.set_page_config(page_title="Mobile Algo Trader", page_icon="📈", layout="centered")

st.title("📱 Mobile Paper Trading Platform")
st.markdown("Test algorithmic scalping strategies with virtual capital right from your phone.")

# Controls
strategy_choice = st.selectbox(
    "Select Strategy",
    ["Moving Average Crossover", "Opening Range Breakout", "RSI Mean Reversion"]
)

initial_balance = st.number_input("Starting Virtual Capital (₹)", value=100000.0, step=10000.0)

if st.button("🚀 Run Live Simulation", type="primary"):
    st.write(f"**Running simulation with {strategy_choice}...**")
    
    cash = initial_balance
    position = 0
    entry_price = 0.0
    
    base_price = 2500.0
    prices = [base_price + random.uniform(-10, 10) for _ in range(25)]
    
    metric_cash = st.empty()
    metric_portfolio = st.empty()
    status_box = st.empty()
    
    for i, p in enumerate(prices):
        current_price = p + random.uniform(-2, 2)
        
        # Strategy Logic Simulation
        action = "HOLD"
        if i >= 3:
            if strategy_choice == "Moving Average Crossover":
                fast = sum(prices[i-2:i])/2
                slow = sum(prices[i-4:i])/4
                action = "BUY" if fast > slow else "SELL"
            elif strategy_choice == "Opening Range Breakout":
                action = "BUY" if current_price > max(prices[:3]) else "SELL"
            else:
                action = "BUY" if random.random() > 0.5 else "SELL"
        
        # Execution
        if action == "BUY" and position == 0:
            position = int(cash / current_price)
            if position > 0:
                cash -= position * current_price
                entry_price = current_price
                status_box.info(f"🟢 BOUGHT {position} shares at ₹{current_price:.2f}")
        elif action == "SELL" and position > 0:
            revenue = position * current_price
            profit = revenue - (position * entry_price)
            cash += revenue
            status_box.success(f"🔴 SOLD shares | P&L: ₹{profit:+.2f}")
            position = 0
        
        portfolio_val = cash + (position * current_price)
        metric_cash.metric("Available Cash", f"₹{cash:,.2f}")
        metric_portfolio.metric("Portfolio Value", f"₹{portfolio_val:,.2f}", delta=f"₹{portfolio_val - initial_balance:,.2f}")
        
        time.sleep(0.15) # Smooth ticker delay
        
    st.balloons()
    st.success("Simulation finished successfully!")
