# 🤖 Lumi AI Assistant 2.0 - Assistente de Produtividade Inteligente

**Lumi** é uma assistente de IA modular e inteligente, projetada para revolucionar seu gerenciamento de produtividade. Evoluindo de uma arquitetura monolítica para um sistema modular avançado, Lumi combina inteligência artificial de ponta com uma interface natural e intuitiva.

## 🌟 O Que é Lumi?

Lumi é mais que um simples gerenciador de tarefas - é sua **parceira inteligente de produtividade**. Com personalidade carismática e capacidades avançadas de IA, ela entende suas necessidades, adapta-se ao seu estilo de trabalho e oferece suporte contextual para maximizar sua eficiência.

### 🎯 Filosofia do Projeto

- **Inteligência Adaptativa**: IA que aprende e evolui com você
- **Simplicidade Poderosa**: Interface natural que esconde complexidade técnica avançada
- **Modularidade**: Arquitetura extensível e maintível
- **Personalização**: Respostas e comportamentos adaptados ao seu contexto

## 🚀 Principais Características

### 🧠 **IA Dual Avançada**
- **Google Gemini** como engine principal
- **OpenRouter** com múltiplos modelos como fallback
- Processamento de linguagem natural contextual

### 📋 **Gerenciamento Inteligente de Tarefas**
- Extração automática de tarefas de texto natural
- Processamento de múltiplas tarefas simultaneamente
- Validação e limpeza inteligente de dados

### 🎭 **Sistema de Personalidade Adaptativa**
- Análise de humor e contexto emocional
- Respostas personalizadas baseadas no estado do usuário
- Memória conversacional para continuidade

### 🔧 **Arquitetura Modular**
- **Core Modules**: AI Engine, Personality, Task Handler, Education
- **Utility Modules**: Pattern Detection, Mood Analysis
- **Fallback System**: Compatibilidade e robustez garantidas

### 📚 **Capacidades Educacionais**
- Explicações detalhadas sobre produtividade
- Conselhos contextuais e motivacionais
- Suporte para aprendizado contínuo

## 🏗️ Arquitetura Técnica

### Versão 2.0 - Modular Architecture
- **Linguagem**: Python 3.7+
- **Arquitetura**: Modular com Dependency Injection
- **IA**: Google Gemini + OpenRouter Fallback
- **API**: Flask REST API incluída
- **Compatibilidade**: Totalmente retrocompatível com v1.0

### Estrutura Modular
```
src/
├── core/              # Módulos principais
│   ├── ai_engine.py   # Engine de IA
│   ├── assistant.py   # Orquestrador principal
│   ├── personality.py # Sistema de personalidade
│   └── task_handler.py # Gerenciador de tarefas
├── utils/             # Módulos utilitários
│   ├── patterns.py    # Detecção de padrões
│   └── mood_analyzer.py # Análise de humor
└── ai_assistant.py    # Wrapper de compatibilidade
```

## 📖 Documentação Completa

Este projeto inclui documentação técnica abrangente para diferentes audiências:

### 📋 **Para Usuários**
- **[README.md](README.md)** - Visão geral e guia de início rápido *(você está aqui)*

### 🔧 **Para Desenvolvedores**
- **[TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md)** - Documentação técnica completa
  - Arquitetura detalhada do sistema
  - Especificações de todos os módulos
  - Fluxos de processamento e integração
  - Guias de configuração e deployment

- **[API_REFERENCE.md](API_REFERENCE.md)** - Referência completa da API
  - Documentação de classes e métodos
  - Exemplos de uso e parâmetros
  - Modelos de dados e tratamento de erros
  - Endpoints REST e configurações

- **[IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)** - Guia de implementação
  - Como estender funcionalidades
  - Padrões de arquitetura
  - Boas práticas de desenvolvimento
  - Configuração de CI/CD e testes

## ⚡ Início Rápido

### Pré-requisitos
- Python 3.7+ instalado
- Conexão com internet para APIs de IA

### 📦 Instalação

1. **Clone o repositório**:
```bash
git clone https://github.com/gabrielnogueiraz/lumi-AI.git
cd lumi-AI
```

2. **Instale as dependências**:
```bash
pip install -r requirements.txt
```

3. **Configure as variáveis de ambiente** (opcional):
```bash
# Para usar Google Gemini
export GEMINI_API_KEY="sua_chave_aqui"

# Para usar OpenRouter (fallback)
export OPENROUTER_API_KEY="sua_chave_aqui"
```

4. **Execute Lumi**:
```bash
python src/main.py
```

Ou use o script de conveniência no Windows:
```bash
run.bat
```

### 🔧 Verificação de Instalação

Execute o verificador automático para garantir que tudo está funcionando:
```bash
python src/scripts/check_setup.py
```

### 🚨 Solução de Problemas Rápidos

**Erro de módulo não encontrado**:
```bash
pip install requests flask psutil flask-cors
```

**Problemas com Python no Windows**:
1. Baixe Python em [python.org](https://www.python.org/downloads/)
2. Marque "Add Python to PATH" durante instalação
3. Use `run.bat` em vez de comandos Python diretos

**Problemas de importação de módulos**:
- O sistema possui fallback automático para máxima compatibilidade
- Módulos não encontrados não impedem o funcionamento básico

## 💬 Como Usar Lumi

### 🎯 Modo Interativo

Execute o programa e converse naturalmente com Lumi:

```bash
python src/main.py
```

### 📝 Exemplos de Interação

#### Gerenciamento de Tarefas
```
👤 Usuário: "Adicionar tarefa estudar Python às 14h"
🤖 Lumi: "✨ Perfeito! Adicionei 'estudar Python às 14h' na sua lista. 
           Que ótimo foco nos estudos! 🚀"

👤 Usuário: "Quais são minhas tarefas?"
🤖 Lumi: "📋 Aqui está sua agenda atual:
           1. estudar Python às 14h
           Você está no caminho certo! 💪"

👤 Usuário: "Concluir tarefa 1"
🤖 Lumi: "🎉 Parabéns! Tarefa 'estudar Python às 14h' concluída! 
           Sua dedicação está rendendo frutos! ⭐"
```

#### Múltiplas Tarefas
```
👤 Usuário: "Adicionar: 1. Revisar código 2. Fazer backup 3. Testar aplicação"
🤖 Lumi: "🚀 Incrível! Adicionei 3 tarefas da sua lista:
           ✅ Revisar código
           ✅ Fazer backup  
           ✅ Testar aplicação
           Organização é a chave do sucesso! 💼"
```

#### Consultas Educacionais
```
👤 Usuário: "Como melhorar meu foco durante o trabalho?"
🤖 Lumi: "🧠 Excelente pergunta! Aqui estão técnicas comprovadas para melhorar o foco:
           
           1. **Técnica Pomodoro**: 25min focado + 5min pausa
           2. **Ambiente limpo**: Elimine distrações visuais
           3. **Objetivos claros**: Defina metas específicas
           ..."
```

### 🌐 API REST

Lumi também oferece uma API REST para integrações:

```bash
# Iniciar servidor API
python src/start_lumi_api.py

# Exemplos de uso
curl -X POST http://localhost:5000/process \
  -H "Content-Type: application/json" \
  -d '{"message": "adicionar tarefa estudar Python"}'
```

## 🏛️ Estrutura do Projeto

```
lumi-AI/
├── 📁 src/                          # Código fonte principal
│   ├── 🔧 core/                     # Módulos principais
│   │   ├── ai_engine.py             # Engine de IA (Gemini/OpenRouter)
│   │   ├── assistant.py             # Orquestrador modular
│   │   ├── personality.py           # Sistema de personalidade
│   │   ├── task_handler.py          # Manipulador de tarefas
│   │   └── education.py             # Módulo educacional
│   ├── 🛠️ utils/                    # Módulos utilitários
│   │   ├── patterns.py              # Detecção de padrões
│   │   └── mood_analyzer.py         # Análise de humor/contexto
│   ├── 📊 data/                     # Armazenamento de dados
│   ├── 🧪 tests/                    # Testes automatizados
│   ├── 📜 scripts/                  # Scripts utilitários
│   ├── ai_assistant.py              # Wrapper de compatibilidade
│   ├── main.py                      # Ponto de entrada principal
│   ├── lumi_api.py                  # API REST Flask
│   └── task_manager.py              # Gerenciador de dados
├── 📚 Documentação/
│   ├── README.md                    # Visão geral (este arquivo)
│   ├── TECHNICAL_DOCUMENTATION.md  # Documentação técnica completa
│   ├── API_REFERENCE.md             # Referência da API
│   └── IMPLEMENTATION_GUIDE.md      # Guia de implementação
├── requirements.txt                 # Dependências Python
└── run.bat                         # Script de conveniência Windows
```

## 🎯 Casos de Uso

### 👨‍💼 **Para Profissionais**
- Gerenciamento ágil de tarefas e projetos
- Relatórios de produtividade automáticos
- Integração com workflows existentes via API

### 🎓 **Para Estudantes**
- Organização de estudos e prazos
- Técnicas de foco e concentração
- Acompanhamento de progresso acadêmico

### 👩‍💻 **Para Desenvolvedores**
- Base sólida para chatbots inteligentes
- Arquitetura modular extensível
- APIs bem documentadas para integração

### 🏢 **Para Equipes**
- Deploy como serviço compartilhado
- Customização de personalidade
- Integração com ferramentas corporativas

## 🔮 Evolução e Roadmap

### ✅ **Versão 2.0 (Atual)**
- Arquitetura modular completa
- IA dual (Gemini + OpenRouter)
- Sistema de personalidade avançado
- Análise de humor e contexto
- Compatibilidade total com v1.0

### 🚧 **Versão 2.1 (Em Desenvolvimento)**
- Plugin system para extensões
- Interface web moderna
- Sincronização em nuvem
- Métricas avançadas de produtividade

### 🌟 **Versão 3.0 (Futuro)**
- Aprendizado de máquina personalizado
- Integração com calendários externos
- Mobile app companion
- Colaboração em equipe

## 🤝 Contribuindo

Lumi é um projeto open-source e contribuições são muito bem-vindas!

### Como Contribuir
1. **Fork** o repositório
2. **Crie** uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. **Commit** suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. **Push** para a branch (`git push origin feature/nova-feature`)
5. **Abra** um Pull Request

### Áreas de Contribuição
- 🐛 **Bug fixes** e melhorias de estabilidade
- ✨ **Novas features** e módulos
- 📚 **Documentação** e exemplos
- 🧪 **Testes** e quality assurance
- 🎨 **UI/UX** para interface web
- 🌐 **Traduções** para outros idiomas

## 📄 Licença

Este projeto está licenciado sob a **Licença MIT** - consulte o arquivo [LICENSE](LICENSE) para detalhes.

### O que isso significa?
- ✅ Uso comercial permitido
- ✅ Modificação permitida
- ✅ Distribuição permitida
- ✅ Uso privado permitido

---

## 🌟 Conclusão

**Lumi AI Assistant 2.0** representa uma evolução significativa em assistentes de produtividade, combinando:

- 🧠 **Inteligência artificial avançada**
- 🏗️ **Arquitetura modular robusta**
- 🎭 **Personalidade adaptativa**
- 🔧 **Extensibilidade total**
- 📚 **Documentação abrangente**

Seja você um usuário buscando produtividade ou um desenvolvedor procurando uma base sólida para IA conversacional, Lumi oferece a solução completa que você precisa.

**Comece sua jornada de produtividade inteligente hoje mesmo!** 🚀

---

<div align="center">

**Feito com ❤️ e IA avançada**

[⭐ Star no GitHub](https://github.com/gabrielnogueiraz/lumi-AI) • [📖 Documentação](TECHNICAL_DOCUMENTATION.md) • [🐛 Reportar Bug](https://github.com/gabrielnogueiraz/lumi-AI/issues) • [💡 Sugerir Feature](https://github.com/gabrielnogueiraz/lumi-AI/issues)

</div>
