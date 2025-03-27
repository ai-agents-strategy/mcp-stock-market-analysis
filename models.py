from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class StockQuoteRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol (e.g., AAPL, MSFT)")

class StockQuoteResponse(BaseModel):
    symbol: str
    price: float
    change: float
    change_percent: str
    volume: int
    latest_trading_day: str
    error: Optional[str] = None

class StockAnalysisRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol to analyze")

class StockIndicators(BaseModel):
    latest_date: str
    latest_price: float
    daily_change_percent: float
    sentiment: str
    current_rsi: Optional[float] = None
    ma_short: Optional[float] = None 
    ma_long: Optional[float] = None

class StockAnalysisResponse(BaseModel):
    symbol: str
    analysis: StockIndicators
    error: Optional[str] = None