"""
Stock Analyzer module for fetching and analyzing stock data
"""

import pandas as pd
import numpy as np
import yfinance as yf
import streamlit as st
from typing import Dict
from config import MARKET_INDICES, DEFAULT_RSI_WINDOW, DEFAULT_STOCK_PERIOD, DEFAULT_MARKET_PERIOD


class StockAnalyzer:
    def __init__(self):
        self.market_indices = MARKET_INDICES
        
    def get_stock_data(self, symbol: str, period: str = DEFAULT_STOCK_PERIOD) -> pd.DataFrame:
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
        data = self.get_stock_data(symbol, DEFAULT_MARKET_PERIOD)
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
            data = self.get_stock_data(symbol, DEFAULT_STOCK_PERIOD)
            
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
    
    def calculate_rsi(self, prices: pd.Series, window: int = DEFAULT_RSI_WINDOW) -> float:
        """Calculate RSI (Relative Strength Index)"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if not rsi.empty else 50 