import { prisma } from '../../prisma/client'
import { tasks, Priority } from '@prisma/client'

export class TaskService {
  async findByUserId(userId: string, limit: number = 10): Promise<tasks[]> {
    return prisma.tasks.findMany({
      where: { userId },
      orderBy: [
        { completed: 'asc' },
        { priority: 'desc' },
        { createdAt: 'desc' }
      ],
      take: limit
    })
  }

  async findPendingTasks(userId: string): Promise<tasks[]> {
    return prisma.tasks.findMany({
      where: { 
        userId, 
        completed: false 
      },
      orderBy: [
        { priority: 'desc' },
        { createdAt: 'desc' }
      ]
    })
  }

  async findTasksByPriority(userId: string, priority: Priority): Promise<tasks[]> {
    return prisma.tasks.findMany({
      where: { 
        userId, 
        priority,
        completed: false 
      },
      orderBy: { createdAt: 'desc' }
    })
  }

  async findUpcomingTasks(userId: string): Promise<tasks[]> {
    const today = new Date()
    const tomorrow = new Date(today)
    tomorrow.setDate(tomorrow.getDate() + 1)

    return prisma.tasks.findMany({
      where: {
        userId,
        completed: false,
        startAt: {
          gte: today,
          lte: tomorrow
        }
      },
      orderBy: { startAt: 'asc' }
    })
  }

  async findOverdueTasks(userId: string): Promise<tasks[]> {
    const now = new Date()

    return prisma.tasks.findMany({
      where: {
        userId,
        completed: false,
        endAt: {
          lt: now
        }
      },
      orderBy: { endAt: 'asc' }
    })
  }

  async markAsCompleted(taskId: string): Promise<tasks> {
    return prisma.tasks.update({
      where: { id: taskId },
      data: { 
        completed: true,
        updatedAt: new Date()
      }
    })
  }

  async getTaskSummary(userId: string): Promise<{
    pending: number
    completed: number
    overdue: number
    today: number
    highPriority: number
  }> {
    const now = new Date()
    const startOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    const endOfDay = new Date(startOfDay)
    endOfDay.setDate(endOfDay.getDate() + 1)

    const [
      pending,
      completed,
      overdue,
      today,
      highPriority
    ] = await Promise.all([
      prisma.tasks.count({
        where: { userId, completed: false }
      }),
      prisma.tasks.count({
        where: { userId, completed: true }
      }),
      prisma.tasks.count({
        where: {
          userId,
          completed: false,
          endAt: { lt: now }
        }
      }),
      prisma.tasks.count({
        where: {
          userId,
          completed: false,
          OR: [
            {
              startAt: {
                gte: startOfDay,
                lt: endOfDay
              }
            },
            {
              endAt: {
                gte: startOfDay,
                lt: endOfDay
              }
            }
          ]
        }
      }),
      prisma.tasks.count({
        where: {
          userId,
          completed: false,
          priority: 'HIGH'
        }
      })
    ])

    return {
      pending,
      completed,
      overdue,
      today,
      highPriority
    }
  }
}
