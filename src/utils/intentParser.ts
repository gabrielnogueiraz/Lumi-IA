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
  intent: z.enum(['create_task', 'update_task', 'delete_task', 'complete_task', 'list_tasks', 'search_tasks', 'none']),
  title: z.string().optional(),
  description: z.string().optional(),
  priority: z.enum(['HIGH', 'MEDIUM', 'LOW']).optional(),
  startAt: z.string().optional(), // ISO string que será convertida para Date
  endAt: z.string().optional(), // ISO string que será convertida para Date
  pomodoroGoal: z.number().int().min(1).max(20).optional(),
  board: z.string().optional(),
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
 * @returns ParsedIntent - Objeto tipado com a intenção e dados extraídos
 */
export async function parseUserIntentFromLumi(input: string, userId: string): Promise<ParsedIntent> {
  try {
    const prompt = buildIntentAnalysisPrompt(input)
    
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
 * 
 * O prompt usa exemplos específicos para ensinar o modelo a:
 * - Identificar diferentes tipos de intenção (criar, editar, deletar, etc.)
 * - Extrair informações relevantes (título, prioridade, datas, etc.)
 * - Lidar com linguagem natural brasileira e suas variações
 * - Retornar sempre JSON estruturado válido
 */
function buildIntentAnalysisPrompt(input: string): string {
  return `Você é um especialista em análise de intenção para um sistema de gerenciamento de tarefas brasileiro.

Analise a mensagem do usuário e retorne APENAS um JSON válido com a intenção detectada e dados extraídos.

TIPOS DE INTENÇÃO:
- create_task: Criar nova tarefa
- update_task: Editar tarefa existente  
- delete_task: Remover tarefa
- complete_task: Marcar tarefa como concluída
- list_tasks: Listar tarefas
- search_tasks: Buscar tarefas específicas
- none: Não é relacionado a tarefas

EXEMPLOS:

Entrada: "Preciso ir à academia hoje às 18h"
Saída: {"intent": "create_task", "title": "Ir à academia", "startAt": "2025-07-17T18:00:00.000Z", "priority": "MEDIUM"}

Entrada: "Bota aí uma reunião com o cliente amanhã de manhã, é importante"
Saída: {"intent": "create_task", "title": "Reunião com o cliente", "startAt": "2025-07-18T09:00:00.000Z", "priority": "HIGH"}

Entrada: "Completei a apresentação do projeto"
Saída: {"intent": "complete_task", "taskReference": "apresentação do projeto"}

Entrada: "Remove aquela tarefa de limpeza"
Saída: {"intent": "delete_task", "taskReference": "limpeza"}

Entrada: "Muda a reunião das 14h para as 16h"
Saída: {"intent": "update_task", "taskReference": "reunião", "startAt": "2025-07-17T16:00:00.000Z"}

Entrada: "O que tenho para fazer hoje?"
Saída: {"intent": "list_tasks"}

Entrada: "Cadê aquela tarefa da academia?"
Saída: {"intent": "search_tasks", "taskReference": "academia"}

Entrada: "Como você está hoje?"
Saída: {"intent": "none"}

REGRAS:
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
export async function debugIntentAnalysis(input: string, userId: string = 'debug-user'): Promise<{
  input: string
  hasPotential: boolean
  intent: ParsedIntent
  rawResponse?: string
}> {
  const hasPotential = hasTaskPotential(input)
  
  let rawResponse: string | undefined
  
  try {
    const prompt = buildIntentAnalysisPrompt(input)
    
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
  
  const intent = await parseUserIntentFromLumi(input, userId)
  
  return {
    input,
    hasPotential,
    intent,
    rawResponse
  }
}
