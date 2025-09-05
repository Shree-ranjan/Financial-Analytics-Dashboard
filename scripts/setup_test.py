"""
Financial Analytics Dashboard - Setup and Configuration Test
Run this script to verify your installation and configuration
"""

import sys
import os
import warnings
warnings.filterwarnings('ignore')

def test_imports():
    """Test if all required packages are installed"""
    print("🔍 Testing package imports...")
    
    required_packages = [
        ('pandas', 'pd'),
        ('numpy', 'np'),
        ('yfinance', 'yf'),
        ('sklearn', 'sklearn'),
        ('tensorflow', 'tf'),
        ('fastapi', 'FastAPI'),
        ('streamlit', 'st'),
        ('plotly', 'plotly'),
        ('requests', 'requests')
    ]
    
    missing_packages = []
    
    for package, alias in required_packages:
        try:
            if alias:
                exec(f"import {package} as {alias}")
            else:
                exec(f"import {package}")
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - MISSING")
            missing_packages.append(package)
    
    # Test optional packages
    optional_packages = [
        ('alpha_vantage', 'Alpha Vantage'),
        ('prophet', 'Prophet (Facebook)')
    ]
    
    print("\n🔍 Testing optional packages...")
    for package, description in optional_packages:
        try:
            exec(f"import {package}")
            print(f"  ✅ {description}")
        except ImportError:
            print(f"  ⚠️  {description} - Optional (recommended)")
    
    return missing_packages

def test_configuration():
    """Test configuration settings"""
    print("\n🔧 Testing configuration...")
    
    try:
        from config.config import settings, validate_api_keys
        print("  ✅ Configuration loaded successfully")
        
        # Test API key validation
        validation_result = validate_api_keys()
        print(f"  🔑 API Keys validation: {validation_result}")
        
        # Test data directories
        from config.config import get_data_paths
        paths = get_data_paths()
        print(f"  📁 Data paths configured: {len(paths)} directories")
        
        return True
    except Exception as e:
        print(f"  ❌ Configuration error: {e}")
        return False

def test_data_ingestion():
    """Test data ingestion without API keys"""
    print("\n📊 Testing data ingestion...")
    
    try:
        # Test Yahoo Finance (no API key required)
        import yfinance as yf
        
        ticker = yf.Ticker("AAPL")
        data = ticker.history(period="5d")
        
        if not data.empty:
            print(f"  ✅ Yahoo Finance: Retrieved {len(data)} days of AAPL data")
            print(f"    Latest price: ${data['Close'].iloc[-1]:.2f}")
            return True
        else:
            print("  ❌ Yahoo Finance: No data retrieved")
            return False
            
    except Exception as e:
        print(f"  ❌ Data ingestion error: {e}")
        return False

def test_models():
    """Test model initialization"""
    print("\n🤖 Testing models...")
    
    try:
        from src.models.forecasting_models import ModelFactory
        
        # Test model factory
        available_models = ModelFactory.get_available_models()
        print(f"  ✅ Available models: {available_models}")
        
        # Test ARIMA model creation
        arima_model = ModelFactory.create_model('ARIMA', 'AAPL')
        print("  ✅ ARIMA model created successfully")
        
        return True
    except Exception as e:
        print(f"  ❌ Model testing error: {e}")
        return False

def create_sample_env_file():
    """Create a sample .env file if it doesn't exist"""
    env_path = ".env"
    if not os.path.exists(env_path):
        print("\n📝 Creating sample .env file...")
        try:
            with open(".env.example", 'r') as example:
                content = example.read()
            
            with open(env_path, 'w') as env_file:
                env_file.write(content)
            
            print("  ✅ Sample .env file created")
            print("  📝 Please edit .env file with your actual API keys")
        except Exception as e:
            print(f"  ❌ Error creating .env file: {e}")

def run_quick_demo():
    """Run a quick demonstration"""
    print("\n🚀 Running quick demo...")
    
    try:
        import yfinance as yf
        from src.models.forecasting_models import ARIMAForecaster
        
        # Get sample data
        ticker = yf.Ticker("AAPL")
        data = ticker.history(period="6m")
        
        if data.empty:
            print("  ❌ Could not fetch demo data")
            return False
        
        # Create and train ARIMA model
        model = ARIMAForecaster("AAPL")
        model.train(data)
        
        # Generate predictions
        predictions = model.predict(data, steps=5)
        
        print(f"  ✅ Demo completed successfully!")
        print(f"  📈 Current AAPL price: ${data['Close'].iloc[-1]:.2f}")
        print(f"  🔮 5-day predictions: {[f'${p:.2f}' for p in predictions['predictions']]}")
        print(f"  📊 Trend: {predictions['prediction_summary']['trend']}")
        
        return True
    except Exception as e:
        print(f"  ❌ Demo error: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("🏦 FINANCIAL ANALYTICS DASHBOARD - SETUP TEST")
    print("=" * 60)
    
    # Test imports
    missing_packages = test_imports()
    
    if missing_packages:
        print(f"\n❌ Missing packages: {missing_packages}")
        print("Please install missing packages using:")
        print("pip install -r requirements.txt")
        return False
    
    # Test configuration
    config_ok = test_configuration()
    
    # Create sample env file
    create_sample_env_file()
    
    # Test data ingestion
    data_ok = test_data_ingestion()
    
    # Test models
    models_ok = test_models()
    
    # Run demo if everything is working
    if config_ok and data_ok and models_ok:
        demo_ok = run_quick_demo()
        
        print("\n" + "=" * 60)
        print("🎉 SETUP TEST COMPLETED!")
        print("=" * 60)
        
        if demo_ok:
            print("✅ All systems operational!")
            print("\n🚀 Next steps:")
            print("  1. Edit .env file with your API keys")
            print("  2. Run: streamlit run src/dashboard/main_dashboard.py")
            print("  3. Or run: uvicorn src.api.main:app --reload")
        else:
            print("⚠️  Basic setup complete, but demo failed")
            print("Check error messages above for details")
    else:
        print("\n❌ Setup incomplete. Please check error messages above.")
    
    return True

if __name__ == "__main__":
    main()