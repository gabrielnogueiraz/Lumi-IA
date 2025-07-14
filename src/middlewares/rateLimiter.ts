import { FastifyRequest, FastifyReply } from 'fastify'
import { rateLimiter, strictRateLimiter } from '../config/rateLimiter'

export async function rateLimitMiddleware(
  request: FastifyRequest,
  reply: FastifyReply
) {
  try {
    const key = request.ip
    await rateLimiter.consume(key)
  } catch (rejRes: any) {
    const secs = Math.round(rejRes.msBeforeNext / 1000) || 1
    reply.header('Retry-After', String(secs))
    return reply.status(429).send({
      error: 'Rate limit exceeded',
      message: `Muitas requisições. Tente novamente em ${secs} segundos.`
    })
  }
}

export async function strictRateLimitMiddleware(
  request: FastifyRequest,
  reply: FastifyReply
) {
  try {
    const key = request.ip
    await strictRateLimiter.consume(key)
  } catch (rejRes: any) {
    const secs = Math.round(rejRes.msBeforeNext / 1000) || 1
    reply.header('Retry-After', String(secs))
    return reply.status(429).send({
      error: 'AI rate limit exceeded',
      message: `Limite de requisições para IA excedido. Tente novamente em ${secs} segundos.`
    })
  }
}
