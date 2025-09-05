"""
Advanced Time Series Forecasting Models for Financial Data
Implements LSTM, ARIMA, Prophet, and ensemble methods for price prediction.
"""

import numpy as np
import pandas as pd
import warnings
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import joblib
import os
import sys

# Machine Learning & Deep Learning
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping

# Time Series Models
from statsmodels.tsa.arima.model import ARIMA
# import pmdarima as pm  # Optional - will use simple ARIMA if not available

# Prophet
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False

# Suppress warnings
warnings.filterwarnings('ignore')
tf.get_logger().setLevel('ERROR')


class BaseForecaster:
    """Base class for all forecasting models"""
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.model = None
        self.is_trained = False
        self.training_history = {}
        self.last_training_date = None
    
    def evaluate(self, actual: np.ndarray, predicted: np.ndarray) -> Dict[str, float]:
        """Evaluate model performance"""
        mse = mean_squared_error(actual, predicted)
        mae = mean_absolute_error(actual, predicted)
        rmse = np.sqrt(mse)
        r2 = r2_score(actual, predicted)
        
        # Calculate directional accuracy
        actual_direction = np.diff(actual) > 0
        predicted_direction = np.diff(predicted) > 0
        directional_accuracy = np.mean(actual_direction == predicted_direction)
        
        return {
            'mse': mse, 'mae': mae, 'rmse': rmse, 'r2': r2,
            'directional_accuracy': directional_accuracy
        }


class LSTMForecaster(BaseForecaster):
    """LSTM Neural Network for time series forecasting"""
    
    def __init__(self, symbol: str, lookback_window: int = 60, features: List[str] = None):
        super().__init__(symbol)
        self.lookback_window = lookback_window
        self.features = features or ['Close']
        self.scaler = MinMaxScaler()
    
    def prepare_data(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare data for LSTM training"""
        feature_data = data[self.features].values
        scaled_data = self.scaler.fit_transform(feature_data)
        
        X, y = [], []
        for i in range(self.lookback_window, len(scaled_data)):
            X.append(scaled_data[i-self.lookback_window:i])
            y.append(scaled_data[i, 0])
        
        return np.array(X), np.array(y)
    
    def build_model(self, input_shape: Tuple[int, int]) -> Sequential:
        """Build LSTM model architecture"""
        model = Sequential([
            LSTM(100, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(50, return_sequences=False),
            Dropout(0.2),
            Dense(25, activation='relu'),
            Dense(1, activation='linear')
        ])
        
        model.compile(optimizer=Adam(learning_rate=0.001), loss='mse', metrics=['mae'])
        return model
    
    def train(self, data: pd.DataFrame, epochs: int = 50) -> Dict[str, Any]:
        """Train the LSTM model"""
        X, y = self.prepare_data(data)
        
        if len(X) == 0:
            raise ValueError(f"Insufficient data for training LSTM model for {self.symbol}")
        
        self.model = self.build_model((X.shape[1], X.shape[2]))
        
        early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
        
        history = self.model.fit(
            X, y, epochs=epochs, batch_size=32, validation_split=0.2,
            callbacks=[early_stopping], verbose=0
        )
        
        self.is_trained = True
        self.last_training_date = datetime.now()
        self.training_history = {
            'final_loss': history.history['loss'][-1],
            'final_val_loss': history.history['val_loss'][-1],
            'epochs_trained': len(history.history['loss'])
        }
        
        return {'training_history': self.training_history}
    
    def predict(self, data: pd.DataFrame, steps: int = 30) -> Dict[str, Any]:
        """Generate LSTM predictions"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        feature_data = data[self.features].values
        scaled_data = self.scaler.transform(feature_data)
        last_sequence = scaled_data[-self.lookback_window:].reshape(1, self.lookback_window, len(self.features))
        
        predictions = []
        current_sequence = last_sequence.copy()
        
        for _ in range(steps):
            next_pred = self.model.predict(current_sequence, verbose=0)[0]
            predictions.append(next_pred[0])
            
            new_point = current_sequence[0, -1, :].copy()
            new_point[0] = next_pred[0]
            
            current_sequence = np.roll(current_sequence, -1, axis=1)
            current_sequence[0, -1, :] = new_point
        
        # Inverse transform predictions
        predictions = np.array(predictions).reshape(-1, 1)
        dummy_features = np.zeros((len(predictions), len(self.features)))
        dummy_features[:, 0] = predictions.flatten()
        predictions_scaled = self.scaler.inverse_transform(dummy_features)[:, 0]
        
        last_date = data.index[-1]
        prediction_dates = pd.date_range(start=last_date + timedelta(days=1), periods=steps, freq='D')
        
        return {
            'predictions': predictions_scaled.tolist(),
            'dates': prediction_dates.strftime('%Y-%m-%d').tolist(),
            'model_type': 'LSTM',
            'last_actual_price': float(data['Close'].iloc[-1]),
            'prediction_summary': {
                'trend': 'bullish' if predictions_scaled[-1] > predictions_scaled[0] else 'bearish'
            }
        }


class ARIMAForecaster(BaseForecaster):
    """ARIMA model for time series forecasting"""
    
    def __init__(self, symbol: str):
        super().__init__(symbol)
        self.order = None
    
    def train(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Train ARIMA model"""
        try:
            # Use simple ARIMA without auto-selection
            self.model = ARIMA(data['Close'], order=(1, 1, 1)).fit()
            self.order = (1, 1, 1)
        except:
            # Fallback to even simpler model
            self.model = ARIMA(data['Close'], order=(1, 0, 1)).fit()
            self.order = (1, 0, 1)
        
        self.is_trained = True
        self.last_training_date = datetime.now()
        
        return {'model_order': self.order}
    
    def predict(self, data: pd.DataFrame, steps: int = 30) -> Dict[str, Any]:
        """Generate ARIMA predictions"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        forecast = self.model.forecast(steps=steps)
        
        last_date = data.index[-1]
        prediction_dates = pd.date_range(start=last_date + timedelta(days=1), periods=steps, freq='D')
        
        predictions = forecast.tolist() if hasattr(forecast, 'tolist') else forecast
        
        return {
            'predictions': predictions,
            'dates': prediction_dates.strftime('%Y-%m-%d').tolist(),
            'model_type': 'ARIMA',
            'last_actual_price': float(data['Close'].iloc[-1]),
            'prediction_summary': {
                'trend': 'bullish' if predictions[-1] > predictions[0] else 'bearish'
            }
        }


class ProphetForecaster(BaseForecaster):
    """Prophet model for time series forecasting"""
    
    def __init__(self, symbol: str):
        super().__init__(symbol)
        if not PROPHET_AVAILABLE:
            raise ImportError("Prophet not available. Install with: pip install prophet")
    
    def train(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Train Prophet model"""
        prophet_data = pd.DataFrame({'ds': data.index, 'y': data['Close'].values})
        
        self.model = Prophet(
            daily_seasonality=True, weekly_seasonality=True,
            yearly_seasonality=True, changepoint_prior_scale=0.05
        )
        
        self.model.fit(prophet_data)
        self.is_trained = True
        self.last_training_date = datetime.now()
        
        return {'training_data_points': len(prophet_data)}
    
    def predict(self, data: pd.DataFrame, steps: int = 30) -> Dict[str, Any]:
        """Generate Prophet predictions"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        future = self.model.make_future_dataframe(periods=steps)
        forecast = self.model.predict(future)
        
        predictions = forecast['yhat'].tail(steps).values
        
        last_date = data.index[-1]
        prediction_dates = pd.date_range(start=last_date + timedelta(days=1), periods=steps, freq='D')
        
        return {
            'predictions': predictions.tolist(),
            'dates': prediction_dates.strftime('%Y-%m-%d').tolist(),
            'model_type': 'Prophet',
            'last_actual_price': float(data['Close'].iloc[-1]),
            'prediction_summary': {
                'trend': 'bullish' if predictions[-1] > predictions[0] else 'bearish'
            }
        }


class EnsembleForecaster:
    """Ensemble forecaster combining multiple models"""
    
    def __init__(self, symbol: str, models: List[str] = None):
        self.symbol = symbol
        self.models = {}
        self.weights = {}
        self.model_types = models or ['LSTM', 'ARIMA']
        
        if 'LSTM' in self.model_types:
            self.models['LSTM'] = LSTMForecaster(symbol)
        if 'ARIMA' in self.model_types:
            self.models['ARIMA'] = ARIMAForecaster(symbol)
        if 'Prophet' in self.model_types and PROPHET_AVAILABLE:
            self.models['Prophet'] = ProphetForecaster(symbol)
    
    def train_all_models(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Train all ensemble models"""
        training_results = {}
        
        for model_name, model in self.models.items():
            try:
                result = model.train(data)
                training_results[model_name] = result
            except Exception as e:
                training_results[model_name] = {'error': str(e)}
        
        # Equal weights for simplicity
        self.weights = {name: 1.0 / len(self.models) for name in self.models.keys()}
        
        return {'individual_results': training_results, 'model_weights': self.weights}
    
    def predict(self, data: pd.DataFrame, steps: int = 30) -> Dict[str, Any]:
        """Generate ensemble predictions"""
        individual_predictions = {}
        weighted_predictions = np.zeros(steps)
        
        for model_name, model in self.models.items():
            try:
                if model.is_trained:
                    pred_result = model.predict(data, steps)
                    individual_predictions[model_name] = pred_result
                    
                    weight = self.weights.get(model_name, 0)
                    if weight > 0:
                        weighted_predictions += np.array(pred_result['predictions']) * weight
            except Exception as e:
                continue
        
        last_date = data.index[-1]
        prediction_dates = pd.date_range(start=last_date + timedelta(days=1), periods=steps, freq='D')
        
        return {
            'predictions': weighted_predictions.tolist(),
            'dates': prediction_dates.strftime('%Y-%m-%d').tolist(),
            'model_type': 'Ensemble',
            'individual_predictions': individual_predictions,
            'model_weights': self.weights,
            'last_actual_price': float(data['Close'].iloc[-1]),
            'prediction_summary': {
                'trend': 'bullish' if weighted_predictions[-1] > weighted_predictions[0] else 'bearish'
            }
        }


class ModelFactory:
    """Factory class for creating forecasting models"""
    
    @staticmethod
    def create_model(model_type: str, symbol: str, **kwargs):
        """Create a forecasting model of the specified type"""
        model_type = model_type.upper()
        
        if model_type == 'LSTM':
            return LSTMForecaster(symbol, **kwargs)
        elif model_type == 'ARIMA':
            return ARIMAForecaster(symbol, **kwargs)
        elif model_type == 'PROPHET':
            return ProphetForecaster(symbol, **kwargs)
        elif model_type == 'ENSEMBLE':
            return EnsembleForecaster(symbol, **kwargs)
        else:
            raise ValueError(f"Unknown model type: {model_type}")
    
    @staticmethod
    def get_available_models():
        """Get list of available model types"""
        models = ['LSTM', 'ARIMA', 'ENSEMBLE']
        if PROPHET_AVAILABLE:
            models.append('PROPHET')
        return models


if __name__ == "__main__":
    import yfinance as yf
    
    print("Testing forecasting models...")
    ticker = yf.Ticker("AAPL")
    data = ticker.history(period="1y")
    
    # Test ensemble model
    ensemble_model = EnsembleForecaster("AAPL")
    ensemble_results = ensemble_model.train_all_models(data)
    predictions = ensemble_model.predict(data, steps=5)
    
    print(f"Ensemble predictions (5 days): {predictions['predictions']}")
    print("Forecasting models test completed!")