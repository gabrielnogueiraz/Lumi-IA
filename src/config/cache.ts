import NodeCache from 'node-cache'

// Cache para contexto do usuário (5 minutos)
export const userContextCache = new NodeCache({
  stdTTL: 300, // 5 minutos
  checkperiod: 60, // Verifica expiração a cada 1 minuto
  useClones: false
})

// Cache para memórias frequentes (10 minutos)
export const memoryCache = new NodeCache({
  stdTTL: 600, // 10 minutos
  checkperiod: 120, // Verifica expiração a cada 2 minutos
  useClones: false
})

// Cache para insights de produtividade (30 minutos)
export const insightsCache = new NodeCache({
  stdTTL: 1800, // 30 minutos
  checkperiod: 300, // Verifica expiração a cada 5 minutos
  useClones: false
})

// Função para gerar chave de cache
export function generateCacheKey(prefix: string, userId: string, ...params: string[]): string {
  return `${prefix}:${userId}${params.length > 0 ? ':' + params.join(':') : ''}`
}

// Limpa todo o cache
export function clearAllCaches(): void {
  userContextCache.flushAll()
  memoryCache.flushAll()
  insightsCache.flushAll()
  console.log('Todos os caches foram limpos')
}
