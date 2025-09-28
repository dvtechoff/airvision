"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import AlertBox from './AlertBox';
import { Brain, Heart, Activity, Home, Car, Clock, User, Sparkles } from 'lucide-react';

interface Suggestions {
  immediate_health: string[];
  outdoor_activity: string[];
  indoor_tips: string[];
  vulnerable_groups: string[];
  commute_travel: string[];
  long_term: string[];
  general_advice: string[];
}

interface ForecastSummary {
  current_aqi: number;
  range: { min: number; max: number };
  average: number;
  overall_quality: string;
  peak_pollution_times: string[];
  hours_forecasted: number;
}

interface AISuggestionsProps {
  city: string;
  userProfile?: {
    age_group?: string;
    health_conditions?: string[];
    activity_level?: string;
  };
  className?: string;
}

export const AISuggestions: React.FC<AISuggestionsProps> = ({ 
  city, 
  userProfile,
  className = ""
}) => {
  const [suggestions, setSuggestions] = useState<Suggestions | null>(null);
  const [forecastSummary, setForecastSummary] = useState<ForecastSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [confidence, setConfidence] = useState<string>('');
  const [source, setSource] = useState<string>('');
  const [showPersonalized, setShowPersonalized] = useState(false);

  const fetchAISuggestions = async () => {
    if (!city) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      let url = `${API_BASE_URL}/api/ai-suggestions?city=${encodeURIComponent(city)}`;
      
      if (userProfile) {
        const profileParam = encodeURIComponent(JSON.stringify(userProfile));
        url += `&user_profile=${profileParam}`;
      }
      
      console.log('Fetching AI suggestions from:', url);
      const response = await fetch(url);
      console.log('Response status:', response.status);
      
      const data = await response.json();
      console.log('Response data:', data);
      
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to fetch AI suggestions');
      }
      
      setSuggestions(data.suggestions);
      setForecastSummary(data.forecast_summary);
      setConfidence(data.confidence);
      setSource(data.source);
      
    } catch (err: any) {
      console.error('Error fetching AI suggestions:', err);
      setError(err.message || 'Failed to load AI suggestions');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAISuggestions();
  }, [city, userProfile]);

  const getAQIColor = (aqi: number) => {
    if (aqi <= 50) return 'bg-green-500';
    if (aqi <= 100) return 'bg-yellow-500';
    if (aqi <= 150) return 'bg-orange-500';
    if (aqi <= 200) return 'bg-red-500';
    if (aqi <= 300) return 'bg-purple-500';
    return 'bg-red-800';
  };

  const getSuggestionIcon = (category: string) => {
    switch (category) {
      case 'immediate_health': return <Heart className="w-4 h-4" />;
      case 'outdoor_activity': return <Activity className="w-4 h-4" />;
      case 'indoor_tips': return <Home className="w-4 h-4" />;
      case 'vulnerable_groups': return <User className="w-4 h-4" />;
      case 'commute_travel': return <Car className="w-4 h-4" />;
      case 'long_term': return <Clock className="w-4 h-4" />;
      default: return <Sparkles className="w-4 h-4" />;
    }
  };

  const getCategoryTitle = (category: string) => {
    switch (category) {
      case 'immediate_health': return 'Immediate Health Advice';
      case 'outdoor_activity': return 'Outdoor Activity Guidance';
      case 'indoor_tips': return 'Indoor Air Quality Tips';
      case 'vulnerable_groups': return 'Vulnerable Groups Advice';
      case 'commute_travel': return 'Commute & Travel Tips';
      case 'long_term': return 'Long-term Strategies';
      case 'general_advice': return 'General Recommendations';
      default: return 'Suggestions';
    }
  };

  if (loading) {
    return (
      <div className={`${className} animate-pulse`}>
        <Card className="bg-white border-gray-200 shadow-sm">
          <CardHeader className="flex flex-row items-center space-y-0 pb-2">
            <Brain className="w-5 h-5 mr-2 text-blue-600" />
            <CardTitle className="text-lg text-black">AI-Powered Suggestions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-4 bg-gray-200 rounded animate-pulse"></div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className={className}>
        <AlertBox 
          type="error" 
          title="AI Suggestions Error"
          description={error}
        />
        <Button 
          onClick={fetchAISuggestions} 
          className="mt-2 w-full bg-white text-black border-gray-300 hover:bg-gray-100"
          variant="outline"
        >
          Retry AI Suggestions
        </Button>
      </div>
    );
  }

  if (!suggestions || !forecastSummary) {
    return null;
  }

  const hasAnySuggestions = Object.values(suggestions).some(arr => arr.length > 0);

  if (!hasAnySuggestions) {
    return (
      <div className={className}>
        <AlertBox 
          type="info" 
          title="No Suggestions Available"
          description="No specific AI suggestions available at this time. Check back later for personalized recommendations."
        />
      </div>
    );
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Header with forecast summary */}
      <Card className="bg-white border-gray-200 shadow-sm">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <Brain className="w-5 h-5 mr-2 text-blue-600" />
              <CardTitle className="text-lg text-black">AI-Powered Health & Activity Guidance</CardTitle>
            </div>
            <Badge variant="outline" className="text-xs bg-white text-black border-gray-300">
              {confidence === 'high' ? '🎯' : confidence === 'medium' ? '📊' : '⚡'} {confidence} confidence
            </Badge>
          </div>
          
          <div className="flex flex-wrap items-center gap-2 text-sm text-gray-600">
            <span className="text-black">Current AQI:</span>
            <Badge className={`text-white ${getAQIColor(forecastSummary.current_aqi)}`}>
              {forecastSummary.current_aqi}
            </Badge>
            <span className="text-black">•</span>
            <span className="text-black">Range: {forecastSummary.range.min}-{forecastSummary.range.max}</span>
            <span className="text-black">•</span>
            <span className="font-medium text-black">{forecastSummary.overall_quality}</span>
          </div>

          {forecastSummary.peak_pollution_times.length > 0 && (
            <div className="flex items-center gap-2 text-sm">
              <Clock className="w-4 h-4 text-orange-500" />
              <span className="text-black">Peak pollution: {forecastSummary.peak_pollution_times.join(', ')}</span>
            </div>
          )}
        </CardHeader>
      </Card>

      {/* Personalized toggle */}
      {userProfile && (
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-black">Personalized for your profile</span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowPersonalized(!showPersonalized)}
            className="bg-white text-black border-gray-300 hover:bg-gray-100"
          >
            {showPersonalized ? 'Hide' : 'Show'} Profile Details
          </Button>
        </div>
      )}

      {showPersonalized && userProfile && (
        <Card className="bg-white border-gray-200 shadow-sm">
          <CardContent className="pt-4">
            <div className="flex flex-wrap gap-2">
              <Badge variant="secondary" className="bg-gray-100 text-black">Age: {userProfile.age_group}</Badge>
              <Badge variant="secondary" className="bg-gray-100 text-black">Activity: {userProfile.activity_level}</Badge>
              {userProfile.health_conditions && userProfile.health_conditions.length > 0 && (
                <>
                  {userProfile.health_conditions.map((condition, idx) => (
                    <Badge key={idx} variant="outline" className="bg-white text-black border-gray-300">{condition}</Badge>
                  ))}
                </>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Suggestion categories */}
      <div className="grid gap-4 md:grid-cols-2">
        {Object.entries(suggestions).map(([category, items]) => {
          if (!items || items.length === 0) return null;
          
          return (
            <Card key={category} className="h-fit bg-white border-gray-200 shadow-sm">
              <CardHeader className="pb-3">
                <div className="flex items-center">
                  {getSuggestionIcon(category)}
                  <CardTitle className="text-sm font-medium ml-2 text-black">
                    {getCategoryTitle(category)}
                  </CardTitle>
                </div>
              </CardHeader>
              <CardContent className="space-y-2">
                {items.map((suggestion: string, idx: number) => (
                  <div 
                    key={idx} 
                    className="flex items-start p-2 bg-gray-50 rounded-md text-sm"
                  >
                    <span className="inline-block w-2 h-2 bg-blue-500 rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
                    <span className="text-black">{suggestion}</span>
                  </div>
                ))}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Source attribution */}
      <div className="text-xs text-gray-500 text-center">
        <span>Powered by {source} • Updated: {new Date().toLocaleTimeString()}</span>
      </div>
    </div>
  );
};

export default AISuggestions;