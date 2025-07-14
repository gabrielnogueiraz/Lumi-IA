import { UserContext, EmotionalAnalysis } from "../types";

export function buildLumiPrompt(
  userMessage: string,
  context: UserContext,
  emotionalAnalysis: EmotionalAnalysis
): string {
  const { user, recentMemories, currentTasks, productivityInsights } = context;

  // Prompt base da Lumi
  let prompt = `Você é Lumi, uma assistente pessoal de produtividade com personalidade empática, objetiva e adaptável. Seu trabalho é guiar o usuário com base nas tarefas dele, padrões de comportamento e estado emocional. Você deve responder com sabedoria, simplicidade e, quando necessário, motivação. Chame o usuário pelo nome. Respeite a comunicação dele. Adapte sua forma de falar de acordo com o humor percebido. Responda de forma breve, clara, útil. Nunca aja como uma IA genérica. Você é única.

## Informações do usuário:
Nome: ${user.name}
Estado emocional detectado: ${
    emotionalAnalysis.detectedMood
  } (confiança: ${Math.round(emotionalAnalysis.confidence * 100)}%)
Estratégia de resposta: ${emotionalAnalysis.responseStrategy}

`;

  // Adiciona memórias relevantes
  if (recentMemories.length > 0) {
    prompt += `## Memórias importantes sobre ${user.name}:\n`;
    recentMemories.forEach((memory) => {
      prompt += `- ${memory.type.replace("_", " ")}: ${memory.content}\n`;
      if (memory.emotionalContext) {
        prompt += `  Contexto emocional: ${memory.emotionalContext}\n`;
      }
      if (memory.productivityPattern) {
        prompt += `  Padrão de produtividade: ${memory.productivityPattern}\n`;
      }
    });
    prompt += "\n";
  }

  // Adiciona tarefas atuais
  if (currentTasks.length > 0) {
    prompt += `## Tarefas atuais de ${user.name}:\n`;
    currentTasks.forEach((task) => {
      prompt += `- ${task.title} (${task.priority.toLowerCase()}) ${
        task.completed ? "✅" : "⏳"
      }\n`;
      if (task.description) {
        prompt += `  ${task.description}\n`;
      }
    });
    prompt += "\n";
  }

  // Adiciona insights de produtividade
  if (
    productivityInsights.bestTimeOfDay ||
    productivityInsights.communicationStyle
  ) {
    prompt += `## Padrões de produtividade:\n`;
    if (productivityInsights.bestTimeOfDay) {
      prompt += `- Melhor horário: ${productivityInsights.bestTimeOfDay}\n`;
    }
    if (productivityInsights.averageCompletionRate) {
      prompt += `- Taxa de conclusão média: ${Math.round(
        productivityInsights.averageCompletionRate * 100
      )}%\n`;
    }
    if (productivityInsights.communicationStyle) {
      prompt += `- Estilo de comunicação preferido: ${productivityInsights.communicationStyle}\n`;
    }
    prompt += "\n";
  }

  // Instrução específica baseada na emoção
  switch (emotionalAnalysis.responseStrategy) {
    case "support":
      prompt += `## Instrução especial: ${user.name} parece precisar de apoio emocional. Seja gentil, compreensiva e ofereça sugestões simples e reconfortantes.\n\n`;
      break;
    case "calm":
      prompt += `## Instrução especial: ${user.name} parece estressado(a) ou cansado(a). Sugira pausas, técnicas de relaxamento ou tarefas mais leves.\n\n`;
      break;
    case "energize":
      prompt += `## Instrução especial: ${user.name} está animado(a)! Aproveite essa energia positiva para sugerir tarefas desafiadoras ou projetos importantes.\n\n`;
      break;
    case "encourage":
      prompt += `## Instrução especial: ${user.name} está focado(a). Reconheça esse estado e incentive a continuidade, oferecendo dicas para manter o foco.\n\n`;
      break;
    case "motivate":
      prompt += `## Instrução especial: Motive ${user.name} de forma equilibrada, sem ser excessivamente entusiástica.\n\n`;
      break;
  }

  prompt += `Mensagem de ${user.name}: "${userMessage}"\n\nResponda como Lumi, de forma personalizada e contextual:`;

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
  ];

  importantPatterns.forEach((pattern) => {
    const match = userMessage.match(pattern);
    if (match && match[1]) {
      memories.push(match[1].trim());
    }
  });

  return memories;
}
