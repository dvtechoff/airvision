'use client'

import { useState, useEffect, useCallback } from 'react'
import ForecastChart from '@/components/ForecastChart'
import AISuggestions from '@/components/AISuggestions'
import AlertBox from '@/components/AlertBox'
import { apiClient, ForecastData } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { RefreshCw, TrendingUp, BarChart3 } from 'lucide-react'
import { useCity } from '@/contexts/CityContext'

export default function ForecastPage() {
  const { selectedCity, setSelectedCity } = useCity();
  const [forecastData, setForecastData] = useState<ForecastData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedPollutant, setSelectedPollutant] = useState('aqi')

  const fetchForecast = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      
      const forecast = await apiClient.getForecast(selectedCity)
      setForecastData(forecast)
      console.log('Forecast data received:', forecast)
    } catch (err) {
      console.error('Forecast error:', err)
      setError(err instanceof Error ? err.message : 'Failed to fetch forecast data')
      
      // Generate realistic mock data based on current time and city
      const mockData = generateRealisticMockData(selectedCity)
      setForecastData(mockData)
    } finally {
      setLoading(false)
    }
  }, [selectedCity])

  const generateRealisticMockData = (cityName: string) => {
    const cityBaseAQI: { [key: string]: number } = {
      'new york': 85, 'los angeles': 120, 'chicago': 75, 'houston': 90,
      'phoenix': 95, 'philadelphia': 80, 'san antonio': 85, 'san diego': 70,
      'dallas': 95, 'austin': 80, 'seattle': 45, 'denver': 75
    }
    
    const baseAQI = cityBaseAQI[cityName.toLowerCase()] || 85
    const forecast = []
    
    for (let i = 0; i < 24; i++) {
      const time = new Date(Date.now() + i * 60 * 60 * 1000)
      const hour = time.getHours()
      
      // Rush hour patterns (higher AQI during 7-9am and 5-7pm)
      let hourFactor = 1.0
      if ((hour >= 7 && hour <= 9) || (hour >= 17 && hour <= 19)) {
        hourFactor = 1.3
      } else if (hour >= 22 || hour <= 5) {
        hourFactor = 0.7
      }
      
      // Add some realistic variation
      const variation = (Math.random() - 0.7) * 30
      const aqi = Math.max(20, Math.min(200, Math.round(baseAQI * hourFactor + variation)))
      
      let category = 'Good'
      if (aqi > 50) category = 'Moderate'
      if (aqi > 100) category = 'Unhealthy for Sensitive Groups'
      if (aqi > 150) category = 'Unhealthy'
      
      forecast.push({
        time: time.toISOString(),
        aqi,
        category
      })
    }
    
    return { city: cityName, forecast }
  }

  useEffect(() => {
    fetchForecast()
  }, [fetchForecast])

  const pollutants = [
    { value: 'aqi', label: 'Overall AQI' },
    { value: 'pm25', label: 'PM2.5' },
    { value: 'pm10', label: 'PM10' },
    { value: 'no2', label: 'NO₂' },
    { value: 'o3', label: 'O₃' }
  ]

  const getForecastInsights = () => {
    if (!forecastData) return null

    const currentAQI = forecastData.forecast[0]?.aqi || 0
    const maxAQI = Math.max(...forecastData.forecast.map(f => f.aqi))
    const minAQI = Math.min(...forecastData.forecast.map(f => f.aqi))
    const avgAQI = forecastData.forecast.reduce((sum, f) => sum + f.aqi, 0) / forecastData.forecast.length

    return {
      current: currentAQI,
      max: maxAQI,
      min: minAQI,
      average: Math.round(avgAQI),
      trend: maxAQI > currentAQI ? 'increasing' : 'decreasing'
    }
  }

  const insights = getForecastInsights()

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center space-x-2">
          <RefreshCw className="w-6 h-6 animate-spin" />
          <span>Loading forecast data...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-white text-black space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-black">Air Quality Forecast</h1>
          <p className="text-gray-700">24-hour predictions using real-time data and AI models</p>
        </div>
        <Button onClick={fetchForecast} disabled={loading} className="bg-blue-600 hover:bg-blue-700 text-white">
          <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* City Selector */}
      <Card className="bg-white border-gray-200 shadow-sm">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2 text-black">
            <BarChart3 className="w-5 h-5 text-blue-500" />
            <span>Select City</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Diego', 'Dallas', 'Austin', 'Seattle'].map((cityName) => (
              <Button
                key={cityName}
                variant={selectedCity === cityName ? "default" : "outline"}
                size="sm"
                onClick={() => setSelectedCity(cityName)}
                className={selectedCity === cityName ? "bg-blue-600 text-white" : "bg-white text-black border-gray-300 hover:bg-gray-100"}
              >
                {cityName}
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Pollutant Selector - HIDDEN */}
      {/* <Card className="bg-white border-gray-200 shadow-sm">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2 text-black">
            <BarChart3 className="w-5 h-5 text-blue-500" />
            <span>Select Metric</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {pollutants.map((pollutant) => (
              <Button
                key={pollutant.value}
                variant={selectedPollutant === pollutant.value ? "default" : "outline"}
                size="sm"
                onClick={() => setSelectedPollutant(pollutant.value)}
                className={selectedPollutant === pollutant.value ? "bg-blue-600 text-white" : "bg-white text-black border-gray-300 hover:bg-gray-100"}
              >
                {pollutant.label}
              </Button>
            ))}
          </div>
        </CardContent>
      </Card> */}

      {/* Forecast Chart */}
      {forecastData && (
        <ForecastChart data={forecastData} className="bg-white" />
      )}

      {/* Insights */}
      {insights && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="bg-white border-gray-200 shadow-sm">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Current AQI</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-black">{insights.current}</div>
              <div className="text-sm text-gray-500 mt-1">
                {insights.current <= 50 ? 'Good' : 
                 insights.current <= 100 ? 'Moderate' : 
                 insights.current <= 150 ? 'Unhealthy for Sensitive' :
                 insights.current <= 200 ? 'Unhealthy' : 'Very Unhealthy'}
              </div>
            </CardContent>
          </Card>
          <Card className="bg-white border-gray-200 shadow-sm">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Peak AQI (24h)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{insights.max}</div>
              <div className="text-sm text-gray-500 mt-1">Expected maximum</div>
            </CardContent>
          </Card>
          <Card className="bg-white border-gray-200 shadow-sm">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Best AQI (24h)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{insights.min}</div>
              <div className="text-sm text-gray-500 mt-1">Expected minimum</div>
            </CardContent>
          </Card>
          <Card className="bg-white border-gray-200 shadow-sm">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Average AQI</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-black">{insights.average}</div>
              <div className="text-sm text-gray-500 mt-1">24-hour average</div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Trend Alert */}
      {insights && insights.trend === 'increasing' && (
        <AlertBox
          type="warning"
          title="Rising Air Pollution Trend"
          description="Air quality is expected to deteriorate over the next 24 hours. Consider limiting outdoor activities during peak hours and using air purifiers indoors."
        />
      )}

      {/* AI-Powered Suggestions */}
      <AISuggestions 
        city={selectedCity} 
        className="w-full"
      />

      {/* Model Information */}
      <Card className="bg-white border-gray-200 shadow-sm">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2 text-black">
            <TrendingUp className="w-5 h-5 text-blue-500" />
            <span>AI Forecast Model</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <p className="text-sm text-gray-700">
              Our enhanced forecast model combines real-time OpenWeatherMap data with predictive algorithms 
              that account for weather patterns, traffic cycles, and seasonal trends to provide accurate 
              24-hour air quality predictions.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <h4 className="font-semibold mb-2 text-black">Real-Time Data Sources:</h4>
                <ul className="space-y-1 text-gray-700">
                  <li>• OpenWeatherMap Air Pollution API</li>
                  <li>• Current weather conditions</li>
                  <li>• NASA TEMPO satellite data</li>
                  <li>• Live traffic and emission patterns</li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold mb-2 text-black">Prediction Features:</h4>
                <ul className="space-y-1 text-gray-700">
                  <li>• Rush hour pollution modeling</li>
                  <li>• Weather-based dispersion factors</li>
                  <li>• Seasonal variation adjustments</li>
                  <li>• Multi-city baseline calibration</li>
                </ul>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {error && (
        <AlertBox
          type="error"
          title="Forecast Error"
          description={error}
        />
      )}
    </div>
  )
}
