import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api, money } from '../api.js'

export default function OrderDetail() {
  const { id } = useParams()
  const [order, setOrder] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.order(id).then(setOrder).catch((err) => setError(err.message))
  }, [id])

  if (error) return <p className="error">{error}</p>
  if (!order) return <p>Loading...</p>

  return (
    <>
      <h1>Order #{order.id.slice(-6)}</h1>
      <p className="muted">Placed on {new Date(order.created).toLocaleString()} &middot; {order.status}</p>
      <p><strong>{order.full_name}</strong><br />{order.address}</p>
      <table>
        <thead>
          <tr><th>Product</th><th>Price</th><th>Qty</th><th className="right">Subtotal</th></tr>
        </thead>
        <tbody>
          {order.items.map((i, idx) => (
            <tr key={idx}>
              <td>{i.name}</td>
              <td>{money(i.price_cents)}</td>
              <td>{i.quantity}</td>
              <td className="right">{money(i.subtotal_cents)}</td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr><th colSpan="3" className="right">Total</th><th className="right">{money(order.total_cents)}</th></tr>
        </tfoot>
      </table>
      <Link to="/orders">&larr; All orders</Link>
    </>
  )
}
