import { FastifyInstance } from 'fastify'
import { TaskAssistant } from './taskAssistant'
import { TaskService } from './taskService'
import { authMiddleware } from '../../middlewares/auth'
import { rateLimitMiddleware } from '../../middlewares/rateLimiter'
import { z } from 'zod'

const taskMessageSchema = z.object({
  message: z.string().min(1).max(1000)
})

export async function taskRoutes(fastify: FastifyInstance) {
  const taskAssistant = new TaskAssistant()
  const taskService = new TaskService()

  fastify.addHook('preHandler', authMiddleware)
  fastify.addHook('preHandler', rateLimitMiddleware)

  // Endpoint para processar comandos de tarefa diretamente
  fastify.post('/process', async (request, reply) => {
    try {
      const user = (request as any).user
      const body = taskMessageSchema.parse(request.body)
      
      const result = await taskAssistant.processTaskRequest(
        user.id,
        body.message,
        user.name
      )

      return reply.send({
        success: true,
        data: result
      })

    } catch (error: any) {
      request.log.error(error)
      
      if (error.name === 'ZodError') {
        return reply.status(400).send({
          error: 'Bad Request',
          message: 'Dados de entrada inválidos',
          details: error.errors
        })
      }

      return reply.status(500).send({
        error: 'Internal Server Error',
        message: 'Erro ao processar comando de tarefa'
      })
    }
  })

  // Endpoint para listar tarefas do usuário
  fastify.get('/list', async (request, reply) => {
    try {
      const user = (request as any).user
      
      const tasks = await taskService.findPendingTasks(user.id)
      const summary = await taskService.getTaskSummary(user.id)

      return reply.send({
        success: true,
        data: {
          tasks: tasks.slice(0, 10).map(task => ({
            id: task.id,
            title: task.title,
            description: task.description,
            priority: task.priority,
            startAt: task.startAt,
            endAt: task.endAt,
            completed: task.completed
          })),
          summary
        }
      })

    } catch (error: any) {
      request.log.error(error)
      return reply.status(500).send({
        error: 'Internal Server Error',
        message: 'Erro ao buscar tarefas'
      })
    }
  })

  // Endpoint para obter resumo das tarefas
  fastify.get('/summary', async (request, reply) => {
    try {
      const user = (request as any).user
      const summary = await taskService.getTaskSummary(user.id)

      return reply.send({
        success: true,
        data: summary
      })

    } catch (error: any) {
      request.log.error(error)
      return reply.status(500).send({
        error: 'Internal Server Error',
        message: 'Erro ao buscar resumo das tarefas'
      })
    }
  })
}
