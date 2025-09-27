'use client'

import { useState, useEffect, useCallback } from 'react'
import ForecastChart from '@/components/ForecastChart'
import AlertBox from '@/components/AlertBox'
import { apiClient, ForecastData } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { RefreshCw, TrendingUp, BarChart3 } from 'lucide-react'

export default function ForecastPage() {
  const [forecastData, setForecastData] = useState<ForecastData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [city, setCity] = useState('Delhi')
  const [selectedPollutant, setSelectedPollutant] = useState('aqi')

  const fetchForecast = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      
      const forecast = await apiClient.getForecast(city)
      setForecastData(forecast)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch forecast data')
      // Set mock data for demo purposes
      setForecastData({
        city: city,
        forecast: [
          { time: new Date(Date.now() + 0 * 60 * 60 * 1000).toISOString(), aqi: 175, category: "Unhealthy" },
          { time: new Date(Date.now() + 1 * 60 * 60 * 1000).toISOString(), aqi: 180, category: "Unhealthy" },
          { time: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString(), aqi: 185, category: "Unhealthy" },
          { time: new Date(Date.now() + 3 * 60 * 60 * 1000).toISOString(), aqi: 190, category: "Unhealthy" },
          { time: new Date(Date.now() + 4 * 60 * 60 * 1000).toISOString(), aqi: 195, category: "Unhealthy" },
          { time: new Date(Date.now() + 5 * 60 * 60 * 1000).toISOString(), aqi: 200, category: "Very Unhealthy" },
          { time: new Date(Date.now() + 6 * 60 * 60 * 1000).toISOString(), aqi: 205, category: "Very Unhealthy" },
          { time: new Date(Date.now() + 7 * 60 * 60 * 1000).toISOString(), aqi: 210, category: "Very Unhealthy" },
          { time: new Date(Date.now() + 8 * 60 * 60 * 1000).toISOString(), aqi: 215, category: "Very Unhealthy" },
          { time: new Date(Date.now() + 9 * 60 * 60 * 1000).toISOString(), aqi: 220, category: "Very Unhealthy" },
          { time: new Date(Date.now() + 10 * 60 * 60 * 1000).toISOString(), aqi: 225, category: "Very Unhealthy" },
          { time: new Date(Date.now() + 11 * 60 * 60 * 1000).toISOString(), aqi: 230, category: "Very Unhealthy" },
          { time: new Date(Date.now() + 12 * 60 * 60 * 1000).toISOString(), aqi: 235, category: "Very Unhealthy" },
          { time: new Date(Date.now() + 13 * 60 * 60 * 1000).toISOString(), aqi: 240, category: "Very Unhealthy" },
          { time: new Date(Date.now() + 14 * 60 * 60 * 1000).toISOString(), aqi: 245, category: "Very Unhealthy" },
          { time: new Date(Date.now() + 15 * 60 * 60 * 1000).toISOString(), aqi: 250, category: "Very Unhealthy" },
          { time: new Date(Date.now() + 16 * 60 * 60 * 1000).toISOString(), aqi: 255, category: "Very Unhealthy" },
          { time: new Date(Date.now() + 17 * 60 * 60 * 1000).toISOString(), aqi: 260, category: "Very Unhealthy" },
          { time: new Date(Date.now() + 18 * 60 * 60 * 1000).toISOString(), aqi: 265, category: "Very Unhealthy" },
          { time: new Date(Date.now() + 19 * 60 * 60 * 1000).toISOString(), aqi: 270, category: "Very Unhealthy" },
          { time: new Date(Date.now() + 20 * 60 * 60 * 1000).toISOString(), aqi: 275, category: "Very Unhealthy" },
          { time: new Date(Date.now() + 21 * 60 * 60 * 1000).toISOString(), aqi: 280, category: "Very Unhealthy" },
          { time: new Date(Date.now() + 22 * 60 * 60 * 1000).toISOString(), aqi: 285, category: "Very Unhealthy" },
          { time: new Date(Date.now() + 23 * 60 * 60 * 1000).toISOString(), aqi: 290, category: "Very Unhealthy" },
        ]
      })
    } finally {
      setLoading(false)
    }
  }, [city])

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
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Air Quality Forecast</h1>
          <p className="text-gray-600">24-hour predictions powered by machine learning models</p>
        </div>
        <Button onClick={fetchForecast} disabled={loading}>
          <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Pollutant Selector */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <BarChart3 className="w-5 h-5 text-blue-500" />
            <span>Select Pollutant</span>
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
              >
                {pollutant.label}
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Forecast Chart */}
      {forecastData && (
        <ForecastChart data={forecastData} />
      )}

      {/* Insights */}
      {insights && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Current AQI</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{insights.current}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Peak AQI</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{insights.max}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Lowest AQI</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{insights.min}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Average AQI</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{insights.average}</div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Trend Alert */}
      {insights && insights.trend === 'increasing' && (
        <AlertBox
          type="warning"
          title="Rising Air Pollution"
          description="Air quality is expected to worsen over the next 24 hours. Consider limiting outdoor activities and using air purifiers indoors."
        />
      )}

      {/* Model Information */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <TrendingUp className="w-5 h-5 text-blue-500" />
            <span>Forecast Model</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <p className="text-sm text-gray-600">
              Our forecast model uses ARIMA (AutoRegressive Integrated Moving Average) to predict air quality trends 
              based on historical data from NASA TEMPO satellite observations and ground-based measurements.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <h4 className="font-semibold mb-2">Data Sources:</h4>
                <ul className="space-y-1 text-gray-600">
                  <li>• NASA TEMPO satellite data</li>
                  <li>• OpenAQ ground measurements</li>
                  <li>• Weather patterns and trends</li>
                  <li>• Historical AQI patterns</li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold mb-2">Model Features:</h4>
                <ul className="space-y-1 text-gray-600">
                  <li>• 24-hour prediction window</li>
                  <li>• Hourly granularity</li>
                  <li>• Multi-pollutant analysis</li>
                  <li>• Confidence intervals</li>
                </ul>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {error && (
        <AlertBox
          type="error"
          title="Error"
          description={error}
        />
      )}
    </div>
  )
}
