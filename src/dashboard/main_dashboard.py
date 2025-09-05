"""
Financial Analytics Dashboard - Streamlit Web Interface
Real-time stock analysis, forecasting, and portfolio management
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Financial Analytics Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(90deg, #1f77b4, #17a2b8);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .positive {
        color: #28a745;
        font-weight: bold;
    }
    .negative {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_stock_data(symbol, period="1y"):
    """Get stock data from Yahoo Finance"""
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period)
        info = ticker.info
        return data, info
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {e}")
        return None, None

def calculate_technical_indicators(data):
    """Calculate technical indicators"""
    if data is None or data.empty:
        return data
    
    # Moving Averages
    data['SMA_20'] = data['Close'].rolling(window=20).mean()
    data['SMA_50'] = data['Close'].rolling(window=50).mean()
    data['EMA_12'] = data['Close'].ewm(span=12).mean()
    
    # RSI
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    
    # Bollinger Bands
    data['BB_Middle'] = data['Close'].rolling(window=20).mean()
    bb_std = data['Close'].rolling(window=20).std()
    data['BB_Upper'] = data['BB_Middle'] + (bb_std * 2)
    data['BB_Lower'] = data['BB_Middle'] - (bb_std * 2)
    
    # MACD
    data['MACD'] = data['EMA_12'] - data['Close'].ewm(span=26).mean()
    data['MACD_Signal'] = data['MACD'].ewm(span=9).mean()
    
    return data

def generate_trading_signals(data, symbol):
    """Generate trading signals"""
    if data is None or data.empty:
        return []
    
    signals = []
    latest = data.iloc[-1]
    
    # RSI signals
    if latest['RSI'] > 70:
        signals.append({"type": "🔴 SELL", "reason": f"RSI Overbought ({latest['RSI']:.1f})", "strength": "Medium"})
    elif latest['RSI'] < 30:
        signals.append({"type": "🟢 BUY", "reason": f"RSI Oversold ({latest['RSI']:.1f})", "strength": "Medium"})
    
    # Moving Average signals
    if latest['Close'] > latest['SMA_20'] > latest['SMA_50']:
        signals.append({"type": "🟢 BUY", "reason": "Bullish MA Alignment", "strength": "Strong"})
    elif latest['Close'] < latest['SMA_20'] < latest['SMA_50']:
        signals.append({"type": "🔴 SELL", "reason": "Bearish MA Alignment", "strength": "Strong"})
    
    # Bollinger Bands signals
    if latest['Close'] > latest['BB_Upper']:
        signals.append({"type": "🔴 SELL", "reason": "Above Upper Bollinger Band", "strength": "Medium"})
    elif latest['Close'] < latest['BB_Lower']:
        signals.append({"type": "🟢 BUY", "reason": "Below Lower Bollinger Band", "strength": "Medium"})
    
    return signals

def create_candlestick_chart(data, symbol):
    """Create candlestick chart with indicators"""
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=(f'{symbol} Price & Indicators', 'Volume', 'RSI'),
        row_width=[0.2, 0.1, 0.1]
    )
    
    # Candlestick
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name=symbol
    ), row=1, col=1)
    
    # Moving Averages
    fig.add_trace(go.Scatter(
        x=data.index, y=data['SMA_20'],
        line=dict(color='orange', width=1),
        name='SMA 20'
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(
        x=data.index, y=data['SMA_50'],
        line=dict(color='red', width=1),
        name='SMA 50'
    ), row=1, col=1)
    
    # Bollinger Bands
    fig.add_trace(go.Scatter(
        x=data.index, y=data['BB_Upper'],
        line=dict(color='gray', width=1, dash='dash'),
        name='BB Upper'
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(
        x=data.index, y=data['BB_Lower'],
        line=dict(color='gray', width=1, dash='dash'),
        name='BB Lower',
        fill='tonexty'
    ), row=1, col=1)
    
    # Volume
    colors = ['green' if row['Close'] >= row['Open'] else 'red' for index, row in data.iterrows()]
    fig.add_trace(go.Bar(
        x=data.index, y=data['Volume'],
        marker_color=colors,
        name='Volume',
        opacity=0.7
    ), row=2, col=1)
    
    # RSI
    fig.add_trace(go.Scatter(
        x=data.index, y=data['RSI'],
        line=dict(color='purple', width=2),
        name='RSI'
    ), row=3, col=1)
    
    # RSI levels
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
    
    fig.update_layout(
        title=f'{symbol} Technical Analysis',
        xaxis_rangeslider_visible=False,
        height=800,
        showlegend=True
    )
    
    return fig

def main():
    # Header
    st.markdown('<h1 class="main-header">📈 Financial Analytics Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("### Real-time Stock Analysis, Technical Indicators & Portfolio Management")
    
    # Sidebar
    st.sidebar.header("🔧 Configuration")
    
    # Stock selection
    default_symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NVDA', 'META', 'NFLX']
    selected_symbol = st.sidebar.selectbox("📊 Select Stock", default_symbols, index=0)
    
    # Time period
    period_options = {
        '1 Month': '1mo',
        '3 Months': '3mo', 
        '6 Months': '6mo',
        '1 Year': '1y',
        '2 Years': '2y',
        '5 Years': '5y'
    }
    selected_period = st.sidebar.selectbox("📅 Time Period", list(period_options.keys()), index=3)
    
    # Portfolio selection
    st.sidebar.subheader("💼 Portfolio Analysis")
    portfolio_symbols = st.sidebar.multiselect(
        "Select Portfolio Stocks",
        default_symbols,
        default=['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']
    )
    
    # Main content
    if selected_symbol:
        # Get data
        with st.spinner(f'Loading data for {selected_symbol}...'):
            data, info = get_stock_data(selected_symbol, period_options[selected_period])
        
        if data is not None and not data.empty:
            # Calculate indicators
            data = calculate_technical_indicators(data)
            
            # Current metrics
            current_price = data['Close'].iloc[-1]
            prev_close = data['Close'].iloc[-2]
            daily_change = current_price - prev_close
            daily_change_pct = (daily_change / prev_close) * 100
            
            # Display current info
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "💲 Current Price",
                    f"${current_price:.2f}",
                    f"{daily_change:+.2f} ({daily_change_pct:+.2f}%)"
                )
            
            with col2:
                market_cap = info.get('marketCap', 0) if info else 0
                st.metric(
                    "💰 Market Cap",
                    f"${market_cap/1e12:.2f}T" if market_cap > 1e12 else f"${market_cap/1e9:.1f}B"
                )
            
            with col3:
                volume = data['Volume'].iloc[-1]
                st.metric("📊 Volume", f"{volume/1e6:.1f}M")
            
            with col4:
                rsi = data['RSI'].iloc[-1] if not pd.isna(data['RSI'].iloc[-1]) else 0
                st.metric("📈 RSI", f"{rsi:.1f}")
            
            # Chart
            st.subheader(f"📊 {selected_symbol} Technical Analysis")
            chart = create_candlestick_chart(data, selected_symbol)
            st.plotly_chart(chart, use_container_width=True)
            
            # Trading Signals
            st.subheader("🚨 Trading Signals")
            signals = generate_trading_signals(data, selected_symbol)
            
            if signals:
                for signal in signals:
                    signal_color = "positive" if "BUY" in signal["type"] else "negative"
                    st.markdown(f"""
                    <div class="metric-card">
                        <span class="{signal_color}">{signal["type"]}</span> - {signal["reason"]} ({signal["strength"]})
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("💤 No clear trading signals at this time")
            
            # Technical Indicators Summary
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Technical Indicators")
                indicators_df = pd.DataFrame({
                    'Indicator': ['SMA 20', 'SMA 50', 'RSI', 'BB Upper', 'BB Lower'],
                    'Value': [
                        f"${data['SMA_20'].iloc[-1]:.2f}",
                        f"${data['SMA_50'].iloc[-1]:.2f}",
                        f"{data['RSI'].iloc[-1]:.1f}",
                        f"${data['BB_Upper'].iloc[-1]:.2f}",
                        f"${data['BB_Lower'].iloc[-1]:.2f}"
                    ]
                })
                st.dataframe(indicators_df, hide_index=True)
            
            with col2:
                st.subheader("📈 Performance Metrics")
                returns = data['Close'].pct_change().dropna()
                performance_df = pd.DataFrame({
                    'Metric': ['Daily Volatility', 'Monthly Return', 'Annual Volatility', 'Sharpe Ratio (approx)'],
                    'Value': [
                        f"{returns.std()*100:.2f}%",
                        f"{((current_price / data['Close'].iloc[0]) - 1)*100:.2f}%",
                        f"{returns.std() * np.sqrt(252) * 100:.2f}%",
                        f"{(returns.mean() / returns.std()) * np.sqrt(252):.2f}"
                    ]
                })
                st.dataframe(performance_df, hide_index=True)
    
    # Portfolio Analysis
    if portfolio_symbols:
        st.header("💼 Portfolio Analysis")
        
        portfolio_data = {}
        portfolio_metrics = []
        
        with st.spinner('Loading portfolio data...'):
            for symbol in portfolio_symbols:
                data, info = get_stock_data(symbol, "1mo")
                if data is not None and not data.empty:
                    current_price = data['Close'].iloc[-1]
                    monthly_return = ((current_price / data['Close'].iloc[0]) - 1) * 100
                    portfolio_data[symbol] = {
                        'Price': current_price,
                        'Monthly Return': monthly_return,
                        'Volume': data['Volume'].iloc[-1]
                    }
                    portfolio_metrics.append({
                        'Symbol': symbol,
                        'Price': f"${current_price:.2f}",
                        'Monthly Return': f"{monthly_return:+.2f}%",
                        'Volume': f"{data['Volume'].iloc[-1]/1e6:.1f}M"
                    })
        
        if portfolio_metrics:
            # Portfolio table
            portfolio_df = pd.DataFrame(portfolio_metrics)
            st.dataframe(portfolio_df, hide_index=True)
            
            # Portfolio performance chart
            returns_data = [data['Monthly Return'] for data in portfolio_data.values()]
            fig = px.bar(
                x=list(portfolio_data.keys()),
                y=returns_data,
                title="📊 Portfolio Monthly Returns",
                labels={'x': 'Symbol', 'y': 'Monthly Return (%)'},
                color=returns_data,
                color_continuous_scale='RdYlGn'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Portfolio summary
            avg_return = np.mean(returns_data)
            volatility = np.std(returns_data)
            best_performer = max(portfolio_data.items(), key=lambda x: x[1]['Monthly Return'])
            worst_performer = min(portfolio_data.items(), key=lambda x: x[1]['Monthly Return'])
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📈 Avg Return", f"{avg_return:+.2f}%")
            with col2:
                st.metric("⚡ Volatility", f"{volatility:.2f}%")
            with col3:
                st.metric("🏆 Best", f"{best_performer[0]} ({best_performer[1]['Monthly Return']:+.2f}%)")
            with col4:
                st.metric("📉 Worst", f"{worst_performer[0]} ({worst_performer[1]['Monthly Return']:+.2f}%)")
    
    # Footer
    st.markdown("---")
    st.markdown("### 🚀 About This Dashboard")
    st.markdown("""
    **Financial Analytics Dashboard** - A comprehensive real-time stock analysis platform featuring:
    - 📊 **Real-time data** from Yahoo Finance (Free API)
    - 🔍 **Technical indicators**: RSI, Moving Averages, Bollinger Bands, MACD
    - 📈 **Interactive charts** with candlestick visualization
    - 🚨 **Trading signals** based on technical analysis
    - 💼 **Portfolio management** and performance tracking
    - 📱 **Responsive design** for desktop and mobile
    
    **Data Sources**: Yahoo Finance • **Technology**: Python, Streamlit, Plotly • **Real-time Updates**: Every 5 minutes
    """)

if __name__ == "__main__":
    main()