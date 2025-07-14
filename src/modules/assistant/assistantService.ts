import { UserService } from '../user/userService'
import { TaskService } from '../task/taskService'
import { TaskAssistant } from '../task/taskAssistant'
import { MemoryService } from '../memory/memoryService'
import { UserContext, EmotionalAnalysis, LumiResponse, TaskResponse } from '../../types'
import { analyzeEmotion } from '../../utils/emotionAnalyzer'
import { buildLumiPrompt, extractMemoryFromResponse } from '../../utils/promptBuilder'
import { prioritizeMemories } from '../../utils/helpers'

export class AssistantService {
  private userService: UserService
  private taskService: TaskService
  private taskAssistant: TaskAssistant
  private memoryService: MemoryService

  constructor() {
    this.userService = new UserService()
    this.taskService = new TaskService()
    this.taskAssistant = new TaskAssistant()
    this.memoryService = new MemoryService()
  }

  async buildUserContext(userId: string): Promise<UserContext> {
    // Busca dados do usuário
    const user = await this.userService.findById(userId)
    if (!user) {
      throw new Error('Usuário não encontrado')
    }

    // Busca memórias recentes
    const allMemories = await this.memoryService.findRecentMemories(userId, 20)
    const recentMemories = allMemories.map(memory => ({
      id: memory.id,
      type: memory.type.toString(),
      content: memory.content,
      importance: memory.importance.toString(),
      emotionalContext: memory.emotionalContext || undefined,
      productivityPattern: memory.productivityPattern || undefined,
      communicationStyle: memory.communicationStyle || undefined,
      createdAt: memory.createdAt,
      tags: memory.tags
    }))

    // Busca tarefas atuais
    const currentTasks = await this.taskService.findPendingTasks(userId)
    const formattedTasks = currentTasks.slice(0, 10).map(task => ({
      id: task.id,
      title: task.title,
      description: task.description || undefined,
      priority: task.priority as 'HIGH' | 'MEDIUM' | 'LOW',
      completed: task.completed,
      startAt: task.startAt || undefined,
      endAt: task.endAt || undefined
    }))

    // Busca insights de produtividade
    const productivityInsights = await this.memoryService.getProductivityPatterns(userId)

    return {
      user: {
        id: user.id,
        name: user.name,
        email: user.email
      },
      recentMemories,
      currentTasks: formattedTasks,
      productivityInsights
    }
  }

  async analyzeUserMessage(message: string, context: UserContext): Promise<{
    emotionalAnalysis: EmotionalAnalysis
    prioritizedMemories: any[]
    prompt: string
    taskResponse?: TaskResponse
  }> {
    // Analisa emoção da mensagem
    const emotionalAnalysis = analyzeEmotion(message)

    // Verifica se é uma solicitação relacionada a tarefas
    const taskResponse = await this.taskAssistant.processTaskRequest(
      context.user.id,
      message,
      context.user.name
    )

    // Se foi processada como tarefa e foi bem-sucedida, retorna resposta específica
    if (taskResponse.success) {
      return {
        emotionalAnalysis,
        prioritizedMemories: [],
        prompt: '', // Prompt vazio pois a resposta já está pronta
        taskResponse
      }
    }

    // Continua com o fluxo normal se não foi uma tarefa
    const prioritizedMemories = prioritizeMemories(context.recentMemories, message)

    const prompt = buildLumiPrompt(message, {
      ...context,
      recentMemories: prioritizedMemories.slice(0, 8)
    }, emotionalAnalysis)

    return {
      emotionalAnalysis,
      prioritizedMemories,
      prompt,
      taskResponse: taskResponse.success ? taskResponse : undefined
    }
  }

  async extractAndSaveMemories(
    userId: string,
    userMessage: string,
    aiResponse: string,
    emotionalAnalysis: EmotionalAnalysis
  ): Promise<void> {
    const extractedInfo = extractMemoryFromResponse(aiResponse, userMessage)
    
    // Salva informações importantes detectadas na conversa
    for (const info of extractedInfo) {
      if (info.length > 5) { // Só salva se tem informação útil
        await this.memoryService.create({
          userId,
          type: this.determineMemoryType(info, userMessage),
          content: info,
          importance: 'MEDIUM',
          emotionalContext: emotionalAnalysis.detectedMood !== 'neutral' 
            ? `Usuário estava ${emotionalAnalysis.detectedMood}` 
            : undefined,
          tags: [emotionalAnalysis.detectedMood, 'conversation']
        })
      }
    }

    // Atualiza padrão de comunicação se necessário
    if (emotionalAnalysis.confidence > 0.7) {
      await this.updateCommunicationPattern(userId, emotionalAnalysis)
    }
  }

  private determineMemoryType(info: string, userMessage: string): any {
    const lowerInfo = info.toLowerCase()
    const lowerMessage = userMessage.toLowerCase()

    if (lowerInfo.includes('trabalho') || lowerInfo.includes('empresa') || lowerInfo.includes('cargo')) {
      return 'WORK_CONTEXT'
    }
    if (lowerInfo.includes('estudo') || lowerInfo.includes('curso') || lowerInfo.includes('faculdade')) {
      return 'STUDY_CONTEXT'
    }
    if (lowerInfo.includes('projeto') || lowerInfo.includes('meta') || lowerInfo.includes('objetivo')) {
      return 'GOALS_PROJECTS'
    }
    if (lowerInfo.includes('gosto') || lowerInfo.includes('prefiro') || lowerInfo.includes('odeio')) {
      return 'PREFERENCES'
    }
    if (lowerMessage.includes('sempre') || lowerMessage.includes('geralmente') || lowerMessage.includes('costumo')) {
      return 'PRODUCTIVITY_PATTERN'
    }

    return 'PERSONAL_INFO'
  }

  private async updateCommunicationPattern(
    userId: string,
    emotionalAnalysis: EmotionalAnalysis
  ): Promise<void> {
    const existingPatterns = await this.memoryService.findByType(userId, 'COMMUNICATION_STYLE')
    
    let communicationStyle = ''
    switch (emotionalAnalysis.responseStrategy) {
      case 'support':
        communicationStyle = 'Prefere suporte emocional e encorajamento'
        break
      case 'calm':
        communicationStyle = 'Responde bem a abordagem calma e tranquila'
        break
      case 'energize':
        communicationStyle = 'Se motiva com energia e entusiasmo'
        break
      case 'encourage':
        communicationStyle = 'Gosta de reconhecimento e incentivo'
        break
      case 'motivate':
        communicationStyle = 'Prefere motivação equilibrada'
        break
    }

    if (existingPatterns.length === 0) {
      await this.memoryService.create({
        userId,
        type: 'COMMUNICATION_STYLE',
        content: communicationStyle,
        importance: 'HIGH',
        communicationStyle: emotionalAnalysis.responseStrategy,
        tags: ['communication', 'pattern']
      })
    } else {
      // Atualiza o padrão existente
      const latest = existingPatterns[0]
      await this.memoryService.update(latest.id, {
        content: communicationStyle,
        communicationStyle: emotionalAnalysis.responseStrategy
      })
    }
  }

  async getTaskSuggestions(userId: string, emotionalAnalysis: EmotionalAnalysis): Promise<string[]> {
    const taskSummary = await this.taskService.getTaskSummary(userId)
    const suggestions: string[] = []

    // Sugestões baseadas no estado emocional
    switch (emotionalAnalysis.responseStrategy) {
      case 'support':
        if (taskSummary.pending > 0) {
          suggestions.push('Que tal começar com uma tarefa pequena e fácil hoje?')
        }
        suggestions.push('Lembre-se de fazer pausas regulares')
        break

      case 'calm':
        if (taskSummary.overdue > 0) {
          suggestions.push('Vamos reorganizar suas prioridades para reduzir o estresse')
        }
        suggestions.push('Considere usar técnicas de respiração entre as tarefas')
        break

      case 'energize':
        if (taskSummary.highPriority > 0) {
          suggestions.push('Aproveite essa energia para tacklear uma tarefa de alta prioridade!')
        }
        suggestions.push('Este é um bom momento para projetos desafiadores')
        break

      case 'encourage':
        if (taskSummary.completed > taskSummary.pending) {
          suggestions.push('Você está indo muito bem! Continue assim')
        }
        suggestions.push('Mantenha o foco, você consegue!')
        break

      case 'motivate':
        if (taskSummary.today > 0) {
          suggestions.push('Você tem tarefas para hoje. Vamos começar?')
        }
        break
    }

    return suggestions
  }
}
