import { useState, useEffect } from 'react'
import { HiOutlinePlay, HiOutlineClock, HiOutlineCheckCircle, HiOutlineXCircle } from 'react-icons/hi2'
import { getDashboardStats } from '../api/client'

export default function Dashboard() {
  const [stats, setStats] = useState({ pending: 0, running: 0, completed: 0, failed: 0 })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStats()
    const interval = setInterval(loadStats, 5000)
    return () => clearInterval(interval)
  }, [])

  const loadStats = async () => {
    try {
      const { data } = await getDashboardStats()
      setStats(data)
    } catch (e) {
      console.error('Failed to load stats', e)
    } finally {
      setLoading(false)
    }
  }

  const statCards = [
    { key: 'running', label: 'Running', icon: <HiOutlinePlay />, value: stats.running },
    { key: 'pending', label: 'Waiting', icon: <HiOutlineClock />, value: stats.pending },
    { key: 'completed', label: 'Completed', icon: <HiOutlineCheckCircle />, value: stats.completed },
    { key: 'failed', label: 'Failed', icon: <HiOutlineXCircle />, value: stats.failed },
  ]

  return (
    <div className="page-enter">
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
        <p className="page-description">Overview of all jobs across your projects</p>
      </div>

      {loading ? (
        <div className="loading-page"><div className="loading-spinner" /></div>
      ) : (
        <div className="stats-grid">
          {statCards.map(card => (
            <div key={card.key} className={`stat-card ${card.key}`}>
              <div className="stat-label">{card.label}</div>
              <div className="stat-value">{card.value}</div>
              <div className="stat-icon">{card.icon}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
