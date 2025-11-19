/**
 * API client for DreamLand backend.
 * Handles all HTTP requests to FastAPI backend.
 */
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const api = {
  // Dreams
  async getDreams(skip = 0, limit = 100) {
    const response = await apiClient.get(`/dreams?skip=${skip}&limit=${limit}`)
    return response.data
  },

  async getDream(id) {
    const response = await apiClient.get(`/dreams/${id}`)
    return response.data
  },

  async createDream(dreamData) {
    const response = await apiClient.post('/dreams', dreamData)
    return response.data
  },

  // Locations
  async getLocations(layer = null) {
    const url = layer ? `/locations?layer=${layer}` : '/locations'
    const response = await apiClient.get(url)
    return response.data
  },

  async getLocation(id) {
    const response = await apiClient.get(`/locations/${id}`)
    return response.data
  },

  async createLocation(locationData) {
    const response = await apiClient.post('/locations', locationData)
    return response.data
  },

  async updateLocation(id, updates) {
    const response = await apiClient.patch(`/locations/${id}`, updates)
    return response.data
  },

  async mergeLocations(sourceIds, targetName, userNote = null) {
    const response = await apiClient.post('/locations/merge', {
      source_ids: sourceIds,
      target_name: targetName,
      user_note: userNote,
    })
    return response.data
  },

  // Entities
  async getEntities(locationId = null) {
    const url = locationId ? `/entities?location_id=${locationId}` : '/entities'
    const response = await apiClient.get(url)
    return response.data
  },

  async getEntity(id) {
    const response = await apiClient.get(`/entities/${id}`)
    return response.data
  },

  async createEntity(entityData) {
    const response = await apiClient.post('/entities', entityData)
    return response.data
  },

  // Transits
  async getLocationTransits(locationId) {
    const response = await apiClient.get(`/locations/${locationId}/transits`)
    return response.data
  },

  // Stats & Export
  async getStats() {
    const response = await apiClient.get('/stats')
    return response.data
  },

  async exportWorld() {
    const response = await apiClient.get('/export')
    return response.data
  },
}

export default api