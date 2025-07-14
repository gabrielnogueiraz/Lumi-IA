import { DateTime } from 'luxon'

export function getCurrentTimeOfDay(): 'morning' | 'afternoon' | 'evening' | 'night' {
  const hour = DateTime.now().hour
  
  if (hour >= 6 && hour < 12) return 'morning'
  if (hour >= 12 && hour < 18) return 'afternoon'
  if (hour >= 18 && hour < 22) return 'evening'
  return 'night'
}

export function formatDateTime(date: Date): string {
  return DateTime.fromJSDate(date)
    .setLocale('pt-BR')
    .toFormat('dd/MM/yyyy HH:mm')
}

export function isRecentMemory(createdAt: Date, daysThreshold: number = 7): boolean {
  const now = DateTime.now()
  const memoryDate = DateTime.fromJSDate(createdAt)
  return now.diff(memoryDate, 'days').days <= daysThreshold
}

export function generateUniqueId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}

export function sanitizeInput(input: string): string {
  return input
    .trim()
    .replace(/[<>]/g, '') // Remove possíveis tags HTML
    .substring(0, 2000) // Limita tamanho
}

export function extractHashtags(text: string): string[] {
  const hashtagRegex = /#[\w\u00C0-\u017F]+/g
  const matches = text.match(hashtagRegex)
  return matches ? matches.map(tag => tag.substring(1).toLowerCase()) : []
}

export function calculateTextSimilarity(text1: string, text2: string): number {
  const words1 = text1.toLowerCase().split(/\s+/)
  const words2 = text2.toLowerCase().split(/\s+/)
  
  const intersection = words1.filter(word => words2.includes(word))
  const union = [...new Set([...words1, ...words2])]
  
  return intersection.length / union.length
}

export function prioritizeMemories(memories: any[], userMessage: string): any[] {
  return memories
    .map(memory => ({
      ...memory,
      relevanceScore: calculateTextSimilarity(memory.content, userMessage)
    }))
    .sort((a, b) => {
      // Prioriza por relevância e importância
      const scoreA = a.relevanceScore + (getImportanceWeight(a.importance))
      const scoreB = b.relevanceScore + (getImportanceWeight(b.importance))
      return scoreB - scoreA
    })
}

function getImportanceWeight(importance: string): number {
  switch (importance) {
    case 'CRITICAL': return 1.0
    case 'HIGH': return 0.7
    case 'MEDIUM': return 0.4
    case 'LOW': return 0.1
    default: return 0
  }
}
