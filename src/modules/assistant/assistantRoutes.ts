import { FastifyInstance } from 'fastify'
import { AssistantService } from './assistantService'
import { askRequestSchema } from '../../types'
import { authMiddleware } from '../../middlewares/auth'
import { strictRateLimitMiddleware } from '../../middlewares/rateLimiter'
import { groq, GROQ_MODEL, MAX_TOKENS, TEMPERATURE } from '../../config/groq'
import { getEmotionalTone } from '../../utils/emotionAnalyzer'

export async function assistantRoutes(fastify: FastifyInstance) {
  const assistantService = new AssistantService()

  // Middleware de autenticação e rate limiting para todas as rotas
  fastify.addHook('preHandler', authMiddleware)
  fastify.addHook('preHandler', strictRateLimitMiddleware)

  // Endpoint principal para conversar com a Lumi
  fastify.post('/ask', async (request, reply) => {
    try {
      const user = (request as any).user
      const body = askRequestSchema.parse(request.body)
      
      // Constrói contexto do usuário
      const userContext = await assistantService.buildUserContext(user.id)
      
      // Analisa a mensagem do usuário
      const {
        emotionalAnalysis,
        prioritizedMemories,
        prompt,
        taskResponse
      } = await assistantService.analyzeUserMessage(body.message, userContext)

      // Se foi uma resposta de tarefa, retorna ela diretamente
      if (taskResponse && taskResponse.success) {
        reply.type('text/plain; charset=utf-8')
        reply.header('Cache-Control', 'no-cache')
        reply.header('Connection', 'keep-alive')
        
        let fullMessage = taskResponse.message
        if (taskResponse.suggestionsMessage) {
          fullMessage += '\n\n' + taskResponse.suggestionsMessage
        }
        
        reply.raw.write(fullMessage)
        reply.raw.end()
        return
      }

      // Busca sugestões baseadas no estado emocional
      const suggestions = await assistantService.getTaskSuggestions(user.id, emotionalAnalysis)

      // Prepara as mensagens para a IA
      const messages = [
        {
          role: 'system' as const,
          content: prompt
        },
        {
          role: 'user' as const,
          content: body.message
        }
      ]

      // Inicia streaming da resposta
      reply.type('text/plain; charset=utf-8')
      reply.header('Cache-Control', 'no-cache')
      reply.header('Connection', 'keep-alive')

      const chatCompletion = await groq.chat.completions.create({
        model: GROQ_MODEL,
        messages,
        stream: true,
        temperature: TEMPERATURE,
        max_tokens: MAX_TOKENS
      })

      let fullResponse = ''

      for await (const chunk of chatCompletion) {
        const content = chunk.choices[0]?.delta?.content || ''
        if (content) {
          fullResponse += content
          reply.raw.write(content)
        }
      }

      reply.raw.end()

      // Após o streaming, processa e salva as memórias em background
      setImmediate(async () => {
        try {
          await assistantService.extractAndSaveMemories(
            user.id,
            body.message,
            fullResponse,
            emotionalAnalysis
          )
        } catch (error) {
          console.error('Erro ao salvar memórias:', error)
        }
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
        message: 'Erro ao processar sua mensagem. Tente novamente.'
      })
    }
  })

  // Endpoint para resposta JSON completa (sem streaming)
  fastify.post('/ask-json', async (request, reply) => {
    try {
      const user = (request as any).user
      const body = askRequestSchema.parse(request.body)
      
      // Constrói contexto do usuário
      const userContext = await assistantService.buildUserContext(user.id)
      
      // Analisa a mensagem do usuário
      const {
        emotionalAnalysis,
        prioritizedMemories,
        prompt,
        taskResponse
      } = await assistantService.analyzeUserMessage(body.message, userContext)

      // Se foi uma resposta de tarefa, retorna ela estruturada
      if (taskResponse && taskResponse.success) {
        let fullMessage = taskResponse.message
        if (taskResponse.suggestionsMessage) {
          fullMessage += '\n\n' + taskResponse.suggestionsMessage
        }

        return reply.send({
          success: true,
          data: {
            message: fullMessage,
            emotionalTone: getEmotionalTone(emotionalAnalysis.responseStrategy),
            taskAction: taskResponse.taskAction,
            conflictDetected: taskResponse.conflictDetected,
            context: {
              detectedMood: emotionalAnalysis.detectedMood,
              confidence: emotionalAnalysis.confidence,
              strategy: emotionalAnalysis.responseStrategy,
              isTaskResponse: true
            }
          }
        })
      }

      // Busca sugestões baseadas no estado emocional
      const suggestions = await assistantService.getTaskSuggestions(user.id, emotionalAnalysis)

      // Prepara as mensagens para a IA
      const messages = [
        {
          role: 'system' as const,
          content: prompt
        },
        {
          role: 'user' as const,
          content: body.message
        }
      ]

      // Faz a requisição sem streaming
      const chatCompletion = await groq.chat.completions.create({
        model: GROQ_MODEL,
        messages,
        stream: false,
        temperature: TEMPERATURE,
        max_tokens: MAX_TOKENS
      })

      const aiResponse = chatCompletion.choices[0]?.message?.content || 'Desculpe, não consegui processar sua mensagem.'

      // Processa e salva as memórias
      await assistantService.extractAndSaveMemories(
        user.id,
        body.message,
        aiResponse,
        emotionalAnalysis
      )

      // Retorna resposta estruturada
      return reply.send({
        success: true,
        data: {
          message: aiResponse,
          emotionalTone: getEmotionalTone(emotionalAnalysis.responseStrategy),
          suggestions,
          context: {
            detectedMood: emotionalAnalysis.detectedMood,
            confidence: emotionalAnalysis.confidence,
            strategy: emotionalAnalysis.responseStrategy
          }
        }
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
        message: 'Erro ao processar sua mensagem. Tente novamente.'
      })
    }
  })

  // Endpoint para buscar contexto do usuário
  fastify.get('/context', async (request, reply) => {
    try {
      const user = (request as any).user
      const context = await assistantService.buildUserContext(user.id)
      
      return reply.send({
        success: true,
        data: context
      })
    } catch (error: any) {
      request.log.error(error)
      return reply.status(500).send({
        error: 'Internal Server Error',
        message: 'Erro ao buscar contexto do usuário'
      })
    }
  })
}
