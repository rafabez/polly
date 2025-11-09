# 🚀 Release Checklist - Polly AI

## Antes de Criar uma Release

### 1. Atualizar Versão
- [ ] Atualizar `__version__` em `polly/__init__.py`
- [ ] Atualizar `version` em `setup.py`
- [ ] Atualizar `version` em `pyproject.toml`
- [ ] Atualizar `pkgver` em `PKGBUILD`

### 2. Atualizar Documentação
- [ ] Atualizar `CHANGELOG.md` com mudanças da versão
- [ ] Revisar `README.md` e `README.pt-BR.md`
- [ ] Verificar exemplos no help (`polly --help`)

### 3. Testes
- [ ] Testar todos os modos: `-e`, `-c`, `-ce`, `-d`, `-r`, `-t`, `-i`, `-x`
- [ ] Testar com diferentes modelos
- [ ] Testar pipe: `cat file | polly`
- [ ] Testar flags: `-v`, `--help`, `--list-models`
- [ ] Testar configuração: `--set-language`, `--set-default-model`
- [ ] Testar múltiplas versões: `polly -c3 'comando'`

### 4. Código
- [ ] Código limpo e sem TODOs pendentes
- [ ] Sem warnings ou erros
- [ ] Dependências atualizadas em `requirements.txt`

## Criar Release

### 1. Commit e Tag
```bash
# Commit final
git add .
git commit -m "Release v0.1.0"

# Criar tag
git tag -a v0.1.0 -m "Release v0.1.0 - Initial public release"

# Push
git push origin main
git push origin v0.1.0
```

### 2. GitHub Release
1. Ir para: https://github.com/rafabez/polly/releases/new
2. Selecionar tag: `v0.1.0`
3. Título: `Polly AI v0.1.0`
4. Descrição: Copiar do CHANGELOG.md
5. Publicar release

### 3. Calcular SHA256
```bash
# Baixar tarball da release
wget https://github.com/rafabez/polly/archive/v0.1.0.tar.gz

# Calcular hash
sha256sum v0.1.0.tar.gz

# Atualizar PKGBUILD com o hash
```

### 4. Atualizar AUR
```bash
# Atualizar sha256sums no PKGBUILD
# Gerar .SRCINFO
makepkg --printsrcinfo > .SRCINFO

# Commit e push para AUR
cd polly-aur
cp ../polly/PKGBUILD .
cp ../polly/.SRCINFO .
git add PKGBUILD .SRCINFO
git commit -m "Update to v0.1.0"
git push origin master
```

## Pós-Release

- [ ] Anunciar no forum BigLinux
- [ ] Anunciar no Telegram BigLinux
- [ ] Atualizar documentação se necessário
- [ ] Monitorar issues no GitHub
- [ ] Monitorar comentários no AUR

## Versões Futuras

### v0.2.0 (Planejado)
- [ ] Modo de histórico de conversas
- [ ] Cache de respostas
- [ ] Suporte a mais idiomas
- [ ] Configuração de timeout customizável

### v0.3.0 (Futuro)
- [ ] Plugin system
- [ ] Integração com editores (vim, nano)
- [ ] Modo offline com modelos locais
