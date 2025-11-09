# Maintainer: Interzone (Rafael Beznos) <rafabez@github>
pkgname=polly-ai
pkgver=0.1.0
pkgrel=1
pkgdesc="AI Assistant for Linux Terminal powered by Pollinations.ai"
arch=('any')
url="https://github.com/rafabez/polly"
license=('MIT')
depends=('python' 'python-requests' 'python-rich' 'python-yaml')
makedepends=('python-setuptools' 'python-build' 'python-installer' 'python-wheel')
source=("$pkgname-$pkgver.tar.gz::https://github.com/rafabez/polly/archive/v$pkgver.tar.gz")
sha256sums=('SKIP')  # Atualizar com o hash real após criar a release

build() {
    cd "$srcdir/polly-$pkgver"
    python -m build --wheel --no-isolation
}

package() {
    cd "$srcdir/polly-$pkgver"
    python -m installer --destdir="$pkgdir" dist/*.whl
    
    # Instalar licença
    install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
    
    # Instalar documentação
    install -Dm644 README.md "$pkgdir/usr/share/doc/$pkgname/README.md"
    install -Dm644 README.pt-BR.md "$pkgdir/usr/share/doc/$pkgname/README.pt-BR.md"
}
