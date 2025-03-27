import os
from dotenv import load_dotenv
import mcp
from mcp.extension import MCPExtension
from mcp.types import Message, MessageType
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import threading

from alphavantage_service import AlphaVantageService
from stock_analyzer import StockAnalyzer
from models import (
    StockQuoteRequest,
    StockQuoteResponse, 
    StockAnalysisRequest, 
    StockAnalysisResponse,
    StockIndicators
)

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

# Create MCP extension
stock_data_extension = MCPExtension(
    name="stock_data",
    description="Get real-time and historical stock data with analysis.",
    usage_hint="Useful for getting stock prices, trends, and technical indicators to answer financial questions."
)

@stock_data_extension.register_method(
    name="get_stock_quote",
    description="Get the latest stock quote for a given symbol.",
    parameters={
        "type": "object",
        "properties": {
            "symbol": {
                "type": "string",
                "description": "The stock symbol to lookup (e.g., AAPL, MSFT, GOOGL)"
            }
        },
        "required": ["symbol"]
    }
)
async def mcp_get_stock_quote(message: Message):
    symbol = message.parameters.get("symbol", "").upper()
    quote = alpha_service.get_stock_quote(symbol)
    
    if "error" in quote:
        return {
            "error": quote["error"]
        }
    
    return {
        "symbol": symbol,
        "price": float(quote.get("05. price", 0)),
        "change": float(quote.get("09. change", 0)),
        "change_percent": quote.get("10. change percent", "0%"),
        "volume": int(quote.get("06. volume", 0)),
        "latest_trading_day": quote.get("07. latest trading day", "")
    }

@stock_data_extension.register_method(
    name="analyze_stock",
    description="Get detailed stock analysis including technical indicators.",
    parameters={
        "type": "object",
        "properties": {
            "symbol": {
                "type": "string",
                "description": "The stock symbol to analyze (e.g., AAPL, MSFT, GOOGL)"
            }
        },
        "required": ["symbol"]
    }
)
async def mcp_analyze_stock(message: Message):
    symbol = message.parameters.get("symbol", "").upper()
    
    # Get historical data
    df = alpha_service.get_daily_stock_data(symbol)
    
    if df is None:
        return {
            "error": f"Unable to fetch data for {symbol}"
        }
    
    # Analyze the stock
    analysis = stock_analyzer.analyze_stock(df)
    
    if "error" in analysis:
        return {
            "error": analysis["error"]
        }
    
    return {
        "symbol": symbol,
        "analysis": analysis
    }

# Create FastAPI endpoints (for testing independently of Claude)
@app.get("/quote/{symbol}", response_model=StockQuoteResponse)
async def api_get_stock_quote(symbol: str):
    quote = alpha_service.get_stock_quote(symbol.upper())
    if "error" in quote:
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
async def api_analyze_stock(symbol: str):
    df = alpha_service.get_daily_stock_data(symbol.upper())
    if df is None:
        raise HTTPException(status_code=404, detail=f"Unable to fetch data for {symbol}")
    
    analysis = stock_analyzer.analyze_stock(df)
    if "error" in analysis:
        raise HTTPException(status_code=500, detail=analysis["error"])
    
    # Convert the dictionary to a StockIndicators model
    indicators = StockIndicators(**analysis)
    
    return StockAnalysisResponse(
        symbol=symbol.upper(),
        analysis=indicators
    )

@app.get("/historical/{symbol}")
async def api_get_historical_data(symbol: str):
    df = alpha_service.get_daily_stock_data(symbol.upper())
    if df is None:
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

# Create MCP Server
server = mcp.Server(
    extensions=[stock_data_extension],
    metadata={
        "name": "Stock Analysis Server",
        "description": "An MCP server for stock market analysis using AlphaVantage data"
    }
)

# Function to run the MCP server
def run_mcp_server():
    server.serve(host="localhost", port=8080)

# Start the MCP server in a separate thread when FastAPI starts
@app.on_event("startup")
async def startup_event():
    # Start MCP server in a separate thread
    mcp_thread = threading.Thread(target=run_mcp_server, daemon=True)
    mcp_thread.start()
    print("MCP server started on http://localhost:8080")

if __name__ == "__main__":
    print("Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)