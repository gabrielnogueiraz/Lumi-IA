import { taskManager } from './taskManager'

/**
 * Exemplos de uso do TaskManager
 * Este arquivo demonstra como usar a funcionalidade de gerenciamento de tarefas da Lumi
 */

export class TaskManagerExamples {
  
  /**
   * Exemplo 1: Criar uma tarefa simples
   */
  static async exemploCrearTarefaSimples(userId: string) {
    console.log('📝 Exemplo: Criando tarefa simples...')
    
    const resultado = await taskManager.createTask({
      userId,
      title: 'Reunião com cliente',
      description: 'Apresentar proposta do projeto',
      priority: 'HIGH',
      startAt: new Date('2025-07-18T14:00:00'),
      endAt: new Date('2025-07-18T15:00:00'),
      pomodoroGoal: 2
    })
    
    console.log('Resultado:', resultado)
    return resultado
  }

  /**
   * Exemplo 2: Criar tarefa com quadro específico
   */
  static async exemploCrearTarefaComQuadro(userId: string) {
    console.log('📋 Exemplo: Criando tarefa com quadro específico...')
    
    const resultado = await taskManager.createTask({
      userId,
      title: 'Treino de corrida',
      description: 'Corrida de 5km no parque',
      priority: 'MEDIUM',
      startAt: new Date('2025-07-18T06:00:00'),
      pomodoroGoal: 1,
      boardTitle: 'Exercícios' // Vai criar ou usar quadro "Exercícios"
    })
    
    console.log('Resultado:', resultado)
    return resultado
  }

  /**
   * Exemplo 3: Atualizar uma tarefa
   */
  static async exemploAtualizarTarefa(userId: string, taskId: string) {
    console.log('✏️ Exemplo: Atualizando tarefa...')
    
    const resultado = await taskManager.updateTask({
      userId,
      taskId,
      title: 'Reunião com cliente - REMARCADA',
      priority: 'MEDIUM',
      startAt: new Date('2025-07-19T10:00:00')
    })
    
    console.log('Resultado:', resultado)
    return resultado
  }

  /**
   * Exemplo 4: Marcar tarefa como concluída
   */
  static async exemploCompletarTarefa(userId: string, taskId: string) {
    console.log('✅ Exemplo: Completando tarefa...')
    
    const resultado = await taskManager.completeTask(userId, taskId)
    
    console.log('Resultado:', resultado)
    return resultado
  }

  /**
   * Exemplo 5: Reabrir uma tarefa concluída
   */
  static async exemploReabrirTarefa(userId: string, taskId: string) {
    console.log('🔄 Exemplo: Reabrindo tarefa...')
    
    const resultado = await taskManager.reopenTask(userId, taskId)
    
    console.log('Resultado:', resultado)
    return resultado
  }

  /**
   * Exemplo 6: Excluir uma tarefa
   */
  static async exemploExcluirTarefa(userId: string, taskId: string) {
    console.log('🗑️ Exemplo: Excluindo tarefa...')
    
    const resultado = await taskManager.deleteTask(userId, taskId)
    
    console.log('Resultado:', resultado)
    return resultado
  }

  /**
   * Exemplo 7: Buscar tarefas
   */
  static async exemploBuscarTarefas(userId: string, query: string) {
    console.log('🔍 Exemplo: Buscando tarefas...')
    
    const resultado = await taskManager.searchTasks(userId, query, 5)
    
    console.log('Resultado:', resultado)
    return resultado
  }

  /**
   * Exemplo de uso completo com tratamento de erros
   */
  static async exemploCompletoComTratamentoDeErros(userId: string) {
    try {
      console.log('🚀 Exemplo: Fluxo completo de tarefa...')
      
      // 1. Criar tarefa
      const criacao = await taskManager.createTask({
        userId,
        title: 'Estudar TypeScript',
        description: 'Revisar conceitos avançados',
        priority: 'HIGH',
        pomodoroGoal: 3
      })
      
      if (!criacao.success) {
        console.error('Erro ao criar tarefa:', criacao.message)
        return
      }
      
      const tarefaCriada = criacao.data
      console.log('✅ Tarefa criada:', tarefaCriada.title)
      
      // 2. Atualizar tarefa
      const atualizacao = await taskManager.updateTask({
        userId,
        taskId: tarefaCriada.id,
        description: 'Revisar conceitos avançados + fazer exercícios práticos',
        pomodoroGoal: 4
      })
      
      if (atualizacao.success) {
        console.log('✅ Tarefa atualizada')
      }
      
      // 3. Simular conclusão da tarefa
      await new Promise(resolve => setTimeout(resolve, 1000)) // Pausa de 1s
      
      const conclusao = await taskManager.completeTask(userId, tarefaCriada.id)
      
      if (conclusao.success) {
        console.log('✅ Tarefa concluída!')
      }
      
      return {
        tarefa: tarefaCriada,
        fluxoCompleto: true
      }
      
    } catch (error: any) {
      console.error('❌ Erro no fluxo completo:', error)
      return {
        erro: error?.message || 'Erro desconhecido',
        fluxoCompleto: false
      }
    }
  }
}

// Função utilitária para testar todas as funcionalidades
export async function testarTodasFuncionalidades(userId: string) {
  console.log('🧪 Iniciando testes das funcionalidades do TaskManager...\n')
  
  try {
    // Teste 1: Criar tarefa simples
    const tarefa1 = await TaskManagerExamples.exemploCrearTarefaSimples(userId)
    
    // Teste 2: Criar tarefa com quadro
    const tarefa2 = await TaskManagerExamples.exemploCrearTarefaComQuadro(userId)
    
    // Teste 3: Buscar tarefas
    await TaskManagerExamples.exemploBuscarTarefas(userId, 'reunião')
    
    // Teste 4: Fluxo completo
    await TaskManagerExamples.exemploCompletoComTratamentoDeErros(userId)
    
    console.log('\n✅ Todos os testes concluídos!')
    
  } catch (error) {
    console.error('\n❌ Erro durante os testes:', error)
  }
}
