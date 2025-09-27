'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { AQIData } from '@/lib/api'
import { getAQICategory } from '@/lib/utils'
import { motion } from 'framer-motion'
import { MapPin } from 'lucide-react'
import dynamic from 'next/dynamic'

// Dynamically import Leaflet components to avoid SSR issues
const MapContainer = dynamic(() => import('react-leaflet').then(mod => mod.MapContainer), { ssr: false })
const TileLayer = dynamic(() => import('react-leaflet').then(mod => mod.TileLayer), { ssr: false })
const Marker = dynamic(() => import('react-leaflet').then(mod => mod.Marker), { ssr: false })
const Popup = dynamic(() => import('react-leaflet').then(mod => mod.Popup), { ssr: false })

interface MapViewProps {
  data: AQIData[]
  className?: string
}

export default function MapView({ data, className }: MapViewProps) {
  const [isClient, setIsClient] = useState(false)

  useEffect(() => {
    setIsClient(true)
  }, [])

  if (!isClient) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <MapPin className="w-5 h-5 text-blue-500" />
            <span>Air Quality Map</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-80 w-full bg-gray-100 rounded-lg flex items-center justify-center">
            <p className="text-gray-500">Loading map...</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  // Default coordinates (Delhi)
  const defaultCenter: [number, number] = [28.6139, 77.2090]
  const defaultZoom = 10

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.3 }}
      className={className}
    >
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <MapPin className="w-5 h-5 text-blue-500" />
            <span>Air Quality Map</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-80 w-full">
            <MapContainer
              center={defaultCenter}
              zoom={defaultZoom}
              style={{ height: '100%', width: '100%' }}
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              {data.map((cityData, index) => {
                const aqiInfo = getAQICategory(cityData.aqi)
                return (
                  <Marker
                    key={index}
                    position={[28.6139 + (index * 0.1), 77.2090 + (index * 0.1)]}
                  >
                    <Popup>
                      <div className="p-2">
                        <h3 className="font-bold text-lg">{cityData.city}</h3>
                        <div className="mt-2">
                          <div className="flex items-center space-x-2">
                            <div className={`w-4 h-4 rounded-full ${aqiInfo.color}`}></div>
                            <span className="font-semibold">AQI: {cityData.aqi}</span>
                          </div>
                          <p className="text-sm text-gray-600 mt-1">{aqiInfo.category}</p>
                          <div className="mt-2 text-xs text-gray-500">
                            <p>PM2.5: {cityData.pollutants.pm25} μg/m³</p>
                            <p>PM10: {cityData.pollutants.pm10} μg/m³</p>
                            <p>NO₂: {cityData.pollutants.no2} μg/m³</p>
                            <p>O₃: {cityData.pollutants.o3} μg/m³</p>
                          </div>
                        </div>
                      </div>
                    </Popup>
                  </Marker>
                )
              })}
            </MapContainer>
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            <div className="flex items-center space-x-1 text-xs">
              <div className="w-3 h-3 rounded-full bg-aqi-good"></div>
              <span>Good (0-50)</span>
            </div>
            <div className="flex items-center space-x-1 text-xs">
              <div className="w-3 h-3 rounded-full bg-aqi-moderate"></div>
              <span>Moderate (51-100)</span>
            </div>
            <div className="flex items-center space-x-1 text-xs">
              <div className="w-3 h-3 rounded-full bg-aqi-unhealthy"></div>
              <span>Unhealthy (101-150)</span>
            </div>
            <div className="flex items-center space-x-1 text-xs">
              <div className="w-3 h-3 rounded-full bg-aqi-very"></div>
              <span>Very Unhealthy (151-200)</span>
            </div>
            <div className="flex items-center space-x-1 text-xs">
              <div className="w-3 h-3 rounded-full bg-aqi-hazardous"></div>
              <span>Hazardous (201-300)</span>
            </div>
            <div className="flex items-center space-x-1 text-xs">
              <div className="w-3 h-3 rounded-full bg-aqi-extremely"></div>
              <span>Extremely Hazardous (300+)</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
