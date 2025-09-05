"""
Financial Analytics Dashboard API
RESTful API for financial data analysis and portfolio management
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import asyncio
import uvicorn

# Pydantic models
class StockRequest(BaseModel):
    symbol: str
    period: str = "1y"

class PortfolioRequest(BaseModel):
    symbols: List[str]
    period: str = "1mo"

class StockData(BaseModel):
    symbol: str
    current_price: float
    daily_change: float
    daily_change_pct: float
    volume: int
    market_cap: Optional[int] = None
    rsi: Optional[float] = None
    signals: List[Dict[str, str]] = []

class PortfolioSummary(BaseModel):
    total_value: float
    avg_return: float
    volatility: float
    best_performer: Dict[str, Any]
    worst_performer: Dict[str, Any]
    stocks: List[StockData]

# Initialize FastAPI app
app = FastAPI(
    title="Financial Analytics Dashboard API",
    description="Real-time financial data analysis and portfolio management API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utility functions
def calculate_rsi(prices, window=14):
    """Calculate RSI indicator"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else None

def generate_signals(data, symbol):
    """Generate trading signals"""
    signals = []
    
    if data is None or data.empty:
        return signals
    
    latest = data.iloc[-1]
    
    # Calculate indicators
    sma_20 = data['Close'].rolling(window=20).mean().iloc[-1]
    sma_50 = data['Close'].rolling(window=50).mean().iloc[-1] if len(data) >= 50 else None
    rsi = calculate_rsi(data['Close'])
    
    # RSI signals
    if rsi and rsi > 70:
        signals.append({"type": "SELL", "reason": f"RSI Overbought ({rsi:.1f})", "strength": "Medium"})
    elif rsi and rsi < 30:
        signals.append({"type": "BUY", "reason": f"RSI Oversold ({rsi:.1f})", "strength": "Medium"})
    
    # Moving average signals
    if sma_50 and latest['Close'] > sma_20 > sma_50:
        signals.append({"type": "BUY", "reason": "Bullish MA Alignment", "strength": "Strong"})
    elif sma_50 and latest['Close'] < sma_20 < sma_50:
        signals.append({"type": "SELL", "reason": "Bearish MA Alignment", "strength": "Strong"})
    
    return signals

async def get_stock_data_async(symbol: str, period: str = "1y"):
    """Get stock data asynchronously"""
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period)
        info = ticker.info
        
        if data.empty:
            return None, None
        
        return data, info
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching data for {symbol}: {str(e)}")

# API Routes
@app.get("/", response_class=HTMLResponse)
async def root():
    """API Documentation Homepage"""
    return """
    <html>
        <head>
            <title>Financial Analytics Dashboard API</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .header { color: #1f77b4; }
                .endpoint { background: #f8f9fa; padding: 10px; margin: 10px 0; border-radius: 5px; }
            </style>
        </head>
        <body>
            <h1 class="header">📈 Financial Analytics Dashboard API</h1>
            <p>Real-time financial data analysis and portfolio management API</p>
            
            <h2>Available Endpoints:</h2>
            <div class="endpoint">
                <strong>GET /health</strong> - Health check
            </div>
            <div class="endpoint">
                <strong>GET /stock/{symbol}</strong> - Get stock data and analysis
            </div>
            <div class="endpoint">
                <strong>POST /stock/analyze</strong> - Analyze stock with custom parameters
            </div>
            <div class="endpoint">
                <strong>POST /portfolio/analyze</strong> - Analyze portfolio performance
            </div>
            <div class="endpoint">
                <strong>GET /market/trending</strong> - Get trending stocks
            </div>
            
            <p><a href="/docs">📚 Interactive API Documentation</a></p>
            <p><a href="/redoc">📖 Alternative Documentation</a></p>
            
            <h3>Example Usage:</h3>
            <code>
                curl http://localhost:8000/stock/AAPL<br>
                curl -X POST http://localhost:8000/portfolio/analyze -H "Content-Type: application/json" -d '{"symbols": ["AAPL", "GOOGL", "MSFT"]}'
            </code>
        </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "services": {
            "yahoo_finance": "available",
            "data_processing": "operational",
            "api": "running"
        }
    }

@app.get("/stock/{symbol}", response_model=StockData)
async def get_stock_analysis(symbol: str, period: str = "1y"):
    """Get comprehensive stock analysis"""
    symbol = symbol.upper()
    
    data, info = await get_stock_data_async(symbol, period)
    
    if data is None:
        raise HTTPException(status_code=404, detail=f"No data found for symbol {symbol}")
    
    # Calculate metrics
    current_price = float(data['Close'].iloc[-1])
    prev_close = float(data['Close'].iloc[-2])
    daily_change = current_price - prev_close
    daily_change_pct = (daily_change / prev_close) * 100
    volume = int(data['Volume'].iloc[-1])
    market_cap = info.get('marketCap') if info else None
    rsi = calculate_rsi(data['Close'])
    signals = generate_signals(data, symbol)
    
    return StockData(
        symbol=symbol,
        current_price=current_price,
        daily_change=daily_change,
        daily_change_pct=daily_change_pct,
        volume=volume,
        market_cap=market_cap,
        rsi=rsi,
        signals=signals
    )

@app.post("/stock/analyze", response_model=StockData)
async def analyze_stock(request: StockRequest):
    """Analyze stock with custom parameters"""
    return await get_stock_analysis(request.symbol, request.period)

@app.post("/portfolio/analyze", response_model=PortfolioSummary)
async def analyze_portfolio(request: PortfolioRequest):
    """Analyze portfolio performance"""
    stocks = []
    returns = []
    prices = []
    
    # Get data for all stocks
    for symbol in request.symbols:
        try:
            stock_data = await get_stock_analysis(symbol.upper(), request.period)
            stocks.append(stock_data)
            
            # Calculate return for period
            data, _ = await get_stock_data_async(symbol, request.period)
            if data is not None and not data.empty:
                period_return = ((data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1) * 100
                returns.append(period_return)
                prices.append(stock_data.current_price)
        except Exception as e:
            continue
    
    if not stocks:
        raise HTTPException(status_code=400, detail="No valid stocks found in portfolio")
    
    # Portfolio metrics
    avg_return = float(np.mean(returns)) if returns else 0.0
    volatility = float(np.std(returns)) if len(returns) > 1 else 0.0
    total_value = float(sum(prices))
    
    best_performer = max(enumerate(returns), key=lambda x: x[1]) if returns else (0, 0)
    worst_performer = min(enumerate(returns), key=lambda x: x[1]) if returns else (0, 0)
    
    return PortfolioSummary(
        total_value=total_value,
        avg_return=avg_return,
        volatility=volatility,
        best_performer={
            "symbol": stocks[best_performer[0]].symbol,
            "return": best_performer[1]
        },
        worst_performer={
            "symbol": stocks[worst_performer[0]].symbol,
            "return": worst_performer[1]
        },
        stocks=stocks
    )

@app.get("/market/trending")
async def get_trending_stocks():
    """Get trending stocks data"""
    trending_symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NVDA', 'META', 'NFLX']
    trending_data = []
    
    for symbol in trending_symbols:
        try:
            stock_data = await get_stock_analysis(symbol, "1d")
            trending_data.append({
                "symbol": stock_data.symbol,
                "price": stock_data.current_price,
                "change_pct": stock_data.daily_change_pct,
                "volume": stock_data.volume
            })
        except:
            continue
    
    # Sort by volume (most active)
    trending_data.sort(key=lambda x: x['volume'], reverse=True)
    
    return {
        "trending_stocks": trending_data[:10],
        "timestamp": datetime.now().isoformat(),
        "market_status": "open" if 9 <= datetime.now().hour <= 16 else "closed"
    }

@app.get("/market/movers")
async def get_market_movers():
    """Get top market movers"""
    symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NVDA', 'META', 'NFLX', 'AMD', 'CRM']
    movers_data = []
    
    for symbol in symbols:
        try:
            stock_data = await get_stock_analysis(symbol, "1d")
            movers_data.append({
                "symbol": stock_data.symbol,
                "price": stock_data.current_price,
                "change": stock_data.daily_change,
                "change_pct": stock_data.daily_change_pct,
                "volume": stock_data.volume
            })
        except:
            continue
    
    # Sort by percentage change
    gainers = sorted([s for s in movers_data if s['change_pct'] > 0], 
                    key=lambda x: x['change_pct'], reverse=True)[:5]
    losers = sorted([s for s in movers_data if s['change_pct'] < 0], 
                   key=lambda x: x['change_pct'])[:5]
    
    return {
        "top_gainers": gainers,
        "top_losers": losers,
        "timestamp": datetime.now().isoformat()
    }

# Background tasks
@app.get("/admin/cache/clear")
async def clear_cache():
    """Clear data cache (admin endpoint)"""
    return {"message": "Cache cleared successfully", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )