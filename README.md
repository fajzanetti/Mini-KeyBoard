# Mini Keyboard

App GTK4 que configura o mini teclado CH57x (USB `1189:8840` e `1189:8842`).
O app lê o número de teclas, o número de knobs e o mapeamento gravado no mini teclado.
O app lê e grava pela biblioteca `hidapi`, sem ferramenta externa.

## Instalação

1. Instale as dependências:

   ```sh
   sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 python3-yaml libhidapi-hidraw0
   ```

2. Instale a regra `udev`. Ela libera a leitura e a gravação do mini teclado para o seu usuário:

   ```sh
   sudo cp udev/70-mini-keyboard.rules /etc/udev/rules.d/
   sudo udevadm control --reload
   sudo udevadm trigger --subsystem-match=usb --subsystem-match=hidraw
   ```

## Uso

```sh
python3 -m mini_keyboard
```

O app lê o mapeamento gravado no mini teclado quando abre.
O botão **Ler do teclado** repete a leitura.

1. Escolha a camada.
2. Clique em uma tecla ou em uma ação do knob.
3. Digite a ação, capture um atalho ou escolha uma ação pronta.
4. Escolha o modo e a cor do LED da camada.
5. Clique em **Gravar no teclado**.

O app salva o mapeamento em `~/.config/mini-keyboard/mapping.yaml`.
O app mostra o mapeamento salvo quando a leitura falha.

## Limites

- A leitura substitui as ações da tela. Grave as suas mudanças antes de ler ou de fechar o app.
- Alguns mini teclados `1189:8840` não respondem ao pedido de leitura. Para eles, o app usa o formato de 6 teclas e 1 knob.
- O mini teclado não informa as linhas e as colunas. O app conhece os formatos de 6, 9, 12 e 15 teclas.
- O app mostra um número de teclas diferente em uma linha única.
- Uma posição vazia (`—`) não tem ação gravada, ou tem uma ação que a sintaxe não cobre.
- A gravação mantém a ação de uma posição vazia.
- O mini teclado não informa o modo de LED. O app mostra o modo salvo no arquivo.
- O modo **Não alterar** mantém o LED que já está gravado no mini teclado.
- O GNOME intercepta alguns atalhos, como `Super` e `Alt+Tab`. Digite esses atalhos no campo de texto (`win-d`, `alt-tab`).
- A sintaxe das ações é a do ch57x-keyboard-tool. Veja a [documentação da sintaxe](https://github.com/kriomant/ch57x-keyboard-tool/blob/654953c0169fb3bb57d130758663c43cc306cdf7/doc/actions.md).
- A gravação direta foi testada em um `1189:8840` de 6 teclas. A persistência depois de reconectar o cabo ainda não foi confirmada.
