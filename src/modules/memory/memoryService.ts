import { prisma } from '../../prisma/client'
import { MemoryCreate, MemoryUpdate, MemoryQuery } from '../../types'
import { LumiMemory, MemoryType, ImportanceLevel } from '@prisma/client'

export class MemoryService {
  async create(data: MemoryCreate): Promise<LumiMemory> {
    return prisma.lumiMemory.create({
      data: {
        ...data,
        id: undefined, // Let Prisma generate the UUID
      }
    })
  }

  async findByUserId(query: MemoryQuery): Promise<LumiMemory[]> {
    const where: any = {
      userId: query.userId,
      OR: [
        { expiresAt: { gt: new Date() } }, // Não expirado
        { expiresAt: null }                // Sem data de expiração
      ]
    }

    if (query.type) {
      where.type = query.type
    }

    if (query.importance) {
      where.importance = query.importance
    }

    if (query.tags && query.tags.length > 0) {
      where.tags = {
        hasSome: query.tags
      }
    }

    return prisma.lumiMemory.findMany({
      where,
      orderBy: [
        { importance: 'desc' },
        { updatedAt: 'desc' }
      ],
      take: query.limit,
      skip: query.offset
    })
  }

  async findRecentMemories(userId: string, limit: number = 10): Promise<LumiMemory[]> {
    return prisma.lumiMemory.findMany({
      where: {
        userId,
        OR: [
          { expiresAt: { gt: new Date() } },
          { expiresAt: null }
        ]
      },
      orderBy: [
        { importance: 'desc' },
        { updatedAt: 'desc' }
      ],
      take: limit
    })
  }

  async findByType(userId: string, type: MemoryType): Promise<LumiMemory[]> {
    return prisma.lumiMemory.findMany({
      where: {
        userId,
        type,
        OR: [
          { expiresAt: { gt: new Date() } },
          { expiresAt: null }
        ]
      },
      orderBy: { updatedAt: 'desc' }
    })
  }

  async update(id: string, data: Partial<MemoryUpdate>): Promise<LumiMemory> {
    return prisma.lumiMemory.update({
      where: { id },
      data: {
        ...data,
        updatedAt: new Date()
      }
    })
  }

  async delete(id: string): Promise<void> {
    await prisma.lumiMemory.delete({
      where: { id }
    })
  }

  async deleteExpired(): Promise<number> {
    const result = await prisma.lumiMemory.deleteMany({
      where: {
        expiresAt: {
          lt: new Date()
        }
      }
    })
    return result.count
  }

  async searchByContent(userId: string, searchTerm: string): Promise<LumiMemory[]> {
    return prisma.lumiMemory.findMany({
      where: {
        userId,
        content: {
          contains: searchTerm,
          mode: 'insensitive'
        },
        OR: [
          { expiresAt: { gt: new Date() } },
          { expiresAt: null }
        ]
      },
      orderBy: [
        { importance: 'desc' },
        { updatedAt: 'desc' }
      ]
    })
  }

  async getProductivityPatterns(userId: string): Promise<{
    bestTimeOfDay?: string
    averageCompletionRate?: number
    communicationStyle?: string
    preferredTaskTypes?: string[]
  }> {
    const patterns = await prisma.lumiMemory.findMany({
      where: {
        userId,
        type: 'PRODUCTIVITY_PATTERN',
        OR: [
          { expiresAt: { gt: new Date() } },
          { expiresAt: null }
        ]
      },
      orderBy: { updatedAt: 'desc' }
    })

    const communicationStyles = await prisma.lumiMemory.findMany({
      where: {
        userId,
        type: 'COMMUNICATION_STYLE',
        OR: [
          { expiresAt: { gt: new Date() } },
          { expiresAt: null }
        ]
      },
      orderBy: { updatedAt: 'desc' }
    })

    // Analisa os padrões para extrair insights
    const insights: any = {}

    if (patterns.length > 0) {
      const latestPattern = patterns[0]
      if (latestPattern.productivityPattern) {
        try {
          const parsed = JSON.parse(latestPattern.productivityPattern)
          insights.bestTimeOfDay = parsed.bestTimeOfDay
          insights.averageCompletionRate = parsed.averageCompletionRate
          insights.preferredTaskTypes = parsed.preferredTaskTypes
        } catch (e) {
          // Se não conseguir parsear, extrai texto
          insights.bestTimeOfDay = latestPattern.content.includes('manhã') ? 'morning' :
                                  latestPattern.content.includes('tarde') ? 'afternoon' :
                                  latestPattern.content.includes('noite') ? 'evening' : undefined
        }
      }
    }

    if (communicationStyles.length > 0) {
      insights.communicationStyle = communicationStyles[0].communicationStyle || 
                                   communicationStyles[0].content
    }

    return insights
  }

  async createProductivityInsight(
    userId: string,
    content: string,
    pattern: any
  ): Promise<LumiMemory> {
    return this.create({
      userId,
      type: 'PRODUCTIVITY_PATTERN',
      content,
      importance: 'HIGH',
      productivityPattern: JSON.stringify(pattern),
      tags: ['analytics', 'productivity']
    })
  }
}
