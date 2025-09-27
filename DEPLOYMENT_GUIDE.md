# 🚀 Deployment Guide - TEMPO Air Quality App

## 📋 Prerequisites

Before deploying, ensure you have:
- GitHub account
- Vercel account (for frontend)
- Render account (for backend)
- API keys for external services

## 🔑 Required API Keys

### OpenAQ API
1. Visit [OpenAQ API](https://openaq.org/#/api)
2. Sign up for a free account
3. Get your API key from the dashboard

### OpenWeatherMap API
1. Visit [OpenWeatherMap API](https://openweathermap.org/api)
2. Sign up for a free account
3. Get your API key from the API keys section

### NASA EarthData (Optional)
1. Visit [NASA EarthData](https://urs.earthdata.nasa.gov/)
2. Create an account
3. Generate credentials for data access

## 🌐 Frontend Deployment (Vercel)

### Step 1: Prepare Repository
```bash
# Ensure all files are committed
git add .
git commit -m "Ready for deployment"
git push origin main
```

### Step 2: Connect to Vercel
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import your GitHub repository
4. Select the `frontend` folder as the root directory

### Step 3: Configure Environment Variables
In Vercel dashboard, go to Settings → Environment Variables:
```
NEXT_PUBLIC_API_URL=https://your-backend-url.onrender.com
```

### Step 4: Deploy
1. Click "Deploy"
2. Wait for deployment to complete
3. Your app will be available at `https://your-app.vercel.app`

## ⚡ Backend Deployment (Render)

### Step 1: Prepare Repository
Ensure your `render.yaml` file is in the root directory.

### Step 2: Connect to Render
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Select the repository

### Step 3: Configure Service
- **Name**: `tempo-air-quality-backend`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Step 4: Set Environment Variables
In Render dashboard, go to Environment:
```
OPENAQ_API_KEY=your_openaq_api_key
OPENWEATHER_API_KEY=your_openweathermap_api_key
EARTHDATA_USERNAME=your_earthdata_username
EARTHDATA_PASSWORD=your_earthdata_password
DATABASE_URL=sqlite:///./tempo_air_quality.db
ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

### Step 5: Deploy
1. Click "Create Web Service"
2. Wait for deployment to complete
3. Your API will be available at `https://your-backend.onrender.com`

## 🐳 Docker Deployment (Alternative)

### Step 1: Build Backend Image
```bash
cd backend
docker build -t tempo-air-quality-backend .
```

### Step 2: Run Container
```bash
docker run -p 8000:8000 \
  -e OPENAQ_API_KEY=your_key \
  -e OPENWEATHER_API_KEY=your_key \
  tempo-air-quality-backend
```

### Step 3: Deploy to Cloud
- **AWS ECS**: Use the Docker image
- **Google Cloud Run**: Deploy container
- **Azure Container Instances**: Run container

## 🔧 Environment Configuration

### Frontend Environment Variables
```env
# Production
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com

# Development
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend Environment Variables
```env
# API Keys
OPENAQ_API_KEY=your_openaq_api_key
OPENWEATHER_API_KEY=your_openweathermap_api_key

# NASA EarthData
EARTHDATA_USERNAME=your_username
EARTHDATA_PASSWORD=your_password

# Database
DATABASE_URL=sqlite:///./tempo_air_quality.db

# CORS
ALLOWED_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000

# Model Settings
MODEL_RETRAIN_HOURS=24
FORECAST_HORIZON_HOURS=24
```

## 🚀 Quick Deployment Script

Create a deployment script for easy setup:

```bash
#!/bin/bash
# deploy.sh

echo "🚀 Starting deployment process..."

# Check if git is clean
if [[ -n $(git status -s) ]]; then
    echo "❌ Git working directory is not clean. Please commit changes first."
    exit 1
fi

# Push to GitHub
echo "📤 Pushing to GitHub..."
git push origin main

# Deploy to Vercel (if vercel CLI is installed)
if command -v vercel &> /dev/null; then
    echo "🌐 Deploying frontend to Vercel..."
    cd frontend
    vercel --prod
    cd ..
fi

# Deploy to Render (if render CLI is installed)
if command -v render &> /dev/null; then
    echo "⚡ Deploying backend to Render..."
    render deploy
fi

echo "✅ Deployment complete!"
echo "Frontend: https://your-app.vercel.app"
echo "Backend: https://your-backend.onrender.com"
```

## 🔍 Post-Deployment Testing

### Test Frontend
1. Visit your Vercel URL
2. Check if the dashboard loads
3. Test API calls to backend
4. Verify responsive design

### Test Backend
1. Visit `https://your-backend.onrender.com/docs`
2. Test API endpoints
3. Check health endpoint
4. Verify CORS configuration

### Test Integration
1. Frontend should connect to backend
2. Data should load correctly
3. Maps should display
4. Charts should render

## 🐛 Troubleshooting

### Common Issues

#### Frontend Issues
- **API Connection Failed**: Check `NEXT_PUBLIC_API_URL`
- **Build Errors**: Check for TypeScript errors
- **Environment Variables**: Ensure variables are set in Vercel

#### Backend Issues
- **API Keys Invalid**: Verify API keys are correct
- **CORS Errors**: Check `ALLOWED_ORIGINS` setting
- **Memory Issues**: Upgrade Render plan if needed

#### Integration Issues
- **Data Not Loading**: Check backend logs
- **CORS Errors**: Verify frontend URL in backend config
- **Rate Limiting**: Check API rate limits

### Debug Commands

```bash
# Check frontend build
cd frontend
npm run build

# Check backend locally
cd backend
uvicorn main:app --reload

# Test API endpoints
curl https://your-backend.onrender.com/health
curl https://your-backend.onrender.com/api/current?city=Delhi
```

## 📊 Monitoring & Maintenance

### Health Checks
- **Frontend**: Vercel provides automatic monitoring
- **Backend**: Render provides basic monitoring
- **API**: Use `/health` endpoint for status

### Logs
- **Frontend**: Check Vercel function logs
- **Backend**: Check Render service logs
- **API**: Monitor API response times

### Updates
- **Frontend**: Automatic deployment on git push
- **Backend**: Manual deployment or webhook
- **Dependencies**: Regular security updates

## 🔒 Security Considerations

### API Security
- Use HTTPS for all communications
- Validate all input data
- Implement rate limiting
- Monitor for abuse

### Data Privacy
- No personal data collection
- Use environment variables for secrets
- Regular security audits
- Keep dependencies updated

## 📈 Scaling Considerations

### Frontend Scaling
- Vercel handles automatic scaling
- CDN distribution worldwide
- Edge functions for performance

### Backend Scaling
- Upgrade Render plan for more resources
- Implement caching strategies
- Use database for persistent storage
- Consider microservices architecture

## 🎯 Production Checklist

- [ ] All environment variables set
- [ ] API keys configured
- [ ] CORS properly configured
- [ ] Health checks working
- [ ] Error handling implemented
- [ ] Logging configured
- [ ] Monitoring set up
- [ ] Security measures in place
- [ ] Performance optimized
- [ ] Documentation updated

## 🆘 Support

### Getting Help
- Check the main README.md
- Review API documentation
- Check GitHub issues
- Contact development team

### Common Resources
- [Vercel Documentation](https://vercel.com/docs)
- [Render Documentation](https://render.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)

---

## 🎉 Deployment Complete!

Your TEMPO Air Quality App is now live and ready to help users monitor air quality using NASA satellite data!

**Frontend**: https://your-app.vercel.app
**Backend**: https://your-backend.onrender.com
**API Docs**: https://your-backend.onrender.com/docs

---

*Built with ❤️ for the NASA Space Challenge*
