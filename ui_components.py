"""
UI Components module for Streamlit interface elements
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict
from config import DEFAULT_STOCKS


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
    """Render the Portfolio Analysis tab with modern, stylish UI"""
    
    # Modern header with gradient background effect
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    ">
        <h1 style="
            color: white;
            text-align: center;
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        ">💼 Portfolio Analysis</h1>
        <p style="
            color: rgba(255,255,255,0.9);
            text-align: center;
            margin: 0.5rem 0 0 0;
            font-size: 1.1rem;
        ">Track your investments and analyze performance</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Modern control bar with glassmorphism effect
    st.markdown("""
    <div style="
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    ">
    """, unsafe_allow_html=True)
    
    # Control buttons in a modern layout
    col1, col2, col3, col4, col5, col6 = st.columns([2, 1, 1, 1, 1, 1])
    
    with col1:
        st.markdown("""
        <h3 style="
            color: #2c3e50;
            margin: 0;
            font-weight: 600;
        ">📊 Portfolio Dashboard</h3>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("🔄 Refresh", 
                    help="Refresh portfolio data from Robinhood",
                    key="refresh_portfolio"):
            st.rerun()
    
    with col3:
        if st.session_state.get('logged_in', False):
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 25px;
                text-align: center;
                font-weight: 600;
                box-shadow: 0 4px 15px rgba(0,184,148,0.3);
            ">
                ✅ Connected
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #e17055 0%, #d63031 100%);
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 25px;
                text-align: center;
                font-weight: 600;
                box-shadow: 0 4px 15px rgba(225,112,85,0.3);
            ">
                ❌ Disconnected
            </div>
            """, unsafe_allow_html=True)
    
    with col4:
        if st.session_state.get('logged_in', False):
            if st.button("🧪 Test API", 
                        help="Test Robinhood connection and show available data",
                        key="test_api"):
                test_results = rh_integration.test_robinhood_connection()
                st.write("**Connection Test Results:**", test_results)
    
    with col5:
        if st.session_state.get('logged_in', False):
            if st.button("📈 Export", 
                        help="Export portfolio data",
                        key="export_data"):
                st.info("Export functionality coming soon!")
    
    with col6:
        # Privacy toggle for hiding dollar amounts
        privacy_mode = st.checkbox(
            "🔒 Hide Amounts", 
            value=st.session_state.get('privacy_mode', False),
            help="Hide actual dollar amounts while keeping growth percentages visible",
            key="privacy_toggle"
        )
        st.session_state['privacy_mode'] = privacy_mode
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Privacy mode indicator
    if privacy_mode:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 15px;
            margin-bottom: 1rem;
            box-shadow: 0 4px 20px rgba(255,107,107,0.3);
            text-align: center;
        ">
            <strong>🔒 Privacy Mode Active:</strong> Dollar amounts are hidden for security. 
            Growth percentages and relative performance remain visible.
        </div>
        """, unsafe_allow_html=True)
    
    if st.session_state.get('logged_in', False):
        # Get portfolio data
        try:
            portfolio_summary = rh_integration.get_detailed_portfolio_summary()
            portfolio = rh_integration.get_portfolio()
        except Exception as e:
            st.error(f"Error fetching portfolio data: {e}")
            portfolio_summary = {}
            portfolio = []
        
        # Account Overview Cards with modern design
        if portfolio_summary and isinstance(portfolio_summary, dict):
            st.markdown("""
            <h2 style="
                color: #2c3e50;
                margin: 2rem 0 1rem 0;
                font-weight: 600;
                font-size: 1.8rem;
            ">📊 Account Overview</h2>
            """, unsafe_allow_html=True)
            
            # Modern metric cards
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                portfolio_value = portfolio_summary.get('total_portfolio_value', 0)
                display_value = "***" if privacy_mode else f"${portfolio_value:,.0f}"
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 1.5rem;
                    border-radius: 15px;
                    text-align: center;
                    box-shadow: 0 8px 25px rgba(102,126,234,0.3);
                    margin-bottom: 1rem;
                ">
                    <h3 style="margin: 0 0 0.5rem 0; font-size: 0.9rem; opacity: 0.9;">Portfolio Value</h3>
                    <h2 style="margin: 0; font-size: 1.8rem; font-weight: 700;">{display_value}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                buying_power = portfolio_summary.get('buying_power', 0)
                display_value = "***" if privacy_mode else f"${buying_power:,.0f}"
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    color: white;
                    padding: 1.5rem;
                    border-radius: 15px;
                    text-align: center;
                    box-shadow: 0 8px 25px rgba(240,147,251,0.3);
                    margin-bottom: 1rem;
                ">
                    <h3 style="margin: 0 0 0.5rem 0; font-size: 0.9rem; opacity: 0.9;">Buying Power</h3>
                    <h2 style="margin: 0; font-size: 1.8rem; font-weight: 700;">{display_value}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                cash_balance = portfolio_summary.get('cash_balance', 0)
                display_value = "***" if privacy_mode else f"${cash_balance:,.0f}"
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                    color: white;
                    padding: 1.5rem;
                    border-radius: 15px;
                    text-align: center;
                    box-shadow: 0 8px 25px rgba(79,172,254,0.3);
                    margin-bottom: 1rem;
                ">
                    <h3 style="margin: 0 0 0.5rem 0; font-size: 0.9rem; opacity: 0.9;">Cash Balance</h3>
                    <h2 style="margin: 0; font-size: 1.8rem; font-weight: 700;">{display_value}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                total_account = portfolio_summary.get('total_account_value', 0)
                display_value = "***" if privacy_mode else f"${total_account:,.0f}"
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
                    color: white;
                    padding: 1.5rem;
                    border-radius: 15px;
                    text-align: center;
                    box-shadow: 0 8px 25px rgba(67,233,123,0.3);
                    margin-bottom: 1rem;
                ">
                    <h3 style="margin: 0 0 0.5rem 0; font-size: 0.9rem; opacity: 0.9;">Total Account</h3>
                    <h2 style="margin: 0; font-size: 1.8rem; font-weight: 700;">{display_value}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            # Account details in a modern info card
            account_number = portfolio_summary.get('account_number', 'N/A')
            account_type = portfolio_summary.get('account_type', 'N/A')
            last_updated = portfolio_summary.get('last_updated', 'N/A')
            if account_number != 'N/A' and account_number != 'Error':
                st.markdown(f"""
                <div style="
                    background: #f8f9fa;
                    padding: 1rem 1.5rem;
                    border-radius: 10px;
                    border-left: 4px solid #28a745;
                    margin-bottom: 2rem;
                ">
                    <p style="margin: 0; color: #6c757d; font-size: 0.9rem;">
                        <strong>Account:</strong> {account_number} | 
                        <strong>Type:</strong> {account_type} | 
                        <strong>Last Updated:</strong> {last_updated}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        # Portfolio Performance Section
        if portfolio and 'total_gain_loss' in portfolio_summary:
            st.markdown("""
            <h2 style="
                color: #2c3e50;
                margin: 2rem 0 1rem 0;
                font-weight: 600;
                font-size: 1.8rem;
            ">📈 Portfolio Performance</h2>
            """, unsafe_allow_html=True)
            
            # Performance metrics in modern cards
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_cost = portfolio_summary.get('total_cost_basis', 0)
                display_value = "***" if privacy_mode else f"${total_cost:,.0f}"
                st.markdown(f"""
                <div style="
                    background: #fff;
                    padding: 1.5rem;
                    border-radius: 15px;
                    text-align: center;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                    border: 1px solid #e9ecef;
                ">
                    <h3 style="margin: 0 0 0.5rem 0; font-size: 0.9rem; color: #6c757d;">Total Cost Basis</h3>
                    <h2 style="margin: 0; font-size: 1.6rem; font-weight: 700; color: #495057;">{display_value}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                total_current = portfolio_summary.get('total_current_value', 0)
                display_value = "***" if privacy_mode else f"${total_current:,.0f}"
                st.markdown(f"""
                <div style="
                    background: #fff;
                    padding: 1.5rem;
                    border-radius: 15px;
                    text-align: center;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                    border: 1px solid #e9ecef;
                ">
                    <h3 style="margin: 0 0 0.5rem 0; font-size: 0.9rem; color: #6c757d;">Current Value</h3>
                    <h2 style="margin: 0; font-size: 1.6rem; font-weight: 700; color: #495057;">{display_value}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                total_gain_loss = portfolio_summary.get('total_gain_loss', 0)
                gain_loss_color = "#28a745" if total_gain_loss >= 0 else "#dc3545"
                gain_loss_icon = "📈" if total_gain_loss >= 0 else "📉"
                display_value = "***" if privacy_mode else f"${total_gain_loss:,.0f}"
                st.markdown(f"""
                <div style="
                    background: #fff;
                    padding: 1.5rem;
                    border-radius: 15px;
                    text-align: center;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                    border: 1px solid #e9ecef;
                ">
                    <h3 style="margin: 0 0 0.5rem 0; font-size: 0.9rem; color: #6c757d;">{gain_loss_icon} Total Gain/Loss</h3>
                    <h2 style="margin: 0; font-size: 1.6rem; font-weight: 700; color: {gain_loss_color};">{display_value}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                total_return = portfolio_summary.get('total_return_percent', 0)
                return_color = "#28a745" if total_return >= 0 else "#dc3545"
                return_icon = "🚀" if total_return >= 0 else "⚠️"
                st.markdown(f"""
                <div style="
                    background: #fff;
                    padding: 1.5rem;
                    border-radius: 15px;
                    text-align: center;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                    border: 1px solid #e9ecef;
                ">
                    <h3 style="margin: 0 0 0.5rem 0; font-size: 0.9rem; color: #6c757d;">{return_icon} Total Return</h3>
                    <h2 style="margin: 0; font-size: 1.6rem; font-weight: 700; color: {return_color};">{total_return:.2f}%</h2>
                </div>
                """, unsafe_allow_html=True)
            
            # Best and worst performers in modern cards
            best_performer = portfolio_summary.get('best_performer')
            worst_performer = portfolio_summary.get('worst_performer')
            if best_performer and worst_performer:
                col1, col2 = st.columns(2)
                with col1:
                    best = best_performer
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
                        color: white;
                        padding: 1.5rem;
                        border-radius: 15px;
                        text-align: center;
                        box-shadow: 0 8px 25px rgba(0,184,148,0.3);
                        margin-bottom: 1rem;
                    ">
                        <h3 style="margin: 0 0 0.5rem 0; font-size: 1rem; opacity: 0.9;">🏆 Best Performer</h3>
                        <h2 style="margin: 0; font-size: 1.5rem; font-weight: 700;">{best['symbol']}</h2>
                        <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; font-weight: 600;">+{best['gain_loss_percent']:.2f}%</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    worst = worst_performer
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #e17055 0%, #d63031 100%);
                        color: white;
                        padding: 1.5rem;
                        border-radius: 15px;
                        text-align: center;
                        box-shadow: 0 8px 25px rgba(225,112,85,0.3);
                        margin-bottom: 1rem;
                    ">
                        <h3 style="margin: 0 0 0.5rem 0; font-size: 1rem; opacity: 0.9;">📉 Worst Performer</h3>
                        <h2 style="margin: 0; font-size: 1.5rem; font-weight: 700;">{worst['symbol']}</h2>
                        <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; font-weight: 600;">{worst['gain_loss_percent']:.2f}%</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Render portfolio details with modern styling and privacy mode
            render_portfolio_details(portfolio, privacy_mode)
        else:
            st.info("No open positions found in your portfolio.")
            
        # Fallback: Try to get basic account info if detailed summary failed
        if not portfolio_summary or not isinstance(portfolio_summary, dict):
            st.warning("⚠️ Detailed portfolio summary unavailable. Trying basic account info...")
            try:
                basic_account = rh_integration.get_account_info()
                if basic_account:
                    st.subheader("📊 Basic Account Information")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        value = basic_account.get('total_portfolio_value', 0)
                        display_value = "***" if privacy_mode else f"${value:,.2f}"
                        st.metric("Portfolio Value", display_value)
                    with col2:
                        value = basic_account.get('buying_power', 0)
                        display_value = "***" if privacy_mode else f"${value:,.2f}"
                        st.metric("Buying Power", display_value)
                    with col3:
                        value = basic_account.get('total_account_value', 0)
                        display_value = "***" if privacy_mode else f"${value:,.2f}"
                        st.metric("Total Account", display_value)
            except Exception as e:
                st.error(f"Could not fetch basic account info: {e}")
    
    else:
        # Modern demo portfolio section for non-logged in users
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 2rem;
            border-radius: 20px;
            text-align: center;
            margin: 2rem 0;
            box-shadow: 0 8px 32px rgba(240,147,251,0.3);
        ">
            <h2 style="margin: 0 0 1rem 0; font-size: 2rem;">💡 Demo Mode</h2>
            <p style="margin: 0; font-size: 1.1rem; opacity: 0.9;">
                Login to Robinhood to see your real portfolio, or explore the demo below
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        render_demo_portfolio()


def render_portfolio_details(portfolio, privacy_mode):
    """Render detailed portfolio information with modern styling"""
    # Validate portfolio data first
    is_valid, validation_message = validate_portfolio_data(portfolio)
    
    if not is_valid:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            margin: 2rem 0;
            box-shadow: 0 8px 25px rgba(255,107,107,0.3);
        ">
            <h3 style="margin: 0 0 0.5rem 0;">⚠️ Data Validation Error</h3>
            <p style="margin: 0; opacity: 0.9;">{validation_message}</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Convert to DataFrame for easier manipulation
    df_portfolio = pd.DataFrame(portfolio)
    
    # Portfolio Allocation Pie Chart
    st.markdown("""
    <h2 style="
        color: #2c3e50;
        margin: 2rem 0 1rem 0;
        font-weight: 600;
        font-size: 1.8rem;
    ">🥧 Portfolio Allocation by Value</h2>
    """, unsafe_allow_html=True)
    
    try:
        # Filter for positive values and prepare data for pie chart
        df_filtered = df_portfolio[df_portfolio['current_value'] > 0].copy()
        
        if not df_filtered.empty:
            # Aggregate small positions into 'Others'
            total_value = df_filtered['current_value'].sum()
            df_filtered['percentage'] = (df_filtered['current_value'] / total_value) * 100
            
            # Define the threshold for 'Others'
            threshold = 4.0
            
            # Separate main positions from small ones
            df_main = df_filtered[df_filtered['percentage'] >= threshold]
            df_others = df_filtered[df_filtered['percentage'] < threshold]
            
            # Create the final DataFrame for the pie chart
            if not df_others.empty:
                others_sum = df_others['current_value'].sum()
                others_row = pd.DataFrame([{
                    'symbol': 'Others', 
                    'current_value': others_sum,
                    'quantity': df_others['quantity'].sum(),
                    'total_cost': df_others['total_cost'].sum(),
                    'gain_loss_percent': (others_sum / df_others['total_cost'].sum() - 1) * 100 if df_others['total_cost'].sum() > 0 else 0
                }])
                df_pie = pd.concat([df_main, others_row], ignore_index=True)
            else:
                df_pie = df_main
            
            # Create modern pie chart
            fig = px.pie(
                df_pie, 
                values='current_value', 
                names='symbol',
                hole=0.4,  # Donut chart
                hover_data=['quantity', 'total_cost', 'gain_loss_percent'],
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            
            # Update layout for modern look
            fig.update_traces(
                textposition='inside',
                texttemplate='%{percent:.1%}',
                hovertemplate="<b>%{label}</b><br>" +
                            "Value: $%{value:,.0f}<br>" +
                            "Quantity: %{customdata[0]:,.0f}<br>" +
                            "Cost: $%{customdata[1]:,.0f}<br>" +
                            "Return: %{customdata[2]:.2f}%<extra></extra>"
            )
            
            fig.update_layout(
                title={
                    'text': "DEBUG: Portfolio Allocation Distribution",
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 18, 'color': '#2c3e50'}
                },
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="top",
                    y=0.9,
                    xanchor="left",
                    x=1.02
                ),
                margin=dict(l=20, r=20, t=40, b=20),
                height=500
            )
            
            # Display the chart
            st.plotly_chart(fig, use_container_width=True)
            
            # Allocation summary table below chart
            st.markdown("""
            <div style="
                background: #f8f9fa;
                padding: 1.5rem;
                border-radius: 15px;
                margin: 1rem 0;
                border-left: 4px solid #007bff;
            ">
                <h4 style="margin: 0 0 1rem 0; color: #2c3e50;">📊 Allocation Summary</h4>
            """, unsafe_allow_html=True)
            
            # Calculate and display allocation percentages using the grouped data from the pie chart
            total_value_summary = df_pie['current_value'].sum()
            allocation_data = []
            
            # Sort for presentation
            df_pie_sorted = df_pie.sort_values(by='current_value', ascending=False)

            for _, row in df_pie_sorted.iterrows():
                percentage = (row['current_value'] / total_value_summary) * 100
                display_value = "***" if privacy_mode else f"${row['current_value']:,.0f}"
                
                allocation_data.append({
                    'Symbol': row['symbol'],
                    'Value': display_value,
                    'Percentage': f"{percentage:.1f}%",
                    'Return': f"{row['gain_loss_percent']:.2f}%"
                })
            
            allocation_df = pd.DataFrame(allocation_data)
            st.dataframe(
                allocation_df,
                use_container_width=True,
                hide_index=True
            )
            
            st.markdown("</div>", unsafe_allow_html=True)
            
        else:
            st.warning("No valid portfolio data available for chart visualization.")
            
    except Exception as e:
        st.error(f"Error creating portfolio allocation chart: {e}")
        st.write("Debug: Portfolio data structure:", type(portfolio))
        if portfolio:
            st.write("First position keys:", list(portfolio[0].keys()) if portfolio[0] else "None")
    
    # Portfolio Performance Chart
    st.markdown("""
    <h2 style="
        color: #2c3e50;
        margin: 2rem 0 1rem 0;
        font-weight: 600;
        font-size: 1.8rem;
    ">📈 Individual Stock Performance</h2>
    """, unsafe_allow_html=True)
    
    try:
        if not df_portfolio.empty:
            # Create performance bar chart
            fig = go.Figure()
            
            # Add bars for gain/loss
            colors = ['#28a745' if x >= 0 else '#dc3545' for x in df_portfolio['gain_loss_percent']]
            
            fig.add_trace(go.Bar(
                x=df_portfolio['symbol'],
                y=df_portfolio['gain_loss_percent'],
                marker_color=colors,
                hovertemplate="<b>%{x}</b><br>" +
                            "Gain/Loss: %{y:.2f}%<br>" +
                            "Value: $" + df_portfolio['current_value'].astype(str) + "<br>" +
                            "Quantity: " + df_portfolio['quantity'].astype(str) + "<extra></extra>",
                name="Performance"
            ))
            
            # Update layout
            fig.update_layout(
                title={
                    'text': "Stock Performance Overview",
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 18, 'color': '#2c3e50'}
                },
                xaxis_title="Stock Symbol",
                yaxis_title="Gain/Loss (%)",
                showlegend=False,
                height=400,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            
            # Add horizontal line at 0%
            fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
            
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.warning("No portfolio data available for performance chart.")
            
    except Exception as e:
        st.error(f"Error creating performance chart: {e}")
    
    # Detailed Portfolio Table
    st.markdown("""
    <h2 style="
        color: #2c3e50;
        margin: 2rem 0 1rem 0;
        font-weight: 600;
        font-size: 1.8rem;
    ">📋 Detailed Holdings</h2>
    """, unsafe_allow_html=True)
    
    try:
        if not df_portfolio.empty:
            # Format the data for display
            display_df = df_portfolio.copy()
            display_df['current_value'] = display_df['current_value'].apply(lambda x: "***" if privacy_mode else f"${x:,.2f}")
            display_df['total_cost'] = display_df['total_cost'].apply(lambda x: "***" if privacy_mode else f"${x:,.2f}")
            display_df['gain_loss'] = display_df['gain_loss'].apply(lambda x: "***" if privacy_mode else f"${x:,.2f}")
            display_df['gain_loss_percent'] = display_df['gain_loss_percent'].apply(lambda x: f"{x:.2f}%")
            
            # Rename columns for better display
            display_df = display_df.rename(columns={
                'symbol': 'Symbol',
                'current_value': 'Current Value',
                'total_cost': 'Cost Basis',
                'gain_loss': 'Gain/Loss ($)',
                'gain_loss_percent': 'Gain/Loss (%)'
            })
            
            # Display in a modern styled table
            st.markdown("""
            <div style="
                background: white;
                padding: 1.5rem;
                border-radius: 15px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                border: 1px solid #e9ecef;
            ">
            """, unsafe_allow_html=True)
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
            
            st.markdown("</div>", unsafe_allow_html=True)
            
        else:
            st.info("No portfolio data available for detailed table.")
            
    except Exception as e:
        st.error(f"Error creating detailed portfolio table: {e}")


def render_demo_portfolio():
    """Render a demo portfolio with modern styling"""
    # Check if privacy mode is active
    privacy_mode = st.session_state.get('privacy_mode', False)
    
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 2rem;
        border-radius: 20px;
        margin: 2rem 0;
        box-shadow: 0 8px 32px rgba(168,237,234,0.3);
    ">
        <h2 style="
            color: #2c3e50;
            margin: 0 0 1rem 0;
            text-align: center;
            font-weight: 600;
        ">🎯 Sample Portfolio Analysis</h2>
        <p style="
            color: #34495e;
            margin: 0;
            text-align: center;
            font-size: 1.1rem;
        ">This is a demonstration of what your portfolio analysis will look like after connecting to Robinhood</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Demo portfolio data
    demo_portfolio = [
        {
            'symbol': 'AMD', 
            'quantity': 50, 
            'current_value': 10000.00, 
            'total_cost': 8000.00, 
            'gain_loss': 2000.00, 
            'gain_loss_percent': 25.00
        },
        {
            'symbol': 'NVDA', 
            'quantity': 20, 
            'current_value': 20000.00, 
            'total_cost': 15000.00, 
            'gain_loss': 5000.00, 
            'gain_loss_percent': 33.33
        },
        {
            'symbol': 'INTC', 
            'quantity': 200, 
            'current_value': 5000.00, 
            'total_cost': 6000.00, 
            'gain_loss': -1000.00, 
            'gain_loss_percent': -16.67
        }
    ]
    
    # Demo metrics
    total_value = sum(pos['current_value'] for pos in demo_portfolio)
    total_cost = sum(pos['total_cost'] for pos in demo_portfolio)
    total_gain_loss = sum(pos['gain_loss'] for pos in demo_portfolio)
    total_return = (total_gain_loss / total_cost) * 100 if total_cost > 0 else 0
    
    # Demo metrics display
    st.markdown("""
    <h3 style="
        color: #2c3e50;
        margin: 2rem 0 1rem 0;
        font-weight: 600;
        font-size: 1.5rem;
    ">📊 Demo Portfolio Metrics</h3>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        display_value = "***" if privacy_mode else f"${total_value:,.0f}"
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 8px 25px rgba(102,126,234,0.3);
            margin-bottom: 1rem;
        ">
            <h3 style="margin: 0 0 0.5rem 0; font-size: 0.9rem; opacity: 0.9;">Total Value</h3>
            <h2 style="margin: 0; font-size: 1.6rem; font-weight: 700;">{display_value}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        display_value = "***" if privacy_mode else f"${total_cost:,.0f}"
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 8px 25px rgba(79,172,254,0.3);
            margin-bottom: 1rem;
        ">
            <h3 style="margin: 0 0 0.5rem 0; font-size: 0.9rem; opacity: 0.9;">Total Cost</h3>
            <h2 style="margin: 0; font-size: 1.6rem; font-weight: 700;">{display_value}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        gain_loss_color = "#28a745" if total_gain_loss >= 0 else "#dc3545"
        gain_loss_icon = "📈" if total_gain_loss >= 0 else "📉"
        display_value = "***" if privacy_mode else f"${total_gain_loss:,.0f}"
        st.markdown(f"""
        <div style="
            background: #fff;
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            border: 1px solid #e9ecef;
            margin-bottom: 1rem;
        ">
            <h3 style="margin: 0 0 0.5rem 0; font-size: 0.9rem; color: #6c757d;">{gain_loss_icon} Total Gain/Loss</h3>
            <h2 style="margin: 0; font-size: 1.6rem; font-weight: 700; color: {gain_loss_color};">{display_value}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        return_color = "#28a745" if total_return >= 0 else "#dc3545"
        return_icon = "🚀" if total_return >= 0 else "⚠️"
        st.markdown(f"""
        <div style="
            background: #fff;
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            border: 1px solid #e9ecef;
            margin-bottom: 1rem;
        ">
            <h3 style="margin: 0 0 0.5rem 0; font-size: 0.9rem; color: #6c757d;">{return_icon} Total Return</h3>
            <h2 style="margin: 0; font-size: 1.6rem; font-weight: 700; color: {return_color};">{total_return:.2f}%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Demo portfolio details
    render_portfolio_details(demo_portfolio, privacy_mode)


def render_buy_opportunities(analyzer, rh_integration, drop_threshold, investment_amount):
    """Render the Buy Opportunities tab"""
    st.header("🎯 Buy Opportunities")
    
    # Stock symbols to analyze
    default_stocks = DEFAULT_STOCKS.copy()
    
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
        import time
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


def render_stock_research(analyzer):
    """Render the Stock Research tab"""
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
