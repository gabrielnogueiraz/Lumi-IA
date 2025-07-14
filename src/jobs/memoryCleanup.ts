import { MemoryService } from '../modules/memory/memoryService'
import { DateTime } from 'luxon'

export class MemoryCleanupJob {
  private memoryService: MemoryService
  private intervalId: NodeJS.Timeout | null = null

  constructor() {
    this.memoryService = new MemoryService()
  }

  start(): void {
    // Executa limpeza a cada 6 horas
    this.intervalId = setInterval(async () => {
      await this.cleanup()
    }, 6 * 60 * 60 * 1000)

    console.log('Memory cleanup job iniciado - execução a cada 6 horas')
  }

  stop(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId)
      this.intervalId = null
      console.log('Memory cleanup job parado')
    }
  }

  async cleanup(): Promise<void> {
    try {
      console.log(`[${new Date().toISOString()}] Iniciando limpeza de memórias...`)
      
      const deletedCount = await this.memoryService.deleteExpired()
      
      console.log(`[${new Date().toISOString()}] Limpeza concluída: ${deletedCount} memórias removidas`)
    } catch (error) {
      console.error('Erro na limpeza de memórias:', error)
    }
  }

  // Executa limpeza manual
  async runNow(): Promise<number> {
    return await this.memoryService.deleteExpired()
  }
}

export const memoryCleanupJob = new MemoryCleanupJob()
