'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  MapPin, 
  Clock, 
  ThumbsUp, 
  ThumbsDown, 
  Users, 
  Eye,
  AlertTriangle,
  CheckCircle,
  Filter
} from 'lucide-react'

interface Incident {
  id: string
  incident_type: string
  severity: string
  title: string
  description: string
  location: {
    latitude: number
    longitude: number
    address?: string
    city: string
    state?: string
    country?: string
  }
  timestamp: string
  verification_status: string
  upvotes: number
  downvotes: number
  affected_people_count?: number
  tags: string[]
  reporter_name?: string
}

export default function CommunityIncidentList() {
  const [incidents, setIncidents] = useState<Incident[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedCity, setSelectedCity] = useState<string>('')
  const [selectedSeverity, setSelectedSeverity] = useState<string>('')
  const [userVotes, setUserVotes] = useState<Record<string, string>>({})

  useEffect(() => {
    fetchIncidents()
  }, [selectedCity])

  const fetchIncidents = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (selectedCity) params.append('city', selectedCity)
      
      const response = await fetch(`/api/community/incidents?${params}`)
      const data = await response.json()
      
      if (response.ok) {
        setIncidents(data.incidents || [])
      } else {
        setError('Failed to load incidents')
      }
    } catch (err) {
      setError('Failed to load incidents')
    } finally {
      setLoading(false)
    }
  }

  const handleVote = async (incidentId: string, voteType: 'upvote' | 'downvote') => {
    try {
      const userId = `user_${Math.random().toString(36).substr(2, 9)}` // Simple user ID generation
      const currentVote = userVotes[incidentId]
      const newVoteType = currentVote === voteType ? 'remove' : voteType
      
      const response = await fetch(
        `/api/community/incidents/${incidentId}/vote?vote_type=${newVoteType}&user_id=${userId}`,
        { method: 'POST' }
      )
      
      const result = await response.json()
      
      if (result.success) {
        // Update the incident in the list
        setIncidents(incidents.map(incident => 
          incident.id === incidentId 
            ? { ...incident, upvotes: result.upvotes, downvotes: result.downvotes }
            : incident
        ))
        
        // Update user vote state
        setUserVotes({
          ...userVotes,
          [incidentId]: newVoteType === 'remove' ? '' : newVoteType
        })
      }
    } catch (err) {
      console.error('Failed to vote:', err)
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'low': return 'bg-green-100 text-green-800 border-green-200'
      case 'moderate': return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-200'
      case 'critical': return 'bg-red-100 text-red-800 border-red-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getIncidentTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      'air_quality_spike': 'Air Quality Spike',
      'industrial_emission': 'Industrial Emission',
      'wildfire_smoke': 'Wildfire Smoke',
      'traffic_pollution': 'Traffic Pollution',
      'construction_dust': 'Construction Dust',
      'chemical_spill': 'Chemical Spill',
      'unusual_odor': 'Unusual Odor',
      'respiratory_irritation': 'Respiratory Issues',
      'other': 'Other'
    }
    return labels[type] || type
  }

  const formatTimeAgo = (timestamp: string) => {
    const now = new Date()
    const incidentTime = new Date(timestamp)
    const diffHours = Math.floor((now.getTime() - incidentTime.getTime()) / (1000 * 60 * 60))
    
    if (diffHours < 1) return 'Less than 1 hour ago'
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
    
    const diffDays = Math.floor(diffHours / 24)
    return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
  }

  const filteredIncidents = incidents.filter(incident => {
    if (selectedSeverity && incident.severity !== selectedSeverity) return false
    return true
  })

  const uniqueCities = Array.from(new Set(incidents.map(i => i.location.city))).sort()
  const severityOptions = ['low', 'moderate', 'high', 'critical']

  if (loading) {
    return (
      <Card className="bg-white border-gray-200">
        <CardContent className="p-6">
          <div className="flex items-center justify-center">
            <div className="text-gray-600">Loading community incidents...</div>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Alert className="border-red-200 bg-red-50">
        <AlertTriangle className="h-4 w-4 text-red-600" />
        <AlertDescription className="text-red-800">{error}</AlertDescription>
      </Alert>
    )
  }

  return (
    <div className="space-y-4">
      {/* Filters */}
      <Card className="bg-white border-gray-200">
        <CardContent className="p-4">
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center space-x-2">
              <Filter className="w-4 h-4 text-gray-500" />
              <span className="text-sm font-medium text-black">Filter by:</span>
            </div>
            
            <select
              value={selectedCity}
              onChange={(e) => setSelectedCity(e.target.value)}
              className="px-3 py-1 border border-gray-300 rounded text-sm text-black bg-white"
            >
              <option value="">All Cities</option>
              {uniqueCities.map(city => (
                <option key={city} value={city}>{city}</option>
              ))}
            </select>
            
            <select
              value={selectedSeverity}
              onChange={(e) => setSelectedSeverity(e.target.value)}
              className="px-3 py-1 border border-gray-300 rounded text-sm text-black bg-white"
            >
              <option value="">All Severities</option>
              {severityOptions.map(severity => (
                <option key={severity} value={severity}>
                  {severity.charAt(0).toUpperCase() + severity.slice(1)}
                </option>
              ))}
            </select>
            
            <div className="text-sm text-gray-600">
              Showing {filteredIncidents.length} of {incidents.length} incidents
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Incidents List */}
      {filteredIncidents.length === 0 ? (
        <Card className="bg-white border-gray-200">
          <CardContent className="p-6 text-center">
            <div className="text-gray-600">
              {selectedCity || selectedSeverity 
                ? 'No incidents match your filter criteria.' 
                : 'No verified incidents reported yet.'}
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {filteredIncidents.map((incident) => (
            <Card key={incident.id} className="bg-white border-gray-200 hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <Badge className={getSeverityColor(incident.severity)}>
                        {incident.severity.toUpperCase()}
                      </Badge>
                      <Badge variant="outline" className="text-gray-600">
                        {getIncidentTypeLabel(incident.incident_type)}
                      </Badge>
                      <div className="flex items-center text-green-600 text-sm">
                        <CheckCircle className="w-4 h-4 mr-1" />
                        Verified
                      </div>
                    </div>
                    
                    <h3 className="text-lg font-semibold text-black mb-2">
                      {incident.title}
                    </h3>
                    
                    <p className="text-gray-700 mb-3 line-clamp-2">
                      {incident.description}
                    </p>
                    
                    <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600">
                      <div className="flex items-center space-x-1">
                        <MapPin className="w-4 h-4" />
                        <span>
                          {incident.location.city}
                          {incident.location.state && `, ${incident.location.state}`}
                        </span>
                      </div>
                      
                      <div className="flex items-center space-x-1">
                        <Clock className="w-4 h-4" />
                        <span>{formatTimeAgo(incident.timestamp)}</span>
                      </div>
                      
                      {incident.affected_people_count && (
                        <div className="flex items-center space-x-1">
                          <Users className="w-4 h-4" />
                          <span>{incident.affected_people_count} affected</span>
                        </div>
                      )}
                      
                      {incident.reporter_name && (
                        <div className="flex items-center space-x-1">
                          <Eye className="w-4 h-4" />
                          <span>Reported by {incident.reporter_name}</span>
                        </div>
                      )}
                    </div>
                    
                    {incident.tags.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-3">
                        {incident.tags.map((tag, index) => (
                          <Badge key={index} variant="outline" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
                
                {/* Voting */}
                <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                  <div className="flex items-center space-x-4">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleVote(incident.id, 'upvote')}
                      className={`flex items-center space-x-1 ${
                        userVotes[incident.id] === 'upvote' 
                          ? 'text-green-600 bg-green-50' 
                          : 'text-gray-600 hover:text-green-600'
                      }`}
                    >
                      <ThumbsUp className="w-4 h-4" />
                      <span>{incident.upvotes}</span>
                    </Button>
                    
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleVote(incident.id, 'downvote')}
                      className={`flex items-center space-x-1 ${
                        userVotes[incident.id] === 'downvote' 
                          ? 'text-red-600 bg-red-50' 
                          : 'text-gray-600 hover:text-red-600'
                      }`}
                    >
                      <ThumbsDown className="w-4 h-4" />
                      <span>{incident.downvotes}</span>
                    </Button>
                  </div>
                  
                  <Button
                    variant="outline"
                    size="sm"
                    className="text-blue-600 hover:bg-blue-50"
                  >
                    View Details
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}