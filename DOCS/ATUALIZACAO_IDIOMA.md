# 🌍 Atualização: Suporte a Idiomas nos Prompts

## ✨ Nova Funcionalidade

Agora o Polly suporta **prompts em Português e Inglês**!

## 🎯 Como Usar

### Opção 1: Configurar Idioma Padrão (Recomendado)

```bash
# Definir português como padrão (já é o padrão)
polly --set-language pt

# Ou definir inglês
polly --set-language en

# Ver configuração atual
polly --config
```

### Opção 2: Usar Flag em Cada Comando

```bash
# Usar em português (padrão)
polly -l pt -ce "listar arquivos modificados hoje"

# Usar em inglês
polly -l en -ce "list files modified today"
```

## 📝 Idiomas Disponíveis

- **`pt`** - Português (padrão)
- **`pt-br`** - Português Brasil (mesmo que pt)
- **`portuguese`** - Português (alias)
- **`en`** - English
- **`english`** - English (alias)

## 🔧 Exemplos

### Comando com Explicação em Português

```bash
$ polly -ce "comprimir todos os logs"
find /var/log -name "*.log" -exec gzip {} \;

Explicação:
- find /var/log: Busca no diretório de logs
- -name "*.log": Corresponde a arquivos de log
- -exec gzip {} \;: Comprime cada arquivo encontrado
```

### Comando com Explicação em Inglês

```bash
$ polly -l en -ce "compress all logs"
find /var/log -name "*.log" -exec gzip {} \;

Explanation:
- find /var/log: Search in log directory
- -name "*.log": Match log files
- -exec gzip {} \;: Compress each file found
```

## ⚙️ Configuração

O idioma é salvo em `~/.config/polly/config.yaml`:

```yaml
default_model: gemini
temperature: 0.7
max_tokens: 2000
stream: false
referrer: interzonesec.com
language: pt  # <-- Idioma dos prompts
```

## 🚀 Para Atualizar

Se você já tinha o Polly instalado:

```bash
cd /home/max/Github/polly

# Se instalou com pipx
pipx upgrade polly

# Se instalou com venv
source venv/bin/activate
pip install -e . --upgrade

# Testar
polly --config
polly -ce "listar arquivos grandes"
```

## 📚 Modos Afetados

Todos os modos agora respeitam o idioma configurado:

- ✅ **Explain** (-e) - Explicações em PT ou EN
- ✅ **Command** (-c) - Comandos (sempre bash, mas prompts em PT/EN)
- ✅ **Command Explain** (-ce) - Comandos com explicações em PT ou EN
- ✅ **Debug** (-d) - Análise de erros em PT ou EN
- ✅ **Refactor** (-r) - Sugestões em PT ou EN
- ✅ **Interactive** (-i) - Chat em PT ou EN
- ✅ **Default** - Perguntas gerais em PT ou EN

## 🎉 Pronto!

Agora você pode usar o Polly completamente em português! 🇧🇷

---

**Nota**: O modo **Translate** (-t) não é afetado, pois ele já traduz para o idioma especificado.
