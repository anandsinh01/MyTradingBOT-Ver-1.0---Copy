"""
Configuration file for Portfolio Intelligence Pro
"""

# Market indices configuration
MARKET_INDICES = {
    'S&P 500': '^GSPC',
    'NASDAQ': '^IXIC',
    'DOW': '^DJI'
}

# Default stocks for analysis
DEFAULT_STOCKS = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NVDA', 'META', 'NFLX']

# Streamlit page configuration
PAGE_CONFIG = {
    'page_title': "Portfolio Intelligence Pro",
    'page_icon': "📈",
    'layout': "wide"
}

# Default settings
DEFAULT_DROP_THRESHOLD = 30
DEFAULT_INVESTMENT_AMOUNT = 1000
DEFAULT_RSI_WINDOW = 14
DEFAULT_STOCK_PERIOD = "1y"
DEFAULT_MARKET_PERIOD = "6mo"
