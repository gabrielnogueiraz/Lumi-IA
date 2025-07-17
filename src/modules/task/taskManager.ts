import { z } from 'zod'
import { TaskService, TaskCreateData, TaskUpdateData } from './taskService'
import { prisma } from '../../prisma/client'
import { Priority } from '@prisma/client'
import crypto from 'crypto'

// Schemas de validação com Zod
const createTaskSchema = z.object({
  title: z.string().min(1, 'Título é obrigatório').max(200, 'Título muito longo'),
  description: z.string().optional(),
  priority: z.enum(['HIGH', 'MEDIUM', 'LOW']).default('MEDIUM'),
  startAt: z.date().optional(),
  endAt: z.date().optional(),
  pomodoroGoal: z.number().int().positive().default(1),
  boardTitle: z.string().optional(), // Para especificar quadro específico
})

const updateTaskSchema = z.object({
  taskId: z.string().uuid('ID da tarefa inválido'),
  title: z.string().min(1).max(200).optional(),
  description: z.string().optional(),
  priority: z.enum(['HIGH', 'MEDIUM', 'LOW']).optional(),
  startAt: z.date().optional(),
  endAt: z.date().optional(),
  pomodoroGoal: z.number().int().positive().optional(),
  completed: z.boolean().optional(),
})

const taskActionSchema = z.object({
  userId: z.string().uuid('ID do usuário inválido'),
  taskId: z.string().uuid('ID da tarefa inválido').optional(),
})

type CreateTaskInput = z.infer<typeof createTaskSchema> & { userId: string }
type UpdateTaskInput = z.infer<typeof updateTaskSchema> & { userId: string }

export interface TaskOperationResult {
  success: boolean
  message: string
  data?: any
  error?: string
}

/**
 * Classe principal para gerenciamento de tarefas da Lumi
 * Implementa todas as operações CRUD com validações e logs completos
 */
export class TaskManager {
  private taskService = new TaskService()

  /**
   * Cria uma nova tarefa com validações completas
   * @param input Dados da tarefa a ser criada
   * @returns Resultado da operação
   */
  async createTask(input: CreateTaskInput): Promise<TaskOperationResult> {
    try {
      console.log(`🔄 [TaskManager] Iniciando criação de tarefa para usuário: ${input.userId}`)
      console.log(`🔍 [TaskManager] Input completo:`, JSON.stringify(input, null, 2))
      
      // Validar entrada com Zod
      const validatedData = createTaskSchema.parse(input)
      
      // Validar datas se fornecidas
      if (validatedData.startAt && validatedData.endAt) {
        if (validatedData.startAt >= validatedData.endAt) {
          return {
            success: false,
            message: 'Data de início deve ser anterior à data de fim',
            error: 'INVALID_DATE_RANGE'
          }
        }
      }

      // Determinar ou criar o quadro e coluna
      const columnId = await this.getOrCreateColumnForTask(
        input.userId, 
        validatedData.title, 
        validatedData.boardTitle
      )

      // Preparar dados para criação
      const taskData: TaskCreateData = {
        title: validatedData.title,
        description: validatedData.description,
        priority: validatedData.priority as Priority,
        startAt: validatedData.startAt,
        endAt: validatedData.endAt,
        pomodoroGoal: validatedData.pomodoroGoal,
        columnId
      }

      // Verificar conflitos de horário se necessário
      if (validatedData.startAt && validatedData.endAt) {
        const conflicts = await this.taskService.findTasksInTimeRange(
          input.userId,
          validatedData.startAt,
          validatedData.endAt
        )

        if (conflicts.length > 0) {
          console.log(`⚠️ [TaskManager] Conflito detectado para tarefa: ${validatedData.title}`)
          return {
            success: false,
            message: `Conflito detectado: você já tem "${conflicts[0].title}" agendado para esse horário`,
            error: 'TIME_CONFLICT',
            data: { conflicts }
          }
        }
      }

      // Criar a tarefa
      console.log(`🔍 [TaskManager] Dados para criação:`, JSON.stringify(taskData, null, 2))
      console.log(`🔍 [TaskManager] userId que será usado:`, input.userId)
      
      const task = await this.taskService.createTask(input.userId, taskData)
      
      console.log(`✅ [TaskManager] Tarefa criada com sucesso - ID: ${task.id}, Título: "${task.title}", Prioridade: ${task.priority}`)
      console.log(`🔍 [TaskManager] Tarefa criada - userId: ${task.userId}, columnId: ${task.columnId}`)

      return {
        success: true,
        message: `Tarefa "${task.title}" criada com sucesso!`,
        data: task
      }

    } catch (error) {
      console.error(`❌ [TaskManager] Erro ao criar tarefa:`, error)
      
      if (error instanceof z.ZodError) {
        return {
          success: false,
          message: 'Dados inválidos para criação da tarefa',
          error: 'VALIDATION_ERROR',
          data: { errors: error.errors }
        }
      }

      return {
        success: false,
        message: 'Erro interno ao criar tarefa',
        error: 'INTERNAL_ERROR'
      }
    }
  }

  /**
   * Atualiza uma tarefa existente
   * @param input Dados da tarefa a ser atualizada
   * @returns Resultado da operação
   */
  async updateTask(input: UpdateTaskInput): Promise<TaskOperationResult> {
    try {
      console.log(`🔄 [TaskManager] Iniciando atualização de tarefa - ID: ${input.taskId}, Usuário: ${input.userId}`)
      
      // Validar entrada
      const validatedData = updateTaskSchema.parse(input)
      
      // Verificar se a tarefa existe e pertence ao usuário
      const existingTask = await this.taskService.findTaskById(validatedData.taskId, input.userId)
      if (!existingTask) {
        console.log(`❌ [TaskManager] Tarefa não encontrada ou sem permissão - ID: ${validatedData.taskId}`)
        return {
          success: false,
          message: 'Tarefa não encontrada ou você não tem permissão para editá-la',
          error: 'TASK_NOT_FOUND'
        }
      }

      // Validar datas se fornecidas
      if (validatedData.startAt && validatedData.endAt) {
        if (validatedData.startAt >= validatedData.endAt) {
          return {
            success: false,
            message: 'Data de início deve ser anterior à data de fim',
            error: 'INVALID_DATE_RANGE'
          }
        }
      }

      // Preparar dados para atualização (apenas campos fornecidos)
      const updateData: TaskUpdateData = {}
      if (validatedData.title !== undefined) updateData.title = validatedData.title
      if (validatedData.description !== undefined) updateData.description = validatedData.description
      if (validatedData.priority !== undefined) updateData.priority = validatedData.priority as Priority
      if (validatedData.startAt !== undefined) updateData.startAt = validatedData.startAt
      if (validatedData.endAt !== undefined) updateData.endAt = validatedData.endAt
      if (validatedData.pomodoroGoal !== undefined) updateData.pomodoroGoal = validatedData.pomodoroGoal
      if (validatedData.completed !== undefined) updateData.completed = validatedData.completed

      // Atualizar a tarefa
      const updatedTask = await this.taskService.updateTask(validatedData.taskId, input.userId, updateData)
      
      console.log(`✅ [TaskManager] Tarefa atualizada com sucesso - ID: ${updatedTask.id}, Título: "${updatedTask.title}"`)

      return {
        success: true,
        message: `Tarefa "${updatedTask.title}" atualizada com sucesso!`,
        data: updatedTask
      }

    } catch (error) {
      console.error(`❌ [TaskManager] Erro ao atualizar tarefa:`, error)
      
      if (error instanceof z.ZodError) {
        return {
          success: false,
          message: 'Dados inválidos para atualização da tarefa',
          error: 'VALIDATION_ERROR',
          data: { errors: error.errors }
        }
      }

      return {
        success: false,
        message: 'Erro interno ao atualizar tarefa',
        error: 'INTERNAL_ERROR'
      }
    }
  }

  /**
   * Exclui uma tarefa
   * @param userId ID do usuário
   * @param taskId ID da tarefa
   * @returns Resultado da operação
   */
  async deleteTask(userId: string, taskId: string): Promise<TaskOperationResult> {
    try {
      console.log(`🔄 [TaskManager] Iniciando exclusão de tarefa - ID: ${taskId}, Usuário: ${userId}`)
      
      // Validar IDs
      const validatedData = taskActionSchema.parse({ userId, taskId })
      
      // Verificar se a tarefa existe e pertence ao usuário
      const existingTask = await this.taskService.findTaskById(taskId, userId)
      if (!existingTask) {
        console.log(`❌ [TaskManager] Tarefa não encontrada ou sem permissão - ID: ${taskId}`)
        return {
          success: false,
          message: 'Tarefa não encontrada ou você não tem permissão para excluí-la',
          error: 'TASK_NOT_FOUND'
        }
      }

      // Excluir a tarefa
      const deletedTask = await this.taskService.deleteTask(taskId, userId)
      
      console.log(`✅ [TaskManager] Tarefa excluída com sucesso - ID: ${deletedTask.id}, Título: "${deletedTask.title}"`)

      return {
        success: true,
        message: `Tarefa "${deletedTask.title}" excluída com sucesso!`,
        data: deletedTask
      }

    } catch (error) {
      console.error(`❌ [TaskManager] Erro ao excluir tarefa:`, error)
      
      if (error instanceof z.ZodError) {
        return {
          success: false,
          message: 'Dados inválidos para exclusão da tarefa',
          error: 'VALIDATION_ERROR',
          data: { errors: error.errors }
        }
      }

      return {
        success: false,
        message: 'Erro interno ao excluir tarefa',
        error: 'INTERNAL_ERROR'
      }
    }
  }

  /**
   * Marca ou desmarca uma tarefa como concluída
   * @param userId ID do usuário
   * @param taskId ID da tarefa
   * @param completed Status de conclusão (true = concluída, false = reabrir)
   * @returns Resultado da operação
   */
  async toggleTaskCompletion(userId: string, taskId: string, completed: boolean = true): Promise<TaskOperationResult> {
    try {
      const action = completed ? 'conclusão' : 'reabertura'
      console.log(`🔄 [TaskManager] Iniciando ${action} de tarefa - ID: ${taskId}, Usuário: ${userId}`)
      
      // Validar IDs
      const validatedData = taskActionSchema.parse({ userId, taskId })
      
      // Verificar se a tarefa existe e pertence ao usuário
      const existingTask = await this.taskService.findTaskById(taskId, userId)
      if (!existingTask) {
        console.log(`❌ [TaskManager] Tarefa não encontrada ou sem permissão - ID: ${taskId}`)
        return {
          success: false,
          message: 'Tarefa não encontrada ou você não tem permissão para modificá-la',
          error: 'TASK_NOT_FOUND'
        }
      }

      // Verificar se já está no status desejado
      if (existingTask.completed === completed) {
        const statusText = completed ? 'já está concluída' : 'já está aberta'
        return {
          success: false,
          message: `A tarefa "${existingTask.title}" ${statusText}`,
          error: 'ALREADY_IN_STATUS'
        }
      }

      // Atualizar status da tarefa
      const updatedTask = await this.taskService.updateTask(taskId, userId, { completed })
      
      const statusText = completed ? 'concluída' : 'reaberta'
      console.log(`✅ [TaskManager] Tarefa ${statusText} com sucesso - ID: ${updatedTask.id}, Título: "${updatedTask.title}"`)

      return {
        success: true,
        message: `Tarefa "${updatedTask.title}" ${statusText} com sucesso!`,
        data: updatedTask
      }

    } catch (error) {
      console.error(`❌ [TaskManager] Erro ao alterar status da tarefa:`, error)
      
      if (error instanceof z.ZodError) {
        return {
          success: false,
          message: 'Dados inválidos para alteração de status da tarefa',
          error: 'VALIDATION_ERROR',
          data: { errors: error.errors }
        }
      }

      return {
        success: false,
        message: 'Erro interno ao alterar status da tarefa',
        error: 'INTERNAL_ERROR'
      }
    }
  }

  /**
   * Método de conveniência para marcar tarefa como concluída
   */
  async completeTask(userId: string, taskId: string): Promise<TaskOperationResult> {
    return this.toggleTaskCompletion(userId, taskId, true)
  }

  /**
   * Método de conveniência para reabrir tarefa
   */
  async reopenTask(userId: string, taskId: string): Promise<TaskOperationResult> {
    return this.toggleTaskCompletion(userId, taskId, false)
  }

  /**
   * Obtém ou cria uma coluna para a tarefa baseado no título/quadro especificado
   * @param userId ID do usuário
   * @param taskTitle Título da tarefa
   * @param boardTitle Título do quadro (opcional)
   * @returns ID da coluna
   */
  private async getOrCreateColumnForTask(
    userId: string, 
    taskTitle: string, 
    boardTitle?: string
  ): Promise<string> {
    try {
      // Se foi especificado um quadro, buscar por ele
      if (boardTitle) {
        const existingBoard = await prisma.boards.findFirst({
          where: { 
            userId, 
            title: { 
              contains: boardTitle, 
              mode: 'insensitive' 
            } 
          },
          include: { columns: { orderBy: { order: 'asc' } } }
        })

        if (existingBoard && existingBoard.columns.length > 0) {
          console.log(`📋 [TaskManager] Usando quadro existente: "${existingBoard.title}"`)
          return existingBoard.columns[0].id
        }
      }

      // Se não especificou quadro ou não encontrou, usar lógica baseada no título da tarefa
      let inferredBoardTitle = boardTitle
      
      if (!inferredBoardTitle) {
        // Inferir nome do quadro baseado no título da tarefa
        // Ex: "Academia às 14h" -> "Academia"
        const words = taskTitle.split(' ')
        inferredBoardTitle = words[0]
        
        // Se for muito genérico, usar "Minha Agenda"
        const genericWords = ['tarefa', 'fazer', 'lembrar', 'task']
        if (genericWords.includes(inferredBoardTitle.toLowerCase()) || inferredBoardTitle.length < 3) {
          inferredBoardTitle = 'Minha Agenda'
        }
      }

      // Tentar encontrar quadro existente com nome similar
      const similarBoard = await prisma.boards.findFirst({
        where: { 
          userId, 
          title: { 
            contains: inferredBoardTitle, 
            mode: 'insensitive' 
          } 
        },
        include: { columns: { orderBy: { order: 'asc' } } }
      })

      if (similarBoard && similarBoard.columns.length > 0) {
        console.log(`📋 [TaskManager] Usando quadro similar existente: "${similarBoard.title}"`)
        return similarBoard.columns[0].id
      }

      // Criar novo quadro e coluna
      console.log(`📋 [TaskManager] Criando novo quadro: "${inferredBoardTitle}"`)
      
      const newBoard = await prisma.boards.create({
        data: {
          id: crypto.randomUUID(),
          title: inferredBoardTitle,
          userId,
          createdAt: new Date(),
          updatedAt: new Date()
        }
      })

      const newColumn = await prisma.columns.create({
        data: {
          id: crypto.randomUUID(),
          title: 'A fazer',
          order: 0,
          boardId: newBoard.id,
          createdAt: new Date(),
          updatedAt: new Date()
        }
      })

      console.log(`📋 [TaskManager] Novo quadro e coluna criados - Quadro: "${newBoard.title}", Coluna: "${newColumn.title}"`)
      
      return newColumn.id

    } catch (error) {
      console.error(`❌ [TaskManager] Erro ao obter/criar coluna:`, error)
      
      // Fallback: usar coluna padrão
      console.log(`📋 [TaskManager] Usando coluna padrão como fallback`)
      return await this.taskService.getDefaultColumn(userId)
    }
  }

  /**
   * Busca tarefas por texto
   * @param userId ID do usuário
   * @param query Texto de busca
   * @param limit Limite de resultados
   * @returns Lista de tarefas encontradas
   */
  async searchTasks(userId: string, query: string, limit: number = 10): Promise<TaskOperationResult> {
    try {
      console.log(`🔍 [TaskManager] Buscando tarefas para usuário: ${userId}, query: "${query}"`)
      
      const tasks = await this.taskService.searchTasks(userId, query, limit)
      
      console.log(`✅ [TaskManager] Busca concluída - ${tasks.length} tarefas encontradas`)

      return {
        success: true,
        message: `Encontradas ${tasks.length} tarefas`,
        data: tasks
      }

    } catch (error) {
      console.error(`❌ [TaskManager] Erro ao buscar tarefas:`, error)
      
      return {
        success: false,
        message: 'Erro interno ao buscar tarefas',
        error: 'INTERNAL_ERROR'
      }
    }
  }
}

// Instância singleton para uso na aplicação
export const taskManager = new TaskManager()
