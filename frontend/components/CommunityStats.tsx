'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { 
  BarChart3, 
  TrendingUp, 
  Users, 
  CheckCircle, 
  Clock, 
  MessageSquare,
  AlertTriangle,
  Award
} from 'lucide-react'

interface CommunityStatsProps {
  stats: {
    total_reports: number
    verified_reports: number
    active_incidents: number
    total_feedback: number
    response_rate: number
    average_verification_time_hours: number
    top_incident_types: Array<{ type: string; count: number }>
    community_engagement_score: number
  }
}

export default function CommunityStats({ stats }: CommunityStatsProps) {
  const getEngagementLevel = (score: number) => {
    if (score >= 80) return { level: 'Excellent', color: 'text-green-600', bgColor: 'bg-green-100' }
    if (score >= 60) return { level: 'Good', color: 'text-blue-600', bgColor: 'bg-blue-100' }
    if (score >= 40) return { level: 'Fair', color: 'text-yellow-600', bgColor: 'bg-yellow-100' }
    return { level: 'Needs Improvement', color: 'text-red-600', bgColor: 'bg-red-100' }
  }

  const getIncidentTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      'air_quality_spike': 'Air Quality Spikes',
      'industrial_emission': 'Industrial Emissions',
      'wildfire_smoke': 'Wildfire Smoke',
      'traffic_pollution': 'Traffic Pollution',
      'construction_dust': 'Construction Dust',
      'chemical_spill': 'Chemical Spills',
      'unusual_odor': 'Unusual Odors',
      'respiratory_irritation': 'Respiratory Issues',
      'other': 'Other Issues'
    }
    return labels[type] || type
  }

  const engagementInfo = getEngagementLevel(stats.community_engagement_score)

  return (
    <div className="space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="bg-white border-gray-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Reports</p>
                <p className="text-3xl font-bold text-black">{stats.total_reports}</p>
              </div>
              <BarChart3 className="w-8 h-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white border-gray-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Verified Reports</p>
                <p className="text-3xl font-bold text-green-600">{stats.verified_reports}</p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white border-gray-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active Incidents</p>
                <p className="text-3xl font-bold text-orange-600">{stats.active_incidents}</p>
              </div>
              <AlertTriangle className="w-8 h-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white border-gray-200">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Feedback</p>
                <p className="text-3xl font-bold text-purple-600">{stats.total_feedback}</p>
              </div>
              <MessageSquare className="w-8 h-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Statistics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Performance Metrics */}
        <Card className="bg-white border-gray-200">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-black">
              <TrendingUp className="w-5 h-5 text-blue-600" />
              <span>Performance Metrics</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-black">Response Rate</span>
                <span className="text-2xl font-bold text-black">{stats.response_rate}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${Math.min(stats.response_rate, 100)}%` }}
                ></div>
              </div>
              <p className="text-xs text-gray-600 mt-1">
                Percentage of reports that receive verification
              </p>
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-black">Avg. Verification Time</span>
                <span className="text-2xl font-bold text-black">
                  {stats.average_verification_time_hours.toFixed(1)}h
                </span>
              </div>
              <div className="flex items-center text-sm text-gray-600">
                <Clock className="w-4 h-4 mr-1" />
                <span>
                  {stats.average_verification_time_hours < 6
                    ? 'Excellent response time'
                    : stats.average_verification_time_hours < 24
                    ? 'Good response time'
                    : 'Could be improved'}
                </span>
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-black">Community Engagement</span>
                <span className={`text-2xl font-bold ${engagementInfo.color}`}>
                  {stats.community_engagement_score.toFixed(1)}
                </span>
              </div>
              <div className={`px-3 py-1 rounded-full text-sm font-medium ${engagementInfo.bgColor} ${engagementInfo.color}`}>
                {engagementInfo.level}
              </div>
              <p className="text-xs text-gray-600 mt-1">
                Based on participation, votes, and feedback quality
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Top Incident Types */}
        <Card className="bg-white border-gray-200">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-black">
              <Award className="w-5 h-5 text-orange-600" />
              <span>Top Incident Types</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {stats.top_incident_types.length > 0 ? (
              <div className="space-y-4">
                {stats.top_incident_types.map((incident, index) => {
                  const maxCount = Math.max(...stats.top_incident_types.map(i => i.count))
                  const percentage = (incident.count / maxCount) * 100

                  return (
                    <div key={incident.type} className="space-y-2">
                      <div className="flex justify-between items-center">
                        <div className="flex items-center space-x-2">
                          <span className="text-sm font-medium text-black">
                            #{index + 1}
                          </span>
                          <span className="text-sm text-black">
                            {getIncidentTypeLabel(incident.type)}
                          </span>
                        </div>
                        <span className="text-sm font-bold text-black">
                          {incident.count}
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full transition-all duration-300 ${
                            index === 0 ? 'bg-red-500' :
                            index === 1 ? 'bg-orange-500' :
                            index === 2 ? 'bg-yellow-500' :
                            index === 3 ? 'bg-green-500' :
                            'bg-blue-500'
                          }`}
                          style={{ width: `${percentage}%` }}
                        ></div>
                      </div>
                    </div>
                  )
                })}
              </div>
            ) : (
              <div className="text-center text-gray-500 py-4">
                No incident data available yet
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Community Impact Summary */}
      <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2 text-black">
            <Users className="w-5 h-5 text-blue-600" />
            <span>Community Impact</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">
                {((stats.verified_reports / Math.max(stats.total_reports, 1)) * 100).toFixed(0)}%
              </div>
              <div className="text-sm text-gray-700">
                Reports Successfully Verified
              </div>
            </div>

            <div className="text-center">
              <div className="text-3xl font-bold text-green-600 mb-2">
                {stats.active_incidents}
              </div>
              <div className="text-sm text-gray-700">
                Active Community Alerts
              </div>
            </div>

            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600 mb-2">
                {(stats.total_reports + stats.total_feedback)}
              </div>
              <div className="text-sm text-gray-700">
                Total Community Contributions
              </div>
            </div>
          </div>

          <div className="mt-6 p-4 bg-white rounded-lg border border-blue-200">
            <h4 className="font-semibold text-black mb-2">How to Improve Community Engagement:</h4>
            <ul className="text-sm text-gray-700 space-y-1">
              {stats.response_rate < 80 && (
                <li>• Encourage more detailed incident reports for better verification rates</li>
              )}
              {stats.average_verification_time_hours > 12 && (
                <li>• Consider expanding the verification team to reduce response times</li>
              )}
              {stats.community_engagement_score < 60 && (
                <li>• Promote community participation through awareness campaigns</li>
              )}
              {stats.total_feedback < 10 && (
                <li>• Encourage users to provide feedback about their experience</li>
              )}
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}