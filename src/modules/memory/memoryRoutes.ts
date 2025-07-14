import { FastifyInstance } from 'fastify'
import { MemoryService } from './memoryService'
import { memoryCreateSchema, memoryUpdateSchema, memoryQuerySchema } from '../../types'
import { authMiddleware } from '../../middlewares/auth'
import { memoryTypeMapperMiddleware } from '../../middlewares/memoryTypeMapper'

export async function memoryRoutes(fastify: FastifyInstance) {
  const memoryService = new MemoryService()

  // Middleware de autenticação para todas as rotas
  fastify.addHook('preHandler', authMiddleware)
  
  // Middleware de mapeamento de tipos para compatibilidade
  fastify.addHook('preHandler', memoryTypeMapperMiddleware)

  // Criar nova memória
  fastify.post('/memories', async (request, reply) => {
    try {
      const data = memoryCreateSchema.parse(request.body)
      const memory = await memoryService.create(data)
      
      return reply.status(201).send({
        success: true,
        data: memory
      })
    } catch (error: any) {
      request.log.error(error)
      return reply.status(400).send({
        error: 'Bad Request',
        message: error.message || 'Dados inválidos'
      })
    }
  })

  // Buscar memórias do usuário
  fastify.get('/memories', async (request, reply) => {
    try {
      const user = (request as any).user
      const queryParams = request.query as any
      
      const query = memoryQuerySchema.parse({
        userId: user.id,
        type: queryParams.type,
        importance: queryParams.importance,
        tags: queryParams.tags,
        limit: queryParams.limit ? parseInt(queryParams.limit) : undefined,
        offset: queryParams.offset ? parseInt(queryParams.offset) : undefined
      })
      
      const memories = await memoryService.findByUserId(query)
      
      return reply.send({
        success: true,
        data: memories,
        total: memories.length
      })
    } catch (error: any) {
      request.log.error(error)
      return reply.status(400).send({
        error: 'Bad Request',
        message: error.message || 'Parâmetros inválidos'
      })
    }
  })

  // Buscar memórias recentes
  fastify.get('/memories/recent', async (request, reply) => {
    try {
      const user = (request as any).user
      const { limit = 10 } = request.query as { limit?: number }
      
      const memories = await memoryService.findRecentMemories(user.id, limit)
      
      return reply.send({
        success: true,
        data: memories
      })
    } catch (error: any) {
      request.log.error(error)
      return reply.status(500).send({
        error: 'Internal Server Error',
        message: 'Erro ao buscar memórias'
      })
    }
  })

  // Buscar insights de produtividade
  fastify.get('/memories/productivity-insights', async (request, reply) => {
    try {
      const user = (request as any).user
      const insights = await memoryService.getProductivityPatterns(user.id)
      
      return reply.send({
        success: true,
        data: insights
      })
    } catch (error: any) {
      request.log.error(error)
      return reply.status(500).send({
        error: 'Internal Server Error',
        message: 'Erro ao buscar insights'
      })
    }
  })

  // Atualizar memória
  fastify.put('/memories/:id', async (request, reply) => {
    try {
      const { id } = request.params as { id: string }
      const bodyData = request.body as any
      const data = memoryUpdateSchema.parse({
        id,
        userId: bodyData.userId,
        type: bodyData.type,
        content: bodyData.content,
        importance: bodyData.importance,
        emotionalContext: bodyData.emotionalContext,
        productivityPattern: bodyData.productivityPattern,
        communicationStyle: bodyData.communicationStyle,
        tags: bodyData.tags,
        expiresAt: bodyData.expiresAt
      })
      
      const memory = await memoryService.update(id, data)
      
      return reply.send({
        success: true,
        data: memory
      })
    } catch (error: any) {
      request.log.error(error)
      return reply.status(400).send({
        error: 'Bad Request',
        message: error.message || 'Dados inválidos'
      })
    }
  })

  // Deletar memória
  fastify.delete('/memories/:id', async (request, reply) => {
    try {
      const { id } = request.params as { id: string }
      await memoryService.delete(id)
      
      return reply.status(204).send()
    } catch (error: any) {
      request.log.error(error)
      return reply.status(500).send({
        error: 'Internal Server Error',
        message: 'Erro ao deletar memória'
      })
    }
  })

  // Buscar por conteúdo
  fastify.get('/memories/search', async (request, reply) => {
    try {
      const user = (request as any).user
      const { q } = request.query as { q: string }
      
      if (!q || q.trim().length < 2) {
        return reply.status(400).send({
          error: 'Bad Request',
          message: 'Termo de busca deve ter pelo menos 2 caracteres'
        })
      }
      
      const memories = await memoryService.searchByContent(user.id, q.trim())
      
      return reply.send({
        success: true,
        data: memories
      })
    } catch (error: any) {
      request.log.error(error)
      return reply.status(500).send({
        error: 'Internal Server Error',
        message: 'Erro na busca'
      })
    }
  })
}
