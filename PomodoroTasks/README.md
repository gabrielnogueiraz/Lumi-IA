# Lumi - Assistente de Produtividade Inteligente

Lumi é uma assistente pessoal de produtividade baseada em IA para o PomodoroTasks que ajuda no gerenciamento de tarefas, acompanhamento de produtividade e fornece insights baseados na técnica Pomodoro.

## Recursos Principais

- **Gerenciamento de Tarefas**: Adicionar, remover, modificar e consultar tarefas e eventos
- **Tracking de Pomodoros**: Registrar sessões de foco usando a técnica Pomodoro
- **Relatórios de Produtividade**: Gerar relatórios detalhados sobre sua produtividade
- **Assistência por IA**: Receba conselhos e sugestões sobre produtividade e disciplina

## Requisitos

- Python 3.7+
- Pacotes necessários: `requests`

## Instalação

1. Clone o repositório:
```
git clone https://github.com/seu-usuario/PomodoroTasks.git
cd PomodoroTasks
```

2. Instale as dependências:
```
pip install -r requirements.txt
```

3. Execute o verificador de instalação para garantir que tudo está correto:
```
python check_setup.py
```

4. Execute o assistente:
```
python main.py
```

### Resolução de Problemas

Se encontrar o erro `ModuleNotFoundError: No module named 'requests'`, significa que o módulo `requests` não está instalado. Para resolver, tente:

```
pip install requests
```

Ou, se o pip não estiver no seu PATH:

```
python -m pip install requests
```

Se estiver usando Windows e tiver problemas com Python, verifique se:
1. O Python está instalado corretamente (baixe em https://www.python.org/downloads/)
2. A opção "Add Python to PATH" foi marcada durante a instalação
3. Tente usar o script `run.bat` em vez do comando Python diretamente

## Como Usar

### Modo Interativo

Execute o programa e interaja com o assistente:

```
python main.py
```

### Exemplos de Comandos

#### Gerenciamento de Tarefas

- Adicionar uma tarefa: `Adicione uma tarefa fazer relatório para amanhã às 14h`
- Consultar tarefas: `Mostre minhas tarefas para hoje`
- Marcar como concluída: `Marque a tarefa fazer relatório como concluída`

#### Relatórios

- Relatório geral: `Gere um relatório da minha semana`
- Relatório de pomodoros: `Mostre meus pomodoros dos últimos 5 dias`
- Relatório detalhado: `Relatório detalhado de produtividade do mês`

#### Perguntas sobre Produtividade

- `Como posso melhorar meu foco durante os pomodoros?`
- `Quais são as melhores técnicas para gerenciar meu tempo?`
- `Como equilibrar trabalho e pausas?`

## Estrutura do Projeto

- `main.py`: Ponto de entrada do programa
- `ai_assistant.py`: Interface principal com a IA
- `task_manager.py`: Gerenciamento de tarefas e eventos
- `reports_generator.py`: Geração de relatórios de produtividade
- `data/`: Diretório onde os dados são armazenados

## Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.
