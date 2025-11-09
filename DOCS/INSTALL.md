# 📦 Instalação do Polly

Guia completo de instalação do Polly no seu sistema Linux.

## 🎯 Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Git (para clonar o repositório)
- Conexão com internet

## 🚀 Método 1: Instalação Rápida (Recomendado para Testes)

Este método instala o Polly no seu ambiente Python do usuário:

```bash
# 1. Clone o repositório
cd ~/Github
git clone https://github.com/rafabez/polly.git
cd polly

# 2. Instale as dependências e o programa
pip install --user -e .

# 3. Teste a instalação
polly --version
polly "Olá, Polly!"
```

**Nota**: O flag `-e` instala em modo "editável", permitindo modificar o código e testar imediatamente.

## 🔧 Método 2: Instalação em Ambiente Virtual (Desenvolvimento)

Ideal para desenvolvimento e testes isolados:

```bash
# 1. Clone o repositório
cd ~/Github
git clone https://github.com/rafabez/polly.git
cd polly

# 2. Crie um ambiente virtual
python3 -m venv venv

# 3. Ative o ambiente virtual
source venv/bin/activate

# 4. Instale o Polly
pip install -e .

# 5. Teste
polly --version
polly "teste"

# Para desativar o ambiente virtual
deactivate
```

**Nota**: Você precisará ativar o ambiente virtual toda vez que quiser usar o Polly.

## 🌍 Método 3: Instalação Global do Sistema

Para disponibilizar o Polly para todos os usuários:

```bash
# 1. Clone o repositório
cd ~/Github
git clone https://github.com/rafabez/polly.git
cd polly

# 2. Instale globalmente (requer sudo)
sudo pip install .

# 3. Teste
polly --version
```

**Aviso**: Instalação global pode causar conflitos com pacotes do sistema. Use com cuidado.

## 📍 Verificando a Instalação

Após instalar, verifique se o comando está disponível:

```bash
# Verificar versão
polly --version

# Verificar localização do executável
which polly

# Listar modelos disponíveis
polly --list-models

# Teste rápido
polly "O que é Linux?"
```

## 🔍 Solução de Problemas

### Problema: Comando `polly` não encontrado

**Solução 1**: Adicione o diretório de scripts Python ao PATH

```bash
# Adicione ao seu ~/.bashrc ou ~/.zshrc
export PATH="$HOME/.local/bin:$PATH"

# Recarregue o shell
source ~/.bashrc  # ou source ~/.zshrc
```

**Solução 2**: Verifique onde o pip instalou

```bash
pip show polly-ai
python3 -m site --user-base
```

### Problema: Erro de permissão ao instalar

```bash
# Use --user para instalar no diretório do usuário
pip install --user -e .

# OU use sudo para instalação global (não recomendado)
sudo pip install .
```

### Problema: Dependências não instaladas

```bash
# Instale as dependências manualmente
pip install requests rich pyyaml

# Depois instale o Polly
pip install -e .
```

### Problema: Versão do Python muito antiga

```bash
# Verifique sua versão do Python
python3 --version

# Se for menor que 3.8, atualize:
# Ubuntu/Debian
sudo apt update
sudo apt install python3.10

# Fedora
sudo dnf install python3.10
```

## 🎨 Configuração Inicial

Após instalar, configure o Polly:

```bash
# Ver configuração atual
polly --config

# Definir modelo padrão
polly --set-default-model gemini

# Testar modo interativo
polly -i
```

## 🔄 Atualizando o Polly

Se você instalou com `-e` (modo editável):

```bash
cd ~/Github/polly
git pull origin main
# As mudanças são aplicadas automaticamente
```

Se você instalou sem `-e`:

```bash
cd ~/Github/polly
git pull origin main
pip install --user --upgrade .
```

## 🗑️ Desinstalação

Para remover o Polly:

```bash
# Desinstalar o pacote
pip uninstall polly-ai

# Remover configurações (opcional)
rm -rf ~/.config/polly

# Remover o repositório (opcional)
rm -rf ~/Github/polly
```

## 📦 Criando Pacote .deb (BigLinux)

Para criar um pacote Debian:

```bash
cd ~/Github/polly

# Instale ferramentas necessárias
sudo apt install python3-stdeb dh-python

# Crie o pacote
python3 setup.py --command-packages=stdeb.command bdist_deb

# O pacote .deb estará em deb_dist/
ls deb_dist/*.deb

# Instale o pacote
sudo dpkg -i deb_dist/python3-polly-ai_*.deb
```

## 🎯 Próximos Passos

Após instalar com sucesso:

1. Leia o [README.md](README.md) para exemplos de uso
2. Teste os diferentes modos: `-e`, `-c`, `-d`, `-i`
3. Configure seu modelo preferido
4. Explore as opções com `polly --help`

## 💡 Dicas

- **Para desenvolvimento**: Use instalação com `-e` em ambiente virtual
- **Para testes diários**: Use instalação `--user`
- **Para produção**: Crie pacote .deb para BigLinux

## 📞 Ajuda

Se encontrar problemas:

1. Verifique os logs: `polly -v "teste"`
2. Consulte o [CONTRIBUTING.md](CONTRIBUTING.md)
3. Abra uma issue no GitHub

---

Boa instalação! 🚀
