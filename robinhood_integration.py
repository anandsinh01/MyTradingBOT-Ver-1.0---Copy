"""
Robinhood Integration module for portfolio management and trading
"""

import robin_stocks.robinhood as rs
import streamlit as st
from typing import Dict, List
import time


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
        self.logged_in = False
    
    def validate_credentials(self, username, password):
        """
        Basic validation of credentials before attempting login.
        Returns (is_valid, error_message)
        """
        if not username or not username.strip():
            return False, "Username cannot be empty"
        
        if not password or not password.strip():
            return False, "Password cannot be empty"
        
        # Check if username looks like an email
        if '@' in username:
            if not username.count('@') == 1 or '.' not in username.split('@')[1]:
                return False, "Please enter a valid email address"
        
        # Check password length
        if len(password) < 6:
            return False, "Password must be at least 6 characters long"
        
        return True, ""
    
    def check_mfa_required(self, username, password):
        """
        Check if MFA is required for login without actually logging in.
        Returns True if MFA is required, False otherwise.
        """
        try:
            # Try to login without MFA to see if it's required
            rs.login(username, password)
            # If we get here, no MFA was required
            rs.logout()  # Clean up
            return False
        except Exception as e:
            error_msg = str(e).lower()
            if any(keyword in error_msg for keyword in ['mfa', 'two-factor', '2fa', 'verification']):
                return True
            else:
                # Some other error, not MFA related
                return False
    
    def login_to_robinhood(self, username, password, mfa_code=None):
        """
        Logs into Robinhood using credentials and optional MFA code.
        Returns True on success, False on failure.
        """
        try:
            # Validate credentials first
            is_valid, error_msg = self.validate_credentials(username, password)
            if not is_valid:
                st.error(f"❌ Invalid credentials: {error_msg}")
                return False
            
            st.info("Attempting to log in to Robinhood...")
            
            # Handle MFA if provided
            if mfa_code:
                if not mfa_code.isdigit() or len(mfa_code) != 6:
                    st.error("❌ MFA code must be a 6-digit number")
                    return False
                try:
                    rs.login(username, password, mfa_code=mfa_code)
                except Exception as mfa_error:
                    st.error(f"❌ MFA login failed: {mfa_error}")
                    return False
            else:
                # Try without MFA first
                try:
                    rs.login(username, password)
                except Exception as mfa_error:
                    error_msg = str(mfa_error).lower()
                    # Check for various MFA-related error messages
                    mfa_keywords = ['mfa', 'two-factor', '2fa', 'verification', 'authenticator', 'sms', 'code']
                    if any(keyword in error_msg for keyword in mfa_keywords):
                        st.warning("⚠️ MFA code required. Please enter your MFA code.")
                        # Set session state to indicate MFA is required
                        if 'mfa_required' not in st.session_state:
                            st.session_state['mfa_required'] = True
                        return False
                    else:
                        # Some other error, not MFA related
                        raise mfa_error
            
            # Test the connection
            try:
                account = rs.load_account_profile()
                if account:
                    self.logged_in = True
                    st.session_state['logged_in'] = True
                    st.success("✅ Login Successful! Connected to Robinhood.")
                    return True
                else:
                    st.error("❌ Login failed: Could not verify account connection.")
                    return False
            except Exception as e:
                st.error(f"❌ Login verification failed: {e}")
                return False
                
        except Exception as e:
            st.error(f"❌ Login Failed: {e}")
            self.logged_in = False
            st.session_state['logged_in'] = False
            return False
    
    def logout(self):
        """Logs out of Robinhood"""
        try:
            rs.logout()
            self.logged_in = False
            st.session_state['logged_in'] = False
            st.success("✅ Logged out successfully!")
            return True
        except Exception as e:
            st.error(f"❌ Logout error: {e}")
            return False
    
    def get_portfolio(self) -> List[Dict]:
        """Get current portfolio holdings"""
        if not st.session_state.get('logged_in', False):
            return []
        
        try:
            positions = rs.get_open_stock_positions()
            portfolio = []
            
            for position in positions:
                if position and float(position['quantity']) > 0:
                    try:
                        # Get instrument details
                        instrument = rs.get_instrument_by_url(position['instrument'])
                        if not instrument:
                            continue
                            
                        symbol = instrument['symbol']
                        
                        # Get current price
                        price_data = rs.get_latest_price(symbol)
                        if not price_data or len(price_data) == 0:
                            continue
                            
                        current_price = float(price_data[0])
                        quantity = float(position['quantity'])
                        avg_cost = float(position['average_buy_price'])
                        
                        # Calculate values
                        current_value = quantity * current_price
                        total_cost = quantity * avg_cost
                        gain_loss = current_value - total_cost
                        gain_loss_percent = ((current_price - avg_cost) / avg_cost) * 100 if avg_cost > 0 else 0
                        
                        portfolio.append({
                            'symbol': symbol,
                            'quantity': quantity,
                            'average_cost': avg_cost,
                            'current_price': current_price,
                            'current_value': current_value,
                            'total_cost': total_cost,
                            'gain_loss': gain_loss,
                            'gain_loss_percent': gain_loss_percent
                        })
                    except Exception as e:
                        st.warning(f"Error processing position for {position.get('instrument', 'unknown')}: {e}")
                        continue
            
            return portfolio
        except Exception as e:
            st.error(f"Error fetching portfolio: {e}")
            return []
    
    def get_account_info(self) -> Dict:
        """Get account information"""
        if not st.session_state.get('logged_in', False):
            return {}
        
        try:
            # Get comprehensive account information
            account_profile = rs.load_account_profile()
            account_portfolio = rs.load_portfolio_profile()
            
            if not account_profile:
                st.error("Could not fetch account profile")
                return {}
            
            # Get buying power from the correct field
            buying_power = float(account_profile.get('buying_power', 0))
            
            # Try multiple approaches to get portfolio value
            portfolio_value = 0
            if account_portfolio:
                # Try different possible field names for portfolio value
                portfolio_value = float(account_portfolio.get('equity', 0))
                if portfolio_value == 0:
                    portfolio_value = float(account_portfolio.get('market_value', 0))
                if portfolio_value == 0:
                    portfolio_value = float(account_portfolio.get('total_equity', 0))
                if portfolio_value == 0:
                    portfolio_value = float(account_portfolio.get('portfolio_value', 0))
            
            # If we still don't have portfolio value, calculate it from positions
            if portfolio_value == 0:
                try:
                    positions = rs.get_open_stock_positions()
                    for position in positions:
                        if position and float(position.get('quantity', 0)) > 0:
                            instrument = rs.get_instrument_by_url(position['instrument'])
                            if instrument:
                                symbol = instrument['symbol']
                                price_data = rs.get_latest_price(symbol)
                                if price_data and len(price_data) > 0:
                                    current_price = float(price_data[0])
                                    quantity = float(position['quantity'])
                                    portfolio_value += current_price * quantity
                except Exception as e:
                    st.warning(f"Could not calculate portfolio value from positions: {e}")
            
            # Get cash balance
            cash_balance = float(account_profile.get('cash', 0))
            
            # Get total account value
            total_account_value = portfolio_value + cash_balance
            
            # Get additional account details
            account_number = account_profile.get('account_number', 'N/A')
            account_type = account_profile.get('type', 'N/A')
            
            return {
                'total_portfolio_value': portfolio_value,
                'buying_power': buying_power,
                'cash_balance': cash_balance,
                'total_account_value': total_account_value,
                'account_number': account_number,
                'account_type': account_type,
                'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            st.error(f"Error fetching account info: {e}")
            # Return default values to prevent crashes
            return {
                'total_portfolio_value': 0,
                'buying_power': 0,
                'cash_balance': 0,
                'total_account_value': 0,
                'account_number': 'Error',
                'account_type': 'Error',
                'last_updated': 'Error'
            }
    
    def get_detailed_portfolio_summary(self) -> Dict:
        """Get detailed portfolio summary with better calculations"""
        if not st.session_state.get('logged_in', False):
            return {}
        
        try:
            portfolio = self.get_portfolio()
            account_info = self.get_account_info()
            
            if not portfolio and not account_info:
                st.warning("No portfolio or account data available")
                return {}
            
            if not portfolio:
                # Return just account info if no portfolio
                return account_info
            
            # Calculate portfolio metrics
            total_quantity = sum(item['quantity'] for item in portfolio)
            total_cost_basis = sum(item['total_cost'] for item in portfolio)
            total_current_value = sum(item['current_value'] for item in portfolio)
            total_gain_loss = sum(item['gain_loss'] for item in portfolio)
            
            # Calculate weighted average return
            if total_cost_basis > 0:
                total_return_percent = (total_gain_loss / total_cost_basis) * 100
            else:
                total_return_percent = 0
            
            # Get best and worst performers
            if portfolio:
                best_performer = max(portfolio, key=lambda x: x['gain_loss_percent'])
                worst_performer = min(portfolio, key=lambda x: x['gain_loss_percent'])
            else:
                best_performer = worst_performer = None
            
            # Combine account info with portfolio summary
            summary = {
                **account_info,
                'total_positions': len(portfolio),
                'total_quantity': total_quantity,
                'total_cost_basis': total_cost_basis,
                'total_current_value': total_current_value,
                'total_gain_loss': total_gain_loss,
                'total_return_percent': total_return_percent,
                'best_performer': best_performer,
                'worst_performer': worst_performer
            }
            
            return summary
            
        except Exception as e:
            st.error(f"Error calculating portfolio summary: {e}")
            import traceback
            st.error(f"Traceback: {traceback.format_exc()}")
            return {}
    
    def place_buy_order(self, symbol: str, amount: float) -> bool:
        """Place a buy order"""
        if not st.session_state.get('logged_in', False):
            st.error("Please login first")
            return False
            
        try:
            # Get current price to calculate quantity
            price_data = rs.get_latest_price(symbol)
            if not price_data or len(price_data) == 0:
                st.error(f"Could not get current price for {symbol}")
                return False
                
            current_price = float(price_data[0])
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

    def test_robinhood_connection(self) -> Dict:
        """Test Robinhood connection and show available data fields"""
        if not st.session_state.get('logged_in', False):
            return {"error": "Not logged in"}
        
        try:
            # Test account profile
            account_profile = rs.load_account_profile()
            portfolio_profile = rs.load_portfolio_profile()
            positions = rs.get_open_stock_positions()
            
            test_results = {
                "account_profile_keys": list(account_profile.keys()) if account_profile else [],
                "portfolio_profile_keys": list(portfolio_profile.keys()) if portfolio_profile else [],
                "positions_count": len(positions) if positions else 0,
                "sample_position": positions[0] if positions and len(positions) > 0 else None
            }
            
            # Show sample data
            if account_profile:
                test_results["sample_account_data"] = {
                    "buying_power": account_profile.get('buying_power'),
                    "cash": account_profile.get('cash'),
                    "account_number": account_profile.get('account_number'),
                    "type": account_profile.get('type')
                }
            
            if portfolio_profile:
                test_results["sample_portfolio_data"] = {
                    "equity": portfolio_profile.get('equity'),
                    "market_value": portfolio_profile.get('market_value'),
                    "total_equity": portfolio_profile.get('total_equity'),
                    "portfolio_value": portfolio_profile.get('portfolio_value')
                }
            
            return test_results
            
        except Exception as e:
            return {"error": str(e)}
