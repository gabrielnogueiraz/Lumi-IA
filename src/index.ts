import { config } from 'dotenv'
import { buildServer } from './server'

// Carrega variáveis de ambiente
config()

const PORT = parseInt(process.env.PORT || '3001', 10)
const HOST = process.env.HOST || '0.0.0.0'

async function start() {
  try {
    console.log('🚀 Iniciando servidor Lumi...')
    
    // Valida variáveis de ambiente obrigatórias
    if (!process.env.DATABASE_URL) {
      throw new Error('DATABASE_URL é obrigatório')
    }
    
    if (!process.env.GROQ_API_KEY) {
      throw new Error('GROQ_API_KEY é obrigatório')
    }

    if (!process.env.JWT_SECRET) {
      console.warn('⚠️  JWT_SECRET não configurado! Definindo chave padrão insegura.')
      process.env.JWT_SECRET = 'default-insecure-key-change-in-production'
    }

    // Constrói e inicia o servidor
    const server = await buildServer()
    
    await server.listen({ port: PORT, host: HOST })
    
    console.log(`✅ Servidor Lumi rodando em http://${HOST}:${PORT}`)
    console.log(`📊 Health check: http://${HOST}:${PORT}/health`)
    console.log(`🔌 WebSocket: ws://${HOST}:${PORT}/ws`)
    
  } catch (error) {
    console.error('❌ Erro ao iniciar servidor:', error)
    process.exit(1)
  }
}

start()
