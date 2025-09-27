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
    <div className="min-h-screen bg-white text-black">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="space-y-12">
          {/* Hero Section */}
          <div className="text-center py-16 bg-gradient-to-br from-blue-50 to-purple-50 rounded-2xl border border-gray-200 shadow-sm">
            <div className="max-w-4xl mx-auto px-4">
              <div className="mb-8">
                <div className="inline-flex p-4 bg-blue-600 rounded-full mb-6">
                  <Cloud className="w-12 h-12 text-white" />
                </div>
                <h1 className="text-5xl font-bold mb-6 text-black">
                  Air<span className="text-blue-600">Vision</span>
                </h1>
                <p className="text-xl mb-8 text-gray-700 leading-relaxed">
                  From Earth Data to Safer Skies - Professional air quality monitoring 
                  powered by NASA TEMPO satellite technology and AI forecasting
                </p>
                <div className="flex flex-wrap justify-center gap-3">
                  <Badge className="bg-blue-100 text-blue-800 border-blue-200 px-4 py-2 text-sm">
                    <Satellite className="w-4 h-4 mr-2" />
                    NASA TEMPO Data
                  </Badge>
                  <Badge className="bg-green-100 text-green-800 border-green-200 px-4 py-2 text-sm">
                    <TrendingUp className="w-4 h-4 mr-2" />
                    AI Forecasting
                  </Badge>
                  <Badge className="bg-purple-100 text-purple-800 border-purple-200 px-4 py-2 text-sm">
                    <Shield className="w-4 h-4 mr-2" />
                    Health Protection
                  </Badge>
                  <Badge className="bg-orange-100 text-orange-800 border-orange-200 px-4 py-2 text-sm">
                    <Users className="w-4 h-4 mr-2" />
                    Community Driven
                  </Badge>
                </div>
              </div>
            </div>
          </div>

          {/* Mission Statement */}
          <Card className="bg-white border-gray-200 shadow-sm">
            <CardHeader className="text-center pb-4">
              <CardTitle className="text-3xl font-bold text-black">Our Mission</CardTitle>
            </CardHeader>
            <CardContent className="px-8 pb-8">
              <p className="text-lg text-gray-700 leading-relaxed text-center max-w-4xl mx-auto">
                We believe that everyone has the right to breathe clean air. Our mission is to democratize access to 
                real-time air quality information by leveraging NASA's cutting-edge TEMPO satellite technology. 
                By combining space-based observations with ground measurements, AI-powered forecasting, and community reporting, 
                we empower individuals and communities to make informed decisions about their health and environment.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
                <div className="text-center p-4 bg-blue-50 rounded-lg border border-blue-100">
                  <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-3">
                    <Satellite className="w-6 h-6 text-white" />
                  </div>
                  <h4 className="font-semibold text-black mb-2">Satellite Technology</h4>
                  <p className="text-sm text-gray-600">NASA TEMPO provides hourly air quality data</p>
                </div>
                <div className="text-center p-4 bg-green-50 rounded-lg border border-green-100">
                  <div className="w-12 h-12 bg-green-600 rounded-full flex items-center justify-center mx-auto mb-3">
                    <BarChart3 className="w-6 h-6 text-white" />
                  </div>
                  <h4 className="font-semibold text-black mb-2">AI Forecasting</h4>
                  <p className="text-sm text-gray-600">Machine learning predicts air quality trends</p>
                </div>
                <div className="text-center p-4 bg-purple-50 rounded-lg border border-purple-100">
                  <div className="w-12 h-12 bg-purple-600 rounded-full flex items-center justify-center mx-auto mb-3">
                    <Users className="w-6 h-6 text-white" />
                  </div>
                  <h4 className="font-semibold text-black mb-2">Community Focus</h4>
                  <p className="text-sm text-gray-600">User reports enhance sensor accuracy</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Features Grid */}
          <div className="py-8">
            <h2 className="text-4xl font-bold text-center mb-12 text-black">Key Features</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {features.map((feature, index) => {
                const Icon = feature.icon
                return (
                  <Card key={index} className="bg-white border-gray-200 shadow-sm hover:shadow-md transition-all duration-300 group">
                    <CardHeader className="text-center pb-4">
                      <div className="inline-flex p-3 bg-gray-50 rounded-full mb-4 group-hover:bg-blue-50 transition-colors">
                        <Icon className={`w-8 h-8 ${feature.color}`} />
                      </div>
                      <CardTitle className="text-xl font-semibold text-black">{feature.title}</CardTitle>
                    </CardHeader>
                    <CardContent className="text-center">
                      <p className="text-gray-600 leading-relaxed">{feature.description}</p>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          </div>

          {/* Data Sources */}
          <div className="py-8">
            <h2 className="text-4xl font-bold text-center mb-12 text-black">Data Sources</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {dataSources.map((source, index) => (
                <Card key={index} className="bg-white border-gray-200 shadow-sm hover:shadow-md transition-all duration-300">
                  <CardHeader className="pb-4">
                    <div className="flex items-center space-x-3 mb-3">
                      <div className={`w-3 h-3 rounded-full ${source.color}`}></div>
                      <CardTitle className="text-xl font-semibold text-black">{source.name}</CardTitle>
                    </div>
                    <p className="text-gray-600 text-sm leading-relaxed">{source.description}</p>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center text-sm">
                        <span className="text-gray-500 font-medium">Coverage:</span>
                        <span className="font-semibold text-black">{source.coverage}</span>
                      </div>
                      <div className="flex justify-between items-center text-sm">
                        <span className="text-gray-500 font-medium">Frequency:</span>
                        <span className="font-semibold text-black">{source.frequency}</span>
                      </div>
                      <div className="pt-2 border-t border-gray-100">
                        <p className="text-sm font-medium text-gray-500 mb-3">Monitored Parameters:</p>
                        <div className="flex flex-wrap gap-1.5">
                          {source.pollutants.map((pollutant, i) => (
                            <Badge key={i} variant="outline" className="text-xs bg-gray-50 text-gray-700 border-gray-200">
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
          <div className="py-8">
            <h2 className="text-4xl font-bold text-center mb-12 text-black">Air Quality Index (AQI) Scale</h2>
            <Card className="bg-white border-gray-200 shadow-sm">
              <CardContent className="p-8">
                <div className="space-y-4">
                  {aqiLevels.map((level, index) => (
                    <div key={index} className="flex items-center space-x-6 p-4 rounded-xl hover:bg-gray-50 transition-colors border border-gray-100">
                      <div className={`w-8 h-8 rounded-full ${level.color} shadow-sm`}></div>
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-1">
                          <span className="font-bold text-lg text-black">{level.level}</span>
                          <Badge variant="outline" className="bg-white border-gray-300 text-gray-700 font-medium">
                            {level.range}
                          </Badge>
                        </div>
                        <p className="text-gray-600 leading-relaxed">{level.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Technology Stack */}
          <Card className="bg-white border-gray-200 shadow-sm">
            <CardHeader className="text-center pb-6">
              <CardTitle className="text-3xl font-bold text-black">Technology Stack</CardTitle>
              <p className="text-gray-600 mt-2">Built with modern, scalable technologies for reliability and performance</p>
            </CardHeader>
            <CardContent className="px-8 pb-8">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
                <div className="space-y-4">
                  <div className="flex items-center space-x-3 mb-6">
                    <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                      <Globe className="w-5 h-5 text-white" />
                    </div>
                    <h3 className="text-2xl font-bold text-black">Frontend</h3>
                  </div>
                  <div className="space-y-3">
                    <div className="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg border border-blue-100">
                      <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                      <span className="text-gray-800 font-medium">Next.js 14 with App Router</span>
                    </div>
                    <div className="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg border border-blue-100">
                      <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                      <span className="text-gray-800 font-medium">React 18 with TypeScript</span>
                    </div>
                    <div className="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg border border-blue-100">
                      <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                      <span className="text-gray-800 font-medium">TailwindCSS for styling</span>
                    </div>
                    <div className="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg border border-blue-100">
                      <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                      <span className="text-gray-800 font-medium">ShadCN/UI components</span>
                    </div>
                    <div className="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg border border-blue-100">
                      <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                      <span className="text-gray-800 font-medium">Recharts for data visualization</span>
                    </div>
                    <div className="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg border border-blue-100">
                      <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                      <span className="text-gray-800 font-medium">Framer Motion for animations</span>
                    </div>
                  </div>
                </div>
                <div className="space-y-4">
                  <div className="flex items-center space-x-3 mb-6">
                    <div className="w-8 h-8 bg-green-600 rounded-lg flex items-center justify-center">
                      <Zap className="w-5 h-5 text-white" />
                    </div>
                    <h3 className="text-2xl font-bold text-black">Backend & Data</h3>
                  </div>
                  <div className="space-y-3">
                    <div className="flex items-center space-x-3 p-3 bg-green-50 rounded-lg border border-green-100">
                      <div className="w-2 h-2 bg-green-600 rounded-full"></div>
                      <span className="text-gray-800 font-medium">FastAPI (Python) for API</span>
                    </div>
                    <div className="flex items-center space-x-3 p-3 bg-green-50 rounded-lg border border-green-100">
                      <div className="w-2 h-2 bg-green-600 rounded-full"></div>
                      <span className="text-gray-800 font-medium">Pandas & Xarray for data processing</span>
                    </div>
                    <div className="flex items-center space-x-3 p-3 bg-green-50 rounded-lg border border-green-100">
                      <div className="w-2 h-2 bg-green-600 rounded-full"></div>
                      <span className="text-gray-800 font-medium">Scikit-learn for ML models</span>
                    </div>
                    <div className="flex items-center space-x-3 p-3 bg-green-50 rounded-lg border border-green-100">
                      <div className="w-2 h-2 bg-green-600 rounded-full"></div>
                      <span className="text-gray-800 font-medium">NASA EarthData API integration</span>
                    </div>
                    <div className="flex items-center space-x-3 p-3 bg-green-50 rounded-lg border border-green-100">
                      <div className="w-2 h-2 bg-green-600 rounded-full"></div>
                      <span className="text-gray-800 font-medium">OpenWeatherMap APIs</span>
                    </div>
                    <div className="flex items-center space-x-3 p-3 bg-green-50 rounded-lg border border-green-100">
                      <div className="w-2 h-2 bg-green-600 rounded-full"></div>
                      <span className="text-gray-800 font-medium">Community Reporting System</span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Call to Action */}
          <Card className="bg-gradient-to-br from-blue-50 to-purple-50 border-blue-200 shadow-sm">
            <CardContent className="text-center py-16">
              <div className="max-w-3xl mx-auto">
                <h2 className="text-4xl font-bold mb-6 text-black">Ready to Take Action?</h2>
                <p className="text-xl text-gray-700 mb-10 leading-relaxed">
                  Start monitoring air quality in your area, receive alerts about pollution events, 
                  and contribute to your community's environmental awareness.
                </p>
                <div className="flex flex-wrap justify-center gap-4">
                  <Button size="lg" className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3">
                    <MapPin className="w-5 h-5 mr-2" />
                    Check Your Area
                  </Button>
                  <Button variant="outline" size="lg" className="border-blue-600 text-blue-600 hover:bg-blue-50 px-8 py-3">
                    <AlertTriangle className="w-5 h-5 mr-2" />
                    Set Up Alerts
                  </Button>
                  <Button variant="outline" size="lg" className="border-purple-600 text-purple-600 hover:bg-purple-50 px-8 py-3">
                    <Users className="w-5 h-5 mr-2" />
                    Join Community
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
