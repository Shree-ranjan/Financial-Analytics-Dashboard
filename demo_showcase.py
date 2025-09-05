"""
Quick Demo of Financial Analytics Dashboard
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def generate_sample_data(symbol="DEMO", days=252):
    """Generate realistic sample stock data"""
    np.random.seed(42)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Realistic price movements
    initial_price = 100.0
    returns = np.random.normal(0.001, 0.02, len(dates))
    prices = initial_price * np.exp(np.cumsum(returns))
    
    volume = np.random.lognormal(15, 0.5, len(dates)).astype(int)
    
    return pd.DataFrame({
        'Open': prices,
        'High': prices * 1.02,
        'Low': prices * 0.98,
        'Close': prices,
        'Volume': volume
    }, index=dates)

def calculate_metrics(data):
    """Calculate key financial metrics"""
    returns = data['Close'].pct_change().dropna()
    
    return {
        'current_price': data['Close'].iloc[-1],
        'total_return': (data['Close'].iloc[-1] / data['Close'].iloc[0] - 1) * 100,
        'volatility': returns.std() * np.sqrt(252) * 100,
        'sharpe_ratio': (returns.mean() / returns.std()) * np.sqrt(252),
        'max_drawdown': ((data['Close'] / data['Close'].cummax()) - 1).min() * 100
    }

def simple_forecast(data, days=5):
    """Simple linear forecast"""
    recent_data = data['Close'].tail(30)
    x = np.arange(len(recent_data))
    trend = np.polyfit(x, recent_data.values, 1)[0]
    
    future_price = data['Close'].iloc[-1] + (trend * days)
    return {
        'prediction': future_price,
        'trend': 'bullish' if trend > 0 else 'bearish'
    }

def create_dashboard():
    """Create demo dashboard"""
    print("=" * 60)
    print("📈 FINANCIAL ANALYTICS DASHBOARD - DEMO")
    print("=" * 60)
    
    symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA']
    
    for i, symbol in enumerate(symbols):
        np.random.seed(i + 42)
        data = generate_sample_data(symbol)
        metrics = calculate_metrics(data)
        forecast = simple_forecast(data)
        
        print(f"\n🔍 {symbol}")
        print(f"Current: ${metrics['current_price']:.2f}")
        print(f"Return: {metrics['total_return']:+.1f}%")
        print(f"Volatility: {metrics['volatility']:.1f}%")
        print(f"Forecast: ${forecast['prediction']:.2f} ({forecast['trend']})")
    
    print("\n" + "=" * 60)
    print("✅ DEMO COMPLETED!")
    print("\n🚀 Full Features:")
    print("• Real-time data from Yahoo Finance & Alpha Vantage")
    print("• LSTM, ARIMA, Prophet forecasting models")
    print("• Portfolio optimization & risk analysis")
    print("• Interactive Streamlit dashboard")
    print("• Production FastAPI backend")
    print("• Comprehensive testing & deployment")
    print("=" * 60)

if __name__ == "__main__":
    create_dashboard()