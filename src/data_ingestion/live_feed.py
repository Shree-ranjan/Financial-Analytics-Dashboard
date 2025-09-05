"""
Real-time Financial Data Ingestion Module
Handles data collection from multiple financial APIs with caching and validation.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, AsyncGenerator
import pandas as pd
import yfinance as yf
import requests
from alpha_vantage.timeseries import TimeSeries
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from config.config import settings


class DataSource:
    """Base class for financial data sources"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.logger = logging.getLogger(self.__class__.__name__)
        self.rate_limit_delay = 1.0  # seconds between requests
        self.last_request_time = 0
    
    async def _rate_limit_check(self):
        """Ensure we don't exceed API rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Validate received data quality"""
        if data.empty:
            return False
        
        # Check for required columns
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in data.columns for col in required_cols):
            return False
        
        # Check for null values in price data
        if data[['Open', 'High', 'Low', 'Close']].isnull().any().any():
            return False
        
        # Check for negative prices
        if (data[['Open', 'High', 'Low', 'Close']] < 0).any().any():
            return False
        
        return True


class YahooFinanceSource(DataSource):
    """Yahoo Finance data source implementation"""
    
    def __init__(self):
        super().__init__()
        self.rate_limit_delay = 0.5  # Yahoo Finance is more lenient
    
    async def get_real_time_price(self, symbol: str) -> Dict[str, Any]:
        """Get real-time price for a symbol"""
        await self._rate_limit_check()
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            history = ticker.history(period="1d", interval="1m")
            
            if history.empty:
                raise ValueError(f"No data received for {symbol}")
            
            latest_data = history.iloc[-1]
            
            return {
                'symbol': symbol,
                'price': float(latest_data['Close']),
                'open': float(latest_data['Open']),
                'high': float(latest_data['High']),
                'low': float(latest_data['Low']),
                'volume': int(latest_data['Volume']),
                'timestamp': latest_data.name.isoformat(),
                'change': float(latest_data['Close'] - history.iloc[0]['Open']),
                'change_percent': float((latest_data['Close'] - history.iloc[0]['Open']) / history.iloc[0]['Open'] * 100),
                'market_cap': info.get('marketCap', None),
                'pe_ratio': info.get('trailingPE', None)
            }
        except Exception as e:
            self.logger.error(f"Error fetching real-time data for {symbol}: {e}")
            raise
    
    async def get_historical_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """Get historical data for a symbol"""
        await self._rate_limit_check()
        
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if not self.validate_data(data):
                raise ValueError(f"Invalid data received for {symbol}")
            
            # Add technical indicators
            data = self._add_technical_indicators(data)
            
            return data
        except Exception as e:
            self.logger.error(f"Error fetching historical data for {symbol}: {e}")
            raise
    
    def _add_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add common technical indicators to the data"""
        # Simple Moving Averages
        data['SMA_20'] = data['Close'].rolling(window=20).mean()
        data['SMA_50'] = data['Close'].rolling(window=50).mean()
        data['SMA_200'] = data['Close'].rolling(window=200).mean()
        
        # Exponential Moving Averages
        data['EMA_12'] = data['Close'].ewm(span=12).mean()
        data['EMA_26'] = data['Close'].ewm(span=26).mean()
        
        # MACD
        data['MACD'] = data['EMA_12'] - data['EMA_26']
        data['MACD_Signal'] = data['MACD'].ewm(span=9).mean()
        data['MACD_Histogram'] = data['MACD'] - data['MACD_Signal']
        
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
        
        return data


class AlphaVantageSource(DataSource):
    """Alpha Vantage data source implementation"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.ts = TimeSeries(key=api_key, output_format='pandas')
        self.rate_limit_delay = 12.0  # Alpha Vantage free tier: 5 calls per minute
    
    async def get_intraday_data(self, symbol: str, interval: str = "5min") -> pd.DataFrame:
        """Get intraday data from Alpha Vantage"""
        await self._rate_limit_check()
        
        try:
            data, meta_data = self.ts.get_intraday(symbol=symbol, interval=interval, outputsize='full')
            
            if not self.validate_data(data):
                raise ValueError(f"Invalid data received for {symbol}")
            
            # Rename columns to match our standard format
            data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            data.index.name = 'timestamp'
            
            return data
        except Exception as e:
            self.logger.error(f"Error fetching intraday data for {symbol}: {e}")
            raise
    
    async def get_daily_data(self, symbol: str, outputsize: str = "full") -> pd.DataFrame:
        """Get daily data from Alpha Vantage"""
        await self._rate_limit_check()
        
        try:
            data, meta_data = self.ts.get_daily(symbol=symbol, outputsize=outputsize)
            
            if not self.validate_data(data):
                raise ValueError(f"Invalid data received for {symbol}")
            
            # Rename columns to match our standard format
            data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            data.index.name = 'timestamp'
            
            return data
        except Exception as e:
            self.logger.error(f"Error fetching daily data for {symbol}: {e}")
            raise


class LiveDataFeed:
    """Real-time data feed orchestrator"""
    
    def __init__(self, symbols: List[str], update_interval: int = 300):
        self.symbols = symbols
        self.update_interval = update_interval  # seconds
        self.yahoo_source = YahooFinanceSource()
        self.alpha_vantage_source = None
        
        # Initialize Alpha Vantage if API key is available
        if settings.alpha_vantage_api_key:
            self.alpha_vantage_source = AlphaVantageSource(settings.alpha_vantage_api_key)
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self.is_running = False
        self.cache = {}
        self.cache_timestamps = {}
    
    async def start_streaming(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Start streaming real-time data for all symbols"""
        self.is_running = True
        self.logger.info(f"Starting real-time data stream for {len(self.symbols)} symbols")
        
        while self.is_running:
            batch_data = {}
            
            # Fetch data for all symbols
            tasks = [self._fetch_symbol_data(symbol) for symbol in self.symbols]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for symbol, result in zip(self.symbols, results):
                if isinstance(result, Exception):
                    self.logger.error(f"Error fetching data for {symbol}: {result}")
                else:
                    batch_data[symbol] = result
                    self.cache[symbol] = result
                    self.cache_timestamps[symbol] = datetime.now()
            
            if batch_data:
                yield {
                    'timestamp': datetime.now().isoformat(),
                    'data': batch_data,
                    'symbols_updated': len(batch_data),
                    'total_symbols': len(self.symbols)
                }
            
            # Wait for next update cycle
            await asyncio.sleep(self.update_interval)
    
    async def _fetch_symbol_data(self, symbol: str) -> Dict[str, Any]:
        """Fetch data for a single symbol"""
        try:
            # Check cache first
            if self._is_cache_valid(symbol):
                return self.cache[symbol]
            
            # Fetch from Yahoo Finance (primary source)
            data = await self.yahoo_source.get_real_time_price(symbol)
            return data
            
        except Exception as e:
            # Fallback to cached data if available
            if symbol in self.cache:
                self.logger.warning(f"Using cached data for {symbol} due to error: {e}")
                return self.cache[symbol]
            raise
    
    def _is_cache_valid(self, symbol: str) -> bool:
        """Check if cached data is still valid"""
        if symbol not in self.cache or symbol not in self.cache_timestamps:
            return False
        
        cache_age = datetime.now() - self.cache_timestamps[symbol]
        return cache_age.total_seconds() < settings.max_cache_age_minutes * 60
    
    def stop_streaming(self):
        """Stop the real-time data stream"""
        self.is_running = False
        self.logger.info("Stopping real-time data stream")
    
    async def get_batch_historical_data(self, symbols: List[str], period: str = "1y") -> Dict[str, pd.DataFrame]:
        """Get historical data for multiple symbols"""
        self.logger.info(f"Fetching historical data for {len(symbols)} symbols")
        
        tasks = [self.yahoo_source.get_historical_data(symbol, period) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        historical_data = {}
        for symbol, result in zip(symbols, results):
            if isinstance(result, Exception):
                self.logger.error(f"Error fetching historical data for {symbol}: {result}")
            else:
                historical_data[symbol] = result
        
        return historical_data


class DataManager:
    """Central data management and persistence"""
    
    def __init__(self):
        self.live_feed = None
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Ensure data directories exist
        os.makedirs(os.path.join(settings.data_dir, "raw"), exist_ok=True)
        os.makedirs(os.path.join(settings.data_dir, "processed"), exist_ok=True)
        os.makedirs(os.path.join(settings.data_dir, "cache"), exist_ok=True)
    
    def initialize_live_feed(self, symbols: List[str]) -> LiveDataFeed:
        """Initialize live data feed for specified symbols"""
        self.live_feed = LiveDataFeed(symbols, settings.data_refresh_seconds)
        return self.live_feed
    
    async def save_historical_data(self, symbols: List[str], period: str = "1y"):
        """Save historical data to disk"""
        if not self.live_feed:
            self.live_feed = LiveDataFeed(symbols)
        
        historical_data = await self.live_feed.get_batch_historical_data(symbols, period)
        
        for symbol, data in historical_data.items():
            # Save raw data
            raw_path = os.path.join(settings.data_dir, "raw", f"{symbol}_{period}.csv")
            data.to_csv(raw_path)
            
            # Save processed data (with technical indicators)
            processed_path = os.path.join(settings.data_dir, "processed", f"{symbol}_{period}_processed.csv")
            data.to_csv(processed_path)
            
            self.logger.info(f"Saved historical data for {symbol} to {raw_path}")
    
    def load_historical_data(self, symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
        """Load historical data from disk"""
        file_path = os.path.join(settings.data_dir, "processed", f"{symbol}_{period}_processed.csv")
        
        if os.path.exists(file_path):
            return pd.read_csv(file_path, index_col=0, parse_dates=True)
        return None


# Utility functions
async def test_data_sources():
    """Test all configured data sources"""
    results = {}
    
    # Test Yahoo Finance
    yahoo_source = YahooFinanceSource()
    try:
        test_data = await yahoo_source.get_real_time_price("AAPL")
        results["yahoo_finance"] = {"status": "success", "sample_data": test_data}
    except Exception as e:
        results["yahoo_finance"] = {"status": "error", "error": str(e)}
    
    # Test Alpha Vantage if configured
    if settings.alpha_vantage_api_key:
        av_source = AlphaVantageSource(settings.alpha_vantage_api_key)
        try:
            test_data = await av_source.get_daily_data("AAPL", outputsize="compact")
            results["alpha_vantage"] = {"status": "success", "rows": len(test_data)}
        except Exception as e:
            results["alpha_vantage"] = {"status": "error", "error": str(e)}
    else:
        results["alpha_vantage"] = {"status": "not_configured", "error": "API key not provided"}
    
    return results


if __name__ == "__main__":
    # Example usage
    async def main():
        # Test data sources
        print("Testing data sources...")
        test_results = await test_data_sources()
        for source, result in test_results.items():
            print(f"{source}: {result['status']}")
        
        # Initialize data manager
        data_manager = DataManager()
        
        # Save historical data for default symbols
        print("Saving historical data...")
        await data_manager.save_historical_data(settings.default_symbols[:3])  # Test with first 3 symbols
        
        # Test real-time feed
        print("Testing real-time feed...")
        live_feed = data_manager.initialize_live_feed(["AAPL", "GOOGL"])
        
        # Stream data for 30 seconds
        async for update in live_feed.start_streaming():
            print(f"Received update: {update['symbols_updated']} symbols at {update['timestamp']}")
            break  # Just test one update
        
        live_feed.stop_streaming()
        print("Data ingestion test completed!")
    
    # Run the test
    asyncio.run(main())