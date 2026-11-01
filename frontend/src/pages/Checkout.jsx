import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, money } from '../api.js'
import { useStore } from '../StoreContext.jsx'

export default function Checkout() {
  const { refreshCart } = useStore()
  const navigate = useNavigate()
  const [cart, setCart] = useState(null)
  const [fullName, setFullName] = useState('')
  const [address, setAddress] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    api.cart().then(setCart).catch((err) => setError(err.message))
  }, [])

  async function handleSubmit(e) {
    e.preventDefault()
    setBusy(true)
    try {
      const order = await api.placeOrder({ full_name: fullName, address })
      await refreshCart()
      navigate('/orders/' + order.id)
    } catch (err) {
      setError(err.message)
      setBusy(false)
    }
  }

  if (!cart) return error ? <p className="error">{error}</p> : <p>Loading...</p>
  if (cart.items.length === 0) return <p>Your cart is empty.</p>

  return (
    <>
      <h1>Checkout</h1>
      <div className="two-col">
        <form onSubmit={handleSubmit}>
          <label>Full name
            <input value={fullName} onChange={(e) => setFullName(e.target.value)} required maxLength="120" />
          </label>
          <label>Delivery address
            <textarea value={address} onChange={(e) => setAddress(e.target.value)} required maxLength="300" rows="4" />
          </label>
          {error && <p className="error">{error}</p>}
          <button className="primary" disabled={busy}>{busy ? 'Placing order...' : 'Place order'}</button>
          <p className="muted small">Payment is cash on delivery in this demo.</p>
        </form>

        <div>
          <h2>Order summary</h2>
          <ul className="summary">
            {cart.items.map((i) => (
              <li key={i.product_id}>
                <span>{i.name} &times; {i.quantity}</span>
                <span>{money(i.subtotal_cents)}</span>
              </li>
            ))}
            <li className="total"><span>Total</span><span>{money(cart.total_cents)}</span></li>
          </ul>
        </div>
      </div>
    </>
  )
}
