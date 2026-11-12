import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Bot, Zap, Search, FileText } from 'lucide-react'
import toast from 'react-hot-toast'
import ResumeUpload from '../components/ResumeUpload.jsx'
import SearchConfig from '../components/SearchConfig.jsx'
import ProfileCard from '../components/ProfileCard.jsx'
import { resumeApi, jobsApi } from '../api/client.js'

export default function Home({ profile, setProfile, setJobs, resumeFile, setResumeFile }) {
  const navigate = useNavigate()
  const [step, setStep] = useState(1) // 1: upload, 2: search config, 3: searching
  const [isUploading, setIsUploading] = useState(false)
  const [isSearching, setIsSearching] = useState(false)
  const [searchConfig, setSearchConfig] = useState({
    portals: ['linkedin', 'indeed', 'glassdoor', 'zip_recruiter'],
    location: '',
    job_type: 'fulltime',
    remote: false,
    results_per_portal: 20,
    min_match_score: 60,
  })

  const handleFileUpload = async (file) => {
    setIsUploading(true)
    setResumeFile(file)
    const formData = new FormData()
    formData.append('file', file)

    try {
      const { data } = await resumeApi.upload(formData)
      setProfile(data)
      setStep(2)
      toast.success(`Resume parsed! Found ${data.skills.length} skills.`)
    } catch (err) {
      toast.error(err.message)
    } finally {
      setIsUploading(false)
    }
  }

  const handleSearch = async () => {
    if (!profile) return
    setIsSearching(true)
    setStep(3)

    try {
      // POST: { profile, search_config: { portals, location, ... } }
      const response = await fetch('/jobs/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          profile,
          search_config: {
            portals: searchConfig.portals,
            location: searchConfig.location,
            job_type: searchConfig.job_type,
            remote: searchConfig.remote,
            results_per_portal: searchConfig.results_per_portal,
            min_match_score: searchConfig.min_match_score,
          },
        }),
      })

      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.detail || 'Search failed')
      }

      const jobs = await response.json()
      setJobs(jobs)
      toast.success(`Found ${jobs.length} matching jobs!`)
      navigate('/dashboard')
    } catch (err) {
      toast.error(err.message)
      setStep(2)
    } finally {
      setIsSearching(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Hero Header */}
      <div className="bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 border-b border-slate-800">
        <div className="max-w-5xl mx-auto px-6 py-16 text-center">
          <div className="inline-flex items-center gap-2 bg-blue-900/40 border border-blue-700/50 rounded-full px-4 py-1.5 mb-6 text-blue-300 text-sm">
            <Bot size={16} />
            Powered by Google Gemini AI
          </div>
          <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-white via-blue-200 to-blue-400 bg-clip-text text-transparent">
            AI Job Hunter
          </h1>
          <p className="text-slate-400 text-xl max-w-2xl mx-auto">
            Upload your resume → AI analyzes it → Searches LinkedIn, Indeed, Glassdoor → Scores matches → Auto-applies for you
          </p>

          {/* Steps */}
          <div className="flex items-center justify-center gap-2 mt-10">
            {[
              { n: 1, label: 'Upload Resume', icon: FileText },
              { n: 2, label: 'Configure Search', icon: Search },
              { n: 3, label: 'Find & Apply', icon: Zap },
            ].map(({ n, label, icon: Icon }, i) => (
              <React.Fragment key={n}>
                <div className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all ${
                  step >= n ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-500'
                }`}>
                  <Icon size={15} />
                  {label}
                </div>
                {i < 2 && <div className={`h-px w-8 ${step > n ? 'bg-blue-600' : 'bg-slate-700'}`} />}
              </React.Fragment>
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 py-12 space-y-8">
        {/* Step 1: Resume Upload */}
        <ResumeUpload
          onUpload={handleFileUpload}
          isLoading={isUploading}
          isComplete={!!profile}
        />

        {/* Parsed Profile Preview */}
        {profile && <ProfileCard profile={profile} />}

        {/* Step 2: Search Config */}
        {profile && step >= 2 && (
          <SearchConfig
            config={searchConfig}
            onChange={setSearchConfig}
            onSearch={handleSearch}
            isSearching={isSearching}
          />
        )}
      </div>
    </div>
  )
}
