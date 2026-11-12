import React from 'react'
import { CheckCircle, XCircle, AlertCircle, ExternalLink } from 'lucide-react'

export default function ApplicationStatus({ results }) {
  const applied = results.filter(r => r.status === 'applied')
  const manual = results.filter(r => r.status === 'requires_manual')
  const failed = results.filter(r => r.status === 'failed')

  return (
    <div className="card border-slate-700">
      <h3 className="font-bold text-lg mb-4">Application Results</h3>

      {/* Summary */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-green-950/30 border border-green-700/50 rounded-xl p-4 text-center">
          <CheckCircle className="text-green-400 mx-auto mb-1" size={24} />
          <div className="text-2xl font-bold text-green-400">{applied.length}</div>
          <div className="text-xs text-slate-400">Submitted</div>
        </div>
        <div className="bg-yellow-950/30 border border-yellow-700/50 rounded-xl p-4 text-center">
          <AlertCircle className="text-yellow-400 mx-auto mb-1" size={24} />
          <div className="text-2xl font-bold text-yellow-400">{manual.length}</div>
          <div className="text-xs text-slate-400">Review Required</div>
        </div>
        <div className="bg-red-950/30 border border-red-700/50 rounded-xl p-4 text-center">
          <XCircle className="text-red-400 mx-auto mb-1" size={24} />
          <div className="text-2xl font-bold text-red-400">{failed.length}</div>
          <div className="text-xs text-slate-400">Failed</div>
        </div>
      </div>

      {/* Detailed results */}
      <div className="space-y-2 max-h-64 overflow-y-auto">
        {results.map((result) => (
          <div key={result.job_id} className="flex items-start gap-3 p-3 rounded-lg bg-slate-800/50 border border-slate-700">
            {result.status === 'applied' && <CheckCircle className="text-green-400 flex-shrink-0 mt-0.5" size={16} />}
            {result.status === 'requires_manual' && <AlertCircle className="text-yellow-400 flex-shrink-0 mt-0.5" size={16} />}
            {result.status === 'failed' && <XCircle className="text-red-400 flex-shrink-0 mt-0.5" size={16} />}

            <div className="flex-1 min-w-0">
              <div className="font-medium text-sm text-slate-200">{result.job_title}</div>
              <div className="text-xs text-slate-500">{result.company} · {result.portal}</div>
              {result.message && (
                <div className="text-xs text-slate-400 mt-1">{result.message}</div>
              )}
            </div>

            <a
              href={result.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-400 hover:text-blue-300 flex-shrink-0"
            >
              <ExternalLink size={14} />
            </a>
          </div>
        ))}
      </div>
    </div>
  )
}
