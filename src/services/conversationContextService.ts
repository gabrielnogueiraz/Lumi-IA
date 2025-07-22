import { ConversationContext, TaskContextMatch } from '../types'

/**
 * 🧠 SERVIÇO DE CONTEXTO DE CONVERSA
 * 
 * Gerencia memória de curto prazo, contexto emocional e similaridade
 * semântica para criar conversas mais fluidas e humanizadas
 */

// Cache em memória para contextos de conversa (em produção, usar Redis)
const conversationCache = new Map<string, ConversationContext>()

export class ConversationContextService {
  
  /**
   * Obtém ou cria um contexto de conversa para o usuário
   */
  getOrCreateContext(userId: string): ConversationContext {
    let context = conversationCache.get(userId)
    
    if (!context) {
      context = {
        userId,
        conversationHistory: [],
        sessionStartTime: new Date(),
        lastInteractionTime: new Date()
      }
      conversationCache.set(userId, context)
    }
    
    // Limpa histórico se a sessão estiver muito antiga (>2 horas)
    const timeSinceLastInteraction = Date.now() - context.lastInteractionTime.getTime()
    if (timeSinceLastInteraction > 2 * 60 * 60 * 1000) {
      context.conversationHistory = []
      context.sessionStartTime = new Date()
      context.lastIntent = undefined
      context.currentEmotion = undefined
      context.focusedTaskId = undefined
      context.focusedTaskTitle = undefined
    }
    
    return context
  }

  /**
   * Atualiza o contexto com nova interação
   */
  updateContext(
    userId: string, 
    userMessage: string, 
    detectedEmotion: string, 
    intent: string,
    aiResponse?: string
  ): ConversationContext {
    const context = this.getOrCreateContext(userId)
    
    // Adiciona nova interação ao histórico
    context.conversationHistory.push({
      timestamp: new Date(),
      userMessage,
      detectedEmotion,
      intent,
      aiResponse
    })
    
    // Mantém apenas os últimos 10 turnos para não sobrecarregar
    if (context.conversationHistory.length > 10) {
      context.conversationHistory = context.conversationHistory.slice(-10)
    }
    
    // Atualiza estado atual
    context.lastIntent = intent
    context.currentEmotion = detectedEmotion
    context.lastInteractionTime = new Date()
    
    conversationCache.set(userId, context)
    return context
  }

  /**
   * Define tarefa em foco na conversa
   */
  setFocusedTask(userId: string, taskId: string, taskTitle: string): void {
    const context = this.getOrCreateContext(userId)
    context.focusedTaskId = taskId
    context.focusedTaskTitle = taskTitle
    conversationCache.set(userId, context)
  }

  /**
   * Encontra similaridade entre mensagem do usuário e tarefas existentes
   * MELHORADO: algoritmo mais efetivo para matching
   */
  findTaskMatches(
    userMessage: string, 
    tasks: Array<{ id: string; title: string; description?: string }>
  ): TaskContextMatch[] {
    const matches: TaskContextMatch[] = []
    const messageLower = userMessage.toLowerCase()
    
    console.log('🔍 Matching - Mensagem:', messageLower)
    console.log('🔍 Matching - Tarefas:', tasks.map(t => t.title))
    
    // Remove stopwords comuns e normaliza
    const stopwords = ['o', 'a', 'os', 'as', 'um', 'uma', 'de', 'do', 'da', 'em', 'no', 'na', 'para', 'com', 'por', 'que', 'não', 'mais', 'como', 'muito', 'também', 'já', 'seu', 'sua', 'estou', 'está']
    
    const messageWords = this.extractSignificantWords(messageLower, stopwords)
    console.log('🔍 Matching - Palavras da mensagem:', messageWords)

    for (const task of tasks) {
      const taskText = (task.title + ' ' + (task.description || '')).toLowerCase()
      const taskWords = this.extractSignificantWords(taskText, stopwords)
      
      console.log(`🔍 Matching - Tarefa "${task.title}":`, taskWords)
      
      // 1. Verifica match exato de frases importantes
      const exactPhraseMatch = this.findExactPhraseMatches(messageLower, taskText)
      
      // 2. Calcula similaridade por palavras individuais
      const wordMatches = this.findWordMatches(messageWords, taskWords)
      
      // 3. Verifica palavras-chave importantes
      const keywordMatch = this.hasImportantKeywordMatch(messageLower, taskText)
      
      let similarity = 0
      let isExactMatch = false
      const matchedKeywords: string[] = []
      
      // Prioriza matches exatos de frases
      if (exactPhraseMatch.length > 0) {
        similarity = 1.0
        isExactMatch = true
        matchedKeywords.push(...exactPhraseMatch)
        console.log(`🎯 Match exato de frase para "${task.title}":`, exactPhraseMatch)
      }
      // Senão, verifica palavras-chave importantes
      else if (keywordMatch.keywords.length > 0) {
        similarity = keywordMatch.similarity
        isExactMatch = keywordMatch.isExact
        matchedKeywords.push(...keywordMatch.keywords)
        console.log(`🎯 Match de palavra-chave para "${task.title}":`, keywordMatch.keywords, 'similaridade:', similarity)
      }
      // Por último, similaridade por palavras comuns
      else if (wordMatches.length > 0) {
        similarity = wordMatches.length / Math.max(messageWords.length, taskWords.length, 1)
        matchedKeywords.push(...wordMatches)
        console.log(`🔍 Match de palavras para "${task.title}":`, wordMatches, 'similaridade:', similarity)
      }
      
      if (similarity > 0.2) { // Lowered threshold
        matches.push({
          taskId: task.id,
          title: task.title,
          similarity,
          isExactMatch,
          matchedKeywords
        })
      }
    }
    
    // Ordena por similaridade
    const sortedMatches = matches
      .sort((a, b) => b.similarity - a.similarity)
      .slice(0, 3)
    
    console.log('🔍 Matching - Resultados finais:', sortedMatches.map(m => `${m.title} (${m.similarity.toFixed(2)})`))
    
    return sortedMatches
  }

  /**
   * Extrai palavras significativas (remove stopwords e normaliza)
   */
  private extractSignificantWords(text: string, stopwords: string[]): string[] {
    return text
      .split(/\s+/)
      .map(word => word.replace(/[^\w]/g, '').toLowerCase())
      .filter(word => word.length > 2 && !stopwords.includes(word))
  }

  /**
   * Busca matches exatos de frases importantes
   */
  private findExactPhraseMatches(message: string, taskText: string): string[] {
    const matches: string[] = []
    
    // Extrai frases de 2-4 palavras do título da tarefa
    const taskPhrases = this.extractPhrases(taskText, 2, 4)
    
    for (const phrase of taskPhrases) {
      if (message.includes(phrase) && phrase.length > 4) { // Frases com mais de 4 caracteres
        matches.push(phrase)
      }
    }
    
    return matches
  }

  /**
   * Extrai frases de tamanho específico
   */
  private extractPhrases(text: string, minWords: number, maxWords: number): string[] {
    const words = text.split(/\s+/)
    const phrases: string[] = []
    
    for (let len = minWords; len <= Math.min(maxWords, words.length); len++) {
      for (let i = 0; i <= words.length - len; i++) {
        const phrase = words.slice(i, i + len).join(' ')
        if (phrase.length > 4) { // Só frases com mais de 4 caracteres
          phrases.push(phrase)
        }
      }
    }
    
    return phrases
  }

  /**
   * Encontra matches de palavras individuais
   */
  private findWordMatches(messageWords: string[], taskWords: string[]): string[] {
    return messageWords.filter(word => 
      taskWords.some(taskWord => 
        taskWord.includes(word) || word.includes(taskWord) || 
        this.calculateLevenshteinSimilarity(word, taskWord) > 0.8
      )
    )
  }

  /**
   * Verifica se há match de palavras-chave importantes (contexto específico)
   */
  private hasImportantKeywordMatch(message: string, taskText: string): {
    keywords: string[],
    similarity: number,
    isExact: boolean
  } {
    const importantKeywords = [
      // Tipos de reunião/evento
      'reunião', 'reuniao', 'meeting', 'encontro', 'bate-papo', 'conversa',
      // Contextos específicos
      'marketing', 'produção', 'producao', 'time', 'equipe', 'cliente', 'vendas',
      'trabalho', 'projeto', 'entrega', 'deadline', 'prazo', 'relatório', 'relatorio',
      // Atividades
      'apresentação', 'apresentacao', 'treino', 'exercício', 'exercicio', 'academia',
      'estudo', 'prova', 'exame', 'consulta', 'médico', 'medico', 'dentista'
    ]
    
    const foundKeywords: string[] = []
    let maxSimilarity = 0
    
    for (const keyword of importantKeywords) {
      if (message.includes(keyword) && taskText.includes(keyword)) {
        foundKeywords.push(keyword)
        maxSimilarity = Math.max(maxSimilarity, 0.8) // High confidence for keyword matches
      }
    }
    
    // Verifica combinações importantes
    if (message.includes('reunião') || message.includes('reuniao')) {
      if (taskText.includes('marketing') && (message.includes('marketing') || message.includes('produção') || message.includes('producao'))) {
        foundKeywords.push('reunião+contexto')
        maxSimilarity = 0.9
      }
      if (taskText.includes('produção') || taskText.includes('producao')) {
        if (message.includes('produção') || message.includes('producao') || message.includes('time')) {
          foundKeywords.push('reunião+produção')
          maxSimilarity = 0.95
        }
      }
    }
    
    const isExact = foundKeywords.length > 0 && maxSimilarity >= 0.8
    
    return {
      keywords: foundKeywords,
      similarity: maxSimilarity,
      isExact
    }
  }

  /**
   * Calcula similaridade entre duas strings usando Levenshtein simplificado
   */
  private calculateLevenshteinSimilarity(str1: string, str2: string): number {
    const longer = str1.length > str2.length ? str1 : str2
    const shorter = str1.length > str2.length ? str2 : str1
    
    if (longer.length === 0) return 1.0
    
    const distance = this.levenshteinDistance(longer, shorter)
    return (longer.length - distance) / longer.length
  }

  private levenshteinDistance(str1: string, str2: string): number {
    const matrix = []
    
    for (let i = 0; i <= str2.length; i++) {
      matrix[i] = [i]
    }
    
    for (let j = 0; j <= str1.length; j++) {
      matrix[0][j] = j
    }
    
    for (let i = 1; i <= str2.length; i++) {
      for (let j = 1; j <= str1.length; j++) {
        if (str2.charAt(i - 1) === str1.charAt(j - 1)) {
          matrix[i][j] = matrix[i - 1][j - 1]
        } else {
          matrix[i][j] = Math.min(
            matrix[i - 1][j - 1] + 1,
            matrix[i][j - 1] + 1,
            matrix[i - 1][j] + 1
          )
        }
      }
    }
    
    return matrix[str2.length][str1.length]
  }

  /**
   * Gera resumo contextual da conversa para incluir no prompt
   */
  generateContextualSummary(context: ConversationContext): string {
    if (context.conversationHistory.length === 0) {
      return "Primeira interação da sessão."
    }
    
    const recentInteractions = context.conversationHistory.slice(-3)
    const emotionalPattern = this.detectEmotionalPattern(recentInteractions)
    
    let summary = `Contexto da conversa atual:\n`
    
    if (context.focusedTaskTitle) {
      summary += `- Tarefa em foco: "${context.focusedTaskTitle}"\n`
    }
    
    if (context.currentEmotion && context.currentEmotion !== 'neutral') {
      summary += `- Estado emocional atual: ${context.currentEmotion}\n`
    }
    
    if (emotionalPattern) {
      summary += `- Padrão emocional: ${emotionalPattern}\n`
    }
    
    if (recentInteractions.length > 1) {
      summary += `- Interações recentes: ${recentInteractions.length} mensagens\n`
      
      const lastIntent = recentInteractions[recentInteractions.length - 1]?.intent
      if (lastIntent && lastIntent !== 'none') {
        summary += `- Última intenção: ${lastIntent}\n`
      }
    }
    
    return summary
  }

  /**
   * Detecta padrões emocionais nas interações recentes
   */
  private detectEmotionalPattern(interactions: ConversationContext['conversationHistory']): string | null {
    if (interactions.length < 2) return null
    
    const emotions = interactions.map(i => i.detectedEmotion)
    
    // Detecta persistência emocional
    const lastEmotion = emotions[emotions.length - 1]
    const persistentCount = emotions.reverse().findIndex(e => e !== lastEmotion)
    
    if (persistentCount >= 2) {
      return `${lastEmotion} persistente (${persistentCount + 1} interações)`
    }
    
    // Detecta mudanças bruscas
    if (emotions.length >= 2) {
      const prev = emotions[emotions.length - 2]
      const current = emotions[emotions.length - 1]
      
      const positiveEmotions = ['happy', 'excited', 'motivated', 'energetic', 'hopeful', 'entusiasmo', 'foco']
      const negativeEmotions = ['sad', 'frustrated', 'overwhelmed', 'confused', 'tired', 'desmotivacao', 'confusao']
      
      const prevIsPositive = positiveEmotions.includes(prev)
      const currentIsPositive = positiveEmotions.includes(current)
      
      if (prevIsPositive && !currentIsPositive) {
        return "mudança de humor positivo para negativo"
      } else if (!prevIsPositive && currentIsPositive) {
        return "recuperação emocional positiva"
      }
    }
    
    return null
  }

  /**
   * Limpa contexto de conversa (útil para reset manual)
   */
  clearContext(userId: string): void {
    conversationCache.delete(userId)
  }
}

export const conversationContextService = new ConversationContextService() 