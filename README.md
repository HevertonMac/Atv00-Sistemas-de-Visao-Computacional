# Atv00 — Interface Gráfica

## Como executar

```bash
python atv00.py
```

> **Requisito:** Python 3.10+ com as bibliotecas `Pillow` e `numpy`.
>
> ```bash
> pip install pillow numpy
> ```

## Funcionalidades implementadas

| Função | Atalho / Botão |
|---|---|
| Carregar e exibir imagem | `Ctrl+O` · botão **Abrir Imagem** · menu *Arquivo* |
| Salvar imagem | `Ctrl+S` · botão **Salvar Imagem** · menu *Arquivo* |
| Zerar todos os pixels (→ preto) | botão **Zerar Pixels** · menu *Editar* |
| Restaurar imagem original | `Ctrl+Z` · botão **Restaurar Original** · menu *Editar* |

## Estrutura do código

```
VCApp (tk.Tk)
├── _build_menu()      # Menu bar + atalhos de teclado
├── _build_layout()    # Sidebar, canvas, barra de status
├── cmd_open()         # Carrega imagem com filedialog
├── cmd_save()         # Salva imagem com filedialog
├── cmd_zero()         # Zera todos os pixels via numpy
├── cmd_restore()      # Restaura cópia da imagem original
└── _refresh_canvas()  # Re-renderiza respeitando o tamanho da janela
```
