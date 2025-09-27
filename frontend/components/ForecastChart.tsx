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
        <div className="bg-white p-4 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold text-black text-sm">{label}</p>
          <p className="text-sm text-gray-700 mt-1">
            AQI: <span className="font-bold text-black">{data.aqi}</span>
          </p>
          <p className="text-sm mt-1" style={{ color: aqiInfo.color }}>
            {aqiInfo.category}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            {aqiInfo.description}
          </p>
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
      <Card className="bg-white border-gray-200 shadow-sm">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2 text-black">
            <TrendingUp className="w-5 h-5 text-blue-500" />
            <span>24-Hour AQI Forecast - {data.city}</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis 
                  dataKey="time" 
                  tick={{ fontSize: 12, fill: '#374151' }}
                  interval="preserveStartEnd"
                  stroke="#6b7280"
                />
                <YAxis 
                  domain={[0, 'dataMax + 20']}
                  tick={{ fontSize: 12, fill: '#374151' }}
                  stroke="#6b7280"
                  label={{ value: 'AQI', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle', fill: '#374151' } }}
                />
                <Tooltip content={<CustomTooltip />} />
                <Line 
                  type="monotone" 
                  dataKey="aqi" 
                  stroke="#2563eb" 
                  strokeWidth={3}
                  dot={{ fill: '#2563eb', strokeWidth: 2, r: 4 }}
                  activeDot={{ r: 6, stroke: '#2563eb', strokeWidth: 2, fill: '#ffffff' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 grid grid-cols-3 gap-4 text-sm">
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-gray-600 text-xs uppercase tracking-wide">Current AQI</p>
              <p className="text-2xl font-bold text-black mt-1">{data.forecast[0]?.aqi || 0}</p>
              <p className="text-xs text-gray-500 mt-1">{data.forecast[0]?.category || 'Unknown'}</p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-gray-600 text-xs uppercase tracking-wide">Peak AQI (24h)</p>
              <p className="text-2xl font-bold text-red-600 mt-1">
                {Math.max(...data.forecast.map(f => f.aqi))}
              </p>
              <p className="text-xs text-gray-500 mt-1">Worst expected</p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-gray-600 text-xs uppercase tracking-wide">Best AQI (24h)</p>
              <p className="text-2xl font-bold text-green-600 mt-1">
                {Math.min(...data.forecast.map(f => f.aqi))}
              </p>
              <p className="text-xs text-gray-500 mt-1">Best expected</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
