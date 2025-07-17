import { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify'
import { authService } from '../services/authService'
import { authMiddleware } from '../middlewares/auth'
import { taskManager } from '../modules/task/taskManager'
import { prisma } from '../prisma/client'
import jwt from 'jsonwebtoken'

export async function debugRoutes(fastify: FastifyInstance) {
  // Endpoint para testar token JWT do Toivo
  fastify.post('/debug/test-toivo-token', async (request, reply) => {
    try {
      const { token } = request.body as { token: string }
      
      if (!token) {
        return reply.status(400).send({
          error: 'Token obrigatório',
          message: 'Forneça o token JWT do Toivo'
        })
      }

      console.log('🧪 DEBUG: Testando token do Toivo')
      console.log('🧪 Token completo:', token)
      
      // Teste 1: Decodificar sem verificar assinatura
      const decoded = jwt.decode(token)
      console.log('🧪 Payload decodificado:', JSON.stringify(decoded, null, 2))
      
      // Teste 2: Verificar com authService da Lumi
      const verified = await authService.verifyToken(token)
      
      if (verified) {
        console.log('✅ Token do Toivo válido na Lumi!')
        return reply.send({
          success: true,
          message: 'Token do Toivo é válido na Lumi!',
          payload: decoded,
          lumiUser: verified
        })
      } else {
        console.log('❌ Token do Toivo inválido na Lumi')
        return reply.status(401).send({
          success: false,
          message: 'Token do Toivo não é válido na Lumi',
          payload: decoded
        })
      }
      
    } catch (error: any) {
      console.error('🧪 DEBUG ERROR:', error)
      return reply.status(500).send({
        error: 'Erro no teste',
        message: error.message,
        details: error.stack
      })
    }
  })

  // Endpoint para gerar token de teste na Lumi
  fastify.post('/debug/generate-lumi-token', async (request, reply) => {
    try {
      const { userId } = request.body as { userId: string }
      
      if (!userId) {
        return reply.status(400).send({
          error: 'userId obrigatório'
        })
      }

      const jwtSecret = process.env.JWT_SECRET || 'fallback-secret-key'
      
      // Gerar token igual ao Toivo
      const tokenPayload = {
        id: userId,  // Usando 'id' como o Toivo
        iat: Math.floor(Date.now() / 1000),
        exp: Math.floor(Date.now() / 1000) + (15 * 60) // 15 minutos
      }
      
      const token = jwt.sign(tokenPayload, jwtSecret, {
        algorithm: 'HS256'
      })
      
      console.log('🧪 DEBUG: Token gerado pela Lumi')
      console.log('🧪 Payload:', JSON.stringify(tokenPayload, null, 2))
      console.log('🧪 Token:', token)
      
      return reply.send({
        success: true,
        token,
        payload: tokenPayload,
        message: 'Token gerado com sucesso pela Lumi'
      })
      
    } catch (error: any) {
      console.error('🧪 DEBUG ERROR:', error)
      return reply.status(500).send({
        error: 'Erro ao gerar token',
        message: error.message
      })
    }
  })

  // Endpoint de teste para validar autenticação (conforme LUMI_IMPLEMENTATION_GUIDE.md)
  fastify.post('/debug/test-auth', {
    preHandler: [async (request: FastifyRequest, reply: FastifyReply) => {
      // Importar middleware dinamicamente para evitar circular dependency
      const { authMiddleware } = await import('../middlewares/auth')
      await authMiddleware(request, reply)
    }]
  }, async (request: FastifyRequest, reply: FastifyReply) => {
    try {
      const user = (request as any).user
      
      console.log('✅ Teste de autenticação bem-sucedido para usuário:', user.id)
      
      return reply.send({
        success: true,
        message: 'Autenticação JWT funcionando perfeitamente!',
        user: {
          id: user.id,
          name: user.name,
          email: user.email
        },
        tokenInfo: {
          algorithm: 'HS256',
          library: 'jsonwebtoken',
          timestamp: new Date().toISOString()
        }
      })
      
    } catch (error: any) {
      console.error('❌ Erro no teste de autenticação:', error)
      
      return reply.status(500).send({
        success: false,
        error: 'Internal Server Error',
        message: 'Erro interno no teste de autenticação'
      })
    }
  })

  // Endpoint para verificar saúde da integração
  fastify.get('/debug/auth-health', async (request: FastifyRequest, reply: FastifyReply) => {
    try {
      return reply.send({
        status: 'healthy',
        auth: {
          jwtSecret: process.env.JWT_SECRET ? 'configured' : 'missing',
          algorithm: 'HS256',
          library: 'jsonwebtoken'
        },
        integration: {
          toivo: 'ready',
          expectedEndpoint: '/api/v1/auth/lumi-token',
          payloadFields: ['userId', 'email', 'name']
        },
        compatibility: {
          acceptsUserId: true,
          acceptsId: true,
          normalizedOutput: 'userId'
        },
        timestamp: new Date().toISOString()
      })
    } catch (error: any) {
      return reply.status(500).send({
        status: 'unhealthy',
        error: error.message,
        timestamp: new Date().toISOString()
      })
    }
  })

  // ===== ROTAS DE DEBUG PARA TAREFAS =====
  
  // Debug: Verificar informações do usuário autenticado
  fastify.get('/debug/user-info', { preHandler: authMiddleware }, async (request, reply) => {
    try {
      const user = (request as any).user
      
      console.log('🔍 [DEBUG] Informações do usuário autenticado:')
      console.log('🔍 [DEBUG] user.id:', user.id)
      console.log('🔍 [DEBUG] user.name:', user.name)
      console.log('🔍 [DEBUG] user.email:', user.email)
      
      return reply.send({
        success: true,
        data: {
          userId: user.id,
          userName: user.name,
          userEmail: user.email,
          timestamp: new Date().toISOString()
        }
      })
    } catch (error: any) {
      console.error('❌ [DEBUG] Erro ao obter informações do usuário:', error)
      return reply.status(500).send({
        error: 'Internal Server Error',
        message: 'Erro ao obter informações do usuário'
      })
    }
  })

  // Debug: Criar tarefa com logs detalhados
  fastify.post('/debug/create-task', { preHandler: authMiddleware }, async (request, reply) => {
    try {
      const user = (request as any).user
      const body = request.body as any
      
      console.log('🔍 [DEBUG] ===== INÍCIO CRIAÇÃO TAREFA DEBUG =====')
      console.log('🔍 [DEBUG] Usuário autenticado:')
      console.log('🔍 [DEBUG] - ID:', user.id)
      console.log('🔍 [DEBUG] - Nome:', user.name)
      console.log('🔍 [DEBUG] - Email:', user.email)
      console.log('🔍 [DEBUG] Dados da tarefa:')
      console.log('🔍 [DEBUG] - Título:', body.title)
      console.log('🔍 [DEBUG] - Prioridade:', body.priority)
      
      // Verificar se o usuário existe no banco
      const userExists = await prisma.user.findUnique({
        where: { id: user.id }
      })
      
      console.log('🔍 [DEBUG] Usuário existe no banco:', !!userExists)
      if (userExists) {
        console.log('🔍 [DEBUG] Nome no banco:', userExists.name)
        console.log('🔍 [DEBUG] Email no banco:', userExists.email)
      }
      
      // Criar tarefa usando TaskManager
      const result = await taskManager.createTask({
        userId: user.id,
        title: body.title || 'Tarefa de Teste DEBUG',
        description: body.description || 'Descrição de teste para debug',
        priority: body.priority || 'MEDIUM',
        pomodoroGoal: body.pomodoroGoal || 1,
        startAt: body.startAt ? new Date(body.startAt) : undefined,
        endAt: body.endAt ? new Date(body.endAt) : undefined
      })
      
      console.log('🔍 [DEBUG] Resultado da criação:', result)
      
      if (result.success) {
        const createdTask = result.data
        console.log('✅ [DEBUG] Tarefa criada com sucesso:')
        console.log('✅ [DEBUG] - ID da tarefa:', createdTask.id)
        console.log('✅ [DEBUG] - userId da tarefa:', createdTask.userId)
        console.log('✅ [DEBUG] - Título:', createdTask.title)
        console.log('✅ [DEBUG] - Coluna ID:', createdTask.columnId)
        
        // Verificar se a tarefa realmente foi salva
        const savedTask = await prisma.tasks.findUnique({
          where: { id: createdTask.id },
          include: {
            columns: {
              include: {
                boards: true
              }
            }
          }
        })
        
        console.log('🔍 [DEBUG] Tarefa encontrada no banco:', !!savedTask)
        if (savedTask) {
          console.log('🔍 [DEBUG] Dados salvos:')
          console.log('🔍 [DEBUG] - ID:', savedTask.id)
          console.log('🔍 [DEBUG] - UserID:', savedTask.userId)
          console.log('🔍 [DEBUG] - Título:', savedTask.title)
          console.log('🔍 [DEBUG] - Quadro:', savedTask.columns.boards.title)
          console.log('🔍 [DEBUG] - Coluna:', savedTask.columns.title)
        }
        
        // Listar todas as tarefas do usuário
        const userTasks = await prisma.tasks.findMany({
          where: { userId: user.id },
          orderBy: { createdAt: 'desc' },
          take: 5
        })
        
        console.log('🔍 [DEBUG] Total de tarefas do usuário:', userTasks.length)
        console.log('🔍 [DEBUG] Últimas 5 tarefas:')
        userTasks.forEach((task, index) => {
          console.log(`🔍 [DEBUG] ${index + 1}. ${task.title} (${task.id.substring(0, 8)}...)`)
        })
      } else {
        console.error('❌ [DEBUG] Falha na criação da tarefa:', result.message)
      }
      
      console.log('🔍 [DEBUG] ===== FIM CRIAÇÃO TAREFA DEBUG =====')
      
      return reply.send({
        success: true,
        data: {
          result,
          userInfo: {
            id: user.id,
            name: user.name,
            email: user.email
          },
          userExists: !!userExists,
          timestamp: new Date().toISOString()
        }
      })
      
    } catch (error: any) {
      console.error('❌ [DEBUG] Erro durante criação de tarefa:', error)
      return reply.status(500).send({
        error: 'Internal Server Error',
        message: 'Erro no debug de criação de tarefa',
        details: error.message
      })
    }
  })

  // Debug: Listar tarefas do usuário
  fastify.get('/debug/list-tasks', { preHandler: authMiddleware }, async (request, reply) => {
    try {
      const user = (request as any).user
      
      console.log('🔍 [DEBUG] ===== LISTAGEM DE TAREFAS DEBUG =====')
      console.log('🔍 [DEBUG] Buscando tarefas para usuário:', user.id)
      
      const tasks = await prisma.tasks.findMany({
        where: { userId: user.id },
        include: {
          columns: {
            include: {
              boards: true
            }
          }
        },
        orderBy: { createdAt: 'desc' }
      })
      
      console.log('🔍 [DEBUG] Total de tarefas encontradas:', tasks.length)
      
      tasks.forEach((task, index) => {
        console.log(`🔍 [DEBUG] ${index + 1}. "${task.title}"`)
        console.log(`🔍 [DEBUG]    - ID: ${task.id}`)
        console.log(`🔍 [DEBUG]    - UserID: ${task.userId}`)
        console.log(`🔍 [DEBUG]    - Quadro: ${task.columns.boards.title}`)
        console.log(`🔍 [DEBUG]    - Coluna: ${task.columns.title}`)
        console.log(`🔍 [DEBUG]    - Concluída: ${task.completed}`)
        console.log(`🔍 [DEBUG]    - Criada em: ${task.createdAt}`)
      })
      
      console.log('🔍 [DEBUG] ===== FIM LISTAGEM DEBUG =====')
      
      return reply.send({
        success: true,
        data: {
          userId: user.id,
          totalTasks: tasks.length,
          tasks: tasks.map(task => ({
            id: task.id,
            title: task.title,
            priority: task.priority,
            completed: task.completed,
            board: task.columns.boards.title,
            column: task.columns.title,
            createdAt: task.createdAt
          }))
        }
      })
      
    } catch (error: any) {
      console.error('❌ [DEBUG] Erro ao listar tarefas:', error)
      return reply.status(500).send({
        error: 'Internal Server Error',
        message: 'Erro no debug de listagem de tarefas',
        details: error.message
      })
    }
  })

  // Debug: Verificar inconsistências no banco
  fastify.get('/debug/check-inconsistencies', { preHandler: authMiddleware }, async (request, reply) => {
    try {
      const user = (request as any).user
      
      console.log('🔍 [DEBUG] ===== VERIFICAÇÃO DE INCONSISTÊNCIAS =====')
      
      // 1. Verificar se há tarefas órfãs (sem usuário válido)
      const orphanTasks = await prisma.tasks.findMany({
        where: {
          NOT: {
            User: {
              id: {
                not: undefined
              }
            }
          }
        }
      })
      
      console.log('🔍 [DEBUG] Tarefas órfãs (sem usuário):', orphanTasks.length)
      
      // 2. Verificar se há tarefas com userId inválido
      const allTasks = await prisma.tasks.findMany({
        include: {
          User: true
        }
      })
      
      const tasksWithInvalidUser = allTasks.filter(task => !task.User)
      console.log('🔍 [DEBUG] Tarefas com userId inválido:', tasksWithInvalidUser.length)
      
      // 3. Verificar tarefas do usuário atual
      const userTasks = allTasks.filter(task => task.userId === user.id)
      console.log('🔍 [DEBUG] Tarefas do usuário atual:', userTasks.length)
      
      // 4. Verificar todos os usuários no sistema
      const allUsers = await prisma.user.findMany({
        select: {
          id: true,
          name: true,
          email: true,
          _count: {
            select: {
              tasks: true
            }
          }
        }
      })
      
      console.log('🔍 [DEBUG] Total de usuários no sistema:', allUsers.length)
      allUsers.forEach(u => {
        console.log(`🔍 [DEBUG] - ${u.name} (${u.id.substring(0, 8)}...): ${u._count.tasks} tarefas`)
      })
      
      console.log('🔍 [DEBUG] ===== FIM VERIFICAÇÃO =====')
      
      return reply.send({
        success: true,
        data: {
          currentUser: {
            id: user.id,
            name: user.name
          },
          orphanTasks: orphanTasks.length,
          tasksWithInvalidUser: tasksWithInvalidUser.length,
          userTasks: userTasks.length,
          totalUsers: allUsers.length,
          userStats: allUsers.map(u => ({
            id: u.id,
            name: u.name,
            email: u.email,
            taskCount: u._count.tasks
          }))
        }
      })
      
    } catch (error: any) {
      console.error('❌ [DEBUG] Erro na verificação:', error)
      return reply.status(500).send({
        error: 'Internal Server Error',
        message: 'Erro na verificação de inconsistências',
        details: error.message
      })
    }
  })
}
