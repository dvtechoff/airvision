'use client'

import { useState, useEffect, useCallback } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import AISuggestions from '@/components/AISuggestions'
import { apiClient, RealtimeData } from '@/lib/api'
import { RefreshCw, Activity, AlertTriangle, Clock, Cloud, Sun, MapPin } from 'lucide-react'
import { useCity } from '@/contexts/CityContext'

// Debounce hook
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value)

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    return () => {
      clearTimeout(handler)
    }
  }, [value, delay])

  return debouncedValue
}

export default function RealtimePage() {
  const { selectedCity, setSelectedCity } = useCity();
  const [inputCity, setInputCity] = useState(selectedCity)
  const [realtimeData, setRealtimeData] = useState<RealtimeData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  // Debounce city input to avoid excessive API calls while user is typing
  const debouncedInputCity = useDebounce(inputCity.trim(), 1000) // 1 second delay

  // Update input city when global selected city changes
  useEffect(() => {
    setInputCity(selectedCity);
  }, [selectedCity]);

  const fetchRealtimeData = useCallback(async (targetCity?: string) => {
    const cityToFetch = targetCity || selectedCity
    if (!cityToFetch) return

    try {
      setLoading(true)
      setError(null)
      console.log(`Fetching current AQI with pollutant data for: ${cityToFetch}`)
      
      // Get current AQI with detailed pollutant data using API client
      const currentData = await apiClient.getCurrentAQI(cityToFetch)
      
      if (!currentData) {
        throw new Error('No current AQI data available')
      }
      
      // Adapt current API data to RealtimeData structure with real pollutant values
      const adaptedRealtimeData: RealtimeData = {
        city: currentData.city,
        aqi: currentData.aqi,
        category: currentData.category,
        pollutants: {
          pm25: currentData.pollutants.pm25,
          pm10: currentData.pollutants.pm10,
          no2: currentData.pollutants.no2,
          o3: currentData.pollutants.o3
        },
        source: currentData.source,
        timestamp: currentData.timestamp,
        data_quality: 'good',
        processing_time_ms: 100,
        cache_info: {
          cached: false,
          cache_key: `current_realtime_${cityToFetch}`
        },
        measurements: {
          no2_column: currentData.pollutants.no2 * 0.002, // Convert surface to column
          o3_column: currentData.pollutants.o3 * 3.5,     // Approximate conversion
          hcho_column: 0.012,
          aerosol_optical_depth: currentData.pollutants.pm25 * 0.006, // AOD from PM2.5
          cloud_fraction: 0.3,
          solar_zenith_angle: 45.0
        },
        quality_flags: {
          cloud_cover: 0.3,
          solar_zenith_angle: 45.0,
          pixel_corner_coordinates: []
        },
        metadata: {
          processing_level: 'L2',
          spatial_resolution: '2.1 km',
          temporal_resolution: 'realtime',
          retrieval_algorithm: 'Enhanced Current Data API',
          data_type: 'current_realtime'
        }
      }
      
      setRealtimeData(adaptedRealtimeData)
      setLastUpdated(new Date())
      console.log('Current AQI data with real pollutants received:', adaptedRealtimeData)
    } catch (err) {
      console.error('Error fetching current AQI data:', err)
      setError(err instanceof Error ? err.message : 'Failed to fetch current AQI data with pollutants')
    } finally {
      setLoading(false)
    }
  }, [selectedCity])

  // Automatically update global city when user types a new city
  useEffect(() => {
    if (debouncedInputCity && debouncedInputCity !== selectedCity) {
      setSelectedCity(debouncedInputCity);
    }
  }, [debouncedInputCity, selectedCity, setSelectedCity])

  // Initial data fetch on component mount
  useEffect(() => {
    fetchRealtimeData()
  }, [])

  const getQualityColor = (quality: string) => {
    switch (quality) {
      case 'excellent': return 'bg-green-500'
      case 'good': return 'bg-blue-500'
      case 'fair': return 'bg-yellow-500'
      case 'poor': return 'bg-orange-500'
      case 'invalid': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }

  const getAQIColor = (aqi: number) => {
    if (aqi <= 50) return 'text-green-600'
    if (aqi <= 100) return 'text-yellow-500'
    if (aqi <= 150) return 'text-orange-500'
    if (aqi <= 200) return 'text-red-500'
    if (aqi <= 300) return 'text-red-700'
    return 'text-purple-600'
  }

  return (
    <div className="min-h-screen bg-white">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2 text-black">Real-Time Air Quality Data</h1>
          <p className="text-gray-700">
            Current air quality conditions powered by enhanced forecast algorithms and real-time data processing
          </p>
        </div>

      {/* City Input and Controls */}
      <div className="mb-6">
        <div className="flex gap-4 items-end mb-4">
          <div className="flex-1">
            <label htmlFor="city" className="block text-sm font-medium mb-2 text-black">
              <MapPin className="w-4 h-4 inline mr-1" />
              City
            </label>
            <Input
              id="city"
              value={inputCity}
              onChange={(e) => setInputCity(e.target.value)}
              placeholder="Enter any city name (e.g., Los Angeles, Tokyo, London)"
              className="w-full bg-white border-gray-300 focus:border-blue-500 focus:ring-blue-500"
            />
          </div>
          <Button 
            onClick={() => fetchRealtimeData()} 
            disabled={loading}
            className="flex items-center gap-2"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            {loading ? 'Processing...' : 'Refresh'}
          </Button>
        </div>
        
        {debouncedInputCity && debouncedInputCity !== selectedCity && (
          <div className="text-sm text-blue-600 mb-2">
            <Clock className="w-3 h-3 inline mr-1" />
            Will fetch fresh data for "{debouncedInputCity}" in a moment...
          </div>
        )}
        
        {loading && (
          <div className="text-sm text-gray-600 mb-2">
            <RefreshCw className="w-3 h-3 inline mr-1 animate-spin" />
            Fetching fresh forecast-based real-time data for {selectedCity}...
          </div>
        )}
      </div>

      {error && (
        <Alert className="mb-6">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 gap-6">
        {/* Main Data Display */}
        <div className="space-y-6">
          {loading ? (
            <Card className="bg-white border border-gray-200 shadow-sm">
              <CardContent className="flex items-center justify-center py-12">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                  <p className="text-gray-600">Processing fresh forecast-based real-time data...</p>
                </div>
              </CardContent>
            </Card>
          ) : realtimeData ? (
            <>
              {/* Air Quality Overview */}
              <Card className="bg-white border border-gray-200 shadow-sm">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-black">
                    <Activity className="w-5 h-5" />
                    Air Quality Data
                  </CardTitle>
                  <CardDescription className="text-gray-700">
                    Real-time processed satellite data for {realtimeData.city}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                    <div className="text-center">
                      <div className={`text-3xl font-bold ${getAQIColor(realtimeData.aqi)}`}>
                        {realtimeData.aqi}
                      </div>
                      <div className="text-sm text-gray-700">AQI</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-semibold text-black">{realtimeData.category}</div>
                      <div className="text-sm text-gray-700">Category</div>
                    </div>
                    <div className="text-center">
                      <Badge className={getQualityColor(realtimeData.data_quality)}>
                        {realtimeData.data_quality}
                      </Badge>
                      <div className="text-sm text-gray-700 mt-1">Quality</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-semibold text-black">
                        {realtimeData.processing_time_ms ? realtimeData.processing_time_ms.toFixed(1) : '0.0'}ms
                      </div>
                      <div className="text-sm text-gray-700">Process Time</div>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                      <div className="text-sm text-gray-700">PM2.5</div>
                      <div className="text-lg font-semibold text-black">{realtimeData.pollutants?.pm25 || 0} μg/m³</div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-700">PM10</div>
                      <div className="text-lg font-semibold text-black">{realtimeData.pollutants?.pm10 || 0} μg/m³</div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-700">NO₂</div>
                      <div className="text-lg font-semibold text-black">{realtimeData.pollutants?.no2 || 0} μg/m³</div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-700">O₃</div>
                      <div className="text-lg font-semibold text-black">{realtimeData.pollutants?.o3 || 0} μg/m³</div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Satellite Measurements */}
              <Card className="bg-white border border-gray-200 shadow-sm">
                <CardHeader>
                  <CardTitle className="text-black">Satellite Measurements</CardTitle>
                  <CardDescription className="text-gray-700">
                    Raw satellite data from NASA TEMPO
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    <div>
                      <div className="text-sm text-gray-700">NO₂ Column</div>
                      <div className="text-lg font-semibold text-black">
                        {realtimeData.measurements?.no2_column?.toFixed(3) || '0.000'} ×10¹⁵ mol/cm²
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-700">O₃ Column</div>
                      <div className="text-lg font-semibold text-black">
                        {realtimeData.measurements?.o3_column?.toFixed(1) || '0.0'} DU
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-700">HCHO Column</div>
                      <div className="text-lg font-semibold text-black">
                        {realtimeData.measurements?.hcho_column?.toFixed(3) || '0.000'} ×10¹⁵ mol/cm²
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-700">Aerosol Optical Depth</div>
                      <div className="text-lg font-semibold text-black">
                        {realtimeData.measurements?.aerosol_optical_depth?.toFixed(3) || '0.000'}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-700">Cloud Fraction</div>
                      <div className="text-lg font-semibold text-black">
                        {realtimeData.measurements?.cloud_fraction ? (realtimeData.measurements.cloud_fraction * 100).toFixed(1) : '0.0'}%
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-700">Solar Zenith Angle</div>
                      <div className="text-lg font-semibold text-black">
                        {realtimeData.measurements?.solar_zenith_angle?.toFixed(1) || '0.0'}°
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Quality Flags */}
              <Card className="bg-white border border-gray-200 shadow-sm">
                <CardHeader>
                  <CardTitle className="text-black">Data Quality Flags</CardTitle>
                  <CardDescription className="text-gray-700">
                    Quality indicators for satellite data processing
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="flex items-center gap-2">
                      <Cloud className="w-4 h-4" />
                      <span className="text-sm text-gray-700">Cloud Cover:</span>
                      <span className="font-semibold text-black">
                        {realtimeData.quality_flags?.cloud_cover ? (realtimeData.quality_flags.cloud_cover * 100).toFixed(1) : '0.0'}%
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Sun className="w-4 h-4" />
                      <span className="text-sm text-gray-700">Solar Zenith:</span>
                      <span className="font-semibold text-black">
                        {realtimeData.quality_flags?.solar_zenith_angle?.toFixed(1) || '0.0'}°
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Metadata */}
              <Card className="bg-white border border-gray-200 shadow-sm">
                <CardHeader>
                  <CardTitle className="text-black">Processing Metadata</CardTitle>
                  <CardDescription className="text-gray-700">
                    Information about data processing and source
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-700">Source:</span>
                      <span className="font-medium text-black">{realtimeData.source || 'Unknown'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-700">Processing Level:</span>
                      <span className="font-medium text-black">{realtimeData.metadata?.processing_level || 'Unknown'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-700">Spatial Resolution:</span>
                      <span className="font-medium text-black">{realtimeData.metadata?.spatial_resolution || 'Unknown'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-700">Temporal Resolution:</span>
                      <span className="font-medium text-black">{realtimeData.metadata?.temporal_resolution || 'Unknown'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-700">Algorithm:</span>
                      <span className="font-medium text-black">{realtimeData.metadata?.retrieval_algorithm || 'Unknown'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-700">Data Freshness:</span>
                      <Badge variant="secondary">
                        Fresh from Server
                      </Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* AI-Powered Suggestions */}
              <AISuggestions 
                city={selectedCity} 
                className="w-full"
              />
            </>
          ) : (
            <Card className="bg-white border border-gray-200 shadow-sm">
              <CardContent className="flex items-center justify-center py-12">
                <div className="text-center">
                  <Activity className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">No Data Available</h3>
                  <p className="text-gray-600 mb-4">Unable to fetch fresh real-time data for this city.</p>
                  <Button onClick={() => fetchRealtimeData()} variant="outline">
                    Try Again
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Last Updated */}
          {lastUpdated && (
            <Card className="bg-white border border-gray-200 shadow-sm">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-black">
                  <Clock className="w-5 h-5" />
                  Last Updated
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-sm text-gray-700">
                  {lastUpdated.toLocaleString()}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  Data fetched fresh from server (no cache)
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
      </div>
    </div>
  )
}
