import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import robin_stocks.robinhood as rs
from typing import Dict, List, Tuple
import time

# Configuration
st.set_page_config(
    page_title="Smart Stock Portfolio Analyzer",
    page_icon="📈",
    layout="wide"
)

class StockAnalyzer:
    def __init__(self):
        self.market_indices = {
            'S&P 500': '^GSPC',
            'NASDAQ': '^IXIC',
            'DOW': '^DJI'
        }
        
    def get_stock_data(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """Fetch stock data using yfinance"""
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period=period)
            return data
        except Exception as e:
            st.error(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
    
    def calculate_market_drop(self, symbol: str) -> float:
        """Calculate the percentage drop from recent high"""
        data = self.get_stock_data(symbol, "6mo")
        if data.empty:
            return 0
        
        recent_high = data['High'].max()
        current_price = data['Close'].iloc[-1]
        drop_percentage = ((recent_high - current_price) / recent_high) * 100
        
        return drop_percentage
    
    def get_stock_metrics(self, symbol: str) -> Dict:
        """Get key stock metrics"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            data = self.get_stock_data(symbol, "1y")
            
            if data.empty:
                return {}
            
            current_price = data['Close'].iloc[-1]
            year_high = data['High'].max()
            year_low = data['Low'].min()
            
            # Calculate volatility (standard deviation of returns)
            returns = data['Close'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(252) * 100  # Annualized
            
            # Calculate RSI
            rsi = self.calculate_rsi(data['Close'])
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'year_high': year_high,
                'year_low': year_low,
                'drop_from_high': self.calculate_market_drop(symbol),
                'volatility': volatility,
                'rsi': rsi,
                'market_cap': info.get('marketCap', 'N/A'),
                'pe_ratio': info.get('trailingPE', 'N/A'),
                'dividend_yield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0
            }
        except Exception as e:
            st.error(f"Error getting metrics for {symbol}: {e}")
            return {}
    
    def calculate_rsi(self, prices: pd.Series, window: int = 14) -> float:
        """Calculate RSI (Relative Strength Index)"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if not rsi.empty else 50

def login_to_robinhood(username, password, mfa_code):
    """
    Logs into Robinhood using credentials and MFA code.
    Returns True on success, False on failure.
    """
    try:
        st.info("Attempting to log in...")
        rs.login(username, password, mfa_code=mfa_code)
        st.session_state.logged_in = True
        st.success("✅ Login Successful!")
        # Give a moment for the success message to be seen before re-running
        time.sleep(2)
        return True
    except Exception as e:
        st.error(f"Login Failed: {e}")
        st.session_state.logged_in = False
        return False

class RobinhoodIntegration:
    def __init__(self):
        pass
    
    def get_portfolio(self) -> List[Dict]:
        """Get current portfolio holdings"""
        if not st.session_state.get('logged_in', False):
            return []
        
        try:
            positions = rs.get_open_stock_positions()
            portfolio = []
            
            for position in positions:
                if position and float(position['quantity']) > 0:
                    symbol = rs.get_instrument_by_url(position['instrument'])['symbol']
                    current_price = float(rs.get_latest_price(symbol)[0])
                    quantity = float(position['quantity'])
                    avg_cost = float(position['average_buy_price'])
                    
                    portfolio.append({
                        'symbol': symbol,
                        'quantity': quantity,
                        'average_cost': avg_cost,
                        'current_price': current_price,
                        'current_value': quantity * current_price,
                        'total_cost': quantity * avg_cost,
                        'gain_loss': (quantity * current_price) - (quantity * avg_cost),
                        'gain_loss_percent': ((current_price - avg_cost) / avg_cost) * 100
                    })
            
            return portfolio
        except Exception as e:
            st.error(f"Error fetching portfolio: {e}")
            return []
    
    def get_account_info(self) -> Dict:
        """Get account information"""
        if not st.session_state.get('logged_in', False):
            return {}
        
        try:
            account = rs.load_account_profile()
            positions = rs.get_open_stock_positions()
            
            # Calculate total portfolio value
            total_value = 0
            for position in positions:
                if position and float(position['quantity']) > 0:
                    symbol = rs.get_instrument_by_url(position['instrument'])['symbol']
                    current_price = float(rs.get_latest_price(symbol)[0])
                    total_value += float(position['quantity']) * current_price
            
            # Get buying power
            account_data = rs.load_account_profile()
            buying_power = float(account_data.get('buying_power', 0))
            
            return {
                'total_portfolio_value': total_value,
                'buying_power': buying_power,
                'total_account_value': total_value + buying_power
            }
        except Exception as e:
            st.error(f"Error fetching account info: {e}")
            return {}
    
    def place_buy_order(self, symbol: str, amount: float) -> bool:
        """Place a buy order"""
        if not st.session_state.get('logged_in', False):
            st.error("Please login first")
            return False
            
        try:
            # Get current price to calculate quantity
            current_price = float(rs.get_latest_price(symbol)[0])
            quantity = int(amount / current_price)
            
            if quantity < 1:
                st.warning(f"Amount too small to buy even 1 share of {symbol} at ${current_price:.2f}")
                return False
            
            # For safety, this is still a simulation
            # Uncomment the line below to place real orders (USE WITH CAUTION!)
            # result = rs.order_buy_market(symbol, quantity)
            
            st.success(f"📋 Order placed: {quantity} shares of {symbol} at ~${current_price:.2f} each (Total: ~${quantity * current_price:.2f})")
            st.info("⚠️ This is a simulation. Uncomment the order line in the code to place real trades.")
            return True
            
        except Exception as e:
            st.error(f"Error placing order: {e}")
            return False

def main():
    st.title("📈 Smart Stock Portfolio Analyzer")
    st.markdown("Analyze your portfolio and find buying opportunities when the market drops")
    
    analyzer = StockAnalyzer()
    rh_integration = RobinhoodIntegration()
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Market drop threshold
        drop_threshold = st.slider("Market Drop Threshold (%)", 10, 50, 30)
        
        # Investment amount
        investment_amount = st.number_input("Investment Amount ($)", min_value=100, max_value=10000, value=1000)
        
        # Robinhood login (optional)
        st.subheader("🔐 Robinhood Integration")
        
        # Check login status
        if st.session_state.get('logged_in', False):
            st.success("✅ Logged in to Robinhood")
            if st.button("🚪 Logout"):
                rs.logout()
                st.session_state.logged_in = False
                st.rerun()
        else:
            with st.expander("Login to Robinhood"):
                username = st.text_input("Username", key="rh_username")
                password = st.text_input("Password", type="password", key="rh_password")
                mfa_code = st.text_input("MFA Code (from your authenticator app)", key="rh_mfa", max_chars=6)
                
                if st.button("🔑 Login to Robinhood"):
                    if username and password and mfa_code:
                        if login_to_robinhood(username, password, mfa_code):
                            st.rerun()
                    else:
                        st.error("Please fill in all fields including MFA code")
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Market Overview", "💼 Portfolio Analysis", "🎯 Buy Opportunities", "📈 Stock Research"])
    
    with tab1:
        st.header("Market Overview")
        
        # Market indices analysis
        col1, col2, col3 = st.columns(3)
        
        for i, (name, symbol) in enumerate(analyzer.market_indices.items()):
            with [col1, col2, col3][i]:
                metrics = analyzer.get_stock_metrics(symbol)
                if metrics:
                    drop = metrics['drop_from_high']
                    
                    # Color coding based on drop
                    if drop >= drop_threshold:
                        color = "🔴"
                        status = "BUY SIGNAL"
                    elif drop >= 15:
                        color = "🟡"
                        status = "WATCH"
                    else:
                        color = "🟢"
                        status = "NORMAL"
                    
                    st.metric(
                        label=f"{color} {name}",
                        value=f"${metrics['current_price']:.2f}",
                        delta=f"-{drop:.1f}% from high"
                    )
                    st.caption(f"Status: **{status}**")
        
        # Market trend chart
        st.subheader("Market Trends (Last 6 Months)")
        
        market_data = {}
        for name, symbol in analyzer.market_indices.items():
            data = analyzer.get_stock_data(symbol, "6mo")
            if not data.empty:
                market_data[name] = data['Close']
        
        if market_data:
            df = pd.DataFrame(market_data)
            # Normalize to percentage change from start
            df_normalized = (df / df.iloc[0] - 1) * 100
            
            fig = px.line(df_normalized, title="Market Performance (% Change)")
            fig.update_layout(yaxis_title="Percentage Change (%)", xaxis_title="Date")
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.header("Portfolio Analysis")
        
        if st.session_state.get('logged_in', False):
            # Real portfolio from Robinhood
            portfolio = rh_integration.get_portfolio()
            account_info = rh_integration.get_account_info()
            
            if account_info:
                # Account overview
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Portfolio Value", f"${account_info['total_portfolio_value']:,.2f}")
                with col2:
                    st.metric("Buying Power", f"${account_info['buying_power']:,.2f}")
                with col3:
                    st.metric("Total Account Value", f"${account_info['total_account_value']:,.2f}")
            
            if portfolio:
                # Portfolio summary
                df_portfolio = pd.DataFrame(portfolio)
                
                total_value = df_portfolio['current_value'].sum()
                total_cost = df_portfolio['total_cost'].sum()
                total_gain_loss = df_portfolio['gain_loss'].sum()
                total_return = (total_gain_loss / total_cost) * 100 if total_cost > 0 else 0
                
                st.subheader("Portfolio Performance")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Value", f"${total_value:,.2f}")
                with col2:
                    st.metric("Total Cost", f"${total_cost:,.2f}")
                with col3:
                    st.metric("Total Gain/Loss", f"${total_gain_loss:,.2f}")
                with col4:
                    st.metric("Total Return", f"{total_return:.2f}%")
                
                # Holdings breakdown
                st.subheader("Current Holdings")
                
                # Format the dataframe for display
                display_df = df_portfolio.copy()
                display_df['Current Value'] = display_df['current_value'].apply(lambda x: f"${x:,.2f}")
                display_df['Total Cost'] = display_df['total_cost'].apply(lambda x: f"${x:,.2f}")
                display_df['Gain/Loss'] = display_df['gain_loss'].apply(lambda x: f"${x:,.2f}")
                display_df['Return %'] = display_df['gain_loss_percent'].apply(lambda x: f"{x:.2f}%")
                display_df['Avg Cost'] = display_df['average_cost'].apply(lambda x: f"${x:.2f}")
                display_df['Current Price'] = display_df['current_price'].apply(lambda x: f"${x:.2f}")
                
                # Select columns to display
                display_columns = ['symbol', 'quantity', 'Avg Cost', 'Current Price', 'Current Value', 'Gain/Loss', 'Return %']
                st.dataframe(display_df[display_columns], use_container_width=True)
                
                # Portfolio allocation pie chart
                fig = px.pie(df_portfolio, values='current_value', names='symbol', 
                           title="Portfolio Allocation by Value")
                st.plotly_chart(fig, use_container_width=True)
                
                # Performance chart
                gains = df_portfolio[df_portfolio['gain_loss'] > 0]
                losses = df_portfolio[df_portfolio['gain_loss'] <= 0]
                
                fig_perf = go.Figure()
                if not gains.empty:
                    fig_perf.add_trace(go.Bar(name='Gains', x=gains['symbol'], y=gains['gain_loss'], 
                                            marker_color='green'))
                if not losses.empty:
                    fig_perf.add_trace(go.Bar(name='Losses', x=losses['symbol'], y=losses['gain_loss'], 
                                            marker_color='red'))
                
                fig_perf.update_layout(title="Gains/Losses by Stock", xaxis_title="Stock", yaxis_title="Gain/Loss ($)")
                st.plotly_chart(fig_perf, use_container_width=True)
                
            else:
                st.info("No open positions found in your portfolio.")
        
        else:
            # Demo portfolio for users not logged in
            st.info("💡 Login to Robinhood to see your real portfolio, or view the demo below")
            
            demo_portfolio = [
                {'Symbol': 'AAPL', 'Shares': 10, 'Avg Cost': 150.00, 'Current Price': 175.00},
                {'Symbol': 'GOOGL', 'Shares': 5, 'Avg Cost': 2500.00, 'Current Price': 2800.00},
                {'Symbol': 'TSLA', 'Shares': 8, 'Avg Cost': 250.00, 'Current Price': 200.00},
                {'Symbol': 'MSFT', 'Shares': 15, 'Avg Cost': 300.00, 'Current Price': 350.00}
            ]
            
            df_demo = pd.DataFrame(demo_portfolio)
            df_demo['Current Value'] = df_demo['Shares'] * df_demo['Current Price']
            df_demo['Total Cost'] = df_demo['Shares'] * df_demo['Avg Cost']
            df_demo['Gain/Loss'] = df_demo['Current Value'] - df_demo['Total Cost']
            df_demo['Return %'] = (df_demo['Gain/Loss'] / df_demo['Total Cost']) * 100
            
            # Format for display
            df_demo['Current Value'] = df_demo['Current Value'].apply(lambda x: f"${x:,.2f}")
            df_demo['Total Cost'] = df_demo['Total Cost'].apply(lambda x: f"${x:,.2f}")
            df_demo['Gain/Loss'] = df_demo['Gain/Loss'].apply(lambda x: f"${x:,.2f}")
            df_demo['Return %'] = df_demo['Return %'].apply(lambda x: f"{x:.2f}%")
            df_demo['Avg Cost'] = df_demo['Avg Cost'].apply(lambda x: f"${x:.2f}")
            df_demo['Current Price'] = df_demo['Current Price'].apply(lambda x: f"${x:.2f}")
            
            st.dataframe(df_demo, use_container_width=True)
    
    with tab3:
        st.header("🎯 Buy Opportunities")
        
        # Stock symbols to analyze
        default_stocks = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NVDA', 'META', 'NFLX']
        
        # Allow user to add custom stocks
        custom_stocks = st.text_input("Add custom stocks (comma-separated)", 
                                    placeholder="e.g., AMD, INTC, CRM")
        
        if custom_stocks:
            additional_stocks = [s.strip().upper() for s in custom_stocks.split(',')]
            all_stocks = default_stocks + additional_stocks
        else:
            all_stocks = default_stocks
        
        st.subheader(f"Analyzing {len(all_stocks)} stocks for opportunities...")
        
        # Analyze stocks
        opportunities = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, symbol in enumerate(all_stocks):
            status_text.text(f'Analyzing {symbol}...')
            metrics = analyzer.get_stock_metrics(symbol)
            
            if metrics and metrics['drop_from_high'] >= drop_threshold:
                opportunities.append(metrics)
            
            progress_bar.progress((i + 1) / len(all_stocks))
            time.sleep(0.1)  # Small delay to show progress
        
        status_text.text('Analysis complete!')
        progress_bar.empty()
        status_text.empty()
        
        if opportunities:
            st.success(f"🎯 Found {len(opportunities)} buying opportunities!")
            
            # Sort by drop percentage
            opportunities.sort(key=lambda x: x['drop_from_high'], reverse=True)
            
            for opp in opportunities:
                with st.expander(f"💰 {opp['symbol']} - Down {opp['drop_from_high']:.1f}% from high"):
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Current Price", f"${opp['current_price']:.2f}")
                        st.metric("Year High", f"${opp['year_high']:.2f}")
                    
                    with col2:
                        st.metric("Drop from High", f"{opp['drop_from_high']:.1f}%")
                        st.metric("RSI", f"{opp['rsi']:.1f}")
                    
                    with col3:
                        st.metric("Volatility", f"{opp['volatility']:.1f}%")
                        if opp['pe_ratio'] != 'N/A':
                            st.metric("P/E Ratio", f"{opp['pe_ratio']:.1f}")
                    
                    with col4:
                        if opp['dividend_yield'] > 0:
                            st.metric("Dividend Yield", f"{opp['dividend_yield']:.2f}%")
                        
                        # Buy button
                        if st.button(f"Buy ${investment_amount} of {opp['symbol']}", key=f"buy_{opp['symbol']}"):
                            rh_integration.place_buy_order(opp['symbol'], investment_amount)
        else:
            st.info("🔍 No buying opportunities found at current thresholds. Consider lowering the drop threshold.")
    
    with tab4:
        st.header("📈 Stock Research")
        
        # Stock symbol input
        research_symbol = st.text_input("Enter stock symbol for detailed analysis", 
                                      value="AAPL", max_chars=10).upper()
        
        if research_symbol:
            metrics = analyzer.get_stock_metrics(research_symbol)
            
            if metrics:
                # Stock overview
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader(f"{research_symbol} Overview")
                    st.metric("Current Price", f"${metrics['current_price']:.2f}")
                    st.metric("52-Week High", f"${metrics['year_high']:.2f}")
                    st.metric("52-Week Low", f"${metrics['year_low']:.2f}")
                    st.metric("Drop from High", f"{metrics['drop_from_high']:.1f}%")
                
                with col2:
                    st.subheader("Key Metrics")
                    st.metric("RSI", f"{metrics['rsi']:.1f}")
                    st.metric("Volatility", f"{metrics['volatility']:.1f}%")
                    if metrics['pe_ratio'] != 'N/A':
                        st.metric("P/E Ratio", f"{metrics['pe_ratio']:.1f}")
                    if metrics['dividend_yield'] > 0:
                        st.metric("Dividend Yield", f"{metrics['dividend_yield']:.2f}%")
                
                # Price chart
                st.subheader("Price Chart (1 Year)")
                data = analyzer.get_stock_data(research_symbol, "1y")
                
                if not data.empty:
                    fig = go.Figure()
                    fig.add_trace(go.Candlestick(
                        x=data.index,
                        open=data['Open'],
                        high=data['High'],
                        low=data['Low'],
                        close=data['Close'],
                        name=research_symbol
                    ))
                    fig.update_layout(
                        title=f"{research_symbol} Stock Price",
                        yaxis_title="Price ($)",
                        xaxis_title="Date"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Volume chart
                st.subheader("Trading Volume")
                fig_volume = px.bar(x=data.index[-30:], y=data['Volume'][-30:], 
                                  title="Trading Volume (Last 30 Days)")
                fig_volume.update_layout(xaxis_title="Date", yaxis_title="Volume")
                st.plotly_chart(fig_volume, use_container_width=True)

if __name__ == "__main__":
    main()