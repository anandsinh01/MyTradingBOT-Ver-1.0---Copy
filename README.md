# 📈 Smart Stock Portfolio Analyzer

A comprehensive Streamlit-based trading bot that integrates with Robinhood to analyze your portfolio, find buying opportunities, and provide market insights.

## 🚀 Features

- **Market Overview**: Real-time analysis of major market indices (S&P 500, NASDAQ, DOW)
- **Portfolio Analysis**: Connect to Robinhood to view your real portfolio performance
- **Buy Opportunities**: Identify stocks that have dropped significantly from their highs
- **Stock Research**: Detailed analysis of individual stocks with charts and metrics
- **Robinhood Integration**: Place trades directly from the application (simulation mode by default)

## 📁 Project Structure

```
MyTradingBOT/
├── app.py                 # Main Streamlit application
├── config.py              # Configuration constants
├── stock_analyzer.py      # Stock data analysis module
├── robinhood_integration.py # Robinhood API integration
├── ui_components.py       # UI rendering functions
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── main.py               # Original single file (can be deleted)
```

## 🛠️ Installation

1. **Clone or download the project files**
2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 🔐 Robinhood Setup

1. **Enable Two-Factor Authentication (2FA)** on your Robinhood account
2. **Get your MFA code** from your authenticator app (Google Authenticator, Authy, etc.)
3. **Note your Robinhood credentials** (username/email and password)

## 🚀 Running the Application

1. **Navigate to the project directory:**
   ```bash
   cd MyTradingBOT
   ```

2. **Run the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

3. **Open your browser** and go to the URL shown in the terminal (usually `http://localhost:8501`)

## 📊 How to Use

### 1. Market Overview Tab
- View real-time market indices performance
- See which markets are showing buy signals based on drop thresholds
- Analyze market trends over the last 6 months

### 2. Portfolio Analysis Tab
- **Without Login**: View demo portfolio data
- **With Robinhood Login**: See your real portfolio performance, gains/losses, and allocation

### 3. Buy Opportunities Tab
- Analyze default stocks (AAPL, GOOGL, MSFT, TSLA, etc.)
- Add custom stocks for analysis
- Find stocks that have dropped significantly from their highs
- Place simulated buy orders (real trading disabled by default)

### 4. Stock Research Tab
- Research individual stocks with detailed metrics
- View price charts and volume data
- Analyze RSI, volatility, P/E ratios, and dividend yields

## ⚠️ Important Notes

### Trading Safety
- **By default, all trades are in simulation mode**
- To enable real trading, uncomment the order line in `robinhood_integration.py`
- **Use with extreme caution** - real money is at stake!

### Robinhood Login
- Your credentials are stored only in Streamlit's session state
- Never share your credentials or commit them to version control
- The app uses the official `robin-stocks` library for API access

## 🔧 Configuration

Edit `config.py` to customize:
- Market indices to track
- Default stocks for analysis
- Default drop threshold percentage
- Default investment amount

## 📈 Technical Details

- **Data Source**: Yahoo Finance (via `yfinance`)
- **Charts**: Plotly for interactive visualizations
- **UI Framework**: Streamlit for web interface
- **Trading API**: Robinhood via `robin-stocks`
- **Analysis**: RSI, volatility, market drop calculations

## 🚨 Disclaimer

This application is for educational and informational purposes only. It is not financial advice. Trading stocks involves risk, and you can lose money. Always do your own research and consider consulting with a financial advisor before making investment decisions.

## 🐛 Troubleshooting

### Common Issues:

1. **Import Errors**: Make sure all dependencies are installed with `pip install -r requirements.txt`

2. **Robinhood Login Fails**: 
   - Verify your credentials
   - Ensure 2FA is enabled
   - Check if your account is active

3. **Data Not Loading**: 
   - Check your internet connection
   - Yahoo Finance may have rate limits

4. **Streamlit Errors**: 
   - Make sure you're running `streamlit run app.py` not `python app.py`

## 📞 Support

If you encounter issues:
1. Check the error messages in the Streamlit interface
2. Verify all dependencies are installed correctly
3. Ensure your Robinhood account is properly configured

## 🔄 Updates

The application automatically fetches real-time data from:
- Yahoo Finance for stock prices and metrics
- Robinhood for portfolio and account information

---

**Happy Trading! 📈💰** 