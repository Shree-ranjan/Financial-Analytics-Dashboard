"""
Configuration settings for Financial Analytics Dashboard
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings and configuration"""
    
    # Application Info
    app_name: str = "Financial Analytics Dashboard"
    app_version: str = "1.0.0"
    description: str = "Real-time Financial Analytics and Portfolio Management Platform"
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # External API Keys
    alpha_vantage_api_key: Optional[str] = Field(default=None, env="ALPHA_VANTAGE_API_KEY")
    # Yahoo Finance doesn't require an API key - it's free to use!
    polygon_api_key: Optional[str] = Field(default=None, env="POLYGON_API_KEY")
    
    # Database Configuration
    database_url: str = Field(default="sqlite:///./financial_data.db", env="DATABASE_URL")
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # Data Configuration
    default_symbols: List[str] = [
        "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", 
        "NVDA", "META", "NFLX", "AMD", "CRM"
    ]
    crypto_symbols: List[str] = [
        "BTC-USD", "ETH-USD", "ADA-USD", "DOT-USD", "LINK-USD"
    ]
    
    # Model Configuration
    forecast_days: int = Field(default=30, env="FORECAST_DAYS")
    retrain_interval_hours: int = Field(default=24, env="RETRAIN_INTERVAL_HOURS")
    
    # Risk Management
    max_portfolio_risk: float = Field(default=0.02, env="MAX_PORTFOLIO_RISK")  # 2%
    confidence_level: float = Field(default=0.95, env="CONFIDENCE_LEVEL")
    
    # Real-time Data
    data_refresh_seconds: int = Field(default=300, env="DATA_REFRESH_SECONDS")  # 5 minutes
    max_cache_age_minutes: int = Field(default=60, env="MAX_CACHE_AGE_MINUTES")
    
    # Paths
    data_dir: str = "data"
    models_dir: str = "outputs/models"
    reports_dir: str = "outputs/reports"
    charts_dir: str = "outputs/charts"
    
    # Streamlit Configuration
    streamlit_port: int = Field(default=8501, env="STREAMLIT_PORT")
    streamlit_host: str = Field(default="localhost", env="STREAMLIT_HOST")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()


def get_data_paths():
    """Get all data-related paths"""
    return {
        "raw": os.path.join(settings.data_dir, "raw"),
        "processed": os.path.join(settings.data_dir, "processed"),
        "cache": os.path.join(settings.data_dir, "cache"),
        "models": settings.models_dir,
        "reports": settings.reports_dir,
        "charts": settings.charts_dir
    }


def validate_api_keys():
    """Validate that required API keys are configured"""
    missing_keys = []
    
    if not settings.alpha_vantage_api_key:
        missing_keys.append("ALPHA_VANTAGE_API_KEY")
    
    return {
        "valid": len(missing_keys) == 0,
        "missing_keys": missing_keys,
        "configured_apis": [
            api for api in ["alpha_vantage", "polygon"] 
            if getattr(settings, f"{api}_api_key")
        ] + ["yahoo_finance"]  # Yahoo Finance is always available
    }


def get_market_hours():
    """Get market trading hours (US Eastern Time)"""
    return {
        "market_open": "09:30:00",
        "market_close": "16:00:00",
        "timezone": "US/Eastern",
        "trading_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    }


# Export settings for easy import
__all__ = ["settings", "get_data_paths", "validate_api_keys", "get_market_hours"]