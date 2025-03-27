import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple
from models import StockIndicators

class StockAnalyzer:
    @staticmethod
    def calculate_moving_averages(df: pd.DataFrame, window_short: int = 20, window_long: int = 50) -> pd.DataFrame:
        """Calculate short and long moving averages"""
        df = df.copy()
        df['MA_short'] = df['close'].rolling(window=window_short).mean()
        df['MA_long'] = df['close'].rolling(window=window_long).mean()
        return df
    
    @staticmethod
    def calculate_rsi(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
        """Calculate Relative Strength Index"""
        df = df.copy()
        delta = df['close'].diff()
        
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=window).mean()
        avg_loss = loss.rolling(window=window).mean()
        
        rs = avg_gain / avg_loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        return df
    
    @staticmethod
    def get_market_sentiment(df: pd.DataFrame) -> str:
        """Determine market sentiment based on indicators"""
        # Get the most recent data point
        latest = df.iloc[0]
        
        # Check if we have necessary data
        if 'MA_short' not in df.columns or 'MA_long' not in df.columns or 'RSI' not in df.columns:
            return "Insufficient data for analysis"
        
        # Trend analysis
        trend = "Neutral"
        if latest['MA_short'] > latest['MA_long']:
            trend = "Bullish"
        elif latest['MA_short'] < latest['MA_long']:
            trend = "Bearish"
            
        # RSI analysis
        rsi_signal = "Neutral"
        if latest['RSI'] > 70:
            rsi_signal = "Overbought"
        elif latest['RSI'] < 30:
            rsi_signal = "Oversold"
            
        return f"Trend: {trend}, RSI: {rsi_signal} ({latest['RSI']:.2f})"
    
    @staticmethod
    def analyze_stock(df: pd.DataFrame) -> Dict[str, Any]:
        """Perform comprehensive stock analysis"""
        if df is None or len(df) < 50:
            return {"error": "Insufficient data for analysis"}
            
        # Calculate indicators
        df = StockAnalyzer.calculate_moving_averages(df)
        df = StockAnalyzer.calculate_rsi(df)
        
        # Sort by date descending to have most recent data first
        df = df.sort_values('date', ascending=False)
        
        latest_price = df.iloc[0]['close']
        previous_price = df.iloc[1]['close']
        daily_change = ((latest_price - previous_price) / previous_price) * 100
        
        # Get the date in a readable format
        latest_date = df.iloc[0]['date'].strftime("%Y-%m-%d")
        
        # Create a StockIndicators object
        indicators = {
            "latest_date": latest_date,
            "latest_price": round(latest_price, 2),
            "daily_change_percent": round(daily_change, 2),
            "sentiment": StockAnalyzer.get_market_sentiment(df),
            "current_rsi": round(df.iloc[0]['RSI'], 2) if 'RSI' in df.columns else None,
            "ma_short": round(df.iloc[0]['MA_short'], 2) if 'MA_short' in df.columns else None,
            "ma_long": round(df.iloc[0]['MA_long'], 2) if 'MA_long' in df.columns else None
        }
        
        return indicators