const BASE = import.meta.env.VITE_API_URL || '/api'

async function request(path, { method = 'GET', body } = {}) {
  const headers = {}
  if (body) headers['Content-Type'] = 'application/json'
  const token = localStorage.getItem('token')
  if (token) headers['Authorization'] = 'Bearer ' + token

  const res = await fetch(BASE + path, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    const err = new Error(data.error || 'Something went wrong')
    err.status = res.status
    throw err
  }
  return data
}

export const api = {
  register: (body) => request('/auth/register', { method: 'POST', body }),
  login: (body) => request('/auth/login', { method: 'POST', body }),
  me: () => request('/auth/me'),

  products: (params) => request('/products?' + new URLSearchParams(params)),
  product: (id) => request('/products/' + id),
  categories: () => request('/categories'),

  cart: () => request('/cart'),
  addToCart: (product_id, quantity) =>
    request('/cart', { method: 'POST', body: { product_id, quantity } }),
  updateCart: (product_id, quantity) =>
    request('/cart/' + product_id, { method: 'PUT', body: { quantity } }),
  removeFromCart: (product_id) => request('/cart/' + product_id, { method: 'DELETE' }),

  placeOrder: (body) => request('/orders', { method: 'POST', body }),
  orders: () => request('/orders'),
  order: (id) => request('/orders/' + id),
}

export function money(cents) {
  return '₹' + (cents / 100).toLocaleString('en-IN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}
