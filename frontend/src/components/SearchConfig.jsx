import React from 'react'
import { Search, Loader2, Globe, Briefcase, MapPin } from 'lucide-react'

const PORTALS = [
  { id: 'linkedin', label: 'LinkedIn', color: 'bg-blue-900/50 border-blue-600' },
  { id: 'indeed', label: 'Indeed', color: 'bg-purple-900/50 border-purple-600' },
  { id: 'glassdoor', label: 'Glassdoor', color: 'bg-green-900/50 border-green-600' },
  { id: 'zip_recruiter', label: 'ZipRecruiter', color: 'bg-orange-900/50 border-orange-600' },
]

const JOB_TYPES = ['fulltime', 'parttime', 'contract', 'internship']

export default function SearchConfig({ config, onChange, onSearch, isSearching }) {
  const togglePortal = (id) => {
    const portals = config.portals.includes(id)
      ? config.portals.filter(p => p !== id)
      : [...config.portals, id]
    onChange({ ...config, portals })
  }

  return (
    <div className="card">
      <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
        <Search className="text-blue-400" size={22} />
        Step 2: Configure Job Search
      </h2>

      <div className="space-y-6">
        {/* Portals */}
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-3 flex items-center gap-2">
            <Globe size={15} /> Job Portals
          </label>
          <div className="flex flex-wrap gap-3">
            {PORTALS.map(portal => (
              <button
                key={portal.id}
                onClick={() => togglePortal(portal.id)}
                className={`px-4 py-2 rounded-xl border text-sm font-medium transition-all ${
                  config.portals.includes(portal.id)
                    ? portal.color + ' text-white'
                    : 'bg-slate-800 border-slate-700 text-slate-400 hover:border-slate-600'
                }`}
              >
                {portal.label}
              </button>
            ))}
          </div>
        </div>

        {/* Location and Type */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2 flex items-center gap-2">
              <MapPin size={15} /> Location (optional)
            </label>
            <input
              type="text"
              placeholder="e.g. Bangalore, India or Remote"
              value={config.location}
              onChange={e => onChange({ ...config, location: e.target.value })}
              className="input-field"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2 flex items-center gap-2">
              <Briefcase size={15} /> Job Type
            </label>
            <select
              value={config.job_type}
              onChange={e => onChange({ ...config, job_type: e.target.value })}
              className="input-field"
            >
              {JOB_TYPES.map(t => (
                <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Options */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Results per portal</label>
            <input
              type="number" min="5" max="50"
              value={config.results_per_portal}
              onChange={e => onChange({ ...config, results_per_portal: Number(e.target.value) })}
              className="input-field"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Min match score: {config.min_match_score}%</label>
            <input
              type="range" min="0" max="100"
              value={config.min_match_score}
              onChange={e => onChange({ ...config, min_match_score: Number(e.target.value) })}
              className="w-full accent-blue-500 mt-3"
            />
          </div>
          <div className="flex items-center gap-3 mt-6">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={config.remote}
                onChange={e => onChange({ ...config, remote: e.target.checked })}
                className="w-4 h-4 accent-blue-500"
              />
              <span className="text-slate-300 text-sm">Remote only</span>
            </label>
          </div>
        </div>

        {/* Search Button */}
        <button
          onClick={onSearch}
          disabled={isSearching || config.portals.length === 0}
          className="btn-primary w-full justify-center py-4 text-base"
        >
          {isSearching ? (
            <><Loader2 className="animate-spin" size={20} /> Searching {config.portals.length} portals & scoring with Gemini...</>
          ) : (
            <><Search size={20} /> Search Jobs Across {config.portals.length} Portals</>
          )}
        </button>
      </div>
    </div>
  )
}
