import { TaskService, TaskCreateData } from './taskService'
import { taskManager, TaskManager } from './taskManager'
import { parseUserIntentFromLumi, ParsedIntent, hasTaskPotential } from '../../utils/intentParser'
import { MemoryService } from '../memory/memoryService'

export class TaskAssistant {
  private taskService = new TaskService()
  private taskManager = taskManager
  private memoryService = new MemoryService()

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

      // Usa o novo sistema LLM para analisar intenção
      const intent = await parseUserIntentFromLumi(message, userId)
      
      if (intent.intent === 'none' || (intent.confidence && intent.confidence < 0.5)) {
        return {
          success: false,
          message: this.getHelpfulResponse(userName, message)
        }
      }

      switch (intent.intent) {
        case 'create_task':
          return await this.handleCreateTask(userId, intent, userName)
        
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
    userName: string
  ): Promise<any> {
    
    if (!intent.title) {
      return {
        success: false,
        message: `${userName}, preciso saber o que você quer agendar! 📝 Pode me dar mais detalhes sobre essa tarefa?`
      }
    }

    try {
      // Usar o novo TaskManager para criar a tarefa
      const result = await this.taskManager.createTask({
        userId,
        title: intent.title,
        description: intent.description,
        priority: intent.priority || 'MEDIUM',
        startAt: intent.startAt ? new Date(intent.startAt) : undefined,
        endAt: intent.endAt ? new Date(intent.endAt) : undefined,
        pomodoroGoal: intent.pomodoroGoal || 1,
      })

      if (!result.success) {
        // Tratar diferentes tipos de erro
        if (result.error === 'TIME_CONFLICT') {
          return {
            success: true,
            taskAction: 'CREATE_WITH_CONFLICT',
            message: `Entendi, ${userName}! Você quer agendar "${intent.title}", mas detectei um conflito de horário. ${result.message}`,
            conflictDetected: true
          }
        }
        
        return {
          success: false,
          message: `${userName}, ${result.message} 🤔`
        }
      }

      const task = result.data
      
      // Salvar padrão na memória
      await this.memoryService.create({
        userId,
        type: 'PRODUCTIVITY_PATTERN',
        content: `Criou tarefa "${task.title}" com prioridade ${task.priority} ${intent.startAt ? `para ${new Date(intent.startAt).toLocaleString('pt-BR')}` : ''}`,
        importance: 'MEDIUM',
        tags: ['task_creation', task.priority.toLowerCase(), ...(intent.tags || [])]
      })

      // Gerar resposta personalizada
      const timeInfo = intent.startAt 
        ? ` para ${this.formatDate(new Date(intent.startAt))} às ${new Date(intent.startAt).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}`
        : ''

      const priorityText = this.getPriorityDescription(task.priority)
      const successMessage = this.getCreationSuccessMessage(userName, task.title, timeInfo, priorityText)

      return {
        success: true,
        taskAction: 'CREATED',
        message: successMessage,
        suggestionsMessage: this.getTaskSuggestion(task.priority)
      }

    } catch (error) {
      console.error('Erro ao criar tarefa via TaskManager:', error)
      return {
        success: false,
        message: `${userName}, tive um problema ao criar a tarefa. Pode tentar novamente? 🤖`
      }
    }
  }

  private getPriorityEmoji(priority: string): string {
    switch (priority) {
      case 'HIGH': return '🔴 alta'
      case 'LOW': return '🟢 baixa'
      default: return '� média'
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
    const [pendingTasks, summary] = await Promise.all([
      this.taskService.findPendingTasks(userId),
      this.taskService.getTaskSummary(userId)
    ])

    if (pendingTasks.length === 0) {
      const emptyMessages = [
        `${userName}, sua agenda está limpinha! 🎉 Hora de relaxar ou planejar novas conquistas?`,
        `Uau, ${userName}! Você está livre como um passarinho! 🕊️ Que tal aproveitar esse tempo?`,
        `${userName}, que inveja! Agenda zerada! 📅✨ Momento perfeito para fazer algo que ama.`
      ]
      
      return {
        success: true,
        taskAction: 'LISTED_EMPTY',
        message: emptyMessages[Math.floor(Math.random() * emptyMessages.length)]
      }
    }

    // Agrupa tarefas por contexto de tempo
    const today = new Date()
    const todayTasks = pendingTasks.filter(task => 
      task.startAt && task.startAt.toDateString() === today.toDateString()
    )
    const futureTasks = pendingTasks.filter(task => 
      !task.startAt || task.startAt.toDateString() !== today.toDateString()
    )

    let taskList = `${userName}, vamos ver sua agenda! 📋\n\n`
    
    // Mostra tarefas de hoje primeiro
    if (todayTasks.length > 0) {
      taskList += `🗓️ **Para hoje:**\n`
      todayTasks.slice(0, 5).forEach((task, index) => {
        const priority = this.getPriorityIcon(task.priority)
        const timeInfo = task.startAt 
          ? ` às ${task.startAt.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}`
          : ''
        
        taskList += `${index + 1}. ${priority} ${task.title}${timeInfo}\n`
      })
      taskList += '\n'
    }
    
    // Mostra próximas tarefas
    if (futureTasks.length > 0) {
      const displayCount = Math.min(5, 8 - todayTasks.length)
      taskList += `📅 **Próximas tarefas:**\n`
      
      futureTasks.slice(0, displayCount).forEach((task, index) => {
        const priority = this.getPriorityIcon(task.priority)
        const timeInfo = task.startAt 
          ? ` - ${this.formatDate(task.startAt)} às ${task.startAt.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}`
          : ''
        
        taskList += `${index + 1}. ${priority} ${task.title}${timeInfo}\n`
      })
    }

    // Resumo inteligente
    taskList += `\n${this.getTaskSummary(summary, userName)}`

    return {
      success: true,
      taskAction: 'LISTED',
      message: taskList,
      suggestionsMessage: this.getProductivityTip(summary, userName)
    }
  }

  private getPriorityIcon(priority: string): string {
    switch (priority) {
      case 'HIGH': return '🔴'
      case 'LOW': return '🟢' 
      default: return '�'
    }
  }

  private getTaskSummary(summary: any, userName: string): string {
    let summaryText = `📊 **Resumo:** ${summary.pending} pendentes`
    
    if (summary.today > 0) {
      summaryText += ` | ${summary.today} para hoje`
    }
    
    if (summary.overdue > 0) {
      summaryText += ` | ⏰ ${summary.overdue} atrasadas`
    }
    
    if (summary.highPriority > 0) {
      summaryText += ` | 🔴 ${summary.highPriority} urgentes`
    }
    
    return summaryText
  }

  private getProductivityTip(summary: any, userName: string): string {
    if (summary.overdue > 0) {
      return `💡 ${userName}, você tem algumas tarefas atrasadas. Que tal focarmos nelas primeiro para ficar em dia? Posso te ajudar a reorganizar!`
    }
    
    if (summary.highPriority > 0) {
      return `⚡ ${userName}, suas tarefas prioritárias merecem atenção especial! Sugiro começar por elas quando estiver com mais energia.`
    }
    
    if (summary.today > 3) {
      return `🎯 ${userName}, dia cheio hoje! Que tal usar a técnica Pomodoro? Posso te lembrar dos intervalos!`
    }
    
    return `👏 ${userName}, você está muito bem organizado! Continue assim e mantenha esse ritmo produtivo!`
  }

  private async handleCompleteTask(
    userId: string, 
    intent: ParsedIntent, 
    userName: string
  ): Promise<any> {
    const { taskReference } = intent
    
    if (!taskReference) {
      const recentTasks = await this.taskService.findPendingTasks(userId)
      if (recentTasks.length === 0) {
        const noTasksMessages = [
          `${userName}, que maravilha! Você não tem tarefas pendentes! 🎉 Está livre para relaxar!`,
          `Incrível, ${userName}! Sua lista está zerada! 🏆 Momento perfeito para um merecido descanso!`,
          `${userName}, parabéns! Nenhuma tarefa pendente! ⭐ Você é um exemplo de produtividade!`
        ]
        
        return {
          success: false,
          taskAction: 'COMPLETE',
          message: noTasksMessages[Math.floor(Math.random() * noTasksMessages.length)]
        }
      }
      
      let message = `${userName}, qual tarefa você finalizou? 🤔 Vejo que você tem:\n\n`
      recentTasks.slice(0, 5).forEach((task, index) => {
        const priority = this.getPriorityIcon(task.priority)
        message += `${index + 1}. ${priority} ${task.title}\n`
      })
      
      return {
        success: false,
        taskAction: 'COMPLETE',
        message: message + '\n💬 Me diga o número ou nome da tarefa que completou!'
      }
    }

    // Busca mais inteligente
    let tasks = await this.taskService.searchTasks(userId, taskReference, 3)
    
    // Se não encontrou, tenta busca mais ampla
    if (tasks.length === 0) {
      const words = taskReference.split(' ')
      for (const word of words) {
        if (word.length > 3) {
          tasks = await this.taskService.searchTasks(userId, word, 2)
          if (tasks.length > 0) break
        }
      }
    }
    
    if (tasks.length === 0) {
      return {
        success: false,
        taskAction: 'COMPLETE',
        message: `${userName}, não consegui encontrar uma tarefa que combine com "${taskReference}". 🔍\n\nPode ser mais específico ou me dizer o nome exato da tarefa?`
      }
    }

    // Se encontrou múltiplas, mostra opções
    if (tasks.length > 1) {
      let message = `${userName}, encontrei algumas opções. Qual você completou?\n\n`
      tasks.slice(0, 3).forEach((task, index) => {
        const priority = this.getPriorityIcon(task.priority)
        message += `${index + 1}. ${priority} ${task.title}\n`
      })
      return {
        success: false,
        taskAction: 'COMPLETE',
        message: message + '\n💬 Me diga o número da tarefa!'
      }
    }

    const task = tasks[0]
    
    try {
      // Usar o novo TaskManager para marcar como concluída
      const result = await this.taskManager.completeTask(userId, task.id)
      
      if (!result.success) {
        return {
          success: false,
          message: `${userName}, ${result.message} 🤔`
        }
      }

      const completedTask = result.data
      
      // Salvar padrão de conclusão
      const now = new Date()
      const isOnTime = !completedTask.endAt || now <= completedTask.endAt
      
      await this.memoryService.create({
        userId,
        type: 'PRODUCTIVITY_PATTERN',
        content: `Concluiu tarefa "${completedTask.title}" (${completedTask.priority}) ${isOnTime ? 'no prazo' : 'com atraso'}`,
        importance: 'MEDIUM',
        tags: ['task_completion', completedTask.priority.toLowerCase(), isOnTime ? 'on_time' : 'late']
      })

      // Mensagem de sucesso personalizada
      const successMessage = this.getCompletionMessage(userName, completedTask.title, completedTask.priority, isOnTime)
      const celebration = this.getCelebrationMessage(completedTask.priority, isOnTime)

      return {
        success: true,
        taskAction: 'COMPLETED',
        message: successMessage,
        suggestionsMessage: celebration
      }

    } catch (error) {
      console.error('Erro ao completar tarefa via TaskManager:', error)
      return {
        success: false,
        message: `${userName}, tive um problema ao marcar a tarefa como concluída. Pode tentar novamente? 🤖`
      }
    }
  }

  private getCompletionMessage(userName: string, taskTitle: string, priority: string, isOnTime: boolean): string {
    if (priority === 'HIGH') {
      if (isOnTime) {
        const messages = [
          `${userName}, que perfeição! ✨ Completou "${taskTitle}" no prazo! Você é incrível!`,
          `Excelente, ${userName}! 🎯 "${taskTitle}" foi finalizada dentro do prazo. Parabéns!`,
          `${userName}, impressionante! ⚡ "${taskTitle}" concluída como um profissional!`
        ]
        return messages[Math.floor(Math.random() * messages.length)]
      } else {
        const messages = [
          `${userName}, "${taskTitle}" está concluída! 💪 Melhor tarde do que nunca!`,
          `Ótimo trabalho, ${userName}! ✅ "${taskTitle}" finalizada! O importante é não desistir!`,
          `${userName}, parabéns! 🎉 "${taskTitle}" está feita! Continue assim!`
        ]
        return messages[Math.floor(Math.random() * messages.length)]
      }
    } else {
      const messages = [
        `Perfeito, ${userName}! ✅ "${taskTitle}" concluída com sucesso!`,
        `${userName}, mais uma tarefa no papo! 🏆 "${taskTitle}" está finalizada!`,
        `Ótimo, ${userName}! 🎯 "${taskTitle}" foi completada!`,
        `${userName}, show! ⭐ "${taskTitle}" está pronta!`
      ]
      return messages[Math.floor(Math.random() * messages.length)]
    }
  }

  private async handleDeleteTask(
    userId: string, 
    intent: ParsedIntent, 
    userName: string
  ): Promise<any> {
    const { taskReference } = intent
    
    if (!taskReference) {
      const recentTasks = await this.taskService.findPendingTasks(userId)
      if (recentTasks.length === 0) {
        return {
          success: false,
          taskAction: 'DELETE',
          message: `${userName}, você não tem tarefas para remover! 🎉 Sua agenda está limpinha!`
        }
      }
      
      let message = `${userName}, qual tarefa você quer remover? 🗑️ Vejo que você tem:\n\n`
      recentTasks.slice(0, 5).forEach((task, index) => {
        const priority = this.getPriorityIcon(task.priority)
        message += `${index + 1}. ${priority} ${task.title}\n`
      })
      
      return {
        success: false,
        taskAction: 'DELETE',
        message: message + '\n💬 Me diga o número ou nome da tarefa!'
      }
    }

    // Busca inteligente similar ao handleCompleteTask
    let tasks = await this.taskService.searchTasks(userId, taskReference, 3)
    
    if (tasks.length === 0) {
      const words = taskReference.split(' ')
      for (const word of words) {
        if (word.length > 3) {
          tasks = await this.taskService.searchTasks(userId, word, 2)
          if (tasks.length > 0) break
        }
      }
    }
    
    if (tasks.length === 0) {
      return {
        success: false,
        taskAction: 'DELETE',
        message: `${userName}, não encontrei uma tarefa que combine com "${taskReference}". 🔍\n\nPode ser mais específico com o nome da tarefa?`
      }
    }

    // Se encontrou múltiplas, mostra opções
    if (tasks.length > 1) {
      let message = `${userName}, encontrei algumas opções. Qual você quer remover?\n\n`
      tasks.slice(0, 3).forEach((task, index) => {
        const priority = this.getPriorityIcon(task.priority)
        message += `${index + 1}. ${priority} ${task.title}\n`
      })
      return {
        success: false,
        taskAction: 'DELETE',
        message: message + '\n💬 Me diga o número da tarefa!'
      }
    }

    const task = tasks[0]
    await this.taskService.deleteTask(task.id, userId)

    // Salvar na memória o padrão de remoção
    await this.memoryService.create({
      userId,
      type: 'PRODUCTIVITY_PATTERN',
      content: `Removeu tarefa "${task.title}" (${task.priority})`,
      importance: 'LOW',
      tags: ['task_deletion', task.priority.toLowerCase()]
    })

    const deleteMessages = [
      `Pronto, ${userName}! 🗑️ Removi "${task.title}" da sua agenda. Às vezes precisamos reorganizar mesmo!`,
      `${userName}, "${task.title}" foi removida! ✨ Sua agenda está mais organizada agora!`,
      `Feito! 🎯 "${task.title}" não está mais na sua lista, ${userName}. Foco no que realmente importa!`,
      `${userName}, "${task.title}" foi cancelada! � Espaço livre para coisas mais importantes!`
    ]

    return {
      success: true,
      taskAction: 'DELETED',
      message: deleteMessages[Math.floor(Math.random() * deleteMessages.length)]
    }
  }

  private async handleUpdateTask(
    userId: string, 
    intent: ParsedIntent, 
    userName: string
  ): Promise<any> {
    const { taskReference } = intent
    
    if (!taskReference) {
      return {
        success: false,
        message: `${userName}, preciso saber qual tarefa você quer editar! 📝 Me diga o nome da tarefa e o que quer alterar.`
      }
    }

    // Buscar a tarefa
    let tasks = await this.taskService.searchTasks(userId, taskReference, 3)
    
    if (tasks.length === 0) {
      const words = taskReference.split(' ')
      for (const word of words) {
        if (word.length > 3) {
          tasks = await this.taskService.searchTasks(userId, word, 2)
          if (tasks.length > 0) break
        }
      }
    }
    
    if (tasks.length === 0) {
      return {
        success: false,
        message: `${userName}, não encontrei uma tarefa que combine com "${taskReference}". 🔍\n\nPode ser mais específico com o nome da tarefa?`
      }
    }

    // Se encontrou múltiplas, mostra opções
    if (tasks.length > 1) {
      let message = `${userName}, encontrei algumas opções. Qual você quer editar?\n\n`
      tasks.slice(0, 3).forEach((task, index) => {
        const priority = this.getPriorityIcon(task.priority)
        message += `${index + 1}. ${priority} ${task.title}\n`
      })
      return {
        success: false,
        message: message + '\n💬 Me diga o número da tarefa!'
      }
    }

    const task = tasks[0]
    
    try {
      // Preparar dados para atualização baseados no que foi extraído
      const updateData: any = {}
      
      if (intent.title && intent.title !== task.title) {
        updateData.title = intent.title
      }
      
      if (intent.description) {
        updateData.description = intent.description
      }
      
      if (intent.priority && intent.priority !== task.priority) {
        updateData.priority = intent.priority
      }
      
      if (intent.startAt) {
        updateData.startAt = new Date(intent.startAt)
      }
      
      if (intent.endAt) {
        updateData.endAt = new Date(intent.endAt)
      }
      
      if (intent.pomodoroGoal && intent.pomodoroGoal !== task.pomodoroGoal) {
        updateData.pomodoroGoal = intent.pomodoroGoal
      }

      // Se não há nada para atualizar, retorna mensagem explicativa
      if (Object.keys(updateData).length === 0) {
        return {
          success: false,
          message: `${userName}, não identifiquei o que você quer alterar na tarefa "${task.title}". Pode me dizer especificamente o que quer mudar? 🤔\n\nPor exemplo: "alterar prioridade", "mudar horário", "trocar título", etc.`
        }
      }

      // Usar o novo TaskManager para atualizar a tarefa
      const result = await this.taskManager.updateTask({
        userId,
        taskId: task.id,
        ...updateData
      })
      
      if (!result.success) {
        return {
          success: false,
          message: `${userName}, ${result.message} 🤔`
        }
      }

      const updatedTask = result.data
      
      // Salvar na memória o padrão de edição
      await this.memoryService.create({
        userId,
        type: 'PRODUCTIVITY_PATTERN',
        content: `Editou tarefa "${updatedTask.title}" - alterações: ${Object.keys(updateData).join(', ')}`,
        importance: 'MEDIUM',
        tags: ['task_update', updatedTask.priority.toLowerCase()]
      })

      // Criar mensagem de sucesso detalhada
      const changes = Object.keys(updateData).map(key => {
        switch (key) {
          case 'title': return `título para "${updateData.title}"`
          case 'priority': return `prioridade para ${this.getPriorityDescription(updateData.priority)}`
          case 'startAt': return `horário de início para ${updateData.startAt.toLocaleString('pt-BR')}`
          case 'endAt': return `horário de fim para ${updateData.endAt.toLocaleString('pt-BR')}`
          case 'pomodoroGoal': return `meta de pomodoros para ${updateData.pomodoroGoal}`
          case 'description': return 'descrição'
          default: return key
        }
      }).join(', ')

      const successMessages = [
        `Perfeito, ${userName}! ✅ Atualizei "${updatedTask.title}" - ${changes}.`,
        `Feito, ${userName}! 🎯 A tarefa "${updatedTask.title}" foi editada - ${changes}.`,
        `Ótimo, ${userName}! ⭐ "${updatedTask.title}" está atualizada - ${changes}.`
      ]

      return {
        success: true,
        taskAction: 'UPDATED',
        message: successMessages[Math.floor(Math.random() * successMessages.length)],
        suggestionsMessage: this.getTaskSuggestion(updatedTask.priority)
      }

    } catch (error) {
      console.error('Erro ao atualizar tarefa via TaskManager:', error)
      return {
        success: false,
        message: `${userName}, tive um problema ao editar a tarefa. Pode tentar novamente? 🤖`
      }
    }
  }

  private async handleSearchTasks(
    userId: string, 
    intent: ParsedIntent, 
    userName: string
  ): Promise<any> {
    const { taskReference } = intent
    
    if (!taskReference) {
      return {
        success: false,
        message: `${userName}, me diga o que você está procurando! 🔍 Posso buscar por título, descrição ou palavra-chave das suas tarefas.`
      }
    }

    try {
      // Usar o TaskManager para buscar tarefas
      const result = await this.taskManager.searchTasks(userId, taskReference, 10)
      
      if (!result.success) {
        return {
          success: false,
          message: `${userName}, ${result.message} 🤔`
        }
      }

      const tasks = result.data
      
      if (tasks.length === 0) {
        return {
          success: false,
          message: `${userName}, não encontrei nenhuma tarefa com "${taskReference}". 🔍\n\nTente usar outras palavras-chave ou verifique se digitou corretamente!`
        }
      }

      // Construir resposta com as tarefas encontradas
      let message = `${userName}, encontrei ${tasks.length} tarefa${tasks.length > 1 ? 's' : ''} com "${taskReference}":\n\n`
      
      tasks.slice(0, 8).forEach((task: any, index: number) => {
        const priority = this.getPriorityIcon(task.priority)
        const status = task.completed ? '✅' : '⏳'
        const timeInfo = task.startAt 
          ? ` - ${this.formatDate(task.startAt)} às ${task.startAt.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}`
          : ''
        
        message += `${index + 1}. ${status} ${priority} ${task.title}${timeInfo}\n`
        
        if (task.description && task.description.length > 0) {
          message += `   📝 ${task.description.substring(0, 50)}${task.description.length > 50 ? '...' : ''}\n`
        }
      })

      if (tasks.length > 8) {
        message += `\n... e mais ${tasks.length - 8} tarefas encontradas.`
      }

      // Salvar na memória o padrão de busca
      await this.memoryService.create({
        userId,
        type: 'PRODUCTIVITY_PATTERN',
        content: `Buscou por "${taskReference}" e encontrou ${tasks.length} tarefas`,
        importance: 'LOW',
        tags: ['task_search', 'productivity']
      })

      return {
        success: true,
        taskAction: 'SEARCHED',
        message: message,
        suggestionsMessage: tasks.length > 5 ? 'Dica: Use termos mais específicos para refinar sua busca! 🎯' : ''
      }

    } catch (error) {
      console.error('Erro ao buscar tarefas via TaskManager:', error)
      return {
        success: false,
        message: `${userName}, tive um problema ao buscar as tarefas. Pode tentar novamente? 🤖`
      }
    }
  }

  private getTaskSuggestion(priority: string): string {
    switch (priority) {
      case 'HIGH':
        const highPriorityTips = [
          'Dica: Tarefas de alta prioridade são melhores feitas no seu horário de maior energia! ⚡',
          'Sugestão: Use a técnica Pomodoro para manter o foco nas tarefas importantes! 🍅',
          'Dica: Elimine distrações quando estiver trabalhando em tarefas urgentes! 🎯'
        ]
        return highPriorityTips[Math.floor(Math.random() * highPriorityTips.length)]
        
      case 'LOW':
        const lowPriorityTips = [
          'Dica: Tarefas simples são perfeitas para quando você está com pouco tempo! ⏰',
          'Sugestão: Use tarefas de baixa prioridade para fazer pausas ativas! 🌱',
          'Dica: Agrupe tarefas simples e faça várias de uma vez! 📦'
        ]
        return lowPriorityTips[Math.floor(Math.random() * lowPriorityTips.length)]
        
      default:
        const mediumPriorityTips = [
          'Dica: Organize suas tarefas por contexto para ser mais eficiente! 📝',
          'Sugestão: Intercale tarefas médias com as de alta prioridade! ⚖️',
          'Dica: Use blocos de tempo para tarefas de complexidade média! ⏱️'
        ]
        return mediumPriorityTips[Math.floor(Math.random() * mediumPriorityTips.length)]
    }
  }

  private getPrioritySuggestion(summary: any): string {
    if (summary.highPriority > 0) {
      return `💡 Sugestão: Você tem ${summary.highPriority} tarefas de alta prioridade. Que tal focar nelas primeiro?`
    }
    if (summary.overdue > 0) {
      return `⚠️ Lembre-se: ${summary.overdue} tarefas estão atrasadas. Vamos colocar em dia?`
    }
    return '🎯 Você está com boa organização! Continue priorizando as tarefas importantes.'
  }

  private getCelebrationMessage(priority?: string, isOnTime?: boolean): string {
    if (priority === 'HIGH' && isOnTime) {
      const messages = [
        'Que máquina de produtividade! 🔥 Tarefa importante concluída no prazo!',
        'Você é um exemplo! ⚡ Alta prioridade finalizada pontualmente!',
        'Impressionante! 🎯 Eficiência e pontualidade em perfeita sintonia!'
      ]
      return messages[Math.floor(Math.random() * messages.length)]
    }
    
    if (priority === 'HIGH') {
      const messages = [
        'Tarefa importante concluída! 🎉 O que importa é a dedicação!',
        'Parabéns pela persistência! 💪 Missão cumprida!',
        'Excelente! ⭐ Você não desistiu e chegou lá!'
      ]
      return messages[Math.floor(Math.random() * messages.length)]
    }
    
    const messages = [
      'Que orgulho de você! 🎉',
      'Mais uma conquista! 🏆', 
      'Produtividade em alta! 📈',
      'Você está arrasando! ⭐',
      'Continue nesse ritmo! 🚀',
      'Show de bola! 👏',
      'Cada tarefa concluída é uma vitória! 🎯'
    ]
    return messages[Math.floor(Math.random() * messages.length)]
  }

  private getHelpfulResponse(userName: string, message: string): string {
    const lowerMessage = message.toLowerCase()
    
    // Se a mensagem não é sobre tarefas, retorna resposta mais geral
    if (!this.isTaskRelatedQuery(message)) {
      return `${userName}, percebi que você não está falando sobre tarefas ou agenda! 😊\n\n` +
             `Sou especialista em gerenciamento de tarefas, mas posso te ajudar com outras coisas também.\n\n` +
             `Se precisar de ajuda com sua agenda, é só falar algo como:\n` +
             `• "Agendar reunião para amanhã"\n` +
             `• "Quais são minhas tarefas?"\n` +
             `• "Cancelar compromisso de hoje"\n\n` +
             `Caso contrário, pode contar mais sobre o que você precisa! �`
    }
    
    // Respostas específicas para tarefas
    if (lowerMessage.includes('ajuda') || lowerMessage.includes('como')) {
      return `${userName}, claro! Posso te ajudar com sua agenda! �\n\n` +
             `📝 Para criar: "Agendar reunião hoje às 14h" ou "Lembrar de ligar para o médico"\n` +
             `📋 Para listar: "Quais são minhas tarefas?" ou "O que tenho hoje?"\n` +
             `✅ Para concluir: "Terminei a apresentação" ou "Completei o projeto"\n` +
             `🗑️ Para remover: "Cancelar reunião" ou "Remover tarefa X"\n\n` +
             `Fale naturalmente comigo, entendo você perfeitamente! 💪`
    }
    
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
