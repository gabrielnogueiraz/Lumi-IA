import { groq, GROQ_MODEL } from '../config/groq'
import { z } from 'zod'

/**
 * 🧠 PARSER DE INTENÇÃO VIA LLM 
 * 
 * Sistema inteligente que utiliza o LLaMA 3 70B para detectar intenções do usuário
 * de forma contextual e semântica, substituindo o sistema de vocabulário fixo.
 * 
 * O modelo é instruído via few-shot prompting para retornar JSON estruturado
 * contendo a intenção detectada e os dados extraídos da tarefa.
 */

// Schema Zod para validação da resposta do modelo
export const ParsedIntentSchema = z.object({
  intent: z.enum(['create_task', 'update_task', 'delete_task', 'complete_task', 'list_tasks', 'search_tasks', 'create_board', 'none']),
  title: z.string().optional(),
  description: z.string().optional(),
  priority: z.enum(['HIGH', 'MEDIUM', 'LOW']).optional(),
  startAt: z.string().optional(), // ISO string que será convertida para Date
  endAt: z.string().optional(), // ISO string que será convertida para Date
  pomodoroGoal: z.number().int().min(1).max(20).optional(),
  boardAction: z.enum(['use_existing', 'create_new', 'suggest_best']).optional(), // Ação relacionada ao quadro
  boardName: z.string().optional(), // Nome do quadro específico ou sugerido
  boardCategory: z.string().optional(), // Categoria/contexto da tarefa para decisão de quadro
  taskReference: z.string().optional(), // Para update/delete/complete - referência à tarefa existente
  tags: z.array(z.string()).optional(),
  confidence: z.number().min(0).max(1).optional().default(0.8)
})

export type ParsedIntent = z.infer<typeof ParsedIntentSchema>

/**
 * Função principal que analisa a intenção do usuário usando o modelo LLaMA 3 70B
 * 
 * @param input - Texto enviado pelo usuário
 * @param userId - ID do usuário para contexto futuro
 * @param userBoards - Lista dos quadros existentes do usuário (opcional)
 * @returns ParsedIntent - Objeto tipado com a intenção e dados extraídos
 */
export async function parseUserIntentFromLumi(
  input: string, 
  userId: string, 
  userBoards?: Array<{ id: string; title: string }>
): Promise<ParsedIntent> {
  try {
    const prompt = buildIntentAnalysisPrompt(input, userBoards)
    
    // Chama o modelo LLaMA 3 70B via Groq
    const completion = await groq.chat.completions.create({
      messages: [{ role: "user", content: prompt }],
      model: GROQ_MODEL,
      temperature: 0.1, // Baixa temperatura para respostas mais consistentes
      max_tokens: 500,
      response_format: { type: "json_object" } // Força retorno em JSON
    })

    const responseContent = completion.choices[0]?.message?.content
    if (!responseContent) {
      throw new Error('Resposta vazia do modelo')
    }

    // Parse e validação da resposta JSON
    const jsonResponse = JSON.parse(responseContent)
    
    // Valida usando Zod
    const validatedResponse = ParsedIntentSchema.parse(jsonResponse)
    
    // Processa datas se existirem
    const processedResponse = processDateFields(validatedResponse)
    
    return processedResponse
    
  } catch (error) {
    console.error('Erro no parseUserIntentFromLumi:', error)
    
    // Fallback gracioso - retorna intenção "none" em caso de erro
    return {
      intent: 'none',
      confidence: 0.0
    }
  }
}

/**
 * Constrói o prompt few-shot para instruir o modelo sobre como analisar intenções
 * incluindo lógica inteligente para gerenciamento de quadros Kanban
 * 
 * O prompt usa exemplos específicos para ensinar o modelo a:
 * - Identificar diferentes tipos de intenção (criar, editar, deletar, etc.)
 * - Extrair informações relevantes (título, prioridade, datas, etc.)
 * - Tomar decisões inteligentes sobre quadros baseado no contexto
 * - Lidar com linguagem natural brasileira e suas variações
 * - Retornar sempre JSON estruturado válido
 */
function buildIntentAnalysisPrompt(input: string, userBoards?: Array<{ id: string; title: string }>): string {
  let boardsContext = '';
  
  if (userBoards && userBoards.length > 0) {
    boardsContext = `\nQUADROS EXISTENTES DO USUÁRIO:
${userBoards.map(board => `- ${board.title} (ID: ${board.id})`).join('\n')}

LÓGICA DE QUADROS:
- Se a tarefa se relaciona com algum quadro existente, use boardAction: "use_existing" e boardName: "nome do quadro"
- Se o usuário pede especificamente um novo quadro, use boardAction: "create_new" e boardName: "nome sugerido"
- Se não há quadro específico mas a tarefa tem contexto claro, use boardAction: "suggest_best" e boardCategory: "categoria"
- Para tarefas genéricas sem contexto claro, use boardAction: "suggest_best" e boardCategory: "geral"
`;
  } else {
    boardsContext = `\nNENHUM QUADRO EXISTENTE - usuário novo
LÓGICA DE QUADROS:
- Para qualquer tarefa, use boardAction: "create_new" e sugira um boardName apropriado
- Se a tarefa tem contexto específico (trabalho, estudos, etc), use esse contexto como nome do quadro
- Para tarefas genéricas, sugira "Minha Agenda" como boardName
`;
  }

  return `Você é um especialista em análise de intenção para um sistema de gerenciamento de tarefas brasileiro com quadros Kanban.

Analise a mensagem do usuário e retorne APENAS um JSON válido com a intenção detectada e dados extraídos.

${boardsContext}

TIPOS DE INTENÇÃO:
- create_task: Criar nova tarefa
- update_task: Editar tarefa existente  
- delete_task: Remover tarefa
- complete_task: Marcar tarefa como concluída
- list_tasks: Listar tarefas
- search_tasks: Buscar tarefas específicas
- create_board: Criar novo quadro específico
- none: Não é relacionado a tarefas

EXEMPLOS COM QUADROS:

Quadros existentes: Trabalho, Faculdade, Academia

Entrada: "Tenho treino de perna hoje às 18h, não me deixe esquecer"
Saída: {"intent": "create_task", "title": "Treino de perna", "startAt": "2025-07-17T18:00:00.000Z", "priority": "MEDIUM", "boardAction": "use_existing", "boardName": "Academia"}

Entrada: "Preciso estudar para a prova de matemática amanhã"
Saída: {"intent": "create_task", "title": "Estudar para prova de matemática", "startAt": "2025-07-18T09:00:00.000Z", "priority": "HIGH", "boardAction": "use_existing", "boardName": "Faculdade"}

Entrada: "Reunião com cliente na sexta às 14h, coloca no quadro de trabalho"
Saída: {"intent": "create_task", "title": "Reunião com cliente", "startAt": "2025-07-18T14:00:00.000Z", "priority": "MEDIUM", "boardAction": "use_existing", "boardName": "Trabalho"}

Entrada: "Criar um quadro novo para organizar meus projetos pessoais"
Saída: {"intent": "create_board", "boardName": "Projetos Pessoais", "boardAction": "create_new"}

Entrada: "Lembrar de comprar leite"
Saída: {"intent": "create_task", "title": "Comprar leite", "priority": "LOW", "boardAction": "suggest_best", "boardCategory": "compras"}

Entrada: "Preciso de um quadro específico para minhas receitas"
Saída: {"intent": "create_board", "boardName": "Receitas", "boardAction": "create_new"}

EXEMPLOS SEM QUADROS EXISTENTES:

Entrada: "Ir ao médico na segunda às 15h"
Saída: {"intent": "create_task", "title": "Consulta médica", "startAt": "2025-07-21T15:00:00.000Z", "priority": "MEDIUM", "boardAction": "create_new", "boardName": "Saúde"}

Entrada: "Estudar inglês hoje à noite"
Saída: {"intent": "create_task", "title": "Estudar inglês", "startAt": "2025-07-17T20:00:00.000Z", "priority": "MEDIUM", "boardAction": "create_new", "boardName": "Estudos"}

REGRAS PARA QUADROS:
1. SEMPRE inclua boardAction quando intent for "create_task"
2. use_existing: quando há quadro compatível óbvio
3. create_new: quando usuário pede especificamente OU quando não há quadro compatível
4. suggest_best: quando não é óbvio mas há contexto para decidir
5. Para boardName, use o nome exato do quadro existente OU sugira nome intuitivo
6. boardCategory ajuda a decisão quando boardAction é "suggest_best"

REGRAS GERAIS:
1. SEMPRE retorne JSON válido
2. Use ISO 8601 para datas (exemplo: "2025-07-17T14:00:00.000Z")
3. priority: HIGH (urgente/importante), MEDIUM (padrão), LOW (pode esperar)
4. Se não souber a data/hora, não inclua startAt/endAt
5. title deve ser conciso e descritivo
6. taskReference para identificar tarefas existentes
7. confidence entre 0 e 1 (padrão: 0.8)

AGORA ANALISE:
"${input}"`
}

/**
 * Processa campos de data convertendo strings ISO para objetos Date
 * e validando se as datas fazem sentido
 */
function processDateFields(response: ParsedIntent): ParsedIntent {
  const processed = { ...response }
  
  // Processa startAt
  if (response.startAt) {
    try {
      const startDate = new Date(response.startAt)
      if (isNaN(startDate.getTime())) {
        console.warn('Data de início inválida, removendo:', response.startAt)
        delete processed.startAt
      }
    } catch (error) {
      console.warn('Erro ao processar startAt:', error)
      delete processed.startAt
    }
  }
  
  // Processa endAt
  if (response.endAt) {
    try {
      const endDate = new Date(response.endAt)
      if (isNaN(endDate.getTime())) {
        console.warn('Data de fim inválida, removendo:', response.endAt)
        delete processed.endAt
      }
    } catch (error) {
      console.warn('Erro ao processar endAt:', error)
      delete processed.endAt
    }
  }
  
  // Valida que endAt seja posterior a startAt
  if (processed.startAt && processed.endAt) {
    const start = new Date(processed.startAt)
    const end = new Date(processed.endAt)
    
    if (end <= start) {
      console.warn('Data de fim deve ser posterior à data de início, removendo endAt')
      delete processed.endAt
    }
  }
  
  return processed
}

/**
 * Função para tomar decisão inteligente sobre qual quadro usar
 * baseado na intenção analisada e quadros existentes do usuário
 */
export function decideBoardForTask(
  intent: ParsedIntent,
  userBoards: Array<{ id: string; title: string }>
): {
  action: 'use_existing' | 'create_new' | 'use_default'
  boardId?: string
  boardName: string
  reason: string
} {
  // Se o modelo já definiu uma ação específica
  if (intent.boardAction === 'use_existing' && intent.boardName) {
    const targetBoard = userBoards.find(board => 
      board.title.toLowerCase() === intent.boardName!.toLowerCase()
    )
    
    if (targetBoard) {
      return {
        action: 'use_existing',
        boardId: targetBoard.id,
        boardName: targetBoard.title,
        reason: `Quadro "${targetBoard.title}" corresponde ao contexto da tarefa`
      }
    }
  }
  
  if (intent.boardAction === 'create_new' && intent.boardName) {
    return {
      action: 'create_new',
      boardName: intent.boardName,
      reason: `Criando novo quadro "${intent.boardName}" conforme solicitado`
    }
  }
  
  // Decisão inteligente baseada no contexto da tarefa
  if (intent.boardAction === 'suggest_best' || !intent.boardAction) {
    const taskContext = (intent.title + ' ' + (intent.description || '')).toLowerCase()
    
    // Mapeamento inteligente de contextos para quadros
    const contextMappings = [
      { keywords: ['academia', 'treino', 'exercício', 'musculação', 'corrida', 'yoga'], boardNames: ['academia', 'treino', 'exercícios', 'fitness'] },
      { keywords: ['trabalho', 'reunião', 'cliente', 'projeto', 'apresentação', 'relatório'], boardNames: ['trabalho', 'profissional', 'emprego', 'job'] },
      { keywords: ['estudo', 'prova', 'faculdade', 'curso', 'aula', 'universidade'], boardNames: ['faculdade', 'estudos', 'universidade', 'curso', 'educação'] },
      { keywords: ['médico', 'consulta', 'exame', 'dentista', 'saúde'], boardNames: ['saúde', 'médico', 'consultas'] },
      { keywords: ['compra', 'mercado', 'shopping', 'farmácia'], boardNames: ['compras', 'mercado', 'shopping'] },
      { keywords: ['casa', 'limpeza', 'organizar', 'arrumação'], boardNames: ['casa', 'doméstico', 'lar'] },
      { keywords: ['pessoal', 'família', 'amigos', 'relacionamento'], boardNames: ['pessoal', 'família', 'social'] }
    ]
    
    // Procura por quadro existente que corresponda ao contexto
    for (const mapping of contextMappings) {
      const hasKeyword = mapping.keywords.some(keyword => taskContext.includes(keyword))
      if (hasKeyword) {
        const matchingBoard = userBoards.find(board => 
          mapping.boardNames.some(name => board.title.toLowerCase().includes(name))
        )
        
        if (matchingBoard) {
          return {
            action: 'use_existing',
            boardId: matchingBoard.id,
            boardName: matchingBoard.title,
            reason: `Tarefa relacionada a ${mapping.keywords.find(k => taskContext.includes(k))} - usando quadro "${matchingBoard.title}"`
          }
        }
      }
    }
    
    // Se não encontrou quadro específico, procura por quadro genérico
    const genericBoards = userBoards.filter(board => 
      ['agenda', 'geral', 'minha agenda', 'tarefas', 'principal'].some(generic => 
        board.title.toLowerCase().includes(generic)
      )
    )
    
    if (genericBoards.length > 0) {
      return {
        action: 'use_existing',
        boardId: genericBoards[0].id,
        boardName: genericBoards[0].title,
        reason: `Usando quadro genérico "${genericBoards[0].title}" para tarefa sem contexto específico`
      }
    }
    
    // Se não tem quadro genérico, sugere criar um baseado no contexto
    if (intent.boardCategory) {
      const categoryToBoardName = {
        'trabalho': 'Trabalho',
        'estudos': 'Estudos',
        'academia': 'Academia',
        'saúde': 'Saúde',
        'compras': 'Compras',
        'casa': 'Casa',
        'pessoal': 'Pessoal',
        'geral': 'Minha Agenda'
      }
      
      const suggestedName = categoryToBoardName[intent.boardCategory as keyof typeof categoryToBoardName] || 'Minha Agenda'
      
      return {
        action: 'create_new',
        boardName: suggestedName,
        reason: `Criando quadro "${suggestedName}" para organizar tarefas de ${intent.boardCategory}`
      }
    }
  }
  
  // Fallback: usar primeiro quadro disponível ou criar "Minha Agenda"
  if (userBoards.length > 0) {
    return {
      action: 'use_existing',
      boardId: userBoards[0].id,
      boardName: userBoards[0].title,
      reason: `Usando primeiro quadro disponível "${userBoards[0].title}"`
    }
  }
  
  return {
    action: 'create_new',
    boardName: 'Minha Agenda',
    reason: 'Criando quadro padrão "Minha Agenda" para organizar tarefas'
  }
}

/**
 * Função auxiliar para detectar se uma mensagem tem potencial de ser relacionada a tarefas
 * Útil para filtros rápidos antes de chamar o LLM
 */
export function hasTaskPotential(input: string): boolean {
  const taskIndicators = [
    // Palavras de ação
    'fazer', 'criar', 'adicionar', 'marcar', 'agendar', 'lembrar', 'preciso', 'tenho que', 'vou',
    // Palavras temporais
    'hoje', 'amanhã', 'semana', 'mês', 'hora', 'às', 'de manhã', 'tarde', 'noite',
    // Contextos de tarefas
    'reunião', 'meeting', 'trabalho', 'academia', 'médico', 'compromisso', 'tarefa',
    // Ações em tarefas
    'completei', 'terminei', 'finalizei', 'acabei', 'fiz', 'remover', 'deletar', 'cancelar',
    // Consultas
    'lista', 'mostrar', 'ver', 'quais', 'que tenho', 'agenda'
  ]
  
  const lowerInput = input.toLowerCase()
  return taskIndicators.some(indicator => lowerInput.includes(indicator))
}

/**
 * Função para teste e debugging - analisa uma mensagem e retorna informações detalhadas
 */
export async function debugIntentAnalysis(
  input: string, 
  userId: string = 'debug-user',
  userBoards?: Array<{ id: string; title: string }>
): Promise<{
  input: string
  hasPotential: boolean
  intent: ParsedIntent
  rawResponse?: string
  boardsUsed?: Array<{ id: string; title: string }>
}> {
  const hasPotential = hasTaskPotential(input)
  
  let rawResponse: string | undefined
  
  try {
    const prompt = buildIntentAnalysisPrompt(input, userBoards)
    
    const completion = await groq.chat.completions.create({
      messages: [{ role: "user", content: prompt }],
      model: GROQ_MODEL,
      temperature: 0.1,
      max_tokens: 500,
      response_format: { type: "json_object" }
    })
    
    rawResponse = completion.choices[0]?.message?.content || ''
  } catch (error) {
    console.error('Erro na análise de debug:', error)
  }
  
  const intent = await parseUserIntentFromLumi(input, userId, userBoards)
  
  return {
    input,
    hasPotential,
    intent,
    rawResponse,
    boardsUsed: userBoards
  }
}
