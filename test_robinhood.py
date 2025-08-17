"""
Test script to verify Robinhood data fetching
Run this after logging into Robinhood to test the API calls
"""

import robin_stocks.robinhood as rs
import json

def test_robinhood_data():
    """Test various Robinhood API calls"""
    try:
        print("🔍 Testing Robinhood API calls...")
        
        # Test account profile
        print("\n1. Testing Account Profile...")
        account_profile = rs.load_account_profile()
        if account_profile:
            print("✅ Account Profile loaded successfully")
            print(f"   Buying Power: ${float(account_profile.get('buying_power', 0)):,.2f}")
            print(f"   Cash: ${float(account_profile.get('cash', 0)):,.2f}")
            print(f"   Account Number: {account_profile.get('account_number', 'N/A')}")
            print(f"   Account Type: {account_profile.get('type', 'N/A')}")
        else:
            print("❌ Failed to load account profile")
        
        # Test portfolio
        print("\n2. Testing Portfolio...")
        account_portfolio = rs.load_portfolio()
        if account_portfolio:
            print("✅ Portfolio loaded successfully")
            print(f"   Equity: ${float(account_portfolio.get('equity', 0)):,.2f}")
            print(f"   Market Value: ${float(account_portfolio.get('market_value', 0)):,.2f}")
            print(f"   Cost Basis: ${float(account_portfolio.get('cost_basis', 0)):,.2f}")
        else:
            print("❌ Failed to load portfolio")
        
        # Test positions
        print("\n3. Testing Stock Positions...")
        positions = rs.get_open_stock_positions()
        if positions:
            print(f"✅ Found {len(positions)} stock positions")
            for i, pos in enumerate(positions[:3]):  # Show first 3
                if pos and float(pos.get('quantity', 0)) > 0:
                    print(f"   Position {i+1}: {pos.get('quantity', 0)} shares")
                    print(f"   Average Cost: ${float(pos.get('average_buy_price', 0)):.2f}")
        else:
            print("❌ No stock positions found")
        
        # Test a sample stock price
        print("\n4. Testing Stock Price...")
        try:
            price_data = rs.get_latest_price('AAPL')
            if price_data:
                print(f"✅ AAPL Price: ${float(price_data[0]):.2f}")
            else:
                print("❌ Failed to get AAPL price")
        except Exception as e:
            print(f"❌ Error getting stock price: {e}")
        
        print("\n🎉 Robinhood API test completed!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")

if __name__ == "__main__":
    test_robinhood_data() 