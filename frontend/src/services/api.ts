import axios from 'axios'

function resolveApiBaseUrl(): string {
  const configuredUrl = import.meta.env.VITE_API_URL?.trim()
  if (configuredUrl) {
    return configuredUrl
  }

  if (import.meta.env.DEV) {
    return 'http://localhost:8000/api/v1'
  }

  return new URL('/api/v1', window.location.origin).toString()
}

export const api = axios.create({ baseURL: resolveApiBaseUrl(), timeout: 30000 })

export function apiAssetUrl(path: string | null): string | null {
  if (!path) return null
  if (/^https?:\/\//.test(path)) return path

  const base = api.defaults.baseURL ?? ''
  const origin = new URL(base, window.location.origin).origin
  return new URL(path, origin).toString()
}
