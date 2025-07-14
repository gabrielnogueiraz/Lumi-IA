import { prisma } from '../../prisma/client'
import { User } from '@prisma/client'

export class UserService {
  async findById(id: string): Promise<User | null> {
    return prisma.user.findUnique({
      where: { id },
      include: {
        tasks: {
          where: { completed: false },
          orderBy: { createdAt: 'desc' },
          take: 10
        }
      }
    })
  }

  async findByEmail(email: string): Promise<User | null> {
    return prisma.user.findUnique({
      where: { email }
    })
  }

  async updateLastCheckIn(userId: string): Promise<User> {
    return prisma.user.update({
      where: { id: userId },
      data: { lastCheckIn: new Date() }
    })
  }

  async getUserStats(userId: string): Promise<{
    totalTasks: number
    completedTasks: number
    activeTasks: number
    completionRate: number
  }> {
    const [totalTasks, completedTasks] = await Promise.all([
      prisma.tasks.count({
        where: { userId }
      }),
      prisma.tasks.count({
        where: { userId, completed: true }
      })
    ])

    const activeTasks = totalTasks - completedTasks
    const completionRate = totalTasks > 0 ? completedTasks / totalTasks : 0

    return {
      totalTasks,
      completedTasks,
      activeTasks,
      completionRate
    }
  }
}
