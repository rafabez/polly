# 🚀 Quick Start - Polly

## Instalação Rápida (SIGA ESTES PASSOS)

```bash
# 1. Entre no diretório do projeto
cd /home/max/Github/polly

# 2. Instale o Polly em modo desenvolvimento
pip install --user -e .

# 3. Verifique se funcionou
polly --version

# 4. Se o comando não for encontrado, adicione ao PATH:
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# 5. Teste novamente
polly --version
```

## ✅ Primeiros Testes

```bash
# Ver ajuda
polly --help

# Listar modelos disponíveis
polly --list-models

# Pergunta simples
polly "O que é Linux?"

# Comando bash
polly -c "listar arquivos modificados hoje"

# Comando com explicação
polly -ce "comprimir todos os logs"

# Explicar um arquivo
polly -e ~/.bashrc

# Modo interativo
polly -i
```

## 🎯 Testes Automáticos

```bash
# Rodar todos os testes de exemplo
bash examples/test_examples.sh

# Ou usando make
make test
```

## ⚙️ Configuração

```bash
# Ver configuração atual
polly --config

# Definir modelo padrão
polly --set-default-model gemini

# Resetar configuração
polly --reset-config
```

## 🔍 Verificação de Problemas

Se algo não funcionar:

```bash
# 1. Verificar se está instalado
pip show polly-ai

# 2. Verificar localização
which polly

# 3. Verificar PATH
echo $PATH | grep ".local/bin"

# 4. Reinstalar
pip uninstall polly-ai
pip install --user -e .
```

## 📚 Próximos Passos

- Leia o [README.md](README.md) completo
- Veja [INSTALL.md](INSTALL.md) para mais opções de instalação
- Contribua! Veja [CONTRIBUTING.md](CONTRIBUTING.md)

---

**Pronto para testar!** 🎉
