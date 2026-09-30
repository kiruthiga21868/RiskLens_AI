import axios from 'axios'

// Base URL is the Vite proxy (dev) / same origin (prod via Nginx).
const api = axios.create({ baseURL: '/api/v1' })

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