# 🤖 Lumi IA - Backend

Lumi é uma inteligência artificial avançada integrada ao sistema Toivo, projetada para aumentar a produtividade dos usuários através de empatia, adaptabilidade e inteligência emocional.

## ✨ Características Principais

- **🧠 IA Contextual**: Entende o contexto do usuário e mantém memória das interações
- **💝 Análise Emocional**: Identifica emoções e adapta a comunicação adequadamente
- **🧩 Memória Inteligente**: Armazena informações importantes e padrões de produtividade
- **⚡ Streaming**: Respostas em tempo real com streaming de conteúdo
- **🔌 WebSocket**: Comunicação bidirecional em tempo real
- **🛡️ Rate Limiting**: Proteção contra abuso da API
- **🔒 Segurança**: Headers de segurança e validação rigorosa de dados

## 🛠️ Stack Tecnológica

- **Backend**: [Fastify](https://fastify.dev/) - Servidor web ultra rápido
- **Banco**: [PostgreSQL](https://www.postgresql.org/) com [Prisma ORM](https://prisma.io/)
- **IA**: [Groq SDK](https://groq.com/) com modelo Llama3-70B
- **Validação**: [Zod](https://zod.dev/) para tipagem e validação
- **WebSocket**: Comunicação em tempo real
- **TypeScript**: Tipagem estática para maior confiabilidade

## � Início Rápido

### Pré-requisitos
- Node.js 18+ 
- PostgreSQL 
- Conta no [Groq](https://console.groq.com/) para API key

### Instalação

```bash
# Clone o repositório
git clone <repo-url>
cd lumi-ia

# Instale as dependências
npm install

# Configure o banco de dados
npx prisma db push
npx prisma generate

# Configure as variáveis de ambiente
cp .env.example .env
# Edite .env com suas configurações
```

### Configuração das Variáveis de Ambiente

```env
# Banco de dados
DATABASE_URL="postgresql://usuario:senha@localhost:5432/lumi_db"

# API do Groq (obtenha em https://console.groq.com/)
GROQ_API_KEY="sua-groq-api-key-aqui"

# Servidor
NODE_ENV="production"
PORT=3001
HOST="0.0.0.0"
```

### Executando

```bash
# Desenvolvimento (com hot reload)
npm run dev

# Produção
npm run build
npm start
```

## 📡 Endpoints da API

### 🏥 Health Check
```http
GET /health
```
Retorna o status do servidor e conectividade com o banco.

### 🤖 Assistente Lumi
```http
POST /api/ask
Content-Type: application/json
Authorization: Bearer {userId}
```

**Exemplo de request:**
```json
{
  "message": "Olá Lumi, como você pode me ajudar hoje?",
  "userId": "uuid-do-usuario",
  "context": {
    "mood": "motivated",
    "timeOfDay": "morning"
  }
}
```

**Resposta em Streaming:** A resposta é enviada em chunks para experiência em tempo real.

### 🧠 Memórias da Lumi
```http
GET    /api/memories              # Lista memórias do usuário
POST   /api/memories              # Cria nova memória
PUT    /api/memories/:id          # Atualiza memória
DELETE /api/memories/:id          # Remove memória
GET    /api/memories/recent       # Memórias recentes
GET    /api/memories/productivity-insights  # Insights de produtividade
```

## 🔌 Integração WebSocket

Conecte-se via WebSocket para comunicação em tempo real:

```javascript
const ws = new WebSocket('ws://localhost:3001/ws');

ws.onopen = () => {
  console.log('✅ Conectado à Lumi');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('💬 Mensagem da Lumi:', data);
};

// Enviar mensagem
ws.send(JSON.stringify({
  type: 'message',
  content: 'Olá Lumi!',
  userId: 'seu-user-id'
}));
```

## 🧠 Arquitetura e Funcionamento

### 1. 💝 Análise Emocional
A Lumi analisa o texto do usuário para detectar:
- **Estado emocional**: feliz, triste, ansioso, motivado, estressado
- **Nível de confiança**: precisão da análise emocional
- **Estratégia de resposta**: adaptação da comunicação baseada na emoção

### 2. 🧩 Contextualização Inteligente
Coleta e processa informações sobre:
- **Tarefas**: pendentes, concluídas e em progresso
- **Padrões**: horários produtivos, preferências de trabalho
- **Histórico**: interações passadas e aprendizados
- **Preferências**: estilo de comunicação personalizado

### 3. ⚡ Geração de Respostas
- **Prompt personalizado**: constrói contexto único para cada usuário
- **IA Groq/Llama3**: processamento com modelo de última geração
- **Streaming**: resposta em tempo real, chunk por chunk
- **Memória persistente**: salva insights importantes para o futuro

### 4. 📈 Aprendizado Contínuo
- **Padrões comportamentais**: identifica rotinas e preferências
- **Evolução comunicativa**: adapta linguagem ao longo do tempo
- **Insights preditivos**: sugere melhorias baseadas em dados históricos

## �️ Esquema de Dados

### 📝 Modelo LumiMemory
```typescript
interface LumiMemory {
  id: string;                    // UUID único
  userId: string;                // ID do usuário
  type: MemoryType;             // Tipo da memória
  content: string;              // Conteúdo da memória
  importance: ImportanceLevel;   // Nível de importância
  emotionalContext?: string;     // Contexto emocional
  productivityPattern?: string;  // Padrão de produtividade
  communicationStyle?: string;   // Estilo de comunicação
  tags: string[];               // Tags para categorização
  createdAt: Date;              // Data de criação
  updatedAt: Date;              // Última atualização
  expiresAt?: Date;             // Data de expiração (opcional)
}
```

### 🏷️ Tipos de Memória Suportados
| Tipo | Descrição | Exemplo |
|------|-----------|---------|
| `PERSONAL_INFO` | Informações pessoais | Nome, preferências pessoais |
| `PERSONAL_CONTEXT` | Contexto pessoal | Família, hobbies, estilo de vida |
| `WORK_CONTEXT` | Contexto profissional | Cargo, empresa, projetos |
| `STUDY_CONTEXT` | Contexto acadêmico | Cursos, objetivos de estudo |
| `PRODUCTIVITY_PATTERN` | Padrões de produtividade | Horários produtivos, métodos |
| `EMOTIONAL_STATE` | Estados emocionais | Humor, motivação, stress |
| `COMMUNICATION_STYLE` | Estilo de comunicação | Tom preferido, formalidade |
| `GOALS_PROJECTS` | Objetivos e projetos | Metas, deadlines, prioridades |
| `PREFERENCES` | Preferências gerais | Configurações, escolhas |
| `IMPORTANT_DATES` | Datas importantes | Prazos, eventos, lembretes |
| `FEEDBACK` | Feedback e avaliações | Retorno sobre interações |

### 📊 Níveis de Importância
- `LOW` - Informação básica
- `MEDIUM` - Informação relevante 
- `HIGH` - Informação muito importante
- `CRITICAL` - Informação essencial

## 🔒 Segurança e Performance

### 🛡️ Medidas de Segurança
- **Rate Limiting**: Proteção contra spam e abuso de API
- **Validação rigorosa**: Todos os inputs são validados com Zod
- **Headers de segurança**: Implementação com Fastify Helmet
- **Autenticação**: Token-based authentication por usuário
- **Sanitização**: Limpeza de dados de entrada

### ⚡ Otimizações de Performance
- **Cache inteligente**: Cache de respostas frequentes
- **Conexão otimizada**: Pool de conexões do banco de dados
- **Streaming**: Respostas em tempo real sem bloqueio
- **Jobs assíncronos**: Limpeza automática de dados antigos
- **Indexação**: Índices otimizados no banco de dados

## 🚀 Deploy em Produção

### 🐳 Docker (Recomendado)

**Dockerfile:**
```dockerfile
FROM node:18-alpine
WORKDIR /app

# Instalar dependências
COPY package*.json ./
RUN npm ci --only=production

# Copiar código e build
COPY . .
RUN npm run build

# Configurar usuário não-root
RUN addgroup -g 1001 -S nodejs
RUN adduser -S lumi -u 1001
USER lumi

EXPOSE 3001
CMD ["npm", "start"]
```

**docker-compose.yml:**
```yaml
version: '3.8'
services:
  lumi:
    build: .
    ports:
      - "3001:3001"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=${DATABASE_URL}
      - GROQ_API_KEY=${GROQ_API_KEY}
    depends_on:
      - postgres
  
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: lumi_db
      POSTGRES_USER: lumi
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 🌐 Variáveis de Produção
```env
NODE_ENV=production
DATABASE_URL="postgresql://usuario:senha@host:5432/lumi_db"
GROQ_API_KEY="gsk_..."
PORT=3001
HOST=0.0.0.0

# Configurações de segurança
RATE_LIMIT_MAX=100
RATE_LIMIT_WINDOW=15
CACHE_TTL=3600
```

## 🔗 Integração com Frontend

### ⚛️ Exemplo React/Next.js

**Hook customizado para Lumi:**
```typescript
import { useState, useCallback } from 'react';

interface LumiResponse {
  message: string;
  confidence: number;
  emotionalAnalysis?: {
    emotion: string;
    confidence: number;
  };
}

export const useLumi = (userId: string) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const askLumi = useCallback(async (
    message: string, 
    context?: Record<string, any>
  ): Promise<LumiResponse> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/ask-json', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${userId}`
        },
        body: JSON.stringify({ message, userId, context })
      });

      if (!response.ok) {
        throw new Error('Falha na comunicação com a Lumi');
      }

      return await response.json();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [userId]);

  const askLumiStream = useCallback(async (
    message: string,
    onChunk: (chunk: string) => void,
    context?: Record<string, any>
  ) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${userId}`
        },
        body: JSON.stringify({ message, userId, context })
      });

      if (!response.ok) {
        throw new Error('Falha na comunicação com a Lumi');
      }

      const reader = response.body?.getReader();
      if (!reader) return;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = new TextDecoder().decode(value);
        onChunk(chunk);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [userId]);

  return { askLumi, askLumiStream, isLoading, error };
};
```

### 🔌 WebSocket no React
```typescript
import { useEffect, useState, useRef } from 'react';

export const useLumiWebSocket = (userId: string) => {
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState<any[]>([]);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    ws.current = new WebSocket(`ws://localhost:3001/ws`);
    
    ws.current.onopen = () => {
      setIsConnected(true);
      console.log('✅ Conectado à Lumi via WebSocket');
    };

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setMessages(prev => [...prev, data]);
    };

    ws.current.onclose = () => {
      setIsConnected(false);
      console.log('❌ Desconectado da Lumi');
    };

    return () => {
      ws.current?.close();
    };
  }, []);

  const sendMessage = useCallback((message: string) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({
        type: 'message',
        content: message,
        userId
      }));
    }
  }, [userId]);

  return { isConnected, messages, sendMessage };
};
```

## 📊 Monitoramento e Observabilidade

### 🏥 Health Check Avançado
```http
GET /health
```

**Resposta exemplo:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "services": {
    "database": "connected",
    "groq": "available",
    "cache": "operational"
  },
  "uptime": 86400,
  "memoryUsage": {
    "used": "45.2 MB",
    "free": "78.8 MB"
  }
}
```

### 📝 Sistema de Logs
- **Requisições**: Todas as chamadas de API são logadas
- **Erros**: Stack traces completos para debugging
- **Performance**: Tempo de resposta e uso de recursos
- **Ações do usuário**: Interações importantes rastreadas

### 📈 Métricas Importantes
- Tempo médio de resposta da IA
- Taxa de acerto da análise emocional
- Número de memórias criadas por usuário
- Performance do banco de dados

## 🔄 Jobs e Automação

### 🧹 Limpeza Automática de Memórias
- **Frequência**: A cada 6 horas
- **Função**: Remove memórias expiradas automaticamente
- **Otimização**: Mantém o banco de dados performático
- **Configurável**: Pode ser ajustado via variáveis de ambiente

### 🔄 Cache Management
- **TTL**: Configurável por tipo de dados
- **Invalidação**: Automática quando dados são atualizados
- **Compressão**: Otimização automática de memória

## �️ Desenvolvimento e Contribuição

### 📋 Scripts Disponíveis
```bash
npm run dev          # Desenvolvimento com hot reload
npm run build        # Build para produção
npm start           # Inicia em modo produção
npm run prisma:generate  # Regenera cliente Prisma
npm run prisma:studio    # Interface visual do banco
npm run prisma:push      # Aplica schema ao banco
```

### 🏗️ Estrutura do Projeto
```
src/
├── config/          # Configurações (cache, groq, rate limiter)
├── jobs/           # Jobs assíncronos (limpeza de memórias)
├── middlewares/    # Middlewares (auth, logger, rate limiter)
├── modules/        # Módulos principais da aplicação
│   ├── assistant/  # Lógica da Lumi IA
│   ├── auth/       # Autenticação
│   ├── memory/     # Sistema de memórias
│   ├── task/       # Integração com tarefas
│   └── user/       # Gerenciamento de usuários
├── prisma/         # Cliente Prisma
├── routes/         # Rotas específicas (debug, etc)
├── services/       # Serviços compartilhados
├── types/          # Tipos TypeScript
└── utils/          # Utilitários (emotion analyzer, helpers)
```

### 🔧 Configuração do Ambiente de Desenvolvimento
1. **Node.js 18+** - Runtime obrigatório
2. **PostgreSQL** - Banco de dados local
3. **VS Code** - Editor recomendado com extensões:
   - TypeScript
   - Prisma
   - ESLint
   - Prettier

## 🎯 Roadmap e Próximos Passos

### 🚀 Versão 1.1 (Próxima)
- [ ] **Sistema de autenticação JWT** robusto
- [ ] **Métricas avançadas** com Prometheus
- [ ] **Cache Redis** para alta performance
- [ ] **Testes automatizados** (unitários e integração)
- [ ] **Documentação OpenAPI** automática

### 🌟 Versão 1.2 (Futuro)
- [ ] **Análise de sentimento** mais avançada
- [ ] **Integração com calendários**
- [ ] **Notificações inteligentes**
- [ ] **API de relatórios** de produtividade
- [ ] **Multi-idiomas** (i18n)

### 🔮 Versão 2.0 (Visão)
- [ ] **Machine Learning** personalizado
- [ ] **Integração com dispositivos IoT**
- [ ] **API de terceiros** (Slack, Teams, etc.)
- [ ] **Mobile SDK** para apps nativas
- [ ] **Análise preditiva** avançada

## 🐛 Troubleshooting

### ❗ Problemas Comuns e Soluções

#### 🔌 Erro de Conexão com Banco de Dados
```bash
Error: Can't reach database server at localhost:5432
```
**Soluções:**
- Verifique se PostgreSQL está em execução: `sudo systemctl status postgresql`
- Confirme as credenciais no `DATABASE_URL`
- Teste a conexão: `psql -h localhost -U usuario -d lumi_db`

#### 🤖 Erro de API do Groq
```bash
Error: Invalid API key or quota exceeded
```
**Soluções:**
- Verifique se `GROQ_API_KEY` está correta no `.env`
- Confirme se há créditos disponíveis em [console.groq.com](https://console.groq.com)
- Teste a key: `curl -H "Authorization: Bearer $GROQ_API_KEY" https://api.groq.com/openai/v1/models`

#### ⚡ Rate Limiting Ativado
```bash
Error: Too Many Requests (429)
```
**Soluções:**
- Aguarde alguns minutos para reset do limite
- Ajuste configurações em `src/config/rateLimiter.ts`
- Para desenvolvimento, aumente os limites temporariamente

#### 🏗️ Erro de Build TypeScript
```bash
Error: Cannot find module or type declarations
```
**Soluções:**
- Execute: `npm run prisma:generate`
- Limpe node_modules: `rm -rf node_modules package-lock.json && npm install`
- Verifique versões: `node --version` (deve ser 18+)

#### 📦 Problema com Prisma
```bash
Error: Prisma schema not found
```
**Soluções:**
- Execute: `npx prisma db push`
- Verifique se `prisma/schema.prisma` existe
- Regenere cliente: `npx prisma generate`

### 🔍 Debug Mode
Para debugging avançado, adicione no `.env`:
```env
NODE_ENV=development
DEBUG=lumi:*
LOG_LEVEL=debug
```

### 📞 Suporte
Para problemas não listados:
1. Verifique os logs em tempo real: `npm run dev`
2. Consulte a documentação do [Groq](https://console.groq.com/docs)
3. Verifique issues conhecidas no repositório

---

## 📄 Licença

MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👥 Créditos

**Desenvolvido com ❤️ pela equipe Lumi**

- 🤖 **IA Powered by**: [Groq](https://groq.com/) + Llama3-70B
- 🚀 **Backend**: [Fastify](https://fastify.dev/)
- 🗄️ **Database**: [PostgreSQL](https://postgresql.org/) + [Prisma](https://prisma.io/)
- 💎 **TypeScript**: Para confiabilidade e produtividade

*Transformando a produtividade através da inteligência emocional artificial.*
