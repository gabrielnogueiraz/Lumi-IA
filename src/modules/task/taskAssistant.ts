import { TaskService, TaskCreateData } from './taskService'
import { taskManager } from './taskManager'
import { parseUserIntentFromLumi, ParsedIntent, hasTaskOrEmotionalPotential, decideBoardForTask } from '../../utils/intentParser'
import { MemoryService } from '../memory/memoryService'
import { prisma } from '../../prisma/client'

class TaskAssistant {
  private taskService: TaskService
  private taskManager = taskManager
  private memoryService: MemoryService

  constructor() {
    this.taskService = new TaskService()
    this.memoryService = new MemoryService()
  }

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
    isEmotionalResponse?: boolean
    emotionalState?: string
  }> {
    try {
      // Verificação expandida - inclui potencial emocional
      if (!hasTaskOrEmotionalPotential(message)) {
        return {
          success: false,
          message: this.getHelpfulResponse(userName, message)
        }
      }

      // Busca os quadros do usuário para contexto
      const userBoards = await this.getUserBoards(userId)

      // Usa o novo sistema LLM emocionalmente inteligente
      const intent = await parseUserIntentFromLumi(message, userId, userBoards)
      
      // Se foi detectada intenção emocional, retorna resposta adequada
      if (this.isEmotionalIntent(intent.intent)) {
        return {
          success: true,
          message: this.getEmotionalResponse(intent, userName),
          isEmotionalResponse: true,
          emotionalState: intent.emotionalState
        }
      }
      
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

  /**
   * Verifica se a intenção é emocional (não relacionada a tarefas práticas)
   */
  private isEmotionalIntent(intent: string): boolean {
    const emotionalIntents = [
      'seek_support', 'express_confusion', 'feeling_overwhelmed', 
      'procrastinating', 'seeking_motivation', 'feeling_stuck',
      'sharing_excitement', 'expressing_frustration', 'checking_in',
      'brainstorming', 'planning_assistance'
    ]
    return emotionalIntents.includes(intent)
  }

  /**
   * Gera resposta empática para intenções emocionais
   */
  private getEmotionalResponse(intent: ParsedIntent, userName: string): string {
    const responses = {
      seek_support: [
        `${userName}, estou aqui para te ajudar! 🤗 Me conta mais sobre o que você está precisando e vamos resolver juntos.`,
        `Claro que vou te ajudar, ${userName}! 💛 Pode compartilhar mais detalhes sobre o que te preocupa?`,
        `${userName}, você não está sozinho nisso! 🌟 Me fala mais sobre o que precisa e vamos encontrar uma solução.`
      ],
      
      express_confusion: [
        `Entendo que você está se sentindo perdido, ${userName}. 🧭 Vamos organizar isso juntos, passo a passo. Me conta sobre o que especificamente está te confundindo?`,
        `${userName}, é super normal se sentir confuso às vezes! 💭 Que tal quebrarmos isso em partes menores? Por onde você gostaria de começar?`,
        `Vamos juntos clarear essa confusão, ${userName}! 🔍 Me explica um pouco mais sobre a situação e eu te ajudo a organizar as ideias.`
      ],
      
      feeling_overwhelmed: [
        `${userName}, respira fundo comigo! 🌊 Quando tem muita coisa, o melhor é focar em uma de cada vez. Qual é a mais urgente agora?`,
        `Ei, ${userName}, eu vejo que está pesado demais! 😮‍💨 Que tal organizarmos por prioridade? Não precisa fazer tudo hoje.`,
        `${userName}, vamos desacelerar um pouco? 🛑 Me conta quais são as principais coisas que estão te sobrecarregando e vamos priorizar juntos.`
      ],
      
      procrastinating: [
        `${userName}, às vezes a gente não está no clima mesmo! 😅 Que tal começarmos com algo bem pequeno? Só 5 minutinhos?`,
        `Entendo, ${userName}! 🐌 Procrastinação é normal. Qual seria a menor ação possível que você conseguiria fazer agora?`,
        `${userName}, que tal mudamos a estratégia? 🎯 Em vez de "fazer tudo", que tal "só começar"? O primeiro passo pode ser bem simples!`
      ],
      
      seeking_motivation: [
        `${userName}, você veio ao lugar certo! ⚡ Lembra do seu potencial incrível? Você já conseguiu tantas coisas! O que te motivava nessas conquistas?`,
        `Vamos reacender essa chama, ${userName}! 🔥 Me conta sobre um objetivo que te empolga e vamos criar um plano para chegar lá!`,
        `${userName}, você é muito mais forte do que imagina! 💪 Que tal definirmos uma pequena vitória para hoje? Algo que vai te dar aquele gosto de "consegui"!`
      ],
      
             feeling_stuck: [
         `${userName}, já passou por isso antes e saiu! 🚪 Às vezes precisamos de uma perspectiva diferente. Me conta mais sobre onde você sente que travou?`,
         `Vamos destravar isso juntos, ${userName}! 🔓 Que tal tentarmos uma abordagem completamente diferente? O que você ainda não tentou?`,
         `${userName}, estar "travado" é só uma pausa para reorganizar a estratégia! 🔄 Me fala sobre o que você já tentou e vamos encontrar novos caminhos.`
       ],
      
      sharing_excitement: [
        `${userName}, que energia incrível! ⚡ Adorei ver você assim empolgado! Me conta mais sobre o que te deixou tão animado!`,
        `ADOREI, ${userName}! 🎉 Essa empolgação é contagiante! Como podemos aproveitar essa energia toda para fazer coisas incríveis?`,
        `${userName}, que maravilha! ✨ Você radiando energia positiva assim é lindo de ver! Conta mais dessa novidade!`
      ],
      
      expressing_frustration: [
        `${userName}, entendo sua frustração! 😤 Às vezes as coisas realmente não funcionam como queremos. Me conta o que está te irritando?`,
        `Respira, ${userName}! 😮‍💨 Frustrações fazem parte, mas vamos juntos encontrar uma saída. O que especificamente não está funcionando?`,
        `${userName}, válido estar frustrado! 🤯 Que tal darmos uma pausa e pensarmos numa abordagem diferente? Me explica o que está travando.`
      ],
      
      checking_in: [
        `Oi, ${userName}! 😊 Que bom ver você por aqui! Como você está se sentindo hoje? Como posso te ajudar?`,
        `${userName}, sempre um prazer! 💛 E aí, como estão as coisas? Precisa de alguma coisa específica ou só quer bater um papo?`,
        `Hey, ${userName}! 👋 Como tem passado? Estou aqui se precisar de qualquer coisa - desde organizar a agenda até só conversar!`
      ],
      
      brainstorming: [
        `${userName}, adorei! 💡 Sessão de brainstorming é comigo mesma! Me conta mais sobre o projeto e vamos gerar ideias incríveis juntos!`,
        `Perfeito, ${userName}! 🧠✨ Adoro ajudar com ideias criativas! Me dá mais contexto sobre o que você está pensando e vamos expandir isso!`,
        `${userName}, que legal! 🎨 Vamos soltar a criatividade! Me fala sobre o tema e vamos fazer uma chuva de ideias bem produtiva!`
      ],
      
      planning_assistance: [
        `${userName}, organização é minha especialidade! 📋 Vamos estruturar isso direitinho! Me conta sobre o que você quer planejar.`,
        `Ótimo, ${userName}! 🗓️ Adoro ajudar a organizar e planejar! Me dá mais detalhes sobre o que você precisa estruturar.`,
        `${userName}, vamos fazer um planejamento nota 10! 📈 Me conta sobre o que você quer organizar e qual é o seu objetivo principal.`
      ]
    }

    const intentResponses = responses[intent.intent as keyof typeof responses] || responses.seek_support
    return intentResponses[Math.floor(Math.random() * intentResponses.length)]
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
      // 🔧 CORREÇÃO PROBLEMA 2: Decisão inteligente sobre qual quadro usar
      const boardDecision = decideBoardForTask(intent, userBoards || [])
      
      console.log('🔍 DEBUG - Board Decision:', boardDecision)
      
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
        // 🔧 CORREÇÃO: Usar quadro existente - buscar primeira coluna disponível
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
        // Fallback: usar coluna padrão do usuário
        targetColumnId = await this.taskService.getDefaultColumn(userId)
        boardInfo = ` no quadro padrão`
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
        content: `Criou tarefa "${newTask.title}" com prioridade ${newTask.priority}${newTask.startAt ? ` para ${newTask.startAt.toLocaleString('pt-BR')}` : ''}${boardInfo}`,
        importance: 'MEDIUM',
        tags: ['task_creation', newTask.priority.toLowerCase(), ...(intent.tags || [])]
      })

      // 🔧 CORREÇÃO PROBLEMA 1: Gerar resposta personalizada com timezone correto
      const timeInfo = newTask.startAt 
        ? ` para ${this.formatDate(newTask.startAt)} às ${this.formatTimeWithCorrectTimezone(newTask.startAt)}`
        : ''

      const priorityText = this.getPriorityDescription(newTask.priority)
      const successMessage = this.getCreationSuccessMessage(userName, newTask.title, timeInfo + boardInfo, priorityText)

      return {
        success: true,
        taskAction: 'CREATED',
        message: successMessage,
        suggestionsMessage: this.getTaskSuggestion(newTask.priority, newTask.title, boardDecision.boardName)
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

  // 🔧 CORREÇÃO PROBLEMA 1: Método para formatar horário brasileiro
  private formatTimeWithCorrectTimezone(date: Date): string {
    // Como a data já vem correta do LLM (agora com prompt corrigido), 
    // apenas formatamos normalmente
    return date.toLocaleTimeString('pt-BR', { 
      hour: '2-digit', 
      minute: '2-digit'
    })
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
    try {
      // Buscar tarefas do usuário
      const tasks = await prisma.tasks.findMany({
        where: { 
          userId,
          completed: false // Só tarefas não concluídas
        },
        include: {
          columns: {
            include: {
              boards: true
            }
          }
        },
        orderBy: [
          { priority: 'desc' },
          { startAt: 'asc' }
        ]
      })

      if (tasks.length === 0) {
        return {
          success: true,
          taskAction: 'LISTED_EMPTY',
          message: `${userName}, sua agenda está limpinha! 🎉 Hora de relaxar ou planejar novas conquistas?`
        }
      }

      // Agrupar tarefas por data
      const today = new Date()
      const tomorrow = new Date(today)
      tomorrow.setDate(today.getDate() + 1)
      
      const todayTasks = tasks.filter(task => 
        task.startAt && this.isSameDate(task.startAt, today)
      )
      
      const tomorrowTasks = tasks.filter(task => 
        task.startAt && this.isSameDate(task.startAt, tomorrow)
      )
      
      const otherTasks = tasks.filter(task => 
        !task.startAt || (!this.isSameDate(task.startAt, today) && !this.isSameDate(task.startAt, tomorrow))
      )

      let message = `📋 Aqui está sua agenda, ${userName}:\n\n`

      // Tarefas de hoje
      if (todayTasks.length > 0) {
        message += `🌅 **HOJE (${today.toLocaleDateString('pt-BR', { day: 'numeric', month: 'short' })})**\n`
        todayTasks.forEach(task => {
          // 🔧 CORREÇÃO: Usar formatação de timezone corrigida
          const timeStr = task.startAt ? ` às ${this.formatTimeWithCorrectTimezone(task.startAt)}` : ''
          const priorityIcon = this.getPriorityIcon(task.priority)
          const boardName = task.columns?.boards?.title || 'Sem quadro'
          message += `${priorityIcon} ${task.title}${timeStr} (${boardName})\n`
        })
        message += '\n'
      }

      // Tarefas de amanhã
      if (tomorrowTasks.length > 0) {
        message += `🌤️ **AMANHÃ (${tomorrow.toLocaleDateString('pt-BR', { day: 'numeric', month: 'short' })})**\n`
        tomorrowTasks.forEach(task => {
          // 🔧 CORREÇÃO: Usar formatação de timezone corrigida
          const timeStr = task.startAt ? ` às ${this.formatTimeWithCorrectTimezone(task.startAt)}` : ''
          const priorityIcon = this.getPriorityIcon(task.priority)
          const boardName = task.columns?.boards?.title || 'Sem quadro'
          message += `${priorityIcon} ${task.title}${timeStr} (${boardName})\n`
        })
        message += '\n'
      }

      // Outras tarefas
      if (otherTasks.length > 0) {
        message += `📅 **OUTRAS TAREFAS**\n`
        otherTasks.forEach(task => {
          // 🔧 CORREÇÃO: Usar formatação de timezone corrigida
          const dateStr = task.startAt ? `${this.formatDate(task.startAt)} às ${this.formatTimeWithCorrectTimezone(task.startAt)}` : 'Sem data'
          const priorityIcon = this.getPriorityIcon(task.priority)
          const boardName = task.columns?.boards?.title || 'Sem quadro'
          message += `${priorityIcon} ${task.title} - ${dateStr} (${boardName})\n`
        })
      }

      message += `\n💡 Total: ${tasks.length} tarefa${tasks.length > 1 ? 's' : ''} pendente${tasks.length > 1 ? 's' : ''}`

      return {
        success: true,
        taskAction: 'LISTED',
        message
      }

    } catch (error) {
      console.error('Erro ao listar tarefas:', error)
      return {
        success: false,
        message: `${userName}, tive um problema ao buscar suas tarefas. Tente novamente! 🤖`
      }
    }
  }

  private isSameDate(date1: Date, date2: Date): boolean {
    return date1.toDateString() === date2.toDateString()
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

  private getTaskSuggestion(priority: string, taskTitle?: string, boardName?: string): string {
    const taskContext = (taskTitle || '').toLowerCase()
    const board = (boardName || '').toLowerCase()
    
    // Dicas contextuais baseadas no tipo de tarefa/quadro
    if (board.includes('academia') || board.includes('treino') || board.includes('exercício') || 
        taskContext.includes('treino') || taskContext.includes('academia') || taskContext.includes('exercício')) {
      const tips = [
        '🏋️ Dica: Hidrate-se bem durante o treino. Quer que eu te lembre de beber água?',
        '⚡ Dica: Para treino de perna, foque em exercícios compostos como agachamento e stiff. Precisa de sugestões?',
        '🎯 Dica: Registre seus pesos e séries para acompanhar evolução. Posso criar lembretes para isso!',
        '🧘 Dica: Não esqueça do alongamento pós-treino. Quer que eu adicione na sua agenda?'
      ]
      return tips[Math.floor(Math.random() * tips.length)]
    }
    
    if (board.includes('trabalho') || board.includes('profissional') || 
        taskContext.includes('reunião') || taskContext.includes('projeto') || taskContext.includes('apresentação')) {
      const tips = [
        '📝 Dica: Para reuniões importantes, prepare uma agenda antecipadamente. Posso te ajudar a estruturar?',
        '🎯 Dica: Defina objetivos claros para cada projeto. Quer quebrar essa tarefa em etapas menores?',
        '⏰ Dica: Reserve 15 min antes de reuniões para revisar materiais. Adiciono um lembrete?',
        '💡 Dica: Use a técnica Pomodoro para projetos complexos. Posso configurar intervalos para você?',
        '📊 Dica: Documente decisões importantes. Precisa de ajuda para organizar um template?'
      ]
      return tips[Math.floor(Math.random() * tips.length)]
    }
    
    if (board.includes('estudo') || board.includes('faculdade') || board.includes('curso') ||
        taskContext.includes('estudar') || taskContext.includes('prova') || taskContext.includes('aula')) {
      const tips = [
        '📚 Dica: Use técnicas de revisão espaçada para melhor retenção. Posso criar um cronograma?',
        '🧠 Dica: Faça pausas de 15 min a cada hora de estudo. Adiciono lembretes automáticos?',
        '✏️ Dica: Pratique exercícios antes da prova. Quer que eu programe sessões de revisão?',
        '🎯 Dica: Divida conteúdos grandes em blocos menores. Precisa de ajuda para organizar?',
        '💡 Dica: Ensine o que aprendeu para fixar melhor. Posso sugerir formas de praticar?'
      ]
      return tips[Math.floor(Math.random() * tips.length)]
    }
    
    if (board.includes('saúde') || board.includes('médico') || 
        taskContext.includes('médico') || taskContext.includes('consulta') || taskContext.includes('exame')) {
      const tips = [
        '📋 Dica: Leve histórico médico e lista de medicamentos. Quer que eu organize isso?',
        '⏰ Dica: Chegue 15 min antes da consulta. Adiciono um lembrete?',
        '💊 Dica: Anote orientações médicas durante a consulta. Precisa de um template?',
        '📱 Dica: Confirme a consulta um dia antes. Posso programar um lembrete automático?'
      ]
      return tips[Math.floor(Math.random() * tips.length)]
    }
    
    if (board.includes('compras') || board.includes('mercado') || 
        taskContext.includes('comprar') || taskContext.includes('mercado')) {
      const tips = [
        '🛒 Dica: Faça uma lista organizada por seções do mercado. Posso te ajudar a estruturar?',
        '💰 Dica: Defina um orçamento antes de sair. Quer que eu calcule um valor ideal?',
        '📝 Dica: Verifique o que já tem em casa primeiro. Posso criar uma checklist?',
        '🥗 Dica: Planeje refeições da semana para comprar apenas o necessário. Precisa de ideias?',
        '⏰ Dica: Evite ir ao mercado com fome para não comprar por impulso!'
      ]
      return tips[Math.floor(Math.random() * tips.length)]
    }
    
    // Dicas baseadas na prioridade quando não há contexto específico
    switch (priority) {
      case 'HIGH':
        const highPriorityTips = [
          '🔥 Dica: Tarefas urgentes são melhores feitas logo pela manhã! Quer reorganizar sua agenda?',
          '⚡ Dica: Elimine distrações para tarefas importantes. Posso sugerir técnicas de foco?',
          '🎯 Dica: Quebre tarefas grandes em etapas menores. Precisa de ajuda para planejar?',
          '💪 Dica: Use sua energia máxima para prioridades altas. Quer dicas de produtividade?'
        ]
        return highPriorityTips[Math.floor(Math.random() * highPriorityTips.length)]
        
      case 'LOW':
        const lowPriorityTips = [
          '😌 Dica: Tarefas simples são ótimas para intervalos entre atividades importantes!',
          '🌱 Dica: Use tarefas leves para fazer pausas ativas. Quer sugestões?',
          '📦 Dica: Agrupe várias tarefas simples e faça de uma vez só!',
          '⏰ Dica: Reserve horários vagos para completar pendências menores.'
        ]
        return lowPriorityTips[Math.floor(Math.random() * lowPriorityTips.length)]
        
      default:
        const mediumPriorityTips = [
          '📊 Dica: Organize tarefas por contexto para ser mais eficiente. Posso te ajudar?',
          '⚖️ Dica: Balance tarefas médias com as de alta prioridade no seu dia!',
          '⏱️ Dica: Use blocos de tempo para tarefas de complexidade média.',
          '🎯 Dica: Mantenha foco mas sem pressão excessiva. Precisa de técnicas de concentração?'
        ]
        return mediumPriorityTips[Math.floor(Math.random() * mediumPriorityTips.length)]
    }
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