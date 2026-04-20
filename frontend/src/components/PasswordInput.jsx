import { useState } from 'react'
import PropTypes from 'prop-types'
import { HiOutlineEye, HiOutlineEyeSlash } from 'react-icons/hi2'

export default function PasswordInput({ id, value, onChange, placeholder, required, disabled, className }) {
  const [showPassword, setShowPassword] = useState(false)

  return (
    <div style={{ position: 'relative' }}>
      <input
        id={id}
        className={className}
        type={showPassword ? 'text' : 'password'}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        required={required}
        disabled={disabled}
        style={{ paddingRight: '40px' }}
      />
      <button
        type="button"
        onClick={() => setShowPassword(!showPassword)}
        style={{
          position: 'absolute',
          right: '10px',
          top: '50%',
          transform: 'translateY(-50%)',
          background: 'none',
          border: 'none',
          cursor: 'pointer',
          color: 'var(--text-muted)',
          display: 'flex',
          alignItems: 'center'
        }}
      >
        {showPassword ? <HiOutlineEyeSlash size={18} /> : <HiOutlineEye size={18} />}
      </button>
    </div>
  )
}

PasswordInput.propTypes = {
  id: PropTypes.string,
  value: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  placeholder: PropTypes.string,
  required: PropTypes.bool,
  disabled: PropTypes.bool,
  className: PropTypes.string
}
