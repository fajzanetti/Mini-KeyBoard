#!/bin/sh
# Gera dist/mini-keyboard_<versão>_all.deb. Uso: packaging/build-deb.sh <versão>
set -eu

version="$1"
root="$(cd "$(dirname "$0")/.." && pwd)"
package="$(mktemp -d)"
trap 'rm -rf "$package"' EXIT

install -Dm644 -t "$package/usr/share/mini-keyboard/mini_keyboard" \
    "$root"/mini_keyboard/*.py "$root/mini_keyboard/style.css"
install -Dm755 -t "$package/usr/bin" "$root/packaging/mini-keyboard"
install -Dm644 -t "$package/usr/lib/udev/rules.d" "$root/udev/70-mini-keyboard.rules"
install -Dm644 -t "$package/usr/share/applications" "$root/packaging/local.MiniKeyboard.desktop"
install -Dm644 -t "$package/usr/share/icons/hicolor/scalable/apps" \
    "$root/packaging/local.MiniKeyboard.svg"
install -Dm755 -t "$package/DEBIAN" "$root/packaging/debian/postinst"
sed "s/@VERSION@/$version/" "$root/packaging/debian/control" > "$package/DEBIAN/control"

mkdir -p "$root/dist"
# O mktemp cria a pasta sem leitura para outros usuários. O pacote precisa da permissão padrão.
chmod 755 "$package"
dpkg-deb --build --root-owner-group "$package" "$root/dist/mini-keyboard_${version}_all.deb"
