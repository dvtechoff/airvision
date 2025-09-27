'use client'

import { WeatherData } from '@/lib/api'
import { motion } from 'framer-motion'
import { Thermometer, Droplets, Wind, Eye, Gauge, CloudRain } from 'lucide-react'

interface WeatherCardProps {
  data: WeatherData
  className?: string
}

export default function WeatherCard({ data, className }: WeatherCardProps) {
  const weatherMetrics = [
    { icon: Droplets, label: 'Humidity', value: `${data.humidity}%`, color: 'text-blue-500', bgColor: 'bg-blue-50' },
    { icon: Wind, label: 'Wind Speed', value: `${data.wind_speed} m/s`, color: 'text-green-500', bgColor: 'bg-green-50' },
    { icon: Eye, label: 'Visibility', value: `${data.visibility} km`, color: 'text-purple-500', bgColor: 'bg-purple-50' },
    { icon: Gauge, label: 'Pressure', value: `${data.pressure} hPa`, color: 'text-orange-500', bgColor: 'bg-orange-50' },
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.1 }}
      className={`bg-white rounded-xl card-shadow card-hover smooth-transition ${className}`}
    >
      <div className="p-6 h-full">
        {/* Header */}
        <div className="flex items-center space-x-3 mb-6">
          <div className="bg-cyan-100 p-2 rounded-lg">
            <CloudRain className="w-6 h-6 text-cyan-600" />
          </div>
          <h3 className="text-xl font-bold text-gray-900">Weather Conditions</h3>
        </div>

        {/* Main Temperature Display */}
        <div className="text-center mb-6">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: "spring" }}
            className="text-5xl font-bold text-gray-900 mb-2"
          >
            {Math.round(data.temperature)}°C
          </motion.div>
          <p className="text-gray-600 capitalize text-lg">{data.conditions}</p>
        </div>

        {/* Weather Metrics Grid */}
        <div className="grid grid-cols-2 gap-3">
          {weatherMetrics.map((metric, index) => (
            <motion.div
              key={metric.label}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 * index, duration: 0.5 }}
              whileHover={{ scale: 1.02 }}
              className={`${metric.bgColor} rounded-lg p-3 smooth-transition`}
            >
              <div className="flex items-center space-x-2">
                <metric.icon className={`w-4 h-4 ${metric.color}`} />
                <div>
                  <p className="text-xs text-gray-500 font-medium">{metric.label}</p>
                  <p className="text-sm font-bold text-gray-900">{metric.value}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </motion.div>
  )
}
