'use client'

import { useState, useEffect } from 'react'

export default function DebugPage() {
  const [apiTest, setApiTest] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    testAPI()
  }, [])

  const testAPI = async () => {
    setLoading(true)
    setError(null)
    
    try {
      console.log('Testing API connection...')
      
      // Test direct fetch
      const response = await fetch('http://localhost:8000/api/current?city=New York')
      console.log('Response status:', response.status)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      console.log('API Response:', data)
      
      setApiTest(data)
    } catch (err) {
      console.error('API Test Error:', err)
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8 text-center">API Debug Page</h1>
        
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">API Connection Test</h2>
          
          {loading && (
            <div className="text-blue-600">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              Testing API connection...
            </div>
          )}
          
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
              <h3 className="text-red-800 font-medium">Error:</h3>
              <p className="text-red-600">{error}</p>
            </div>
          )}
          
          {apiTest && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h3 className="text-green-800 font-medium mb-2">✅ API Response Successful!</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p><strong>City:</strong> {apiTest.city}</p>
                  <p><strong>AQI:</strong> {apiTest.aqi}</p>
                  <p><strong>Category:</strong> {apiTest.category}</p>
                  <p><strong>Source:</strong> {apiTest.source}</p>
                  <p><strong>Timestamp:</strong> {new Date(apiTest.timestamp).toLocaleString()}</p>
                </div>
                <div>
                  <h4 className="font-medium mb-2">Pollutants:</h4>
                  {apiTest.pollutants && Object.entries(apiTest.pollutants).map(([key, value]) => (
                    <p key={key}><strong>{key.toUpperCase()}:</strong> {value as string}</p>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
        
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Debug Information</h2>
          <div className="space-y-2 text-sm">
            <p><strong>Current URL:</strong> {typeof window !== 'undefined' ? window.location.href : 'N/A'}</p>
            <p><strong>Backend URL:</strong> http://localhost:8000</p>
            <p><strong>API Endpoint:</strong> http://localhost:8000/api/current</p>
          </div>
          
          <button
            onClick={testAPI}
            className="mt-4 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Test API Again
          </button>
        </div>
      </div>
    </div>
  )
}