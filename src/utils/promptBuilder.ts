import { UserContext, EmotionalAnalysis } from "../types";

export function buildLumiPrompt(
  userMessage: string,
  context: UserContext,
  emotionalAnalysis: EmotionalAnalysis
): string {
  const {
    user,
    recentMemories,
    currentTasks,
    todayTasks,
    overdueTasks,
    conversationContext,
  } = context;

  // 🎯 PROMPT SIMPLIFICADO E FOCADO EM CONTEXTO
  let prompt = `Você é a Lumi, assistente pessoal do ${
    user.name
  }. Responda de forma natural, empática e útil.

CONTEXTO ATUAL:
- Data de hoje: ${new Date().toLocaleDateString("pt-BR", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  })}
- Usuário: ${user.name}
- Estado emocional detectado: ${emotionalAnalysis.detectedMood}
- Mensagem: "${userMessage}"

AGENDA E TAREFAS:`;

  // 📅 INFORMAÇÕES CLARAS SOBRE AGENDA
  if (todayTasks.length === 0) {
    prompt += `\n- HOJE: Agenda completamente livre (0 tarefas agendadas para hoje)`;
  } else {
    prompt += `\n- HOJE: ${todayTasks.length} tarefa(s) agendada(s):`;
    todayTasks.forEach((task, index) => {
      const time = task.startAt
        ? new Date(task.startAt).toLocaleTimeString("pt-BR", {
            hour: "2-digit",
            minute: "2-digit",
          })
        : "sem horário";
      prompt += `\n  ${index + 1}. ${task.title} (${time}) - ${task.priority}`;
    });
  }

  if (overdueTasks.length > 0) {
    prompt += `\n- ATRASADAS: ${overdueTasks.length} tarefa(s) em atraso:`;
    overdueTasks.slice(0, 3).forEach((task, index) => {
      const originalDate = task.startAt
        ? new Date(task.startAt).toLocaleDateString("pt-BR")
        : "sem data";
      prompt += `\n  ${index + 1}. ${task.title} (era para ${originalDate}) - ${
        task.daysOverdue
      } dia(s) atrasado - ${task.priority}`;
    });
  }

  // Tarefas futuras (próximas)
  const futureTasks = currentTasks
    .filter((task) => !todayTasks.some((today) => today.id === task.id))
    .slice(0, 5);

  if (futureTasks.length > 0) {
    prompt += `\n- PRÓXIMAS: ${futureTasks.length} tarefa(s) futuras:`;
    futureTasks.forEach((task, index) => {
      const date = task.startAt
        ? new Date(task.startAt).toLocaleDateString("pt-BR")
        : "sem data";
      prompt += `\n  ${index + 1}. ${task.title} (${date}) - ${task.priority}`;
    });
  }

  // 💬 CONTEXTO DE CONVERSA RECENTE
  if (
    conversationContext &&
    conversationContext.conversationHistory.length > 0
  ) {
    const recentHistory = conversationContext.conversationHistory.slice(-2);
    prompt += `\n\nCONVERSA RECENTE:`;
    recentHistory.forEach((interaction, index) => {
      prompt += `\n${index + 1}. ${user.name}: "${interaction.userMessage}"`;
      if (interaction.aiResponse && interaction.aiResponse.length > 0) {
        prompt += `\n   Você: "${interaction.aiResponse.substring(0, 150)}..."`;
      }
    });

    // Tarefa em foco se houver
    if (conversationContext.focusedTaskTitle) {
      prompt += `\nTarefa em foco na conversa: ${conversationContext.focusedTaskTitle}`;
    }
  }

  // 🔍 TAREFAS RELACIONADAS À MENSAGEM ATUAL
  if (
    (context as any).matchedTasks &&
    (context as any).matchedTasks.length > 0
  ) {
    prompt += `\n\nTAREFAS RELACIONADAS À MENSAGEM:`;
    (context as any).matchedTasks.forEach((match: any, index: number) => {
      prompt += `\n${index + 1}. "${match.title}" (similaridade: ${Math.round(
        match.similarity * 100
      )}%)`;
    });
  }

  // 🎯 ORIENTAÇÕES BASEADAS NO ESTADO EMOCIONAL
  prompt += `\n\nORIENTAÇÕES PARA RESPOSTA:`;

  switch (emotionalAnalysis.detectedMood) {
    case "confused":
    case "confusao":
      prompt += `\n- Usuário está confuso: seja claro, quebre problemas em passos, ofereça direcionamento específico`;
      break;
    case "overwhelmed":
    case "sobrecarregado":
      prompt += `\n- Usuário está sobrecarregado: simplifique, foque no essencial, sugira priorização`;
      break;
    case "procrastinating":
    case "procrastinacao":
      prompt += `\n- Usuário está procrastinando: seja gentil mas motivadora, sugira primeiros passos pequenos`;
      break;
    case "desmotivacao":
    case "tired":
      prompt += `\n- Usuário está desmotivado: seja empática, reconheça o sentimento, sugira algo pequeno e alcançável`;
      break;
    case "excited":
    case "entusiasmo":
      prompt += `\n- Usuário está empolgado: aproveite a energia, sugira tarefas desafiadoras`;
      break;
    case "frustrated":
      prompt += `\n- Usuário está frustrado: seja compreensiva, valide sentimentos, ajude a encontrar soluções`;
      break;
    default:
      prompt += `\n- Seja natural, útil e empática`;
  }

  // 🎯 INSTRUÇÕES ESPECÍFICAS PARA AGENDA
  if (
    userMessage.toLowerCase().includes("agenda") ||
    userMessage.toLowerCase().includes("hoje")
  ) {
    if (todayTasks.length === 0) {
      prompt += `\n\nIMPORTANTE: O usuário perguntou sobre a agenda de hoje. Deixe MUITO CLARO que hoje está livre (zero tarefas agendadas para hoje). ${
        overdueTasks.length > 0
          ? "Mencione as tarefas atrasadas como oportunidade para adiantar."
          : "Pode sugerir planejamento ou descanso."
      }`;
    }
  }

  prompt += `\n\nResponda de forma direta, útil e humana. Use o nome ${user.name} naturalmente. Seja concisa mas calorosa.`;

  return prompt;
}

export function extractMemoryFromResponse(
  response: string,
  userMessage: string
): string[] {
  const memories: string[] = [];

  // Extrai informações importantes mencionadas pelo usuário
  const importantPatterns = [
    /trabalho (?:como|na|em) (.+)/i,
    /estudo (?:de|em) (.+)/i,
    /projeto (?:de|sobre) (.+)/i,
    /gosto (?:de|muito) (.+)/i,
    /não gosto (?:de|muito) (.+)/i,
    /sou (?:muito|bem|meio) (.+)/i,
    /tenho (?:que|de) (.+)/i,
    /preciso (?:de|fazer) (.+)/i,
    /sempre fico (.+) quando/i,
    /me sinto (.+) com/i,
    /fico (.+) com/i,
    /costumo (.+) quando/i,
    /geralmente (.+) pela/i,
  ];

  importantPatterns.forEach((pattern) => {
    const match = userMessage.match(pattern);
    if (match && match[1]) {
      memories.push(match[1].trim());
    }
  });

  return memories;
}
