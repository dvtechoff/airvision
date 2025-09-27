# TEMPO Air Quality App

A comprehensive full-stack application for real-time air quality monitoring using NASA TEMPO satellite data, built for the NASA Space Challenge.

## 🌟 Features

- **Real-time Air Quality Monitoring**: Live AQI data from multiple sources
- **NASA TEMPO Integration**: Satellite-based pollution monitoring
- **AI-Powered Forecasting**: 24-hour AQI predictions using machine learning
- **Interactive Maps**: Visual representation of air quality data
- **Health Alerts**: Personalized recommendations based on air quality
- **Multi-source Data**: Combines satellite, ground, and weather data

## 🚀 Tech Stack

### Frontend
- **Next.js 14** with App Router
- **React 18** with TypeScript
- **TailwindCSS** for styling
- **ShadCN/UI** components
- **Recharts** for data visualization
- **Leaflet.js** for interactive maps
- **Framer Motion** for animations

### Backend
- **FastAPI** (Python)
- **Pandas & Xarray** for data processing
- **Scikit-learn** for machine learning
- **Statsmodels** for time series forecasting
- **OpenAQ API** for ground measurements
- **OpenWeatherMap API** for weather data

## 📁 Project Structure

```
tempo-air-quality-app/
├── frontend/                 # Next.js 14 frontend
│   ├── app/                 # App Router pages
│   │   ├── page.tsx         # Dashboard
│   │   ├── forecast/        # Forecast page
│   │   ├── alerts/          # Alerts page
│   │   └── about/           # About page
│   ├── components/          # React components
│   │   ├── ui/              # ShadCN UI components
│   │   ├── AQICard.tsx      # AQI display card
│   │   ├── WeatherCard.tsx  # Weather display card
│   │   ├── ForecastChart.tsx # Forecast visualization
│   │   ├── MapView.tsx      # Interactive map
│   │   └── AlertBox.tsx     # Alert notifications
│   ├── lib/                 # Utilities and API client
│   └── styles/              # Global styles
│
├── backend/                 # FastAPI backend
│   ├── routes/              # API endpoints
│   │   ├── current.py       # Current AQI endpoint
│   │   ├── forecast.py      # Forecast endpoint
│   │   └── weather.py       # Weather endpoint
│   ├── services/            # Data services
│   │   ├── openaq_service.py    # OpenAQ API integration
│   │   ├── weather_service.py   # Weather API integration
│   │   ├── tempo_service.py     # TEMPO data processing
│   │   └── forecast_service.py  # ML forecasting
│   ├── models/              # Data models
│   │   └── schemas.py       # Pydantic schemas
│   └── main.py              # FastAPI application
│
└── deployment/              # Deployment configs
    ├── vercel.json          # Vercel frontend config
    ├── render.yaml          # Render backend config
    └── Dockerfile           # Docker configuration
```

## 🛠️ Installation & Setup

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- Git

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create environment file:
```bash
cp .env.example .env.local
```

4. Update environment variables in `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

5. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create environment file:
```bash
cp env.example .env
```

5. Update environment variables in `.env`:
```env
OPENAQ_API_KEY=your_openaq_api_key
OPENWEATHER_API_KEY=your_openweathermap_api_key
EARTHDATA_USERNAME=your_earthdata_username
EARTHDATA_PASSWORD=your_earthdata_password
```

6. Start the development server:
```bash
uvicorn main:app --reload
```

The backend API will be available at `http://localhost:8000`

## 🌐 API Endpoints

### Current Air Quality
- `GET /api/current?city=Delhi` - Get current AQI data
- `GET /api/current/multiple?cities=Delhi,Mumbai` - Get multiple cities

### Forecast
- `GET /api/forecast?city=Delhi&hours=24` - Get AQI forecast
- `GET /api/forecast/accuracy` - Get model accuracy metrics

### Weather
- `GET /api/weather?city=Delhi` - Get current weather
- `GET /api/weather/forecast?city=Delhi&days=5` - Get weather forecast

## 🚀 Deployment

### Frontend (Vercel)

1. Connect your GitHub repository to Vercel
2. Set environment variables in Vercel dashboard:
   - `NEXT_PUBLIC_API_URL`: Your backend URL
3. Deploy automatically on push to main branch

### Backend (Render)

1. Connect your GitHub repository to Render
2. Set environment variables in Render dashboard
3. Deploy using the `render.yaml` configuration

### Alternative: Docker

1. Build the backend Docker image:
```bash
cd backend
docker build -t tempo-air-quality-backend .
```

2. Run the container:
```bash
docker run -p 8000:8000 tempo-air-quality-backend
```

## 📊 Data Sources

- **NASA TEMPO**: Tropospheric Emissions Monitoring of Pollution satellite
- **OpenAQ**: Open air quality data platform
- **OpenWeatherMap**: Weather data and forecasts

## 🤖 Machine Learning

The forecasting model uses:
- **ARIMA** for time series analysis
- **Scikit-learn** for regression models
- **Polynomial features** for non-linear relationships
- **Historical AQI data** for training

## 🎯 Key Features

### Dashboard
- Real-time AQI display with color-coded categories
- Weather information integration
- Interactive map with air quality markers
- Health recommendations

### Forecast
- 24-hour AQI predictions
- Multiple pollutant analysis
- Trend visualization with Recharts
- Model accuracy metrics

### Alerts
- Real-time air quality alerts
- Health recommendations
- Customizable notification preferences
- Severity-based categorization

### About
- Information about NASA TEMPO mission
- Technology stack details
- AQI scale explanation
- Data source information

## 🔧 Development

### Adding New Features

1. **Frontend Components**: Add to `frontend/components/`
2. **API Endpoints**: Add to `backend/routes/`
3. **Data Services**: Add to `backend/services/`
4. **Data Models**: Update `backend/models/schemas.py`

### Testing

```bash
# Frontend tests
cd frontend
npm run test

# Backend tests
cd backend
pytest
```

## 📝 Environment Variables

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend (.env)
```env
OPENAQ_API_KEY=your_openaq_api_key
OPENWEATHER_API_KEY=your_openweathermap_api_key
EARTHDATA_USERNAME=your_earthdata_username
EARTHDATA_PASSWORD=your_earthdata_password
DATABASE_URL=sqlite:///./tempo_air_quality.db
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- NASA for the TEMPO satellite mission
- OpenAQ for ground-based air quality data
- OpenWeatherMap for weather data
- The open-source community for amazing tools and libraries

## 📞 Support

For questions or support, please open an issue on GitHub or contact the development team.

---

**Built with ❤️ for the NASA Space Challenge**
