import React, { useState } from 'react'
import { ExternalLink, MapPin, Building2, Clock, ChevronDown, ChevronUp, Zap, CheckCircle, XCircle, AlertCircle } from 'lucide-react'
import clsx from 'clsx'

const PORTAL_COLORS = {
  linkedin: 'bg-blue-900/40 text-blue-300 border-blue-700/50',
  indeed: 'bg-purple-900/40 text-purple-300 border-purple-700/50',
  glassdoor: 'bg-green-900/40 text-green-300 border-green-700/50',
  zip_recruiter: 'bg-orange-900/40 text-orange-300 border-orange-700/50',
  unknown: 'bg-slate-800 text-slate-400 border-slate-700',
}

function ScoreBadge({ score }) {
  const color = score >= 80 ? 'text-green-400' : score >= 60 ? 'text-yellow-400' : 'text-red-400'
  const bg = score >= 80 ? 'bg-green-950 border-green-700/50' : score >= 60 ? 'bg-yellow-950 border-yellow-700/50' : 'bg-red-950 border-red-700/50'
  return (
    <div className={clsx('border rounded-xl px-3 py-1 text-center min-w-[64px]', bg)}>
      <div className={clsx('text-xl font-bold', color)}>{Math.round(score)}%</div>
      <div className="text-xs text-slate-500">match</div>
    </div>
  )
}

function StatusBadge({ status }) {
  const configs = {
    applied: { icon: CheckCircle, color: 'text-green-400', label: 'Applied' },
    requires_manual: { icon: AlertCircle, color: 'text-yellow-400', label: 'Review Required' },
    failed: { icon: XCircle, color: 'text-red-400', label: 'Failed' },
    pending: { icon: Clock, color: 'text-slate-400', label: 'Pending' },
  }
  const { icon: Icon, color, label } = configs[status] || configs.pending
  return (
    <span className={clsx('flex items-center gap-1 text-xs font-medium', color)}>
      <Icon size={13} /> {label}
    </span>
  )
}

export default function JobCard({ job, selected, onToggle, result }) {
  const [expanded, setExpanded] = useState(false)
  const portalColor = PORTAL_COLORS[job.portal] || PORTAL_COLORS.unknown

  return (
    <div
      className={clsx(
        'card cursor-pointer transition-all duration-200 border',
        selected ? 'border-blue-500 bg-blue-950/10' : 'border-slate-800 hover:border-slate-700',
      )}
      onClick={onToggle}
    >
      <div className="flex items-start gap-4">
        {/* Checkbox */}
        <div className={clsx(
          'mt-1 w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0 transition-all',
          selected ? 'bg-blue-600 border-blue-600' : 'border-slate-600'
        )}>
          {selected && <div className="w-2.5 h-2.5 rounded-sm bg-white" />}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <div className="flex items-center gap-2 flex-wrap mb-1">
                <h3 className="font-semibold text-slate-100 text-lg leading-tight">{job.title}</h3>
                {job.easy_apply && (
                  <span className="badge bg-blue-900/50 text-blue-300 border border-blue-700/50">
                    <Zap size={11} className="mr-1" /> Easy Apply
                  </span>
                )}
              </div>

              <div className="flex items-center gap-4 text-sm text-slate-400 flex-wrap">
                <span className="flex items-center gap-1"><Building2 size={13} />{job.company}</span>
                {job.location && <span className="flex items-center gap-1"><MapPin size={13} />{job.location}</span>}
                {job.salary && job.salary !== 'None - None' && (
                  <span className="text-green-400 font-medium">{job.salary}</span>
                )}
                {job.posted_date && <span className="flex items-center gap-1"><Clock size={13} />{job.posted_date}</span>}
              </div>

              {/* Portal badge */}
              <div className="flex items-center gap-2 mt-2 flex-wrap">
                <span className={clsx('badge border', portalColor)}>
                  {job.portal}
                </span>
                {job.job_type && (
                  <span className="badge bg-slate-800 text-slate-400 border border-slate-700">{job.job_type}</span>
                )}
                {result && <StatusBadge status={result.status} />}
              </div>
            </div>

            <div className="flex flex-col items-end gap-2 flex-shrink-0">
              <ScoreBadge score={job.match_score} />
              <a
                href={job.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-400 hover:text-blue-300 p-1"
                onClick={e => e.stopPropagation()}
              >
                <ExternalLink size={16} />
              </a>
            </div>
          </div>

          {/* Match reasons */}
          {job.match_reasons?.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-1.5">
              {job.match_reasons.map((reason, i) => (
                <span key={i} className="text-xs bg-slate-800/80 text-slate-400 rounded-lg px-2 py-0.5 border border-slate-700">
                  ✓ {reason}
                </span>
              ))}
            </div>
          )}

          {/* Result message */}
          {result?.message && (
            <div className={clsx(
              'mt-3 text-xs p-2 rounded-lg border',
              result.status === 'applied' ? 'bg-green-950/30 border-green-700/50 text-green-300' :
              result.status === 'failed' ? 'bg-red-950/30 border-red-700/50 text-red-300' :
              'bg-yellow-950/30 border-yellow-700/50 text-yellow-300'
            )}>
              {result.message}
            </div>
          )}

          {/* Description expand */}
          {job.description && (
            <>
              <button
                onClick={(e) => { e.stopPropagation(); setExpanded(p => !p) }}
                className="mt-3 text-xs text-slate-500 hover:text-slate-300 flex items-center gap-1"
              >
                {expanded ? <><ChevronUp size={13} /> Hide description</> : <><ChevronDown size={13} /> View job description</>}
              </button>
              {expanded && (
                <div className="mt-2 text-sm text-slate-400 bg-slate-800/50 rounded-lg p-3 max-h-48 overflow-y-auto border border-slate-700 whitespace-pre-wrap">
                  {job.description}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}
