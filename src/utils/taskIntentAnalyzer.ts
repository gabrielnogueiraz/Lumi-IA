export interface TaskIntent {
  action: 'CREATE' | 'UPDATE' | 'DELETE' | 'COMPLETE' | 'LIST' | 'SEARCH' | 'NONE'
  confidence: number
  extractedData: {
    title?: string
    description?: string
    priority?: 'HIGH' | 'MEDIUM' | 'LOW'
    startAt?: Date
    endAt?: Date
    pomodoroGoal?: number
    tags?: string[]
    taskReference?: string
  }
  conflictCheck?: boolean
}

export function analyzeTaskIntent(message: string): TaskIntent {
  const lowerMessage = message.toLowerCase()
  
  // FASE 1: Verifica se é realmente sobre tarefas/agenda
  const isTaskRelated = isMessageAboutTasks(message)
  
  if (!isTaskRelated) {
    return {
      action: 'NONE',
      confidence: 0,
      extractedData: {}
    }
  }
  
  // FASE 2: Se é sobre tarefas, detecta a ação específica
  let action: TaskIntent['action'] = 'NONE'
  let confidence = 0
  
  // Palavras-chave mais específicas e precisas
  const createKeywords = [
    'agendar', 'marcar', 'anotar na agenda', 'colocar na agenda', 'bloquear horário',
    'reservar horário', 'adicionar tarefa', 'criar tarefa'
  ]
  
  const listKeywords = [
    'minha agenda', 'minhas tarefas', 'o que tenho', 'quais tarefas', 'agenda de hoje',
    'compromissos de', 'horários de', 'programação de'
  ]
  
  const completeKeywords = [
    'terminei', 'acabei', 'completei', 'finalizei', 'concluí', 'está pronto', 'já fiz'
  ]
  
  const deleteKeywords = [
    'cancelar', 'remarcar', 'remover da agenda', 'tirar da agenda', 'desmarcar'
  ]

  // Detecção por contexto específico (mais confiável)
  if (isDefiniteTaskCreation(message)) {
    action = 'CREATE'
    confidence = 0.9
  } else if (isDefiniteTaskListing(message)) {
    action = 'LIST'
    confidence = 0.85
  } else if (isDefiniteTaskCompletion(message)) {
    action = 'COMPLETE'
    confidence = 0.85
  } else if (isDefiniteTaskDeletion(message)) {
    action = 'DELETE'
    confidence = 0.85
  } else if (createKeywords.some(kw => lowerMessage.includes(kw))) {
    action = 'CREATE'
    confidence = 0.7
  } else if (listKeywords.some(kw => lowerMessage.includes(kw))) {
    action = 'LIST'
    confidence = 0.7
  } else if (completeKeywords.some(kw => lowerMessage.includes(kw))) {
    action = 'COMPLETE'
    confidence = 0.7
  } else if (deleteKeywords.some(kw => lowerMessage.includes(kw))) {
    action = 'DELETE'
    confidence = 0.7
  }

  const extractedData: TaskIntent['extractedData'] = {}

  if (action === 'CREATE') {
    extractedData.title = extractTaskTitle(message)
    extractedData.priority = extractPriority(message)
    extractedData.description = extractDescription(message)
    
    const timeInfo = extractTimeInfo(message)
    extractedData.startAt = timeInfo.startAt
    extractedData.endAt = timeInfo.endAt
    
    extractedData.pomodoroGoal = extractPomodoroGoal(message)
    extractedData.tags = extractTags(message)
    
    // Aumenta confiança para tarefas importantes
    if (extractedData.priority === 'HIGH' || 
        lowerMessage.includes('importante') || 
        lowerMessage.includes('urgente') ||
        lowerMessage.includes('crítico')) {
      confidence += 0.1
    }
    
    // Aumenta confiança se tem horário específico
    if (extractedData.startAt) {
      confidence += 0.05
    }
  }

  if (action === 'DELETE' || action === 'COMPLETE') {
    extractedData.taskReference = extractTaskReference(message)
  }

  return {
    action,
    confidence: Math.min(confidence, 1),
    extractedData,
    conflictCheck: extractedData.priority === 'HIGH' || 
                   lowerMessage.includes('importante') ||
                   lowerMessage.includes('urgente')
  }
}

function extractTaskTitle(message: string): string {
  // Remove palavras de ação e conectores comuns
  let cleanMessage = message
    .replace(/\b(adicionar|criar|agendar|marcar|incluir|colocar|anotar|lembrar|preciso|tenho|vou ter)\b/gi, '')
    .replace(/\b(na|minha|agenda|hoje|amanhã|para|ontem|depois)\b/gi, '')
    .replace(/\b(às|as|at|em|no|dia|hora)\s+\d+[:h]?\d{0,2}/gi, '')
    .replace(/\b(importante|urgente|prioritário|crítico)\b/gi, '')
    .replace(/\b(manhã|tarde|noite)\b/gi, '')
    .trim()
  
  // Procura por padrões específicos de tarefas
  const taskPatterns = [
    /\b(reunião|meeting|encontro)\s+(.+)/i,
    /\b(projeto|trabalho)\s+(.+)/i,
    /\b(consulta|médico)\s+(.+)/i,
    /\b(compromisso|evento)\s+(.+)/i,
    /\b(tarefa|task)\s+(.+)/i
  ]
  
  for (const pattern of taskPatterns) {
    const match = cleanMessage.match(pattern)
    if (match && match[2]) {
      cleanMessage = match[0].trim()
      break
    }
  }
  
  // Remove artigos e preposições do início
  cleanMessage = cleanMessage
    .replace(/^(uma|um|a|o|com|para|de)\s+/i, '')
    .replace(/\s+(às|as|at|em|no|dia)\s+.*$/i, '')
    .trim()
  
  // Se não encontrou nada significativo, tenta extrair a parte principal
  if (!cleanMessage || cleanMessage.length < 3) {
    const words = message.split(' ').filter(word => 
      word.length > 2 && 
      !['hoje', 'amanhã', 'para', 'com', 'pela', 'pelo', 'das', 'nos'].includes(word.toLowerCase())
    )
    cleanMessage = words.slice(0, 4).join(' ')
  }
  
  return cleanMessage || 'Nova tarefa'
}

function extractPriority(message: string): 'HIGH' | 'MEDIUM' | 'LOW' {
  const lowerMessage = message.toLowerCase()
  
  // Palavras-chave para alta prioridade
  const highPriorityKeywords = [
    'importante', 'urgente', 'prioritário', 'crítico', 'essencial',
    'imperdível', 'fundamental', 'obrigatório', 'crucial', 'emergência',
    'asap', 'imediato', 'inadiável', 'vital', 'grave'
  ]
  
  // Palavras-chave para baixa prioridade
  const lowPriorityKeywords = [
    'quando der', 'se possível', 'talvez', 'opcional', 'se sobrar tempo',
    'simples', 'rápido', 'básico', 'tranquilo', 'eventual', 'se conseguir',
    'não urgente', 'sem pressa', 'flexível'
  ]
  
  // Contextos que indicam alta prioridade
  const highPriorityContexts = [
    /reunião.*diretor|ceo|presidente|liderança/i,
    /apresentação.*cliente|board|diretoria/i,
    /entrega.*hoje|amanhã/i,
    /deadline.*hoje|amanhã/i,
    /médico|hospital|emergência/i,
    /prova|exame.*importante/i
  ]
  
  // Contextos que indicam baixa prioridade
  const lowPriorityContexts = [
    /organizar.*arquivo|gaveta|mesa/i,
    /lembrar.*comprar|buscar/i,
    /quando.*tempo.*livre/i,
    /talvez.*fazer/i
  ]
  
  // Verifica contextos primeiro (mais específico)
  if (highPriorityContexts.some(pattern => pattern.test(message))) {
    return 'HIGH'
  }
  
  if (lowPriorityContexts.some(pattern => pattern.test(message))) {
    return 'LOW'
  }
  
  // Verifica palavras-chave
  if (highPriorityKeywords.some(kw => lowerMessage.includes(kw))) {
    return 'HIGH'
  }
  
  if (lowPriorityKeywords.some(kw => lowerMessage.includes(kw))) {
    return 'LOW'
  }
  
  // Prioridade baseada em horário
  const hasSpecificTime = /\b\d{1,2}[:h]\d{2}\b|\b\d{1,2}\s*(da\s+)?(manhã|tarde|noite)\b/i.test(message)
  const isToday = /\bhoje\b/i.test(message)
  
  if (hasSpecificTime && isToday) {
    return 'HIGH'
  }
  
  return 'MEDIUM'
}

function extractTimeInfo(message: string): { startAt?: Date, endAt?: Date } {
  const today = new Date()
  const tomorrow = new Date(today)
  tomorrow.setDate(tomorrow.getDate() + 1)
  
  // Padrões de horário mais abrangentes
  const timePatterns = [
    /\b(\d{1,2})[:h](\d{2})\b/gi,                    // 14:30, 14h30
    /\b(\d{1,2})\s*horas?\b/gi,                      // 14 horas
    /\b(\d{1,2})\s*(da\s+)?(manhã|tarde|noite)\b/gi, // 2 da tarde
    /\bmeio[- ]dia\b/gi,                             // meio-dia
    /\bmeia[- ]noite\b/gi                            // meia-noite
  ]
  
  // Padrões de data mais específicos
  const dayPatterns = [
    { pattern: /\bhoje\b/i, offset: 0 },
    { pattern: /\bamanhã\b/i, offset: 1 },
    { pattern: /\bdepois de amanhã\b/i, offset: 2 },
    { pattern: /\bsegunda[- ]feira\b/i, dayOfWeek: 1 },
    { pattern: /\bterça[- ]feira\b/i, dayOfWeek: 2 },
    { pattern: /\bquarta[- ]feira\b/i, dayOfWeek: 3 },
    { pattern: /\bquinta[- ]feira\b/i, dayOfWeek: 4 },
    { pattern: /\bsexta[- ]feira\b/i, dayOfWeek: 5 },
    { pattern: /\bsábado\b/i, dayOfWeek: 6 },
    { pattern: /\bdomingo\b/i, dayOfWeek: 0 }
  ]
  
  let targetDate = new Date(today)
  let hour: number | null = null
  
  // Detecta o dia
  for (const dayPattern of dayPatterns) {
    if (dayPattern.pattern.test(message)) {
      if (dayPattern.offset !== undefined) {
        targetDate = new Date(today)
        targetDate.setDate(today.getDate() + dayPattern.offset)
      } else if (dayPattern.dayOfWeek !== undefined) {
        targetDate = getNextWeekday(today, dayPattern.dayOfWeek)
      }
      break
    }
  }
  
  // Detecta o horário
  for (const pattern of timePatterns) {
    const matches = [...message.matchAll(pattern)]
    if (matches.length > 0) {
      const match = matches[0]
      hour = extractHourFromMatch(match)
      break
    }
  }
  
  // Casos especiais
  if (/\bmeio[- ]dia\b/i.test(message)) {
    hour = 12
  } else if (/\bmeia[- ]noite\b/i.test(message)) {
    hour = 0
  }
  
  if (hour !== null) {
    const taskDate = new Date(targetDate)
    taskDate.setHours(hour, 0, 0, 0)
    
    // Estima duração baseada no tipo de tarefa
    let duration = 60 // 1 hora por padrão
    
    if (/reunião|meeting|encontro/i.test(message)) {
      duration = 60 // reuniões geralmente 1h
    } else if (/consulta|médico/i.test(message)) {
      duration = 30 // consultas geralmente 30min
    } else if (/apresentação|workshop/i.test(message)) {
      duration = 120 // apresentações geralmente 2h
    }
    
    return {
      startAt: taskDate,
      endAt: new Date(taskDate.getTime() + duration * 60 * 1000)
    }
  }
  
  return {}
}

function getNextWeekday(date: Date, targetDay: number): Date {
  const result = new Date(date)
  const currentDay = date.getDay()
  const daysUntilTarget = (targetDay - currentDay + 7) % 7
  
  if (daysUntilTarget === 0) {
    // Se é o mesmo dia da semana, pega a próxima semana
    result.setDate(date.getDate() + 7)
  } else {
    result.setDate(date.getDate() + daysUntilTarget)
  }
  
  return result
}

function extractHourFromMatch(match: RegExpMatchArray): number | null {
  if (!match[1]) return null
  
  let hour = parseInt(match[1])
  const context = match[0].toLowerCase()
  
  // Ajusta baseado no contexto
  if (context.includes('tarde') && hour < 12) {
    hour += 12
  } else if (context.includes('noite') && hour < 12) {
    hour += 12
  } else if (context.includes('manhã') && hour > 12) {
    hour -= 12
  }
  
  return hour >= 0 && hour <= 23 ? hour : null
}

function extractPomodoroGoal(message: string): number {
  // Padrões mais abrangentes para detectar metas de pomodoro
  const pomodoroPatterns = [
    /(\d+)\s*(pomodoro|sessão|sessões|ciclo|ciclos)/gi,
    /em\s+(\d+)\s*(sessão|sessões)/gi,
    /fazer\s+(\d+)\s*pomodoros?/gi
  ]
  
  for (const pattern of pomodoroPatterns) {
    const match = message.match(pattern)
    if (match && match[1]) {
      const goal = parseInt(match[1])
      return goal > 0 && goal <= 20 ? goal : 1
    }
  }
  
  // Se é uma tarefa complexa, sugere mais pomodoros
  if (/projeto|apresentação|estudo|relatório|análise/i.test(message)) {
    return 2
  }
  
  return 1
}

function extractTaskReference(message: string): string | undefined {
  const lowerMessage = message.toLowerCase()
  
  // Padrões para referenciar tarefas específicas
  const referencePatterns = [
    /\b(a|o)\s+(reunião|projeto|tarefa|compromisso|evento|consulta)\s*([^,\.!?]*)/gi,
    /\b(aquela?|essa?|esta?)\s+([^,\.!?]+)/gi,
    /\b(primeira|segunda|terceira|última)\s+(tarefa|reunião|compromisso)/gi,
    /\bnúmero\s+(\d+)/gi,
    /\b(\d+)[ºª]?\s*(tarefa|item)/gi
  ]
  
  // Procura por padrões específicos primeiro
  for (const pattern of referencePatterns) {
    const matches = [...message.matchAll(pattern)]
    if (matches.length > 0) {
      const match = matches[0]
      let reference = match[0].trim()
      
      // Limpa a referência
      reference = reference
        .replace(/\b(concluir|finalizar|terminar|completar|remover|deletar|cancelar)\b/gi, '')
        .trim()
      
      if (reference.length > 2) {
        return reference
      }
    }
  }
  
  // Procura por palavras-chave de tipos de tarefa
  const taskTypeKeywords = [
    'reunião', 'meeting', 'projeto', 'tarefa', 'compromisso', 'evento',
    'consulta', 'médico', 'dentista', 'apresentação', 'workshop',
    'entrevista', 'call', 'ligação', 'curso', 'aula'
  ]
  
  for (const keyword of taskTypeKeywords) {
    const regex = new RegExp(`\\b${keyword}\\b`, 'i')
    if (regex.test(message)) {
      // Tenta capturar contexto ao redor da palavra-chave
      const contextRegex = new RegExp(`\\b${keyword}\\s+([^,\\.!?]{0,30})`, 'i')
      const match = message.match(contextRegex)
      if (match && match[1] && match[1].trim().length > 0) {
        return `${keyword} ${match[1].trim()}`
      }
      return keyword
    }
  }
  
  // Se não encontrou nada específico, tenta extrair palavras significativas
  const words = message.split(' ').filter(word => 
    word.length > 3 && 
    !['hoje', 'amanhã', 'para', 'com', 'pela', 'pelo', 'das', 'nos', 'que', 'esta', 'essa', 'aquela'].includes(word.toLowerCase())
  )
  
  if (words.length > 0) {
    return words.slice(0, 2).join(' ')
  }
  
  return undefined
}

// Funções auxiliares para detecção de contexto mais inteligente

// FUNÇÃO PRINCIPAL: Determina se a mensagem é realmente sobre tarefas/agenda
function isMessageAboutTasks(message: string): boolean {
  const lowerMessage = message.toLowerCase()
  
  // Palavras/frases que claramente indicam gestão de tarefas/agenda
  const explicitTaskIndicators = [
    'agenda', 'tarefas', 'compromissos', 'horários', 'programação',
    'agendar', 'marcar', 'cancelar compromisso', 'remarcar',
    'minha agenda', 'minhas tarefas', 'o que tenho hoje',
    'bloquear horário', 'reservar horário', 'adicionar tarefa',
    'lista de afazeres', 'to-do', 'planner'
  ]
  
  // Contextos que claramente são sobre agenda/tarefas
  const taskContextPatterns = [
    /agenda\s+(de\s+)?(hoje|amanhã|semana)/i,
    /(marcar|agendar|cancelar)\s+(reunião|consulta|compromisso)/i,
    /(o\s+que|quais)\s+(tenho|são\s+meus)\s+(hoje|amanhã)/i,
    /horário\s+(livre|ocupado|disponível)/i,
    /(adicionar|incluir|colocar)\s+na\s+agenda/i,
    /lembrar\s+de\s+(fazer|ir\s+em|comparecer)/i
  ]
  
  // Se tem indicadores explícitos ou padrões claros, é sobre tarefas
  if (explicitTaskIndicators.some(indicator => lowerMessage.includes(indicator)) ||
      taskContextPatterns.some(pattern => pattern.test(message))) {
    return true
  }
  
  // Casos específicos que podem ser confundidos (devem retornar FALSE)
  if (isDefinitelyNotTaskRelated(message)) {
    return false
  }
  
  // Se tem data/hora + ação específica, pode ser tarefa
  const hasDateTime = /\b(hoje|amanhã|segunda|terça|quarta|quinta|sexta|sábado|domingo)\b/i.test(message) ||
                     /\d{1,2}[:h]\d{2}/i.test(message)
  
  const hasActionableVerb = /\b(ir|fazer|estudar|trabalhar|completar|terminar|começar)\b/i.test(message)
  
  // Só considera tarefa se tem AMBOS: tempo E ação E contexto específico
  if (hasDateTime && hasActionableVerb) {
    const specificTaskWords = ['reunião', 'consulta', 'apresentação', 'projeto', 'deadline']
    return specificTaskWords.some(word => lowerMessage.includes(word))
  }
  
  return false
}

function isDefinitelyNotTaskRelated(message: string): boolean {
  const lowerMessage = message.toLowerCase()
  
  // Contextos que claramente NÃO são sobre tarefas
  const nonTaskContexts = [
    'consegue me ajudar', 'pode me ajudar', 'me ajuda',
    'como fazer', 'como criar', 'como escrever',
    'dicas para', 'sugestões de', 'ideias para',
    'o que você acha', 'qual sua opinião',
    'me explica', 'me conta', 'me fala sobre',
    'planejamento de conteúdo', 'estratégia de', 'brainstorm',
    'posts para', 'conteúdo para', 'texto para'
  ]
  
  return nonTaskContexts.some(context => lowerMessage.includes(context))
}

function isDefiniteTaskCreation(message: string): boolean {
  const definiteCreationPatterns = [
    /agendar\s+(reunião|consulta|compromisso)/i,
    /marcar\s+(consulta|reunião|horário)/i,
    /adicionar\s+na\s+agenda/i,
    /colocar\s+na\s+agenda/i,
    /bloquear\s+horário/i,
    /reservar\s+(horário|tempo)/i,
    /(tenho|vou\s+ter)\s+(reunião|consulta|compromisso)\s+(hoje|amanhã)/i
  ]
  
  return definiteCreationPatterns.some(pattern => pattern.test(message))
}

function isDefiniteTaskListing(message: string): boolean {
  const definiteListingPatterns = [
    /minha\s+agenda\s+(de\s+)?(hoje|amanhã)/i,
    /quais\s+(são\s+)?minhas\s+tarefas/i,
    /o\s+que\s+tenho\s+(hoje|amanhã)/i,
    /me\s+mostra\s+(minha\s+)?agenda/i,
    /como\s+está\s+minha\s+agenda/i,
    /tenho\s+algo\s+(marcado|agendado)/i
  ]
  
  return definiteListingPatterns.some(pattern => pattern.test(message))
}

function isDefiniteTaskCompletion(message: string): boolean {
  const definiteCompletionPatterns = [
    /(terminei|acabei|completei|finalizei)\s+(a\s+)?(reunião|tarefa|projeto)/i,
    /está\s+(pronto|feito|concluído)/i,
    /já\s+(fiz|terminei)/i,
    /consegui\s+(fazer|terminar|completar)/i
  ]
  
  return definiteCompletionPatterns.some(pattern => pattern.test(message))
}

function isDefiniteTaskDeletion(message: string): boolean {
  const definiteDeletionPatterns = [
    /cancelar\s+(reunião|consulta|compromisso)/i,
    /remarcar\s+(reunião|consulta)/i,
    /remover\s+(da\s+)?agenda/i,
    /desmarcar\s+(reunião|consulta)/i,
    /tirar\s+(da\s+)?agenda/i
  ]
  
  return definiteDeletionPatterns.some(pattern => pattern.test(message))
}

function isCreationContext(message: string): boolean {
  // Mantida para compatibilidade, mas agora mais específica
  const creationPatterns = [
    /hoje\s+(tenho|vou ter)\s+(reunião|consulta|compromisso)/i,
    /amanhã\s+(tenho|vou ter)\s+(reunião|consulta|compromisso)/i,
    /(às|as)\s+\d{1,2}[:h]?\d{0,2}\s+(tenho|vou ter)/i,
    /preciso\s+(ir|comparecer)\s+(em|na|no)/i
  ]
  
  return creationPatterns.some(pattern => pattern.test(message))
}

function isCompletionContext(message: string): boolean {
  // Mantida para compatibilidade, mas agora mais específica
  const completionPatterns = [
    /já\s+(fiz|terminei|acabei)\s+(a\s+)?(reunião|tarefa|projeto)/i,
    /está\s+(pronto|feito|concluído)\s+(o\s+)?(projeto|relatório|trabalho)/i,
    /consegui\s+(fazer|terminar)\s+(a\s+)?(tarefa|reunião)/i,
    /(finalizei|completei)\s+(o\s+)?(projeto|trabalho|tarefa)/i
  ]
  
  return completionPatterns.some(pattern => pattern.test(message))
}

function isListingContext(message: string): boolean {
  // Mantida para compatibilidade, mas agora mais específica  
  const listingPatterns = [
    /o que\s+(tenho|preciso fazer)\s+(hoje|amanhã)/i,
    /quais\s+(são\s+)?minhas\s+(tarefas|reuniões|compromissos)/i,
    /me\s+(mostra|fala|diz)\s+(minha\s+)?agenda/i,
    /como\s+está\s+minha\s+agenda/i,
    /tenho\s+algo\s+(hoje|amanhã|marcado)/i
  ]
  
  return listingPatterns.some(pattern => pattern.test(message))
}

function extractDescription(message: string): string | undefined {
  // Extrai descrição adicional se houver
  const descriptionPatterns = [
    /sobre\s+(.+)/i,
    /referente\s+a\s+(.+)/i,
    /relacionado\s+a\s+(.+)/i,
    /que\s+(.+)/i
  ]
  
  for (const pattern of descriptionPatterns) {
    const match = message.match(pattern)
    if (match && match[1] && match[1].length > 5) {
      return match[1].trim()
    }
  }
  
  return undefined
}

function extractTags(message: string): string[] {
  const tags: string[] = []
  
  // Tags baseadas em contexto
  if (/trabalho|empresa|corporativo|reunião/i.test(message)) {
    tags.push('trabalho')
  }
  if (/pessoal|casa|família/i.test(message)) {
    tags.push('pessoal')
  }
  if (/estudo|faculdade|curso|aprender/i.test(message)) {
    tags.push('estudo')
  }
  if (/exercício|academia|correr|treino/i.test(message)) {
    tags.push('saúde')
  }
  if (/médico|consulta|exame/i.test(message)) {
    tags.push('saúde', 'médico')
  }
  if (/compras|mercado|shopping/i.test(message)) {
    tags.push('compras')
  }
  
  return tags
}
