import fastify from 'fastify'
import cors from '@fastify/cors'
import helmet from '@fastify/helmet'
import websocket from '@fastify/websocket'
import { loggerMiddleware } from './middlewares/logger'
import { rateLimitMiddleware } from './middlewares/rateLimiter'
import { memoryRoutes } from './modules/memory/memoryRoutes'
import { assistantRoutes } from './modules/assistant/assistantRoutes'
import { authRoutes } from './modules/auth/authRoutes'
import { debugRoutes } from './routes/debug'
import { memoryCleanupJob } from './jobs/memoryCleanup'
import { prisma } from './prisma/client'

export async function buildServer() {
  const server = fastify({
    logger: true,
    trustProxy: true
  })

  // Registra plugins de segurança (temporariamente desabilitado para debug CORS)
  // await server.register(helmet, {
  //   contentSecurityPolicy: false,
  // })

  // Configuração CORS simplificada para resolver conflitos
  await server.register(cors, {
    origin: ['http://localhost:5000', 'http://127.0.0.1:5000'],
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization'],
    preflightContinue: false,
    optionsSuccessStatus: 204
  })

  // Registra WebSocket
  await server.register(websocket)

  // Middleware global de logging (temporariamente desabilitado)
  // server.addHook('preHandler', loggerMiddleware)

  // Middleware global de rate limiting (temporariamente desabilitado)
  // server.addHook('preHandler', rateLimitMiddleware)

  // Debug middleware removido - deixando apenas o CORS plugin resolver

  // Health check
  server.get('/health', async (request, reply) => {
    try {
      // Testa conexão com o banco
      await prisma.$queryRaw`SELECT 1`
      
      return {
        status: 'ok',
        timestamp: new Date().toISOString(),
        version: '1.0.0',
        database: 'connected'
      }
    } catch (error) {
      return reply.status(503).send({
        status: 'error',
        timestamp: new Date().toISOString(),
        version: '1.0.0',
        database: 'disconnected',
        error: 'Database connection failed'
      })
    }
  })

  // Endpoint simples para testar CORS
  server.post('/api/test-cors', async (request, reply) => {
    return {
      success: true,
      message: 'CORS funcionando!',
      timestamp: new Date().toISOString(),
      origin: request.headers.origin
    }
  })

  // Registra rotas dos módulos
  server.register(authRoutes, { prefix: '/api' })
  server.register(memoryRoutes, { prefix: '/api' })
  server.register(assistantRoutes, { prefix: '/api' })
  
  // Registra rotas de debug (apenas em desenvolvimento)
  if (process.env.NODE_ENV === 'development') {
    server.register(debugRoutes, { prefix: '/api' })
  }

  // WebSocket para comunicação em tempo real
  server.register(async function (fastify) {
    fastify.get('/ws', { websocket: true }, async (connection, req) => {
      console.log('Nova conexão WebSocket estabelecida')
      
      connection.on('message', async (message: any) => {
        try {
          const data = JSON.parse(message.toString())
          
          // Aqui você pode implementar diferentes tipos de mensagens
          // Por exemplo: status updates, notificações, etc.
          
          connection.send(JSON.stringify({
            type: 'ack',
            message: 'Mensagem recebida',
            timestamp: new Date().toISOString()
          }))
        } catch (error) {
          connection.send(JSON.stringify({
            type: 'error',
            message: 'Formato de mensagem inválido',
            timestamp: new Date().toISOString()
          }))
        }
      })

      connection.on('close', () => {
        console.log('Conexão WebSocket fechada')
      })

      // Envia mensagem de boas-vindas
      connection.send(JSON.stringify({
        type: 'welcome',
        message: 'Conectado ao servidor Lumi',
        timestamp: new Date().toISOString()
      }))
    })
  })

  // Inicia job de limpeza de memórias
  memoryCleanupJob.start()

  // Graceful shutdown
  const gracefulShutdown = async (signal: string) => {
    console.log(`Recebido sinal ${signal}, iniciando shutdown graceful...`)
    
    memoryCleanupJob.stop()
    await prisma.$disconnect()
    await server.close()
    
    console.log('Servidor fechado com sucesso')
    process.exit(0)
  }

  process.on('SIGTERM', () => gracefulShutdown('SIGTERM'))
  process.on('SIGINT', () => gracefulShutdown('SIGINT'))

  return server
}
