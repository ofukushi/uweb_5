

import yfinance as yf

# Simple in-memory cache for stock prices
stock_price_cache = {}

def get_latest_stock_price(seccode):
    if seccode in stock_price_cache:
        return stock_price_cache[seccode]
    
    try:
        stock_data = yf.download(f"{seccode}.T", period='1d')
        if not stock_data.empty:
            latest_stock_price = stock_data['Close'].iloc[-1]
            stock_price_cache[seccode] = latest_stock_price
            return latest_stock_price
    except Exception as e:
        print(f"Failed to retrieve stock data for {seccode}: {e}")
    
    return None
