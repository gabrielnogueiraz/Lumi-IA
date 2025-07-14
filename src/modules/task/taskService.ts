import { prisma } from '../../prisma/client'
import { tasks, Priority } from '@prisma/client'

export interface TaskCreateData {
  title: string
  description?: string
  priority: Priority
  startAt?: Date
  endAt?: Date
  pomodoroGoal?: number
  columnId: string
}

export interface TaskUpdateData {
  title?: string
  description?: string
  priority?: Priority
  completed?: boolean
  startAt?: Date
  endAt?: Date
  pomodoroGoal?: number
}

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

  async findTasksInTimeRange(userId: string, startDate: Date, endDate: Date): Promise<tasks[]> {
    return prisma.tasks.findMany({
      where: {
        userId,
        OR: [
          {
            startAt: {
              gte: startDate,
              lte: endDate
            }
          },
          {
            endAt: {
              gte: startDate,
              lte: endDate
            }
          }
        ]
      },
      orderBy: { startAt: 'asc' }
    })
  }

  async createTask(userId: string, data: TaskCreateData): Promise<tasks> {
    const task = await prisma.tasks.create({
      data: {
        id: crypto.randomUUID(),
        userId,
        title: data.title,
        description: data.description,
        priority: data.priority,
        startAt: data.startAt,
        endAt: data.endAt,
        pomodoroGoal: data.pomodoroGoal || 1,
        columnId: data.columnId,
        completed: false,
        createdAt: new Date(),
        updatedAt: new Date()
      }
    })

    console.log(`✅ Tarefa criada via Lumi: ${task.title} (${task.priority})`)
    return task
  }

  async updateTask(taskId: string, userId: string, data: TaskUpdateData): Promise<tasks> {
    const task = await prisma.tasks.findFirst({
      where: { id: taskId, userId }
    })

    if (!task) {
      throw new Error('Tarefa não encontrada ou sem permissão')
    }

    return prisma.tasks.update({
      where: { id: taskId },
      data: {
        ...data,
        updatedAt: new Date()
      }
    })
  }

  async deleteTask(taskId: string, userId: string): Promise<tasks> {
    const task = await prisma.tasks.findFirst({
      where: { id: taskId, userId }
    })

    if (!task) {
      throw new Error('Tarefa não encontrada ou sem permissão')
    }

    return prisma.tasks.delete({
      where: { id: taskId }
    })
  }

  async completeTask(taskId: string, userId: string): Promise<tasks> {
    return this.updateTask(taskId, userId, { completed: true })
  }

  async findTaskById(taskId: string, userId: string): Promise<tasks | null> {
    return prisma.tasks.findFirst({
      where: { id: taskId, userId }
    })
  }

  async searchTasks(userId: string, query: string, limit: number = 5): Promise<tasks[]> {
    return prisma.tasks.findMany({
      where: {
        userId,
        OR: [
          { title: { contains: query, mode: 'insensitive' } },
          { description: { contains: query, mode: 'insensitive' } }
        ]
      },
      orderBy: [
        { priority: 'desc' },
        { createdAt: 'desc' }
      ],
      take: limit
    })
  }

  async getDefaultColumn(userId: string): Promise<string> {
    const board = await prisma.boards.findFirst({
      where: { userId },
      include: { columns: true }
    })

    if (!board || !board.columns.length) {
      const newBoard = await prisma.boards.create({
        data: {
          id: crypto.randomUUID(),
          title: 'Minha Agenda',
          userId,
          createdAt: new Date(),
          updatedAt: new Date()
        }
      })

      const column = await prisma.columns.create({
        data: {
          id: crypto.randomUUID(),
          title: 'A Fazer',
          order: 0,
          boardId: newBoard.id,
          createdAt: new Date(),
          updatedAt: new Date()
        }
      })

      return column.id
    }

    return board.columns[0].id
  }
}
