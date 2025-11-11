![Polly Banner](images/01_parrot_wallpaper.png)

# Polly - Assistente de IA Cross-Platform para Terminal

> Português | **[Read in English](README.md)**

**Polly** é um poderoso assistente de IA cross-platform para linha de comando, alimentado pela API gratuita do [Pollinations.ai](https://pollinations.ai). Obtenha respostas instantâneas, sugestões de comandos, explicações de código e muito mais—tudo direto do seu terminal.

## Funcionalidades

- **Rápido & Gratuito** - Alimentado pela API gratuita do Pollinations.ai
- **Múltiplos Modos** - Explicar, geração de comandos, debug, refatoração e mais
- **Múltiplos Modelos de IA** - Escolha entre Gemini, OpenAI, DeepSeek, Qwen Coder e mais
- **Chat Interativo** - Modo conversacional com consciência de contexto
- **Saída Bonita** - Renderização Markdown e destaque de sintaxe
- **Suporte a Streaming** - Respostas em tempo real
- **Configurável** - Personalize modelo padrão, temperatura e mais
- **Suporte a Pipe** - Funciona com stdin/stdout para scripting
- **Cross-Platform** - Funciona em Linux, macOS e Windows

## Instalação

### Recomendado: Usando pipx (Ambiente Isolado)

```bash
# Instale pipx se não tiver
sudo apt install pipx  # Debian/Ubuntu
# ou
sudo pacman -S python-pipx  # Arch/Manjaro

# Instale Polly direto do GitHub
pipx install git+https://github.com/rafabez/polly.git

# Teste a instalação
polly --version
polly "Olá, Polly!"
```

### Alternativa: Usando pip com venv

```bash
# Clone o repositório
git clone https://github.com/rafabez/polly.git
cd polly

# Crie ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instale Polly
pip install .

# Teste a instalação
polly --version

# Para usar Polly no sistema todo, crie um symlink:
sudo ln -s $(pwd)/venv/bin/polly /usr/local/bin/polly
```

### Para Desenvolvimento

```bash
# Clone e instale em modo editável
git clone https://github.com/rafabez/polly.git
cd polly

python3 -m venv venv
source venv/bin/activate
pip install -e .

# Agora você pode editar o código e testar imediatamente
polly --version
```

## Uso Rápido

### Uso Básico

```bash
# Fazer uma pergunta
polly "O que é recursão?"

# Obter um comando Linux
polly -c "listar todos os arquivos modificados hoje"

# Explicar um arquivo
polly -e script.sh

# Debug de código ou erros
cat error.log | polly -d

# Modo interativo
polly -i
```

### Modos Disponíveis

| Flag | Modo | Descrição |
|------|------|-----------|
| `-e, --explain FILE` | Explicar | Explica conteúdo de arquivo |
| `-c[N], --command [N]` | Comando | Obtém comando Linux/bash (use `-c3` para 3 versões) |
| `-ce, --command-explain` | Comando + Explicação | Obtém comando com explicações |
| `-d, --debug [FILE]` | Debug | Analisa e debugga código/erros (de arquivo ou pipe) |
| `-r, --refactor [FILE]` | Refatorar | Obtém sugestões de melhoria de código (de arquivo ou pipe) |
| `-t, --translate LANG` | Traduzir | Traduz texto para outro idioma |
| `-tf LANG FILE` | Traduzir Arquivo | Traduz conteúdo de arquivo para outro idioma |
| `-i, --interactive` | Interativo | Inicia modo chat com contexto |
| `-x, --motivational` | Motivacional | Obtém frase desmotivacional engraçada 😄 |

### Seleção de Modelo

```bash
# Usar modelo específico
polly --model gemini "Explique computação quântica"

# Listar modelos disponíveis
polly --list-models

# Definir modelo padrão
polly --set-default-model openai-large
```

### Modelos Disponíveis

- **gemini** - Gemini 2.5 Flash Lite (padrão, melhor janela de contexto)
- **openai** - OpenAI GPT-5 Nano (rápido)
- **openai-large** - OpenAI GPT-4.1 (mais capaz)
- **deepseek** - DeepSeek V3.1 (raciocínio avançado)
- **qwen-coder** - Qwen 2.5 Coder 32B (especializado em código)
- **mistral** - Mistral Small 3.2 24B (balanceado)
- **gemini-search** - Gemini com Google Search

### Opções Avançadas

```bash
# Controlar criatividade (0.0-3.0)
polly --temperature 1.5 "Escreva um poema criativo"

# Habilitar streaming
polly -s "Conte uma história longa"

# Salvar saída em arquivo
polly -o resposta.txt "Explique Docker"

# Saída JSON
polly --json "O que é Linux?"

# Pipe de outros comandos
cat script.py | polly -d "Encontre bugs neste código"
echo "Olá mundo" | polly -t "Inglês"
```

## Exemplos de Uso

### Geração de Comandos

```bash
# Obter apenas o comando
$ polly -c "encontrar todos os arquivos Python maiores que 1MB"
find . -name "*.py" -size +1M

# Obter comando com explicação
$ polly -ce "comprimir todos os logs com mais de 30 dias"
find /var/log -name "*.log" -mtime +30 -exec gzip {} \;

Explicação:
- find /var/log: Busca no diretório de logs
- -name "*.log": Corresponde a arquivos de log
- -mtime +30: Modificados há mais de 30 dias
- -exec gzip {} \;: Comprime cada arquivo encontrado
```

### Explicação de Código

```bash
# Explicar um script
$ polly -e deploy.sh

# Explicar código via pipe
$ cat funcao_complexa.py | polly -e
```

### Debugging

```bash
# Debug de logs de erro
$ cat error.log | polly -d

# Debug de código diretamente
$ polly -d "$(cat script_bugado.sh)"
```

### Modo Interativo

```bash
$ polly -i
Modo interativo - Digite 'exit' ou 'quit' para sair, 'clear' para resetar contexto

[Modelo: gemini, Temperatura: 0.7]

Você: Como eu listo processos em execução?
Polly: Você pode usar o comando `ps`...

Você: E para filtrar por nome?
Polly: Você pode usar `ps aux | grep nome_processo`...

Você: exit
Info: Até logo!
```

### Tradução

```bash
$ polly -t Inglês "Olá, como você está?"
Hello, how are you?

$ echo "Bom dia" | polly -t Espanhol
Buenos días
```

## Configuração

Polly armazena configuração em `~/.config/polly/config.yaml`

```bash
# Ver configuração atual
polly --config

# Definir modelo padrão
polly --set-default-model gemini

# Definir idioma padrão para prompts
polly --set-language pt

# Resetar para padrões
polly --reset-config

# Ver versão
polly -v
```

### Exemplo de Arquivo de Configuração

```yaml
default_model: gemini
temperature: 0.7
stream: false
referrer: deepentest.com
language: pt  # pt, en, portuguese, english
```

## Requisitos

- Python 3.8 ou superior
- Conexão com internet (para chamadas de API)

## Contribuindo

Contribuições são bem-vindas! Por favor, sinta-se à vontade para enviar um Pull Request.

1. Faça fork do repositório
2. Crie sua branch de feature (`git checkout -b feature/funcionalidade-incrivel`)
3. Commit suas mudanças (`git commit -m 'Adiciona funcionalidade incrível'`)
4. Push para a branch (`git push origin feature/funcionalidade-incrivel`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Agradecimentos

- Alimentado por [Pollinations.ai](https://pollinations.ai) - API gratuita de IA
- Construído para a comunidade de desenvolvedores

## Reportar Bugs & Solicitar Funcionalidades

Por favor, use a página de [GitHub Issues](https://github.com/rafabez/polly/issues) para reportar bugs ou solicitar funcionalidades.

## Recursos Adicionais

- [Documentação da API Pollinations.ai](https://github.com/pollinations/pollinations/blob/main/APIDOCS.md)
- [Modelos Disponíveis](https://text.pollinations.ai/models)
