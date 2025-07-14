import { FastifyRequest, FastifyReply } from 'fastify'

/**
 * Middleware para mapear tipos de memória para garantir compatibilidade
 * Converte tipos similares automaticamente
 */
export async function memoryTypeMapperMiddleware(
  request: FastifyRequest,
  reply: FastifyReply
) {
  // Aplica apenas para rotas de memória
  if (!request.url.includes('/api/memories')) {
    return
  }

  // Aplica apenas para métodos que enviam dados
  if (request.method !== 'POST' && request.method !== 'PUT' && request.method !== 'PATCH') {
    return
  }

  const body = request.body as any

  if (body && body.type) {
    // Mapeamento de tipos similares para compatibilidade
    const typeMapping: Record<string, string> = {
      'PERSONAL_CONTEXT': 'PERSONAL_CONTEXT', // Já existe agora
      'PERSONAL_DATA': 'PERSONAL_INFO',
      'PERSONAL': 'PERSONAL_INFO',
      'WORK': 'WORK_CONTEXT',
      'STUDY': 'STUDY_CONTEXT',
      'EMOTION': 'EMOTIONAL_STATE',
      'COMMUNICATION': 'COMMUNICATION_STYLE',
      'GOAL': 'GOALS_PROJECTS',
      'PROJECT': 'GOALS_PROJECTS',
      'PREFERENCE': 'PREFERENCES',
      'DATE': 'IMPORTANT_DATES',
      'PRODUCTIVITY': 'PRODUCTIVITY_PATTERN'
    }

    // Se o tipo não é válido, tenta mapear
    const originalType = body.type.toString().toUpperCase()
    if (typeMapping[originalType]) {
      body.type = typeMapping[originalType]
      console.log(`🔄 Memory type mapped: ${originalType} → ${body.type}`)
    }
  }
}
