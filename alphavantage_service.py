import requests
import pandas as pd
from typing import Dict, Any, Optional
from pydantic import ValidationError

class AlphaVantageService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
    
    def get_daily_stock_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Fetch daily stock data for a given symbol"""
        try:
            params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol,
                "outputsize": "compact",
                "apikey": self.api_key
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if "Time Series (Daily)" not in data:
                print(f"Error: {data.get('Note', data)}")
                return None
                
            time_series = data["Time Series (Daily)"]
            
            # Convert to DataFrame
            df = pd.DataFrame(time_series).T
            
            # Fix column names and data types
            df.columns = [col.split(". ")[1] for col in df.columns]
            df = df.astype(float)
            
            # Add date as a column
            df.index = pd.to_datetime(df.index)
            df.reset_index(inplace=True)
            df.rename(columns={"index": "date"}, inplace=True)
            
            return df
        
        except Exception as e:
            print(f"Error fetching stock data: {e}")
            return None
    
    def get_stock_quote(self, symbol: str) -> Dict[str, Any]:
        """Get the latest quote for a stock"""
        try:
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": self.api_key
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if "Global Quote" not in data:
                return {"error": data.get("Note", "Unknown error")}
            
            quote = data["Global Quote"]
            
            # Convert numeric strings to appropriate types
            try:
                processed_quote = {
                    "01. symbol": quote.get("01. symbol", ""),
                    "02. open": float(quote.get("02. open", 0)),
                    "03. high": float(quote.get("03. high", 0)),
                    "04. low": float(quote.get("04. low", 0)),
                    "05. price": float(quote.get("05. price", 0)),
                    "06. volume": int(quote.get("06. volume", 0)),
                    "07. latest trading day": quote.get("07. latest trading day", ""),
                    "08. previous close": float(quote.get("08. previous close", 0)),
                    "09. change": float(quote.get("09. change", 0)),
                    "10. change percent": quote.get("10. change percent", "")
                }
                return processed_quote
            except (ValueError, TypeError) as e:
                return {"error": f"Error processing quote data: {e}", "raw_data": quote}
        
        except Exception as e:
            return {"error": str(e)}