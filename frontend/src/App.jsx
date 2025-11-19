/**
 * Main DreamLand application component.
 * Manages state and layout for the dream journaling interface.
 */
import { useState, useEffect } from 'react'
import DreamInput from './components/DreamInput'
import DreamList from './components/DreamList'
import WorldMap from './components/WorldMap'
import LanguageToggle from './components/LanguageToggle'
import { api } from './lib/api'
import { useTranslation } from './lib/i18n'
import './App.css'

function App() {
  const [dreams, setDreams] = useState([])
  const [locations, setLocations] = useState([])
  const [selectedLocation, setSelectedLocation] = useState(null)
  const [currentLayer, setCurrentLayer] = useState('PRIMARY')
  const [loading, setLoading] = useState(true)
  const { t } = useTranslation()

  // Load initial data
  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const [dreamsData, locationsData] = await Promise.all([
        api.getDreams(),
        api.getLocations()
      ])
      setDreams(dreamsData)
      setLocations(locationsData)
    } catch (error) {
      console.error('Error loading data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDreamSubmit = async (dreamData) => {
    try {
      const newDream = await api.createDream(dreamData)
      setDreams([newDream, ...dreams])
      
      // Reload locations after processing (with delay)
      setTimeout(() => {
        api.getLocations().then(setLocations)
      }, 2000)
    } catch (error) {
      console.error('Error creating dream:', error)
      alert('Failed to create dream. Please try again.')
    }
  }

  const handleLocationUpdate = async (locationId, updates) => {
    try {
      const updated = await api.updateLocation(locationId, updates)
      setLocations(locations.map(loc => 
        loc.id === locationId ? updated : loc
      ))
    } catch (error) {
      console.error('Error updating location:', error)
    }
  }

  const filteredLocations = locations.filter(loc => 
    currentLayer === 'ALL' || loc.layer === currentLayer
  )

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-900">
        <div className="text-white text-xl">{t('loading')}</div>
      </div>
    )
  }

  return (
    <div className="flex h-screen bg-gray-900 text-white">
      {/* Left Panel - Dream Input & List */}
      <div className="w-96 flex flex-col border-r border-gray-700">
        <div className="p-4 border-b border-gray-700 flex items-center justify-between">
          <h1 className="text-2xl font-bold text-blue-400">🌙 DreamLand</h1>
          <LanguageToggle />
        </div>
        
        <div className="p-4 border-b border-gray-700">
          <DreamInput onSubmit={handleDreamSubmit} />
        </div>
        
        <div className="flex-1 overflow-y-auto">
          <DreamList 
            dreams={dreams} 
            onSelectDream={(dream) => console.log('Selected:', dream)}
          />
        </div>
        
        <div className="p-4 border-t border-gray-700">
          <div className="text-sm text-gray-400">
            <div>{t('stats.dreams')}: {dreams.length}</div>
            <div>{t('stats.locations')}: {locations.length}</div>
          </div>
        </div>
      </div>

      {/* Right Panel - Map */}
      <div className="flex-1 flex flex-col">
        <div className="p-4 border-b border-gray-700 flex items-center justify-between">
          <h2 className="text-xl font-semibold">{t('map.title')}</h2>
          
          <div className="flex gap-2">
            <button
              onClick={() => setCurrentLayer('LOWER')}
              className={`px-3 py-1 rounded ${
                currentLayer === 'LOWER' 
                  ? 'bg-gray-600 text-white' 
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
            >
              {t('map.layers.lower')}
            </button>
            <button
              onClick={() => setCurrentLayer('PRIMARY')}
              className={`px-3 py-1 rounded ${
                currentLayer === 'PRIMARY' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
            >
              {t('map.layers.primary')}
            </button>
            <button
              onClick={() => setCurrentLayer('UPPER')}
              className={`px-3 py-1 rounded ${
                currentLayer === 'UPPER' 
                  ? 'bg-purple-600 text-white' 
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
            >
              {t('map.layers.upper')}
            </button>
            <button
              onClick={() => setCurrentLayer('ALL')}
              className={`px-3 py-1 rounded ${
                currentLayer === 'ALL' 
                  ? 'bg-green-600 text-white' 
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
            >
              {t('map.layers.all')}
            </button>
          </div>
        </div>
        
        <div className="flex-1">
          <WorldMap
            locations={filteredLocations}
            selectedLocation={selectedLocation}
            onLocationSelect={setSelectedLocation}
            onLocationUpdate={handleLocationUpdate}
          />
        </div>
      </div>
    </div>
  )
}

export default App