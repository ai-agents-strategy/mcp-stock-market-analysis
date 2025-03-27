import os
from dotenv import load_dotenv
from alphavantage_service import AlphaVantageService

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
print(f"Using API key: {api_key}")

# Initialize service
alpha_service = AlphaVantageService(api_key=api_key)

# Test stock quote
print("\nTesting stock quote:")
symbol = "AAPL"
quote = alpha_service.get_stock_quote(symbol)
print(f"Quote for {symbol}:")
print(quote)

# Test daily stock data
print("\nTesting daily stock data:")
df = alpha_service.get_daily_stock_data(symbol)
if df is not None:
    print(f"Data for {symbol}:")
    print(df.head())
else:
    print(f"Failed to get data for {symbol}")
