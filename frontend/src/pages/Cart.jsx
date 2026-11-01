import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api, money } from '../api.js'
import { useStore } from '../StoreContext.jsx'

export default function Cart() {
  const { refreshCart } = useStore()
  const navigate = useNavigate()
  const [cart, setCart] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.cart().then(setCart).catch((err) => setError(err.message))
  }, [])

  async function change(action) {
    try {
      setCart(await action())
      setError('')
      refreshCart()
    } catch (err) {
      setError(err.message)
    }
  }

  if (!cart) return error ? <p className="error">{error}</p> : <p>Loading...</p>

  if (cart.items.length === 0) {
    return <p>Your cart is empty. <Link to="/">Keep shopping</Link></p>
  }

  return (
    <>
      <h1>Your Cart</h1>
      {error && <p className="error">{error}</p>}
      <table>
        <thead>
          <tr><th>Product</th><th>Price</th><th>Quantity</th><th className="right">Subtotal</th><th></th></tr>
        </thead>
        <tbody>
          {cart.items.map((item) => (
            <tr key={item.product_id}>
              <td><Link to={'/product/' + item.product_id}>{item.name}</Link></td>
              <td>{money(item.price_cents)}</td>
              <td>
                <input
                  type="number"
                  min="0"
                  max={item.stock}
                  defaultValue={item.quantity}
                  className="qty"
                  onBlur={(e) => {
                    const qty = Number(e.target.value)
                    if (qty !== item.quantity) change(() => api.updateCart(item.product_id, qty))
                  }}
                />
              </td>
              <td className="right">{money(item.subtotal_cents)}</td>
              <td>
                <button className="danger" onClick={() => change(() => api.removeFromCart(item.product_id))}>
                  Remove
                </button>
              </td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr>
            <th colSpan="3" className="right">Total</th>
            <th className="right">{money(cart.total_cents)}</th>
            <th></th>
          </tr>
        </tfoot>
      </table>
      <button className="primary" onClick={() => navigate('/checkout')}>Proceed to checkout</button>
    </>
  )
}
