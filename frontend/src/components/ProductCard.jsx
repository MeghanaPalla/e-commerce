import { Link } from 'react-router-dom'
import { money } from '../api.js'

export default function ProductCard({ product }) {
  return (
    <Link to={'/product/' + product.id} className="card">
      <div className="thumb">{product.name[0]}</div>
      <div className="card-body">
        <div className="card-title">{product.name}</div>
        <div className="muted small">{product.category}</div>
        <div className="price">{money(product.price_cents)}</div>
        {product.stock === 0 && <span className="badge">Out of stock</span>}
      </div>
    </Link>
  )
}
