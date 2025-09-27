'use client'

import { useState, useEffect } from 'react'
import AlertBox from '@/components/AlertBox'
import { Badge } from '@/components/ui/badge'
import { motion } from 'framer-motion'
import { AlertTriangle, Bell, Satellite, MapPin, Activity, Zap } from 'lucide-react'

interface Alert {
  id: string
  type: 'warning' | 'info' | 'success' | 'error'
  title: string
  description: string
  timestamp: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  location: string
  aqi?: number
}

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setTimeout(() => {
      setAlerts([
        {
          id: '1',
          type: 'error',
          title: 'Hazardous Air Quality',
          description: 'AQI levels in New York have reached hazardous levels (411). Avoid outdoor activities.',
          timestamp: new Date().toISOString(),
          severity: 'critical',
          location: 'New York, North America',
          aqi: 411
        },
        {
          id: '2',
          type: 'warning',
          title: 'PM2.5 Spike Detected',
          description: 'NASA TEMPO satellite detected significant increase in particulate matter concentrations.',
          timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
          severity: 'high',
          location: 'New York, North America',
          aqi: 285
        }
      ])
      setLoading(false)
    }, 1000)
  }, [])

  const severityColors = {
    low: 'bg-green-500/10 text-green-400 border-green-500/30',
    medium: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30',
    high: 'bg-orange-500/10 text-orange-400 border-orange-500/30',
    critical: 'bg-red-500/10 text-red-400 border-red-500/30'
  }

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center">
          <Satellite className="w-8 h-8 text-blue-600 animate-spin mx-auto" />
          <p className="text-gray-600 mt-2">Loading alerts...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="space-y-6">
        <div className="text-center mb-8">
          <div className="flex items-center justify-center space-x-3 mb-4">
            <Bell className="w-8 h-8 text-blue-600" />
            <h1 className="text-4xl font-bold text-gray-900">Air Quality Alerts</h1>
          </div>
          <p className="text-gray-600">Real-time alerts from NASA TEMPO satellite</p>
        </div>

        {alerts.map((alert, index) => (
          <motion.div
            key={alert.id}
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: index * 0.1 }}
          className="bg-white rounded-xl card-shadow p-6"
        >
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center space-x-3">
              <Activity className="w-6 h-6 text-blue-600" />
              <div>
                <h3 className="text-xl font-bold text-gray-900">{alert.title}</h3>
                <div className="flex items-center space-x-2 mt-1">
                  <MapPin className="w-4 h-4 text-gray-500" />
                  <span className="text-sm text-gray-500">{alert.location}</span>
                  {alert.aqi && (
                    <Badge className="bg-red-500/10 text-red-600 border border-red-200">AQI {alert.aqi}</Badge>
                  )}
                </div>
              </div>
            </div>
            <Badge className={severityColors[alert.severity]}>
              {alert.severity.toUpperCase()}
            </Badge>
          </div>
          <p className="text-gray-600">{alert.description}</p>
        </motion.div>
        ))}
      </div>
    </div>
  )
}
