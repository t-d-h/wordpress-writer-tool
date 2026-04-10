import { useState, useEffect } from 'react'
import { HiOutlineSparkles, HiOutlineCheck, HiOutlineXMark } from 'react-icons/hi2'
import { getProviders, getDefaultModels, updateDefaultModels, getProviderModels } from '../../api/client'

export default function DefaultModels() {
  const [providers, setProviders] = useState([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [defaults, setDefaults] = useState({
    writing_provider_id: '',
    writing_model_name: '',
    image_provider_id: '',
    image_model_name: '',
    video_provider_id: '',
    video_model_name: '',
  })
  const [availableModels, setAvailableModels] = useState({})
  const [fetchingModels, setFetchingModels] = useState({})

  useEffect(() => {
    const init = async () => {
      try {
        const { data: provs } = await getProviders()
        setProviders(provs)
        
        try {
          const { data } = await getDefaultModels()
          if (data.id) {
            setDefaults({
              writing_provider_id: data.writing_provider_id || '',
              writing_model_name: data.writing_model_name || '',
              image_provider_id: data.image_provider_id || '',
              image_model_name: data.image_model_name || '',
              video_provider_id: data.video_provider_id || '',
              video_model_name: data.video_model_name || '',
            })

            // Now fetch models for the loaded defaults
            const sections = ['writing', 'image', 'video']
            for (const section of sections) {
              const provId = data[`${section}_provider_id`]
              if (provId) {
                const provider = provs.find(p => p.id === provId)
                if (provider && provider.provider_type === 'openai_compatible') {
                  setFetchingModels(prev => ({ ...prev, [section]: true }))
                  try {
                    const { data: mData } = await getProviderModels(provId)
                    setAvailableModels(prev => ({ ...prev, [section]: mData.models || [] }))
                  } catch (e) {
                    console.error('Failed to fetch models for', section, e)
                    setAvailableModels(prev => ({ ...prev, [section]: [] }))
                  } finally {
                    setFetchingModels(prev => ({ ...prev, [section]: false }))
                  }
                }
              }
            }
          }
        } catch (e) {
          console.error('Error loading default models:', e)
        }
      } catch (e) {
        console.error('Error loading providers:', e)
      } finally {
        setLoading(false)
      }
    }
    init()
  }, [])

  const handleSave = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      await updateDefaultModels(defaults)
      alert('Default models saved successfully!')
    } catch (e) {
      alert('Error: ' + (e.response?.data?.detail || e.message))
    } finally {
      setSaving(false)
    }
  }

  const handleProviderChange = async (providerId, section) => {
    const fieldMap = {
      writing: 'writing_provider_id',
      image: 'image_provider_id',
      video: 'video_provider_id',
    }
    const modelFieldMap = {
      writing: 'writing_model_name',
      image: 'image_model_name',
      video: 'video_model_name',
    }
    
    setDefaults({
      ...defaults,
      [fieldMap[section]]: providerId,
      [modelFieldMap[section]]: '',
    })
    
    if (providerId) {
      await fetchModelsForProvider(providerId, section)
    }
  }

  const fetchModelsForProvider = async (providerId, section) => {
    const provider = providers.find(p => p.id === providerId)
    if (!provider || provider.provider_type !== 'openai_compatible') {
      setAvailableModels(prev => ({ ...prev, [section]: [] }))
      return
    }

    setFetchingModels(prev => ({ ...prev, [section]: true }))
    try {
      const { data } = await getProviderModels(providerId)
      setAvailableModels(prev => ({ ...prev, [section]: data.models || [] }))
    } catch (e) {
      console.error('Failed to fetch models:', e)
      setAvailableModels(prev => ({ ...prev, [section]: [] }))
    } finally {
      setFetchingModels(prev => ({ ...prev, [section]: false }))
    }
  }

  const getProvider = (providerId) => providers.find(p => p.id === providerId)

  const renderSection = (title, icon, sectionKey) => {
    const providerIdField = `${sectionKey}_provider_id`
    const modelNameField = `${sectionKey}_model_name`
    const provider = getProvider(defaults[providerIdField])
    const showModelName = provider && provider.provider_type === 'openai_compatible'

    return (
      <div key={sectionKey} style={{ marginBottom: 32, paddingBottom: 24, borderBottom: '1px solid var(--border)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
          {icon}
          <h3 style={{ fontSize: 16, fontWeight: 600, margin: 0 }}>{title}</h3>
        </div>

        <div className="form-group" style={{ marginBottom: 16 }}>
          <label className="form-label">Default AI Provider</label>
          <select
            className="form-select"
            value={defaults[providerIdField]}
            onChange={e => handleProviderChange(e.target.value, sectionKey)}
          >
            <option value="">-- No default --</option>
            {providers.map(p => (
              <option key={p.id} value={p.id}>{p.name} ({p.provider_type})</option>
            ))}
          </select>
          <small style={{ display: 'block', marginTop: 4, color: 'var(--text-muted)' }}>
            Select a provider to use as default for {title.toLowerCase()}
          </small>
        </div>

        {showModelName && (
          <div className="form-group">
            <label className="form-label">Default Model Name</label>
            {fetchingModels[sectionKey] ? (
              <div style={{ color: 'var(--text-muted)', fontSize: 14 }}>Loading models...</div>
            ) : (
              <div>
                <input
                  type="text"
                  className="form-input"
                  style={{ width: '100%' }}
                  placeholder="Enter or select model name"
                  value={defaults[modelNameField]}
                  onChange={e => setDefaults({ ...defaults, [modelNameField]: e.target.value })}
                  list={`${sectionKey}-models`}
                />
                {availableModels[sectionKey] && availableModels[sectionKey].length > 0 && (
                  <datalist id={`${sectionKey}-models`}>
                    {availableModels[sectionKey].map(m => (
                      <option key={m} value={m} />
                    ))}
                  </datalist>
                )}
                {(!availableModels[sectionKey] || availableModels[sectionKey].length === 0) && (
                  <small style={{ display: 'block', marginTop: 4, color: 'var(--text-muted)' }}>
                    Type the exact model name. No models were automatically found for this provider.
                  </small>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    )
  }

  if (loading) return <div className="loading-page"><div className="loading-spinner" /></div>

  return (
    <div className="page-enter">
      <div className="page-header">
        <h1 className="page-title">Default Models</h1>
        <p className="page-description">Configure default AI models for content generation</p>
      </div>

      <form onSubmit={handleSave}>
        {renderSection('Writing', <HiOutlineSparkles size={20} />, 'writing')}
        {renderSection('Image Generation', <HiOutlineSparkles size={20} />, 'image')}
        {renderSection('Video Generation', <HiOutlineSparkles size={20} />, 'video')}

        <div className="modal-footer" style={{ marginTop: 24, paddingTop: 16, borderTop: '1px solid var(--border)' }}>
          <button type="submit" className="btn btn-primary" disabled={saving}>
            {saving ? 'Saving...' : 'Save Defaults'}
          </button>
        </div>
      </form>
    </div>
  )
}
