"""
Atividade Prática 00 - Interface Gráfica
Disciplina: Sistemas de Visão Computacional
Autor: Heverton Macedo <heverton.macedo@ufpi.edu.br>
VipLab UFPI

Interface gráfica que serve como casca para receber implementações
de algoritmos de visão computacional futuros.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import os


# ─────────────────────────────────────────────
# Constantes de estilo
# ─────────────────────────────────────────────
BG_DARK   = "#1e1e2e"
BG_PANEL  = "#2a2a3e"
BG_BTN    = "#3d3d5c"
BG_BTN_HL = "#5c5c8a"
FG_TEXT   = "#cdd6f4"
FG_DIM    = "#7c7fa8"
ACCENT    = "#89b4fa"
DANGER    = "#f38ba8"
SUCCESS   = "#a6e3a1"
FONT_MAIN = ("Segoe UI", 10)
FONT_H1   = ("Segoe UI", 13, "bold")
FONT_MONO = ("Consolas", 9)


class VCApp(tk.Tk):
    """Janela principal da aplicação de Visão Computacional."""

    def __init__(self):
        super().__init__()
        self.title("Visão Computacional — VipLab UFPI")
        self.geometry("1100x700")
        self.minsize(800, 550)
        self.configure(bg=BG_DARK)

        # Estado interno
        self._original_image: Image.Image | None = None  # PIL original
        self._current_image: Image.Image | None  = None  # PIL atual (exibida)
        self._photo: ImageTk.PhotoImage | None   = None  # referência anti-GC
        self._filepath: str | None               = None

        self._build_menu()
        self._build_layout()
        self._update_status("Nenhuma imagem carregada.")

    # ─────────────────────── UI ─────────────────────────

    def _build_menu(self):
        menubar = tk.Menu(self, bg=BG_PANEL, fg=FG_TEXT,
                          activebackground=BG_BTN_HL, activeforeground=FG_TEXT,
                          relief="flat", bd=0)

        # Arquivo
        m_file = tk.Menu(menubar, tearoff=0, bg=BG_PANEL, fg=FG_TEXT,
                         activebackground=BG_BTN_HL, activeforeground=FG_TEXT)
        m_file.add_command(label="Abrir imagem…   Ctrl+O", command=self.cmd_open)
        m_file.add_command(label="Salvar imagem…  Ctrl+S", command=self.cmd_save)
        m_file.add_separator()
        m_file.add_command(label="Sair            Alt+F4", command=self.destroy)
        menubar.add_cascade(label="Arquivo", menu=m_file)

        # Editar
        m_edit = tk.Menu(menubar, tearoff=0, bg=BG_PANEL, fg=FG_TEXT,
                         activebackground=BG_BTN_HL, activeforeground=FG_TEXT)
        m_edit.add_command(label="Zerar pixels        (→ preto)", command=self.cmd_zero)
        m_edit.add_command(label="Restaurar original  Ctrl+Z",    command=self.cmd_restore)
        menubar.add_cascade(label="Editar", menu=m_edit)

        # Ajuda
        m_help = tk.Menu(menubar, tearoff=0, bg=BG_PANEL, fg=FG_TEXT,
                         activebackground=BG_BTN_HL, activeforeground=FG_TEXT)
        m_help.add_command(label="Sobre", command=self._show_about)
        menubar.add_cascade(label="Ajuda", menu=m_help)

        self.config(menu=menubar)

        # Atalhos
        self.bind("<Control-o>", lambda e: self.cmd_open())
        self.bind("<Control-s>", lambda e: self.cmd_save())
        self.bind("<Control-z>", lambda e: self.cmd_restore())

    def _build_layout(self):
        # ── Barra lateral esquerda ──────────────────────
        sidebar = tk.Frame(self, bg=BG_PANEL, width=210)
        sidebar.pack(side="left", fill="y", padx=(10, 4), pady=10)
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="⚙  Ferramentas", font=FONT_H1,
                 bg=BG_PANEL, fg=ACCENT).pack(pady=(14, 10))

        ttk.Separator(sidebar, orient="horizontal").pack(fill="x", padx=10)

        btn_cfg = dict(font=FONT_MAIN, bg=BG_BTN, fg=FG_TEXT,
                       activebackground=BG_BTN_HL, activeforeground=FG_TEXT,
                       relief="flat", bd=0, cursor="hand2",
                       width=22, pady=8)

        tk.Button(sidebar, text="📂  Abrir Imagem",
                  command=self.cmd_open, **btn_cfg).pack(pady=(12, 4), padx=12)

        tk.Button(sidebar, text="💾  Salvar Imagem",
                  command=self.cmd_save, **btn_cfg).pack(pady=4, padx=12)

        ttk.Separator(sidebar, orient="horizontal").pack(fill="x", padx=10, pady=8)

        tk.Label(sidebar, text="Operações", font=("Segoe UI", 9, "italic"),
                 bg=BG_PANEL, fg=FG_DIM).pack()

        tk.Button(sidebar, text="⬛  Zerar Pixels",
                  command=self.cmd_zero,
                  **{**btn_cfg, "bg": "#4a2a3e",
                     "activebackground": DANGER}).pack(pady=4, padx=12)

        tk.Button(sidebar, text="↩  Restaurar Original",
                  command=self.cmd_restore,
                  **{**btn_cfg, "bg": "#2a4a3e",
                     "activebackground": SUCCESS}).pack(pady=4, padx=12)

        # ── Info da imagem ──────────────────────────────
        ttk.Separator(sidebar, orient="horizontal").pack(fill="x", padx=10, pady=8)
        tk.Label(sidebar, text="Informações", font=("Segoe UI", 9, "italic"),
                 bg=BG_PANEL, fg=FG_DIM).pack()

        self._info_var = tk.StringVar(value="—")
        tk.Label(sidebar, textvariable=self._info_var, font=FONT_MONO,
                 bg=BG_PANEL, fg=FG_TEXT, justify="left",
                 wraplength=190).pack(pady=6, padx=12, anchor="w")

        # ── Área central: canvas de imagem ─────────────
        center = tk.Frame(self, bg=BG_DARK)
        center.pack(side="left", fill="both", expand=True, padx=(4, 10), pady=10)

        canvas_frame = tk.Frame(center, bg=BG_PANEL, bd=0, relief="flat")
        canvas_frame.pack(fill="both", expand=True)

        self._canvas = tk.Canvas(canvas_frame, bg="#111118",
                                 highlightthickness=0, cursor="crosshair")
        self._canvas.pack(fill="both", expand=True)
        self._canvas.bind("<Configure>", self._on_canvas_resize)

        # Placeholder
        self._placeholder_id = self._canvas.create_text(
            400, 300,
            text="Abra uma imagem para começar\n(Ctrl+O ou menu Arquivo → Abrir)",
            fill=FG_DIM, font=("Segoe UI", 13), anchor="center", justify="center"
        )

        # ── Barra de status ─────────────────────────────
        self._status_var = tk.StringVar()
        status_bar = tk.Label(self, textvariable=self._status_var,
                              font=FONT_MONO, bg="#141420", fg=FG_DIM,
                              anchor="w", padx=10, pady=4)
        status_bar.pack(side="bottom", fill="x")

    # ─────────────────────── Comandos ───────────────────

    def cmd_open(self):
        """Carrega e exibe uma imagem do disco."""
        path = filedialog.askopenfilename(
            title="Abrir imagem",
            filetypes=[
                ("Imagens", "*.png *.jpg *.jpeg *.bmp *.tiff *.tif *.gif *.webp"),
                ("Todos os arquivos", "*.*"),
            ]
        )
        if not path:
            return

        try:
            img = Image.open(path).convert("RGB")
        except Exception as exc:
            messagebox.showerror("Erro ao abrir", str(exc))
            return

        self._filepath = path
        self._original_image = img.copy()
        self._current_image  = img.copy()
        self._refresh_canvas()
        self._update_info()
        self._update_status(f"Imagem carregada: {os.path.basename(path)}")

    def cmd_save(self):
        """Salva a imagem atual no disco."""
        if self._current_image is None:
            messagebox.showwarning("Aviso", "Nenhuma imagem para salvar.")
            return

        default_name = os.path.basename(self._filepath) if self._filepath else "imagem.png"
        path = filedialog.asksaveasfilename(
            title="Salvar imagem",
            initialfile=default_name,
            defaultextension=".png",
            filetypes=[
                ("PNG",  "*.png"),
                ("JPEG", "*.jpg *.jpeg"),
                ("BMP",  "*.bmp"),
                ("TIFF", "*.tiff *.tif"),
                ("Todos os arquivos", "*.*"),
            ]
        )
        if not path:
            return

        try:
            self._current_image.save(path)
            self._update_status(f"Imagem salva em: {path}")
        except Exception as exc:
            messagebox.showerror("Erro ao salvar", str(exc))

    def cmd_zero(self):
        """Atribui intensidade 0 a todos os pixels (imagem preta)."""
        if self._current_image is None:
            messagebox.showwarning("Aviso", "Nenhuma imagem carregada.")
            return

        arr = np.array(self._current_image)
        arr[:] = 0
        self._current_image = Image.fromarray(arr.astype(np.uint8))
        self._refresh_canvas()
        self._update_info()
        self._update_status("Pixels zerados — imagem totalmente preta.")

    def cmd_restore(self):
        """Restaura a imagem ao estado original carregado."""
        if self._original_image is None:
            messagebox.showwarning("Aviso", "Nenhuma imagem original disponível.")
            return

        self._current_image = self._original_image.copy()
        self._refresh_canvas()
        self._update_info()
        self._update_status("Imagem restaurada ao estado original.")

    # ─────────────────────── Helpers ────────────────────

    def _refresh_canvas(self):
        """Redesenha a imagem atual no canvas, ajustando ao tamanho disponível."""
        if self._current_image is None:
            return

        # Remove placeholder
        self._canvas.delete(self._placeholder_id)

        cw = self._canvas.winfo_width()  or 800
        ch = self._canvas.winfo_height() or 600

        img = self._current_image.copy()
        img.thumbnail((cw, ch), Image.LANCZOS)

        self._photo = ImageTk.PhotoImage(img)
        self._canvas.delete("img")
        self._canvas.create_image(cw // 2, ch // 2,
                                  anchor="center", image=self._photo, tags="img")

    def _on_canvas_resize(self, event):
        """Re-renderiza ao redimensionar a janela."""
        if self._current_image is not None:
            self._refresh_canvas()

    def _update_info(self):
        if self._current_image is None:
            self._info_var.set("—")
            return
        w, h = self._current_image.size
        mode = self._current_image.mode
        arr  = np.array(self._current_image)
        text = (f"Tamanho : {w} × {h} px\n"
                f"Modo    : {mode}\n"
                f"Canais  : {arr.shape[2] if arr.ndim == 3 else 1}\n"
                f"Mín     : {arr.min()}\n"
                f"Máx     : {arr.max()}\n"
                f"Média   : {arr.mean():.1f}")
        self._info_var.set(text)

    def _update_status(self, msg: str):
        self._status_var.set(f"  {msg}")

    def _show_about(self):
        messagebox.showinfo(
            "Sobre",
            "Atividade Prática 00 — Interface Gráfica\n"
            "Disciplina: Sistemas de Visão Computacional\n\n"
            "VipLab UFPI\n"
            "Autor: Heverton Macedo"
        )


# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = VCApp()
    app.mainloop()
