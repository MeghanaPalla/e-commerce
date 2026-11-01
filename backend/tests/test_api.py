def register(client, name='bob'):
    r = client.post('/api/auth/register', json={
        'username': name, 'email': name + '@x.com', 'password': 'secret1'})
    assert r.status_code == 201
    return {'Authorization': 'Bearer ' + r.get_json()['token']}


def first_product(client):
    return client.get('/api/products').get_json()['items'][0]


def test_product_listing_search_filter_sort_paging(client):
    r = client.get('/api/products').get_json()
    assert r['total'] == 16 and r['pages'] == 2 and len(r['items']) == 8
    assert len(client.get('/api/products?page=2').get_json()['items']) == 8

    r = client.get('/api/products?category=Kitchen').get_json()
    assert r['total'] == 3 and all(p['category'] == 'Kitchen' for p in r['items'])

    r = client.get('/api/products?q=mug').get_json()
    assert [p['name'] for p in r['items']] == ['Ceramic Mug']

    prices = [p['price_cents'] for p in client.get('/api/products?sort=price_asc').get_json()['items']]
    assert prices == sorted(prices)
    prices = [p['price_cents'] for p in client.get('/api/products?sort=price_desc').get_json()['items']]
    assert prices == sorted(prices, reverse=True)

    assert 'Kitchen' in client.get('/api/categories').get_json()


def test_auth(client):
    register(client)
    assert client.post('/api/auth/register', json={
        'username': 'bob', 'email': 'other@x.com', 'password': 'secret1'}).status_code == 409
    assert client.post('/api/auth/register', json={
        'username': 'al', 'email': 'bad', 'password': '1'}).status_code == 400
    assert client.post('/api/auth/login', json={'username': 'bob', 'password': 'nope'}).status_code == 401
    r = client.post('/api/auth/login', json={'username': 'bob', 'password': 'secret1'})
    token = r.get_json()['token']
    me = client.get('/api/auth/me', headers={'Authorization': 'Bearer ' + token})
    assert me.get_json()['user']['username'] == 'bob'
    assert client.get('/api/cart').status_code == 401
    assert client.get('/api/auth/me', headers={'Authorization': 'Bearer junk'}).status_code == 401


def test_cart_and_checkout(client):
    h = register(client)
    p = first_product(client)
    q = client.get('/api/products?q=mug').get_json()['items'][0]

    r = client.post('/api/cart', json={'product_id': p['id'], 'quantity': 2}, headers=h)
    assert r.status_code == 200
    client.post('/api/cart', json={'product_id': q['id']}, headers=h)
    cart = client.get('/api/cart', headers=h).get_json()
    assert cart['count'] == 3
    assert cart['total_cents'] == p['price_cents'] * 2 + q['price_cents']

    assert client.post('/api/cart', json={'product_id': p['id'], 'quantity': 9999}, headers=h).status_code == 400
    assert client.post('/api/cart', json={'product_id': 'bad', 'quantity': 1}, headers=h).status_code == 400

    cart = client.put('/api/cart/' + p['id'], json={'quantity': 3}, headers=h).get_json()
    assert cart['count'] == 4
    cart = client.delete('/api/cart/' + q['id'], headers=h).get_json()
    assert cart['count'] == 3

    # checkout validation
    assert client.post('/api/orders', json={'full_name': '', 'address': ''}, headers=h).status_code == 400
    r = client.post('/api/orders', json={'full_name': 'Bob', 'address': '12 Hill Rd'}, headers=h)
    assert r.status_code == 201
    order = r.get_json()
    assert order['total_cents'] == p['price_cents'] * 3

    # cart is empty, stock went down, order is listed and readable only by its owner
    assert client.get('/api/cart', headers=h).get_json()['count'] == 0
    assert client.get('/api/products/' + p['id']).get_json()['stock'] == p['stock'] - 3
    assert len(client.get('/api/orders', headers=h).get_json()) == 1
    assert client.get('/api/orders/' + order['id'], headers=h).status_code == 200
    h2 = register(client, 'alice')
    assert client.get('/api/orders/' + order['id'], headers=h2).status_code == 404
    assert client.post('/api/orders', json={'full_name': 'A', 'address': 'B'}, headers=h2).status_code == 400
