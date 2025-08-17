"""
Main Streamlit application for Portfolio Intelligence Pro
"""

import streamlit as st
import robin_stocks.robinhood as rs
import config
from stock_analyzer import StockAnalyzer
from robinhood_integration import RobinhoodIntegration, login_to_robinhood
from ui_components import (
    render_market_overview,
    render_portfolio_analysis,
    render_buy_opportunities,
    render_stock_research,
    render_demo_portfolio
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
                        rh_integration = RobinhoodIntegration()
                        
                        # Attempt login with or without MFA
                        if mfa_required and mfa_code:
                            # Login with MFA
                            if rh_integration.login_to_robinhood(username, password, mfa_code):
                                st.session_state['logged_in'] = True
                                st.session_state['rh_integration'] = rh_integration
                                st.session_state['mfa_required'] = False  # Reset MFA requirement
                                st.session_state['last_error'] = ""  # Clear any previous errors
                                st.success("✅ Login successful!")
                                st.rerun()
                            else:
                                st.error("❌ Login failed. Please check your MFA code.")
                        elif not mfa_required:
                            # Try login without MFA first
                            login_result = rh_integration.login_to_robinhood(username, password)
                            if login_result:
                                st.session_state['logged_in'] = True
                                st.session_state['rh_integration'] = rh_integration
                                st.session_state['mfa_required'] = False
                                st.session_state['last_error'] = ""
                                st.success("✅ Login successful!")
                                st.rerun()
                            else:
                                # Check if MFA is required based on the last error
                                last_error = st.session_state.get('last_error', '')
                                if any(keyword in last_error.lower() for keyword in ['mfa', 'two-factor', '2fa', 'verification']):
                                    st.session_state['mfa_required'] = True
                                    st.warning("⚠️ MFA code required. Please enter your MFA code above.")
                                    st.rerun()
                                else:
                                    st.error("❌ Login failed. Please check your credentials.")
                        else:
                            st.warning("⚠️ MFA code is required. Please enter it above.")
                    except Exception as e:
                        error_msg = str(e)
                        st.error(f"❌ Login error: {error_msg}")
                        st.session_state['last_error'] = error_msg
                        
                        # Check if this is an MFA-related error
                        if any(keyword in error_msg.lower() for keyword in ['mfa', 'two-factor', '2fa', 'verification']):
                            st.session_state['mfa_required'] = True
                            st.warning("⚠️ MFA code required. Please enter your MFA code above.")
                            st.rerun()
                else:
                    st.warning("⚠️ Please enter both username and password.")
        
        with col2:
            if st.button("🚪 Logout", key="logout"):
                if st.session_state.get('rh_integration'):
                    st.session_state['rh_integration'].logout()
                st.session_state['logged_in'] = False
                st.session_state['rh_integration'] = None
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
            help="Hide actual dollar amounts while keeping growth percentages visible",
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
                    🔒 Privacy Mode Active
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
                    👁️ Amounts Visible
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # App information
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            padding: 1.5rem;
            border-radius: 15px;
            margin-bottom: 1rem;
            box-shadow: 0 4px 20px rgba(240,147,251,0.3);
        ">
            <h3 style="
                color: white;
                margin: 0 0 1rem 0;
                text-align: center;
                font-weight: 600;
            ">ℹ️ App Info</h3>
            <p style="
                color: white;
                margin: 0;
                font-size: 0.9rem;
                text-align: center;
                opacity: 0.9;
            ">Version 2.0</p>
            <p style="
                color: white;
                margin: 0.5rem 0 0 0;
                font-size: 0.9rem;
                text-align: center;
                opacity: 0.9;
            ">Modern UI Design</p>
        """, unsafe_allow_html=True)
    
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
    rh_integration = st.session_state.get('rh_integration')
    
    with tab1:
        render_market_overview(analyzer, drop_threshold)
    
    with tab2:
        if rh_integration:
            render_portfolio_analysis(rh_integration)
        else:
            st.info("💡 Please log in to Robinhood to view your portfolio analysis.")
            render_demo_portfolio()
    
    with tab3:
        if rh_integration:
            render_buy_opportunities(analyzer, rh_integration, drop_threshold, investment_amount)
        else:
            st.info("💡 Please log in to Robinhood to view buy opportunities.")
    
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
