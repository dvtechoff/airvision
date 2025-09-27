'use client'

import { useState, useEffect } from 'react'

export default function SimpleTestPage() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchSimpleData()
  }, [])

  const fetchSimpleData = async () => {
    setLoading(true)
    setError(null)
    
    try {
      console.log('Fetching from: http://localhost:8000/api/current?city=New York')
      
      const response = await fetch('http://localhost:8000/api/current?city=New York', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      
      console.log('Response status:', response.status)
      console.log('Response headers:', response.headers)
      
      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`HTTP ${response.status}: ${errorText}`)
      }
      
      const jsonData = await response.json()
      console.log('Received data:', jsonData)
      
      setData(jsonData)
    } catch (err) {
      console.error('Fetch error:', err)
      setError(err instanceof Error ? err.message : 'Unknown error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold mb-6">Simple API Test</h1>
        
        {loading && (
          <div className="bg-white rounded-lg shadow p-6 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p>Loading data...</p>
          </div>
        )}
        
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-6">
            <h2 className="text-red-800 font-semibold mb-2">Error:</h2>
            <p className="text-red-600">{error}</p>
            <button
              onClick={fetchSimpleData}
              className="mt-4 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
            >
              Try Again
            </button>
          </div>
        )}
        
        {data && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-green-800 font-semibold mb-4">✅ Success!</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-medium mb-2">Basic Info</h3>
                <p><strong>City:</strong> {data.city}</p>
                <p><strong>AQI:</strong> <span className="text-2xl font-bold text-orange-600">{data.aqi}</span></p>
                <p><strong>Category:</strong> {data.category}</p>
                <p><strong>Source:</strong> {data.source}</p>
              </div>
              
              <div>
                <h3 className="font-medium mb-2">Pollutants</h3>
                {data.pollutants && Object.entries(data.pollutants).map(([key, value]) => (
                  <p key={key}>
                    <strong>{key.toUpperCase()}:</strong> {value as string}
                  </p>
                ))}
              </div>
            </div>
            
            <div className="mt-4 pt-4 border-t">
              <p className="text-sm text-gray-600">
                <strong>Last Updated:</strong> {new Date(data.timestamp).toLocaleString()}
              </p>
            </div>
            
            <div className="mt-4 p-4 bg-gray-50 rounded">
              <h3 className="font-medium mb-2">Raw Data:</h3>
              <pre className="text-xs overflow-auto">
                {JSON.stringify(data, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}