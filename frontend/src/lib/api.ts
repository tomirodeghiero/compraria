import axios from 'axios'

export type ProductoInput = {
  nombre: string
  cantidad?: number
}

export type ListaComprasInput = {
  productos: ProductoInput[]
  max_supermercados?: number
}

const getApiBase = () => {
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
}

export async function optimizarLista(payload: ListaComprasInput) {
  const base = getApiBase()
  const url = `${base.replace(/\/$/, '')}/api/optimizar`
  const resp = await axios.post(url, payload, {
    headers: { 'Content-Type': 'application/json' },
    timeout: 120000,
  })
  return resp.data
}

export async function healthCheck() {
  const base = getApiBase()
  const url = `${base.replace(/\/$/, '')}/`
  const resp = await axios.get(url, { timeout: 5000 })
  return resp.data
}

export default { optimizarLista, healthCheck }
