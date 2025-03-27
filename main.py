"""
Stock Market Analysis Application

This application provides stock market data and analysis through both a FastAPI server
and an MCP (Model Context Protocol) server for AI assistant integration.
"""

import os
import logging
from typing import Dict, Any, List, Optional
import asyncio
import signal
import threading
import pandas as pd

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from mcp.server.fastmcp import FastMCP, Context

from alphavantage_service import AlphaVantageService
from stock_analyzer import StockAnalyzer
from models import (
    StockQuoteResponse, 
    StockAnalysisResponse,
    StockIndicators
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("stock_market_analysis")

# Load environment variables
load_dotenv()

# Load AlphaVantage API key
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
if not ALPHA_VANTAGE_API_KEY:
    raise ValueError("Missing ALPHA_VANTAGE_API_KEY environment variable")

# Initialize services
alpha_service = AlphaVantageService(api_key=ALPHA_VANTAGE_API_KEY)
stock_analyzer = StockAnalyzer()

# Create FastAPI app
app = FastAPI(
    title="Stock Analysis API",
    description="API for stock market analysis using AlphaVantage data",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create MCP server using FastMCP
mcp_server = FastMCP(
    "Stock Analysis Server",
    description="An MCP server for stock market analysis using AlphaVantage data",
    dependencies=["pandas", "requests", "python-dotenv"]
)

# MCP Tools

@mcp_server.tool()
async def get_stock_quote(symbol: str, ctx: Context) -> Dict[str, Any]:
    """
    Get the latest stock quote for a given symbol.
    
    Args:
        symbol: The stock symbol to lookup (e.g., AAPL, MSFT, GOOGL)
        ctx: MCP context object
        
    Returns:
        Dictionary containing stock quote information
    """
    ctx.info(f"Fetching quote for {symbol}")
    symbol = symbol.upper()
    quote = alpha_service.get_stock_quote(symbol)
    
    if "error" in quote:
        ctx.error(f"Error fetching quote: {quote['error']}")
        return {
            "error": quote["error"]
        }
    
    result = {
        "symbol": symbol,
        "price": float(quote.get("05. price", 0)),
        "change": float(quote.get("09. change", 0)),
        "change_percent": quote.get("10. change percent", "0%"),
        "volume": int(quote.get("06. volume", 0)),
        "latest_trading_day": quote.get("07. latest trading day", "")
    }
    
    ctx.info(f"Quote retrieved successfully for {symbol}")
    return result

@mcp_server.tool()
async def analyze_stock(symbol: str, ctx: Context) -> Dict[str, Any]:
    """
    Get detailed stock analysis including technical indicators.
    
    Args:
        symbol: The stock symbol to analyze (e.g., AAPL, MSFT, GOOGL)
        ctx: MCP context object
        
    Returns:
        Dictionary containing stock analysis information
    """
    ctx.info(f"Analyzing stock: {symbol}")
    symbol = symbol.upper()
    
    # Get historical data
    ctx.info(f"Fetching historical data for {symbol}")
    df = alpha_service.get_daily_stock_data(symbol)
    
    if df is None:
        ctx.error(f"Unable to fetch data for {symbol}")
        return {
            "error": f"Unable to fetch data for {symbol}"
        }
    
    # Analyze the stock
    ctx.info(f"Performing analysis for {symbol}")
    analysis = stock_analyzer.analyze_stock(df)
    
    if "error" in analysis:
        ctx.error(f"Analysis error: {analysis['error']}")
        return {
            "error": analysis["error"]
        }
    
    ctx.info(f"Analysis completed successfully for {symbol}")
    return {
        "symbol": symbol,
        "analysis": analysis
    }

# MCP Resources

@mcp_server.resource("stock://{symbol}/quote")
async def stock_quote_resource(symbol: str) -> str:
    """
    Get the latest stock quote as a resource.
    
    Args:
        symbol: The stock symbol to lookup
        
    Returns:
        Formatted string with stock quote information
    """
    symbol = symbol.upper()
    quote = alpha_service.get_stock_quote(symbol)
    
    if "error" in quote:
        return f"Error: {quote['error']}"
    
    price = float(quote.get("05. price", 0))
    change = float(quote.get("09. change", 0))
    change_percent = quote.get("10. change percent", "0%")
    volume = int(quote.get("06. volume", 0))
    latest_trading_day = quote.get("07. latest trading day", "")
    
    return f"""
Stock Quote: {symbol}
Price: ${price:.2f}
Change: {change:.2f} ({change_percent})
Volume: {volume:,}
Latest Trading Day: {latest_trading_day}
"""

@mcp_server.resource("stock://{symbol}/analysis")
async def stock_analysis_resource(symbol: str) -> str:
    """
    Get stock analysis as a resource.
    
    Args:
        symbol: The stock symbol to analyze
        
    Returns:
        Formatted string with stock analysis information
    """
    symbol = symbol.upper()
    df = alpha_service.get_daily_stock_data(symbol)
    
    if df is None:
        return f"Error: Unable to fetch data for {symbol}"
    
    analysis = stock_analyzer.analyze_stock(df)
    
    if "error" in analysis:
        return f"Error: {analysis['error']}"
    
    return f"""
Stock Analysis: {symbol}
Latest Date: {analysis['latest_date']}
Price: ${analysis['latest_price']:.2f}
Daily Change: {analysis['daily_change_percent']:.2f}%
Sentiment: {analysis['sentiment']}
RSI: {analysis['current_rsi']:.2f}
Short-term MA: {analysis['ma_short']:.2f}
Long-term MA: {analysis['ma_long']:.2f}
"""

# FastAPI endpoints

@app.get("/quote/{symbol}", response_model=StockQuoteResponse)
async def api_get_stock_quote(symbol: str) -> StockQuoteResponse:
    """API endpoint to get the latest stock quote"""
    logger.info(f"API request for quote: {symbol}")
    quote = alpha_service.get_stock_quote(symbol.upper())
    if "error" in quote:
        logger.error(f"Quote error: {quote['error']}")
        raise HTTPException(status_code=404, detail=quote["error"])
    
    return StockQuoteResponse(
        symbol=symbol.upper(),
        price=float(quote.get("05. price", 0)),
        change=float(quote.get("09. change", 0)),
        change_percent=quote.get("10. change percent", "0%"),
        volume=int(quote.get("06. volume", 0)),
        latest_trading_day=quote.get("07. latest trading day", "")
    )

@app.get("/analyze/{symbol}", response_model=StockAnalysisResponse)
async def api_analyze_stock(symbol: str) -> StockAnalysisResponse:
    """API endpoint to get detailed stock analysis"""
    logger.info(f"API request for analysis: {symbol}")
    df = alpha_service.get_daily_stock_data(symbol.upper())
    if df is None:
        logger.error(f"Unable to fetch data for {symbol}")
        raise HTTPException(status_code=404, detail=f"Unable to fetch data for {symbol}")
    
    analysis = stock_analyzer.analyze_stock(df)
    if "error" in analysis:
        logger.error(f"Analysis error: {analysis['error']}")
        raise HTTPException(status_code=500, detail=analysis["error"])
    
    # Handle NaN values in the analysis results
    for key, value in analysis.items():
        if isinstance(value, float) and (pd.isna(value) or pd.isnull(value)):
            analysis[key] = None
    
    # Convert the dictionary to a StockIndicators model
    indicators = StockIndicators(**analysis)
    
    return StockAnalysisResponse(
        symbol=symbol.upper(),
        analysis=indicators
    )

@app.get("/historical/{symbol}")
async def api_get_historical_data(symbol: str) -> List[Dict[str, Any]]:
    """API endpoint to get historical stock data with indicators"""
    logger.info(f"API request for historical data: {symbol}")
    df = alpha_service.get_daily_stock_data(symbol.upper())
    if df is None:
        logger.error(f"Unable to fetch data for {symbol}")
        raise HTTPException(status_code=404, detail=f"Unable to fetch data for {symbol}")
    
    # Calculate indicators
    df = stock_analyzer.calculate_moving_averages(df)
    df = stock_analyzer.calculate_rsi(df)
    
    # Convert to list of dictionaries for JSON response
    # Convert datetime to string format
    result = []
    for _, row in df.iterrows():
        row_dict = row.to_dict()
        row_dict['date'] = row_dict['date'].strftime('%Y-%m-%d')
        result.append(row_dict)
    
    return result

# Server startup and shutdown

def run_mcp_server() -> None:
    """Run the MCP server in a separate process"""
    logger.info("Starting MCP server...")
    # FastMCP.run() doesn't accept host/port parameters directly
    mcp_server.run()

@app.on_event("startup")
async def startup_event() -> None:
    """Start the MCP server when FastAPI starts"""
    # Start MCP server in a separate thread
    mcp_thread = threading.Thread(target=run_mcp_server, daemon=True)
    mcp_thread.start()
    logger.info("MCP server started on http://localhost:8080")

@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Shutdown handlers for clean application termination"""
    logger.info("Shutting down application...")

def handle_signals() -> None:
    """Set up signal handlers for graceful shutdown"""
    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}, shutting down...")
        # Trigger FastAPI shutdown
        asyncio.get_event_loop().stop()
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    handle_signals()
    logger.info("Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
