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
    
    def calculate_rsi(self, prices: pd.Series, window: int = DEFAULT_RSI_WINDOW) -> float:
        """Calculate RSI (Relative Strength Index)"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if not rsi.empty else 50
    
    def calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line.iloc[-1] if not macd_line.empty else 0,
            'signal': signal_line.iloc[-1] if not signal_line.empty else 0,
            'histogram': histogram.iloc[-1] if not histogram.empty else 0
        }
    
    def calculate_bollinger_bands(self, prices: pd.Series, window: int = 20, std_dev: int = 2) -> Dict:
        """Calculate Bollinger Bands"""
        sma = prices.rolling(window=window).mean()
        std = prices.rolling(window=window).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return {
            'upper': upper_band.iloc[-1] if not upper_band.empty else 0,
            'middle': sma.iloc[-1] if not sma.empty else 0,
            'lower': lower_band.iloc[-1] if not lower_band.empty else 0
        }
    
    def calculate_stochastic(self, high: pd.Series, low: pd.Series, close: pd.Series, k_window: int = 14, d_window: int = 3) -> Dict:
        """Calculate Stochastic Oscillator"""
        lowest_low = low.rolling(window=k_window).min()
        highest_high = high.rolling(window=k_window).max()
        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_window).mean()
        
        return {
            'k': k_percent.iloc[-1] if not k_percent.empty else 50,
            'd': d_percent.iloc[-1] if not d_percent.empty else 50
        }
    
    def calculate_support_resistance(self, data: pd.DataFrame, window: int = 20) -> Dict:
        """Calculate support and resistance levels"""
        highs = data['High'].rolling(window=window).max()
        lows = data['Low'].rolling(window=window).min()
        
        current_price = data['Close'].iloc[-1]
        
        # Find nearest support and resistance
        resistance_levels = highs.unique()
        resistance_levels = resistance_levels[resistance_levels > current_price]
        nearest_resistance = min(resistance_levels) if len(resistance_levels) > 0 else current_price * 1.1
        
        support_levels = lows.unique()
        support_levels = support_levels[support_levels < current_price]
        nearest_support = max(support_levels) if len(support_levels) > 0 else current_price * 0.9
        
        return {
            'support': nearest_support,
            'resistance': nearest_resistance,
            'support_distance': ((current_price - nearest_support) / current_price) * 100,
            'resistance_distance': ((nearest_resistance - current_price) / current_price) * 100
        }
    
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
            
            # Calculate technical indicators
            rsi = self.calculate_rsi(data['Close'])
            macd_data = self.calculate_macd(data['Close'])
            bb_data = self.calculate_bollinger_bands(data['Close'])
            stoch_data = self.calculate_stochastic(data['High'], data['Low'], data['Close'])
            sr_data = self.calculate_support_resistance(data)
            
            # Calculate moving averages
            ma_20 = data['Close'].rolling(window=20).mean().iloc[-1]
            ma_50 = data['Close'].rolling(window=50).mean().iloc[-1]
            ma_200 = data['Close'].rolling(window=200).mean().iloc[-1]
            
            # Calculate price momentum
            momentum_1m = ((current_price / data['Close'].iloc[-22]) - 1) * 100 if len(data) >= 22 else 0
            momentum_3m = ((current_price / data['Close'].iloc[-66]) - 1) * 100 if len(data) >= 66 else 0
            momentum_6m = ((current_price / data['Close'].iloc[-126]) - 1) * 100 if len(data) >= 126 else 0
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'year_high': year_high,
                'year_low': year_low,
                'drop_from_high': self.calculate_market_drop(symbol),
                'volatility': volatility,
                'rsi': rsi,
                'macd': macd_data,
                'bollinger_bands': bb_data,
                'stochastic': stoch_data,
                'support_resistance': sr_data,
                'moving_averages': {
                    'ma_20': ma_20,
                    'ma_50': ma_50,
                    'ma_200': ma_200
                },
                'momentum': {
                    '1m': momentum_1m,
                    '3m': momentum_3m,
                    '6m': momentum_6m
                },
                'market_cap': info.get('marketCap', 'N/A'),
                'pe_ratio': info.get('trailingPE', 'N/A'),
                'dividend_yield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,
                'beta': info.get('beta', 'N/A'),
                'shares_outstanding': info.get('sharesOutstanding', 'N/A'),
                'volume_avg': info.get('averageVolume', 'N/A'),
                'price_to_book': info.get('priceToBook', 'N/A'),
                'debt_to_equity': info.get('debtToEquity', 'N/A'),
                'return_on_equity': info.get('returnOnEquity', 'N/A'),
                'profit_margins': info.get('profitMargins', 'N/A')
            }
        except Exception as e:
            st.error(f"Error getting metrics for {symbol}: {e}")
            return {}
    
    def get_trading_signals(self, symbol: str) -> Dict:
        """Generate trading signals based on technical analysis"""
        try:
            metrics = self.get_stock_metrics(symbol)
            if not metrics:
                return {}
            
            signals = []
            signal_strength = 0
            
            # RSI signals
            rsi = metrics.get('rsi', 50)
            if rsi < 30:
                signals.append(("RSI Oversold", "Strong Buy", 2))
                signal_strength += 2
            elif rsi < 40:
                signals.append(("RSI Below Neutral", "Buy", 1))
                signal_strength += 1
            elif rsi > 70:
                signals.append(("RSI Overbought", "Strong Sell", -2))
                signal_strength -= 2
            elif rsi > 60:
                signals.append(("RSI Above Neutral", "Sell", -1))
                signal_strength -= 1
            
            # MACD signals
            macd_data = metrics.get('macd', {})
            if macd_data:
                macd_line = macd_data.get('macd', 0)
                signal_line = macd_data.get('signal', 0)
                histogram = macd_data.get('histogram', 0)
                
                if macd_line > signal_line and histogram > 0:
                    signals.append(("MACD Bullish", "Buy", 1))
                    signal_strength += 1
                elif macd_line < signal_line and histogram < 0:
                    signals.append(("MACD Bearish", "Sell", -1))
                    signal_strength -= 1
            
            # Moving average signals
            ma_data = metrics.get('moving_averages', {})
            current_price = metrics.get('current_price', 0)
            
            if ma_data:
                ma_20 = ma_data.get('ma_20', 0)
                ma_50 = ma_data.get('ma_50', 0)
                ma_200 = ma_data.get('ma_200', 0)
                
                if current_price > ma_20 > ma_50:
                    signals.append(("Golden Cross (20/50)", "Strong Buy", 2))
                    signal_strength += 2
                elif current_price < ma_20 < ma_50:
                    signals.append(("Death Cross (20/50)", "Strong Sell", -2))
                    signal_strength -= 2
                
                if current_price > ma_200:
                    signals.append(("Above 200 MA", "Bullish", 1))
                    signal_strength += 1
                else:
                    signals.append(("Below 200 MA", "Bearish", -1))
                    signal_strength -= 1
            
            # Bollinger Bands signals
            bb_data = metrics.get('bollinger_bands', {})
            if bb_data:
                upper = bb_data.get('upper', 0)
                lower = bb_data.get('lower', 0)
                
                if current_price < lower:
                    signals.append(("Below Lower BB", "Oversold", 1))
                    signal_strength += 1
                elif current_price > upper:
                    signals.append(("Above Upper BB", "Overbought", -1))
                    signal_strength -= 1
            
            # Stochastic signals
            stoch_data = metrics.get('stochastic', {})
            if stoch_data:
                k_value = stoch_data.get('k', 50)
                d_value = stoch_data.get('d', 50)
                
                if k_value < 20 and d_value < 20:
                    signals.append(("Stochastic Oversold", "Buy", 1))
                    signal_strength += 1
                elif k_value > 80 and d_value > 80:
                    signals.append(("Stochastic Overbought", "Sell", -1))
                    signal_strength -= 1
            
            # Overall signal
            if signal_strength >= 3:
                overall_signal = "Strong Buy"
            elif signal_strength >= 1:
                overall_signal = "Buy"
            elif signal_strength <= -3:
                overall_signal = "Strong Sell"
            elif signal_strength <= -1:
                overall_signal = "Sell"
            else:
                overall_signal = "Hold"
            
            return {
                'signals': signals,
                'signal_strength': signal_strength,
                'overall_signal': overall_signal
            }
            
        except Exception as e:
            st.error(f"Error generating trading signals for {symbol}: {e}")
            return {}
    
    def get_risk_assessment(self, symbol: str) -> Dict:
        """Assess risk level for a stock"""
        try:
            metrics = self.get_stock_metrics(symbol)
            if not metrics:
                return {}
            
            risk_score = 0
            risk_factors = []
            
            # Volatility risk
            volatility = metrics.get('volatility', 0)
            if volatility > 50:
                risk_score += 3
                risk_factors.append("High volatility (>50%)")
            elif volatility > 30:
                risk_score += 2
                risk_factors.append("Moderate volatility (>30%)")
            
            # Price drop risk
            drop_from_high = metrics.get('drop_from_high', 0)
            if drop_from_high > 50:
                risk_score += 3
                risk_factors.append("Significant drop from high (>50%)")
            elif drop_from_high > 30:
                risk_score += 2
                risk_factors.append("Moderate drop from high (>30%)")
            
            # Beta risk
            beta = metrics.get('beta', 'N/A')
            if beta != 'N/A':
                if abs(beta) > 1.5:
                    risk_score += 2
                    risk_factors.append("High beta (>1.5)")
                elif abs(beta) > 1.2:
                    risk_score += 1
                    risk_factors.append("Above-average beta (>1.2)")
            
            # Market cap risk
            market_cap = metrics.get('market_cap', 'N/A')
            if market_cap != 'N/A':
                if market_cap < 1e9:  # Less than $1B
                    risk_score += 2
                    risk_factors.append("Small cap stock (<$1B)")
                elif market_cap < 1e10:  # Less than $10B
                    risk_score += 1
                    risk_factors.append("Mid cap stock (<$10B)")
            
            # Determine risk level
            if risk_score <= 2:
                risk_level = "Low"
            elif risk_score <= 5:
                risk_level = "Medium"
            else:
                risk_level = "High"
            
            return {
                'risk_score': risk_score,
                'risk_level': risk_level,
                'risk_factors': risk_factors
            }
            
        except Exception as e:
            st.error(f"Error assessing risk for {symbol}: {e}")
            return {} 