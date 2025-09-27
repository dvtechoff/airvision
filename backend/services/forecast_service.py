import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import joblib
import os

from models.schemas import ForecastData, ForecastPoint

class ForecastService:
    """
    Service for generating AQI forecasts using machine learning models.
    """
    
    def __init__(self):
        self.model = None
        self.model_path = "models/aqi_forecast_model.pkl"
        self.load_model()
    
    def load_model(self):
        """
        Load the trained forecasting model.
        """
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
            else:
                # Create a new model if none exists
                self.model = self._create_new_model()
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = self._create_new_model()
    
    def _create_new_model(self):
        """
        Create a new forecasting model.
        """
        # For demo purposes, we'll use a simple linear regression
        # In production, you might use ARIMA, LSTM, or other time series models
        return LinearRegression()
    
    async def get_forecast(self, city: str, hours: int = 24) -> ForecastData:
        """
        Generate AQI forecast for a city.
        """
        try:
            # Get historical data for the city
            historical_data = await self._get_historical_data(city)
            
            if not historical_data:
                # Return mock forecast if no historical data
                return self._generate_mock_forecast(city, hours)
            
            # Generate forecast
            forecast_points = self._generate_forecast_points(historical_data, hours)
            
            return ForecastData(
                city=city,
                forecast=forecast_points
            )
            
        except Exception as e:
            print(f"Error generating forecast: {e}")
            return self._generate_mock_forecast(city, hours)
    
    async def _get_historical_data(self, city: str) -> List[Dict[str, Any]]:
        """
        Get historical AQI data for training/forecasting.
        In production, this would fetch from a database.
        """
        # For demo purposes, generate synthetic historical data
        return self._generate_synthetic_historical_data(city)
    
    def _generate_synthetic_historical_data(self, city: str) -> List[Dict[str, Any]]:
        """
        Generate synthetic historical data for demonstration.
        """
        data = []
        base_time = datetime.now() - timedelta(days=30)
        
        # Generate 30 days of hourly data
        for i in range(30 * 24):
            timestamp = base_time + timedelta(hours=i)
            
            # Simulate realistic AQI patterns
            # Higher AQI during rush hours and lower at night
            hour = timestamp.hour
            day_of_week = timestamp.weekday()
            
            # Base AQI with daily and weekly patterns
            base_aqi = 100
            hour_factor = 1.2 if 7 <= hour <= 9 or 17 <= hour <= 19 else 0.8
            day_factor = 1.1 if day_of_week < 5 else 0.9  # Weekdays vs weekends
            
            # Add some randomness
            noise = np.random.normal(0, 20)
            
            aqi = max(0, min(500, int(base_aqi * hour_factor * day_factor + noise)))
            
            data.append({
                "timestamp": timestamp,
                "aqi": aqi,
                "hour": hour,
                "day_of_week": day_of_week
            })
        
        return data
    
    def _generate_forecast_points(self, historical_data: List[Dict[str, Any]], hours: int) -> List[ForecastPoint]:
        """
        Generate forecast points using the trained model.
        """
        forecast_points = []
        
        # Convert historical data to DataFrame
        df = pd.DataFrame(historical_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.set_index('timestamp')
        
        # Prepare features for forecasting
        features = ['aqi', 'hour', 'day_of_week']
        X = df[features].values
        y = df['aqi'].values
        
        # Train a simple model for this forecast
        # In production, you'd use a more sophisticated time series model
        if len(X) > 10:
            try:
                # Use polynomial features for non-linear relationships
                poly_features = PolynomialFeatures(degree=2, include_bias=False)
                X_poly = poly_features.fit_transform(X)
                
                # Train the model
                self.model.fit(X_poly, y)
                
                # Generate forecast
                for i in range(hours):
                    forecast_time = datetime.now() + timedelta(hours=i)
                    hour = forecast_time.hour
                    day_of_week = forecast_time.weekday()
                    
                    # Use recent AQI as base
                    recent_aqi = df['aqi'].iloc[-1] if len(df) > 0 else 100
                    
                    # Create feature vector
                    feature_vector = np.array([[recent_aqi, hour, day_of_week]])
                    feature_vector_poly = poly_features.transform(feature_vector)
                    
                    # Predict AQI
                    predicted_aqi = max(0, min(500, int(self.model.predict(feature_vector_poly)[0])))
                    
                    # Determine category
                    category = self._get_aqi_category(predicted_aqi)
                    
                    forecast_points.append(ForecastPoint(
                        time=forecast_time,
                        aqi=predicted_aqi,
                        category=category
                    ))
                    
            except Exception as e:
                print(f"Error in model prediction: {e}")
                # Fallback to simple trend-based forecast
                forecast_points = self._generate_simple_forecast(historical_data, hours)
        else:
            # Not enough data, generate simple forecast
            forecast_points = self._generate_simple_forecast(historical_data, hours)
        
        return forecast_points
    
    def _generate_simple_forecast(self, historical_data: List[Dict[str, Any]], hours: int) -> List[ForecastPoint]:
        """
        Generate a simple trend-based forecast when model prediction fails.
        """
        forecast_points = []
        
        if not historical_data:
            return self._generate_mock_forecast_points(hours)
        
        # Calculate trend from recent data
        recent_aqis = [d['aqi'] for d in historical_data[-24:]]  # Last 24 hours
        if len(recent_aqis) > 1:
            trend = (recent_aqis[-1] - recent_aqis[0]) / len(recent_aqis)
            base_aqi = recent_aqis[-1]
        else:
            trend = 0
            base_aqi = 100
        
        # Generate forecast with trend
        for i in range(hours):
            forecast_time = datetime.now() + timedelta(hours=i)
            
            # Apply trend and add some variation
            predicted_aqi = max(0, min(500, int(base_aqi + trend * i + np.random.normal(0, 10))))
            category = self._get_aqi_category(predicted_aqi)
            
            forecast_points.append(ForecastPoint(
                time=forecast_time,
                aqi=predicted_aqi,
                category=category
            ))
        
        return forecast_points
    
    def _generate_mock_forecast_points(self, hours: int) -> List[ForecastPoint]:
        """
        Generate mock forecast points when no data is available.
        """
        forecast_points = []
        base_aqi = 150
        
        for i in range(hours):
            forecast_time = datetime.now() + timedelta(hours=i)
            
            # Simulate realistic AQI variation
            variation = np.random.normal(0, 20)
            predicted_aqi = max(0, min(500, int(base_aqi + variation + (i * 2))))
            category = self._get_aqi_category(predicted_aqi)
            
            forecast_points.append(ForecastPoint(
                time=forecast_time,
                aqi=predicted_aqi,
                category=category
            ))
        
        return forecast_points
    
    def _get_aqi_category(self, aqi: int) -> str:
        """
        Get AQI category based on AQI value.
        """
        if aqi <= 50:
            return "Good"
        elif aqi <= 100:
            return "Moderate"
        elif aqi <= 150:
            return "Unhealthy for Sensitive Groups"
        elif aqi <= 200:
            return "Unhealthy"
        elif aqi <= 300:
            return "Very Unhealthy"
        else:
            return "Hazardous"
    
    def _generate_mock_forecast(self, city: str, hours: int) -> ForecastData:
        """
        Generate mock forecast data for demonstration.
        """
        forecast_points = self._generate_mock_forecast_points(hours)
        
        return ForecastData(
            city=city,
            forecast=forecast_points
        )
    
    def save_model(self):
        """
        Save the trained model to disk.
        """
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump(self.model, self.model_path)
        except Exception as e:
            print(f"Error saving model: {e}")
