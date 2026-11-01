import { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { api } from './api.js'

// keeps the logged in user and the cart count available to every page
const StoreContext = createContext(null)

export function StoreProvider({ children }) {
  const [user, setUser] = useState(null)
  const [cartCount, setCartCount] = useState(0)
  const [loading, setLoading] = useState(true)

  const refreshCart = useCallback(async () => {
    try {
      const cart = await api.cart()
      setCartCount(cart.count)
    } catch {
      setCartCount(0)
    }
  }, [])

  // on first load, check if the saved token is still good
  useEffect(() => {
    if (!localStorage.getItem('token')) {
      setLoading(false)
      return
    }
    api.me()
      .then((data) => {
        setUser(data.user)
        return refreshCart()
      })
      .catch(() => localStorage.removeItem('token'))
      .finally(() => setLoading(false))
  }, [refreshCart])

  function saveSession(data) {
    localStorage.setItem('token', data.token)
    setUser(data.user)
    refreshCart()
  }

  async function login(username, password) {
    saveSession(await api.login({ username, password }))
  }

  async function register(username, email, password) {
    saveSession(await api.register({ username, email, password }))
  }

  function logout() {
    localStorage.removeItem('token')
    setUser(null)
    setCartCount(0)
  }

  return (
    <StoreContext.Provider
      value={{ user, loading, cartCount, refreshCart, login, register, logout }}
    >
      {children}
    </StoreContext.Provider>
  )
}

export const useStore = () => useContext(StoreContext)
