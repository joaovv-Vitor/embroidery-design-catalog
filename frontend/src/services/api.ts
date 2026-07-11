import axios from 'axios'
export const api = axios.create({baseURL:import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',timeout:30000})
export function apiAssetUrl(path:string|null):string|null { if(!path)return null; if(/^https?:\/\//.test(path))return path; const base=api.defaults.baseURL ?? ''; const origin=new URL(base,window.location.origin).origin; return new URL(path,origin).toString() }
