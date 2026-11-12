import axios from 'axios'

const api = axios.create({
  baseURL: '',
  timeout: 120000, // 2 min for AI operations
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'An error occurred'
    return Promise.reject(new Error(message))
  }
)

export const resumeApi = {
  upload: (formData) => api.post('/resume/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 60000,
  }),
  parseText: (text) => api.post('/resume/parse-text', { text }),
}

export const jobsApi = {
  searchWithBody: (body) => api.post('/jobs/search', body, { timeout: 180000 }),
}

export const applyApi = {
  start: (data) => api.post('/apply/start', data),
  results: (taskId) => api.get(`/apply/results/${taskId}`),
  generateCoverLetter: (data) => api.post('/apply/cover-letter', data),
}

export default api
