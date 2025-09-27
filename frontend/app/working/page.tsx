'use client'

import { useState, useEffect } from 'react'

interface AirQualityData {
  city: string
  aqi: number
  category: string
  pollutants: {
    pm25: number
    pm10: number
    no2: number
    o3: number
  }
  source: string
  timestamp: string
}

interface WeatherData {
  temperature: number
  humidity: number
  wind_speed: number
  conditions: string
  pressure: number
  visibility: number
}

export default function WorkingPage() {
  const [aqiData, setAqiData] = useState<AirQualityData | null>(null)
  const [weatherData, setWeatherData] = useState<WeatherData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [city, setCity] = useState('New York')

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    setLoading(true)
    setError(null)
    
    try {
      console.log('Fetching data...')
      
      // Fetch AQI data
      const aqiResponse = await fetch(`http://localhost:8000/api/current?city=${encodeURIComponent(city)}`)
      console.log('AQI Response status:', aqiResponse.status)
      
      if (!aqiResponse.ok) {
        throw new Error(`AQI API error: ${aqiResponse.status}`)
      }
      
      const aqiJson = await aqiResponse.json()
      console.log('AQI data:', aqiJson)
      setAqiData(aqiJson)
      
      // Fetch weather data
      const weatherResponse = await fetch(`http://localhost:8000/api/weather?city=${encodeURIComponent(city)}`)
      console.log('Weather Response status:', weatherResponse.status)
      
      if (!weatherResponse.ok) {
        throw new Error(`Weather API error: ${weatherResponse.status}`)
      }
      
      const weatherJson = await weatherResponse.json()
      console.log('Weather data:', weatherJson)
      setWeatherData(weatherJson)
      
    } catch (err) {
      console.error('Fetch error:', err)
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center">
        <div className="bg-white rounded-xl shadow-lg p-8 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading air quality data...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 to-pink-50 flex items-center justify-center">
        <div className="bg-white rounded-xl shadow-lg p-8 text-center max-w-md">
          <div className="text-red-600 text-6xl mb-4">⚠️</div>
          <h2 className="text-xl font-semibold mb-2 text-red-800">Connection Error</h2>
          <p className="text-red-600 mb-4">{error}</p>
          <button 
            onClick={fetchData}
            className="bg-red-600 text-white px-6 py-2 rounded-lg hover:bg-red-700"
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            🌍 AirVision - Real Data Dashboard
          </h1>
          <p className="text-gray-600">Live air quality monitoring with NASA satellite data</p>
        </div>

        {/* Main Dashboard */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-6xl mx-auto">
          
          {/* AQI Card */}
          {aqiData && (
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-800">Air Quality Index</h2>
                <div className="text-xs text-gray-500">Real-time data</div>
              </div>
              
              <div className="text-center mb-6">
                <div className="text-4xl font-bold text-orange-600 mb-2">{aqiData.aqi}</div>
                <div className="text-lg text-gray-700 font-medium">{aqiData.category}</div>
                <div className="text-sm text-gray-500">{aqiData.city}</div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-blue-50 rounded-lg p-3 text-center">
                  <div className="text-sm text-blue-600 font-medium">PM2.5</div>
                  <div className="text-lg font-bold text-blue-800">{aqiData.pollutants.pm25}</div>
                </div>
                <div className="bg-green-50 rounded-lg p-3 text-center">
                  <div className="text-sm text-green-600 font-medium">PM10</div>
                  <div className="text-lg font-bold text-green-800">{aqiData.pollutants.pm10}</div>
                </div>
                <div className="bg-purple-50 rounded-lg p-3 text-center">
                  <div className="text-sm text-purple-600 font-medium">NO2</div>
                  <div className="text-lg font-bold text-purple-800">{aqiData.pollutants.no2}</div>
                </div>
                <div className="bg-orange-50 rounded-lg p-3 text-center">
                  <div className="text-sm text-orange-600 font-medium">O3</div>
                  <div className="text-lg font-bold text-orange-800">{aqiData.pollutants.o3}</div>
                </div>
              </div>
              
              <div className="mt-4 pt-4 border-t">
                <div className="text-xs text-gray-500">
                  Source: {aqiData.source}
                </div>
                <div className="text-xs text-gray-500">
                  Updated: {new Date(aqiData.timestamp).toLocaleString()}
                </div>
              </div>
            </div>
          )}
          
          {/* Weather Card */}
          {weatherData && (
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-800">Weather Conditions</h2>
                <div className="text-xs text-gray-500">Current</div>
              </div>
              
              <div className="text-center mb-6">
                <div className="text-4xl font-bold text-blue-600 mb-2">{weatherData.temperature}°C</div>
                <div className="text-lg text-gray-700 font-medium">{weatherData.conditions}</div>
                <div className="text-sm text-gray-500">{city}</div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-blue-50 rounded-lg p-3">
                  <div className="text-sm text-blue-600 font-medium">Humidity</div>
                  <div className="text-lg font-bold text-blue-800">{weatherData.humidity}%</div>
                </div>
                <div className="bg-green-50 rounded-lg p-3">
                  <div className="text-sm text-green-600 font-medium">Wind Speed</div>
                  <div className="text-lg font-bold text-green-800">{weatherData.wind_speed} m/s</div>
                </div>
                <div className="bg-purple-50 rounded-lg p-3">
                  <div className="text-sm text-purple-600 font-medium">Pressure</div>
                  <div className="text-lg font-bold text-purple-800">{weatherData.pressure} hPa</div>
                </div>
                <div className="bg-orange-50 rounded-lg p-3">
                  <div className="text-sm text-orange-600 font-medium">Visibility</div>
                  <div className="text-lg font-bold text-orange-800">{weatherData.visibility} km</div>
                </div>
              </div>
            </div>
          )}
        </div>
        
        {/* Success Message */}
        <div className="text-center mt-8">
          <div className="inline-flex items-center bg-green-100 text-green-800 px-4 py-2 rounded-full">
            <span className="mr-2">✅</span>
            <span>Real data successfully loaded from OpenWeatherMap API</span>
          </div>
        </div>
        
        {/* Action Button */}
        <div className="text-center mt-6">
          <button 
            onClick={fetchData}
            className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 font-medium"
          >
            Refresh Data
          </button>
        </div>
      </div>
    </div>
  )
}