# MCP Stock Market Analysis

A powerful stock market analysis application that leverages the AlphaVantage API to provide real-time stock data and technical analysis. This application integrates with the Model Context Protocol (MCP) to enable AI assistants to access stock market data and analysis.

This project is based on the excellent article [Step-by-Step Guide: Building an MCP Server using Python SDK, AlphaVantage & Claude AI](https://medium.com/@syed_hasan/step-by-step-guide-building-an-mcp-server-using-python-sdk-alphavantage-claude-ai-7a2bfb0c3096) by Syed Hasan, with improvements to follow the latest MCP Python SDK best practices.

## Features

- **Real-time Stock Quotes**: Get up-to-date stock prices and trading information
- **Technical Analysis**: Calculate and visualize key indicators like RSI and moving averages
- **MCP Integration**: Seamless integration with AI assistants through the Model Context Protocol
- **REST API**: FastAPI endpoints for programmatic access to stock data
- **Interactive Dashboard**: Streamlit-based visualization dashboard

## Getting Started

### Prerequisites

- Python 3.12 or higher
- [AlphaVantage API Key](https://www.alphavantage.co/support/#api-key) (free tier available)
- Git

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/mcp-stock-market-analysis.git
   cd mcp-stock-market-analysis
   ```

2. **Create and activate a virtual environment**

   For Windows:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

   For macOS/Linux:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**

   Using pip:
   ```bash
   pip install -e .
   ```

   Or using uv (faster):
   ```bash
   pip install uv
   uv install
   ```

4. **Set up environment variables**

   Create a `.env` file in the project root with your AlphaVantage API key:
   ```
   ALPHA_VANTAGE_API_KEY=your_api_key_here
   ```

   You can get a free API key by signing up at [AlphaVantage](https://www.alphavantage.co/support/#api-key).

## Usage

### Running the Complete Application

The easiest way to run the entire application (API server, MCP server, and dashboard) is:

```bash
python server.py
```

This will start:
- FastAPI server on http://localhost:8000
- MCP server on http://localhost:8080
- Streamlit dashboard on http://localhost:8501

### Running Components Separately

#### API and MCP Server

```bash
python main.py
```

#### Dashboard Only

```bash
cd dashboard
streamlit run app.py
```

## API Reference

### REST API Endpoints

| Endpoint | Method | Description | Example |
|----------|--------|-------------|---------|
| `/quote/{symbol}` | GET | Get the latest stock quote | `/quote/AAPL` |
| `/analyze/{symbol}` | GET | Get detailed stock analysis with indicators | `/analyze/MSFT` |
| `/historical/{symbol}` | GET | Get historical data with technical indicators | `/historical/GOOGL` |

### MCP Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `get_stock_quote` | Get the latest stock quote | `symbol`: Stock symbol (e.g., AAPL) |
| `analyze_stock` | Get detailed stock analysis with technical indicators | `symbol`: Stock symbol (e.g., AAPL) |

### MCP Resources

| Resource | Description | Example URI |
|----------|-------------|-------------|
| Stock Quote | Get formatted stock quote information | `stock://AAPL/quote` |
| Stock Analysis | Get formatted stock analysis information | `stock://AAPL/analysis` |

## Examples

### Getting a Stock Quote

```bash
curl http://localhost:8000/quote/AAPL
```

Response:
```json
{
  "symbol": "AAPL",
  "price": 221.53,
  "change": -2.21,
  "change_percent": "-0.9889%",
  "volume": 58932401,
  "latest_trading_day": "2025-03-26"
}
```

### Using with Claude or Other AI Assistants

Once the MCP server is running, you can connect it to Claude Desktop or other MCP-compatible AI assistants. The AI can then use commands like:

```
Get me the latest stock quote for Apple.
Analyze the recent performance of Microsoft stock.
```

## Troubleshooting

- **API Key Issues**: Ensure your AlphaVantage API key is correctly set in the `.env` file
- **Port Conflicts**: If you get "address already in use" errors, ensure no other applications are using ports 8000, 8080, or 8501
- **Rate Limiting**: The free tier of AlphaVantage has usage limits. If you encounter errors, you might be exceeding these limits

## License

This project is licensed under the MIT License - see the LICENSE file for details.
