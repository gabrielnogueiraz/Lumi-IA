import { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify'
import { authService } from '../services/authService'
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
}
