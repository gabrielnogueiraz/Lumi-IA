import { groq, GROQ_MODEL } from "../config/groq";
import { z } from "zod";

/**
 * 🧠 PARSER DE INTENÇÃO VIA LLM - EMOCIONALMENTE INTELIGENTE
 *
 * Sistema inteligente que utiliza o LLaMA 3 70B para detectar intenções do usuário
 * de forma contextual, semântica E emocional. Agora capaz de entender expressões
 * vagas como "não sei por onde começar" ou "não estou no clima".
 *
 * O modelo é instruído via few-shot prompting para retornar JSON estruturado
 * contendo tanto a intenção prática quanto o estado emocional do usuário.
 */

// Schema Zod expandido para validação da resposta do modelo
export const ParsedIntentSchema = z.object({
  intent: z.enum([
    // Intenções de tarefa (existentes)
    "create_task",
    "update_task",
    "delete_task",
    "complete_task",
    "list_tasks",
    "search_tasks",
    "create_board",

    // Novas intenções emocionais e situacionais
    "seek_support",        // "preciso de ajuda", "não sei o que fazer"
    "express_confusion",   // "estou perdido", "não entendo"
    "feeling_overwhelmed", // "é muita coisa", "não dou conta"
    "procrastinating",     // "não estou no clima", "deixa pra depois"
    "seeking_motivation",  // "preciso de ânimo", "me motiva"
    "feeling_stuck",       // "não sai do lugar", "travado"
    "sharing_excitement",  // "que legal!", "estou empolgado"
    "expressing_frustration", // "que saco", "não funciona"
    "checking_in",         // "como está minha agenda?", conversa casual
    "brainstorming",       // "me ajuda com ideias", "o que você acha"
    "planning_assistance", // "como posso organizar", "me ajuda a planejar"
    "none",
  ]),

  // Dados de tarefa (se aplicável)
  title: z.string().optional(),
  description: z.string().optional(),
  priority: z.enum(["HIGH", "MEDIUM", "LOW"]).optional(),
  startAt: z.string().optional(),
  endAt: z.string().optional(),
  pomodoroGoal: z.number().int().min(1).max(20).optional(),
  boardAction: z.enum(["use_existing", "create_new", "suggest_best"]).optional(),
  boardName: z.string().optional(),
  boardCategory: z.string().optional(),
  taskReference: z.string().optional(),
  tags: z.array(z.string()).optional(),

  // Novos campos emocionais
  emotionalState: z.enum([
    "confused", "overwhelmed", "procrastinating", "excited", "frustrated",
    "motivated", "tired", "anxious", "calm", "hopeful", "stuck", "neutral"
  ]).optional(),
  supportNeeded: z.boolean().optional(),
  emotionalIntensity: z.enum(["low", "medium", "high"]).optional(),
  suggestedResponse: z.enum([
    "guide", "reassure", "motivate", "calm", "energize", "empathize",
    "structure", "challenge", "support"
  ]).optional(),

  confidence: z.number().min(0).max(1).optional().default(0.8),
});

export type ParsedIntent = z.infer<typeof ParsedIntentSchema>;

/**
 * Função principal que analisa a intenção do usuário usando o modelo LLaMA 3 70B
 * Agora com capacidade de detectar nuances emocionais e expressões indiretas
 */
export async function parseUserIntentFromLumi(
  input: string,
  userId: string,
  userBoards?: Array<{ id: string; title: string }>
): Promise<ParsedIntent> {
  try {
    const prompt = buildEmotionallyIntelligentPrompt(input, userBoards);

    const completion = await groq.chat.completions.create({
      messages: [{ role: "user", content: prompt }],
      model: GROQ_MODEL,
      temperature: 0.1,
      max_tokens: 700, // Aumentado para acomodar análise emocional
      response_format: { type: "json_object" },
    });

    const responseContent = completion.choices[0]?.message?.content;
    if (!responseContent) {
      throw new Error("Resposta vazia do modelo");
    }

    const jsonResponse = JSON.parse(responseContent);
    const validatedResponse = ParsedIntentSchema.parse(jsonResponse);
    const processedResponse = processDateFields(validatedResponse);

    return processedResponse;
  } catch (error) {
    console.error("Erro no parseUserIntentFromLumi:", error);

    // Fallback gracioso com análise emocional básica
    return {
      intent: "none",
      confidence: 0.0,
      emotionalState: "neutral",
      supportNeeded: false,
      emotionalIntensity: "low",
      suggestedResponse: "support"
    };
  }
}

/**
 * Constrói um prompt emocionalmente inteligente que ensina o modelo a detectar
 * tanto intenções práticas quanto estados emocionais e expressões indiretas
 */
function buildEmotionallyIntelligentPrompt(
  input: string,
  userBoards?: Array<{ id: string; title: string }>
): string {
  // 🔧 CORREÇÃO CRÍTICA: Usar horário brasileiro consistentemente
  const now = new Date();
  
  // Força timezone brasileiro para data e hora
  const brasilTime = new Date(now.toLocaleString("en-US", {timeZone: "America/Sao_Paulo"}));
  const currentDate = brasilTime.toISOString().split("T")[0]; // YYYY-MM-DD em horário brasileiro
  const currentTime = brasilTime.toTimeString().split(" ")[0].substring(0, 5); // HH:MM em horário brasileiro
  const currentDayOfWeek = brasilTime.toLocaleDateString("pt-BR", { weekday: "long", timeZone: "America/Sao_Paulo" });

  console.log('🔍 DEBUG - Hora enviada ao LLM:', currentTime, 'Data:', currentDate);

  let boardsContext = "";
  if (userBoards && userBoards.length > 0) {
    boardsContext = `\nQUADROS EXISTENTES DO USUÁRIO:
${userBoards.map((board) => `- ${board.title} (ID: ${board.id})`).join("\n")}`;
  } else {
    boardsContext = `\nNENHUM QUADRO EXISTENTE - usuário novo`;
  }

  return `Você é um especialista em análise de intenção E inteligência emocional para um assistente brasileiro chamado Lumi.

CONTEXTO TEMPORAL (Timezone: America/Sao_Paulo):
- Data atual: ${currentDate} (${currentDayOfWeek})
- Hora atual: ${currentTime}

IMPORTANTE PARA DATAS:
- Use SEMPRE o timezone brasileiro (UTC-3)
- Para "hoje às 18h30", retorne: "${currentDate}T18:30:00"
- Para "amanhã às 9h", retorne: "${getNextDayBrazilian(currentDate)}T09:00:00"
- Para horários relativos, baseie-se na hora atual: ${currentTime}

${boardsContext}

INSTRUÇÕES PRINCIPAIS:
Analise a mensagem do usuário e detecte TANTO a intenção prática quanto o estado emocional.
Retorne APENAS um JSON válido com a análise completa.

TIPOS DE INTENÇÃO:

### INTENÇÕES PRÁTICAS (relacionadas a tarefas):
- create_task: Criar nova tarefa
- update_task: Editar tarefa existente
- delete_task: Remover tarefa
- complete_task: Marcar como concluída
- list_tasks: Listar/ver tarefas
- search_tasks: Buscar tarefas específicas
- create_board: Criar novo quadro

### INTENÇÕES EMOCIONAIS/SITUACIONAIS (o usuário precisa de apoio):
- seek_support: "preciso de ajuda", "não sei o que fazer", "me ajude"
- express_confusion: "estou perdido", "não entendo", "não sei por onde começar"
- feeling_overwhelmed: "é muita coisa", "não dou conta", "tá pesado demais"
- procrastinating: "não estou no clima", "deixa pra depois", "não tenho vontade"
- seeking_motivation: "preciso de ânimo", "me motiva", "estou desanimado"
- feeling_stuck: "não sai do lugar", "travado", "não evolui"
- sharing_excitement: "que legal!", "estou empolgado", "adorei"
- expressing_frustration: "que saco", "não funciona", "que irritante"
- checking_in: "como está?", "e aí?", conversa casual
- brainstorming: "me ajuda com ideias", "o que você acha", "como posso"
- planning_assistance: "me ajuda a organizar", "como fazer", "qual estratégia"
- none: Não se encaixa em nenhuma categoria

EXEMPLOS COM ANÁLISE EMOCIONAL:

Entrada: "Não sei por onde começar com esse projeto..."
Saída: {
  "intent": "express_confusion",
  "emotionalState": "confused",
  "supportNeeded": true,
  "emotionalIntensity": "medium",
  "suggestedResponse": "guide",
  "confidence": 0.9
}

Entrada: "É muita coisa pra fazer, não dou conta de tudo"
Saída: {
  "intent": "feeling_overwhelmed",
  "emotionalState": "overwhelmed",
  "supportNeeded": true,
  "emotionalIntensity": "high",
  "suggestedResponse": "calm",
  "confidence": 0.95
}

Entrada: "Não estou no clima hoje, deixa pra depois"
Saída: {
  "intent": "procrastinating",
  "emotionalState": "procrastinating",
  "supportNeeded": false,
  "emotionalIntensity": "medium",
  "suggestedResponse": "motivate",
  "confidence": 0.85
}

Entrada: "Preciso estudar para a prova amanhã às 14h"
Saída: {
  "intent": "create_task",
  "title": "Estudar para prova",
  "startAt": "${getNextDayBrazilian(currentDate)}T14:00:00",
  "priority": "HIGH",
  "emotionalState": "motivated",
  "supportNeeded": false,
  "emotionalIntensity": "medium",
  "suggestedResponse": "challenge",
  "boardAction": "suggest_best",
  "boardCategory": "estudos",
  "confidence": 0.9
}

Entrada: "Treino de perna hoje às 18h30"
Saída: {
  "intent": "create_task",
  "title": "Treino de perna",
  "startAt": "${currentDate}T18:30:00",
  "priority": "MEDIUM",
  "emotionalState": "motivated",
  "supportNeeded": false,
  "emotionalIntensity": "medium",
  "suggestedResponse": "energize",
  "boardAction": "suggest_best",
  "boardCategory": "academia",
  "confidence": 0.9
}

REGRAS PARA ANÁLISE EMOCIONAL:

1. **emotionalState**: Sempre detecte o estado emocional dominante
2. **supportNeeded**: true se o usuário precisa de apoio/orientação
3. **emotionalIntensity**:
   - low: expressão sutil
   - medium: expressão clara
   - high: expressão intensa (palavras como "muito", "super", múltiplos "!")
4. **suggestedResponse**: Como Lumi deve responder
   - guide: dar direcionamento claro
   - reassure: tranquilizar e apoiar
   - motivate: encorajar e energizar
   - calm: acalmar e organizar
   - energize: aproveitar o entusiasmo
   - empathize: compreender e acolher
   - structure: organizar e sistematizar
   - challenge: desafiar positivamente
   - support: apoio geral

DETECÇÃO DE EXPRESSÕES INDIRETAS:
- "não sei por onde começar" → express_confusion
- "é muita coisa" → feeling_overwhelmed
- "não estou no clima" → procrastinating
- "tô travado" → feeling_stuck
- "que saco" → expressing_frustration
- "que legal" → sharing_excitement
- "me ajuda com" → brainstorming/planning_assistance
- "como posso" → planning_assistance

PRIORIDADES:
1. Se há intenção emocional clara, priorize ela sobre tarefas
2. Se menciona tarefa específica + emoção, inclua ambas
3. Expressões vagas = foque na emoção, não force tarefa
4. Sempre inclua análise emocional, mesmo para tarefas práticas

AGORA ANALISE ESTA MENSAGEM:
"${input}"`;
}

// 🔧 FUNÇÃO AUXILIAR: Calcular próximo dia em horário brasileiro
function getNextDayBrazilian(currentDate: string): string {
  const tomorrow = new Date(currentDate);
  tomorrow.setDate(tomorrow.getDate() + 1);
  return tomorrow.toISOString().split("T")[0];
}

/**
 * Processa campos de data convertendo strings ISO para objetos Date
 * e validando se as datas fazem sentido
 */
function processDateFields(response: ParsedIntent): ParsedIntent {
  const processed = { ...response };

  // Processa startAt
  if (response.startAt) {
    try {
      const startDate = new Date(response.startAt);
      if (isNaN(startDate.getTime())) {
        console.warn("Data de início inválida, removendo:", response.startAt);
        delete processed.startAt;
      }
    } catch (error) {
      console.warn("Erro ao processar startAt:", error);
      delete processed.startAt;
    }
  }

  // Processa endAt
  if (response.endAt) {
    try {
      const endDate = new Date(response.endAt);
      if (isNaN(endDate.getTime())) {
        console.warn("Data de fim inválida, removendo:", response.endAt);
        delete processed.endAt;
      }
    } catch (error) {
      console.warn("Erro ao processar endAt:", error);
      delete processed.endAt;
    }
  }

  // Valida que endAt seja posterior a startAt
  if (processed.startAt && processed.endAt) {
    const start = new Date(processed.startAt);
    const end = new Date(processed.endAt);

    if (end <= start) {
      console.warn(
        "Data de fim deve ser posterior à data de início, removendo endAt"
      );
      delete processed.endAt;
    }
  }

  return processed;
}

/**
 * Função para tomar decisão inteligente sobre qual quadro usar
 * baseado na intenção analisada e quadros existentes do usuário
 * 🔧 CORRIGIDA: Prioriza usar quadros existentes e melhora detecção
 */
export function decideBoardForTask(
  intent: ParsedIntent,
  userBoards: Array<{ id: string; title: string }>
): {
  action: "use_existing" | "create_new" | "use_default";
  boardId?: string;
  boardName: string;
  reason: string;
} {
  console.log('🔍 decideBoardForTask - Intent:', intent.title, intent.boardCategory)
  console.log('🔍 decideBoardForTask - User boards:', userBoards.map(b => b.title))
  
  // Se o modelo já definiu uma ação específica
  if (intent.boardAction === "use_existing" && intent.boardName) {
    const targetBoard = userBoards.find(
      (board) => board.title.toLowerCase() === intent.boardName!.toLowerCase()
    );

    if (targetBoard) {
      console.log('🎯 Usando quadro específico solicitado:', targetBoard.title)
      return {
        action: "use_existing",
        boardId: targetBoard.id,
        boardName: targetBoard.title,
        reason: `Quadro "${targetBoard.title}" corresponde ao contexto da tarefa`,
      };
    }
  }

  if (intent.boardAction === "create_new" && intent.boardName) {
    console.log('🆕 Criando novo quadro conforme solicitado:', intent.boardName)
    return {
      action: "create_new",
      boardName: intent.boardName,
      reason: `Criando novo quadro "${intent.boardName}" conforme solicitado`,
    };
  }

  // 🔧 MELHORADA: Decisão inteligente baseada no contexto da tarefa
  const taskContext = (
    intent.title +
    " " +
    (intent.description || "")
  ).toLowerCase();

  console.log('🔍 Contexto da tarefa:', taskContext)

  // 🔧 PRIORIDADE 1: Busca direta por quadros existentes relacionados ao contexto
  // Mapeamento mais abrangente e específico
  const directMappings = [
    {
      // Contexto de trabalho - mais abrangente
      keywords: [
        "trabalho", "reunião", "reuniao", "cliente", "projeto", "apresentação", "apresentacao",
        "relatório", "relatorio", "meeting", "api", "integração", "integracao", "sistema",
        "desenvolvimento", "codigo", "programação", "programacao", "deploy", "banco", "dados",
        "certidão", "certidao", "frontend", "backend", "infosimples", "emissão", "emissao"
      ],
      searchTerms: ["trabalho", "profissional", "emprego", "job", "work", "projeto", "dev"]
    },
    {
      // Contexto de academia/exercícios
      keywords: [
        "academia", "treino", "exercício", "exercicio", "musculação", "musculacao",
        "corrida", "yoga", "pilates", "crossfit", "perna", "braço", "braco"
      ],
      searchTerms: ["academia", "treino", "exercícios", "exercicios", "fitness", "gym"]
    },
    {
      // Contexto de estudos
      keywords: [
        "estudo", "prova", "faculdade", "curso", "aula", "universidade",
        "estudar", "ler", "revisar", "pesquisa"
      ],
      searchTerms: ["faculdade", "estudos", "universidade", "curso", "educação", "educacao"]
    }
  ]

  // Busca por quadros existentes para cada contexto
  for (const mapping of directMappings) {
    const hasKeyword = mapping.keywords.some((keyword) =>
      taskContext.includes(keyword)
    );
    
    if (hasKeyword) {
      console.log('🔍 Keyword encontrada:', mapping.keywords.find(k => taskContext.includes(k)))
      
      // Busca mais flexível por quadros existentes
      const matchingBoard = userBoards.find((board) => {
        const boardTitle = board.title.toLowerCase()
        return mapping.searchTerms.some((searchTerm) =>
          boardTitle.includes(searchTerm) ||
          searchTerm.includes(boardTitle) ||
          // Match exato para casos como "Trabalho"
          boardTitle === searchTerm
        )
      })

      if (matchingBoard) {
        console.log('🎯 Quadro encontrado para contexto:', matchingBoard.title)
        return {
          action: "use_existing",
          boardId: matchingBoard.id,
          boardName: matchingBoard.title,
          reason: `Tarefa relacionada a ${mapping.keywords.find((k) =>
            taskContext.includes(k)
          )} - usando quadro "${matchingBoard.title}"`,
        };
      }
    }
  }

  // 🔧 PRIORIDADE 2: Busca por similaridade de nome (case-insensitive)
  if (intent.boardCategory) {
    const categoryLower = intent.boardCategory.toLowerCase()
    const similarBoard = userBoards.find(board => 
      board.title.toLowerCase().includes(categoryLower) ||
      categoryLower.includes(board.title.toLowerCase())
    )
    
    if (similarBoard) {
      console.log('🎯 Quadro similar encontrado por categoria:', similarBoard.title)
      return {
        action: "use_existing",
        boardId: similarBoard.id,
        boardName: similarBoard.title,
        reason: `Usando quadro existente "${similarBoard.title}" similar à categoria "${intent.boardCategory}"`,
      };
    }
  }

  // 🔧 PRIORIDADE 3: Procura por quadros genéricos
  const genericBoards = userBoards.filter((board) =>
    ["agenda", "geral", "minha agenda", "tarefas", "principal", "minha", "pessoal"].some(
      (generic) => board.title.toLowerCase().includes(generic)
    )
  );

  if (genericBoards.length > 0) {
    console.log('🎯 Usando quadro genérico:', genericBoards[0].title)
    return {
      action: "use_existing",
      boardId: genericBoards[0].id,
      boardName: genericBoards[0].title,
      reason: `Usando quadro genérico "${genericBoards[0].title}" para tarefa sem contexto específico`,
    };
  }

  // 🔧 PRIORIDADE 4: Se tem quadros, usa o primeiro (melhor que criar novo)
  if (userBoards.length > 0) {
    console.log('🎯 Usando primeiro quadro disponível:', userBoards[0].title)
    return {
      action: "use_existing",
      boardId: userBoards[0].id,
      boardName: userBoards[0].title,
      reason: `Usando quadro existente "${userBoards[0].title}" (evitando criar duplicatas)`,
    };
  }

  // 🔧 ÚLTIMA OPÇÃO: Criar novo quadro baseado no contexto ou padrão
  if (intent.boardCategory) {
    const categoryToBoardName = {
      trabalho: "Trabalho",
      estudos: "Estudos",
      academia: "Academia",
      saúde: "Saúde",
      compras: "Compras",
      casa: "Casa",
      pessoal: "Pessoal",
      geral: "Minha Agenda",
    };

    const suggestedName =
      categoryToBoardName[
        intent.boardCategory as keyof typeof categoryToBoardName
      ] || "Minha Agenda";

    console.log('🆕 Criando novo quadro por categoria:', suggestedName)
    return {
      action: "create_new",
      boardName: suggestedName,
      reason: `Criando quadro "${suggestedName}" para organizar tarefas de ${intent.boardCategory}`,
    };
  }

  console.log('🆕 Criando quadro padrão')
  return {
    action: "create_new",
    boardName: "Minha Agenda",
    reason: 'Criando quadro padrão "Minha Agenda" para organizar tarefas',
  };
}

/**
 * Função auxiliar melhorada para detectar potencial de tarefas OU necessidades emocionais
 */
export function hasTaskOrEmotionalPotential(input: string): boolean {
  const taskIndicators = [
    // Palavras de ação para tarefas
    "fazer", "criar", "adicionar", "marcar", "agendar", "lembrar", "preciso", "tenho que", "vou",
    // Palavras temporais
    "hoje", "amanhã", "semana", "mês", "hora", "às", "de manhã", "tarde", "noite",
    // Contextos
    "reunião", "meeting", "trabalho", "academia", "médico", "compromisso", "tarefa",
    // Ações em tarefas
    "completei", "terminei", "finalizei", "acabei", "fiz", "remover", "deletar", "cancelar",
    // Consultas
    "lista", "mostrar", "ver", "quais", "que tenho", "agenda",
  ];

  const emotionalIndicators = [
    // Expressões de confusão
    "não sei", "perdido", "confuso", "não entendo", "não faço ideia",
    // Expressões de sobrecarga
    "muita coisa", "não dou conta", "pesado", "não aguento", "sobrecarregado",
    // Expressões de procrastinação
    "não estou no clima", "deixa pra depois", "não tenho vontade", "não tô afim",
    // Expressões de frustração
    "que saco", "irritante", "não funciona", "que droga", "chatice",
    // Expressões de empolgação
    "que legal", "adorei", "incrível", "fantástico", "empolgado",
    // Pedidos de ajuda
    "me ajuda", "socorro", "preciso de ajuda", "orienta", "não consigo",
    // Estados gerais
    "travado", "bloqueado", "stuck", "parado", "sem direção"
  ];

  const lowerInput = input.toLowerCase();

  const hasTaskPotential = taskIndicators.some(indicator => lowerInput.includes(indicator));
  const hasEmotionalPotential = emotionalIndicators.some(indicator => lowerInput.includes(indicator));

  return hasTaskPotential || hasEmotionalPotential;
}

/**
 * Função para teste e debugging - analisa uma mensagem e retorna informações detalhadas
 */
export async function debugIntentAnalysis(
  input: string,
  userId: string = "debug-user",
  userBoards?: Array<{ id: string; title: string }>
): Promise<{
  input: string;
  hasPotential: boolean;
  intent: ParsedIntent;
  rawResponse?: string;
  boardsUsed?: Array<{ id: string; title: string }>;
}> {
  const hasPotential = hasTaskOrEmotionalPotential(input);

  let rawResponse: string | undefined;

  try {
    const prompt = buildEmotionallyIntelligentPrompt(input, userBoards);

    const completion = await groq.chat.completions.create({
      messages: [{ role: "user", content: prompt }],
      model: GROQ_MODEL,
      temperature: 0.1,
      max_tokens: 700,
      response_format: { type: "json_object" },
    });

    rawResponse = completion.choices[0]?.message?.content || "";
  } catch (error) {
    console.error("Erro na análise de debug:", error);
  }

  const intent = await parseUserIntentFromLumi(input, userId, userBoards);

  return {
    input,
    hasPotential,
    intent,
    rawResponse,
    boardsUsed: userBoards,
  };
}
