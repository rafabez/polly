# 📦 Guia de Empacotamento para AUR (Arch User Repository)

## 🎯 Pré-requisitos

1. **Conta no AUR**: https://aur.archlinux.org/register
2. **Configurar SSH**: Adicionar sua chave SSH pública na conta AUR
3. **Ferramentas necessárias**:
   ```bash
   sudo pacman -S base-devel git
   ```

## 📋 Passo a Passo para Publicar no AUR

### 1️⃣ Criar Release no GitHub

Primeiro, crie uma release no GitHub:

```bash
cd /home/max/Github/polly

# Criar tag
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0

# Ou criar release pela interface do GitHub:
# https://github.com/rafabez/polly/releases/new
```

### 2️⃣ Atualizar SHA256SUM no PKGBUILD

Após criar a release, baixe o tarball e calcule o hash:

```bash
# Baixar o tarball
wget https://github.com/rafabez/polly/archive/v0.1.0.tar.gz

# Calcular SHA256
sha256sum v0.1.0.tar.gz

# Copiar o hash e atualizar no PKGBUILD (linha sha256sums)
```

### 3️⃣ Testar o PKGBUILD Localmente

```bash
# Testar build
makepkg -si

# Se funcionar, limpar
makepkg --clean
```

### 4️⃣ Gerar .SRCINFO

```bash
# Gerar arquivo .SRCINFO (necessário para AUR)
makepkg --printsrcinfo > .SRCINFO
```

### 5️⃣ Clonar Repositório AUR

```bash
# Clonar repositório vazio do AUR
git clone ssh://aur@aur.archlinux.org/polly-ai.git polly-aur
cd polly-aur

# Copiar arquivos necessários
cp ../polly/PKGBUILD .
cp ../polly/.SRCINFO .

# Adicionar e commitar
git add PKGBUILD .SRCINFO
git commit -m "Initial commit: polly-ai v0.1.0"

# Enviar para AUR
git push origin master
```

### 6️⃣ Verificar no AUR

Acesse: https://aur.archlinux.org/packages/polly-ai

## 🔄 Atualizar Versão no AUR

Quando lançar uma nova versão:

```bash
cd polly-aur

# 1. Atualizar pkgver no PKGBUILD
# 2. Incrementar pkgrel (ou resetar para 1 se mudou pkgver)
# 3. Atualizar sha256sums

# Gerar novo .SRCINFO
makepkg --printsrcinfo > .SRCINFO

# Commitar e enviar
git add PKGBUILD .SRCINFO
git commit -m "Update to v0.2.0"
git push origin master
```

## 🐧 Para BigLinux Especificamente

### Opção 1: Via AUR
1. Publique no AUR primeiro (passos acima)
2. Usuários BigLinux podem instalar com um AUR helper:
   ```bash
   yay -S polly-ai
   # ou
   paru -S polly-ai
   ```

### Opção 2: Repositório Oficial BigLinux
1. Entre em contato com a equipe BigLinux
2. Envie o PKGBUILD para análise
3. Eles podem incluir no repositório oficial

**Contatos BigLinux:**
- Forum: https://forum.biglinux.com.br/
- Telegram: https://t.me/biglinuxbr
- GitHub: https://github.com/biglinux

## 📝 Checklist Final

Antes de publicar no AUR:

- [ ] Release criada no GitHub (v0.1.0)
- [ ] SHA256 atualizado no PKGBUILD
- [ ] PKGBUILD testado localmente (`makepkg -si`)
- [ ] .SRCINFO gerado (`makepkg --printsrcinfo > .SRCINFO`)
- [ ] Conta AUR criada
- [ ] SSH configurado no AUR
- [ ] PKGBUILD e .SRCINFO commitados
- [ ] Push para AUR realizado

## 🎉 Pronto!

Seu pacote estará disponível em:
- **AUR**: https://aur.archlinux.org/packages/polly-ai
- **Instalação**: `yay -S polly-ai` ou `paru -S polly-ai`

## 📚 Recursos Úteis

- [AUR Submission Guidelines](https://wiki.archlinux.org/title/AUR_submission_guidelines)
- [PKGBUILD Guide](https://wiki.archlinux.org/title/PKGBUILD)
- [Arch Package Guidelines](https://wiki.archlinux.org/title/Arch_package_guidelines)
