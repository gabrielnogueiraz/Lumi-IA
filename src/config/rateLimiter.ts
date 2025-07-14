import { RateLimiterMemory } from 'rate-limiter-flexible'

export const rateLimiter = new RateLimiterMemory({
  points: 20, // Número de requests
  duration: 60, // Por minuto
  blockDuration: 60, // Block por 1 minuto se exceder
})

export const strictRateLimiter = new RateLimiterMemory({
  points: 5, // Apenas 5 requests para IA
  duration: 60, // Por minuto
  blockDuration: 120, // Block por 2 minutos se exceder
})
