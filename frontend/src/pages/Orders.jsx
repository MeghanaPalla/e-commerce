import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, money } from '../api.js'

export default function Orders() {
  const [orders, setOrders] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.orders().then(setOrders).catch((err) => setError(err.message))
  }, [])

  if (error) return <p className="error">{error}</p>
  if (!orders) return <p>Loading...</p>
  if (orders.length === 0) return <p>You haven't ordered anything yet. <Link to="/">Start shopping</Link></p>

  return (
    <>
      <h1>My Orders</h1>
      <table>
        <thead>
          <tr><th>Order</th><th>Date</th><th>Status</th><th className="right">Total</th></tr>
        </thead>
        <tbody>
          {orders.map((o) => (
            <tr key={o.id}>
              <td><Link to={'/orders/' + o.id}>#{o.id.slice(-6)}</Link></td>
              <td>{new Date(o.created).toLocaleString()}</td>
              <td>{o.status}</td>
              <td className="right">{money(o.total_cents)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  )
}
