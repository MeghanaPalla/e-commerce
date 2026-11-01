import { Navigate, useLocation } from 'react-router-dom'
import { useStore } from '../StoreContext.jsx'

export default function RequireAuth({ children }) {
  const { user, loading } = useStore()
  const location = useLocation()
  if (loading) return <p>Loading...</p>
  if (!user) return <Navigate to="/login" state={{ from: location.pathname }} replace />
  return children
}
