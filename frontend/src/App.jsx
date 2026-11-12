import React, { useState } from 'react'
import { Routes, Route } from 'react-router-dom'
import Home from './pages/Home.jsx'
import Dashboard from './pages/Dashboard.jsx'

export default function App() {
  const [profile, setProfile] = useState(null)
  const [jobs, setJobs] = useState([])
  const [resumeFile, setResumeFile] = useState(null)

  return (
    <Routes>
      <Route
        path="/"
        element={
          <Home
            profile={profile}
            setProfile={setProfile}
            jobs={jobs}
            setJobs={setJobs}
            resumeFile={resumeFile}
            setResumeFile={setResumeFile}
          />
        }
      />
      <Route
        path="/dashboard"
        element={
          <Dashboard
            profile={profile}
            jobs={jobs}
            setJobs={setJobs}
          />
        }
      />
    </Routes>
  )
}
