/**
 * Location details popup component.
 * Displays information about a selected location including entities and transits.
 */
import { useEffect, useState } from 'react'
import { X, MapPin, User, ArrowRight } from 'lucide-react'
import { api } from '../lib/api'
import { useTranslation } from '../lib/i18n'

export default function LocationPopup({ location, onClose }) {
  const { t } = useTranslation()
  const [entities, setEntities] = useState([])
  const [transits, setTransits] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadLocationDetails()
  }, [location.id])

  const loadLocationDetails = async () => {
    setLoading(true)
    try {
      const [entitiesData, transitsData] = await Promise.all([
        api.getEntities(location.id),
        api.getLocationTransits(location.id)
      ])
      setEntities(entitiesData)
      setTransits(transitsData)
    } catch (error) {
      console.error('Error loading location details:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose()
    }
  }

  return (
    <div 
      className="popup-overlay fade-in"
      onClick={handleBackdropClick}
    >
      <div className="popup-content">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <span className="text-4xl">{location.symbol || '📍'}</span>
            <div>
              <h2 className="text-2xl font-bold text-white">{location.name}</h2>
              <p className="text-sm text-gray-400">{location.archetype}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-700 rounded"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Description */}
        {location.description && (
          <div className="mb-4">
            <p className="text-gray-300">{location.description}</p>
          </div>
        )}

        {/* Stats */}
        <div className="flex gap-4 mb-4 text-sm">
          <div className="flex items-center gap-2">
            <MapPin className="w-4 h-4 text-blue-400" />
            <span className="text-gray-400">
              {t('location.frequency', { count: location.frequency })}
            </span>
          </div>
          <div className="px-2 py-1 bg-gray-800 rounded">
            <span className="text-gray-400">Layer: </span>
            <span className="text-white">{location.layer}</span>
          </div>
          <div className="px-2 py-1 rounded" style={{ backgroundColor: location.color + '33' }}>
            <span style={{ color: location.color }}>●</span>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-8 text-gray-400">
            Loading details...
          </div>
        ) : (
          <>
            {/* Entities */}
            {entities.length > 0 && (
              <div className="mb-4">
                <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                  <User className="w-5 h-5" />
                  {t('location.entities')}
                </h3>
                <div className="space-y-2">
                  {entities.map(entity => (
                    <div 
                      key={entity.id}
                      className="flex items-center gap-3 p-2 bg-gray-800 rounded"
                    >
                      <span className="text-2xl">{entity.symbol || '👤'}</span>
                      <div className="flex-1">
                        <div className="font-medium text-white">{entity.name}</div>
                        <div className="text-xs text-gray-400">{entity.type}</div>
                      </div>
                      {entity.confidence < 1 && (
                        <div className="text-xs text-yellow-500">
                          {Math.round(entity.confidence * 100)}%
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Transits */}
            {transits.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                  <ArrowRight className="w-5 h-5" />
                  {t('location.transits')}
                </h3>
                <div className="space-y-2">
                  {transits.map(transit => (
                    <div 
                      key={transit.id}
                      className="p-2 bg-gray-800 rounded text-sm"
                    >
                      <div className="flex items-center gap-2 text-gray-300">
                        <span>→</span>
                        <span>Location #{transit.to_location_id}</span>
                      </div>
                      {transit.trigger && (
                        <div className="text-xs text-gray-400 mt-1">
                          {transit.trigger}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {entities.length === 0 && transits.length === 0 && (
              <div className="text-center py-8 text-gray-400">
                No additional details available
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}