import { useState } from 'react'
import { Link, useNavigate, Navigate } from 'react-router-dom'
import { useStore } from '../StoreContext.jsx'

export default function Register() {
  const { user, register } = useStore()
  const navigate = useNavigate()
  const [form, setForm] = useState({ username: '', email: '', password: '', password2: '' })
  const [error, setError] = useState('')

  if (user) return <Navigate to="/" replace />

  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value })

  async function handleSubmit(e) {
    e.preventDefault()
    if (form.password !== form.password2) {
      setError('Passwords do not match')
      return
    }
    try {
      await register(form.username, form.email, form.password)
      navigate('/')
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="auth-form">
      <h1>Register</h1>
      <label>Username
        <input value={form.username} onChange={set('username')} required minLength="3" maxLength="64" />
      </label>
      <label>Email
        <input type="email" value={form.email} onChange={set('email')} required />
      </label>
      <label>Password
        <input type="password" value={form.password} onChange={set('password')} required minLength="6" />
      </label>
      <label>Repeat password
        <input type="password" value={form.password2} onChange={set('password2')} required />
      </label>
      {error && <p className="error">{error}</p>}
      <button className="primary">Register</button>
      <p>Already registered? <Link to="/login">Sign in</Link></p>
    </form>
  )
}
