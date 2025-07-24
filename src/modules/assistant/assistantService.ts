import { UserService } from '../user/userService'
import { TaskService } from '../task/taskService'
import { TaskAssistant } from '../task/taskAssistant'
import { MemoryService } from '../memory/memoryService'
import { UserContext, EmotionalAnalysis, TaskResponse } from '../../types'
import { analyzeEmotion, analyzeEmotionWithContext } from '../../utils/emotionAnalyzer'
import { buildLumiPrompt, extractMemoryFromResponse } from '../../utils/promptBuilder'
import { prioritizeMemories } from '../../utils/helpers'
import { conversationContextService } from '../../services/conversationContextService'

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

    // Busca todas as tarefas do usuário
    const allTasks = await this.taskService.findPendingTasks(userId)
    
    // 🚨 CORREÇÃO CRÍTICA: Filtragem de data mais precisa
    const now = new Date()
    
    // Garante que estamos comparando apenas a data, não horário
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    const tomorrow = new Date(today.getTime() + 24 * 60 * 60 * 1000)
    
    console.log('🔍 DEBUG - Data atual:', today.toISOString().split('T')[0])
    
    // Tarefas de hoje (filtro mais rigoroso)
    const todayTasks = allTasks.filter(task => {
      if (!task.startAt) return false
      
      const taskDate = new Date(task.startAt)
      const taskDateOnly = new Date(taskDate.getFullYear(), taskDate.getMonth(), taskDate.getDate())
      
      console.log('🔍 DEBUG - Comparando tarefa:', task.title, 'Data:', taskDateOnly.toISOString().split('T')[0])
      
      return taskDateOnly.getTime() === today.getTime()
    }).map(task => ({
      id: task.id,
      title: task.title,
      description: task.description || undefined,
      priority: task.priority as 'HIGH' | 'MEDIUM' | 'LOW',
      completed: task.completed,
      startAt: task.startAt || undefined,
      endAt: task.endAt || undefined
    }))

    // Tarefas atrasadas (antes de hoje)
    const overdueTasks = allTasks.filter(task => {
      if (!task.startAt || task.completed) return false
      
      const taskDate = new Date(task.startAt)
      const taskDateOnly = new Date(taskDate.getFullYear(), taskDate.getMonth(), taskDate.getDate())
      
      return taskDateOnly.getTime() < today.getTime()
    }).map(task => {
      const taskDate = new Date(task.startAt!)
      const taskDateOnly = new Date(taskDate.getFullYear(), taskDate.getMonth(), taskDate.getDate())
      const daysOverdue = Math.floor((today.getTime() - taskDateOnly.getTime()) / (1000 * 60 * 60 * 24))
      
      return {
        id: task.id,
        title: task.title,
        description: task.description || undefined,
        priority: task.priority as 'HIGH' | 'MEDIUM' | 'LOW',
        daysOverdue,
        startAt: task.startAt || undefined
      }
    })

    // Tarefas futuras (após hoje)
    const futureTasks = allTasks.filter(task => {
      if (!task.startAt || task.completed) return false
      
      const taskDate = new Date(task.startAt)
      const taskDateOnly = new Date(taskDate.getFullYear(), taskDate.getMonth(), taskDate.getDate())
      
      return taskDateOnly.getTime() > today.getTime()
    }).map(task => ({
      id: task.id,
      title: task.title,
      description: task.description || undefined,
      priority: task.priority as 'HIGH' | 'MEDIUM' | 'LOW',
      completed: task.completed,
      startAt: task.startAt || undefined,
      endAt: task.endAt || undefined
    }))

    // Todas as tarefas (para compatibilidade)
    const currentTasks = [...todayTasks, ...futureTasks].slice(0, 15)

    // Busca insights de produtividade
    const productivityInsights = await this.memoryService.getProductivityPatterns(userId)

    // Incluir contexto de conversa
    const conversationContext = conversationContextService.getOrCreateContext(userId)

    console.log('🔍 DEBUG - Tarefas de hoje:', todayTasks.length)
    console.log('🔍 DEBUG - Tarefas atrasadas:', overdueTasks.length)
    console.log('🔍 DEBUG - Tarefas futuras:', futureTasks.length)

    return {
      user: {
        id: user.id,
        name: user.name,
        email: user.email
      },
      recentMemories,
      currentTasks,
      todayTasks,
      overdueTasks,
      productivityInsights,
      conversationContext
    }
  }

  async analyzeUserMessage(message: string, context: UserContext): Promise<{
    emotionalAnalysis: EmotionalAnalysis
    prioritizedMemories: any[]
    prompt: string
    taskResponse?: TaskResponse
    matchedTasks?: any[]
  }> {
    // Analisa emoção da mensagem com contexto conversacional
    const emotionalAnalysis = analyzeEmotionWithContext(message, context.conversationContext)

    // 🔍 MELHOR MATCHING DE TAREFAS: busca em todas as tarefas
    const allUserTasks = [...context.currentTasks, ...context.todayTasks, ...context.overdueTasks]
    const matchedTasks = conversationContextService.findTaskMatches(message, allUserTasks)
    
    // Log para debug
    console.log('🔍 DEBUG - Mensagem:', message)
    console.log('🔍 DEBUG - Tarefas encontradas:', matchedTasks.map(t => `${t.title} (${t.similarity})`))
    
    // Se encontrou match de tarefa, define foco na conversa
    if (matchedTasks.length > 0 && matchedTasks[0].similarity > 0.5) {
      const topMatch = matchedTasks[0]
      conversationContextService.setFocusedTask(
        context.user.id, 
        topMatch.taskId, 
        topMatch.title
      )
      console.log('🔍 DEBUG - Tarefa em foco:', topMatch.title)
    }

    // Verifica se é uma solicitação relacionada a tarefas
    const taskResponse = await this.taskAssistant.processTaskRequest(
      context.user.id,
      message,
      context.user.name
    )

    // Adiciona informação sobre tarefas encontradas ao taskResponse
    if (taskResponse && matchedTasks.length > 0) {
      (taskResponse as any).matchedTask = matchedTasks[0]
    }

    // Se foi processada como tarefa e foi bem-sucedida, retorna resposta específica
    if (taskResponse.success) {
      // Atualiza contexto de conversa
      conversationContextService.updateContext(
        context.user.id,
        message,
        emotionalAnalysis.detectedMood,
        taskResponse.taskAction || 'task_action'
      )

      return {
        emotionalAnalysis,
        prioritizedMemories: [],
        prompt: '', // Prompt vazio pois a resposta já está pronta
        taskResponse,
        matchedTasks
      }
    }

    // Se foi uma ação de tarefa reconhecida mas precisa de mais informação
    if (taskResponse.taskAction) {
      // Atualiza contexto mesmo que não tenha sido completamente processada
      conversationContextService.updateContext(
        context.user.id,
        message,
        emotionalAnalysis.detectedMood,
        taskResponse.taskAction
      )

      return {
        emotionalAnalysis,
        prioritizedMemories: [],
        prompt: '', // Prompt vazio pois a resposta já está pronta
        taskResponse,
        matchedTasks
      }
    }

    // Continua com o fluxo normal se não foi uma tarefa
    const prioritizedMemories = prioritizeMemories(context.recentMemories, message)

    // Contexto enriquecido incluindo conversa e tarefas encontradas
    const enrichedContext = {
      ...context,
      recentMemories: prioritizedMemories.slice(0, 5), // Reduzido para menos ruído
      conversationContext: context.conversationContext,
      matchedTasks: matchedTasks.slice(0, 2) // Adiciona tarefas relacionadas
    }

    const prompt = buildLumiPrompt(message, enrichedContext, emotionalAnalysis)

    // Atualiza contexto de conversa
    conversationContextService.updateContext(
      context.user.id,
      message,
      emotionalAnalysis.detectedMood,
      'general_conversation'
    )

    return {
      emotionalAnalysis,
      prioritizedMemories,
      prompt,
      taskResponse: taskResponse.success ? taskResponse : undefined,
      matchedTasks
    }
  }

  async extractAndSaveMemories(
    userId: string,
    userMessage: string,
    response: string
  ): Promise<void> {
    const extractedMemories = extractMemoryFromResponse(response, userMessage)
    
    for (const memory of extractedMemories) {
      if (memory.length > 10) { // Só salva memórias significativas
        await this.memoryService.create({
          userId,
          type: 'COMMUNICATION_STYLE',
          content: memory,
          importance: 'MEDIUM',
          tags: ['extracted_memory']
        })
      }
    }
  }

  private determineMemoryType(info: string, userMessage: string): any {
    const lowerInfo = info.toLowerCase()
    const lowerMessage = userMessage.toLowerCase()
    
    if (lowerInfo.includes('trabalho') || lowerInfo.includes('empresa')) {
      return 'WORK_CONTEXT'
    }
    if (lowerInfo.includes('estud') || lowerInfo.includes('faculdade') || lowerInfo.includes('curso')) {
      return 'STUDY_CONTEXT'  
    }
    if (lowerMessage.includes('gosto') || lowerMessage.includes('prefiro') || lowerMessage.includes('amo')) {
      return 'PREFERENCES'
    }
    if (lowerMessage.includes('sempre') || lowerMessage.includes('costumo') || lowerMessage.includes('geralmente')) {
      return 'PRODUCTIVITY_PATTERN'
    }
    if (lowerMessage.includes('sinto') || lowerMessage.includes('fico') || lowerMessage.includes('me deixa')) {
      return 'EMOTIONAL_STATE'
    }
    
    return 'PERSONAL_CONTEXT'
  }

  private async updateCommunicationPattern(userId: string, emotionalAnalysis: EmotionalAnalysis): Promise<void> {
    const patterns = {
      'high_energy': ['excited', 'energetic', 'entusiasmo', 'motivated'],
      'needs_support': ['sad', 'confused', 'overwhelmed', 'desmotivacao', 'confusao', 'sobrecarregado'],
      'task_focused': ['focused', 'determined', 'foco', 'motivated']
    }

    let patternType = 'balanced'
    for (const [pattern, moods] of Object.entries(patterns)) {
      if (moods.includes(emotionalAnalysis.detectedMood)) {
        patternType = pattern
        break
      }
    }

    await this.memoryService.create({
      userId,
      type: 'COMMUNICATION_STYLE',
      content: `Padrão detectado: ${patternType} (confiança: ${Math.round(emotionalAnalysis.confidence * 100)}%)`,
      importance: 'MEDIUM',
      emotionalContext: emotionalAnalysis.detectedMood,
      communicationStyle: patternType,
      tags: ['communication_pattern', emotionalAnalysis.detectedMood]
    })
  }

  async getTaskSuggestions(userId: string, emotionalAnalysis: EmotionalAnalysis): Promise<string[]> {
    const suggestions: string[] = []
    
    // Sugestões baseadas no estado emocional
    switch (emotionalAnalysis.detectedMood) {
      case 'overwhelmed':
      case 'sobrecarregado':
        suggestions.push('Que tal priorizarmos apenas 1-2 tarefas importantes para hoje?')
        suggestions.push('Vamos organizar suas tarefas por ordem de urgência?')
        break
        
      case 'procrastinating':
      case 'procrastinacao':
        suggestions.push('Que tal começarmos com uma tarefa pequena, só para "quebrar o gelo"?')
        suggestions.push('Vamos definir um timer de 15 minutos para uma atividade?')
        break
        
      case 'confused':
      case 'confusao':
        suggestions.push('Posso te ajudar a organizar suas ideias em etapas?')
        suggestions.push('Vamos quebrar esse projeto em partes menores?')
        break
        
      case 'excited':
      case 'entusiasmo':
        suggestions.push('Com essa energia toda, que tal tacklearmos uma tarefa desafiadora?')
        suggestions.push('Vamos aproveitar esse ânimo para adiantar algumas pendências?')
        break
        
      case 'tired':
      case 'desmotivacao':
        suggestions.push('Que tal algo leve para hoje? Uma tarefa rápida só para sentir progresso?')
        suggestions.push('Vamos focar no essencial e deixar o resto para quando você estiver melhor?')
        break
        
      default:
        suggestions.push('Como posso te ajudar a organizar o dia?')
        suggestions.push('Quer que eu analise suas prioridades?')
    }
    
    return suggestions
  }
}
