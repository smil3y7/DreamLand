/**
 * Dream input form component.
 * Allows users to enter new dreams with date, cycle, and content.
 */
import { useState } from 'react'
import { useTranslation } from '../lib/i18n'

export default function DreamInput({ onSubmit }) {
  const { t } = useTranslation()
  const [formData, setFormData] = useState({
    date: new Date().toISOString().split('T')[0],
    cycle: 1,
    content: '',
  })
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: name === 'cycle' ? parseInt(value) || 1 : value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!formData.content.trim()) {
      alert('Please enter dream content')
      return
    }

    setIsSubmitting(true)
    
    try {
      await onSubmit({
        date: new Date(formData.date).toISOString(),
        cycle: formData.cycle,
        content: formData.content,
        language: 'en', // Could be dynamic based on i18n
      })
      
      // Reset form
      setFormData({
        date: new Date().toISOString().split('T')[0],
        cycle: 1,
        content: '',
      })
    } catch (error) {
      console.error('Error submitting dream:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="bg-gray-800 rounded-lg p-4">
      <h3 className="text-lg font-semibold mb-4 text-blue-300">
        {t('dream.title')}
      </h3>
      
      <form onSubmit={handleSubmit} className="space-y-3">
        <div>
          <label className="block text-sm text-gray-300 mb-1">
            {t('dream.date')}
          </label>
          <input
            type="date"
            name="date"
            value={formData.date}
            onChange={handleChange}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded focus:outline-none focus:border-blue-500 text-white"
            required
          />
        </div>

        <div>
          <label className="block text-sm text-gray-300 mb-1">
            {t('dream.cycle')}
          </label>
          <input
            type="number"
            name="cycle"
            min="1"
            value={formData.cycle}
            onChange={handleChange}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded focus:outline-none focus:border-blue-500 text-white"
            required
          />
        </div>

        <div>
          <label className="block text-sm text-gray-300 mb-1">
            {t('dream.content')}
          </label>
          <textarea
            name="content"
            value={formData.content}
            onChange={handleChange}
            rows="6"
            placeholder="Describe your dream..."
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded focus:outline-none focus:border-blue-500 text-white resize-none"
            required
          />
        </div>

        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded font-medium transition-colors"
        >
          {isSubmitting ? t('dream.processing') : t('dream.submit')}
        </button>
      </form>
    </div>
  )
}