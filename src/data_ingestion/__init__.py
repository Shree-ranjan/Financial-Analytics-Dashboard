"""
Data Ingestion Package
Real-time financial data collection and management
"""

from .live_feed import (
    DataSource,
    YahooFinanceSource, 
    AlphaVantageSource,
    LiveDataFeed,
    DataManager,
    test_data_sources
)

__all__ = [
    "DataSource",
    "YahooFinanceSource", 
    "AlphaVantageSource",
    "LiveDataFeed",
    "DataManager",
    "test_data_sources"
]