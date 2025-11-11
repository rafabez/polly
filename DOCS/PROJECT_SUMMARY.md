# 📊 Polly - Resumo do Projeto

## 🎯 Visão Geral

**Polly** é um assistente de IA para terminal Linux, desenvolvido em Python, que utiliza a API gratuita do Pollinations.ai. O projeto foi criado com o objetivo de ser incluído na distribuição BigLinux e potencialmente em repositórios oficiais.

## 📁 Estrutura do Projeto

```
polly/
├── polly/                    # Código fonte principal
│   ├── __init__.py          # Informações do pacote
│   ├── __main__.py          # Entry point e lógica principal
│   ├── api.py               # Cliente da API Pollinations
│   ├── cli.py               # Interface de linha de comando
│   ├── config.py            # Gerenciamento de configuração
│   ├── prompts.py           # Templates de prompts
│   └── utils.py             # Funções utilitárias
│
├── tests/                    # Testes
│   ├── __init__.py
│   └── test_basic.py        # Testes básicos
│
├── examples/                 # Exemplos e scripts de teste
│   └── test_examples.sh     # Script de testes automatizados
│
├── .github/                  # GitHub Actions
│   └── workflows/
│       └── test.yml         # CI/CD workflow
│
├── setup.py                  # Script de instalação
├── pyproject.toml           # Configuração moderna de build
├── requirements.txt         # Dependências
├── Makefile                 # Comandos úteis
│
├── README.md                # Documentação principal
├── QUICKSTART.md            # Guia rápido de instalação
├── INSTALL.md               # Guia detalhado de instalação
├── CONTRIBUTING.md          # Guia de contribuição
├── PROJECT_SUMMARY.md       # Este arquivo
├── LICENSE                  # Licença MIT
│
├── init_repo.sh             # Script de inicialização do Git
└── .gitignore              # Arquivos ignorados pelo Git
```

## 🚀 Funcionalidades Implementadas

### Modos de Operação

1. **Modo Padrão**: Perguntas gerais
   ```bash
   polly "O que é recursão?"
   ```

2. **Modo Explain (-e)**: Explica arquivos ou conteúdo
   ```bash
   polly -e script.sh
   cat file.txt | polly -e
   ```

3. **Modo Command (-c)**: Gera comandos bash (apenas comando)
   ```bash
   polly -c "listar arquivos modificados hoje"
   ```

4. **Modo Command Explain (-ce)**: Gera comandos com explicações
   ```bash
   polly -ce "comprimir logs antigos"
   ```

5. **Modo Debug (-d)**: Analisa erros e código
   ```bash
   cat error.log | polly -d
   ```

6. **Modo Refactor (-r)**: Sugere melhorias de código
   ```bash
   polly -r "$(cat script.py)"
   ```

7. **Modo Translate (-t)**: Traduz texto
   ```bash
   polly -t Portuguese "Hello world"
   ```

8. **Modo Interactive (-i)**: Chat interativo com contexto
   ```bash
   polly -i
   ```

### Modelos Disponíveis

- **gemini** (padrão) - Gemini 2.5 Flash Lite - Maior janela de contexto
- **openai** - OpenAI GPT-5 Nano - Rápido
- **openai-large** - OpenAI GPT-4.1 - Mais capaz
- **deepseek** - DeepSeek V3.1 - Raciocínio avançado
- **qwen-coder** - Qwen 2.5 Coder 32B - Especializado em código
- **mistral** - Mistral Small 3.2 24B - Balanceado
- **gemini-search** - Gemini com Google Search

### Parâmetros Configuráveis

- **--model**: Seleciona modelo específico
- **--temperature**: Controla criatividade (0.0-3.0)
- **--stream**: Habilita resposta em tempo real
- **--max-tokens**: Limita tamanho da resposta
- **-o, --output**: Salva resposta em arquivo
- **--json**: Saída em formato JSON
- **--no-markdown**: Desabilita formatação markdown

### Configuração

- Arquivo de configuração: `~/.config/polly/config.yaml`
- Configurações persistentes para modelo padrão, temperatura, etc.
- Comandos de configuração: `--config`, `--set-default-model`, `--reset-config`

## 🛠️ Tecnologias Utilizadas

### Linguagem
- **Python 3.8+** - Escolhido por:
  - Facilidade de distribuição
  - Código legível e manutenível
  - Ecossistema rico de bibliotecas
  - Compatibilidade com todas as distros Linux

### Bibliotecas Principais
- **requests** (2.31.0+) - Chamadas HTTP à API
- **rich** (13.7.0+) - Interface bonita no terminal
- **pyyaml** (6.0.1+) - Gerenciamento de configuração

### API
- **Pollinations.ai** - API gratuita de IA
  - Endpoint: `https://text.pollinations.ai`
  - Referrer obrigatório: `deepentest.com`
  - Suporta temperatura, streaming, múltiplos modelos
  - Compatível com OpenAI API

## 📦 Empacotamento

### Métodos de Instalação

1. **Desenvolvimento** (recomendado para testes):
   ```bash
   pip install --user -e .
   ```

2. **Usuário**:
   ```bash
   pip install --user .
   ```

3. **Sistema** (requer sudo):
   ```bash
   sudo pip install .
   ```

4. **Pacote .deb** (para BigLinux):
   ```bash
   python3 setup.py --command-packages=stdeb.command bdist_deb
   ```

### Arquivos de Empacotamento

- **setup.py** - Setup tradicional
- **pyproject.toml** - Build moderno (PEP 517/518)
- **requirements.txt** - Dependências
- **Makefile** - Comandos úteis

## 🎨 Design e Boas Práticas

### Arquitetura
- **Modular**: Separação clara de responsabilidades
- **Configurável**: Sistema de configuração flexível
- **Extensível**: Fácil adicionar novos modos e funcionalidades
- **Testável**: Estrutura preparada para testes

### Código
- Segue **PEP 8** (estilo Python)
- Docstrings em todas as funções
- Type hints para clareza
- Tratamento robusto de erros
- Logging para debugging

### UX
- Output bonito com **Rich** (markdown, syntax highlighting)
- Mensagens de erro claras
- Help detalhado (`--help`)
- Feedback visual (spinners, cores)
- Suporte a pipe para scripting

## 🔒 Segurança e Privacidade

- API gratuita, sem necessidade de chave
- Referrer obrigatório: `interzonesec.com`
- Sem coleta de dados do usuário
- Código open source (MIT License)
- Validação de entrada para evitar injeção

## 🚦 Status do Projeto

### ✅ Implementado
- [x] Estrutura completa do projeto
- [x] Todos os modos de operação
- [x] Múltiplos modelos de IA
- [x] Sistema de configuração
- [x] Suporte a streaming
- [x] Suporte a pipe (stdin/stdout)
- [x] Interface bonita com Rich
- [x] Documentação completa
- [x] Scripts de instalação
- [x] Testes básicos
- [x] Licença MIT

### 🔄 Para Futuras Versões
- [ ] Testes unitários completos
- [ ] Bash/Zsh completion
- [ ] Man page
- [ ] Histórico de conversas
- [ ] Cache de respostas
- [ ] Suporte a plugins
- [ ] Análise de imagens (se API suportar)
- [ ] Pacote .deb oficial para BigLinux
- [ ] Pacote .rpm para Fedora/RHEL

## 📊 Métricas do Projeto

- **Linhas de código**: ~1500 (Python)
- **Arquivos Python**: 7 módulos
- **Dependências**: 3 (requests, rich, pyyaml)
- **Compatibilidade**: Python 3.8+
- **Licença**: MIT
- **Tamanho**: ~50KB (código fonte)

## 🎯 Próximos Passos

### Para Desenvolvimento
1. Instalar: `pip install --user -e .`
2. Testar: `bash examples/test_examples.sh`
3. Desenvolver novas features
4. Criar testes unitários
5. Documentar mudanças

### Para Produção (BigLinux)
1. Testar extensivamente
2. Criar pacote .deb
3. Adicionar ao repositório BigLinux
4. Documentar para usuários finais
5. Coletar feedback

### Para Comunidade
1. Publicar no GitHub
2. Criar releases
3. Aceitar contribuições
4. Manter documentação atualizada
5. Responder issues

## 📞 Contato e Suporte

- **GitHub**: (adicionar URL do repositório)
- **Issues**: Para bugs e feature requests
- **Discussions**: Para perguntas e ideias
- **BigLinux**: Integração futura

## 🙏 Agradecimentos

- **Pollinations.ai** - API gratuita de IA
- **BigLinux** - Distribuição alvo
- **Comunidade Python** - Bibliotecas excelentes
- **Comunidade Linux** - Inspiração e feedback

---

**Versão**: 0.1.0  
**Data**: 2025  
**Status**: Pronto para testes  
**Licença**: MIT
