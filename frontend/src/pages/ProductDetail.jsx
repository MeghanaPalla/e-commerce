import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { api, money } from '../api.js'
import { useStore } from '../StoreContext.jsx'

export default function ProductDetail() {
  const { id } = useParams()
  const { user, refreshCart } = useStore()
  const navigate = useNavigate()
  const [product, setProduct] = useState(null)
  const [quantity, setQuantity] = useState(1)
  const [error, setError] = useState('')

  useEffect(() => {
    api.product(id).then(setProduct).catch((err) => setError(err.message))
  }, [id])

  async function addToCart() {
    if (!user) {
      navigate('/login', { state: { from: '/product/' + id } })
      return
    }
    try {
      await api.addToCart(id, quantity)
      await refreshCart()
      navigate('/cart')
    } catch (err) {
      setError(err.message)
    }
  }

  if (error && !product) return <p className="error">{error}</p>
  if (!product) return <p>Loading...</p>

  return (
    <div className="detail">
      <div className="thumb big">{product.name[0]}</div>
      <div>
        <Link to="/" className="small">&larr; All products</Link>
        <h1>{product.name}</h1>
        <p className="muted">{product.category}</p>
        <p className="price large">{money(product.price_cents)}</p>
        <p>{product.description}</p>

        {product.stock > 0 ? (
          <>
            <p className="muted small">{product.stock} in stock</p>
            <div className="row">
              <input
                type="number"
                min="1"
                max={product.stock}
                value={quantity}
                onChange={(e) => setQuantity(Math.max(1, Number(e.target.value) || 1))}
                className="qty"
              />
              <button className="primary" onClick={addToCart}>
                {user ? 'Add to cart' : 'Log in to buy'}
              </button>
            </div>
          </>
        ) : (
          <span className="badge">Out of stock</span>
        )}
        {error && <p className="error">{error}</p>}
      </div>
    </div>
  )
}
