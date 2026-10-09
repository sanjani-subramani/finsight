import { useState, type FormEvent } from 'react'
import { Navigate } from 'react-router-dom'
import { authApi } from '../api/auth'
import { useOrgAuth } from '../auth/useOrgAuth'
import './Login.css'

export function Login() {
  const { login, isAuthenticated } = useOrgAuth()
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [email, setEmail] = useState('')
  const [displayName, setDisplayName] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  if (isAuthenticated) {
    return <Navigate to="/" replace />
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setSubmitting(true)

    try {
      if (mode === 'register') {
        if (password.length < 10) {
          setError('Password must be at least 10 characters long.')
          setSubmitting(false)
          return
        }
        try {
          await authApi.register({
            email,
            password,
            display_name: displayName || undefined,
          })
        } catch (regErr: any) {
          // If email is already registered, proceed to attempt login with the given password
          if (regErr?.response?.status === 409) {
            // Already registered - try logging in
          } else {
            throw regErr
          }
        }
      }
      // After registration (or for sign-in), authenticate the session
      await login(email, password)
    } catch (err: any) {
      const data = err?.response?.data
      const msg = data?.error?.message || data?.detail || (typeof data?.error === 'string' ? data.error : null)
      if (msg) {
        setError(typeof msg === 'string' ? msg : 'Authentication failed. Please check your details.')
      } else {
        setError(mode === 'login' ? 'Invalid email or password.' : 'Could not complete registration. Please try signing in.')
      }
    } finally {
      setSubmitting(false)
    }
  }

  function toggleMode(newMode: 'login' | 'register') {
    setMode(newMode)
    setError(null)
  }

  return (
    <div className="login-page">
      <div className="login-card animate-fade-in">
        <div className="login-brand">
          <div className="login-logo">FS</div>
          <div className="login-brand__text">
            <h1>FinSentinel</h1>
            <span className="login-brand__subtitle">Operations &amp; Security Platform</span>
          </div>
        </div>

        <div className="login-tabs" role="tablist">
          <button
            type="button"
            className={`login-tab ${mode === 'login' ? 'login-tab--active' : ''}`}
            onClick={() => toggleMode('login')}
          >
            Sign in
          </button>
          <button
            type="button"
            className={`login-tab ${mode === 'register' ? 'login-tab--active' : ''}`}
            onClick={() => toggleMode('register')}
          >
            Create account
          </button>
        </div>

        <form className="login-form" onSubmit={handleSubmit}>
          {mode === 'register' && (
            <label>
              <span>Full name / Display name</span>
              <input
                type="text"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                placeholder="Alex Morgan"
              />
            </label>
          )}

          <label>
            <span>Email address</span>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="operator@finsentinel.io"
              required
              autoFocus
            />
          </label>

          <label>
            <span>Password</span>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••••••"
              required
            />
            {mode === 'register' && (
              <span className="login-form__hint">Must be at least 10 characters with numbers and letters</span>
            )}
          </label>

          {error && (
            <div className="login-form__error animate-fade-in" role="alert">
              <span>⚠️</span> {error}
            </div>
          )}

          <button type="submit" disabled={submitting} className="login-submit-btn">
            {submitting ? (
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}>
                <span className="spinner" style={{ width: 14, height: 14 }} />{' '}
                {mode === 'login' ? 'Signing in…' : 'Creating account…'}
              </span>
            ) : mode === 'login' ? (
              'Sign in'
            ) : (
              'Create account'
            )}
          </button>

          <button
            type="button"
            className="login-toggle-link"
            onClick={() => toggleMode(mode === 'login' ? 'register' : 'login')}
          >
            {mode === 'login' ? "Don't have an account? Create one" : 'Already have an account? Sign in'}
          </button>
        </form>

        <div className="login-footer">
          <span>Protected by multi-tenant role-based access control</span>
        </div>
      </div>
    </div>
  )
}
