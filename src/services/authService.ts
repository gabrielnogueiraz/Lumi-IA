import jwt from 'jsonwebtoken'
import { prisma } from '../prisma/client'

/**
 * Interface para o payload do JWT
 * Compatível com Toivo (que usa 'id') e Lumi (que usa 'userId')
 */
export interface JWTPayload {
  userId?: string
  id?: string
  email: string
  name: string
  iat?: number
  exp?: number
}

export class AuthService {
  private readonly jwtSecret: string
  private userCache: Map<string, { user: any; timestamp: number }> = new Map()
  private readonly CACHE_TTL = 5 * 60 * 1000 // 5 minutos

  constructor() {
    this.jwtSecret = process.env.JWT_SECRET || 'fallback-secret-key'
    
    if (!process.env.JWT_SECRET) {
      console.warn('⚠️  JWT_SECRET não configurado! Usando chave padrão insegura.')
    }
  }

  /**
   * Limpa cache expirado
   */
  private cleanExpiredCache() {
    const now = Date.now()
    for (const [key, value] of this.userCache.entries()) {
      if (now - value.timestamp > this.CACHE_TTL) {
        this.userCache.delete(key)
      }
    }
  }

  /**
   * Busca usuário no cache ou banco
   */
  private async getUserFromCacheOrDB(userId: string) {
    // Limpa cache expirado
    this.cleanExpiredCache()
    
    // Verifica cache
    const cached = this.userCache.get(userId)
    if (cached && (Date.now() - cached.timestamp) < this.CACHE_TTL) {
      console.log('📋 AuthService: Usuário encontrado no cache:', cached.user.name)
      return cached.user
    }

    // Busca no banco
    console.log('🔍 AuthService: Buscando usuário no banco:', userId)
    const user = await prisma.user.findUnique({
      where: { id: userId },
      select: { 
        id: true, 
        name: true, 
        email: true,
        createdAt: true,
        updatedAt: true
      }
    })

    if (user) {
      // Adiciona ao cache
      this.userCache.set(userId, {
        user: {
          userId: user.id,
          email: user.email,
          name: user.name
        },
        timestamp: Date.now()
      })
      console.log('✅ AuthService: Usuário encontrado:', user.name)
      return {
        userId: user.id,
        email: user.email,
        name: user.name
      }
    }

    return null
  }

  /**
   * Verifica e decodifica um token JWT
   * 
   * Compatível tanto com tokens gerados pelo Toivo (que usa 'id') 
   * quanto tokens gerados pelo Lumi (que usa 'userId')
   */
  async verifyToken(token: string): Promise<JWTPayload | null> {
    try {
      console.log('🔍 AuthService: Iniciando verificação do token')
      console.log('🔍 Token recebido (primeiros 50 chars):', token.substring(0, 50) + '...')
      
      // Força uso do algoritmo HS256 para compatibilidade com Toivo
      const decoded = jwt.verify(token, this.jwtSecret, { 
        algorithms: ['HS256'] 
      }) as JWTPayload
      console.log('✅ AuthService: Token decodificado com sucesso')
      console.log('🔍 Payload decodificado:', JSON.stringify(decoded, null, 2))
      
      // Determina o ID do usuário, aceitando tanto userId quanto id
      const userId = decoded.userId || decoded.id
      console.log('🔍 AuthService: userId extraído:', userId)
      
      if (!userId) {
        console.warn('❌ AuthService: Token JWT não contém campo userId nem id')
        return null
      }
      
      // Verifica se o usuário ainda existe no banco
      const user = await this.getUserFromCacheOrDB(userId)

      if (!user) {
        console.warn(`❌ AuthService: Token válido mas usuário ${userId} não encontrado`)
        return null
      }

      return {
        userId: user.userId,
        email: user.email,
        name: user.name
      }
    } catch (error) {
      console.log('❌ AuthService: Erro ao verificar token')
      if (error instanceof jwt.TokenExpiredError) {
        console.warn('❌ AuthService: Token JWT expirado')
        console.warn('   Expirou em:', new Date(error.expiredAt).toISOString())
      } else if (error instanceof jwt.JsonWebTokenError) {
        console.warn('❌ AuthService: Token JWT inválido:', error.message)
        console.warn('   Tipo de erro:', error.name)
      } else {
        console.error('❌ AuthService: Erro inesperado ao verificar token JWT:', error)
      }
      return null
    }
  }

  /**
   * Verifica se o token está próximo do vencimento
   */
  isTokenExpiringSoon(token: string, thresholdMinutes: number = 30): boolean {
    try {
      const decoded = jwt.decode(token) as JWTPayload
      
      if (!decoded.exp) return false
      
      const now = Math.floor(Date.now() / 1000)
      const timeUntilExpiry = decoded.exp - now
      const thresholdSeconds = thresholdMinutes * 60
      
      return timeUntilExpiry < thresholdSeconds
    } catch {
      return true // Se não conseguir decodificar, assume que está expirando
    }
  }

  /**
   * Extrai informações do token sem verificar (útil para logs)
   */
  decodeToken(token: string): JWTPayload | null {
    try {
      return jwt.decode(token) as JWTPayload
    } catch {
      return null
    }
  }

  /**
   * Atualiza o lastCheckIn do usuário (para analytics)
   */
  async updateLastCheckIn(userId: string): Promise<void> {
    try {
      await prisma.user.update({
        where: { id: userId },
        data: { lastCheckIn: new Date() }
      })
    } catch (error) {
      console.warn('Erro ao atualizar lastCheckIn:', error)
    }
  }

  /**
   * Busca usuário completo por ID (com cache)
   */
  async getUserById(userId: string): Promise<{
    id: string
    name: string
    email: string
    theme: string
    profileImage?: string
    createdAt: Date
    lastCheckIn?: Date
  } | null> {
    try {
      const user = await this.getUserFromCacheOrDB(userId)

      if (!user) return null

      return {
        id: user.id,
        name: user.name,
        email: user.email,
        theme: user.theme,
        profileImage: user.profileImage || undefined,
        createdAt: user.createdAt,
        lastCheckIn: user.lastCheckIn || undefined
      }
    } catch (error) {
      console.error('Erro ao buscar usuário por ID:', error)
      return null
    }
  }

  /**
   * Busca usuário completo por Email
   */
  async getUserByEmail(email: string): Promise<{
    id: string
    name: string
    email: string
    theme: string
    profileImage?: string | null
    createdAt: Date
    lastCheckIn?: Date | null
  } | null> {
    try {
      return await prisma.user.findUnique({
        where: { email },
        select: {
          id: true,
          name: true,
          email: true,
          theme: true,
          profileImage: true,
          createdAt: true,
          lastCheckIn: true
        }
      })
    } catch (error) {
      console.error('Erro ao buscar usuário por email:', error)
      return null
    }
  }
}

// Instância singleton
export const authService = new AuthService()
