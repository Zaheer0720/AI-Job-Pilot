import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Zap, Filter, SortDesc } from 'lucide-react'
import toast from 'react-hot-toast'
import JobCard from '../components/JobCard.jsx'
import ApplicationStatus from '../components/ApplicationStatus.jsx'
import { applyApi } from '../api/client.js'

export default function Dashboard({ profile, jobs, setJobs }) {
  const navigate = useNavigate()
  const [selectedJobs, setSelectedJobs] = useState([])
  const [applying, setApplying] = useState(false)
  const [results, setResults] = useState([])
  const [autoSubmit, setAutoSubmit] = useState(false)
  const [filterPortal, setFilterPortal] = useState('all')
  const [minScore, setMinScore] = useState(0)

  const portals = ['all', ...new Set(jobs.map(j => j.portal))]

  const filteredJobs = jobs
    .filter(j => filterPortal === 'all' || j.portal === filterPortal)
    .filter(j => j.match_score >= minScore)

  const toggleJob = (jobId) => {
    setSelectedJobs(prev =>
      prev.includes(jobId) ? prev.filter(id => id !== jobId) : [...prev, jobId]
    )
  }

  const handleApply = async () => {
    if (selectedJobs.length === 0) {
      toast.error('Select at least one job to apply')
      return
    }

    if (!profile) {
      toast.error('No profile found. Please upload your resume first.')
      navigate('/')
      return
    }

    if (autoSubmit && !confirm('⚠️ AUTO-SUBMIT is ON. This will actually submit applications. Continue?')) {
      return
    }

    setApplying(true)

    try {
      const jobsToApply = jobs.filter(j => selectedJobs.includes(j.id))

      const { data: started } = await applyApi.start({
        jobs: jobsToApply,
        profile,
        resume_path: profile.resume_path || '',
        headless: true,
        auto_submit: autoSubmit,
      })

      if (!started.resume_attached) {
        toast('No resume file attached - upload your resume again to include it.', { icon: '⚠️' })
      }

      // Poll for progress until the background task finishes
      let applicationResults = []
      for (;;) {
        await new Promise(r => setTimeout(r, 3000))
        const { data: task } = await applyApi.results(started.task_id)
        applicationResults = task.results
        setResults(task.results)
        if (task.done) {
          if (task.error) throw new Error(task.error)
          break
        }
      }

      const applied = applicationResults.filter(r => r.status === 'applied').length
      const filled = applicationResults.filter(r => r.status === 'requires_manual').length
      toast.success(`Done! ${applied} submitted, ${filled} forms filled (review required)`)

    } catch (err) {
      toast.error(err.message)
    } finally {
      setApplying(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Header */}
      <div className="bg-slate-900 border-b border-slate-800 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button onClick={() => navigate('/')} className="btn-secondary text-sm">
              <ArrowLeft size={16} /> Back
            </button>
            <div>
              <h1 className="font-bold text-lg">Job Matches</h1>
              <p className="text-slate-400 text-sm">{filteredJobs.length} jobs found · {selectedJobs.length} selected</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Auto-submit toggle */}
            <label className="flex items-center gap-2 text-sm cursor-pointer">
              <div className={`relative w-10 h-5 rounded-full transition-colors ${autoSubmit ? 'bg-red-600' : 'bg-slate-700'}`}
                onClick={() => setAutoSubmit(p => !p)}>
                <div className={`absolute top-0.5 w-4 h-4 bg-white rounded-full transition-transform ${autoSubmit ? 'translate-x-5' : 'translate-x-0.5'}`} />
              </div>
              <span className={autoSubmit ? 'text-red-400 font-medium' : 'text-slate-400'}>
                {autoSubmit ? '⚠️ Auto-Submit ON' : 'Auto-Submit OFF'}
              </span>
            </label>

            <button
              onClick={handleApply}
              disabled={applying || selectedJobs.length === 0}
              className="btn-primary"
            >
              <Zap size={16} />
              {applying ? 'Applying...' : `Apply to ${selectedJobs.length} Jobs`}
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Application Results */}
        {results.length > 0 && (
          <div className="mb-8">
            <ApplicationStatus results={results} />
          </div>
        )}

        {/* Filters */}
        <div className="flex items-center gap-4 mb-6 flex-wrap">
          <div className="flex items-center gap-2">
            <Filter size={16} className="text-slate-400" />
            <select
              value={filterPortal}
              onChange={(e) => setFilterPortal(e.target.value)}
              className="input-field w-auto text-sm"
            >
              {portals.map(p => (
                <option key={p} value={p}>{p === 'all' ? 'All Portals' : p.charAt(0).toUpperCase() + p.slice(1)}</option>
              ))}
            </select>
          </div>
          <div className="flex items-center gap-2">
            <SortDesc size={16} className="text-slate-400" />
            <span className="text-slate-400 text-sm">Min match:</span>
            <input
              type="range" min="0" max="100" value={minScore}
              onChange={(e) => setMinScore(Number(e.target.value))}
              className="w-24 accent-blue-500"
            />
            <span className="text-sm font-mono text-blue-400">{minScore}%</span>
          </div>
          <button
            onClick={() => setSelectedJobs(filteredJobs.map(j => j.id))}
            className="text-sm text-blue-400 hover:text-blue-300"
          >
            Select All
          </button>
          <button
            onClick={() => setSelectedJobs([])}
            className="text-sm text-slate-400 hover:text-slate-300"
          >
            Clear
          </button>
        </div>

        {/* Job List */}
        {filteredJobs.length === 0 ? (
          <div className="text-center py-20 text-slate-500">
            <p className="text-xl">No jobs found matching your filters.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredJobs.map((job) => (
              <JobCard
                key={job.id}
                job={job}
                selected={selectedJobs.includes(job.id)}
                onToggle={() => toggleJob(job.id)}
                result={results.find(r => r.job_id === job.id)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
