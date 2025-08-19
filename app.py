"""
Main Streamlit application for Portfolio Intelligence Pro
"""

import streamlit as st
import robin_stocks.robinhood as rs
import config
import pandas as pd
import plotly.graph_objects as go
from stock_analyzer import StockAnalyzer
from ui_components import (
    render_market_overview,
    render_stock_research,
    render_demo_portfolio,
    render_buy_opportunities
)


def main():
    """Main Streamlit application"""
    
    # Page configuration MUST be called first, before any other Streamlit commands
    st.set_page_config(
        page_title=config.PAGE_CONFIG['page_title'],
        page_icon=config.PAGE_CONFIG['page_icon'],
        layout=config.PAGE_CONFIG['layout'],
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for modern styling
    st.markdown("""
    <style>
    /* Modern styling for the entire app */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1rem;
    }
    
    /* Custom button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(102,126,234,0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102,126,234,0.4);
    }
    
    /* Custom metric styling */
    .stMetric {
        background: white;
        padding: 1rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #e9ecef;
    }
    
    /* Custom dataframe styling */
    .stDataFrame {
        background: white;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #e9ecef;
    }
    
    /* Custom expander styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        font-weight: 600;
    }
    
    /* Custom sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
    }
    
    /* Custom header styling */
    .css-1v0mbdj {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    /* Custom tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: white;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(102,126,234,0.3);
    }
    
    /* Custom input styling */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .stNumberInput > div > div > input {
        border-radius: 10px;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    /* Custom selectbox styling */
    .stSelectbox > div > div {
        border-radius: 10px;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    /* Custom slider styling */
    .stSlider > div > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Custom checkbox styling */
    .stCheckbox > div > label {
        background: white;
        padding: 0.5rem 1rem;
        border-radius: 10px;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    /* Custom radio styling */
    .stRadio > div > label {
        background: white;
        padding: 0.5rem 1rem;
        border-radius: 10px;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    /* Custom file uploader styling */
    .stFileUploader > div > div {
        background: white;
        border-radius: 15px;
        border: 2px dashed #667eea;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }
    
    /* Custom success/error message styling */
    .stAlert {
        border-radius: 15px;
        border: none;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }
    
    /* Custom info message styling */
    .stInfo {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        border-radius: 15px;
        border: none;
        box-shadow: 0 4px 20px rgba(79,172,254,0.3);
    }
    
    /* Custom warning message styling */
    .stWarning {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border-radius: 15px;
        border: none;
        box-shadow: 0 4px 20px rgba(240,147,251,0.3);
    }
    
    /* Custom error message styling */
    .stError {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        color: white;
        border-radius: 15px;
        border: none;
        box-shadow: 0 4px 20px rgba(255,107,107,0.3);
    }
    
    /* Custom success message styling */
    .stSuccess {
        background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
        color: white;
        border-radius: 15px;
        border: none;
        box-shadow: 0 4px 20px rgba(0,184,148,0.3);
    }
    
    /* Custom plotly chart styling */
    .js-plotly-plot {
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #e9ecef;
    }
    
    /* Custom table styling */
    .stTable {
        background: white;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #e9ecef;
    }
    
    /* Custom code block styling */
    .stCodeBlock {
        background: #2c3e50;
        border-radius: 15px;
        border: 1px solid #34495e;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    /* Custom markdown styling */
    .stMarkdown {
        background: white;
        padding: 1rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #e9ecef;
        margin: 1rem 0;
    }
    
    /* Custom divider styling */
    .stDivider {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        height: 3px;
        border-radius: 2px;
        margin: 2rem 0;
    }
    
    /* Custom progress bar styling */
    .stProgress > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    /* Custom spinner styling */
    .stSpinner > div > div {
        border: 3px solid #f3f3f3;
        border-top: 3px solid #667eea;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Custom tooltip styling */
    .stTooltip {
        background: #2c3e50;
        color: white;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }
    
    /* Custom sidebar navigation styling */
    .css-1d391kg .css-1lcbmhc {
        background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
        border-radius: 15px;
        margin: 0.5rem;
        padding: 1rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    /* Custom main content area styling */
    .main .block-container {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        border: 1px solid #e9ecef;
        margin: 1rem 0;
    }
    
    /* Custom footer styling */
    .css-1v0mbdj + div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 15px;
        text-align: center;
        margin-top: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    /* Responsive design improvements */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem;
            margin: 0.5rem 0;
        }
        
        .stButton > button {
            width: 100%;
            margin: 0.5rem 0;
        }
        
        .stTabs [data-baseweb="tab"] {
            font-size: 0.9rem;
            padding: 0.3rem 0.8rem;
        }
    }
    
    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        .main {
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        }
        
        .main .block-container {
            background: #2d2d2d;
            color: #ffffff;
            border: 1px solid #444444;
        }
        
        .stMetric, .stDataFrame, .stTable, .stMarkdown {
            background: #2d2d2d;
            color: #ffffff;
            border: 1px solid #444444;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Modern header
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        text-align: center;
        ">
        <h1 style="
            color: white;
            margin: 0;
            font-size: 3rem;
            font-weight: 700;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        ">🚀 Portfolio Intelligence Pro</h1>
        <p style="
            color: rgba(255,255,255,0.9);
            margin: 0.5rem 0 0 0;
            font-size: 1.3rem;
            font-weight: 300;
        ">Advanced Portfolio Analysis & Trading Intelligence</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            padding: 1.5rem;
            border-radius: 15px;
            margin-bottom: 1rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        ">
            <h3 style="
                color: white;
                margin: 0 0 1rem 0;
                text-align: center;
                font-weight: 600;
            ">⚙️ Configuration</h3>
        """, unsafe_allow_html=True)
        
        # Configuration parameters
        drop_threshold = st.slider(
            "Market Drop Threshold (%)",
            min_value=5,
            max_value=50,
            value=config.DEFAULT_DROP_THRESHOLD,
            help="Stocks dropping more than this percentage from their high will be flagged as buy opportunities"
        )
        
        investment_amount = st.number_input(
            "Investment Amount ($)",
            min_value=100,
            max_value=100000,
            value=config.DEFAULT_INVESTMENT_AMOUNT,
            step=100,
            help="Amount to invest in each buy opportunity"
        )
        
        rsi_window = st.slider(
            "RSI Window",
            min_value=5,
            max_value=30,
            value=config.DEFAULT_RSI_WINDOW,
            help="Number of periods for RSI calculation"
        )
        
        stock_period = st.selectbox(
            "Stock Analysis Period",
            options=["1mo", "3mo", "6mo", "1y", "2y", "5y"],
            index=2,
            help="Time period for stock data analysis"
        )
        
        market_period = st.selectbox(
            "Market Analysis Period",
            options=["1mo", "3mo", "6mo", "1y", "2y", "5y"],
            index=2,
            help="Time period for market data analysis"
        )
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Robinhood login section
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
            padding: 1.5rem;
            border-radius: 15px;
            margin-bottom: 1rem;
            box-shadow: 0 4px 20px rgba(0,184,148,0.3);
        ">
            <h3 style="
                color: white;
                margin: 0 0 1rem 0;
                text-align: center;
                font-weight: 600;
            ">🔐 Robinhood Login</h3>
        """, unsafe_allow_html=True)
        
        username = st.text_input("Username/Email", key="username", placeholder="Enter your Robinhood username or email")
        password = st.text_input("Password", type="password", key="password", placeholder="Enter your Robinhood password")
        
        # MFA field with conditional display
        mfa_required = st.session_state.get('mfa_required', False)
        
        # Add a manual MFA toggle for testing
        col_mfa1, col_mfa2 = st.columns([3, 1])
        with col_mfa1:
            if mfa_required:
                mfa_code = st.text_input(
                    "MFA Code", 
                    key="mfa_code", 
                    placeholder="Enter your 6-digit MFA code",
                    help="Enter the 6-digit code from your authenticator app or SMS"
                )
            else:
                mfa_code = None
        
        with col_mfa2:
            if st.button("🔐 MFA", key="toggle_mfa", help="Click if you need to enter MFA code"):
                st.session_state['mfa_required'] = not mfa_required
                st.rerun()
        
        # Show MFA status
        if mfa_required:
            st.info("🔐 MFA Code Required - Please enter your 6-digit authentication code")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔑 Login", key="login"):
                if username and password:
                    try:
                        # Quick check if already logged in
                        try:
                            # Try to get account info to see if already logged in
                            test_account = rs.load_account_profile()
                            if test_account:
                                st.session_state['logged_in'] = True
                                st.success("✅ Already logged in!")
                                st.rerun()
                        except:
                            pass  # Not logged in, continue with login
                        
                        # Show login attempt message with shorter timeout
                        with st.spinner("🔐 Logging in..."):
                            # Set a shorter timeout for faster feedback
                            import time
                            start_time = time.time()
                            
                            try:
                                # Try direct login without MFA first
                                if mfa_required and mfa_code:
                                    # Login with MFA
                                    rs.login(username, password, mfa_code=mfa_code)
                                else:
                                    # Try login without MFA
                                    rs.login(username, password)
                                
                                # If we get here, login was successful
                                st.session_state['logged_in'] = True
                                st.session_state['mfa_required'] = False
                                st.session_state['last_error'] = ""
                                st.success("✅ Login successful!")
                                st.rerun()
                                
                            except Exception as login_error:
                                error_msg = str(login_error).lower()
                                
                                # Check if MFA is required
                                if any(keyword in error_msg for keyword in ['mfa', 'two-factor', '2fa', 'verification']):
                                    st.session_state['mfa_required'] = True
                                    st.warning("⚠️ MFA code required. Please enter your MFA code above.")
                                    st.rerun()
                                elif 'timeout' in error_msg or 'connection' in error_msg:
                                    st.error("⏱️ Login timeout. Please check your internet connection and try again.")
                                else:
                                    # Other login error
                                    st.error(f"❌ Login failed: {login_error}")
                                    st.info("💡 Try using your Robinhood app to approve the login if prompted.")
                                    
                    except Exception as e:
                        st.error(f"❌ Login error: {e}")
                        st.info("💡 If you see device verification prompts, please approve them in your Robinhood app.")
                else:
                    st.warning("⚠️ Please enter both username and password.")
        
        with col2:
            if st.button("🚪 Logout", key="logout"):
                try:
                    rs.logout()
                except:
                    pass  # Ignore logout errors
                st.session_state['logged_in'] = False
                st.session_state['mfa_required'] = False
                st.success("✅ Logged out successfully!")
                st.rerun()
        
        # MFA help information
        if mfa_required:
            st.markdown("""
            <div style="
                background: rgba(255,255,255,0.1);
                padding: 1rem;
                border-radius: 10px;
                margin-top: 1rem;
                border-left: 4px solid #ffc107;
            ">
                <h4 style="margin: 0 0 0.5rem 0; color: white;">🔐 Multi-Factor Authentication Required</h4>
                <p style="margin: 0; color: rgba(255,255,255,0.9); font-size: 0.9rem;">
                    Robinhood requires MFA for security. Enter the 6-digit code from your authenticator app or SMS.
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Privacy mode section
        privacy_mode = st.session_state.get('privacy_mode', False)
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
            padding: 1.5rem;
            border-radius: 15px;
            margin-bottom: 1rem;
            box-shadow: 0 4px 20px rgba(255,107,107,0.3);
        ">
            <h3 style="
                color: white;
                margin: 0 0 1rem 0;
                text-align: center;
                font-weight: 600;
            ">🔒 Privacy Settings</h3>
        """, unsafe_allow_html=True)
        
        privacy_toggle = st.checkbox(
            "Hide Dollar Amounts", 
            value=privacy_mode,
            help="Hide actual dollar amounts and quantities while keeping growth percentages visible",
            key="sidebar_privacy_toggle"
        )
        
        if privacy_toggle != privacy_mode:
            st.session_state['privacy_mode'] = privacy_toggle
            st.rerun()
        
        if privacy_mode:
            st.markdown("""
            <div style="
                background: rgba(255,255,255,0.2);
                padding: 0.5rem;
                border-radius: 10px;
                text-align: center;
                margin-top: 0.5rem;
            ">
                <p style="margin: 0; color: white; font-size: 0.9rem; font-weight: 600;">
                    🔒 Privacy Mode Active - All values hidden as ***
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="
                background: rgba(255,255,255,0.2);
                padding: 0.5rem;
                border-radius: 10px;
                text-align: center;
                margin-top: 0.5rem;
            ">
                <p style="margin: 0; color: white; font-size: 0.9rem; font-weight: 600;">
                    👁️ All Values Visible
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Market Overview",
        "💼 Portfolio Analysis", 
        "🎯 Buy Opportunities",
        "🔍 Stock Research"
    ])
    
    # Initialize components
    analyzer = StockAnalyzer()
    
    # Check if user is logged in
    is_logged_in = st.session_state.get('logged_in', False)
    
    # Get privacy mode setting
    privacy_mode = st.session_state.get('privacy_mode', False)
    
    with tab1:
        render_market_overview(analyzer, drop_threshold)
    
    with tab2:
        if is_logged_in:
            # Get account data
            try:
                account = rs.load_account_profile()
                portfolio = rs.load_portfolio_profile()
                
                if account and portfolio:
                    # Extract account values using correct sources and safe parsing
                    def _safe_float(value):
                        try:
                            return float(value)
                        except Exception:
                            return 0.0

                    # Portfolio (securities) market value comes from portfolio profile
                    portfolio_value = _safe_float(
                        (portfolio.get('market_value') if isinstance(portfolio, dict) else 0)
                        or (portfolio.get('equity') if isinstance(portfolio, dict) else 0)
                        or 0
                    )

                    # Buying power primarily from account; fall back to cash_available_for_withdrawal/portfolio_cash
                    buying_power = _safe_float(
                        (account.get('buying_power') if isinstance(account, dict) else 0)
                        or (account.get('cash_available_for_withdrawal') if isinstance(account, dict) else 0)
                        or (account.get('portfolio_cash') if isinstance(account, dict) else 0)
                        or 0
                    )

                    # Cash balance from account; fall back appropriately
                    cash_balance = _safe_float(
                        (account.get('cash') if isinstance(account, dict) else 0)
                        or (account.get('portfolio_cash') if isinstance(account, dict) else 0)
                        or (account.get('cash_available_for_withdrawal') if isinstance(account, dict) else 0)
                        or 0
                    )

                    # Total account value equals equity (includes cash); fall back to sum
                    total_account = _safe_float(
                        (portfolio.get('equity') if isinstance(portfolio, dict) else 0)
                        or (portfolio_value + cash_balance)
                    )
                    
                    st.markdown("""
                    <div style="margin-bottom: 2rem;">
                        <h2 style="
                            color: #2c3e50;
                            margin: 0 0 1rem 0;
                            font-weight: 600;
                            display: flex;
                            align-items: center;
                            gap: 0.5rem;
                        ">
                            <span style="
                                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                -webkit-background-clip: text;
                                -webkit-text-fill-color: transparent;
                                background-clip: text;
                            ">📊</span>
                            Account Overview
                        </h2>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Account Overview Cards
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            padding: 1.5rem;
                            border-radius: 15px;
                            text-align: center;
                            color: white;
                            box-shadow: 0 4px 20px rgba(102,126,234,0.3);
                            margin-bottom: 1rem;
                        ">
                            <h4 style="margin: 0 0 0.5rem 0; font-size: 0.9rem; opacity: 0.9;">Portfolio Value</h4>
                            <h3 style="margin: 0; font-size: 1.8rem; font-weight: bold;">{"***" if privacy_mode else f"${portfolio_value:,.0f}"}</h3>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                            padding: 1.5rem;
                            border-radius: 15px;
                            text-align: center;
                            color: white;
                            box-shadow: 0 4px 20px rgba(240,147,251,0.3);
                            margin-bottom: 1rem;
                        ">
                            <h4 style="margin: 0 0 0.5rem 0; font-size: 0.9rem; opacity: 0.9;">Buying Power</h4>
                            <h3 style="margin: 0; font-size: 1.8rem; font-weight: bold;">{"***" if privacy_mode else f"${buying_power:,.0f}"}</h3>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                            padding: 1.5rem;
                            border-radius: 15px;
                            text-align: center;
                            color: white;
                            box-shadow: 0 4px 20px rgba(79,172,254,0.3);
                            margin-bottom: 1rem;
                        ">
                            <h4 style="margin: 0 0 0.5rem 0; font-size: 0.9rem; opacity: 0.9;">Cash Balance</h4>
                            <h3 style="margin: 0; font-size: 1.8rem; font-weight: bold;">{"***" if privacy_mode else f"${cash_balance:,.0f}"}</h3>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col4:
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
                            padding: 1.5rem;
                            border-radius: 15px;
                            text-align: center;
                            color: white;
                            box-shadow: 0 4px 20px rgba(67,233,123,0.3);
                            margin-bottom: 1rem;
                        ">
                            <h4 style="margin: 0 0 0.5rem 0; font-size: 0.9rem; opacity: 0.9;">Total Account</h4>
                            <h3 style="margin: 0; font-size: 1.8rem; font-weight: bold;">{"***" if privacy_mode else f"${total_account:,.0f}"}</h3>
                        </div>
                        """, unsafe_allow_html=True)
                    
            except Exception as e:
                st.error(f"Error loading account overview: {e}")
            
            # Portfolio Performance Section
            st.subheader("📊 Portfolio Performance")
            
            try:
                positions = rs.get_open_stock_positions()
                if positions:
                    # Calculate portfolio totals
                    total_value = 0
                    total_cost_basis = 0
                    total_gain_loss = 0
                    portfolio_data = []
                    
                    for position in positions:
                        if position and float(position['quantity']) > 0:
                            try:
                                # Get instrument details
                                instrument = rs.get_instrument_by_url(position['instrument'])
                                if instrument:
                                    symbol = instrument['symbol']
                                    quantity = float(position['quantity'])
                                    avg_cost = float(position['average_buy_price'])
                                    
                                    # Get current price
                                    price_data = rs.get_latest_price(symbol)
                                    if price_data:
                                        current_price = float(price_data[0])
                                        
                                        current_value = quantity * current_price
                                        cost_basis = quantity * avg_cost
                                        gain_loss = current_value - cost_basis
                                        gain_loss_pct = (gain_loss / cost_basis) * 100 if cost_basis > 0 else 0
                                        
                                        portfolio_data.append({
                                            'Symbol': symbol,
                                            'Quantity': "***" if privacy_mode else f"{quantity:.2f}",
                                            'Avg Cost': "***" if privacy_mode else f"${avg_cost:.2f}",
                                            'Current Price': "***" if privacy_mode else f"${current_price:.2f}",
                                            'Current Value': "***" if privacy_mode else f"${current_value:.2f}",
                                            'Gain/Loss': "***" if privacy_mode else f"${gain_loss:.2f}",
                                            'Gain/Loss %': f"{gain_loss_pct:.2f}%"
                                        })
                                        
                                        # Update totals
                                        total_value += current_value
                                        total_cost_basis += cost_basis
                                        total_gain_loss += gain_loss
                            except Exception as e:
                                continue
                    
                    if portfolio_data:
                        # Portfolio summary metrics
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total Cost Basis", "***" if privacy_mode else f"${total_cost_basis:,.0f}")
                        with col2:
                            st.metric("Current Value", "***" if privacy_mode else f"${total_value:,.0f}")
                        with col3:
                            st.metric("Total Gain/Loss", "***" if privacy_mode else f"${total_gain_loss:,.0f}", f"{((total_gain_loss/total_cost_basis)*100):.2f}%" if total_cost_basis > 0 else "0%")
                        with col4:
                            total_return_pct = ((total_gain_loss/total_cost_basis)*100) if total_cost_basis > 0 else 0
                            st.metric("Total Return", f"{total_return_pct:.2f}%")
                        
                        # Best and Worst Performers
                        if len(portfolio_data) > 1:
                            # Sort by gain/loss percentage
                            sorted_data = sorted(portfolio_data, key=lambda x: float(x['Gain/Loss %'].replace('%', '')), reverse=True)
                            best_performer = sorted_data[0]
                            worst_performer = sorted_data[-1]
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("""
                                <div style="
                                    background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
                                    padding: 1.5rem;
                                    border-radius: 15px;
                                    text-align: center;
                                    color: white;
                                    box-shadow: 0 4px 20px rgba(0,184,148,0.3);
                                ">
                                    <h4 style="margin: 0 0 0.5rem 0;">🏆 Best Performer</h4>
                                    <h3 style="margin: 0.5rem 0;">{}</h3>
                                    <p style="margin: 0; font-size: 1.2rem; font-weight: bold;">{}</p>
                                </div>
                                """.format(best_performer['Symbol'], best_performer['Gain/Loss %']), unsafe_allow_html=True)
                            
                            with col2:
                                st.markdown("""
                                <div style="
                                    background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
                                    padding: 1.5rem;
                                    border-radius: 15px;
                                    text-align: center;
                                    color: white;
                                    box-shadow: 0 4px 20px rgba(255,107,107,0.3);
                                ">
                                    <h4 style="margin: 0 0 0.5rem 0;">📉 Worst Performer</h4>
                                    <h3 style="margin: 0.5rem 0;">{}</h3>
                                    <p style="margin: 0; font-size: 1.2rem; font-weight: bold;">{}</p>
                                </div>
                                """.format(worst_performer['Symbol'], worst_performer['Gain/Loss %']), unsafe_allow_html=True)
                    else:
                        st.info("No active positions found in your portfolio.")
                        
            except Exception as e:
                st.error(f"Error loading portfolio performance: {e}")
            
            # 1. Create allocation pie chart FIRST
            st.subheader("📈 Portfolio Allocation")
            
            # Extract data for pie chart
            try:
                positions = rs.get_open_stock_positions()
                if positions:
                    symbols = []
                    values = []
                    total_portfolio_value = 0
                    
                    # First pass: calculate total portfolio value
                    for position in positions:
                        if position and float(position['quantity']) > 0:
                            try:
                                instrument = rs.get_instrument_by_url(position['instrument'])
                                if instrument:
                                    symbol = instrument['symbol']
                                    quantity = float(position['quantity'])
                                    
                                    # Get current price
                                    price_data = rs.get_latest_price(symbol)
                                    if price_data:
                                        current_price = float(price_data[0])
                                        current_value = quantity * current_price
                                        total_portfolio_value += current_value
                            except Exception as e:
                                continue
                    
                    # Second pass: filter positions > 4% and collect data
                    for position in positions:
                        if position and float(position['quantity']) > 0:
                            try:
                                instrument = rs.get_instrument_by_url(position['instrument'])
                                if instrument:
                                    symbol = instrument['symbol']
                                    quantity = float(position['quantity'])
                                    
                                    # Get current price
                                    price_data = rs.get_latest_price(symbol)
                                    if price_data:
                                        current_price = float(price_data[0])
                                        current_value = quantity * current_price
                                        
                                        # Calculate percentage of total portfolio
                                        percentage = (current_value / total_portfolio_value * 100) if total_portfolio_value > 0 else 0
                                        
                                        # Only include positions > 4%
                                        if percentage > 4:
                                            symbols.append(symbol)
                                            values.append(current_value)
                            except Exception as e:
                                continue
                    
                    if symbols and values:
                        fig_pie = go.Figure()
                        fig_pie.add_trace(go.Pie(
                            labels=symbols,
                            values=values,
                            hole=0.3,
                            textinfo='label+percent',
                            textposition='outside'
                        ))
                        fig_pie.update_layout(
                            title='Portfolio Allocation by Value (>4% positions only)',
                            height=500
                        )
                        st.plotly_chart(fig_pie, use_container_width=True)
                        
                        # Show info about filtered positions
                        if len(symbols) < len([p for p in positions if p and float(p['quantity']) > 0]):
                            st.info(f"💡 Showing {len(symbols)} positions representing >4% of portfolio value. Smaller positions are hidden for clarity.")
                    else:
                        st.info("No positions found representing more than 4% of your portfolio.")
                else:
                    st.info("No active positions found in your portfolio.")
            except Exception as e:
                st.error(f"Error loading portfolio data for pie chart: {e}")
            
            # 2. Display detailed holdings table SECOND
            st.subheader("📋 Detailed Holdings")
            try:
                positions = rs.get_open_stock_positions()
                if positions:
                    portfolio_data = []
                    
                    for position in positions:
                        if position and float(position['quantity']) > 0:
                            try:
                                # Get instrument details
                                instrument = rs.get_instrument_by_url(position['instrument'])
                                if instrument:
                                    symbol = instrument['symbol']
                                    quantity = float(position['quantity'])
                                    avg_cost = float(position['average_buy_price'])
                                    
                                    # Get current price
                                    price_data = rs.get_latest_price(symbol)
                                    if price_data:
                                        current_price = float(price_data[0])
                                        current_value = quantity * current_price
                                        gain_loss = current_value - (quantity * avg_cost)
                                        gain_loss_pct = (gain_loss / (quantity * avg_cost)) * 100 if avg_cost > 0 else 0
                                        
                                        portfolio_data.append({
                                            'Symbol': symbol,
                                            'Quantity': "***" if privacy_mode else f"{quantity:.2f}",
                                            'Avg Cost': f"${avg_cost:.2f}",
                                            'Current Price': f"${current_price:.2f}",
                                            'Current Value': "***" if privacy_mode else f"${current_value:.2f}",
                                            'Gain/Loss': "***" if privacy_mode else f"${gain_loss:.2f}",
                                            'Gain/Loss %': f"{gain_loss_pct:.2f}%"
                                        })
                            except Exception as e:
                                continue
                    
                    if portfolio_data:
                        df = pd.DataFrame(portfolio_data)
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.info("No active positions found in your portfolio.")
                else:
                    st.info("No active positions found in your portfolio.")
            except Exception as e:
                st.error(f"Error loading portfolio data for detailed holdings: {e}")
            
            # 3. Create performance bar chart THIRD
            st.subheader("📊 Stock Performance Overview")
            try:
                positions = rs.get_open_stock_positions()
                if positions:
                    symbols = []
                    gain_loss_pcts = []
                    
                    for position in positions:
                        if position and float(position['quantity']) > 0:
                            try:
                                # Get instrument details
                                instrument = rs.get_instrument_by_url(position['instrument'])
                                if instrument:
                                    symbol = instrument['symbol']
                                    quantity = float(position['quantity'])
                                    avg_cost = float(position['average_buy_price'])
                                    
                                    # Get current price
                                    price_data = rs.get_latest_price(symbol)
                                    if price_data:
                                        current_price = float(price_data[0])
                                        gain_loss = (current_price - avg_cost) / avg_cost * 100 if avg_cost > 0 else 0
                                        
                                        symbols.append(symbol)
                                        gain_loss_pcts.append(gain_loss)
                            except Exception as e:
                                continue
                    
                    if symbols and gain_loss_pcts:
                        # Create bar chart
                        fig_bar = go.Figure()
                        colors = ['green' if x >= 0 else 'red' for x in gain_loss_pcts]
                        
                        fig_bar.add_trace(go.Bar(
                            x=symbols,
                            y=gain_loss_pcts,
                            marker_color=colors,
                            text=[f"{x:.1f}%" for x in gain_loss_pcts],
                            textposition='auto'
                        ))
                        
                        fig_bar.update_layout(
                            title='Stock Performance Overview',
                            xaxis_title='Stock Symbol',
                            yaxis_title='Gain/Loss (%)',
                            height=500,
                            showlegend=False
                        )
                        
                        st.plotly_chart(fig_bar, use_container_width=True)
                    else:
                        st.info("No active positions found in your portfolio.")
                else:
                    st.info("No active positions found in your portfolio.")
            except Exception as e:
                st.error(f"Error loading portfolio data for performance bar chart: {e}")
            
        else:
            st.info("💡 Please log in to Robinhood to view your portfolio analysis.")
            render_demo_portfolio()
    
    with tab3:
        render_buy_opportunities(analyzer, None, drop_threshold, investment_amount)
    
    with tab4:
        render_stock_research(analyzer)
    
    # Modern footer
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin-top: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    ">
        <p style="margin: 0; font-size: 1rem; opacity: 0.9;">
            🚀 Portfolio Intelligence Pro - Advanced Portfolio Analysis & Trading Intelligence
        </p>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; opacity: 0.8;">
            Built with Streamlit • Powered by Robinhood API • Modern UI Design
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()