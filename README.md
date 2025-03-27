# MCP Stock Market Analysis

A stock market analysis application that uses the AlphaVantage API to fetch stock data and provides analysis through both a FastAPI server and an MCP server.

## Features

- Real-time stock quotes
- Technical analysis with indicators (RSI, moving averages, etc.)
- MCP integration for AI assistants
- FastAPI endpoints for programmatic access
- Dashboard for visualization

## Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies: `pip install -e .` or `uv install`
5. Create a `.env` file with your AlphaVantage API key:
   ```
   ALPHA_VANTAGE_API_KEY=your_api_key_here
   ```

## Usage

### Running the API Server

```bash
python main.py
```

This will start:
- FastAPI server on http://localhost:8000
- MCP server on http://localhost:8080

### Running the Dashboard

```bash
cd dashboard
streamlit run app.py
```

## API Endpoints

- `/quote/{symbol}` - Get the latest stock quote
- `/analyze/{symbol}` - Get detailed stock analysis
- `/historical/{symbol}` - Get historical data with indicators

## MCP Methods

- `get_stock_quote` - Get the latest stock quote
- `analyze_stock` - Get detailed stock analysis with technical indicators

## License

MIT
