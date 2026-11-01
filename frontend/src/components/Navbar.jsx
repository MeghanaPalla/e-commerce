import { Link, useNavigate } from 'react-router-dom'
import { useStore } from '../StoreContext.jsx'

export default function Navbar() {
  const { user, cartCount, logout } = useStore()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/')
  }

  return (
    <header className="navbar">
      <div className="container nav-inner">
        <Link to="/" className="brand">MiniShop</Link>
        <nav>
          {user ? (
            <>
              <Link to="/orders">Orders</Link>
              <Link to="/cart">Cart ({cartCount})</Link>
              <button className="link-button" onClick={handleLogout}>
                Logout ({user.username})
              </button>
            </>
          ) : (
            <>
              <Link to="/login">Login</Link>
              <Link to="/register">Register</Link>
            </>
          )}
        </nav>
      </div>
    </header>
  )
}
