'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { apiClient, RealtimeData, CacheStats, QualityMetrics } from '@/lib/api'
import { RefreshCw, Database, Activity, AlertTriangle, CheckCircle, Clock, Cloud, Sun } from 'lucide-react'

export default function RealtimePage() {
  const [city, setCity] = useState('New York')
  const [realtimeData, setRealtimeData] = useState<RealtimeData | null>(null)
  const [cacheStats, setCacheStats] = useState<CacheStats | null>(null)
  const [qualityMetrics, setQualityMetrics] = useState<QualityMetrics | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  const fetchRealtimeData = async (forceRefresh = false) => {
    try {
      setLoading(true)
      setError(null)
      const data = await apiClient.getRealtimeData(city, forceRefresh)
      setRealtimeData(data)
      setLastUpdated(new Date())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch real-time data')
    } finally {
      setLoading(false)
    }
  }

  const fetchCacheStats = async () => {
    try {
      const response = await apiClient.getCacheStats()
      setCacheStats(response.cache_statistics)
    } catch (err) {
      console.error('Failed to fetch cache stats:', err)
    }
  }

  const fetchQualityMetrics = async () => {
    try {
      const response = await apiClient.getQualityMetrics(city)
      setQualityMetrics(response.quality_metrics)
    } catch (err) {
      console.error('Failed to fetch quality metrics:', err)
    }
  }

  const clearCache = async () => {
    try {
      await apiClient.clearCache()
      await fetchCacheStats()
      await fetchRealtimeData(true) // Force refresh after clearing cache
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to clear cache')
    }
  }

  useEffect(() => {
    fetchRealtimeData()
    fetchCacheStats()
    fetchQualityMetrics()
  }, [city])

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
          <h1 className="text-3xl font-bold mb-2 text-black">Real-Time Air Quality Processing</h1>
          <p className="text-gray-700">
            Live satellite data processing with quality filtering and intelligent caching
          </p>
        </div>

      {/* City Input and Controls */}
      <div className="mb-6 flex gap-4 items-end">
        <div className="flex-1">
          <label htmlFor="city" className="block text-sm font-medium mb-2 text-black">
            City
          </label>
          <Input
            id="city"
            value={city}
            onChange={(e) => setCity(e.target.value)}
            placeholder="Enter city name"
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
        <Button 
          onClick={() => fetchRealtimeData(true)} 
          disabled={loading}
          variant="outline"
          className="flex items-center gap-2"
        >
          <Database className="w-4 h-4" />
          Force Refresh
        </Button>
      </div>

      {error && (
        <Alert className="mb-6">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Data Display */}
        <div className="lg:col-span-2 space-y-6">
          {loading ? (
            <Card className="bg-white border border-gray-200 shadow-sm">
              <CardContent className="flex items-center justify-center py-12">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                  <p className="text-gray-600">Processing real-time data...</p>
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
                      <span className="text-gray-700">Cached:</span>
                      <Badge variant={realtimeData.cache_info?.cached ? "default" : "secondary"}>
                        {realtimeData.cache_info?.cached ? "Yes" : "No"}
                      </Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </>
          ) : (
            <Card className="bg-white border border-gray-200 shadow-sm">
              <CardContent className="flex items-center justify-center py-12">
                <div className="text-center">
                  <Activity className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">No Data Available</h3>
                  <p className="text-gray-600 mb-4">Unable to fetch real-time data for this city.</p>
                  <Button onClick={() => fetchRealtimeData()} variant="outline">
                    Try Again
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Cache Statistics */}
          <Card className="bg-white border border-gray-200 shadow-sm">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-black">
                <Database className="w-5 h-5" />
                Cache Statistics
              </CardTitle>
            </CardHeader>
            <CardContent>
              {cacheStats ? (
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-700">Total Entries:</span>
                    <span className="font-semibold text-black">{cacheStats.total_entries}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-700">Cache Size:</span>
                    <span className="font-semibold text-black">{cacheStats.total_size_mb} MB</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-700">Hit Rate:</span>
                    <span className="font-semibold text-black">{(cacheStats.hit_rate * 100).toFixed(1)}%</span>
                  </div>
                  <Button 
                    onClick={clearCache} 
                    variant="outline" 
                    size="sm" 
                    className="w-full mt-3"
                  >
                    Clear Cache
                  </Button>
                </div>
              ) : (
                <div className="text-sm text-gray-600">Loading cache statistics...</div>
              )}
            </CardContent>
          </Card>

          {/* Quality Metrics */}
          <Card className="bg-white border border-gray-200 shadow-sm">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-black">
                <CheckCircle className="w-5 h-5" />
                Quality Metrics
              </CardTitle>
            </CardHeader>
            <CardContent>
              {qualityMetrics ? (
                <div className="space-y-3">
                  <div>
                    <div className="text-sm text-gray-700 mb-2">Quality Distribution</div>
                    <div className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span className="text-gray-700">Excellent</span>
                        <span className="text-black">{(qualityMetrics.quality_distribution.excellent * 100).toFixed(1)}%</span>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span className="text-gray-700">Good</span>
                        <span className="text-black">{(qualityMetrics.quality_distribution.good * 100).toFixed(1)}%</span>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span className="text-gray-700">Fair</span>
                        <span className="text-black">{(qualityMetrics.quality_distribution.fair * 100).toFixed(1)}%</span>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span className="text-gray-700">Poor</span>
                        <span className="text-black">{(qualityMetrics.quality_distribution.poor * 100).toFixed(1)}%</span>
                      </div>
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-700 mb-2">Performance</div>
                    <div className="space-y-1 text-xs">
                      <div className="flex justify-between">
                        <span className="text-gray-700">Avg Process Time:</span>
                        <span className="text-black">{qualityMetrics.processing_performance.average_processing_time_ms.toFixed(1)}ms</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-700">Cache Hit Rate:</span>
                        <span className="text-black">{(qualityMetrics.processing_performance.cache_hit_rate * 100).toFixed(1)}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-700">Data Availability:</span>
                        <span className="text-black">{(qualityMetrics.processing_performance.data_availability * 100).toFixed(1)}%</span>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-sm text-gray-600">Loading quality metrics...</div>
              )}
            </CardContent>
          </Card>

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
              </CardContent>
            </Card>
          )}
        </div>
      </div>
      </div>
    </div>
  )
}
