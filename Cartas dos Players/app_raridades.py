
import os
import tkinter as tk
from PIL import Image, ImageTk

PASTA_IMAGENS = "imagens"
PASTA_BG = "backgrounds"
PASTAS_USUARIOS = ["KillerxG", "Leonardofake", "Imp", "Dartrian", "Angelo", "Misaki"]
RARIDADES = ["Comum", "Raro", "Super Raro", "Ultra Raro", "Secreta Rara", "Espirito"]

class AppImagemViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Cartas por Usuário e Raridade")
        self.root.state("zoomed")
        self.root.configure(bg="black")

        self.bg_image = None
        self.background_label = None
        self.carregar_fundo()

        self.frame_main = tk.Frame(root, bg="black")
        self.frame_main.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        for usuario in PASTAS_USUARIOS:
            for raridade in RARIDADES:
                os.makedirs(os.path.join(PASTA_IMAGENS, usuario, raridade), exist_ok=True)

        self.mostrar_menu_usuarios()
        self.root.bind("<Escape>", lambda e: self.root.destroy())

    def carregar_fundo(self):
        try:
            self.root.update_idletasks()
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            caminho_bg = os.path.join(PASTA_BG, "fundo.jpg")
            imagem = Image.open(caminho_bg).resize((screen_width, screen_height), Image.LANCZOS)
            self.bg_image = ImageTk.PhotoImage(imagem)
            self.background_label = tk.Label(self.root, image=self.bg_image)
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Erro ao carregar fundo: {e}")

    def limpar_tela(self):
        for widget in self.frame_main.winfo_children():
            widget.destroy()

    def mostrar_menu_usuarios(self):
        self.limpar_tela()
        tk.Label(self.frame_main, text="Selecione um usuário:", font=("Arial", 18), fg="red", bg="black").pack(pady=20)
        for nome in PASTAS_USUARIOS:
            btn = tk.Button(self.frame_main, text=nome, width=25, font=("Arial", 14),
                            fg="red", bg="black", activeforeground="red",
                            command=lambda n=nome: self.mostrar_menu_raridades(n))
            btn.pack(pady=8)

    def mostrar_menu_raridades(self, usuario):
        self.limpar_tela()
        tk.Label(self.frame_main, text=f"Raridades de {usuario}", font=("Arial", 18), fg="red", bg="black").pack(pady=20)

        for raridade in RARIDADES:
            btn = tk.Button(self.frame_main, text=raridade, width=25, font=("Arial", 14),
                            fg="red", bg="black", activeforeground="red",
                            command=lambda u=usuario, r=raridade: self.abrir_galeria(u, r))
            btn.pack(pady=5)

        btn_voltar = tk.Button(self.frame_main, text="← Voltar", font=("Arial", 12),
                               fg="red", bg="black", activeforeground="red",
                               command=self.mostrar_menu_usuarios)
        btn_voltar.pack(pady=20)

    def abrir_galeria(self, usuario, raridade):
        galeria = tk.Toplevel(self.root)
        galeria.title(f"{usuario} - {raridade}")
        galeria.state("zoomed")
        galeria.configure(bg="black")

        canvas = tk.Canvas(galeria, bg="black", highlightthickness=0)
        scrollbar = tk.Scrollbar(galeria, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        container = tk.Frame(canvas, bg="black")
        canvas_window = canvas.create_window((0, 0), window=container, anchor="nw")

        def _on_mousewheel(event):
            if event.num == 5 or event.delta == -120:
                canvas.yview_scroll(1, 'units')
            elif event.num == 4 or event.delta == 120:
                if canvas.yview()[0] > 0:
                    canvas.yview_scroll(-1, 'units')

        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        galeria.bind("<Escape>", lambda e: galeria.destroy())

        pasta = os.path.join(PASTA_IMAGENS, usuario, raridade)
        imagens = [os.path.join(pasta, f) for f in os.listdir(pasta) if f.lower().endswith(".jpg")]
        imagens.sort()
        imagens_tk = []

        if not imagens:
            tk.Label(container, text="Nenhuma imagem encontrada.", font=("Arial", 14), bg="black", fg="red").pack()
            return

        colunas = 12
        largura_padrao = 200
        largura_hover = 800

        zoom_preview = tk.Label(galeria, bg="black", bd=0)
        zoom_preview.place_forget()

        rows = (len(imagens) + colunas - 1) // colunas
        for r in range(rows):
            linha = tk.Frame(container, bg="black")
            linha.pack(anchor="center")
            for c in range(colunas):
                idx = r * colunas + c
                if idx >= len(imagens): break

                path = imagens[idx]
                img_normal = Image.open(path)
                img_normal.thumbnail((largura_padrao, largura_padrao))
                img_hover = Image.open(path)
                img_hover.thumbnail((largura_hover, largura_hover))

                img_normal_tk = ImageTk.PhotoImage(img_normal)
                img_hover_tk = ImageTk.PhotoImage(img_hover)

                imagens_tk.extend([img_normal_tk, img_hover_tk])

                quadro = tk.Frame(linha, bg="black", padx=4, pady=4)
                quadro.pack(side=tk.LEFT)

                label = tk.Label(quadro, image=img_normal_tk, bg="black")
                label.image_normal = img_normal_tk
                label.image_hover = img_hover_tk
                label.pack()

                def make_hover_handler(col_idx, hover):
                    def on_enter(event):
                        x_root = event.x_root - galeria.winfo_rootx()
                        y_root = event.y_root - galeria.winfo_rooty()

                        if col_idx >= 6:
                            x = x_root - hover.width() - 20
                        else:
                            x = x_root + 20
                        y = y_root - 20

                        screen_width = galeria.winfo_width()
                        screen_height = galeria.winfo_height()

                        if x + hover.width() > screen_width:
                            x = screen_width - hover.width() - 10
                        if x < 0:
                            x = 10
                        if y + hover.height() > screen_height:
                            y = screen_height - hover.height() - 10
                        if y < 0:
                            y = 10

                        zoom_preview.config(image=hover)
                        zoom_preview.place(x=x, y=y)

                    return on_enter

                label.bind("<Enter>", make_hover_handler(c, img_hover_tk))
                label.bind("<Leave>", lambda e: zoom_preview.place_forget())

        def atualizar_scrollregion():
            canvas.update_idletasks()
            canvas.config(scrollregion=canvas.bbox("all"))

        galeria.after(100, atualizar_scrollregion)

if __name__ == "__main__":
    root = tk.Tk()
    app = AppImagemViewer(root)
    root.mainloop()
