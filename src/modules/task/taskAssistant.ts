import { TaskService, TaskCreateData } from './taskService'
import { taskManager, TaskManager } from './taskManager'
import { parseUserIntentFromLumi, ParsedIntent, hasTaskPotential, decideBoardForTask } from '../../utils/intentParser'
import { MemoryService } from '../memory/memoryService'
import { prisma } from '../../prisma/client'

class TaskAssistant {
  private taskService = new TaskService()
  private taskManager = taskManager
  private memoryService = new MemoryService()

  /**
   * Busca os quadros do usuário para contexto na análise de intenção
   */
  private async getUserBoards(userId: string): Promise<Array<{ id: string; title: string }>> {
    try {
      const boards = await prisma.boards.findMany({
        where: { userId },
        select: { id: true, title: true },
        orderBy: { createdAt: 'asc' }
      })
      
      return boards
    } catch (error) {
      console.error('Erro ao buscar quadros do usuário:', error)
      return []
    }
  }

  async processTaskRequest(
    userId: string, 
    message: string,
    userName: string
  ): Promise<{
    success: boolean
    message: string
    taskAction?: string
    conflictDetected?: boolean
    suggestionsMessage?: string
  }> {
    try {
      // Verificação rápida se tem potencial de ser tarefa
      if (!hasTaskPotential(message)) {
        return {
          success: false,
          message: this.getHelpfulResponse(userName, message)
        }
      }

      // Busca os quadros do usuário para contexto
      const userBoards = await this.getUserBoards(userId)

      // Usa o novo sistema LLM para analisar intenção com contexto de quadros
      const intent = await parseUserIntentFromLumi(message, userId, userBoards)
      
      if (intent.intent === 'none' || (intent.confidence && intent.confidence < 0.5)) {
        return {
          success: false,
          message: this.getHelpfulResponse(userName, message)
        }
      }

      switch (intent.intent) {
        case 'create_task':
          return await this.handleCreateTask(userId, intent, userName, userBoards)
        
        case 'create_board':
          return await this.handleCreateBoard(userId, intent, userName)
        
        case 'update_task':
          return await this.handleUpdateTask(userId, intent, userName)
        
        case 'delete_task':
          return await this.handleDeleteTask(userId, intent, userName)
        
        case 'complete_task':
          return await this.handleCompleteTask(userId, intent, userName)
        
        case 'list_tasks':
          return await this.handleListTasks(userId, userName)
        
        case 'search_tasks':
          return await this.handleSearchTasks(userId, intent, userName)
        
        default:
          return {
            success: false,
            message: `${userName}, não consegui entender exatamente o que você precisa. Que tal me contar de forma diferente? 😊`
          }
      }
    } catch (error) {
      console.error('Erro no processamento de tarefa:', error)
      return {
        success: false,
        message: `Ops, ${userName}! Tive um probleminha técnico. Pode tentar novamente? Estou aqui para ajudar! 🤖`
      }
    }
  }

  private async handleCreateTask(
    userId: string, 
    intent: ParsedIntent, 
    userName: string,
    userBoards?: Array<{ id: string; title: string }>
  ): Promise<any> {
    
    if (!intent.title) {
      return {
        success: false,
        message: `${userName}, preciso saber o que você quer agendar! 📝 Pode me dar mais detalhes sobre essa tarefa?`
      }
    }

    try {
      // Decisão inteligente sobre qual quadro usar
      const boardDecision = decideBoardForTask(intent, userBoards || [])
      
      let targetColumnId: string
      let boardInfo = ''
      
      if (boardDecision.action === 'create_new') {
        // Criar novo quadro
        const newBoard = await prisma.boards.create({
          data: {
            id: `board_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            title: boardDecision.boardName,
            userId: userId,
            updatedAt: new Date()
          }
        })
        
        // Criar coluna padrão "A fazer" no novo quadro
        const defaultColumn = await prisma.columns.create({
          data: {
            id: `col_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            title: 'A fazer',
            order: 1,
            boardId: newBoard.id,
            updatedAt: new Date()
          }
        })
        
        targetColumnId = defaultColumn.id
        boardInfo = ` no novo quadro "${newBoard.title}"`
        
        // Salvar na memória que criou um quadro
        await this.memoryService.create({
          userId,
          type: 'PRODUCTIVITY_PATTERN',
          content: `Criou quadro "${newBoard.title}" para organizar tarefas de ${boardDecision.reason}`,
          importance: 'MEDIUM',
          tags: ['board_creation', 'organization']
        })
        
      } else if (boardDecision.action === 'use_existing' && boardDecision.boardId) {
        // Usar quadro existente - buscar primeira coluna disponível
        const firstColumn = await prisma.columns.findFirst({
          where: { boardId: boardDecision.boardId },
          orderBy: { order: 'asc' }
        })
        
        if (!firstColumn) {
          // Se não tem colunas, criar uma padrão
          const defaultColumn = await prisma.columns.create({
            data: {
              id: `col_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
              title: 'A fazer',
              order: 1,
              boardId: boardDecision.boardId,
              updatedAt: new Date()
            }
          })
          targetColumnId = defaultColumn.id
        } else {
          targetColumnId = firstColumn.id
        }
        
        boardInfo = ` no quadro "${boardDecision.boardName}"`
      } else {
        return {
          success: false,
          message: `${userName}, tive um problema para decidir onde organizar sua tarefa. Você pode me dizer em qual quadro quer que eu coloque?`
        }
      }

      // Criar os dados da tarefa
      const taskData: TaskCreateData = {
        title: intent.title,
        description: intent.description,
        priority: intent.priority || 'MEDIUM',
        startAt: intent.startAt ? new Date(intent.startAt) : undefined,
        endAt: intent.endAt ? new Date(intent.endAt) : undefined,
        pomodoroGoal: intent.pomodoroGoal || 1,
        columnId: targetColumnId
      }

      // Usar o TaskService para criar a tarefa
      const newTask = await this.taskService.createTask(userId, taskData)

      // Salvar padrão na memória
      await this.memoryService.create({
        userId,
        type: 'PRODUCTIVITY_PATTERN',
        content: `Criou tarefa "${newTask.title}" com prioridade ${newTask.priority}${intent.startAt ? ` para ${new Date(intent.startAt).toLocaleString('pt-BR')}` : ''}${boardInfo}`,
        importance: 'MEDIUM',
        tags: ['task_creation', newTask.priority.toLowerCase(), ...(intent.tags || [])]
      })

      // Gerar resposta personalizada
      const timeInfo = intent.startAt 
        ? ` para ${this.formatDate(new Date(intent.startAt))} às ${new Date(intent.startAt).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}`
        : ''

      const priorityText = this.getPriorityDescription(newTask.priority)
      const successMessage = this.getCreationSuccessMessage(userName, newTask.title, timeInfo + boardInfo, priorityText)

      return {
        success: true,
        taskAction: 'CREATED',
        message: successMessage,
        suggestionsMessage: this.getTaskSuggestion(newTask.priority)
      }

    } catch (error) {
      console.error('Erro ao criar tarefa:', error)
      return {
        success: false,
        message: `${userName}, tive um problema ao criar a tarefa. Pode tentar novamente? 🤖`
      }
    }
  }

  private async handleCreateBoard(
    userId: string,
    intent: ParsedIntent,
    userName: string
  ): Promise<any> {
    if (!intent.boardName) {
      return {
        success: false,
        message: `${userName}, preciso saber qual o nome do quadro que você quer criar! 📋`
      }
    }

    try {
      // Verificar se já existe um quadro com o mesmo nome
      const existingBoard = await prisma.boards.findFirst({
        where: {
          userId,
          title: {
            equals: intent.boardName,
            mode: 'insensitive'
          }
        }
      })

      if (existingBoard) {
        return {
          success: false,
          message: `${userName}, você já tem um quadro chamado "${existingBoard.title}"! Quer usar esse ou criar com outro nome? 🤔`
        }
      }

      // Criar novo quadro
      const newBoard = await prisma.boards.create({
        data: {
          id: `board_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          title: intent.boardName,
          userId: userId,
          updatedAt: new Date()
        }
      })

      // Criar colunas padrão
      const defaultColumns = [
        { title: 'A fazer', order: 1 },
        { title: 'Em andamento', order: 2 },
        { title: 'Concluído', order: 3 }
      ]

      for (const columnData of defaultColumns) {
        await prisma.columns.create({
          data: {
            id: `col_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            title: columnData.title,
            order: columnData.order,
            boardId: newBoard.id,
            updatedAt: new Date()
          }
        })
      }

      // Salvar na memória
      await this.memoryService.create({
        userId,
        type: 'PRODUCTIVITY_PATTERN',
        content: `Criou quadro "${newBoard.title}" para organização de tarefas`,
        importance: 'MEDIUM',
        tags: ['board_creation', 'organization']
      })

      return {
        success: true,
        taskAction: 'BOARD_CREATED',
        message: `✅ Perfeito, ${userName}! Criei o quadro "${newBoard.title}" com as colunas padrão. Agora você pode organizar suas tarefas lá! 📋✨`
      }

    } catch (error) {
      console.error('Erro ao criar quadro:', error)
      return {
        success: false,
        message: `${userName}, tive um problema ao criar o quadro. Pode tentar novamente? 🤖`
      }
    }
  }

  private getPriorityDescription(priority: string): string {
    switch (priority) {
      case 'HIGH': return 'alta prioridade'
      case 'LOW': return 'baixa prioridade'
      default: return 'prioridade média'
    }
  }

  private formatDate(date: Date): string {
    const today = new Date()
    const tomorrow = new Date(today)
    tomorrow.setDate(today.getDate() + 1)
    
    if (date.toDateString() === today.toDateString()) {
      return 'hoje'
    } else if (date.toDateString() === tomorrow.toDateString()) {
      return 'amanhã'
    } else {
      return date.toLocaleDateString('pt-BR', { weekday: 'long', day: 'numeric', month: 'long' })
    }
  }

  private getCreationSuccessMessage(userName: string, title: string, timeInfo: string, priorityText: string): string {
    const successMessages = [
      `Pronto, ${userName}! ✅ Agendei "${title}"${timeInfo}. Definida como ${priorityText}.`,
      `Perfeito! 🎯 "${title}" está na sua agenda${timeInfo} com ${priorityText}.`,
      `Ótimo, ${userName}! 📅 "${title}" foi adicionada${timeInfo}. Prioridade: ${priorityText}.`,
      `Feito! ⭐ "${title}" já está marcada${timeInfo} como ${priorityText}.`
    ]
    
    return successMessages[Math.floor(Math.random() * successMessages.length)]
  }

  private async handleListTasks(userId: string, userName: string): Promise<any> {
    return {
      success: true,
      taskAction: 'LISTED_EMPTY',
      message: `${userName}, sua agenda está limpinha! 🎉 Hora de relaxar ou planejar novas conquistas?`
    }
  }

  private getPriorityIcon(priority: string): string {
    switch (priority) {
      case 'HIGH': return '🔴'
      case 'LOW': return '🟢' 
      default: return '🟡'
    }
  }

  private async handleCompleteTask(
    userId: string, 
    intent: ParsedIntent, 
    userName: string
  ): Promise<any> {
    return {
      success: false,
      message: `${userName}, funcionalidade ainda não implementada! 🚧`
    }
  }

  private async handleDeleteTask(
    userId: string, 
    intent: ParsedIntent, 
    userName: string
  ): Promise<any> {
    return {
      success: false,
      message: `${userName}, funcionalidade ainda não implementada! 🚧`
    }
  }

  private async handleUpdateTask(
    userId: string, 
    intent: ParsedIntent, 
    userName: string
  ): Promise<any> {
    return {
      success: false,
      message: `${userName}, funcionalidade ainda não implementada! 🚧`
    }
  }

  private async handleSearchTasks(
    userId: string, 
    intent: ParsedIntent, 
    userName: string
  ): Promise<any> {
    return {
      success: false,
      message: `${userName}, funcionalidade ainda não implementada! 🚧`
    }
  }

  private getTaskSuggestion(priority: string): string {
    return '💡 Dica: Organize suas tarefas por prioridade para ser mais produtivo! 🎯'
  }

  private getHelpfulResponse(userName: string, message: string): string {
    return `${userName}, não consegui entender exatamente o que você precisa com suas tarefas. 🤔\n\n` +
           `Que tal tentar algo como:\n` +
           `• "Adicionar [tarefa] para [quando]"\n` +
           `• "Listar minhas tarefas"\n` +
           `• "Completei [tarefa]"\n\n` +
           `Ou me conte de outra forma o que você precisa! 😊`
  }

  private isTaskRelatedQuery(message: string): boolean {
    const lowerMessage = message.toLowerCase()
    const taskKeywords = [
      'tarefa', 'agenda', 'compromisso', 'reunião', 'agendar', 'marcar',
      'cancelar', 'remarcar', 'horário', 'programação', 'to-do'
    ]
    
    return taskKeywords.some(keyword => lowerMessage.includes(keyword))
  }
}

export { TaskAssistant }