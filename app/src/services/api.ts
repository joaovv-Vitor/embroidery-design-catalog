import axios from 'axios'

function resolveApiBaseUrl(): string {
  const configuredUrl = import.meta.env.VITE_API_URL?.trim()
  if (configuredUrl) {
    return configuredUrl.replace(/\/$/, '')
  }

  throw new Error('VITE_API_URL não foi configurada para este ambiente.')
}

export const api = axios.create({ baseURL: resolveApiBaseUrl(), timeout: 30000 })

export function apiAssetUrl(path: string | null): string | null {
  if (!path) return null
  if (/^https?:\/\//.test(path)) return path

  const base = api.defaults.baseURL ?? ''
  const origin = new URL(base, window.location.origin).origin
  return new URL(path, origin).toString()
}
