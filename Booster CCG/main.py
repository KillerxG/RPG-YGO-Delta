
import tkinter as tk
from PIL import Image, ImageTk, ImageOps
import os
import random

BOOSTERS = [f"RPG_Series_{i}" for i in range(1, 16)]
DELAY_REVELACAO = 400
CHANCE_EXTRA_SECRETA = 0.2
TAMANHO_TELA = (1280, 720)

COR_BOTAO = "#3e3e3e"
COR_HOVER = "#5e5e5e"
COR_TEXTO = "red"
COR_SECRETA = "#FFD700"
COR_SUPER = "skyblue"
COR_TEXTO_SUPER = "cyan"
COR_TEXTO_SECRETA = "#FFD700"

def carregar_cartas(booster):
    base = os.path.join('cards', booster)
    super_path = os.path.join(base, "Super Raras")
    secreta_path = os.path.join(base, "Secreta Raras")
    super_raras = [f for f in os.listdir(super_path) if f.endswith('.jpg')]
    secretas = [f for f in os.listdir(secreta_path) if f.endswith('.jpg')]
    return super_raras, secretas, super_path, secreta_path

def estilizar_botao_hover(botao):
    def on_enter(e):
        botao.config(bg=COR_HOVER)
        botao.config(font=("Helvetica", 16, "bold"))
    def on_leave(e):
        botao.config(bg=COR_BOTAO)
        botao.config(font=("Helvetica", 14, "bold"))
    botao.bind("<Enter>", on_enter)
    botao.bind("<Leave>", on_leave)
    botao.configure(
        bg=COR_BOTAO,
        fg=COR_TEXTO,
        font=("Helvetica", 14, "bold"),
        relief="raised",
        bd=4,
        activebackground=COR_HOVER,
        activeforeground=COR_TEXTO,
        cursor="hand2"
    )

def mostrar_resultado_em_janela(cartas, booster_name):
    janela = tk.Toplevel(root, bg="black")
    janela.title("Cartas Obtidas")
    janela.geometry(f"{TAMANHO_TELA[0]}x{TAMANHO_TELA[1]}")

    label_booster = tk.Label(janela, text=booster_name, font=("Helvetica", 22, "bold"), fg="white", bg="black")
    label_booster.place(relx=0.5, rely=0.05, anchor="center")

    frame_cartas = tk.Frame(janela, bg="black")
    frame_cartas.place(relx=0.5, rely=0.5, anchor="center")

    def revelar(i):
        if i >= len(cartas):
            return
        card_file, raridade, caminho = cartas[i]
        img_path = os.path.join(caminho, card_file)
        img = Image.open(img_path).resize((200, 280))
        if raridade == 'marca':
            img = img
        elif raridade == 'secreta':
            img = ImageOps.expand(img, border=6, fill=COR_SECRETA)
        else:
            img = ImageOps.expand(img, border=6, fill=COR_SUPER)

        tk_img = ImageTk.PhotoImage(img)
        carta_frame = tk.Frame(frame_cartas, bg="black")
        carta_frame.grid(row=i // 5, column=i % 5, padx=10, pady=10)
        label_img = tk.Label(carta_frame, image=tk_img, bg="black")
        label_img.image = tk_img
        label_img.pack()

        def on_enter_card(e, lbl=label_img):
            lbl.place_configure(rely=0.0)
            lbl.master.lift()
            lbl.master.configure(bg="#111111")
            lbl.config(width=int(200*1.1), height=int(280*1.1))

        def on_leave_card(e, lbl=label_img):
            lbl.master.configure(bg="black")
            lbl.config(width=200, height=280)

        label_texto = tk.Label(
            carta_frame,
            text="" if raridade == 'marca' else ("Secreta Rara" if raridade == 'secreta' else "Super Rara"),
            fg="white" if raridade == 'marca' else (COR_TEXTO_SECRETA if raridade == 'secreta' else COR_TEXTO_SUPER),
            bg="black",
            font=("Helvetica", 10, "bold")
        )
        label_texto.pack()
        janela.after(DELAY_REVELACAO, lambda: revelar(i + 1))

    revelar(0)

    voltar_btn = tk.Button(janela, text="Voltar", command=janela.destroy)
    estilizar_botao_hover(voltar_btn)
    voltar_btn.place(relx=0.5, rely=0.93, anchor="center")

def abrir_booster(booster):
    super_raras, secretas, super_path, secreta_path = carregar_cartas(booster)
    resultado = []
    if len(super_raras) >= 7:
        resultado += [(c, 'super', super_path) for c in random.sample(super_raras, 7)]
    else:
        resultado += [(c, 'super', super_path) for c in super_raras]
    if secretas:
        resultado.append((random.choice(secretas), 'secreta', secreta_path))
    if random.random() < CHANCE_EXTRA_SECRETA and secretas:
        resultado.append((random.choice(secretas), 'secreta', secreta_path))
    elif len(super_raras) > 0:
        resultado.append((random.choice(super_raras), 'super', super_path))
    random.shuffle(resultado)
    # Verifica se há duas cartas secretas e escolhe a imagem correta da marca
    num_secretas = sum(1 for c in resultado if c[1] == "secreta")
    marca_img = "marca2.jpg" if num_secretas >= 2 else "marca.jpg"
    resultado.append((marca_img, "marca", "backgrounds"))
    mostrar_resultado_em_janela(resultado, booster)

def mostrar_menu():
    for widget in frame_inicio.winfo_children():
        widget.destroy()
    frame_menu.pack(fill="both", expand=True)
    for c in range(7): frame_menu.grid_columnconfigure(c, weight=1)
    for widget in frame_menu.winfo_children():
        widget.destroy()

    frame_menu.configure(bg="black")

    booster_frame = tk.Frame(frame_menu, bg="black")
    booster_frame.place(relx=0.5, rely=0.5, anchor="center")

    for i, booster in enumerate(BOOSTERS):
        frame_menu.grid_columnconfigure(i % 5 + 1, weight=1)
        img_path = os.path.join("capa", f"{booster}.jpg")
        img = Image.open(img_path).resize((200, 250))
        tk_img = ImageTk.PhotoImage(img)
        btn = tk.Button(frame_menu, image=tk_img, command=lambda b=booster: abrir_booster(b), bd=4, relief="raised", bg="black")
        btn.image = tk_img
        btn.grid(row=i // 5, column=i % 5, padx=10, pady=10, in_=booster_frame)
        btn.bind("<Enter>", lambda e, b=btn: b.config(relief="sunken"))
        btn.bind("<Leave>", lambda e, b=btn: b.config(relief="raised"))

    voltar_btn = tk.Button(frame_menu, text="Voltar", command=voltar_inicio)
    estilizar_botao_hover(voltar_btn)
    voltar_btn.place(x=20, y=20)

def voltar_inicio():
    frame_menu.pack_forget()
    for widget in frame_inicio.winfo_children():
        widget.destroy()
    montar_tela_inicial()

def montar_tela_inicial():
    frame_inicio.configure(bg="black")
    btn_booster = tk.Button(frame_inicio, text="Abrir Boosters", font=("Helvetica", 20, "bold"), command=mostrar_menu)
    estilizar_botao_hover(btn_booster)
    btn_booster.pack(pady=10)

def toggle_fullscreen(event=None):
    is_fullscreen = not root.attributes("-fullscreen")
    root.attributes("-fullscreen", is_fullscreen)

root = tk.Tk()
root.title("Simulador de Booster")
root.state("zoomed")
root.configure(bg="black")
root.bind("<F11>", toggle_fullscreen)

frame_inicio = tk.Frame(root, bg="black")
frame_inicio.pack(pady=60)

frame_menu = tk.Frame(root, bg="black")

montar_tela_inicial()

root.mainloop()
