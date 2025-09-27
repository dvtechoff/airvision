'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  MessageSquare, 
  AlertTriangle, 
  Users, 
  TrendingUp, 
  MapPin, 
  Clock,
  ThumbsUp,
  ThumbsDown,
  FileText,
  Phone,
  Mail
} from 'lucide-react'
import FeedbackForm from '@/components/FeedbackForm'
import IncidentReportForm from '@/components/IncidentReportForm'
import CommunityIncidentList from '@/components/CommunityIncidentList'
import CommunityStats from '@/components/CommunityStats'

export default function CommunityPage() {
  const [activeTab, setActiveTab] = useState('incidents')
  const [communityStats, setCommunityStats] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchCommunityStats()
  }, [])

  const fetchCommunityStats = async () => {
    try {
      const response = await fetch('/api/community/stats')
      if (response.ok) {
        const stats = await response.json()
        setCommunityStats(stats)
      }
    } catch (error) {
      console.error('Failed to fetch community stats:', error)
    }
  }

  const tabs = [
    { id: 'incidents', label: 'Community Reports', icon: AlertTriangle },
    { id: 'feedback', label: 'Feedback', icon: MessageSquare },
    { id: 'report', label: 'Report Incident', icon: FileText },
    { id: 'stats', label: 'Community Stats', icon: TrendingUp }
  ]

  return (
    <div className="min-h-screen bg-white text-black p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold text-black">Community Hub</h1>
          <p className="text-lg text-gray-700 max-w-3xl mx-auto">
            Help improve air quality monitoring by reporting incidents, providing feedback, 
            and staying informed about air quality issues in your community.
          </p>
        </div>

        {/* Quick Stats */}
        {communityStats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card className="bg-white border-gray-200">
              <CardContent className="p-4 text-center">
                <div className="text-2xl font-bold text-blue-600">{communityStats.total_reports}</div>
                <div className="text-sm text-gray-600">Total Reports</div>
              </CardContent>
            </Card>
            <Card className="bg-white border-gray-200">
              <CardContent className="p-4 text-center">
                <div className="text-2xl font-bold text-green-600">{communityStats.verified_reports}</div>
                <div className="text-sm text-gray-600">Verified</div>
              </CardContent>
            </Card>
            <Card className="bg-white border-gray-200">
              <CardContent className="p-4 text-center">
                <div className="text-2xl font-bold text-orange-600">{communityStats.active_incidents}</div>
                <div className="text-sm text-gray-600">Active Incidents</div>
              </CardContent>
            </Card>
            <Card className="bg-white border-gray-200">
              <CardContent className="p-4 text-center">
                <div className="text-2xl font-bold text-purple-600">{communityStats.response_rate}%</div>
                <div className="text-sm text-gray-600">Response Rate</div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Tab Navigation */}
        <div className="flex flex-wrap justify-center gap-2">
          {tabs.map((tab) => {
            const IconComponent = tab.icon
            return (
              <Button
                key={tab.id}
                variant={activeTab === tab.id ? "default" : "outline"}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 ${
                  activeTab === tab.id 
                    ? "bg-blue-600 text-white hover:bg-blue-700" 
                    : "bg-white text-black border-gray-300 hover:bg-gray-100"
                }`}
              >
                <IconComponent className="w-4 h-4" />
                <span>{tab.label}</span>
              </Button>
            )
          })}
        </div>

        {/* Tab Content */}
        <div className="mt-6">
          {activeTab === 'incidents' && (
            <div className="space-y-6">
              <Card className="bg-blue-50 border-blue-200">
                <CardContent className="p-6">
                  <div className="flex items-start space-x-4">
                    <Users className="w-8 h-8 text-blue-600 mt-1" />
                    <div>
                      <h3 className="text-lg font-semibold text-black">Community Incident Reports</h3>
                      <p className="text-gray-700 mt-2">
                        View verified air quality incidents reported by community members. 
                        These reports help identify pollution sources and air quality issues 
                        that may not be captured by automated sensors.
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <CommunityIncidentList />
            </div>
          )}

          {activeTab === 'feedback' && (
            <div className="space-y-6">
              <Card className="bg-green-50 border-green-200">
                <CardContent className="p-6">
                  <div className="flex items-start space-x-4">
                    <MessageSquare className="w-8 h-8 text-green-600 mt-1" />
                    <div>
                      <h3 className="text-lg font-semibold text-black">Share Your Feedback</h3>
                      <p className="text-gray-700 mt-2">
                        Help us improve AirVision by sharing your thoughts, reporting bugs, 
                        suggesting features, or providing feedback about data accuracy.
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <FeedbackForm onSubmissionSuccess={() => fetchCommunityStats()} />
            </div>
          )}

          {activeTab === 'report' && (
            <div className="space-y-6">
              <Card className="bg-orange-50 border-orange-200">
                <CardContent className="p-6">
                  <div className="flex items-start space-x-4">
                    <AlertTriangle className="w-8 h-8 text-orange-600 mt-1" />
                    <div>
                      <h3 className="text-lg font-semibold text-black">Report an Air Quality Incident</h3>
                      <p className="text-gray-700 mt-2">
                        Report pollution incidents, unusual odors, or air quality issues in your area. 
                        Your reports help create a comprehensive picture of air quality conditions 
                        and can alert others in your community.
                      </p>
                      <div className="mt-4 p-4 bg-white rounded-lg border border-orange-200">
                        <h4 className="font-semibold text-black mb-2">What should you report?</h4>
                        <ul className="text-sm text-gray-700 space-y-1">
                          <li>• Industrial emissions or visible pollution</li>
                          <li>• Unusual or strong odors</li>
                          <li>• Wildfire smoke or dust storms</li>
                          <li>• Construction dust or traffic pollution</li>
                          <li>• Health symptoms related to air quality</li>
                          <li>• Discrepancies in sensor readings</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <IncidentReportForm onSubmissionSuccess={() => fetchCommunityStats()} />
            </div>
          )}

          {activeTab === 'stats' && (
            <div className="space-y-6">
              <Card className="bg-purple-50 border-purple-200">
                <CardContent className="p-6">
                  <div className="flex items-start space-x-4">
                    <TrendingUp className="w-8 h-8 text-purple-600 mt-1" />
                    <div>
                      <h3 className="text-lg font-semibold text-black">Community Engagement</h3>
                      <p className="text-gray-700 mt-2">
                        View statistics about community participation, incident verification rates, 
                        and overall engagement with air quality monitoring efforts.
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              {communityStats && <CommunityStats stats={communityStats} />}
            </div>
          )}
        </div>

        {/* Contact Information */}
        <Card className="bg-gray-50 border-gray-200 mt-8">
          <CardContent className="p-6">
            <h3 className="text-lg font-semibold text-black mb-4">Need Help?</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-center space-x-3">
                <Mail className="w-5 h-5 text-blue-600" />
                <div>
                  <div className="font-medium text-black">Email Support</div>
                  <div className="text-sm text-gray-600">support@airvision.app</div>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <Phone className="w-5 h-5 text-green-600" />
                <div>
                  <div className="font-medium text-black">Emergency Line</div>
                  <div className="text-sm text-gray-600">1-800-AIR-HELP</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}