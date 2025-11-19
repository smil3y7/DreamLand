/**
 * Language toggle component.
 * Allows switching between English and Slovenian.
 */
import { useTranslation } from '../lib/i18n'
import { Globe } from 'lucide-react'

export default function LanguageToggle() {
  const { language, setLanguage, t } = useTranslation()

  const toggleLanguage = () => {
    setLanguage(language === 'en' ? 'si' : 'en')
  }

  return (
    <button
      onClick={toggleLanguage}
      className="flex items-center gap-2 px-3 py-1.5 bg-gray-800 hover:bg-gray-700 rounded transition-colors"
      title="Change Language"
    >
      <Globe className="w-4 h-4" />
      <span className="text-sm font-medium">
        {language === 'en' ? 'EN' : 'SI'}
      </span>
    </button>
  )
}