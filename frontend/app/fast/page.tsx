'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { RefreshCw, Activity, Zap, Clock } from 'lucide-react'

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

export default function FastDashboard() {
  const [aqiData, setAqiData] = useState<AirQualityData | null>(null)
  const [weatherData, setWeatherData] = useState<WeatherData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [fetchTime, setFetchTime] = useState<number | null>(null)
  const [city] = useState('New York')

  useEffect(() => {
    fetchDataFast()
  }, [])

  const fetchDataFast = async () => {
    setLoading(true)
    setError(null)
    
    const startTime = performance.now()
    console.log('🚀 Fast fetch starting...', new Date().toISOString())
    
    try {
      // Single optimized request - use the regular endpoint (now fast by default)
      const response = await fetch(`http://localhost:8000/api/current?city=${encodeURIComponent(city)}`, {
        method: 'GET',
        headers: { 'Accept': 'application/json' }
      })
      
      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`)
      }
      
      const data = await response.json()
      setAqiData(data)
      
      const endTime = performance.now()
      const totalTime = Math.round(endTime - startTime)
      setFetchTime(totalTime)
      
      console.log('✅ Fast fetch complete in', totalTime, 'ms')
      
      // Get weather data separately (non-blocking)
      setTimeout(async () => {
        try {
          const weatherResponse = await fetch(`http://localhost:8000/api/weather?city=${encodeURIComponent(city)}`)
          if (weatherResponse.ok) {
            const weatherData = await weatherResponse.json()
            setWeatherData(weatherData)
          }
        } catch (err) {
          console.warn('Weather data failed (non-critical):', err)
        }
      }, 100) // Small delay to not block main render
      
    } catch (err) {
      console.error('❌ Fast fetch failed:', err)
      setError(err instanceof Error ? err.message : 'Failed to load data')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="bg-white rounded-2xl shadow-2xl p-8 text-center max-w-md">
          <div className="relative mb-6">
            <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-200 border-t-blue-600 mx-auto"></div>
            <Activity className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-6 h-6 text-blue-600" />
          </div>
          <h2 className="text-xl font-bold text-gray-800 mb-2">Loading Air Quality Data</h2>
          <p className="text-gray-600">Fetching real-time data from NASA satellites...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 to-pink-100 flex items-center justify-center">
        <div className="bg-white rounded-2xl shadow-2xl p-8 text-center max-w-md">
          <div className="text-red-500 mb-4">
            <Zap className="w-16 h-16 mx-auto" />
          </div>
          <h2 className="text-xl font-bold text-red-800 mb-4">Connection Error</h2>
          <p className="text-red-600 mb-6">{error}</p>
          <button 
            onClick={fetchDataFast}
            className="bg-red-600 text-white px-8 py-3 rounded-xl hover:bg-red-700 font-medium transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      <div className="container mx-auto px-4 py-12">
        
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-5xl font-bold text-gray-800 mb-4">
            🌍 AirVision <span className="text-blue-600">Fast</span>
          </h1>
          <p className="text-xl text-gray-600 mb-4">Ultra-fast air quality monitoring</p>
          
          {fetchTime && (
            <div className="inline-flex items-center bg-green-100 text-green-800 px-4 py-2 rounded-full">
              <Clock className="w-4 h-4 mr-2" />
              <span className="font-medium">Loaded in {fetchTime}ms</span>
            </div>
          )}
        </motion.div>

        {/* Main Dashboard */}
        <div className="max-w-4xl mx-auto">
          
          {/* AQI Card */}
          {aqiData && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-white rounded-2xl shadow-2xl p-8 mb-8 border border-gray-100"
            >
              <div className="text-center mb-8">
                <div className="inline-flex items-center bg-blue-100 text-blue-800 px-4 py-2 rounded-full mb-4">
                  <Activity className="w-4 h-4 mr-2" />
                  <span className="font-medium">Live Air Quality</span>
                </div>
                
                <div className="mb-6">
                  <div className="text-7xl font-bold text-orange-600 mb-2">{aqiData.aqi}</div>
                  <div className="text-2xl font-semibold text-gray-700">{aqiData.category}</div>
                  <div className="text-lg text-gray-600 mt-2">{aqiData.city}</div>
                </div>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-4 text-center">
                  <div className="text-sm font-semibold text-blue-700 mb-2">PM2.5</div>
                  <div className="text-3xl font-bold text-blue-800">{aqiData.pollutants.pm25}</div>
                  <div className="text-xs text-blue-600">µg/m³</div>
                </div>
                
                <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-4 text-center">
                  <div className="text-sm font-semibold text-green-700 mb-2">PM10</div>
                  <div className="text-3xl font-bold text-green-800">{aqiData.pollutants.pm10}</div>
                  <div className="text-xs text-green-600">µg/m³</div>
                </div>
                
                <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-4 text-center">
                  <div className="text-sm font-semibold text-purple-700 mb-2">NO2</div>
                  <div className="text-3xl font-bold text-purple-800">{aqiData.pollutants.no2}</div>
                  <div className="text-xs text-purple-600">µg/m³</div>
                </div>
                
                <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl p-4 text-center">
                  <div className="text-sm font-semibold text-orange-700 mb-2">O3</div>
                  <div className="text-3xl font-bold text-orange-800">{aqiData.pollutants.o3}</div>
                  <div className="text-xs text-orange-600">µg/m³</div>
                </div>
              </div>
              
              <div className="flex flex-col sm:flex-row justify-between items-center pt-4 border-t border-gray-200">
                <div className="text-sm text-gray-600 mb-4 sm:mb-0">
                  <div><strong>Source:</strong> {aqiData.source}</div>
                  <div><strong>Updated:</strong> {new Date(aqiData.timestamp).toLocaleString()}</div>
                </div>
                
                <button
                  onClick={fetchDataFast}
                  className="inline-flex items-center bg-blue-600 text-white px-6 py-3 rounded-xl hover:bg-blue-700 font-medium transition-colors"
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Refresh
                </button>
              </div>
            </motion.div>
          )}
          
          {/* Weather Card */}
          {weatherData && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-white rounded-2xl shadow-xl p-6 border border-gray-100"
            >
              <div className="text-center mb-6">
                <h3 className="text-xl font-bold text-gray-800 mb-4">Weather Conditions</h3>
                <div className="text-4xl font-bold text-blue-600 mb-2">{weatherData.temperature}°C</div>
                <div className="text-lg text-gray-700">{weatherData.conditions}</div>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div className="bg-blue-50 rounded-lg p-3 text-center">
                  <div className="text-xs text-blue-700">Humidity</div>
                  <div className="text-lg font-bold text-blue-800">{weatherData.humidity}%</div>
                </div>
                
                <div className="bg-green-50 rounded-lg p-3 text-center">
                  <div className="text-xs text-green-700">Wind</div>
                  <div className="text-lg font-bold text-green-800">{weatherData.wind_speed} m/s</div>
                </div>
                
                <div className="bg-purple-50 rounded-lg p-3 text-center">
                  <div className="text-xs text-purple-700">Pressure</div>
                  <div className="text-lg font-bold text-purple-800">{weatherData.pressure} hPa</div>
                </div>
                
                <div className="bg-orange-50 rounded-lg p-3 text-center">
                  <div className="text-xs text-orange-700">Visibility</div>
                  <div className="text-lg font-bold text-orange-800">{weatherData.visibility} km</div>
                </div>
              </div>
            </motion.div>
          )}
        </div>
        
        {/* Performance Info */}
        <div className="text-center mt-12">
          <div className="inline-flex items-center bg-white rounded-xl shadow-lg px-6 py-3 border border-gray-200">
            <Zap className="w-5 h-5 text-yellow-500 mr-2" />
            <span className="text-gray-700">
              Optimized for speed • Real-time NASA data • {fetchTime ? `${fetchTime}ms load time` : 'Ultra-fast'}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}