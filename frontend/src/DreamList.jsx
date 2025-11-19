/**
 * Dream list component.
 * Displays all recorded dreams in chronological order.
 */
import { format } from 'date-fns'
import { useTranslation } from '../lib/i18n'
import { Check, Clock } from 'lucide-react'

export default function DreamList({ dreams, onSelectDream }) {
  const { t } = useTranslation()

  if (dreams.length === 0) {
    return (
      <div className="p-8 text-center text-gray-400">
        <p>{t('dream.list.empty')}</p>
      </div>
    )
  }

  return (
    <div className="p-4">
      <h3 className="text-lg font-semibold mb-4 text-gray-300">
        {t('dream.list.title')}
      </h3>
      
      <div className="space-y-3">
        {dreams.map(dream => (
          <div
            key={dream.id}
            onClick={() => onSelectDream(dream)}
            className="bg-gray-800 p-4 rounded-lg cursor-pointer hover:bg-gray-750 transition-colors border border-gray-700"
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-400">
                  {format(new Date(dream.date), 'MMM d, yyyy')}
                </span>
                {dream.cycle > 1 && (
                  <span className="text-xs bg-gray-700 px-2 py-0.5 rounded">
                    Cycle {dream.cycle}
                  </span>
                )}
              </div>
              
              {dream.processed ? (
                <Check className="w-4 h-4 text-green-500" />
              ) : (
                <Clock className="w-4 h-4 text-yellow-500 animate-pulse" />
              )}
            </div>
            
            <p className="text-sm text-gray-300 line-clamp-3">
              {dream.content}
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}