'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Search, MapPin, TrendingUp, Activity, Zap, Database, RefreshCw } from 'lucide-react'
import AQICard from '@/components/AQICard'
import WeatherCard from '@/components/WeatherCard'
import apiClient, { AQIData, WeatherData, RealtimeData } from '@/lib/api'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

// Cache management
interface CachedData {
  aqiData: AQIData | null
  weatherData: WeatherData | null
  realtimeData: RealtimeData | null
  timestamp: number
  city: string
}

const CACHE_DURATION = 5 * 60 * 1000 // 5 minutes
const CACHE_KEY = 'airvision_cache'

export default function HomePage() {
  const [city, setCity] = useState('New York')
  const [aqiData, setAqiData] = useState<AQIData | null>(null)
  const [weatherData, setWeatherData] = useState<WeatherData | null>(null)
  const [realtimeData, setRealtimeData] = useState<RealtimeData | null>(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [searchCity, setSearchCity] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  useEffect(() => {
    loadDataWithCache(city)
  }, [city])

  const loadCachedData = (): CachedData | null => {
    if (typeof window === 'undefined') return null
    
    try {
      const cached = localStorage.getItem(CACHE_KEY)
      if (cached) {
        const data: CachedData = JSON.parse(cached)
        const now = Date.now()
        if (now - data.timestamp < CACHE_DURATION && data.city === city) {
          return data
        }
      }
    } catch (error) {
      console.warn('Error loading cache:', error)
    }
    return null
  }

  const saveCachedData = (data: CachedData) => {
    if (typeof window === 'undefined') return
    
    try {
      localStorage.setItem(CACHE_KEY, JSON.stringify(data))
    } catch (error) {
      console.warn('Error saving cache:', error)
    }
  }

  const loadDataWithCache = async (cityName: string) => {
    setLoading(true)
    setError(null)
    
    // Try to load from cache first
    const cachedData = loadCachedData()
    if (cachedData && cachedData.city === cityName) {
      console.log('Loading from cache for:', cityName)
      setAqiData(cachedData.aqiData)
      setWeatherData(cachedData.weatherData)
      setRealtimeData(cachedData.realtimeData)
      setLastUpdated(new Date(cachedData.timestamp))
      setLoading(false)
      return
    }

    // If no cache or expired, fetch fresh data
    await fetchData(cityName)
  }

  const refreshData = async () => {
    setRefreshing(true)
    await fetchData(city, true)
    setRefreshing(false)
  }

  const fetchData = async (cityName: string, forceRefresh: boolean = false) => {
    if (!forceRefresh) {
      setLoading(true)
    }
    setError(null)
    
    const startTime = performance.now()
    console.log('🚀 Starting data fetch for:', cityName, forceRefresh ? '(forced)' : '(normal)')
    const baseURL = 'http://localhost:8000'
    
    try {
      console.log('⏰ Fetch start time:', new Date().toISOString())
      
      // Use Promise.all for parallel requests instead of sequential
      const [aqiResponse, weatherResponse] = await Promise.all([
        fetch(`${baseURL}/api/current?city=${encodeURIComponent(cityName)}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache'
          }
        }),
        fetch(`${baseURL}/api/weather?city=${encodeURIComponent(cityName)}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache'
          }
        })
      ])
      
      const aqiTime = performance.now()
      console.log('📊 AQI response time:', aqiTime - startTime, 'ms, status:', aqiResponse.status)
      
      if (!aqiResponse.ok) {
        throw new Error(`AQI API error: ${aqiResponse.status} ${aqiResponse.statusText}`)
      }
      
      if (!weatherResponse.ok) {
        throw new Error(`Weather API error: ${weatherResponse.status} ${weatherResponse.statusText}`)
      }
      
      // Parse JSON in parallel
      const [fetchedAqiData, fetchedWeatherData] = await Promise.all([
        aqiResponse.json(),
        weatherResponse.json()
      ])
      
      const parseTime = performance.now()
      console.log('📝 JSON parsing time:', parseTime - aqiTime, 'ms')
      console.log('✅ AQI data received:', fetchedAqiData)
      console.log('🌤️ Weather data received:', fetchedWeatherData)
      
      setAqiData(fetchedAqiData)
      setWeatherData(fetchedWeatherData)
      
      // Optional realtime data (don't block UI for this) - Skip for now to improve speed
      /*
      let fetchedRealtimeData = null
      try {
        const realtimeResponse = await fetch(`${baseURL}/api/realtime/process?city=${encodeURIComponent(cityName)}`)
        if (realtimeResponse.ok) {
          fetchedRealtimeData = await realtimeResponse.json()
          setRealtimeData(fetchedRealtimeData)
          console.log('🔄 Realtime data received:', fetchedRealtimeData)
        }
      } catch (error) {
        console.warn('⚠️ Real-time data not available (non-critical):', error)
      }
      */
      
      // Save to cache
      const cacheData: CachedData = {
        aqiData: fetchedAqiData,
        weatherData: fetchedWeatherData,
        realtimeData: null, // Skip realtime for speed
        timestamp: Date.now(),
        city: cityName
      }
      saveCachedData(cacheData)
      setLastUpdated(new Date())
      
      const totalTime = performance.now() - startTime
      console.log('🏁 Total fetch time:', totalTime, 'ms')
      
    } catch (error) {
      const errorTime = performance.now() - startTime
      console.error('❌ Error after', errorTime, 'ms:', error)
      setError(`Failed to fetch data for ${cityName}. ${error instanceof Error ? error.message : 'Please try again.'}`)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchCity.trim()) {
      setCity(searchCity.trim())
      setSearchCity('')
    }
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-blue-50 via-white to-purple-50">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-blue-100/20 via-transparent to-purple-100/20"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <div className="mb-8">
              <div className="inline-flex p-4 bg-blue-600 rounded-full mb-6">
                <Activity className="w-8 h-8 text-white" />
              </div>
            </div>
            <h1 className="text-5xl md:text-6xl font-bold mb-6 text-black leading-tight">
              From Earth Data to{' '}
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Safer Skies
              </span>
            </h1>
            <p className="text-xl md:text-2xl text-gray-700 mb-12 max-w-4xl mx-auto leading-relaxed">
              Professional air quality monitoring powered by NASA TEMPO satellite data and real-time community reports. 
              Get accurate insights to protect your health and environment.
            </p>
            
            {/* Feature Badges */}
            <div className="flex flex-wrap justify-center gap-3 mb-12">
              <Badge className="bg-blue-100 text-blue-800 border-blue-200 px-4 py-2 text-sm">
                <Activity className="w-4 h-4 mr-2" />
                NASA TEMPO Satellite
              </Badge>
              <Badge className="bg-green-100 text-green-800 border-green-200 px-4 py-2 text-sm">
                <TrendingUp className="w-4 h-4 mr-2" />
                AI Forecasting
              </Badge>
              <Badge className="bg-purple-100 text-purple-800 border-purple-200 px-4 py-2 text-sm">
                <Database className="w-4 h-4 mr-2" />
                Real-time Processing
              </Badge>
              <Badge className="bg-orange-100 text-orange-800 border-orange-200 px-4 py-2 text-sm">
                <MapPin className="w-4 h-4 mr-2" />
                Community Reports
              </Badge>
            </div>
            
            {/* Search Bar */}
            <motion.form
              onSubmit={handleSearch}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.3 }}
              className="max-w-lg mx-auto"
            >
              <div className="relative flex space-x-3 p-2 bg-white rounded-2xl shadow-lg border border-gray-200">
                <div className="relative flex-1">
                  <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <Input
                    type="text"
                    placeholder="Enter city name to check air quality..."
                    value={searchCity}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearchCity(e.target.value)}
                    className="pl-12 pr-4 py-3 bg-transparent border-0 text-gray-900 placeholder-gray-500 focus:ring-0"
                  />
                </div>
                <Button 
                  type="submit" 
                  className="bg-blue-600 text-white hover:bg-blue-700 px-6 py-3 rounded-xl shadow-md hover:shadow-lg transition-all duration-200"
                >
                  Check Quality
                </Button>
              </div>
              <p className="text-sm text-gray-500 mt-3">
                Try: New York, Los Angeles, Chicago, Houston, or any major city
              </p>
            </motion.form>
          </motion.div>
        </div>
      </section>

      {/* Dashboard Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="text-center mb-12"
            >
              <h2 className="text-3xl md:text-4xl font-bold text-black mb-4">
                Live Environmental Dashboard - {city}
              </h2>
              <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-4">
                Real-time air quality and weather data from OpenWeatherMap API
              </p>
              
              {/* Cache Status and Refresh */}
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                {lastUpdated && (
                  <div className="text-sm text-gray-500">
                    Last updated: {lastUpdated.toLocaleTimeString()}
                  </div>
                )}
                <button
                  onClick={refreshData}
                  disabled={refreshing}
                  className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
                >
                  <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
                  {refreshing ? 'Refreshing...' : 'Refresh Data'}
                </button>
              </div>
            </motion.div>

          {error && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-red-50 border border-red-200 rounded-2xl p-6 mb-8 text-center"
            >
              <p className="text-red-800 text-lg">{error}</p>
              <Button 
                onClick={() => fetchData('New York')}
                className="mt-4 bg-red-600 text-white hover:bg-red-700"
              >
                Try New York
              </Button>
            </motion.div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="relative"
            >
              <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-purple-500/10 rounded-2xl blur-xl"></div>
              <div className="relative bg-white rounded-2xl shadow-xl border border-gray-200 p-1">
                {loading && !aqiData ? (
                  <div className="h-80 flex items-center justify-center">
                    <div className="flex flex-col items-center">
                      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
                      <p className="text-gray-600">Loading air quality data...</p>
                    </div>
                  </div>
                ) : aqiData ? (
                  <div className="relative">
                    {refreshing && (
                      <div className="absolute top-2 right-2 z-10">
                        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                      </div>
                    )}
                    <AQICard data={aqiData} />
                  </div>
                ) : (
                  <div className="h-80 flex items-center justify-center">
                    <p className="text-gray-500">No air quality data available</p>
                  </div>
                )}
              </div>
            </motion.div>            <motion.div
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, delay: 0.6 }}
              className="relative"
            >
              <div className="absolute inset-0 bg-gradient-to-br from-green-500/10 to-blue-500/10 rounded-2xl blur-xl"></div>
              <div className="relative bg-white rounded-2xl shadow-xl border border-gray-200 p-1">
                {loading && !weatherData ? (
                  <div className="h-80 flex items-center justify-center">
                    <div className="flex flex-col items-center">
                      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mb-4"></div>
                      <p className="text-gray-600">Loading weather data...</p>
                    </div>
                  </div>
                ) : weatherData ? (
                  <div className="relative">
                    {refreshing && (
                      <div className="absolute top-2 right-2 z-10">
                        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-green-600"></div>
                      </div>
                    )}
                    <WeatherCard data={weatherData} />
                  </div>
                ) : (
                  <div className="h-80 flex items-center justify-center">
                    <p className="text-gray-500">No weather data available</p>
                  </div>
                )}
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Health Recommendations Section */}
      <section className="py-16 bg-gradient-to-br from-green-50 to-blue-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="text-center mb-12"
          >
            <h2 className="text-3xl md:text-4xl font-bold text-black mb-4">
              Personalized Health Recommendations
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Get tailored advice based on current air quality conditions in {city} to protect your health
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {getHealthTips(aqiData?.aqi || 50).map((tip, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.3 + index * 0.1 }}
                className="bg-white p-6 rounded-2xl shadow-lg border border-gray-200 hover:shadow-xl transition-all duration-300"
              >
                <div className="mb-4">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-3">
                    <Activity className="w-6 h-6 text-blue-600" />
                  </div>
                  <h3 className="text-lg font-semibold text-black mb-2">{tip.title}</h3>
                </div>
                <p className="text-gray-600 leading-relaxed">{tip.description}</p>
              </motion.div>
            ))}
          </div>

          {aqiData && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.8 }}
              className="text-center mt-12"
            >
              <div className="inline-flex items-center bg-white px-6 py-3 rounded-full shadow-lg border border-gray-200">
                <span className="text-gray-600 mr-2">Current AQI in {city}:</span>
                <span className="font-bold text-2xl text-black">{aqiData.aqi}</span>
                <span className="ml-2 text-sm font-medium text-gray-500">({aqiData.category})</span>
              </div>
            </motion.div>
          )}
        </div>
      </section>

      {/* Call to Action Section */}
      <section className="py-16 bg-gradient-to-r from-blue-600 to-purple-600">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
              Join the Community-Driven Air Quality Revolution
            </h2>
            <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto leading-relaxed">
              Help build a comprehensive air quality network by reporting incidents and sharing feedback. 
              Together, we can create safer communities for everyone.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button 
                className="bg-white text-blue-600 hover:bg-gray-100 px-8 py-4 rounded-xl text-lg font-semibold shadow-lg hover:shadow-xl transition-all duration-200"
                onClick={() => window.location.href = '/community'}
              >
                Join Community
              </Button>
              <Button 
                className="bg-transparent border-2 border-white text-white hover:bg-white hover:text-blue-600 px-8 py-4 rounded-xl text-lg font-semibold transition-all duration-200"
                onClick={() => window.location.href = '/forecast'}
              >
                View Forecasts
              </Button>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  )
}

function getHealthTips(aqi: number) {
  if (aqi <= 50) {
    return [
      { icon: '', title: 'Perfect for Outdoor Activities', description: 'Air quality is excellent. Great time for jogging, cycling, or outdoor sports.' },
      { icon: '', title: 'Bike to Work', description: 'Consider biking or walking instead of driving to reduce emissions.' },
      { icon: '', title: 'Plant Some Greenery', description: 'Good day to tend to your garden or plant trees to improve air quality.' }
    ]
  } else if (aqi <= 100) {
    return [
      { icon: '', title: 'Light Outdoor Exercise', description: 'Moderate activities are fine for most people. Limit intense outdoor exercise.' },
      { icon: '', title: 'Ventilate Your Home', description: 'Open windows to let fresh air circulate through your home.' },
      { icon: '', title: 'Sensitive Groups Be Careful', description: 'People with heart or lung conditions should reduce outdoor activities.' }
    ]
  } else if (aqi <= 150) {
    return [
      { icon: '', title: 'Limit Outdoor Time', description: 'Reduce prolonged outdoor activities, especially for sensitive groups.' },
      { icon: '', title: 'Stay Indoors More', description: 'Consider indoor alternatives for exercise and activities.' },
      { icon: '', title: 'Wear a Mask', description: 'Use N95 masks when going outside, especially in crowded areas.' }
    ]
  } else {
    return [
      { icon: '', title: 'Avoid Outdoor Activities', description: 'Stay indoors and avoid all outdoor physical activities.' },
      { icon: '', title: 'Always Wear Masks', description: 'Use high-quality masks (N95/KN95) when you must go outside.' },
      { icon: '', title: 'Keep Windows Closed', description: 'Use air purifiers indoors and keep windows closed.' }
    ]
  }
}
