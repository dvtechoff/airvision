'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ForecastData } from '@/lib/api'
import { getAQICategory } from '@/lib/utils'
import { motion } from 'framer-motion'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { TrendingUp } from 'lucide-react'

interface ForecastChartProps {
  data: ForecastData
  className?: string
}

export default function ForecastChart({ data, className }: ForecastChartProps) {
  const chartData = data.forecast.map(item => ({
    time: new Date(item.time).toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: true 
    }),
    aqi: item.aqi,
    category: item.category,
    fullTime: item.time
  }))

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      const aqiInfo = getAQICategory(data.aqi)
      return (
        <div className="bg-white p-3 border rounded-lg shadow-lg">
          <p className="font-semibold">{label}</p>
          <p className="text-sm">
            AQI: <span className="font-bold">{data.aqi}</span>
          </p>
          <p className="text-sm text-gray-600">{aqiInfo.category}</p>
        </div>
      )
    }
    return null
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className={className}
    >
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <TrendingUp className="w-5 h-5 text-blue-500" />
            <span>24-Hour AQI Forecast - {data.city}</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="time" 
                  tick={{ fontSize: 12 }}
                  interval="preserveStartEnd"
                />
                <YAxis 
                  domain={[0, 300]}
                  tick={{ fontSize: 12 }}
                />
                <Tooltip content={<CustomTooltip />} />
                <Line 
                  type="monotone" 
                  dataKey="aqi" 
                  stroke="#3b82f6" 
                  strokeWidth={3}
                  dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
                  activeDot={{ r: 6, stroke: '#3b82f6', strokeWidth: 2 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-gray-500">Current AQI</p>
              <p className="text-2xl font-bold">{data.forecast[0]?.aqi || 0}</p>
            </div>
            <div>
              <p className="text-gray-500">Peak AQI (24h)</p>
              <p className="text-2xl font-bold">
                {Math.max(...data.forecast.map(f => f.aqi))}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
