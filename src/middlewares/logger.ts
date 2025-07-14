import { FastifyRequest, FastifyReply } from 'fastify'

export async function loggerMiddleware(
  request: FastifyRequest,
  reply: FastifyReply
) {
  const start = Date.now()
  
  // Log da requisição
  console.log(`[${new Date().toISOString()}] ${request.method} ${request.url} - ${request.ip}`)
  
  // Calcula duração na resposta
  request.log.info({ url: request.url, method: request.method, ip: request.ip }, 'Request started')
  
  const originalSend = reply.send.bind(reply)
  reply.send = function(payload: any) {
    const duration = Date.now() - start
    const user = (request as any).user
    
    console.log(
      `[${new Date().toISOString()}] ${request.method} ${request.url} - ${reply.statusCode} - ${duration}ms${
        user ? ` - User: ${user.name}` : ''
      }`
    )
    
    return originalSend(payload)
  }
}
