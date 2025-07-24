/**
 * 🎯 ANALISADOR EMOCIONAL MELHORADO DA LUMI
 * 
 * MELHORIAS IMPLEMENTADAS PARA CORRIGIR SUPERDETECÇÃO DE CONFUSÃO:
 * 
 * 1. 🔍 CLASSIFICAÇÃO INTELIGENTE DE PERGUNTAS
 *    - Distingue perguntas informacionais de confusão emocional real
 *    - Classifica perguntas técnicas como "curious" em vez de "confused"
 *    - Usa regex patterns para identificar perguntas neutras
 * 
 * 2. 🎚️ SISTEMA DE PONTUAÇÃO EQUILIBRADO
 *    - Reduziu peso de palavras-chave genéricas (0.8 vs 1.0)
 *    - Mantém peso alto para expressões indiretas específicas (3.0)
 *    - Remove emoções com pontuação muito baixa (<0.5)
 * 
 * 3. 🛡️ FILTROS DE NEUTRALIDADE
 *    - Detecta padrões neutros/casuais e reduz intensidade emocional
 *    - Ignora cumprimentos, agradecimentos e expressões cotidianas
 *    - Contexto casual reduz peso das detecções emocionais
 * 
 * 4. 🧠 CONTEXTO CONVERSACIONAL
 *    - Considera histórico da conversa para ajustar análise
 *    - Detecta padrões de perguntas frequentes vs confusão real
 *    - Ajusta confiança baseado na consistência emocional
 * 
 * 5. ✅ SISTEMA DE VALIDAÇÃO FINAL
 *    - Previne classificações obviamente incorretas
 *    - Remove contradições emocionais (ex: happy + sad)
 *    - Aplica regras de sanidade baseadas no contexto
 * 
 * 6. 🎯 ANÁLISE CONTEXTUAL REFINADA
 *    - Só marca confusão com interrogação se tiver palavras de confusão
 *    - Considera contexto de problema real vs pergunta casual
 *    - Analisa intensificadores apenas em contextos apropriados
 * 
 * RESULTADO: Precisão muito maior, menos falsos positivos de confusão,
 *           melhor experiência do usuário com respostas adequadas ao contexto.
 */

import { EmotionalAnalysis } from '../types'

const emotionalKeywords = {
  happy: ['feliz', 'alegre', 'animado', 'contente', 'satisfeito', 'empolgado', 'bem', 'ótimo', 'maravilhoso', 'incrível', 'radiante', 'eufórico'],
  sad: ['triste', 'deprimido', 'desanimado', 'abatido', 'melancólico', 'mal', 'péssimo', 'ruim', 'chateado', 'desalentado', 'desolado'],
  anxious: ['ansioso', 'nervoso', 'preocupado', 'tenso', 'estressado', 'inquieto', 'agitado', 'aflito', 'apreensivo', 'angustiado'],
  motivated: ['motivado', 'determinado', 'focado', 'produtivo', 'energizado', 'inspirado', 'pronto', 'vamos', 'decidido', 'resoluto'],
  tired: ['cansado', 'exausto', 'esgotado', 'fatigado', 'sonolento', 'acabado', 'sem energia', 'drenado', 'desgastado'],
  focused: ['concentrado', 'focado', 'atento', 'determinado', 'direcionado', 'centrado', 'na zona', 'ligado'],
  stressed: ['estressado', 'sobrecarregado', 'pressionado', 'tenso', 'sob pressão', 'sufocado', 'oprimido'],
  
  // Estados emocionais refinados - removidas palavras genéricas
  confused: ['confuso', 'perdido', 'desorientado', 'sem rumo', 'sem direção', 'atrapalhado', 'bagunçado'],
  overwhelmed: ['sobrecarregado', 'assoberbado', 'sufocado', 'esmagado', 'dominado', 'cercado', 'bombardeado'],
  procrastinating: ['procrastinando', 'enrolando', 'empurrando', 'adiando', 'evitando', 'fugindo', 'esquivando'],
  excited: ['empolgado', 'animado', 'entusiasmado', 'eufórico', 'radiante', 'vibrando', 'elétrico'],
  determined: ['determinado', 'decidido', 'resoluto', 'firme', 'comprometido', 'focado', 'obstinado'],
  frustrated: ['frustrado', 'irritado', 'chateado', 'aborrecido', 'contrariado', 'impaciente', 'exasperado'],
  calm: ['calmo', 'tranquilo', 'sereno', 'pacífico', 'relaxado', 'zen', 'equilibrado'],
  energetic: ['energético', 'cheio de energia', 'elétrico', 'vibrante', 'dinâmico', 'ativo', 'disposto'],
  melancholy: ['melancólico', 'pensativo', 'reflexivo', 'nostálgico', 'contemplatvo', 'introspectivo'],
  hopeful: ['esperançoso', 'otimista', 'confiante', 'positivo', 'animado', 'encorajado'],
  stuck: ['preso', 'travado', 'bloqueado', 'emperrado', 'parado', 'estagnado', 'sem saída'],
  curious: ['curioso', 'interessado', 'querendo saber', 'intrigado'],

  // CATEGORIAS REFINADAS - removidas expressões muito genéricas
  desmotivacao: [
    'desmotivado', 'sem vontade', 'desanimado', 'apático', 'desencorajado',
    'sem energia', 'largado', 'desinteressado', 'sem pique', 'sem ânimo',
    'tô largado', 'sem gás', 'desestimulado'
  ],
  
  procrastinacao: [
    'procrastinando', 'empurrando', 'adiando', 'enrolando', 'deixando pra depois',
    'não tô afim', 'depois eu faço', 'amanhã eu vejo', 'ainda não', 
    'evitando', 'fugindo', 'escapando', 'esquivando', 'postergando'
  ],
  
  confusao: [
    'meio perdido', 'sem direção', 'bagunçado',
    'tô boiando', 'não tô entendendo nada', 'completamente perdido',
    'muito confuso', 'super confuso'
  ],
  
  sobrecarregado: [
    'sobrecarregado', 'muito pra fazer', 'não dou conta', 'pesado demais',
    'bombardeado', 'sufocado', 'dominado', 'esmagado', 'cercado',
    'muita pressão', 'muita coisa', 'não aguento', 'tá demais'
  ],
  
  entusiasmo: [
    'entusiasmado', 'empolgado', 'animadíssimo', 'super motivado',
    'cheio de energia', 'que legal', 'incrível', 'fantástico', 'adorei',
    'que máximo', 'show', 'demais', 'vibrando', 'elétrico'
  ],
  
  foco: [
    'focado', 'concentrado', 'na zona', 'ligado', 'atento', 'centrado',
    'determinado', 'direcionado', 'em modo trabalho', 'produtivo',
    'no flow', 'mergulhado', 'imerso', 'dedicado'
  ]
}

// Expressões que indicam REAL confusão emocional (não apenas perguntas)
const realConfusionExpressions = [
  'não sei por onde começar',
  'estou completamente perdido',
  'não faço ideia do que fazer',
  'tô meio perdido aqui',
  'não entendo direito o que tá acontecendo',
  'tá tudo confuso na minha cabeça',
  'não consigo organizar as ideias',
  'estou muito confuso sobre isso',
  'não sei mais o que fazer',
  'tô totalmente perdido'
]

// Padrões que indicam perguntas informacionais (NÃO confusão)
const informationalQuestionPatterns = [
  /^como (fazer|funciona|posso)/i,
  /^qual (é|seria|seria)/i,
  /^onde (fica|posso|está)/i,
  /^quando (é|seria|vai)/i,
  /^por que|porque/i,
  /^o que (é|seria|significa)/i,
  /^quem (é|foi|criou|desenvolveu)/i,
  /^você (pode|consegue|sabe)/i,
  /^tem como/i,
  /^existe (algum|alguma)/i,
  /^me (explica|conta|fala)/i
]

// Expressões indiretas refinadas - mais específicas
const indirectEmotionalExpressions = {
  confused: realConfusionExpressions,
  
  overwhelmed: [
    'é muita coisa pra hoje',
    'não vai dar tempo de tudo',
    'tá muito pesado hoje',
    'muita pressão em cima de mim',
    'não consigo dar conta de tudo',
    'tá sufocante essa rotina',
    'muita demanda hoje',
    'bombardeado de coisas pra fazer'
  ],
  
  procrastinating: [
    'vou deixar pra depois',
    'não tô no clima hoje',
    'amanhã eu começo',
    'depois eu vejo isso',
    'não tô afim agora',
    'vou empurrar um pouco',
    'ainda não é hora',
    'deixa quieto por hoje'
  ],
  
  stuck: [
    'não sai do lugar',
    'não evolui nada',
    'tô travado nesse ponto',
    'não consigo avançar',
    'empacou completamente',
    'não vai pra frente',
    'tô bloqueado nisso',
    'não flui de jeito nenhum'
  ],
  
  frustrated: [
    'que saco isso',
    'tá muito difícil',
    'não funciona de jeito nenhum',
    'que droga de situação',
    'não vai nunca',
    'que chatice',
    'que coisa irritante',
    'não dá certo nunca'
  ],
  
  tired: [
    'tô completamente acabado',
    'sem energia nenhuma',
    'exausto demais',
    'não aguento mais hoje',
    'tô totalmente drenado',
    'sem pique nenhum',
    'morto de cansaço'
  ],
  
  excited: [
    'que legal demais',
    'adorei muito isso',
    'que máximo essa ideia',
    'muito bom mesmo',
    'incrível essa oportunidade',
    'fantástico isso',
    'show de bola'
  ],

  desmotivacao: [
    'não tenho vontade de fazer nada hoje',
    'tô sem pique pra qualquer coisa',
    'sem ânimo pra nada mesmo',
    'tô muito largado',
    'nada me anima hoje',
    'sem gás pra qualquer coisa',
    'tô muito apático',
    'nada desperta meu interesse'
  ],
  
  sobrecarregado: [
    'muita coisa pra pouco tempo',
    'agenda impossível hoje',
    'mil coisas pra resolver',
    'não tem como dar conta',
    'agenda super apertada',
    'muita demanda junta'
  ],
  
  entusiasmo: [
    'que energia boa hoje',
    'tô super animado com isso',
    'que empolgação total',
    'tô vibrando de alegria',
    'adorando demais a ideia',
    'tô elétrico hoje',
    'cheio de energia boa'
  ],
  
  foco: [
    'tô super concentrado',
    'no modo trabalho total',
    'foco máximo agora',
    'mente totalmente ligada',
    'concentração de 100%',
    'na zona de produtividade',
    'mergulhado no trabalho',
    'dedicação total hoje'
  ]
}

// Palavras que intensificam emoções
const intensifiers = ['muito', 'super', 'extremamente', 'completamente', 'totalmente', 'absurdamente', 'demais', 'mega', 'ultra']

// Palavras que indicam necessidade de suporte REAL
const supportIndicators = [
  'me ajude por favor', 'preciso muito de ajuda', 'não dou conta sozinho', 
  'tô perdido mesmo', 'me orienta', 'não aguento mais', 'difícil demais pra mim',
  'não sei mesmo como', 'me explica direito', 'como faz isso'
]

// 🎯 NOVA ADIÇÃO: Padrões que NÃO devem ser considerados emocionalmente intensos
const neutralPatterns = [
  // Perguntas técnicas/profissionais
  /como (fazer|criar|configurar|instalar|usar)/i,
  /qual (é|seria) (o|a) (melhor|forma|jeito)/i,
  /onde (encontro|posso|fica)/i,
  /tem (algum|alguma|como)/i,
  
  // Expressões cotidianas neutras
  /obrigado/i, /valeu/i, /legal/i, /entendi/i, /certo/i, /ok/i,
  /bom dia/i, /boa tarde/i, /boa noite/i, /oi/i, /olá/i,
  
  // Confirmações e agradecimentos
  /perfeito/i, /show/i, /massa/i, /beleza/i
]

// 🎯 NOVA ADIÇÃO: Contextos que reduzem intensidade emocional
const casualContexts = [
  'só queria saber', 'só uma dúvida', 'rapidinho', 'só pra confirmar',
  'me tira uma dúvida', 'uma pergunta rápida', 'só checando'
]

export function analyzeEmotion(message: string): EmotionalAnalysis {
  const lowerMessage = message.toLowerCase()
  const detectedEmotions: Record<string, number> = {}
  const foundKeywords: string[] = []
  const contextualClues: string[] = []
  let emotionalIntensity: 'low' | 'medium' | 'high' = 'low'
  let needsSupport = false

  // 🎯 VERIFICAÇÃO DE NEUTRALIDADE PRIMEIRO
  const isNeutralPattern = neutralPatterns.some(pattern => pattern.test(message))
  const isCasualContext = casualContexts.some(context => lowerMessage.includes(context))
  
  if (isNeutralPattern || isCasualContext) {
    contextualClues.push('Padrão neutro/casual detectado - reduzindo intensidade emocional')
  }

  // 🎯 NOVA LÓGICA: Verifica se é pergunta informacional primeiro
  const isInformationalQuestion = isInformationalQuestionCheck(message)
  if (isInformationalQuestion) {
    contextualClues.push('Pergunta informacional detectada - não indica confusão emocional')
    
    // Se é pergunta informacional, classifica como curiosidade, não confusão
    detectedEmotions.curious = 2
    foundKeywords.push('pergunta informacional')
    
    return {
      detectedMood: 'curious',
      confidence: 0.8,
      keywords: foundKeywords,
      responseStrategy: 'guide',
      emotionalIntensity: 'low',
      needsSupport: false,
      contextualClues
    }
  }

  // Analisa expressões indiretas primeiro (mais específicas e peso maior)
  Object.entries(indirectEmotionalExpressions).forEach(([emotion, expressions]) => {
    expressions.forEach(expression => {
      if (lowerMessage.includes(expression)) {
        // 🎯 AJUSTE: Reduz peso se for contexto neutro/casual
        const weight = (isNeutralPattern || isCasualContext) ? 2 : 3
        detectedEmotions[emotion] = (detectedEmotions[emotion] || 0) + weight
        foundKeywords.push(expression)
        contextualClues.push(`Expressão indireta de ${emotion}: "${expression}"`)
      }
    })
  })

  // Analisa palavras-chave diretas (peso reduzido)
  Object.entries(emotionalKeywords).forEach(([emotion, keywords]) => {
    keywords.forEach(keyword => {
      if (lowerMessage.includes(keyword)) {
        // 🎯 AJUSTE: Peso ainda menor para contextos casuais
        const weight = (isNeutralPattern || isCasualContext) ? 0.4 : 0.8
        detectedEmotions[emotion] = (detectedEmotions[emotion] || 0) + weight
        foundKeywords.push(keyword)
      }
    })
  })

  // Detecta intensificadores
  const hasIntensifier = intensifiers.some(intensifier => lowerMessage.includes(intensifier))
  if (hasIntensifier && !isNeutralPattern) { // Não amplifica se for padrão neutro
    emotionalIntensity = 'high'
    Object.keys(detectedEmotions).forEach(emotion => {
      detectedEmotions[emotion] *= 1.5
    })
    contextualClues.push(`Intensificador detectado: emoção amplificada`)
  }

  // Detecta necessidade de suporte REAL
  needsSupport = supportIndicators.some(indicator => lowerMessage.includes(indicator))
  if (needsSupport) {
    contextualClues.push(`Indicadores de necessidade de suporte detectados`)
  }

  // Análise contextual melhorada
  analyzeImprovedContextualClues(lowerMessage, detectedEmotions, contextualClues, isInformationalQuestion, isNeutralPattern || isCasualContext)

  // 🎯 FILTRO DE RUÍDO: Remove emoções com pontuação muito baixa
  Object.keys(detectedEmotions).forEach(emotion => {
    if (detectedEmotions[emotion] < 0.5) {
      delete detectedEmotions[emotion]
      contextualClues.push(`Emoção "${emotion}" removida por pontuação baixa`)
    }
  })

  // 🎯 SISTEMA DE VALIDAÇÃO FINAL
  const validatedEmotions = validateEmotionalClassification(detectedEmotions, message, contextualClues)

  // Determina intensidade baseada na pontuação total
  const totalScore = Object.values(validatedEmotions).reduce((sum, score) => sum + score, 0)
  if (totalScore >= 4) emotionalIntensity = 'high'
  else if (totalScore >= 2) emotionalIntensity = 'medium'

  // Encontra a emoção dominante
  const dominantEmotion = Object.entries(validatedEmotions)
    .sort(([,a], [,b]) => b - a)[0]

  const detectedMood = dominantEmotion 
    ? dominantEmotion[0] as EmotionalAnalysis['detectedMood']
    : 'neutral'
  
  const confidence = dominantEmotion 
    ? Math.min(dominantEmotion[1] / 4, 1) // Ajustado para nova pontuação
    : 0

  // 🎯 AJUSTE FINAL: Reduz confiança para contextos casuais
  const finalConfidence = (isNeutralPattern || isCasualContext) 
    ? Math.max(confidence - 0.3, 0.1) 
    : confidence

  // Define estratégia de resposta
  const responseStrategy = getAdvancedResponseStrategy(detectedMood, emotionalIntensity, needsSupport)

  return {
    detectedMood,
    confidence: finalConfidence,
    keywords: foundKeywords,
    responseStrategy,
    emotionalIntensity,
    needsSupport,
    contextualClues
  }
}

/**
 * 🎯 NOVA FUNÇÃO: Detecta se é pergunta informacional
 */
function isInformationalQuestionCheck(message: string): boolean {
  const lowerMessage = message.toLowerCase()
  
  // Verifica padrões de pergunta informacional
  const hasInformationalPattern = informationalQuestionPatterns.some(pattern => 
    pattern.test(lowerMessage)
  )
  
  // Verifica se tem sinais de confusão emocional real
  const hasRealConfusionSigns = realConfusionExpressions.some(expression =>
    lowerMessage.includes(expression)
  )
  
  // Se tem padrão informacional E NÃO tem sinais de confusão real = pergunta informacional
  return hasInformationalPattern && !hasRealConfusionSigns
}

/**
 * 🎯 ANÁLISE CONTEXTUAL MELHORADA
 */
function analyzeImprovedContextualClues(
  message: string, 
  detectedEmotions: Record<string, number>,
  contextualClues: string[],
  isInformationalQuestion: boolean,
  isNeutralContext?: boolean
) {
  // Pontuação REFINADA - não penaliza perguntas normais
  if (message.includes('...')) {
    detectedEmotions.melancholy = (detectedEmotions.melancholy || 0) + 0.5
    // Só adiciona confusão se não for pergunta informacional
    if (!isInformationalQuestion) {
      const confusionWeight = isNeutralContext ? 0.1 : 0.3
      detectedEmotions.confusao = (detectedEmotions.confusao || 0) + confusionWeight
    }
    contextualClues.push('Reticências indicam hesitação/melancolia')
  }
  
  // INTERROGAÇÃO: Só indica confusão se tiver outros sinais
  if (message.includes('?') && !isInformationalQuestion) {
    const confusionWords = ['perdido', 'confuso', 'não entendo', 'não faço ideia']
    const hasConfusionWords = confusionWords.some(word => message.toLowerCase().includes(word))
    
    if (hasConfusionWords && !isNeutralContext) {
      detectedEmotions.confusao = (detectedEmotions.confusao || 0) + 0.5
      contextualClues.push('Interrogação + palavras de confusão indicam dúvida genuína')
    }
  }
  
  const exclamationCount = (message.match(/!/g) || []).length
  if (exclamationCount >= 2 && !isNeutralContext) {
    detectedEmotions.entusiasmo = (detectedEmotions.entusiasmo || 0) + 1
    detectedEmotions.excited = (detectedEmotions.excited || 0) + 0.5
    contextualClues.push(`Múltiplas exclamações (${exclamationCount}) indicam entusiasmo`)
  }

  // Padrões de linguagem REFINADOS
  // Só marca confusão se for contexto de problema real
  const hasRealProblemContext = ['projeto', 'trabalho', 'situação', 'problema', 'vida'].some(word => 
    message.toLowerCase().includes(word)
  )
  
  if (message.includes('não') && (message.includes('consigo') || message.includes('sei')) && hasRealProblemContext && !isNeutralContext) {
    detectedEmotions.confusao = (detectedEmotions.confusao || 0) + 0.8
    detectedEmotions.desmotivacao = (detectedEmotions.desmotivacao || 0) + 0.5
    contextualClues.push('Padrão "não consigo/sei" em contexto problemático indica confusão real')
  }

  if (message.includes('preciso') || message.includes('tenho que')) {
    const motivationWeight = isNeutralContext ? 0.2 : 0.5
    detectedEmotions.motivated = (detectedEmotions.motivated || 0) + motivationWeight
    detectedEmotions.foco = (detectedEmotions.foco || 0) + motivationWeight
    contextualClues.push('Linguagem de necessidade/obrigação indica motivação/foco')
  }

  // Outros padrões ajustados para contexto...
  const procrastinationTimeWords = ['depois', 'mais tarde', 'amanhã', 'próxima', 'quando der']
  if (procrastinationTimeWords.some(word => message.includes(word)) && !isNeutralContext) {
    detectedEmotions.procrastinacao = (detectedEmotions.procrastinacao || 0) + 1
    contextualClues.push('Linguagem temporal indica procrastinação')
  }

  if ((message.includes('muito') || message.includes('muita')) && 
      (message.includes('coisa') || message.includes('trabalho') || message.includes('tarefa')) &&
      !isNeutralContext) {
    detectedEmotions.sobrecarregado = (detectedEmotions.sobrecarregado || 0) + 1
    contextualClues.push('Quantificadores de sobrecarga detectados')
  }

  const positiveIntense = ['adorei', 'amei', 'perfeito', 'incrível', 'fantástico', 'maravilhoso']
  if (positiveIntense.some(word => message.includes(word))) {
    const enthusiasmWeight = isNeutralContext ? 0.5 : 1
    detectedEmotions.entusiasmo = (detectedEmotions.entusiasmo || 0) + enthusiasmWeight
    detectedEmotions.excited = (detectedEmotions.excited || 0) + enthusiasmWeight
    contextualClues.push('Expressões positivas intensas detectadas')
  }

  const focusWords = ['concentrado', 'focado', 'produtivo', 'trabalhando', 'fazendo']
  if (focusWords.some(word => message.includes(word))) {
    const focusWeight = isNeutralContext ? 0.5 : 1
    detectedEmotions.foco = (detectedEmotions.foco || 0) + focusWeight
    contextualClues.push('Indicadores de foco/concentração detectados')
  }
}

function getAdvancedResponseStrategy(
  mood: EmotionalAnalysis['detectedMood'], 
  intensity: 'low' | 'medium' | 'high',
  needsSupport: boolean
): EmotionalAnalysis['responseStrategy'] {
  
  if (needsSupport) {
    return 'support'
  }

  switch (mood) {
    case 'confused':
    case 'confusao':
      return intensity === 'high' ? 'guide' : 'structure'
    
    case 'overwhelmed':
    case 'sobrecarregado':
      return intensity === 'high' ? 'calm' : 'structure'
    
    case 'procrastinating':
    case 'procrastinacao':
      return intensity === 'high' ? 'gentle_push' : 'motivate'
    
    case 'stuck':
      return 'guide'
    
    case 'frustrated':
      return intensity === 'high' ? 'empathize' : 'reassure'
    
    case 'excited':
    case 'entusiasmo':
      return 'energize'
    
    case 'determined':
    case 'foco':
      return 'challenge'
    
    case 'tired':
      return intensity === 'high' ? 'calm' : 'support'
    
    case 'anxious':
    case 'stressed':
      return intensity === 'high' ? 'ground' : 'calm'
    
    case 'sad':
    case 'melancholy':
    case 'desmotivacao':
      return intensity === 'high' ? 'empathize' : 'encourage'
    
    case 'happy':
    case 'energetic':
      return 'energize'
    
    case 'motivated':
    case 'focused':
      return 'challenge'
    
    case 'hopeful':
      return 'encourage'
    
    case 'calm':
      return 'motivate'
    
    case 'curious':
      return 'guide'
    
    case 'proud':
      return 'share_origin'
    
    default:
      return 'motivate'
  }
}

export function getEmotionalTone(strategy: EmotionalAnalysis['responseStrategy']): 'supportive' | 'motivational' | 'calm' | 'enthusiastic' | 'gentle' {
  switch (strategy) {
    case 'support':
    case 'empathize':
      return 'supportive'
    case 'calm':
    case 'ground':
      return 'calm'
    case 'energize':
    case 'challenge':
      return 'enthusiastic'
    case 'encourage':
    case 'motivate':
      return 'motivational'
    case 'guide':
    case 'structure':
    case 'reassure':
    case 'gentle_push':
      return 'gentle'
    default:
      return 'gentle'
  }
}

/**
 * 🎯 NOVA FUNÇÃO: Análise emocional com contexto conversacional
 * Considera o histórico da conversa para melhorar a precisão
 */
export function analyzeEmotionWithContext(
  message: string, 
  conversationContext?: any
): EmotionalAnalysis {
  const baseAnalysis = analyzeEmotion(message)
  
  // Se não há contexto, retorna análise básica
  if (!conversationContext || !conversationContext.conversationHistory) {
    return baseAnalysis
  }
  
  const history = conversationContext.conversationHistory
  const recentEmotions = history.slice(-3).map((entry: any) => entry.detectedEmotion)
  
  // 🎯 AJUSTES BASEADOS NO CONTEXTO
  
  // Se o usuário tem histórico de perguntas informacionais, reduz chance de confusão
  const recentQuestions = history.slice(-5).filter((entry: any) => 
    entry.userMessage.includes('?') && !entry.detectedEmotion.includes('confus')
  )
  
  if (recentQuestions.length >= 2 && baseAnalysis.detectedMood === 'confused') {
    // Usuário tem padrão de fazer perguntas - provavelmente é curiosidade
    return {
      ...baseAnalysis,
      detectedMood: 'curious',
      confidence: Math.max(baseAnalysis.confidence - 0.3, 0.1),
      contextualClues: [
        ...baseAnalysis.contextualClues,
        `Histórico de perguntas informacionais detectado - reclassificado como curiosidade`
      ]
    }
  }
  
  // Se há padrão consistente de emoção, ajusta confiança
  const dominantRecentEmotion = getMostFrequentEmotion(recentEmotions)
  if (dominantRecentEmotion && dominantRecentEmotion === baseAnalysis.detectedMood) {
    return {
      ...baseAnalysis,
      confidence: Math.min(baseAnalysis.confidence + 0.2, 1),
      contextualClues: [
        ...baseAnalysis.contextualClues,
        `Padrão emocional consistente detectado - confiança aumentada`
      ]
    }
  }
  
  // Se há mudança brusca de emoção, reduz confiança
  const lastEmotion = recentEmotions[recentEmotions.length - 1]
  if (lastEmotion && isEmotionallyOpposite(lastEmotion, baseAnalysis.detectedMood)) {
    return {
      ...baseAnalysis,
      confidence: Math.max(baseAnalysis.confidence - 0.4, 0.1),
      contextualClues: [
        ...baseAnalysis.contextualClues,
        `Mudança brusca de emoção detectada - confiança reduzida`
      ]
    }
  }
  
  return baseAnalysis
}

/**
 * Encontra a emoção mais frequente em uma lista
 */
function getMostFrequentEmotion(emotions: string[]): string | null {
  if (!emotions.length) return null
  
  const frequency: Record<string, number> = {}
  emotions.forEach(emotion => {
    frequency[emotion] = (frequency[emotion] || 0) + 1
  })
  
  return Object.entries(frequency)
    .sort(([,a], [,b]) => b - a)[0]?.[0] || null
}

/**
 * Verifica se duas emoções são opostas
 */
function isEmotionallyOpposite(emotion1: string, emotion2: string): boolean {
  const opposites: Record<string, string[]> = {
    'happy': ['sad', 'frustrated', 'tired'],
    'sad': ['happy', 'excited', 'energetic'],
    'excited': ['tired', 'sad', 'desmotivacao'],
    'frustrated': ['happy', 'calm', 'satisfied'],
    'calm': ['anxious', 'frustrated', 'stressed'],
    'anxious': ['calm', 'relaxed'],
    'motivated': ['desmotivacao', 'tired'],
    'desmotivacao': ['motivated', 'excited', 'energetic']
  }
  
  return opposites[emotion1]?.includes(emotion2) || false
}

/**
 * 🎯 SISTEMA DE VALIDAÇÃO FINAL
 * Aplica lógica de sanidade para prevenir classificações incorretas
 */
function validateEmotionalClassification(
  detectedEmotions: Record<string, number>, 
  originalMessage: string,
  contextualClues: string[]
): Record<string, number> {
  const lowerMessage = originalMessage.toLowerCase()
  const validatedEmotions = { ...detectedEmotions }
  
  // 🎯 REGRA 1: Cumprimentos não são confusão
  const greetingPatterns = [
    /^(oi|olá|hey|e aí|opa|fala)/i,
    /(bom dia|boa tarde|boa noite)/i,
    /^(tchau|até|falou|valeu)/i
  ]
  
  const isGreeting = greetingPatterns.some(pattern => pattern.test(originalMessage.trim()))
  if (isGreeting && validatedEmotions.confusao) {
    delete validatedEmotions.confusao
    contextualClues.push('Validação: Cumprimento detectado - confusão removida')
  }
  
  // 🎯 REGRA 2: Agradecimentos são positivos, não neutros
  const thankPatterns = [
    /obrigad[oa]/i, /valeu/i, /muito bom/i, /legal/i, /show/i
  ]
  
  const isThanking = thankPatterns.some(pattern => pattern.test(lowerMessage))
  if (isThanking && Object.keys(validatedEmotions).length === 0) {
    validatedEmotions.happy = 1.5
    contextualClues.push('Validação: Agradecimento detectado - classificado como positivo')
  }
  
  // 🎯 REGRA 3: Perguntas técnicas específicas não são confusão emocional
  const technicalQuestionPatterns = [
    /como (instalar|configurar|usar|fazer|criar)/i,
    /qual (comando|função|biblioteca|framework)/i,
    /onde (encontro|baixo|instalo)/i,
    /(error|erro|exception|bug)/i
  ]
  
  const isTechnicalQuestion = technicalQuestionPatterns.some(pattern => pattern.test(lowerMessage))
  if (isTechnicalQuestion && validatedEmotions.confusao) {
    // Reduz drasticamente ou remove confusão
    if (validatedEmotions.confusao <= 1) {
      delete validatedEmotions.confusao
    } else {
      validatedEmotions.confusao *= 0.3
    }
    // Adiciona curiosidade se não tiver outras emoções fortes
    if (Object.keys(validatedEmotions).length <= 1) {
      validatedEmotions.curious = 2
    }
    contextualClues.push('Validação: Pergunta técnica detectada - confusão reduzida/removida')
  }
  
  // 🎯 REGRA 4: Mensagens muito curtas raramente têm emoção intensa
  if (originalMessage.trim().length <= 10) {
    Object.keys(validatedEmotions).forEach(emotion => {
      if (validatedEmotions[emotion] > 2) {
        validatedEmotions[emotion] = Math.min(validatedEmotions[emotion], 1.5)
      }
    })
    contextualClues.push('Validação: Mensagem curta detectada - intensidade emocional reduzida')
  }
  
  // 🎯 REGRA 5: Contradições emocionais (remove emoções fracas quando há opostas fortes)
  const emotionalOpposites = {
    'happy': ['sad', 'frustrated', 'desmotivacao'],
    'excited': ['tired', 'desmotivacao', 'melancholy'],
    'focused': ['confusao', 'procrastinacao'],
    'motivated': ['desmotivacao', 'procrastinacao'],
    'calm': ['anxious', 'stressed', 'frustrated']
  }
  
  Object.entries(emotionalOpposites).forEach(([emotion, opposites]) => {
    if (validatedEmotions[emotion] && validatedEmotions[emotion] >= 2) {
      opposites.forEach(opposite => {
        if (validatedEmotions[opposite] && validatedEmotions[opposite] < validatedEmotions[emotion]) {
          delete validatedEmotions[opposite]
          contextualClues.push(`Validação: Contradição emocional - ${opposite} removido devido a ${emotion} dominante`)
        }
      })
    }
  })
  
  return validatedEmotions
}
