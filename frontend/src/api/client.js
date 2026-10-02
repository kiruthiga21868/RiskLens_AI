import axios from 'axios'

// Use the Vite proxy locally and the deployed API when the frontend is hosted
// separately (for example, on Vercel).
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
})

// Attach the JWT on every request if present.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// On 401, clear tokens and bounce to login.
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401 && !err.config?.url?.includes('/auth/')) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
    }
    return Promise.reject(err)
  },
)

export default api