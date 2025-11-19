/**
 * Internationalization (i18n) utilities.
 * Supports English and Slovenian languages.
 */
import { useState, useEffect, createContext, useContext } from 'react'

const translations = {
  en: {
    loading: 'Loading...',
    'dream.title': 'New Dream',
    'dream.date': 'Date',
    'dream.cycle': 'Cycle',
    'dream.content': 'Dream Content',
    'dream.submit': 'Save Dream',
    'dream.processing': 'Processing...',
    'dream.list.title': 'Dream Journal',
    'dream.list.empty': 'No dreams yet. Start recording!',
    'map.title': 'Dream World Map',
    'map.zoom': 'Zoom',
    'map.reset': 'Reset View',
    'map.layers.primary': 'Primary',
    'map.layers.upper': 'Upper',
    'map.layers.lower': 'Lower',
    'map.layers.all': 'All Layers',
    'location.frequency': 'Visited {count} time(s)',
    'location.entities': 'Entities',
    'location.transits': 'Connections',
    'stats.dreams': 'Total Dreams',
    'stats.locations': 'Total Locations',
    'language.en': 'English',
    'language.si': 'Slovenščina',
  },
  si: {
    loading: 'Nalaganje...',
    'dream.title': 'Nove sanje',
    'dream.date': 'Datum',
    'dream.cycle': 'Cikel',
    'dream.content': 'Vsebina sanj',
    'dream.submit': 'Shrani sanje',
    'dream.processing': 'Obdelava...',
    'dream.list.title': 'Dnevnik sanj',
    'dream.list.empty': 'Še ni sanj. Začni zapisovati!',
    'map.title': 'Karta sveta sanj',
    'map.zoom': 'Povečava',
    'map.reset': 'Ponastavi pogled',
    'map.layers.primary': 'Primarni',
    'map.layers.upper': 'Zgornji',
    'map.layers.lower': 'Spodnji',
    'map.layers.all': 'Vsi sloji',
    'location.frequency': 'Obiskano {count}x',
    'location.entities': 'Entitete',
    'location.transits': 'Povezave',
    'stats.dreams': 'Skupaj sanj',
    'stats.locations': 'Skupaj lokacij',
    'language.en': 'English',
    'language.si': 'Slovenščina',
  },
}

// Create context
const LanguageContext = createContext()

export const LanguageProvider = ({ children }) => {
  const [language, setLanguage] = useState(() => {
    return localStorage.getItem('dreamland_language') || 'en'
  })

  useEffect(() => {
    localStorage.setItem('dreamland_language', language)
  }, [language])

  const t = (key, params = {}) => {
    let text = translations[language][key] || key
    
    // Replace parameters
    Object.keys(params).forEach(param => {
      text = text.replace(`{${param}}`, params[param])
    })
    
    return text
  }

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  )
}

export const useTranslation = () => {
  const context = useContext(LanguageContext)
  if (!context) {
    // Return fallback if not wrapped in provider
    return {
      language: 'en',
      setLanguage: () => {},
      t: (key) => key,
    }
  }
  return context
}

export default LanguageProvider