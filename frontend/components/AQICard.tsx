'use client'

import { useState, useEffect } from 'react'
import { Badge } from '@/components/ui/badge'
import { getAQICategory } from '@/lib/utils'  
import { AQIData } from '@/lib/api'
import { motion } from 'framer-motion'
import { Activity, Wind, Droplets, Sun, Satellite, Zap, TrendingUp } from 'lucide-react'

interface AQICardProps {
  data: AQIData | null
  loading?: boolean
  className?: string
}

export default function AQICard({ data, loading = false, className }: AQICardProps) {
  const [displayAQI, setDisplayAQI] = useState(0)
  
  // Count up animation effect
  useEffect(() => {
    if (data && !loading) {
      let start = 0
      const end = data.aqi
      const duration = 1500 // 1.5 seconds
      const increment = end / (duration / 16) // 60fps
      
      const timer = setInterval(() => {
        start += increment
        if (start >= end) {
          setDisplayAQI(end)
          clearInterval(timer)
        } else {
          setDisplayAQI(Math.floor(start))
        }
      }, 16)
      
      return () => clearInterval(timer)
    }
  }, [data, loading])

  if (loading || !data) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className={`bg-white rounded-xl card-shadow p-8 ${className}`}
      >
        <div className="animate-pulse space-y-6">
          <div className="flex items-center justify-between">
            <div className="h-8 bg-gray-200 rounded w-1/3"></div>
            <div className="h-6 bg-gray-200 rounded w-20"></div>
          </div>
          <div className="text-center space-y-4">
            <div className="h-24 bg-gray-200 rounded w-32 mx-auto"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2 mx-auto"></div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="h-16 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </motion.div>
    )
  }

  const aqiInfo = getAQICategory(data.aqi)
  
  const pollutantData = [
    { icon: Activity, label: 'PM2.5', value: data.pollutants.pm25, unit: 'μg/m³', color: 'text-red-500', bgColor: 'bg-red-50' },
    { icon: Wind, label: 'PM10', value: data.pollutants.pm10, unit: 'μg/m³', color: 'text-orange-500', bgColor: 'bg-orange-50' },
    { icon: Droplets, label: 'NO₂', value: data.pollutants.no2, unit: 'μg/m³', color: 'text-blue-500', bgColor: 'bg-blue-50' },
    { icon: Sun, label: 'O₃', value: data.pollutants.o3, unit: 'μg/m³', color: 'text-yellow-500', bgColor: 'bg-yellow-50' },
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={`bg-white rounded-xl card-shadow card-hover smooth-transition ${className}`}
    >
      <div className="p-8 h-full">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-3">
            <div className="bg-blue-100 p-2 rounded-lg">
              <Satellite className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">{data.city}</h2>
              <p className="text-sm text-gray-500 flex items-center space-x-1">
                <TrendingUp className="w-3 h-3" />
                <span>{data.source}</span>
              </p>
            </div>
          </div>
          <Badge className={`${aqiInfo.color} text-white px-4 py-2 text-sm font-semibold`}>
            {aqiInfo.category}
          </Badge>
        </div>

        {/* Main AQI Display */}
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
            className="relative inline-block"
          >
            <div className={`text-8xl font-bold count-up ${aqiInfo.color.replace('bg-', 'text-')}`}>
              {displayAQI}
            </div>
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
              className="absolute -top-2 -right-2"
            >
              <Zap className="w-8 h-8 text-yellow-500" />
            </motion.div>
          </motion.div>
          <p className="text-gray-600 mt-3 text-lg font-medium">{aqiInfo.description}</p>
        </div>

        {/* Pollutant Grid */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          {pollutantData.map((pollutant, index) => (
            <motion.div
              key={pollutant.label}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 * index, duration: 0.5 }}
              whileHover={{ scale: 1.02 }}
              className={`${pollutant.bgColor} rounded-lg p-4 smooth-transition`}
            >
              <div className="flex items-center space-x-3">
                <pollutant.icon className={`w-5 h-5 ${pollutant.color}`} />
                <div>
                  <p className="text-xs text-gray-500 font-medium">{pollutant.label}</p>
                  <p className="text-lg font-bold text-gray-900">
                    {pollutant.value} <span className="text-xs font-normal text-gray-500">{pollutant.unit}</span>
                  </p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Status Footer */}
        <div className="flex items-center justify-between text-sm text-gray-500 pt-4 border-t border-gray-100">
          <div className="flex items-center space-x-2">
            <motion.div
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
              className={`w-3 h-3 rounded-full ${
                aqiInfo.color.includes('red') ? 'bg-red-400' :
                aqiInfo.color.includes('orange') ? 'bg-orange-400' :
                aqiInfo.color.includes('yellow') ? 'bg-yellow-400' :
                aqiInfo.color.includes('green') ? 'bg-green-400' : 'bg-blue-400'
              }`}
            />
            <span>Live data</span>
          </div>
          <span>Updated: {new Date(data.timestamp).toLocaleTimeString()}</span>
        </div>
      </div>
    </motion.div>
  )
}
