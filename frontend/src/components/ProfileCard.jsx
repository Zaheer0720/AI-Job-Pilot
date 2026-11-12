import React, { useState } from 'react'
import { User, Mail, Phone, MapPin, Briefcase, GraduationCap, Code2, ChevronDown, ChevronUp } from 'lucide-react'

export default function ProfileCard({ profile }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="card border-blue-800/50">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center text-2xl font-bold">
            {profile.name ? profile.name[0].toUpperCase() : '?'}
          </div>
          <div>
            <h2 className="text-xl font-bold">{profile.name || 'Unknown'}</h2>
            <div className="flex items-center gap-4 text-slate-400 text-sm mt-1 flex-wrap">
              {profile.email && <span className="flex items-center gap-1"><Mail size={13} />{profile.email}</span>}
              {profile.phone && <span className="flex items-center gap-1"><Phone size={13} />{profile.phone}</span>}
              {profile.location && <span className="flex items-center gap-1"><MapPin size={13} />{profile.location}</span>}
            </div>
          </div>
        </div>
        <div className="text-right">
          <div className="text-slate-400 text-sm">Experience</div>
          <div className="text-2xl font-bold text-blue-400">{profile.years_of_experience}y</div>
        </div>
      </div>

      {/* Key titles */}
      {profile.job_titles?.length > 0 && (
        <div className="flex gap-2 flex-wrap mb-4">
          {profile.job_titles.map((title, i) => (
            <span key={i} className="badge bg-blue-900/50 text-blue-300 border border-blue-700/50">{title}</span>
          ))}
        </div>
      )}

      {/* Summary */}
      {profile.summary && (
        <p className="text-slate-400 text-sm mb-4 line-clamp-2">{profile.summary}</p>
      )}

      {/* Skills */}
      {profile.skills?.length > 0 && (
        <div className="mb-4">
          <div className="flex items-center gap-2 text-sm font-medium text-slate-300 mb-2">
            <Code2 size={15} className="text-blue-400" />
            Skills ({profile.skills.length})
          </div>
          <div className="flex flex-wrap gap-1.5">
            {profile.skills.slice(0, expanded ? undefined : 12).map((skill, i) => (
              <span key={i} className="badge bg-slate-800 text-slate-300 border border-slate-700">{skill}</span>
            ))}
            {!expanded && profile.skills.length > 12 && (
              <span className="badge bg-slate-800 text-slate-500">+{profile.skills.length - 12} more</span>
            )}
          </div>
        </div>
      )}

      {/* Expand for more details */}
      {expanded && (
        <div className="space-y-4 border-t border-slate-800 pt-4">
          {/* Experience */}
          {profile.experience?.length > 0 && (
            <div>
              <div className="flex items-center gap-2 text-sm font-medium text-slate-300 mb-2">
                <Briefcase size={15} className="text-blue-400" /> Experience
              </div>
              {profile.experience.map((exp, i) => (
                <div key={i} className="text-sm mb-2 pl-4 border-l border-slate-700">
                  <div className="font-medium text-slate-200">{exp.title} @ {exp.company}</div>
                  <div className="text-slate-500">{exp.duration}</div>
                </div>
              ))}
            </div>
          )}

          {/* Education */}
          {profile.education?.length > 0 && (
            <div>
              <div className="flex items-center gap-2 text-sm font-medium text-slate-300 mb-2">
                <GraduationCap size={15} className="text-blue-400" /> Education
              </div>
              {profile.education.map((edu, i) => (
                <div key={i} className="text-sm mb-2 pl-4 border-l border-slate-700">
                  <div className="font-medium text-slate-200">{edu.degree} in {edu.field}</div>
                  <div className="text-slate-500">{edu.institution} · {edu.year}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      <button
        onClick={() => setExpanded(p => !p)}
        className="mt-4 text-sm text-blue-400 hover:text-blue-300 flex items-center gap-1"
      >
        {expanded ? <><ChevronUp size={15} /> Show less</> : <><ChevronDown size={15} /> Show full profile</>}
      </button>
    </div>
  )
}
