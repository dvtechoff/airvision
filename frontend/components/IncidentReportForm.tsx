'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { CheckCircle, AlertCircle, MapPin } from 'lucide-react'

interface IncidentReportFormProps {
  onSubmissionSuccess?: () => void
}

export default function IncidentReportForm({ onSubmissionSuccess }: IncidentReportFormProps) {
  const [formData, setFormData] = useState({
    incident_type: 'air_quality_spike',
    severity: 'moderate',
    title: '',
    description: '',
    location: {
      latitude: 0,
      longitude: 0,
      address: '',
      city: '',
      state: '',
      country: 'USA'
    },
    reporter_name: '',
    reporter_email: '',
    reporter_phone: '',
    affected_people_count: '',
    environmental_impact: '',
    tags: ''
  })
  const [submitting, setSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [locationError, setLocationError] = useState<string | null>(null)

  const incidentTypes = [
    { value: 'air_quality_spike', label: 'Air Quality Spike' },
    { value: 'industrial_emission', label: 'Industrial Emission' },
    { value: 'wildfire_smoke', label: 'Wildfire Smoke' },
    { value: 'traffic_pollution', label: 'Traffic Pollution' },
    { value: 'construction_dust', label: 'Construction Dust' },
    { value: 'chemical_spill', label: 'Chemical Spill' },
    { value: 'unusual_odor', label: 'Unusual Odor' },
    { value: 'respiratory_irritation', label: 'Respiratory Irritation' },
    { value: 'other', label: 'Other' }
  ]

  const severityLevels = [
    { value: 'low', label: 'Low', color: 'text-green-600' },
    { value: 'moderate', label: 'Moderate', color: 'text-yellow-600' },
    { value: 'high', label: 'High', color: 'text-orange-600' },
    { value: 'critical', label: 'Critical', color: 'text-red-600' }
  ]

  const getCurrentLocation = () => {
    setLocationError(null)
    
    if (!navigator.geolocation) {
      setLocationError('Geolocation is not supported by this browser')
      return
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setFormData({
          ...formData,
          location: {
            ...formData.location,
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          }
        })
      },
      (error) => {
        setLocationError('Unable to get your location. Please enter it manually.')
      }
    )
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    setError(null)

    // Prepare data for submission
    const submitData = {
      ...formData,
      affected_people_count: formData.affected_people_count ? parseInt(formData.affected_people_count) : null,
      tags: formData.tags ? formData.tags.split(',').map(tag => tag.trim()) : []
    }

    try {
      const response = await fetch('/api/community/incidents', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(submitData)
      })

      const result = await response.json()

      if (response.ok && result.success) {
        setSubmitted(true)
        // Reset form
        setFormData({
          incident_type: 'air_quality_spike',
          severity: 'moderate',
          title: '',
          description: '',
          location: {
            latitude: 0,
            longitude: 0,
            address: '',
            city: '',
            state: '',
            country: 'USA'
          },
          reporter_name: '',
          reporter_email: '',
          reporter_phone: '',
          affected_people_count: '',
          environmental_impact: '',
          tags: ''
        })
        onSubmissionSuccess?.()
      } else {
        setError(result.message || 'Failed to submit incident report')
      }
    } catch (err) {
      setError('Failed to submit incident report. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    
    if (name.startsWith('location.')) {
      const locationField = name.split('.')[1]
      setFormData({
        ...formData,
        location: {
          ...formData.location,
          [locationField]: locationField === 'latitude' || locationField === 'longitude' ? parseFloat(value) : value
        }
      })
    } else {
      setFormData({
        ...formData,
        [name]: value
      })
    }
  }

  if (submitted) {
    return (
      <Card className="bg-white border-gray-200">
        <CardContent className="p-6">
          <Alert className="border-green-200 bg-green-50">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-800">
              <div className="space-y-2">
                <p>Thank you for reporting this incident! Your report has been submitted for verification.</p>
                <p className="text-sm">
                  • Reports are typically reviewed within 2-6 hours<br/>
                  • Verified incidents will be visible to the community<br/>
                  • Critical incidents may generate immediate alerts
                </p>
              </div>
            </AlertDescription>
          </Alert>
          <Button
            onClick={() => setSubmitted(false)}
            className="mt-4 bg-blue-600 hover:bg-blue-700 text-white"
          >
            Report Another Incident
          </Button>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="bg-white border-gray-200">
      <CardHeader>
        <CardTitle className="text-black">Report Air Quality Incident</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <Alert className="border-red-200 bg-red-50">
              <AlertCircle className="h-4 w-4 text-red-600" />
              <AlertDescription className="text-red-800">{error}</AlertDescription>
            </Alert>
          )}

          {/* Incident Type and Severity */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-black mb-1">
                Incident Type *
              </label>
              <select
                name="incident_type"
                value={formData.incident_type}
                onChange={handleChange}
                required
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black bg-white"
              >
                {incidentTypes.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-black mb-1">
                Severity Level *
              </label>
              <select
                name="severity"
                value={formData.severity}
                onChange={handleChange}
                required
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black bg-white"
              >
                {severityLevels.map((level) => (
                  <option key={level.value} value={level.value}>
                    {level.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Title and Description */}
          <div>
            <label className="block text-sm font-medium text-black mb-1">
              Incident Title *
            </label>
            <input
              type="text"
              name="title"
              value={formData.title}
              onChange={handleChange}
              required
              maxLength={200}
              placeholder="Brief, descriptive title for the incident"
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black bg-white"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-black mb-1">
              Detailed Description *
            </label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              required
              maxLength={2000}
              rows={5}
              placeholder="Provide detailed information about what you observed, when it occurred, and any other relevant details..."
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black bg-white resize-vertical"
            />
            <div className="text-right text-sm text-gray-500 mt-1">
              {formData.description.length}/2000 characters
            </div>
          </div>

          {/* Location Section */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="text-lg font-medium text-black">Location Information</h4>
              <Button
                type="button"
                onClick={getCurrentLocation}
                variant="outline"
                size="sm"
                className="flex items-center space-x-2"
              >
                <MapPin className="w-4 h-4" />
                <span>Use Current Location</span>
              </Button>
            </div>

            {locationError && (
              <Alert className="border-yellow-200 bg-yellow-50">
                <AlertCircle className="h-4 w-4 text-yellow-600" />
                <AlertDescription className="text-yellow-800">{locationError}</AlertDescription>
              </Alert>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-black mb-1">
                  City *
                </label>
                <input
                  type="text"
                  name="location.city"
                  value={formData.location.city}
                  onChange={handleChange}
                  required
                  placeholder="City name"
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black bg-white"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-black mb-1">
                  State/Province
                </label>
                <input
                  type="text"
                  name="location.state"
                  value={formData.location.state}
                  onChange={handleChange}
                  placeholder="State or province"
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black bg-white"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-black mb-1">
                Street Address (Optional)
              </label>
              <input
                type="text"
                name="location.address"
                value={formData.location.address}
                onChange={handleChange}
                placeholder="Street address or landmarks"
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black bg-white"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-black mb-1">
                  Latitude
                </label>
                <input
                  type="number"
                  step="any"
                  name="location.latitude"
                  value={formData.location.latitude || ''}
                  onChange={handleChange}
                  placeholder="0.000000"
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black bg-white"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-black mb-1">
                  Longitude
                </label>
                <input
                  type="number"
                  step="any"
                  name="location.longitude"
                  value={formData.location.longitude || ''}
                  onChange={handleChange}
                  placeholder="0.000000"
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black bg-white"
                />
              </div>
            </div>
          </div>

          {/* Additional Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-black mb-1">
                Affected People (Estimate)
              </label>
              <input
                type="number"
                name="affected_people_count"
                value={formData.affected_people_count}
                onChange={handleChange}
                min="0"
                placeholder="Number of people affected"
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black bg-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-black mb-1">
                Tags (Optional)
              </label>
              <input
                type="text"
                name="tags"
                value={formData.tags}
                onChange={handleChange}
                placeholder="emergency, industrial, health, etc."
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black bg-white"
              />
              <div className="text-sm text-gray-500 mt-1">
                Separate tags with commas
              </div>
            </div>
          </div>

          {/* Contact Information */}
          <div className="space-y-4">
            <h4 className="text-lg font-medium text-black">Contact Information (Optional)</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-black mb-1">
                  Your Name
                </label>
                <input
                  type="text"
                  name="reporter_name"
                  value={formData.reporter_name}
                  onChange={handleChange}
                  placeholder="Your name"
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black bg-white"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-black mb-1">
                  Email
                </label>
                <input
                  type="email"
                  name="reporter_email"
                  value={formData.reporter_email}
                  onChange={handleChange}
                  placeholder="your.email@example.com"
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black bg-white"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-black mb-1">
                  Phone
                </label>
                <input
                  type="tel"
                  name="reporter_phone"
                  value={formData.reporter_phone}
                  onChange={handleChange}
                  placeholder="(555) 123-4567"
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black bg-white"
                />
              </div>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-black mb-1">
              Environmental Impact (Optional)
            </label>
            <textarea
              name="environmental_impact"
              value={formData.environmental_impact}
              onChange={handleChange}
              rows={3}
              placeholder="Describe any environmental impacts you've observed..."
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black bg-white resize-vertical"
            />
          </div>

          <div className="flex justify-end">
            <Button
              type="submit"
              disabled={submitting}
              className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-2"
            >
              {submitting ? 'Submitting Report...' : 'Submit Incident Report'}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}