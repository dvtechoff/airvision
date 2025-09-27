'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Search, MapPin, TrendingUp, Activity } from 'lucide-react'
import AQICard from '@/components/AQICard'
import WeatherCard from '@/components/WeatherCard'
import apiClient, { AQIData, WeatherData } from '@/lib/api'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'

export default function HomePage() {
  const [city, setCity] = useState('Delhi')
  const [aqiData, setAqiData] = useState<AQIData | null>(null)
  const [weatherData, setWeatherData] = useState<WeatherData | null>(null)
  const [loading, setLoading] = useState(true)
  const [searchCity, setSearchCity] = useState('')

  useEffect(() => {
    fetchData(city)
  }, [city])

  const fetchData = async (cityName: string) => {
    setLoading(true)
    try {
      const [aqi, weather] = await Promise.all([
        apiClient.getCurrentAQI(cityName),
        apiClient.getWeather(cityName)
      ])
      setAqiData(aqi)
      setWeatherData(weather)
    } catch (error) {
      console.error('Error fetching data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchCity.trim()) {
      setCity(searchCity.trim())
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-blue-600 via-purple-600 to-blue-800 text-white overflow-hidden">
        <div className="absolute inset-0 bg-black/20"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <h1 className="text-5xl md:text-6xl font-bold mb-6">
              From Earth Data to{' '}
              <span className="bg-gradient-to-r from-yellow-400 to-orange-400 bg-clip-text text-transparent">
                Safer Skies
              </span>
            </h1>
            <p className="text-xl md:text-2xl text-blue-100 mb-8 max-w-3xl mx-auto">
              Professional air quality monitoring powered by NASA TEMPO satellite data. 
              Get real-time insights to protect your health and environment.
            </p>
            
            {/* Search Bar */}
            <motion.form
              onSubmit={handleSearch}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.3 }}
              className="max-w-md mx-auto flex space-x-2"
            >
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <Input
                  type="text"
                  placeholder="Enter city name..."
                  value={searchCity}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearchCity(e.target.value)}
                  className="pl-10 bg-white/90 border-0 text-gray-900"
                />
              </div>
              <Button type="submit" className="bg-white text-blue-600 hover:bg-gray-100">
                Check Air Quality
              </Button>
            </motion.form>
          </motion.div>
        </div>
      </section>

      {/* Dashboard Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          {/* Current Location Header */}
          <div className="flex items-center space-x-2 mb-8">
            <MapPin className="w-6 h-6 text-blue-600" />
            <h2 className="text-3xl font-bold text-gray-900">{city}</h2>
            <div className="flex items-center space-x-1 text-sm text-gray-500">
              <Activity className="w-4 h-4" />
              <span>Live data from NASA TEMPO</span>
            </div>
          </div>

          {/* Main Cards Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
            {/* AQI Card - Takes 2 columns */}
            <div className="lg:col-span-2">
              <AQICard 
                data={aqiData} 
                loading={loading}
                className="h-full"
              />
            </div>
            
            {/* Weather Card */}
            <div className="lg:col-span-1">
              {weatherData && (
                <WeatherCard 
                  data={weatherData}
                  className="h-full"
                />
              )}
            </div>
          </div>

          {/* Health Tips Section */}
          {aqiData && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              className="bg-white rounded-xl card-shadow p-8"
            >
              <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center space-x-2">
                <TrendingUp className="w-6 h-6 text-blue-600" />
                <span>Health Recommendations</span>
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {getHealthTips(aqiData.aqi).map((tip, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.5, delay: 0.1 * index }}
                    className="bg-gray-50 rounded-lg p-4"
                  >
                    <div className="text-2xl mb-2">{tip.icon}</div>
                    <h4 className="font-semibold text-gray-900 mb-2">{tip.title}</h4>
                    <p className="text-sm text-gray-600">{tip.description}</p>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}
        </motion.div>
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
