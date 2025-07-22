import { z } from 'zod'

// Schema personalizado para aceitar IDs no formato Nano ID ou UUID
const idSchema = z.string().refine(
  (val) => {
    // Aceita UUID padrão (36 caracteres com hífens)
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
    // Aceita Nano ID (tipicamente 21 caracteres, mas pode variar)
    const nanoIdRegex = /^[A-Za-z0-9_-]{10,30}$/
    
    return uuidRegex.test(val) || nanoIdRegex.test(val)
  },
  {
    message: "ID deve ser um UUID válido ou um Nano ID válido"
  }
)

// Esquemas para validação de entrada
export const askRequestSchema = z.object({
  message: z.string().min(1).max(2000),
  userId: idSchema,
  context: z.object({
    currentTask: z.string().optional(),
    mood: z.enum([
      'happy', 'sad', 'anxious', 'motivated', 'tired', 'focused', 'stressed',
      'confused', 'overwhelmed', 'procrastinating', 'excited', 'determined',
      'frustrated', 'calm', 'energetic', 'melancholy', 'hopeful', 'stuck',
      'desmotivacao', 'procrastinacao', 'confusao'
      , 'sobrecarregado', 'entusiasmo', 'foco'
    ]).optional(),
    timeOfDay: z.enum(['morning', 'afternoon', 'evening', 'night']).optional(),
  }).optional(),
})

export const memoryCreateSchema = z.object({
  userId: idSchema,
  type: z.enum(['PERSONAL_INFO', 'PERSONAL_CONTEXT', 'WORK_CONTEXT', 'STUDY_CONTEXT', 'PRODUCTIVITY_PATTERN', 'EMOTIONAL_STATE', 'COMMUNICATION_STYLE', 'GOALS_PROJECTS', 'PREFERENCES', 'IMPORTANT_DATES', 'FEEDBACK']),
  content: z.string().min(1).max(5000),
  importance: z.enum(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']).default('MEDIUM'),
  emotionalContext: z.string().optional(),
  productivityPattern: z.string().optional(),
  communicationStyle: z.string().optional(),
  tags: z.array(z.string()).default([]),
  expiresAt: z.date().optional(),
})

export const memoryUpdateSchema = memoryCreateSchema.partial().extend({
  id: z.string().uuid(), // LumiMemory IDs são UUIDs gerados pelo Prisma
})

export const memoryQuerySchema = z.object({
  userId: idSchema,
  type: z.enum(['PERSONAL_INFO', 'PERSONAL_CONTEXT', 'WORK_CONTEXT', 'STUDY_CONTEXT', 'PRODUCTIVITY_PATTERN', 'EMOTIONAL_STATE', 'COMMUNICATION_STYLE', 'GOALS_PROJECTS', 'PREFERENCES', 'IMPORTANT_DATES', 'FEEDBACK']).optional(),
  importance: z.enum(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']).optional(),
  tags: z.array(z.string()).optional(),
  limit: z.number().min(1).max(100).default(50),
  offset: z.number().min(0).default(0),
})

// Tipos TypeScript derivados dos schemas
export type AskRequest = z.infer<typeof askRequestSchema>
export type MemoryCreate = z.infer<typeof memoryCreateSchema>
export type MemoryUpdate = z.infer<typeof memoryUpdateSchema>
export type MemoryQuery = z.infer<typeof memoryQuerySchema>

// Novos tipos para contexto de conversa e memória de curto prazo
export interface ConversationContext {
  userId: string
  lastIntent?: string
  currentEmotion?: string
  emotionalIntensity?: 'low' | 'medium' | 'high'
  focusedTaskId?: string
  focusedTaskTitle?: string
  conversationHistory: Array<{
    timestamp: Date
    userMessage: string
    detectedEmotion: string
    intent: string
    aiResponse?: string
  }>
  sessionStartTime: Date
  lastInteractionTime: Date
}

export interface TaskContextMatch {
  taskId: string
  title: string
  similarity: number
  isExactMatch: boolean
  matchedKeywords: string[]
}

export interface EmotionalAnalysis {
  detectedMood: 'happy' | 'sad' | 'anxious' | 'motivated' | 'tired' | 'focused' | 'stressed' | 'neutral' | 'confused' | 'overwhelmed' | 'procrastinating' | 'excited' | 'determined' | 'frustrated' | 'calm' | 'energetic' | 'melancholy' | 'hopeful' | 'stuck' | 'desmotivacao' | 'procrastinacao' | 'confusao' | 'sobrecarregado' | 'entusiasmo' | 'foco' | 'proud' | 'curious'
  confidence: number
  keywords: string[]
  responseStrategy: 'calm' | 'encourage' | 'motivate' | 'support' | 'energize' | 'guide' | 'reassure' | 'challenge' | 'ground' | 'gentle_push' | 'empathize' | 'structure' | 'share_origin'
  emotionalIntensity: 'low' | 'medium' | 'high'
  needsSupport: boolean
  contextualClues: string[]
}

export interface UserContext {
  user: {
    id: string
    name: string
    email: string
  }
  recentMemories: Array<{
    id: string
    type: string
    content: string
    importance: string
    emotionalContext?: string
    productivityPattern?: string
    communicationStyle?: string
    createdAt: Date
    tags: string[]
  }>
  currentTasks: Array<{
    id: string
    title: string
    description?: string
    priority: 'HIGH' | 'MEDIUM' | 'LOW'
    completed: boolean
    startAt?: Date
    endAt?: Date
  }>
  todayTasks: Array<{
    id: string
    title: string
    description?: string
    priority: 'HIGH' | 'MEDIUM' | 'LOW'
    completed: boolean
    startAt?: Date
    endAt?: Date
  }>
  overdueTasks: Array<{
    id: string
    title: string
    description?: string
    priority: 'HIGH' | 'MEDIUM' | 'LOW'
    daysOverdue: number
    startAt?: Date
  }>
  productivityInsights: {
    bestTimeOfDay?: string
    averageCompletionRate?: number
    preferredTaskTypes?: string[]
    communicationStyle?: string
  }
  conversationContext?: ConversationContext
}

export interface TaskResponse {
  success: boolean
  message: string
  taskAction?: string
  conflictDetected?: boolean
  suggestionsMessage?: string
  isEmotionalResponse?: boolean
  emotionalState?: string
  matchedTask?: TaskContextMatch
}
