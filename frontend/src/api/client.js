import axios from 'axios'

// Use the Vite proxy locally. Render supplies the backend hostname through
// VITE_API_HOST so generated service URLs do not need to be hard-coded.
const configuredApiUrl = import.meta.env.VITE_API_URL
  || (import.meta.env.VITE_API_HOST ? `https://${import.meta.env.VITE_API_HOST}/api/v1` : '/api/v1')

const api = axios.create({
  baseURL: configuredApiUrl,
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