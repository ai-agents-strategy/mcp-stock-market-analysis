import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# FastAPI endpoint URLs
API_BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Stock Market Dashboard",
    page_icon="📈",
    layout="wide"
)

# Title and description
st.title("Stock Market Dashboard")
st.markdown("This dashboard connects to the MCP server for stock data analysis.")

# Sidebar for user input
st.sidebar.header("Stock Selection")
symbol = st.sidebar.text_input("Enter Stock Symbol (e.g., AAPL, MSFT, GOOGL)", "AAPL")

if st.sidebar.button("Analyze Stock", type="primary"):
    # Display loading message
    with st.spinner(f"Analyzing {symbol}..."):
        try:
            # Get stock quote
            quote_response = requests.get(f"{API_BASE_URL}/quote/{symbol}")
            quote_data = quote_response.json()
            
            # Get stock analysis
            analysis_response = requests.get(f"{API_BASE_URL}/analyze/{symbol}")
            analysis_data = analysis_response.json()
            
            # Display results in dashboard
            col1, col2 = st.columns(2)
            
            # Quote data
            with col1:
                st.subheader("Stock Quote")
                quote_metrics = st.container()
                with quote_metrics:
                    price = quote_data.get("price", 0)
                    change = quote_data.get("change", 0)
                    change_percent = quote_data.get("change_percent", "0%").strip("%")
                    
                    st.metric(
                        label=f"{symbol} Price",
                        value=f"${price:.2f}",
                        delta=f"{change:.2f} ({change_percent}%)"
                    )
                    
                    st.text(f"Volume: {quote_data.get('volume', 0):,}")
                    st.text(f"Latest Trading Day: {quote_data.get('latest_trading_day', '')}")
            
            # Analysis data
            with col2:
                st.subheader("Technical Analysis")
                analysis = analysis_data.get("analysis", {})
                
                st.markdown(f"**Sentiment**: {analysis.get('sentiment', 'N/A')}")
                st.markdown(f"**RSI**: {analysis.get('current_rsi', 'N/A')}")
                
                # Create RSI gauge chart
                if analysis.get('current_rsi') is not None:
                    rsi = analysis.get('current_rsi', 50)
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=rsi,
                        title={"text": "RSI"},
                        gauge={
                            "axis": {"range": [0, 100]},
                            "bar": {"color": "darkblue"},
                            "steps": [
                                {"range": [0, 30], "color": "green"},
                                {"range": [30, 70], "color": "gray"},
                                {"range": [70, 100], "color": "red"}
                            ],
                            "threshold": {
                                "line": {"color": "red", "width": 4},
                                "thickness": 0.75,
                                "value": rsi
                            }
                        }
                    ))
                    fig.update_layout(height=250)
                    st.plotly_chart(fig, use_container_width=True)
            
            # Get historical data for chart
            historical_response = requests.get(f"{API_BASE_URL}/historical/{symbol}")
            if historical_response.status_code == 200:
                historical_data = historical_response.json()
                df = pd.DataFrame(historical_data)
                
                # Convert date column
                df['date'] = pd.to_datetime(df['date'])
                
                # Create price chart with moving averages
                st.subheader("Price History and Moving Averages")
                fig = px.line(df, x='date', y=['close', 'MA_short', 'MA_long'], 
                             title=f"{symbol} Stock Price with Moving Averages")
                fig.update_layout(xaxis_title="Date", yaxis_title="Price ($)")
                st.plotly_chart(fig, use_container_width=True)
                
                # Create RSI chart
                st.subheader("Relative Strength Index (RSI)")
                fig = px.line(df, x='date', y='RSI', title=f"{symbol} RSI")
                fig.add_hline(y=30, line_dash="dash", line_color="green")
                fig.add_hline(y=70, line_dash="dash", line_color="red")
                fig.update_layout(xaxis_title="Date", yaxis_title="RSI")
                st.plotly_chart(fig, use_container_width=True)
                
                # Raw data (expandable)
                with st.expander("View Raw Data"):
                    st.dataframe(df.sort_values('date', ascending=False))
            
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Add a section for comparing multiple stocks
st.sidebar.header("Compare Stocks")
compare_symbols = st.sidebar.text_input("Enter Symbols (comma-separated)", "AAPL,MSFT,GOOGL")

if st.sidebar.button("Compare Stocks"):
    symbols = [sym.strip() for sym in compare_symbols.split(",")]
    
    if len(symbols) > 1:
        st.subheader("Stock Price Comparison")
        
        with st.spinner("Fetching comparison data..."):
            comparison_data = []
            
            for sym in symbols:
                try:
                    quote_response = requests.get(f"{API_BASE_URL}/quote/{sym}")
                    if quote_response.status_code == 200:
                        quote_data = quote_response.json()
                        comparison_data.append({
                            "Symbol": sym,
                            "Price": quote_data.get("price", 0),
                            "Change %": float(quote_data.get("change_percent", "0%").strip("%"))
                        })
                except Exception as e:
                    st.warning(f"Could not fetch data for {sym}: {str(e)}")
            
            if comparison_data:
                comparison_df = pd.DataFrame(comparison_data)
                
                # Create comparison charts
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.bar(comparison_df, x="Symbol", y="Price", title="Current Price Comparison")
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = px.bar(comparison_df, x="Symbol", y="Change %", title="Daily Change % Comparison")
                    fig.update_traces(marker_color=comparison_df["Change %"].apply(
                        lambda x: 'green' if x > 0 else 'red'))
                    st.plotly_chart(fig, use_container_width=True)
                
                st.dataframe(comparison_df)
            else:
                st.warning("No comparison data available")