import { EmotionalAnalysis } from '../types'

const emotionalKeywords = {
  happy: ['feliz', 'alegre', 'animado', 'contente', 'satisfeito', 'empolgado', 'bem', 'ótimo', 'maravilhoso', 'incrível', 'radiante', 'eufórico'],
  sad: ['triste', 'deprimido', 'desanimado', 'abatido', 'melancólico', 'mal', 'péssimo', 'ruim', 'chateado', 'desalentado', 'desolado'],
  anxious: ['ansioso', 'nervoso', 'preocupado', 'tenso', 'estressado', 'inquieto', 'agitado', 'aflito', 'apreensivo', 'angustiado'],
  motivated: ['motivado', 'determinado', 'focado', 'produtivo', 'energizado', 'inspirado', 'pronto', 'vamos', 'decidido', 'resoluto'],
  tired: ['cansado', 'exausto', 'esgotado', 'fatigado', 'sonolento', 'acabado', 'sem energia', 'drenado', 'desgastado'],
  focused: ['concentrado', 'focado', 'atento', 'determinado', 'direcionado', 'centrado', 'na zona', 'ligado'],
  stressed: ['estressado', 'sobrecarregado', 'pressionado', 'tenso', 'sob pressão', 'sufocado', 'oprimido'],
  
  // Estados emocionais existentes expandidos
  confused: ['confuso', 'perdido', 'desorientado', 'sem rumo', 'sem direção', 'não entendo', 'não sei'],
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

  // NOVAS CATEGORIAS EMOCIONAIS SOLICITADAS
  desmotivacao: [
    'desmotivado', 'sem vontade', 'desanimado', 'apático', 'desencorajado',
    'sem energia', 'largado', 'desinteressado', 'sem pique', 'sem ânimo',
    'não tenho vontade', 'tô largado', 'sem gás', 'desestimulado'
  ],
  
  procrastinacao: [
    'procrastinando', 'empurrando', 'adiando', 'enrolando', 'deixando pra depois',
    'não tô afim', 'depois eu faço', 'amanhã eu vejo', 'ainda não', 
    'evitando', 'fugindo', 'escapando', 'esquivando', 'postergando'
  ],
  
  confusao: [
    'confuso', 'perdido', 'sem rumo', 'desorientado', 'atrapalhado',
    'não entendo', 'não sei', 'meio perdido', 'sem direção', 'bagunçado',
    'não faço ideia', 'tô boiando', 'não tô entendendo nada'
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

// Expressões indiretas expandidas com as novas categorias
const indirectEmotionalExpressions = {
  confused: [
    'não sei por onde começar',
    'não entendo nada',
    'estou meio perdido',
    'não faço ideia',
    'que confusão',
    'tá tudo bagunçado',
    'não sei o que fazer',
    'estou sem rumo'
  ],
  
  overwhelmed: [
    'é muita coisa',
    'não dou conta',
    'tá pesado demais',
    'muita pressão',
    'não aguento mais',
    'tá difícil demais',
    'é muita responsabilidade',
    'não consigo mais'
  ],
  
  procrastinating: [
    'não estou no clima',
    'não tenho vontade',
    'deixa pra depois',
    'ainda não',
    'mais tarde eu faço',
    'não tô afim',
    'depois eu vejo',
    'amanhã eu começo'
  ],
  
  stuck: [
    'não sai do lugar',
    'não evolui',
    'tô travado',
    'não consigo avançar',
    'empacou',
    'não vai pra frente',
    'tô bloqueado',
    'não flui'
  ],
  
  frustrated: [
    'que saco',
    'tá difícil',
    'não funciona',
    'que droga',
    'não vai',
    'chatice',
    'que irritante',
    'não dá certo'
  ],
  
  tired: [
    'tô acabado',
    'sem energia',
    'exausto',
    'não aguento',
    'tô drenado',
    'sem pique',
    'morto de cansaço'
  ],
  
  excited: [
    'que legal',
    'adorei',
    'que máximo',
    'muito bom',
    'incrível',
    'fantástico',
    'show de bola'
  ],

  // NOVAS EXPRESSÕES INDIRETAS
  desmotivacao: [
    'não tenho vontade de fazer nada',
    'tô sem pique',
    'sem ânimo pra nada',
    'tô largado',
    'não me anima',
    'sem gás',
    'tô meio apático',
    'não desperta interesse'
  ],
  
  procrastinacao: [
    'vou deixar pra depois',
    'não tô no clima hoje',
    'amanhã eu começo',
    'depois eu vejo isso',
    'não tô afim agora',
    'vou empurrar um pouco',
    'ainda não é hora',
    'deixa quieto por hoje'
  ],
  
  confusao: [
    'não tô entendendo direito',
    'meio perdido aqui',
    'não sei como fazer',
    'tô meio confuso',
    'não tá claro pra mim',
    'tô boiando',
    'meio atrapalhado',
    'não tô conseguindo organizar'
  ],
  
  sobrecarregado: [
    'é muita coisa pra hoje',
    'não vai dar tempo',
    'tá muito pesado',
    'muita pressão em cima',
    'não consigo dar conta',
    'tá sufocante',
    'muita demanda',
    'bombardeado de tarefas'
  ],
  
  entusiasmo: [
    'que energia boa',
    'tô super animado',
    'que empolgação',
    'tô vibrando',
    'que legal isso',
    'adorando a ideia',
    'tô elétrico',
    'cheio de energia'
  ],
  
  foco: [
    'tô concentrado',
    'no modo trabalho',
    'foco total',
    'mente ligada',
    'concentração máxima',
    'na zona de produtividade',
    'mergulhado no trabalho',
    'dedicação total'
  ]
}

// Palavras que intensificam emoções
const intensifiers = ['muito', 'super', 'extremamente', 'completamente', 'totalmente', 'absurdamente', 'demais', 'mega', 'ultra']

// Palavras que indicam necessidade de suporte
const supportIndicators = [
  'ajuda', 'socorro', 'me ajude', 'preciso de', 'não consigo', 'não sei como',
  'não dou conta', 'tô perdido', 'me orienta', 'não aguento', 'difícil demais',
  'me explica', 'não entendo', 'como faz', 'o que fazer'
]

export function analyzeEmotion(message: string): EmotionalAnalysis {
  const lowerMessage = message.toLowerCase()
  const detectedEmotions: Record<string, number> = {}
  const foundKeywords: string[] = []
  const contextualClues: string[] = []
  let emotionalIntensity: 'low' | 'medium' | 'high' = 'low'
  let needsSupport = false

  // Analisa expressões indiretas primeiro (mais específicas e peso maior)
  Object.entries(indirectEmotionalExpressions).forEach(([emotion, expressions]) => {
    expressions.forEach(expression => {
      if (lowerMessage.includes(expression)) {
        detectedEmotions[emotion] = (detectedEmotions[emotion] || 0) + 3 // Peso alto para expressões indiretas
        foundKeywords.push(expression)
        contextualClues.push(`Expressão indireta de ${emotion}: "${expression}"`)
      }
    })
  })

  // Analisa palavras-chave diretas
  Object.entries(emotionalKeywords).forEach(([emotion, keywords]) => {
    keywords.forEach(keyword => {
      if (lowerMessage.includes(keyword)) {
        detectedEmotions[emotion] = (detectedEmotions[emotion] || 0) + 1
        foundKeywords.push(keyword)
      }
    })
  })

  // Detecta intensificadores e modifica pontuações
  const hasIntensifier = intensifiers.some(intensifier => lowerMessage.includes(intensifier))
  if (hasIntensifier) {
    emotionalIntensity = 'high'
    // Multiplica todas as emoções detectadas por 1.5
    Object.keys(detectedEmotions).forEach(emotion => {
      detectedEmotions[emotion] *= 1.5
    })
    contextualClues.push(`Intensificador detectado: emoção amplificada`)
  }

  // Detecta necessidade de suporte
  needsSupport = supportIndicators.some(indicator => lowerMessage.includes(indicator))
  if (needsSupport) {
    contextualClues.push(`Indicadores de necessidade de suporte detectados`)
  }

  // Análise contextual avançada
  analyzeAdvancedContextualClues(lowerMessage, detectedEmotions, contextualClues)

  // Determina intensidade baseada na pontuação total
  const totalScore = Object.values(detectedEmotions).reduce((sum, score) => sum + score, 0)
  if (totalScore >= 4) emotionalIntensity = 'high'
  else if (totalScore >= 2) emotionalIntensity = 'medium'

  // Encontra a emoção dominante
  const dominantEmotion = Object.entries(detectedEmotions)
    .sort(([,a], [,b]) => b - a)[0]

  const detectedMood = dominantEmotion 
    ? dominantEmotion[0] as EmotionalAnalysis['detectedMood']
    : 'neutral'
  
  const confidence = dominantEmotion 
    ? Math.min(dominantEmotion[1] / 5, 1) // Ajustado para as novas pontuações
    : 0

  // Define estratégia de resposta baseada na emoção e contexto
  const responseStrategy = getAdvancedResponseStrategy(detectedMood, emotionalIntensity, needsSupport)

  return {
    detectedMood,
    confidence,
    keywords: foundKeywords,
    responseStrategy,
    emotionalIntensity,
    needsSupport,
    contextualClues
  }
}

/**
 * Análise contextual expandida para detectar padrões mais sutis
 */
function analyzeAdvancedContextualClues(
  message: string, 
  detectedEmotions: Record<string, number>,
  contextualClues: string[]
) {
  // Pontuação e símbolos
  if (message.includes('...')) {
    detectedEmotions.melancholy = (detectedEmotions.melancholy || 0) + 0.5
    detectedEmotions.confusao = (detectedEmotions.confusao || 0) + 0.5
    contextualClues.push('Reticências indicam hesitação/melancolia')
  }
  
  if (message.includes('?')) {
    detectedEmotions.confusao = (detectedEmotions.confusao || 0) + 0.5
    contextualClues.push('Interrogação indica dúvida/confusão')
  }
  
  const exclamationCount = (message.match(/!/g) || []).length
  if (exclamationCount >= 2) {
    detectedEmotions.entusiasmo = (detectedEmotions.entusiasmo || 0) + 1
    detectedEmotions.excited = (detectedEmotions.excited || 0) + 0.5
    contextualClues.push(`Múltiplas exclamações (${exclamationCount}) indicam entusiasmo`)
  }

  // Padrões de linguagem específicos
  if (message.includes('não') && (message.includes('consigo') || message.includes('sei'))) {
    detectedEmotions.confusao = (detectedEmotions.confusao || 0) + 1
    detectedEmotions.desmotivacao = (detectedEmotions.desmotivacao || 0) + 0.5
    contextualClues.push('Padrão "não consigo/sei" indica confusão/desmotivação')
  }

  if (message.includes('preciso') || message.includes('tenho que')) {
    detectedEmotions.motivated = (detectedEmotions.motivated || 0) + 0.5
    detectedEmotions.foco = (detectedEmotions.foco || 0) + 0.5
    contextualClues.push('Linguagem de necessidade/obrigação indica motivação/foco')
  }

  // Linguagem temporal que indica procrastinação
  const procrastinationTimeWords = ['depois', 'mais tarde', 'amanhã', 'próxima', 'quando der']
  if (procrastinationTimeWords.some(word => message.includes(word))) {
    detectedEmotions.procrastinacao = (detectedEmotions.procrastinacao || 0) + 1
    contextualClues.push('Linguagem temporal indica procrastinação')
  }

  // Expressões de sobrecarga quantitativa
  if ((message.includes('muito') || message.includes('muita')) && 
      (message.includes('coisa') || message.includes('trabalho') || message.includes('tarefa'))) {
    detectedEmotions.sobrecarregado = (detectedEmotions.sobrecarregado || 0) + 1
    contextualClues.push('Quantificadores de sobrecarga detectados')
  }

  // Expressões positivas intensas
  const positiveIntense = ['adorei', 'amei', 'perfeito', 'incrível', 'fantástico', 'maravilhoso']
  if (positiveIntense.some(word => message.includes(word))) {
    detectedEmotions.entusiasmo = (detectedEmotions.entusiasmo || 0) + 1
    detectedEmotions.excited = (detectedEmotions.excited || 0) + 1
    contextualClues.push('Expressões positivas intensas detectadas')
  }

  // Detecção de foco/concentração
  const focusWords = ['concentrado', 'focado', 'produtivo', 'trabalhando', 'fazendo']
  if (focusWords.some(word => message.includes(word))) {
    detectedEmotions.foco = (detectedEmotions.foco || 0) + 1
    contextualClues.push('Indicadores de foco/concentração detectados')
  }
}

function getAdvancedResponseStrategy(
  mood: EmotionalAnalysis['detectedMood'], 
  intensity: 'low' | 'medium' | 'high',
  needsSupport: boolean
): EmotionalAnalysis['responseStrategy'] {
  
  // Se claramente precisa de suporte, prioriza isso
  if (needsSupport) {
    return 'support'
  }

  switch (mood) {
    // Estados existentes
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
