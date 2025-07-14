import { EmotionalAnalysis } from '../types'

const emotionalKeywords = {
  happy: ['feliz', 'alegre', 'animado', 'contente', 'satisfeito', 'empolgado', 'bem', 'ótimo', 'maravilhoso', 'incrível'],
  sad: ['triste', 'deprimido', 'desanimado', 'abatido', 'melancólico', 'mal', 'péssimo', 'ruim', 'chateado'],
  anxious: ['ansioso', 'nervoso', 'preocupado', 'tenso', 'estressado', 'inquieto', 'agitado', 'aflito'],
  motivated: ['motivado', 'determinado', 'focado', 'produtivo', 'energizado', 'inspirado', 'pronto', 'vamos'],
  tired: ['cansado', 'exausto', 'esgotado', 'fatigado', 'sonolento', 'acabado', 'sem energia'],
  focused: ['concentrado', 'focado', 'atento', 'determinado', 'direcionado', 'centrado'],
  stressed: ['estressado', 'sobrecarregado', 'pressionado', 'tenso', 'sob pressão', 'sufocado']
}

export function analyzeEmotion(message: string): EmotionalAnalysis {
  const lowerMessage = message.toLowerCase()
  const detectedEmotions: Record<string, number> = {}
  const foundKeywords: string[] = []

  // Analisa cada categoria emocional
  Object.entries(emotionalKeywords).forEach(([emotion, keywords]) => {
    const matches = keywords.filter(keyword => 
      lowerMessage.includes(keyword)
    )
    
    if (matches.length > 0) {
      detectedEmotions[emotion] = matches.length
      foundKeywords.push(...matches)
    }
  })

  // Pontuação baseada em contexto
  if (lowerMessage.includes('não consigo') || lowerMessage.includes('não sei')) {
    detectedEmotions.anxious = (detectedEmotions.anxious || 0) + 1
  }
  
  if (lowerMessage.includes('!')) {
    detectedEmotions.motivated = (detectedEmotions.motivated || 0) + 0.5
  }

  // Encontra a emoção dominante
  const dominantEmotion = Object.entries(detectedEmotions)
    .sort(([,a], [,b]) => b - a)[0]

  const detectedMood = dominantEmotion 
    ? dominantEmotion[0] as EmotionalAnalysis['detectedMood']
    : 'neutral'
  
  const confidence = dominantEmotion 
    ? Math.min(dominantEmotion[1] / 3, 1) 
    : 0

  // Define estratégia de resposta
  const responseStrategy = getResponseStrategy(detectedMood)

  return {
    detectedMood,
    confidence,
    keywords: foundKeywords,
    responseStrategy
  }
}

function getResponseStrategy(mood: EmotionalAnalysis['detectedMood']): EmotionalAnalysis['responseStrategy'] {
  switch (mood) {
    case 'sad':
    case 'anxious':
      return 'support'
    case 'tired':
      return 'calm'
    case 'stressed':
      return 'calm'
    case 'happy':
    case 'motivated':
      return 'energize'
    case 'focused':
      return 'encourage'
    default:
      return 'motivate'
  }
}

export function getEmotionalTone(strategy: EmotionalAnalysis['responseStrategy']): 'supportive' | 'motivational' | 'calm' | 'enthusiastic' | 'gentle' {
  switch (strategy) {
    case 'support':
      return 'supportive'
    case 'calm':
      return 'calm'
    case 'energize':
      return 'enthusiastic'
    case 'encourage':
      return 'motivational'
    case 'motivate':
      return 'motivational'
    default:
      return 'gentle'
  }
}
