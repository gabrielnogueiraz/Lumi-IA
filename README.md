# 🤖 Lumi AI - Assistente de Produtividade Inteligente

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12+-blue.svg)](https://postgresql.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Lumi** é uma assistente de produtividade baseada em IA que se adapta ao seu estado emocional e oferece insights personalizados para otimizar seu fluxo de trabalho. Integrada nativamente ao **Toivo App**, ela compreende seus padrões, antecipa suas necessidades e evolui com você.

## ✨ Características Principais

### 🧠 **Inteligência Artificial Adaptativa**
- 🎭 **Personalidade Dinâmica**: 6 estados emocionais distintos (motivado, lutando, focado, sobrecarregado, celebrando, retornando)
- 📈 **Análise Comportamental**: Detecta padrões de produtividade em tempo real
- 💬 **Conversas Contextuais**: Respostas que evoluem com seu estado mental

### 📊 **Analytics de Produtividade**
- 🎯 **Insights Profundos**: Métricas detalhadas sobre hábitos e performance
- 🕐 **Análise Temporal**: Identifica seus horários de maior produtividade
- 🌱 **Crescimento Pessoal**: Acompanha evolução e conquistas

### 🎯 **Gerenciamento Inteligente**
- ⚡ **Otimização Automática**: Reorganiza tarefas baseado em energia e contexto
- ⏱️ **Estimativas Precisas**: Calcula tempo necessário baseado em histórico
- 🏆 **Priorização Dinâmica**: Ajusta prioridades conforme deadlines e energia

### 🔗 **Integração Total com Toivo**
- 👥 **Consciência de Usuários**: Acesso completo aos perfis do app
- ✅ **Gestão de Tarefas**: Manipula tarefas diretamente do banco
- 📊 **Contexto Histórico**: Analisa todo histórico de pomodoros e conquistas

## 🚀 Início Rápido

### 📋 Pré-requisitos
- **Python 3.8+**
- **PostgreSQL 12+** (banco do Toivo App)
- **Chave API Google Gemini**

### ⚡ Instalação Express

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/lumi-ai.git
cd lumi-ai

# 2. Instale dependências
pip install -r requirements.txt

# 3. Configure ambiente
cp .env.example .env
# Edite .env com suas configurações

# 4. Execute a aplicação
python main.py
```

### 🔧 Configuração

1. **Configure PostgreSQL** (banco existente do Toivo):
   ```bash
   DB_NAME=pomodorotasks
   DB_USER=seu_usuario
   DB_PASSWORD=sua_senha
   ```

2. **Obtenha chave Gemini** ([Google AI Studio](https://makersuite.google.com/app/apikey)):
   ```bash
   GEMINI_API_KEY=sua_chave_aqui
   ```

3. **Teste a instalação**:
   ```bash
   curl http://localhost:5000/health
   ```

## 🎯 Uso Prático

### 💬 Chat Inteligente
```bash
curl -X POST "http://localhost:5000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "message": "Como está minha produtividade esta semana?",
    "context": {"mood": "focused"}
  }'
```

### 📊 Analytics
```bash
curl "http://localhost:5000/analytics/1/insights?period=week"
```

### 🎭 Estados da Personalidade

| Estado | Comportamento | Quando Ativa |
|--------|---------------|--------------|
| 🎯 **Motivated** | Energia alta, foco em conquistas | Após completar metas |
| 😰 **Struggling** | Suporte emocional, quebra de tarefas | Baixa produtividade |
| 🧘 **Focused** | Minimiza distrações, deep work | Sessões longas |
| 😵 **Overwhelmed** | Priorização, técnicas de calma | Muitas tarefas pendentes |
| 🎉 **Celebrating** | Reconhecimento, momentum | Conquistas importantes |
| 👋 **Returning** | Reintegração suave | Volta após pausa |

## 📱 Endpoints Principais

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/chat` | POST | Conversação com a Lumi |
| `/analytics/{user_id}/insights` | GET | Insights de produtividade |
| `/health` | GET | Status do sistema |
| `/docs` | GET | Documentação interativa |

## 🏗️ Arquitetura

```
📦 Lumi AI/
├── 🤖 core/              # Motor de IA e personalidade
│   ├── ai_engine.py      # Integração Gemini AI
│   ├── personality_engine.py # Sistema de personalidade
│   └── context_analyzer.py   # Análise de contexto
├── 📡 api/               # Endpoints REST
├── 🧪 services/          # Lógica de negócio
├── 📊 models/            # Modelos de dados
├── ⚙️ config/            # Configurações
└── 🔧 utils/             # Utilitários
```

## 📚 Documentação

### 📋 **Para Usuários**
- **README.md** - Visão geral e início rápido *(você está aqui)*

### 🔧 **Para Desenvolvedores**
- **[TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md)** - Arquitetura e especificações técnicas
- **[API_REFERENCE.md](API_REFERENCE.md)** - Referência completa da API
- **[IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)** - Guia de implementação e extensão

### 🌐 **Documentação Interativa**
- **Swagger UI**: `http://localhost:5000/docs`
- **ReDoc**: `http://localhost:5000/redoc`

## 🤝 Contribuição

1. **Fork** o projeto
2. **Crie** sua feature branch: `git checkout -b feature/nova-funcionalidade`
3. **Commit** suas mudanças: `git commit -m 'feat: adiciona nova funcionalidade'`
4. **Push** para a branch: `git push origin feature/nova-funcionalidade`
5. **Abra** um Pull Request

---

<div align="center">

**🚀 Lumi AI - Transformando produtividade através de inteligência artificial adaptativa**

*Desenvolvido com ❤️ para o ecossistema Toivo*

</div>
