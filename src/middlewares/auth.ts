import { FastifyRequest, FastifyReply } from 'fastify'
import { authService } from '../services/authService'

export async function authMiddleware(
  request: FastifyRequest,
  reply: FastifyReply
) {
  try {
    console.log('🔍 AuthMiddleware: Iniciando verificação de autenticação')
    const authHeader = request.headers.authorization
    console.log('🔍 AuthMiddleware: Authorization header presente:', !!authHeader)
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      console.log('❌ AuthMiddleware: Header Authorization ausente ou malformado')
      return reply.status(401).send({
        error: 'Unauthorized',
        message: 'Token de acesso necessário'
      })
    }

    const token = authHeader.replace('Bearer ', '')
    console.log('🔍 AuthMiddleware: Token extraído (primeiros 50 chars):', token.substring(0, 50) + '...')

    // Verifica o token JWT
    const payload = await authService.verifyToken(token)

    if (!payload) {
      console.log('❌ AuthMiddleware: Token inválido ou expirado')
      return reply.status(401).send({
        error: 'Unauthorized',
        message: 'Token inválido ou expirado'
      })
    }

    console.log('✅ AuthMiddleware: Autenticação bem-sucedida para usuário:', payload.userId)
    
    // Adiciona o usuário ao request
    ;(request as any).user = {
      id: payload.userId,  // Agora garantimos que payload.userId estará sempre definido
      name: payload.name,
      email: payload.email
    }

    // Atualiza lastCheckIn em background (não bloqueia a requisição)
    setImmediate(() => {
      if (payload.userId) {
        authService.updateLastCheckIn(payload.userId).catch(err => {
          console.warn('Erro ao atualizar lastCheckIn:', err)
        })
      }
    })

  } catch (error) {
    console.error('Erro no middleware de autenticação:', error)
    return reply.status(500).send({
      error: 'Internal Server Error',
      message: 'Erro ao verificar autenticação'
    })
  }
}

export async function optionalAuthMiddleware(
  request: FastifyRequest,
  reply: FastifyReply
) {
  try {
    const authHeader = request.headers.authorization
    
    if (authHeader && authHeader.startsWith('Bearer ')) {
      const token = authHeader.replace('Bearer ', '')
      
      const payload = await authService.verifyToken(token)

      if (payload) {
        ;(request as any).user = {
          id: payload.userId,
          name: payload.name,
          email: payload.email
        }
      }
    }
  } catch (error) {
    // Em caso de erro, apenas continue sem autenticação
    console.warn('Optional auth middleware error:', error)
  }
}

/**
 * Middleware específico para autenticação via User ID (compatibilidade)
 * Use apenas para testes ou desenvolvimento
 */
export async function legacyUserIdAuthMiddleware(
  request: FastifyRequest,
  reply: FastifyReply
) {
  try {
    const authHeader = request.headers.authorization
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return reply.status(401).send({
        error: 'Unauthorized',
        message: 'Token de acesso necessário'
      })
    }

    const userIdOrToken = authHeader.replace('Bearer ', '')

    // Se parecer um JWT (contém pontos), tenta verificar como JWT
    if (userIdOrToken.includes('.')) {
      const payload = await authService.verifyToken(userIdOrToken)
      if (payload) {
        ;(request as any).user = {
          id: payload.userId,
          name: payload.name,
          email: payload.email
        }
        return
      }
    }

    // Caso contrário, trata como userId legado
    const user = await authService.getUserById(userIdOrToken)

    if (!user) {
      return reply.status(401).send({
        error: 'Unauthorized',
        message: 'Usuário não encontrado'
      })
    }

    ;(request as any).user = {
      id: user.id,
      name: user.name,
      email: user.email
    }

  } catch (error) {
    console.error('Erro no middleware de autenticação legado:', error)
    return reply.status(500).send({
      error: 'Internal Server Error',
      message: 'Erro ao verificar autenticação'
    })
  }
}
