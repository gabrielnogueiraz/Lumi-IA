import { TaskService, TaskCreateData } from './taskService'
import { analyzeTaskIntent, TaskIntent } from '../../utils/taskIntentAnalyzer'
import { MemoryService } from '../memory/memoryService'

export class TaskAssistant {
  private taskService = new TaskService()
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
      const intent = analyzeTaskIntent(message)
      
      if (intent.action === 'NONE' || intent.confidence < 0.5) {
        return {
          success: false,
          message: this.getHelpfulResponse(userName, message)
        }
      }

      switch (intent.action) {
        case 'CREATE':
          return await this.handleCreateTask(userId, intent, userName)
        
        case 'UPDATE':
          return await this.handleUpdateTask(userId, intent, userName)
        
        case 'DELETE':
          return await this.handleDeleteTask(userId, intent, userName)
        
        case 'COMPLETE':
          return await this.handleCompleteTask(userId, intent, userName)
        
        case 'LIST':
          return await this.handleListTasks(userId, userName)
        
        case 'SEARCH':
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
    intent: TaskIntent, 
    userName: string
  ): Promise<any> {
    const { extractedData } = intent
    
    if (!extractedData.title) {
      return {
        success: false,
        message: `${userName}, preciso saber o que você quer agendar! 📝 Pode me dar mais detalhes sobre essa tarefa?`
      }
    }

    // Verificar conflitos se necessário
    let conflictMessage = ''
    if (intent.conflictCheck && extractedData.startAt && extractedData.endAt) {
      const conflicts = await this.taskService.findTasksInTimeRange(
        userId,
        extractedData.startAt,
        extractedData.endAt
      )

      if (conflicts.length > 0) {
        const conflictTask = conflicts[0]
        const conflictTime = extractedData.startAt.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
        
        conflictMessage = `\n\n⚠️ Opa! Notei que você já tem "${conflictTask.title}" marcado para ${conflictTime}. ` +
                         `Como "${extractedData.title}" parece ser importante, quer que eu remarcque a outra tarefa? ` +
                         `Ou prefere escolher outro horário para essa nova? 🤔`
        
        return {
          success: true,
          taskAction: 'CREATE_WITH_CONFLICT',
          message: `Entendi, ${userName}! Você quer agendar "${extractedData.title}" como prioridade ${this.getPriorityEmoji(extractedData.priority || 'MEDIUM')}.${conflictMessage}`,
          conflictDetected: true
        }
      }
    }

    const defaultColumnId = await this.taskService.getDefaultColumn(userId)
    
    const taskData: TaskCreateData = {
      title: extractedData.title,
      description: extractedData.description,
      priority: extractedData.priority || 'MEDIUM',
      startAt: extractedData.startAt,
      endAt: extractedData.endAt,
      pomodoroGoal: extractedData.pomodoroGoal,
      columnId: defaultColumnId
    }

    const task = await this.taskService.createTask(userId, taskData)
    
    // Salvar padrão na memória
    await this.memoryService.create({
      userId,
      type: 'PRODUCTIVITY_PATTERN',
      content: `Criou tarefa "${task.title}" com prioridade ${task.priority} ${extractedData.startAt ? `para ${extractedData.startAt.toLocaleString('pt-BR')}` : ''}`,
      importance: 'MEDIUM',
      tags: ['task_creation', task.priority.toLowerCase(), ...(extractedData.tags || [])]
    })

    // Gerar resposta personalizada
    const timeInfo = extractedData.startAt 
      ? ` para ${this.formatDate(extractedData.startAt)} às ${extractedData.startAt.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}`
      : ''

    const priorityText = this.getPriorityDescription(task.priority)
    const successMessage = this.getCreationSuccessMessage(userName, task.title, timeInfo, priorityText)

    return {
      success: true,
      taskAction: 'CREATED',
      message: successMessage,
      suggestionsMessage: this.getTaskSuggestion(task.priority)
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
    intent: TaskIntent, 
    userName: string
  ): Promise<any> {
    const { taskReference } = intent.extractedData
    
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
        message: message + '\n💬 Me diga o número da tarefa!'
      }
    }

    const task = tasks[0]
    await this.taskService.completeTask(task.id, userId)
    
    // Salvar padrão de conclusão
    const now = new Date()
    const isOnTime = !task.endAt || now <= task.endAt
    
    await this.memoryService.create({
      userId,
      type: 'PRODUCTIVITY_PATTERN',
      content: `Concluiu tarefa "${task.title}" (${task.priority}) ${isOnTime ? 'no prazo' : 'com atraso'}`,
      importance: 'MEDIUM',
      tags: ['task_completion', task.priority.toLowerCase(), isOnTime ? 'on_time' : 'late']
    })

    // Mensagem de sucesso personalizada
    const successMessage = this.getCompletionMessage(userName, task.title, task.priority, isOnTime)
    const celebration = this.getCelebrationMessage(task.priority, isOnTime)

    return {
      success: true,
      taskAction: 'COMPLETED',
      message: successMessage,
      suggestionsMessage: celebration
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
    intent: TaskIntent, 
    userName: string
  ): Promise<any> {
    const { taskReference } = intent.extractedData
    
    if (!taskReference) {
      const recentTasks = await this.taskService.findPendingTasks(userId)
      if (recentTasks.length === 0) {
        return {
          success: false,
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
    intent: TaskIntent, 
    userName: string
  ): Promise<any> {
    return {
      success: false,
      message: 'A funcionalidade de edição ainda está sendo aprimorada. Por enquanto, que tal remover a tarefa antiga e criar uma nova? 😊'
    }
  }

  private async handleSearchTasks(
    userId: string, 
    intent: TaskIntent, 
    userName: string
  ): Promise<any> {
    return {
      success: false,
      message: 'Pesquisa específica ainda em desenvolvimento. Use "listar tarefas" para ver todas! 📋'
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
