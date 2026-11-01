import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { api } from '../api.js'
import ProductCard from '../components/ProductCard.jsx'

export default function Home() {
  // search, category, sort and page live in the URL so links can be shared
  const [params, setParams] = useSearchParams()
  const q = params.get('q') || ''
  const category = params.get('category') || ''
  const sort = params.get('sort') || 'newest'
  const page = Number(params.get('page') || 1)

  const [search, setSearch] = useState(q)
  const [categories, setCategories] = useState([])
  const [data, setData] = useState({ items: [], pages: 1, total: 0 })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.categories().then(setCategories).catch(() => {})
  }, [])

  useEffect(() => {
    setLoading(true)
    api.products({ q, category, sort, page })
      .then((res) => { setData(res); setError('') })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [q, category, sort, page])

  function update(changes) {
    const next = { q, category, sort, page: 1, ...changes }
    const clean = {}
    for (const [key, value] of Object.entries(next)) {
      if (value && !(key === 'page' && value === 1) && !(key === 'sort' && value === 'newest')) {
        clean[key] = value
      }
    }
    setParams(clean)
  }

  function handleSearch(e) {
    e.preventDefault()
    update({ q: search.trim() })
  }

  return (
    <>
      <div className="filters">
        <form onSubmit={handleSearch} className="search">
          <input
            placeholder="Search products"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <button>Search</button>
        </form>
        <select value={category} onChange={(e) => update({ category: e.target.value })}>
          <option value="">All categories</option>
          {categories.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>
        <select value={sort} onChange={(e) => update({ sort: e.target.value })}>
          <option value="newest">Newest</option>
          <option value="price_asc">Price: low to high</option>
          <option value="price_desc">Price: high to low</option>
          <option value="name">Name A-Z</option>
        </select>
      </div>

      {error && <p className="error">{error}</p>}
      {loading && <p>Loading...</p>}
      {!loading && !error && data.items.length === 0 && <p>No products found.</p>}

      <div className="grid">
        {data.items.map((p) => <ProductCard key={p.id} product={p} />)}
      </div>

      {data.pages > 1 && (
        <div className="pager">
          <button disabled={page <= 1} onClick={() => update({ page: page - 1 })}>Previous</button>
          <span>Page {data.page} of {data.pages}</span>
          <button disabled={page >= data.pages} onClick={() => update({ page: page + 1 })}>Next</button>
        </div>
      )}
    </>
  )
}
