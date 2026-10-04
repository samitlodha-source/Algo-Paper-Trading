import time
import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Real-Data Paper Trader", page_icon="📈", layout="centered")

st.title("📈 Real-Data Paper Trading Platform")
st.markdown("Test your algorithmic strategies using live data from any stock ticker.")

# Sidebar or inputs for configuration
col1, col2 = st.columns(2)
with col1:
    ticker_symbol = st.text_input("Stock Ticker Symbol", value="AAPL").upper()
with col2:
    strategy_choice = st.selectbox(
        "Select Strategy",
        ["Moving Average Crossover", "Opening Range Breakout", "RSI Mean Reversion"]
    )

initial_balance = st.number_input("Starting Virtual Capital (₹/$)", value=100000.0, step=10000.0)

if st.button("🚀 Run Simulation with Real Data", type="primary"):
    with st.spinner(f"Fetching market data for {ticker_symbol}..."):
        try:
            # Fetch recent price data (using 5 days of hourly data for fine-grained steps)
            df = yf.download(ticker_symbol, period="5d", interval="1h", progress=False)
            
            # Handle multi-index columns if returned by newer yfinance versions
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
                
            prices = df["Close"].dropna().tolist()
            
            if len(prices) < 10:
                st.error("Not enough price data found for this ticker. Try another symbol like 'AAPL' or 'MSFT'.")
            else:
                st.success(f"Loaded {len(prices)} price data points for {ticker_symbol}!")
                
                cash = initial_balance
                position = 0
                entry_price = 0.0
                
                metric_cash = st.empty()
                metric_portfolio = st.empty()
                status_box = st.empty()
                
                chart_slot = st.empty()
                chart_slot.line_chart(prices[:5]) # Show progressive chart
                
                for i in range(len(prices)):
                    current_price = prices[i]
                    
                    # Strategy Logic Simulation
                    action = "HOLD"
                    if i >= 4:
                        if strategy_choice == "Moving Average Crossover":
                            fast = sum(prices[i-2:i])/2
                            slow = sum(prices[i-4:i])/4
                            action = "BUY" if fast > slow else "SELL"
                        elif strategy_choice == "Opening Range Breakout":
                            action = "BUY" if current_price > max(prices[:3]) else "SELL"
                        else: # RSI Mean Reversion simulation
                            price_change = current_price - prices[i-1]
                            action = "BUY" if price_change < 0 else "SELL"
                    
                    # Execution
                    if action == "BUY" and position == 0:
                        position = int(cash / current_price)
                        if position > 0:
                            cash -= position * current_price
                            entry_price = current_price
                            status_box.info(f"🟢 BOUGHT {position} shares of {ticker_symbol} at ₹{current_price:.2f}")
                    elif action == "SELL" and position > 0:
                        revenue = position * current_price
                        profit = revenue - (position * entry_price)
                        cash += revenue
                        status_box.success(f"🔴 SOLD shares | P&L: ₹{profit:+.2f}")
                        position = 0
                    
                    portfolio_val = cash + (position * current_price)
                    metric_cash.metric("Available Cash", f"{cash:,.2f}")
                    metric_portfolio.metric("Portfolio Value", f"{portfolio_val:,.2f}", delta=f"{portfolio_val - initial_balance:,.2f}")
                    
                    time.sleep(0.1) # Smooth playback delay
                    
                st.balloons()
                st.success("Simulation finished using real market data!")

        except Exception as e:
            st.error(f"Error fetching data: {e}")
