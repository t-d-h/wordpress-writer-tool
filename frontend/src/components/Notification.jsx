import { useEffect } from 'react'
import { HiOutlineCheck, HiOutlineXMark, HiOutlineExclamationTriangle } from 'react-icons/hi2'

export default function Notification({ type, message, duration, onDismiss }) {
  useEffect(() => {
    if (duration && onDismiss) {
      const timer = setTimeout(() => {
        onDismiss()
      }, duration)
      return () => clearTimeout(timer)
    }
  }, [duration, onDismiss])

  const icons = {
    success: <HiOutlineCheck size={20} />,
    error: <HiOutlineExclamationTriangle size={20} />,
  }

  return (
    <div className={`notification ${type}`}>
      <div className="notification-icon">
        {icons[type]}
      </div>
      <div className="notification-message">
        {message}
      </div>
      <button className="notification-close" onClick={onDismiss} aria-label="Dismiss notification">
        <HiOutlineXMark size={18} />
      </button>
    </div>
  )
}
