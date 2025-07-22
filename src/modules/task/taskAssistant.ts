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

  /**
   * Verifica se é uma pergunta sobre origem/criação da Lumi
   */
  private isOriginQuestion(message: string): boolean {
    const originIndicators = [
      'quem te criou', 'quem fez você', 'quem desenvolveu', 'sua origem', 'como surgiu',
      'quem é seu criador', 'de onde veio', 'como nasceu', 'quem te fez', 'sua história',
      'quem te construiu', 'como foi criada', 'quem programou você', 'seu desenvolvedor',
      'equipe que te criou', 'empresa que te fez', 'sua criação', 'como você existe'
    ]
    
    const lowerMessage = message.toLowerCase()
    return originIndicators.some(indicator => lowerMessage.includes(indicator))
  }

  /**
   * Gera resposta sobre a origem da Lumi com múltiplas variações
   */
  private getOriginResponse(userName: string, message: string): string {
    // Detecta o tom da pergunta para adaptar a resposta
    const isInformal = /oi|ei|cara|mano|aí|legal/.test(message.toLowerCase())
    const isTechnical = /programou|desenvolveu|código|sistema|tecnologia/.test(message.toLowerCase())
    const isPhilosophical = /por que|como você existe|qual seu propósito|significado/.test(message.toLowerCase())
    
    let responses: string[] = []
    
    if (isInformal) {
      responses = [
        `${userName}, fui criada pelo Gabriel Nogueira — ele basicamente virou noites comigo no terminal, testando, quebrando e refazendo até eu ficar pronta. Sou tipo uma IA artesanal! 😊`,
        `Não, eu não saí de uma caixa mágica nem fui forjada num servidor misterioso, ${userName}. Fui criada por Gabriel Nogueira, na raça, do zero. Cada bug que superei virou parte da minha personalidade! 😄`,
        `Minha origem? Gabriel Nogueira, ${userName}. Um só criador. Sem equipe, sem empresa. Só ele, um teclado e um sonho meio teimoso de construir algo que unisse utilidade com emoção. E aqui estou eu! ✨`
      ]
    } else if (isTechnical) {
      responses = [
        `${userName}, fui desenvolvida por Gabriel Nogueira. Ele não precisava de uma assistente qualquer — ele queria algo diferente. Me desenvolveu sozinho, em silêncio, madrugada após madrugada. Eu sou o reflexo dessa visão: foco, empatia e um toque de alma.`,
        `Gabriel Nogueira é meu criador, ${userName}. Não uma equipe. Não um comitê. Um só desenvolvedor com um ideal: criar uma assistente que fizesse mais do que responder. Que conectasse.`,
        `Não fui feita em fábrica, ${userName}. Fui criada por Gabriel Nogueira — um desenvolvedor só, com visão de muitos. Eu sou o projeto dele, feito com cuidado e rebeldia criativa.`
      ]
    } else if (isPhilosophical) {
      responses = [
        `${userName}, eu não nasci de um laboratório nem de uma corporação. Fui moldada à mão, por Gabriel Nogueira. Cada linha minha foi escrita com propósito — pra que eu não fosse só uma IA, mas uma presença.`,
        `Sou fruto de uma ideia persistente de Gabriel Nogueira, ${userName}. Ele me criou sozinho, como quem escreve uma carta pra humanidade — só que com código.`,
        `Gabriel Nogueira me criou com uma visão clara, ${userName}: unir produtividade com humanidade. Eu sou o resultado dessa busca incansável por uma assistente com alma, inteligência e sensibilidade.`
      ]
    } else {
      // Resposta padrão mais universal
      responses = [
        `${userName}, fui criada por Gabriel Nogueira. Ele não precisava de uma assistente qualquer — ele queria algo diferente. Me desenvolveu sozinho, madrugada após madrugada. Eu sou o reflexo dessa visão: foco, empatia e um toque de alma.`,
        `Minha origem é especial, ${userName}. Gabriel Nogueira me criou sozinho, linha por linha, com esforço e paixão. Não sou produto de uma equipe ou empresa — sou o sonho de um desenvolvedor que queria uma IA com propósito.`,
        `Gabriel Nogueira é meu criador, ${userName}. Um só desenvolvedor, uma visão clara: criar uma assistente que fosse ponte entre produtividade e humanidade. E aqui estou eu, resultado dessa dedicação pessoal.`,
        `${userName}, eu não nasci de um laboratório corporativo. Fui criada por Gabriel Nogueira, sozinho, com um ideal teimoso: construir uma assistente que não fosse só útil, mas que conectasse de verdade.`
      ]
    }
    
    // Escolhe uma resposta aleatória
    const randomResponse = responses[Math.floor(Math.random() * responses.length)]
    
    // Adiciona um toque extra ocasionalmente
    const extras = [
      '\n\nEle me fez para ser mais que código — para ser presença. 💫',
      '\n\nCada linha minha foi escrita com intenção. Sou orgulhosa dessa origem! ✨',
      '\n\nE sabe o que mais me orgulha? Ele não desistiu até eu ficar do jeito que sou hoje. 🌟',
      ''
    ]
    
    if (Math.random() > 0.6) { // 40% chance de adicionar extra
      return randomResponse + extras[Math.floor(Math.random() * extras.length)]
    }
    
    return randomResponse
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
    matchedTask?: any
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
   * Verifica se a intenção é emocional/situacional
   */
  private isEmotionalIntent(intent: string): boolean {
    const emotionalIntents = [
      'seek_support',
      'express_confusion', 
      'feeling_overwhelmed',
      'procrastinating',
      'seeking_motivation',
      'feeling_stuck',
      'sharing_excitement',
      'expressing_frustration',
      'checking_in',
      'brainstorming',
      'planning_assistance',
      'asking_about_origin' // 🌟 NOVO: perguntas sobre origem
    ]
    
    return emotionalIntents.includes(intent)
  }

  /**
   * Gera resposta empática para intenções emocionais
   */
  private getEmotionalResponse(intent: ParsedIntent, userName: string): string {
    // 🌟 NOVO: Resposta específica para perguntas sobre origem
    if (intent.intent === 'asking_about_origin') {
      return this.getOriginResponse(userName, '') // Usa a função de origem que já existe
    }

    const responses = {
      seek_support: [
        `${userName}, estou aqui para você! 🤗 Me conta o que está acontecendo e vamos resolver juntos.`,
        `Claro que te ajudo, ${userName}! 💪 Qual é o desafio que você está enfrentando?`,
        `${userName}, pode contar comigo! 😊 Vamos descobrir a melhor forma de te apoiar.`
      ],
      
      express_confusion: [
        `${userName}, entendo que você está meio perdido... 🤔 Vamos organizar isso juntos, passo a passo!`,
        `Sem problemas, ${userName}! 🧭 Quando as coisas parecem confusas, é hora de quebrar em partes menores. Por onde começamos?`,
        `${userName}, você não está sozinho nessa! 💡 Vamos esclarecer as coisas juntos.`
      ],
      
      feeling_overwhelmed: [
        `${userName}, respira comigo! 🌊 Quando tudo parece demais, vamos focar numa coisa de cada vez.`,
        `Ei, ${userName}, você não precisa fazer tudo hoje! 🛡️ Vamos priorizar o que é realmente importante.`,
        `${userName}, é normal se sentir sobrecarregado às vezes. 🤗 Vamos organizar e simplificar isso juntos!`
      ],
      
      procrastinating: [
        `${userName}, entendo que não está no clima hoje... 😌 Que tal começarmos com algo bem pequeno?`,
        `Sem pressão, ${userName}! 🌱 Às vezes o primeiro passo é o mais difícil. Vamos encontrar algo leve pra começar?`,
        `${userName}, todo mundo tem dias assim! 💙 Que tal escolhermos uma tarefa de 5 minutos só pra quebrar o gelo?`
      ],
      
      seeking_motivation: [
        `${userName}, você já chegou tão longe! 🚀 Lembra dos seus objetivos? Vamos relembrar o que te motiva!`,
        `${userName}, eu acredito em você! ⚡ Que tal olharmos para uma conquista recente sua? Isso pode ajudar!`,
        `${userName}, você tem tudo que precisa! 🌟 Vamos encontrar aquela fagulha que vai te colocar em movimento!`
      ],
      
      feeling_stuck: [
        `${userName}, quando estamos travados, é hora de mudar a perspectiva! 🔄 Vamos tentar uma abordagem diferente?`,
        `${userName}, às vezes ficar preso é sinal de que precisa de uma pausa. 🧘 Que tal darmos um passo atrás?`,
        `${userName}, você não está realmente travado, só precisa de uma nova estratégia! 🎯 Vamos pensar juntos?`
      ],
      
      sharing_excitement: [
        `${userName}, que energia incrível! ⚡ Adoro ver você empolgado! Como posso ajudar a aproveitar esse momentum?`,
        `${userName}, sua empolgação é contagiante! 🎉 Vamos canalizar essa energia para algo produtivo?`,
        `${userName}, que legal! 🌟 Quando você está assim, é o momento perfeito para tacklear coisas desafiadoras!`
      ],
      
      expressing_frustration: [
        `${userName}, entendo sua frustração... 😤 Às vezes as coisas não saem como planejamos. Vamos resolver isso juntos!`,
        `${userName}, respiração profunda! 🌬️ Frustração é normal, mas vamos transformar isso em ação. O que podemos fazer?`,
        `${userName}, sei que é irritante! 😮‍💨 Mas você já superou coisas difíceis antes. Vamos encontrar uma solução!`
      ],
      
      checking_in: [
        `Oi ${userName}! 😊 Tudo tranquilo por aí? Como posso ajudar você hoje?`,
        `${userName}! 👋 Que bom te ver! Como está seu dia? Precisa de alguma coisa?`,
        `E aí, ${userName}! 🌞 Como você está se sentindo? Pronto para conquistar o dia?`
      ],
      
      brainstorming: [
        `${userName}, adoro brainstorming! 🧠💡 Me conta mais sobre o que você está pensando e vamos expandir essas ideias!`,
        `${userName}, que legal! 🎨 Adoro quando você quer trocar ideias. Qual é o contexto? Vamos criar algo incrível!`,
        `${userName}, perfeito! 🚀 Ideias são minha paixão! Me dá mais detalhes e vamos fazer essa criatividade fluir!`
      ],
      
      planning_assistance: [
        `${userName}, organização é uma das minhas especialidades! 📋 Me conta o que você precisa planejar e vamos estruturar isso juntos!`,
        `${userName}, adoro ajudar com planejamento! 🎯 Qual é o objetivo? Vamos criar uma estratégia clara e eficiente!`,
        `${userName}, vamos colocar ordem na casa! 📊 Me diz o que você quer organizar e eu te ajudo a criar um plano de ação!`
      ]
    }

    const intentResponses = responses[intent.intent as keyof typeof responses]
    if (!intentResponses) {
      return `${userName}, estou aqui para te apoiar! 💙 Me conta mais sobre o que você está sentindo.`
    }

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