import { FastifyInstance } from 'fastify'
import { authService } from '../../services/authService'
import { authMiddleware, legacyUserIdAuthMiddleware } from '../../middlewares/auth'
import { z } from 'zod'

const validateTokenSchema = z.object({
  token: z.string()
})

export async function authRoutes(fastify: FastifyInstance) {
  
  // Health check específico para autenticação
  fastify.get('/auth/health', async (request, reply) => {
    return {
      status: 'ok',
      service: 'Lumi Auth Service',
      timestamp: new Date().toISOString(),
      jwtConfigured: !!process.env.JWT_SECRET
    }
  })

  // REMOVIDO: Endpoint para gerar token JWT (agora só o Toivo gera tokens)
  // O Lumi apenas valida tokens gerados pelo Toivo

  // Endpoint para validar token JWT
  fastify.post('/auth/validate-token', async (request, reply) => {
    try {
      const { token } = validateTokenSchema.parse(request.body)
      
      const payload = await authService.verifyToken(token)
      
      if (!payload) {
        return reply.status(401).send({
          valid: false,
          error: 'Invalid Token',
          message: 'Token inválido ou expirado'
        })
      }

      const isExpiringSoon = authService.isTokenExpiringSoon(token, 30)

      return reply.send({
        valid: true,
        data: {
          userId: payload.userId,
          email: payload.email,
          name: payload.name,
          expiringSoon: isExpiringSoon
        }
      })

    } catch (error: any) {
      if (error.name === 'ZodError') {
        return reply.status(400).send({
          error: 'Bad Request',
          message: 'Dados inválidos',
          details: error.errors
        })
      }

      request.log.error(error)
      return reply.status(500).send({
        error: 'Internal Server Error',
        message: 'Erro ao validar token'
      })
    }
  })

  // Endpoint protegido para testar autenticação JWT
  fastify.get('/auth/me', { preHandler: authMiddleware }, async (request, reply) => {
    try {
      const user = (request as any).user
      const fullUser = await authService.getUserById(user.id)
      
      if (!fullUser) {
        return reply.status(404).send({
          error: 'User Not Found',
          message: 'Usuário não encontrado'
        })
      }

      return reply.send({
        success: true,
        data: fullUser
      })

    } catch (error: any) {
      request.log.error(error)
      return reply.status(500).send({
        error: 'Internal Server Error',
        message: 'Erro ao buscar dados do usuário'
      })
    }
  })

  // REMOVIDO: Endpoint para refrescar token (o Toivo deve gerenciar renovação de tokens)
  // O Lumi apenas valida tokens gerados pelo Toivo

  // Endpoint legado para compatibilidade (aceita userId direto)
  fastify.get('/auth/me-legacy', { preHandler: legacyUserIdAuthMiddleware }, async (request, reply) => {
    try {
      const user = (request as any).user
      
      return reply.send({
        success: true,
        data: user,
        message: 'Este endpoint é legado. Use JWT tokens em produção.'
      })

    } catch (error: any) {
      request.log.error(error)
      return reply.status(500).send({
        error: 'Internal Server Error',
        message: 'Erro ao buscar dados do usuário'
      })
    }
  })
}
