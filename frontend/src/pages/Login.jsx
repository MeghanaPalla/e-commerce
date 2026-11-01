import { useState } from 'react'
import { Link, useNavigate, useLocation, Navigate } from 'react-router-dom'
import { useStore } from '../StoreContext.jsx'

export default function Login() {
  const { user, login } = useStore()
  const navigate = useNavigate()
  const location = useLocation()
  const from = location.state?.from || '/'
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  if (user) return <Navigate to="/" replace />

  async function handleSubmit(e) {
    e.preventDefault()
    try {
      await login(username, password)
      navigate(from, { replace: true })
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="auth-form">
      <h1>Sign In</h1>
      <label>Username or email
        <input value={username} onChange={(e) => setUsername(e.target.value)} required />
      </label>
      <label>Password
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
      </label>
      {error && <p className="error">{error}</p>}
      <button className="primary">Sign In</button>
      <p>New here? <Link to="/register">Create an account</Link></p>
    </form>
  )
}
