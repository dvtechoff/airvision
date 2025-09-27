'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  Satellite, 
  Globe, 
  BarChart3, 
  Shield, 
  Users, 
  Zap,
  Cloud,
  MapPin,
  TrendingUp,
  AlertTriangle
} from 'lucide-react'

export default function AboutPage() {
  const features = [
    {
      icon: Satellite,
      title: "NASA TEMPO Data",
      description: "Real-time air quality monitoring using NASA's Tropospheric Emissions Monitoring of Pollution satellite",
      color: "text-blue-500"
    },
    {
      icon: Globe,
      title: "North American Coverage",
      description: "Comprehensive air quality monitoring across North America with NASA TEMPO satellite data",
      color: "text-green-500"
    },
    {
      icon: BarChart3,
      title: "AI Forecasting",
      description: "Machine learning models predict air quality trends up to 24 hours in advance",
      color: "text-purple-500"
    },
    {
      icon: Shield,
      title: "Health Protection",
      description: "Personalized health recommendations based on current air quality conditions",
      color: "text-red-500"
    },
    {
      icon: Users,
      title: "Community Alerts",
      description: "Real-time alerts and notifications to keep communities informed",
      color: "text-orange-500"
    },
    {
      icon: Zap,
      title: "Real-time Updates",
      description: "Live data updates every hour with instant notifications for critical changes",
      color: "text-yellow-500"
    }
  ]

  const dataSources = [
    {
      name: "NASA TEMPO",
      description: "Tropospheric Emissions Monitoring of Pollution satellite",
      coverage: "North America",
      frequency: "Hourly",
      pollutants: ["NO₂", "O₃", "HCHO", "Aerosols"],
      color: "bg-blue-500"
    },
    {
      name: "OpenAQ",
      description: "Open air quality data platform",
      coverage: "Global",
      frequency: "Real-time",
      pollutants: ["PM2.5", "PM10", "NO₂", "O₃", "SO₂", "CO"],
      color: "bg-green-500"
    },
    {
      name: "OpenWeatherMap",
      description: "Weather data and forecasts",
      coverage: "Global",
      frequency: "Real-time",
      pollutants: ["Temperature", "Humidity", "Wind", "Pressure"],
      color: "bg-orange-500"
    }
  ]

  const aqiLevels = [
    { range: "0-50", level: "Good", color: "bg-green-500", description: "Air quality is satisfactory" },
    { range: "51-100", level: "Moderate", color: "bg-yellow-500", description: "Air quality is acceptable" },
    { range: "101-150", level: "Unhealthy for Sensitive Groups", color: "bg-orange-500", description: "Sensitive groups may experience health effects" },
    { range: "151-200", level: "Unhealthy", color: "bg-red-500", description: "Everyone may begin to experience health effects" },
    { range: "201-300", level: "Very Unhealthy", color: "bg-purple-500", description: "Health warnings of emergency conditions" },
    { range: "300+", level: "Hazardous", color: "bg-red-800", description: "Health alert: everyone may experience serious health effects" }
  ]

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="space-y-8">
        {/* Hero Section */}
        <div className="text-center py-12 bg-white rounded-lg border border-gray-200 card-shadow">
          <div className="max-w-4xl mx-auto px-4">
            <Cloud className="w-16 h-16 mx-auto mb-4 text-blue-600" />
            <h1 className="text-4xl font-bold mb-4 text-gray-900">AirVision</h1>
            <p className="text-xl mb-6 text-gray-600">
              From Earth Data to Safer Skies - Real-time air quality monitoring powered by NASA TEMPO satellite data
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <Badge className="bg-blue-100 text-blue-700 border border-blue-200 px-4 py-2">
                <Satellite className="w-4 h-4 mr-2" />
                NASA TEMPO Data
              </Badge>
              <Badge className="bg-green-100 text-green-700 border border-green-200 px-4 py-2">
                <TrendingUp className="w-4 h-4 mr-2" />
                AI Forecasting
              </Badge>
              <Badge className="bg-purple-100 text-purple-700 border border-purple-200 px-4 py-2">
                <Shield className="w-4 h-4 mr-2" />
                Health Protection
              </Badge>
            </div>
          </div>
      </div>

      {/* Mission Statement */}
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">Our Mission</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-lg text-gray-600 leading-relaxed">
            We believe that everyone has the right to breathe clean air. Our mission is to democratize access to 
            real-time air quality information by leveraging NASA&apos;s cutting-edge TEMPO satellite technology. 
            By combining space-based observations with ground measurements and AI-powered forecasting, 
            we empower individuals and communities to make informed decisions about their health and environment.
          </p>
        </CardContent>
      </Card>

      {/* Features Grid */}
      <div>
        <h2 className="text-3xl font-bold text-center mb-8">Key Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => {
            const Icon = feature.icon
            return (
              <Card key={index} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <Icon className={`w-8 h-8 ${feature.color} mb-2`} />
                  <CardTitle className="text-lg">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600">{feature.description}</p>
                </CardContent>
              </Card>
            )
          })}
        </div>
      </div>

      {/* Data Sources */}
      <div>
        <h2 className="text-3xl font-bold text-center mb-8">Data Sources</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {dataSources.map((source, index) => (
            <Card key={index}>
              <CardHeader>
                <div className="flex items-center space-x-2">
                  <div className={`w-4 h-4 rounded-full ${source.color}`}></div>
                  <CardTitle className="text-lg">{source.name}</CardTitle>
                </div>
                <p className="text-sm text-gray-600">{source.description}</p>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Coverage:</span>
                    <span className="font-medium">{source.coverage}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Frequency:</span>
                    <span className="font-medium">{source.frequency}</span>
                  </div>
                  <div className="mt-3">
                    <p className="text-sm text-gray-500 mb-2">Pollutants:</p>
                    <div className="flex flex-wrap gap-1">
                      {source.pollutants.map((pollutant, i) => (
                        <Badge key={i} variant="outline" className="text-xs">
                          {pollutant}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* AQI Scale */}
      <div>
        <h2 className="text-3xl font-bold text-center mb-8">Air Quality Index (AQI) Scale</h2>
        <Card>
          <CardContent className="p-6">
            <div className="space-y-3">
              {aqiLevels.map((level, index) => (
                <div key={index} className="flex items-center space-x-4 p-3 rounded-lg hover:bg-gray-50">
                  <div className={`w-6 h-6 rounded-full ${level.color}`}></div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-semibold">{level.level}</span>
                      <Badge variant="outline">{level.range}</Badge>
                    </div>
                    <p className="text-sm text-gray-600">{level.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Technology Stack */}
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">Technology Stack</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h3 className="text-lg font-semibold mb-4">Frontend</h3>
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <span>Next.js 14 with App Router</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <span>React 18 with TypeScript</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <span>TailwindCSS for styling</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <span>ShadCN/UI components</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <span>Recharts for data visualization</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <span>Leaflet.js for interactive maps</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <span>Framer Motion for animations</span>
                </div>
              </div>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Backend & Data</h3>
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>FastAPI (Python) for API</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>Pandas & Xarray for data processing</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>Scikit-learn for ML models</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>Statsmodels for ARIMA forecasting</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>NASA EarthData API integration</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>OpenAQ & OpenWeatherMap APIs</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>Pydantic for data validation</span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Call to Action */}
      <Card className="bg-gradient-to-r from-blue-50 to-purple-50">
        <CardContent className="text-center py-12">
          <h2 className="text-3xl font-bold mb-4">Ready to Take Action?</h2>
          <p className="text-lg text-gray-600 mb-6">
            Start monitoring air quality in your area and make informed decisions about your health.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Button size="lg">
              <MapPin className="w-5 h-5 mr-2" />
              Check Your Area
            </Button>
            <Button variant="outline" size="lg">
              <AlertTriangle className="w-5 h-5 mr-2" />
              Set Up Alerts
            </Button>
          </div>
        </CardContent>
      </Card>
      </div>
    </div>
  )
}
