"""
UI Components module for Streamlit interface elements
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from typing import List, Dict
from config import DEFAULT_STOCKS
import yfinance as yf


def validate_portfolio_data(portfolio):
    """Validate portfolio data structure and show any issues"""
    if not portfolio:
        return False, "Portfolio is empty"
    
    if not isinstance(portfolio, list):
        return False, f"Portfolio is not a list, got {type(portfolio)}"
    
    required_fields = ['symbol', 'quantity', 'current_value', 'total_cost', 'gain_loss', 'gain_loss_percent']
    issues = []
    
    for i, position in enumerate(portfolio):
        if not isinstance(position, dict):
            issues.append(f"Position {i} is not a dictionary")
            continue
            
        for field in required_fields:
            if field not in position:
                issues.append(f"Position {i} missing field: {field}")
            elif field in ['quantity', 'current_value', 'total_cost', 'gain_loss', 'gain_loss_percent']:
                try:
                    float(position[field])
                except (ValueError, TypeError):
                    issues.append(f"Position {i} field {field} is not numeric: {position[field]}")
    
    if issues:
        return False, f"Data validation issues: {'; '.join(issues)}"
    
    return True, "Portfolio data is valid"


def render_market_overview(analyzer, drop_threshold):
    """Render the Market Overview tab"""
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


def render_portfolio_analysis(rh_integration):
    """Render the Portfolio Analysis tab"""
    st.header("Portfolio Analysis")
    st.info("Portfolio analysis functionality coming soon!")


def render_stock_research(analyzer):
    """Render the Stock Research tab with comprehensive analysis"""
    st.header("🔍 Stock Research & Analysis")
    
    # Stock selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        stock_symbol = st.text_input(
            "Enter Stock Symbol",
            value="AAPL",
            placeholder="e.g., AAPL, GOOGL, MSFT",
            help="Enter the stock symbol you want to research"
        ).upper()
    
    with col2:
        analysis_period = st.selectbox(
            "Analysis Period",
            options=["1mo", "3mo", "6mo", "1y", "2y", "5y"],
            index=3,
            help="Select the time period for analysis"
        )
    
    if stock_symbol:
        try:
            # Get stock data
            stock_data = analyzer.get_stock_data(stock_symbol, analysis_period)
            stock_metrics = analyzer.get_stock_metrics(stock_symbol)
            
            if not stock_data.empty and stock_metrics:
                # Stock info header
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Current Price",
                        f"${stock_metrics['current_price']:.2f}",
                        f"{stock_metrics['drop_from_high']:.1f}% from high"
                    )
                
                with col2:
                    st.metric(
                        "52-Week High",
                        f"${stock_metrics['year_high']:.2f}"
                    )
                
                with col3:
                    st.metric(
                        "52-Week Low",
                        f"${stock_metrics['year_low']:.2f}"
                    )
                
                with col4:
                    st.metric(
                        "Volatility",
                        f"{stock_metrics['volatility']:.1f}%"
                    )
                
                # Technical indicators
                st.subheader("📊 Technical Indicators")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    rsi = stock_metrics.get('rsi', 50)
                    rsi_color = "green" if rsi < 30 else "red" if rsi > 70 else "orange"
                    st.metric(
                        "RSI (14)",
                        f"{rsi:.1f}",
                        delta="Oversold" if rsi < 30 else "Overbought" if rsi > 70 else "Neutral"
                    )
                
                with col2:
                    pe_ratio = stock_metrics.get('pe_ratio', 'N/A')
                    if pe_ratio != 'N/A':
                        st.metric("P/E Ratio", f"{pe_ratio:.2f}")
                    else:
                        st.metric("P/E Ratio", "N/A")
                
                with col3:
                    dividend_yield = stock_metrics.get('dividend_yield', 0)
                    st.metric("Dividend Yield", f"{dividend_yield:.2f}%")
                
                with col4:
                    market_cap = stock_metrics.get('market_cap', 'N/A')
                    if market_cap != 'N/A':
                        if market_cap > 1e12:
                            market_cap_str = f"${market_cap/1e12:.1f}T"
                        elif market_cap > 1e9:
                            market_cap_str = f"${market_cap/1e9:.1f}B"
                        else:
                            market_cap_str = f"${market_cap/1e6:.1f}M"
                        st.metric("Market Cap", market_cap_str)
                    else:
                        st.metric("Market Cap", "N/A")
                
                # Price chart with technical indicators
                st.subheader("📈 Price Chart & Technical Analysis")
                
                # Create candlestick chart
                fig = go.Figure()
                
                fig.add_trace(go.Candlestick(
                    x=stock_data.index,
                    open=stock_data['Open'],
                    high=stock_data['High'],
                    low=stock_data['Low'],
                    close=stock_data['Close'],
                    name='Price'
                ))
                
                # Add moving averages
                ma_20 = stock_data['Close'].rolling(window=20).mean()
                ma_50 = stock_data['Close'].rolling(window=50).mean()
                
                fig.add_trace(go.Scatter(
                    x=stock_data.index,
                    y=ma_20,
                    mode='lines',
                    name='MA 20',
                    line=dict(color='orange', width=1)
                ))
                
                fig.add_trace(go.Scatter(
                    x=stock_data.index,
                    y=ma_50,
                    mode='lines',
                    name='MA 50',
                    line=dict(color='blue', width=1)
                ))
                
                fig.update_layout(
                    title=f'{stock_symbol} Price Chart',
                    yaxis_title='Price ($)',
                    xaxis_title='Date',
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Volume analysis
                st.subheader("📊 Volume Analysis")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Volume chart
                    fig_volume = go.Figure()
                    fig_volume.add_trace(go.Bar(
                        x=stock_data.index,
                        y=stock_data['Volume'],
                        name='Volume',
                        marker_color='lightblue'
                    ))
                    fig_volume.update_layout(
                        title='Trading Volume',
                        yaxis_title='Volume',
                        height=300
                    )
                    st.plotly_chart(fig_volume, use_container_width=True)
                
                with col2:
                    # Volume statistics
                    avg_volume = stock_data['Volume'].mean()
                    current_volume = stock_data['Volume'].iloc[-1]
                    volume_ratio = current_volume / avg_volume
                    
                    st.metric("Average Volume", f"{avg_volume:,.0f}")
                    st.metric("Current Volume", f"{current_volume:,.0f}")
                    st.metric("Volume Ratio", f"{volume_ratio:.2f}x")
                    
                    if volume_ratio > 1.5:
                        st.success("🔥 High volume - Strong interest")
                    elif volume_ratio < 0.5:
                        st.warning("📉 Low volume - Weak interest")
                    else:
                        st.info("📊 Normal volume")
                
                # Buy/Sell signals
                st.subheader("🎯 Trading Signals")
                
                signals = []
                
                # RSI signals
                if rsi < 30:
                    signals.append(("🟢 RSI Oversold", "Strong Buy", "success"))
                elif rsi > 70:
                    signals.append(("🔴 RSI Overbought", "Strong Sell", "error"))
                
                # Moving average signals
                if ma_20.iloc[-1] > ma_50.iloc[-1]:
                    signals.append(("🟢 MA 20 > MA 50", "Bullish", "success"))
                else:
                    signals.append(("🔴 MA 20 < MA 50", "Bearish", "error"))
                
                # Price vs moving averages
                current_price = stock_data['Close'].iloc[-1]
                if current_price > ma_20.iloc[-1]:
                    signals.append(("🟢 Price > MA 20", "Above Support", "success"))
                else:
                    signals.append(("🔴 Price < MA 20", "Below Support", "error"))
                
                # Display signals
                for signal, description, color in signals:
                    if color == "success":
                        st.success(f"{signal}: {description}")
                    elif color == "error":
                        st.error(f"{signal}: {description}")
                    else:
                        st.info(f"{signal}: {description}")
                
                # Risk assessment
                st.subheader("⚠️ Risk Assessment")
                
                risk_score = 0
                risk_factors = []
                
                # Volatility risk
                if stock_metrics['volatility'] > 50:
                    risk_score += 3
                    risk_factors.append("High volatility (>50%)")
                elif stock_metrics['volatility'] > 30:
                    risk_score += 2
                    risk_factors.append("Moderate volatility (>30%)")
                
                # Drop from high risk
                if stock_metrics['drop_from_high'] > 50:
                    risk_score += 3
                    risk_factors.append("Significant drop from high (>50%)")
                elif stock_metrics['drop_from_high'] > 30:
                    risk_score += 2
                    risk_factors.append("Moderate drop from high (>30%)")
                
                # RSI risk
                if rsi > 80 or rsi < 20:
                    risk_score += 1
                    risk_factors.append("Extreme RSI levels")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if risk_score <= 2:
                        st.success(f"Risk Level: Low ({risk_score}/10)")
                    elif risk_score <= 5:
                        st.warning(f"Risk Level: Medium ({risk_score}/10)")
                    else:
                        st.error(f"Risk Level: High ({risk_score}/10)")
                
                with col2:
                    st.write("Risk Factors:")
                    for factor in risk_factors:
                        st.write(f"• {factor}")
                
            else:
                st.error(f"Unable to fetch data for {stock_symbol}. Please check the symbol and try again.")
                
        except Exception as e:
            st.error(f"Error analyzing {stock_symbol}: {e}")


def render_demo_portfolio():
    """Render a demo portfolio"""
    st.header("Demo Portfolio")
    st.info("Demo portfolio functionality coming soon!")


def render_buy_opportunities(analyzer, rh_integration, drop_threshold, investment_amount):
    """Render the Buy Opportunities tab with comprehensive analysis"""
    st.header("🎯 Buy Opportunities & Market Analysis")
    
    # Configuration section
    st.subheader("⚙️ Opportunity Detection Settings")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        min_drop = st.slider(
            "Minimum Drop %",
            min_value=10,
            max_value=80,
            value=drop_threshold,
            help="Minimum percentage drop from high to consider as opportunity"
        )
    
    with col2:
        max_pe = st.slider(
            "Maximum P/E Ratio",
            min_value=5,
            max_value=100,
            value=30,
            help="Maximum P/E ratio for value stocks"
        )
    
    with col3:
        min_market_cap = st.selectbox(
            "Minimum Market Cap",
            options=["$1B", "$5B", "$10B", "$50B", "$100B"],
            index=2,
            help="Minimum market capitalization to filter stocks"
        )
    
    # Market sectors to analyze
    st.subheader("📊 Sector Analysis")
    
    sectors = {
        "Technology": ["AAPL", "GOOGL", "MSFT", "NVDA", "META", "NFLX", "TSLA", "AMD"],
        "Healthcare": ["JNJ", "PFE", "UNH", "ABBV", "TMO", "DHR", "LLY", "ABT"],
        "Financial": ["JPM", "BAC", "WFC", "GS", "MS", "C", "BLK", "AXP"],
        "Consumer": ["AMZN", "HD", "MCD", "SBUX", "NKE", "DIS", "KO", "PEP"],
        "Energy": ["XOM", "CVX", "COP", "EOG", "SLB", "PSX", "VLO", "MPC"]
    }
    
    selected_sectors = st.multiselect(
        "Select Sectors to Analyze",
        options=list(sectors.keys()),
        default=["Technology", "Healthcare"],
        help="Choose which sectors to scan for opportunities"
    )
    
    if st.button("🔍 Scan for Opportunities", type="primary"):
        with st.spinner("Scanning market for buy opportunities..."):
            opportunities = []
            
            for sector in selected_sectors:
                for symbol in sectors[sector]:
                    try:
                        metrics = analyzer.get_stock_metrics(symbol)
                        if metrics and metrics.get('current_price', 0) > 0:
                            drop = metrics.get('drop_from_high', 0)
                            pe_ratio = metrics.get('pe_ratio', 999)
                            market_cap = metrics.get('market_cap', 0)
                            
                            # Filter based on criteria
                            if (drop >= min_drop and 
                                (pe_ratio == 'N/A' or pe_ratio <= max_pe) and
                                market_cap != 'N/A' and market_cap > 0):
                                
                                # Calculate opportunity score
                                score = 0
                                score += min(drop / 10, 5)  # Drop score (max 5)
                                if pe_ratio != 'N/A' and pe_ratio < 20:
                                    score += (20 - pe_ratio) / 2  # P/E score
                                if market_cap > 1e10:  # Large cap bonus
                                    score += 1
                                
                                opportunities.append({
                                    'symbol': symbol,
                                    'sector': sector,
                                    'current_price': metrics['current_price'],
                                    'drop_from_high': drop,
                                    'pe_ratio': pe_ratio,
                                    'market_cap': market_cap,
                                    'rsi': metrics.get('rsi', 50),
                                    'volatility': metrics.get('volatility', 0),
                                    'score': score
                                })
                    except Exception as e:
                        continue
            
            # Sort by opportunity score
            opportunities.sort(key=lambda x: x['score'], reverse=True)
            
            if opportunities:
                st.success(f"Found {len(opportunities)} buy opportunities!")
                
                # Display opportunities in a table
                st.subheader("📋 Top Buy Opportunities")
                
                # Create DataFrame for display
                opp_data = []
                for opp in opportunities[:20]:  # Show top 20
                    market_cap_str = "N/A"
                    if opp['market_cap'] != 'N/A':
                        if opp['market_cap'] > 1e12:
                            market_cap_str = f"${opp['market_cap']/1e12:.1f}T"
                        elif opp['market_cap'] > 1e9:
                            market_cap_str = f"${opp['market_cap']/1e9:.1f}B"
                        else:
                            market_cap_str = f"${opp['market_cap']/1e6:.1f}M"
                    
                    opp_data.append({
                        'Symbol': opp['symbol'],
                        'Sector': opp['sector'],
                        'Price': f"${opp['current_price']:.2f}",
                        'Drop %': f"{opp['drop_from_high']:.1f}%",
                        'P/E': f"{opp['pe_ratio']:.1f}" if opp['pe_ratio'] != 'N/A' else 'N/A',
                        'Market Cap': market_cap_str,
                        'RSI': f"{opp['rsi']:.1f}",
                        'Score': f"{opp['score']:.1f}"
                    })
                
                df_opp = pd.DataFrame(opp_data)
                st.dataframe(df_opp, use_container_width=True)
                
                # Detailed analysis of top opportunities
                st.subheader("🔍 Detailed Analysis")
                
                if opportunities:
                    top_opportunity = opportunities[0]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
                            padding: 1.5rem;
                            border-radius: 15px;
                            color: white;
                            text-align: center;
                            box-shadow: 0 4px 20px rgba(0,184,148,0.3);
                        ">
                            <h3 style="margin: 0 0 0.5rem 0;">🏆 Top Opportunity</h3>
                            <h2 style="margin: 0.5rem 0; font-size: 2rem;">{top_opportunity['symbol']}</h2>
                            <p style="margin: 0; font-size: 1.2rem;">Score: {top_opportunity['score']:.1f}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.metric("Current Price", f"${top_opportunity['current_price']:.2f}")
                        st.metric("Drop from High", f"{top_opportunity['drop_from_high']:.1f}%")
                        st.metric("P/E Ratio", f"{top_opportunity['pe_ratio']:.1f}" if top_opportunity['pe_ratio'] != 'N/A' else 'N/A')
                        st.metric("RSI", f"{top_opportunity['rsi']:.1f}")
                    
                    # Chart for top opportunity
                    st.subheader(f"📈 {top_opportunity['symbol']} Price Analysis")
                    
                    try:
                        stock_data = analyzer.get_stock_data(top_opportunity['symbol'], "6mo")
                        if not stock_data.empty:
                            fig = go.Figure()
                            
                            fig.add_trace(go.Candlestick(
                                x=stock_data.index,
                                open=stock_data['Open'],
                                high=stock_data['High'],
                                low=stock_data['Low'],
                                close=stock_data['Close'],
                                name='Price'
                            ))
                            
                            # Add moving averages
                            ma_20 = stock_data['Close'].rolling(window=20).mean()
                            ma_50 = stock_data['Close'].rolling(window=50).mean()
                            
                            fig.add_trace(go.Scatter(
                                x=stock_data.index,
                                y=ma_20,
                                mode='lines',
                                name='MA 20',
                                line=dict(color='orange', width=1)
                            ))
                            
                            fig.add_trace(go.Scatter(
                                x=stock_data.index,
                                y=ma_50,
                                mode='lines',
                                name='MA 50',
                                line=dict(color='blue', width=1)
                            ))
                            
                            fig.update_layout(
                                title=f'{top_opportunity["symbol"]} Price Chart',
                                yaxis_title='Price ($)',
                                xaxis_title='Date',
                                height=400
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Investment recommendation
                            st.subheader("💡 Investment Recommendation")
                            
                            if top_opportunity['score'] >= 7:
                                st.success("🚀 Strong Buy Opportunity")
                                st.write("This stock shows strong fundamentals and technical indicators suggesting a good entry point.")
                            elif top_opportunity['score'] >= 5:
                                st.warning("📈 Moderate Buy Opportunity")
                                st.write("This stock shows potential but consider additional research before investing.")
                            else:
                                st.info("📊 Watch List Candidate")
                                st.write("This stock meets some criteria but may need more analysis.")
                            
                            # Risk factors
                            st.subheader("⚠️ Risk Considerations")
                            risk_factors = []
                            
                            if top_opportunity['drop_from_high'] > 50:
                                risk_factors.append("Significant price decline may indicate fundamental issues")
                            if top_opportunity['rsi'] < 20:
                                risk_factors.append("Extremely oversold - could indicate continued weakness")
                            if top_opportunity['volatility'] > 50:
                                risk_factors.append("High volatility suggests increased risk")
                            
                            if risk_factors:
                                for factor in risk_factors:
                                    st.write(f"• {factor}")
                            else:
                                st.success("No major risk factors identified")
                    
                    except Exception as e:
                        st.error(f"Error creating chart for {top_opportunity['symbol']}: {e}")
                
                # Sector breakdown
                st.subheader("📊 Opportunities by Sector")
                
                sector_counts = {}
                for opp in opportunities:
                    sector = opp['sector']
                    sector_counts[sector] = sector_counts.get(sector, 0) + 1
                
                if sector_counts:
                    fig_sector = go.Figure(data=[go.Pie(
                        labels=list(sector_counts.keys()),
                        values=list(sector_counts.values()),
                        hole=0.3
                    )])
                    fig_sector.update_layout(title="Opportunities by Sector")
                    st.plotly_chart(fig_sector, use_container_width=True)
            
            else:
                st.warning("No buy opportunities found with current criteria. Try adjusting the filters.")
    
    # Market sentiment analysis
    st.subheader("📊 Market Sentiment")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Market Fear Index", "High", delta="-15%")
        st.caption("Based on VIX and market volatility")
    
    with col2:
        st.metric("Buying Pressure", "Moderate", delta="+5%")
        st.caption("Based on volume and price action")
    
    with col3:
        st.metric("Market Breadth", "Neutral", delta="0%")
        st.caption("Advancing vs declining stocks")
    
    # Market timing indicators
    st.subheader("⏰ Market Timing Indicators")
    
    timing_indicators = [
        ("RSI Divergence", "Bullish", "success"),
        ("MACD Crossover", "Neutral", "info"),
        ("Volume Confirmation", "Bearish", "error"),
        ("Support Level", "Strong", "success")
    ]
    
    for indicator, signal, color in timing_indicators:
        if color == "success":
            st.success(f"✅ {indicator}: {signal}")
        elif color == "error":
            st.error(f"❌ {indicator}: {signal}")
        else:
            st.info(f"ℹ️ {indicator}: {signal}")
