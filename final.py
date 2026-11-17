"""
BLACKJACK ROYALE - Trabalho final de módulo (tkinter)

Funcionalidades:
  * Menu principal, Regras, Estatísticas e Definições
  * Mesa com visual melhorado (feltro, sombras, fichas 3D, animações, confetti)
  * Sapato com vários baralhos e "cut card"
  * Mecânicas: Pedir, Ficar, Dobrar, Desistir, Blackjack paga 3:2
  * Fichas por clique ou arrastar; repetir aposta; desfazer ficha
  * Contagem Hi-Lo opcional (modo treino)
  * Progresso guardado automaticamente em ficheiro JSON
  * Atalhos de teclado: H = pedir, S = ficar, D = dobrar, Enter/Espaço = avançar
"""

import tkinter as tk
from tkinter import messagebox
import random
import json
import os
import math
import copy

# ==========================================================
# CONSTANTES
# ==========================================================

PASTA = os.path.dirname(os.path.abspath(__file__))
FICHEIRO_SAVE = os.path.join(PASTA, "blackjack_save.json")

BG = "#101820"
PAINEL = "#17261f"
DOURADO = "#E8BD61"
BRANCO = "#FFFFFF"
VERMELHO = "#D94343"
VERDE = "#4FD18B"
PRETO = "#171717"
CINZA = "#3a3f47"

TEMAS = {
    "Verde": ("#0b3d2c", "#168062"),
    "Azul": ("#0c2d4d", "#1b6aa5"),
    "Bordô": ("#4a0f1d", "#9b2842"),
}

NAIPES = ["♠", "♥", "♦", "♣"]
VALORES = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

FICHAS_TIPOS = [
    {"valor": 5, "cor": "#8a8f98", "y": 100},
    {"valor": 10, "cor": "#2878D0", "y": 175},
    {"valor": 25, "cor": "#D94343", "y": 250},
    {"valor": 50, "cor": "#269B62", "y": 325},
    {"valor": 100, "cor": "#252525", "y": 400},
    {"valor": 500, "cor": "#7b3fa0", "y": 475},
]
COR_FICHA = {f["valor"]: f["cor"] for f in FICHAS_TIPOS}

CW, CH = 1100, 560          # tamanho do canvas do jogo
CX = 440                    # centro horizontal da mesa
CARTA_W, CARTA_H = 80, 116
SHOE_X, SHOE_Y = 770, 46
ZONA_APOSTA = (190, 415, 690, 552)
CHIP_X = 990

FATOR_VEL = {1: 1.5, 2: 1.0, 3: 0.6}   # multiplicador de atrasos

PADRAO = {
    "saldo": 1000,
    "vitorias": 0,
    "derrotas": 0,
    "empates": 0,
    "blackjacks": 0,
    "rondas": 0,
    "falencias": 0,
    "saldo_max": 1000,
    "maior_ganho": 0,
    "ultima_aposta": 0,
    "config": {
        "velocidade": 2,
        "baralhos": 6,
        "soft17": False,
        "contagem": False,
        "tema": "Verde",
    },
}


# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================

def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def misturar(a, b, t):
    ra, rb = hex_rgb(a), hex_rgb(b)
    return "#%02x%02x%02x" % tuple(
        int(ra[i] + (rb[i] - ra[i]) * t) for i in range(3)
    )


def fmt(n):
    return f"{n:,}".replace(",", ".")


def carregar():
    dados = copy.deepcopy(PADRAO)
    try:
        with open(FICHEIRO_SAVE, "r", encoding="utf-8") as f:
            guardado = json.load(f)
        for k, v in guardado.items():
            if k == "config" and isinstance(v, dict):
                dados["config"].update(v)
            elif k in dados:
                dados[k] = v
    except (OSError, ValueError):
        pass
    if dados["config"]["tema"] not in TEMAS:
        dados["config"]["tema"] = "Verde"
    return dados


def guardar(dados):
    try:
        with open(FICHEIRO_SAVE, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
    except OSError:
        pass


def calcular(cartas):
    """Devolve (total, soft). soft=True se houver um Ás a valer 11."""
    total, ases = 0, 0
    for valor, _ in cartas:
        if valor == "A":
            total += 11
            ases += 1
        elif valor in ("J", "Q", "K"):
            total += 10
        else:
            total += int(valor)
    while total > 21 and ases:
        total -= 10
        ases -= 1
    return total, ases > 0


def rrect(cv, x1, y1, x2, y2, r=10, tags="dyn", **kw):
    """Retângulo com cantos arredondados."""
    r = max(0, min(r, (x2 - x1) / 2, (y2 - y1) / 2))
    pts = [
        x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
        x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
        x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
    ]
    return cv.create_polygon(pts, smooth=True, tags=tags, **kw)


def ficha_topo(cv, x, y, valor, cor, r=28, tags="dyn"):
    """Ficha vista de cima (painel e arrastar)."""
    cv.create_oval(x - r + 3, y - r + 4, x + r + 3, y + r + 4,
                   fill="#050a08", outline="", tags=tags)
    cv.create_oval(x - r, y - r, x + r, y + r,
                   fill=BRANCO, outline=BRANCO, tags=tags)
    cv.create_oval(x - r + 5, y - r + 5, x + r - 5, y + r - 5,
                   fill=cor, outline=BRANCO, width=2, tags=tags)
    for ang in range(0, 360, 45):
        rad = math.radians(ang)
        px = x + (r - 3) * math.cos(rad)
        py = y + (r - 3) * math.sin(rad)
        cv.create_oval(px - 3, py - 3, px + 3, py + 3,
                       fill=cor, outline=cor, tags=tags)
    cv.create_text(x, y, text=str(valor), fill=BRANCO,
                   font=("Arial", 12 if valor < 100 else 11, "bold"),
                   tags=tags)


def ficha_plana(cv, x, y, valor, cor, topo, r=26, tags="dyn"):
    """Ficha em perspetiva (para pilhas)."""
    rv = r * 0.55
    cv.create_oval(x - r, y - rv + 5, x + r, y + rv + 5,
                   fill=misturar(cor, "#000000", 0.5),
                   outline="", tags=tags)
    cv.create_oval(x - r, y - rv, x + r, y + rv,
                   fill=cor, outline=BRANCO, width=2, tags=tags)
    cv.create_oval(x - r + 7, y - rv + 4, x + r - 7, y + rv - 4,
                   outline=BRANCO, dash=(3, 3), tags=tags)
    if topo:
        cv.create_text(x, y, text=str(valor), fill=BRANCO,
                       font=("Arial", 9, "bold"), tags=tags)


def carta_cv(cv, x, y, carta, oculta, sx=1.0, tags="dyn",
             sombra="#06140e", w=CARTA_W, h=CARTA_H):
    """Desenha uma carta. sx = escala horizontal (para o efeito de virar)."""
    cx = x + w / 2
    meia = w / 2 * sx
    x1, x2 = cx - meia, cx + meia
    if meia < 1:
        return
    rrect(cv, x1 + 4, y + 5, x2 + 4, y + h + 5, 10,
          tags=tags, fill=sombra, outline="")

    if oculta:
        rrect(cv, x1, y, x2, y + h, 10, tags=tags,
              fill=BRANCO, outline="#cccccc")
        rrect(cv, x1 + 5, y + 5, x2 - 5, y + h - 5, 7, tags=tags,
              fill="#1c3f73", outline=DOURADO, width=2)
        if sx > 0.6:
            my = y + h / 2
            cv.create_polygon(cx, my - 30, cx + 20 * sx, my, cx, my + 30,
                              cx - 20 * sx, my, fill="", outline=DOURADO,
                              width=2, tags=tags)
            cv.create_text(cx, my, text="♠", fill=DOURADO,
                           font=("Arial", 22, "bold"), tags=tags)
        return

    rrect(cv, x1, y, x2, y + h, 10, tags=tags,
          fill=BRANCO, outline="#c8c8c8", width=2)
    if sx < 0.8:
        return
    valor, naipe = carta
    cor = VERMELHO if naipe in ("♥", "♦") else PRETO
    cv.create_text(x1 + 14, y + 16, text=valor, fill=cor,
                   font=("Arial", 14, "bold"), tags=tags)
    cv.create_text(x1 + 14, y + 34, text=naipe, fill=cor,
                   font=("Arial", 14), tags=tags)
    cv.create_text(cx, y + h / 2, text=naipe, fill=cor,
                   font=("Arial", 38), tags=tags)
    cv.create_text(x2 - 14, y + h - 34, text=naipe, fill=cor,
                   font=("Arial", 14), tags=tags)
    cv.create_text(x2 - 14, y + h - 16, text=valor, fill=cor,
                   font=("Arial", 14, "bold"), tags=tags)


def fundo_gradiente(cv, w, h, tema, tag="fundo"):
    escuro = TEMAS[tema][0]
    n = 40
    for i in range(n):
        cv.create_rectangle(0, h * i / n, w, h * (i + 1) / n + 1,
                            fill=misturar(BG, escuro, i / (n - 1)),
                            outline="", tags=tag)


def botao(parent, texto, comando, largura=14, cor=DOURADO, fg=BG, tam=10):
    b = tk.Button(
        parent, text=texto, command=comando,
        font=("Arial", tam, "bold"), bg=cor, fg=fg,
        activebackground=misturar(cor, "#ffffff", 0.25),
        activeforeground=fg, disabledforeground="#8a8f98",
        relief="flat", bd=0, cursor="hand2", width=largura,
        pady=8, takefocus=0,
    )
    b.cor = cor
    b.fg_normal = fg

    def entrar(_):
        if str(b["state"]) == "normal":
            b.config(bg=misturar(b.cor, "#ffffff", 0.25))

    def sair(_):
        if str(b["state"]) == "normal":
            b.config(bg=b.cor)

    b.bind("<Enter>", entrar)
    b.bind("<Leave>", sair)
    return b


def ativar(b, ligado):
    if ligado:
        b.config(state="normal", bg=b.cor, cursor="hand2")
    else:
        b.config(state="disabled", bg=CINZA, cursor="arrow")


# ==========================================================
# ECRÃ: MENU PRINCIPAL
# ==========================================================

class Menu(tk.Frame):

    def __init__(self, app):
        super().__init__(app.root, bg=BG)
        self.app = app
        self.cv = tk.Canvas(self, width=1100, height=700, bg=BG,
                            highlightthickness=0)
        self.cv.pack()

        opcoes = [
            ("JOGAR", lambda: app.mostrar("jogo")),
            ("REGRAS", lambda: app.mostrar("regras")),
            ("ESTATÍSTICAS", lambda: app.mostrar("stats")),
            ("DEFINIÇÕES", lambda: app.mostrar("defs")),
            ("SAIR", app.sair),
        ]
        for i, (txt, cmd) in enumerate(opcoes):
            b = botao(self, txt, cmd, largura=26, tam=13,
                      cor=DOURADO if i == 0 else "#d9d2bd")
            self.cv.create_window(550, 372 + i * 58, window=b, tags="ui")

    def ao_mostrar(self):
        c = self.cv
        c.delete("fundo")
        c.delete("dyn")
        tema = self.app.dados["config"]["tema"]
        fundo_gradiente(c, 1100, 700, tema)

        # naipes decorativos
        claro = misturar(TEMAS[tema][1], BG, 0.75)
        posicoes = [(90, 90, "♠"), (1010, 110, "♥"), (150, 330, "♦"),
                    (960, 360, "♣"), (80, 600, "♥"), (1020, 610, "♠"),
                    (250, 150, "♣"), (850, 190, "♦")]
        for x, y, s in posicoes:
            c.create_text(x, y, text=s, fill=claro, tags="fundo",
                          font=("Arial", 70, "bold"))
        c.tag_lower("fundo")

        # cartas A♠ + K♥ (um blackjack!)
        sombra = misturar(TEMAS[tema][0], "#000000", 0.6)
        carta_cv(c, 462, 28, ("A", "♠"), False, sombra=sombra)
        carta_cv(c, 508, 40, ("K", "♥"), False, sombra=sombra)

        # título
        c.create_text(553, 203, text="BLACKJACK", fill="#000000",
                      font=("Georgia", 58, "bold"), tags="dyn")
        c.create_text(550, 200, text="BLACKJACK", fill=DOURADO,
                      font=("Georgia", 58, "bold"), tags="dyn")
        c.create_text(550, 262, text="R  O  Y  A  L  E", fill=BRANCO,
                      font=("Georgia", 20, "bold"), tags="dyn")
        c.create_line(300, 290, 800, 290, fill=DOURADO, width=2, tags="dyn")

        d = self.app.dados
        c.create_text(550, 672,
                      text=f"Saldo: {fmt(d['saldo'])} fichas    •    "
                           f"Recorde: {fmt(d['saldo_max'])}",
                      fill=DOURADO, font=("Arial", 12, "bold"), tags="dyn")


# ==========================================================
# ECRÃ: REGRAS
# ==========================================================

class Regras(tk.Frame):

    TEXTO = [
        ("h", "OBJETIVO"),
        ("p", "Chegar o mais perto possível de 21 pontos sem ultrapassar, "
              "e ter mais pontos do que o dealer.\n"),
        ("h", "VALOR DAS CARTAS"),
        ("p", "• 2 a 10: valem o número da carta\n"
              "• J, Q, K: valem 10\n"
              "• Ás: vale 11 ou 1 (o que for melhor para ti)\n"),
        ("h", "COMO JOGAR"),
        ("p", "1. Arrasta (ou clica) nas fichas para a zona de aposta. "
              "Aposta mínima: 10.\n"
              "2. Carrega em DAR CARTAS. Recebes duas cartas e o dealer "
              "fica com uma virada para baixo.\n"
              "3. PEDIR (H) dá-te mais uma carta. FICAR (S) termina a tua vez.\n"
              "4. DOBRAR (D): dobras a aposta, recebes só mais uma carta e "
              "ficas. Só nas duas primeiras cartas.\n"
              "5. DESISTIR: recuperas metade da aposta. Só nas duas primeiras cartas.\n"),
        ("h", "PAGAMENTOS"),
        ("p", "• Vitória normal: paga 1 para 1\n"
              "• Blackjack (Ás + figura/10 nas duas primeiras cartas): paga 3 para 2\n"
              "• Empate (push): a aposta é devolvida\n"
              "• Derrota ou rebentar (mais de 21): perdes a aposta\n"),
        ("h", "REGRAS DO DEALER"),
        ("p", "O dealer pede carta até chegar a 17 e depois fica. "
              "Nas Definições podes ativar a variante em que também pede "
              "num 17 \"soft\" (17 com um Ás a valer 11).\n"),
        ("h", "EXTRA: CONTAGEM HI-LO"),
        ("p", "Ativa-a nas Definições para treinares. 2-6 contam +1, 7-9 "
              "contam 0 e 10/J/Q/K/Ás contam -1. Uma contagem alta significa "
              "que restam mais cartas altas no sapato, o que favorece o jogador.\n"),
        ("h", "ATALHOS"),
        ("p", "H = pedir   •   S = ficar   •   D = dobrar   •   "
              "Enter/Espaço = dar cartas / nova ronda   •   Esc = menu\n"),
    ]

    def __init__(self, app):
        super().__init__(app.root, bg=BG)
        tk.Label(self, text="REGRAS DO JOGO", font=("Georgia", 30, "bold"),
                 fg=DOURADO, bg=BG).pack(pady=(25, 10))

        moldura = tk.Frame(self, bg=DOURADO, padx=2, pady=2)
        moldura.pack()
        txt = tk.Text(moldura, width=88, height=22, bg=PAINEL, fg=BRANCO,
                      font=("Arial", 12), wrap="word", padx=25, pady=15,
                      relief="flat", spacing1=2, spacing3=2,
                      highlightthickness=0, cursor="arrow")
        barra = tk.Scrollbar(moldura, command=txt.yview)
        txt.config(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y")
        txt.pack(side="left")
        txt.tag_config("h", font=("Georgia", 14, "bold"), foreground=DOURADO,
                       spacing1=10)
        txt.tag_config("p", foreground=BRANCO)
        for tag, t in self.TEXTO:
            txt.insert("end", t + ("\n" if tag == "h" else ""), tag)
        txt.config(state="disabled")

        botao(self, "◀ VOLTAR AO MENU", lambda: app.mostrar("menu"),
              largura=22, tam=11).pack(pady=15)


# ==========================================================
# ECRÃ: ESTATÍSTICAS
# ==========================================================

class Estatisticas(tk.Frame):

    def __init__(self, app):
        super().__init__(app.root, bg=BG)
        self.app = app
        self.cv = tk.Canvas(self, width=1100, height=700, bg=BG,
                            highlightthickness=0)
        self.cv.pack()
        b1 = botao(self, "◀ VOLTAR AO MENU", lambda: app.mostrar("menu"),
                   largura=22, tam=11)
        b2 = botao(self, "REPOR PROGRESSO", self.repor, largura=22,
                   cor="#e0715f", tam=11)
        self.cv.create_window(400, 655, window=b1)
        self.cv.create_window(700, 655, window=b2)

    def repor(self):
        if messagebox.askyesno(
                "Repor progresso",
                "Queres mesmo apagar saldo e estatísticas?\n"
                "As definições mantêm-se."):
            cfg = self.app.dados["config"]
            self.app.dados.clear()
            self.app.dados.update(copy.deepcopy(PADRAO))
            self.app.dados["config"] = cfg
            guardar(self.app.dados)
            self.app.ecras["jogo"].reiniciar()
            self.ao_mostrar()

    def ao_mostrar(self):
        c = self.cv
        c.delete("fundo")
        c.delete("dyn")
        d = self.app.dados
        tema = d["config"]["tema"]
        fundo_gradiente(c, 1100, 700, tema)
        c.tag_lower("fundo")

        c.create_text(550, 50, text="ESTATÍSTICAS", fill=DOURADO,
                      font=("Georgia", 30, "bold"), tags="dyn")

        total = d["vitorias"] + d["derrotas"] + d["empates"]
        taxa = (d["vitorias"] / total * 100) if total else 0
        caixas = [
            ("SALDO ATUAL", fmt(d["saldo"])),
            ("SALDO MÁXIMO", fmt(d["saldo_max"])),
            ("RONDAS JOGADAS", str(d["rondas"])),
            ("TAXA DE VITÓRIA", f"{taxa:.1f}%"),
            ("BLACKJACKS", str(d["blackjacks"])),
            ("MAIOR GANHO", fmt(d["maior_ganho"])),
        ]
        for i, (titulo, valor) in enumerate(caixas):
            x = 70 + (i % 3) * 330
            y = 105 + (i // 3) * 130
            rrect(c, x, y, x + 300, y + 105, 16, fill=PAINEL,
                  outline=DOURADO, width=2)
            c.create_text(x + 150, y + 30, text=titulo, fill=BRANCO,
                          font=("Arial", 11, "bold"), tags="dyn")
            c.create_text(x + 150, y + 68, text=valor, fill=DOURADO,
                          font=("Georgia", 26, "bold"), tags="dyn")

        # barras
        barras = [("Vitórias", d["vitorias"], VERDE),
                  ("Derrotas", d["derrotas"], VERMELHO),
                  ("Empates", d["empates"], "#7fa8d6")]
        for i, (nome, v, cor) in enumerate(barras):
            y = 395 + i * 55
            c.create_text(100, y + 16, text=nome, fill=BRANCO, anchor="w",
                          font=("Arial", 13, "bold"), tags="dyn")
            rrect(c, 230, y, 880, y + 32, 10, fill="#0b1712", outline="")
            larg = int(650 * v / total) if total else 0
            if larg > 14:
                rrect(c, 230, y, 230 + larg, y + 32, 10, fill=cor, outline="")
            pc = (v / total * 100) if total else 0
            c.create_text(900, y + 16, text=f"{v}  ({pc:.0f}%)", fill=BRANCO,
                          anchor="w", font=("Arial", 12, "bold"), tags="dyn")

        c.create_text(550, 600,
                      text=f"Falências: {d['falencias']}",
                      fill="#9aa5a0", font=("Arial", 11), tags="dyn")


# ==========================================================
# ECRÃ: DEFINIÇÕES
# ==========================================================

class Definicoes(tk.Frame):

    def __init__(self, app):
        super().__init__(app.root, bg=BG)
        self.app = app
        tk.Label(self, text="DEFINIÇÕES", font=("Georgia", 30, "bold"),
                 fg=DOURADO, bg=BG).pack(pady=(40, 20))

        painel = tk.Frame(self, bg=PAINEL, padx=45, pady=30,
                          highlightbackground=DOURADO, highlightthickness=2)
        painel.pack()

        self.v_vel = tk.IntVar()
        self.v_bar = tk.IntVar()
        self.v_soft = tk.BooleanVar()
        self.v_cont = tk.BooleanVar()
        self.v_tema = tk.StringVar()

        def linha(r, texto):
            tk.Label(painel, text=texto, font=("Arial", 13, "bold"),
                     fg=BRANCO, bg=PAINEL, anchor="w", width=28
                     ).grid(row=r, column=0, sticky="w", pady=12)
            f = tk.Frame(painel, bg=PAINEL)
            f.grid(row=r, column=1, sticky="w", padx=(20, 0))
            return f

        def radio(f, txt, var, val):
            tk.Radiobutton(
                f, text=txt, variable=var, value=val, command=self.aplicar,
                bg=PAINEL, fg=BRANCO, selectcolor=BG,
                activebackground=PAINEL, activeforeground=DOURADO,
                font=("Arial", 12), takefocus=0, cursor="hand2"
            ).pack(side="left", padx=6)

        f = linha(0, "Velocidade das animações")
        for t, v in (("Lenta", 1), ("Normal", 2), ("Rápida", 3)):
            radio(f, t, self.v_vel, v)

        f = linha(1, "Número de baralhos")
        for n in (1, 2, 4, 6, 8):
            radio(f, str(n), self.v_bar, n)

        f = linha(2, "Tema da mesa")
        for t in TEMAS:
            radio(f, t, self.v_tema, t)

        f = linha(3, "Dealer pede em 17 \"soft\"")
        tk.Checkbutton(f, text="Ativado", variable=self.v_soft,
                       command=self.aplicar, bg=PAINEL, fg=BRANCO,
                       selectcolor=BG, activebackground=PAINEL,
                       activeforeground=DOURADO, font=("Arial", 12),
                       takefocus=0, cursor="hand2").pack(side="left", padx=6)

        f = linha(4, "Mostrar contagem Hi-Lo")
        tk.Checkbutton(f, text="Ativado", variable=self.v_cont,
                       command=self.aplicar, bg=PAINEL, fg=BRANCO,
                       selectcolor=BG, activebackground=PAINEL,
                       activeforeground=DOURADO, font=("Arial", 12),
                       takefocus=0, cursor="hand2").pack(side="left", padx=6)

        tk.Label(self, text="Mudar o nº de baralhos baralha um sapato novo "
                            "na próxima ronda.",
                 font=("Arial", 10, "italic"), fg="#9aa5a0", bg=BG
                 ).pack(pady=(12, 0))

        botao(self, "◀ VOLTAR AO MENU", lambda: app.mostrar("menu"),
              largura=22, tam=11).pack(pady=20)

    def ao_mostrar(self):
        cfg = self.app.dados["config"]
        self.v_vel.set(cfg["velocidade"])
        self.v_bar.set(cfg["baralhos"])
        self.v_soft.set(cfg["soft17"])
        self.v_cont.set(cfg["contagem"])
        self.v_tema.set(cfg["tema"])

    def aplicar(self):
        cfg = self.app.dados["config"]
        cfg["velocidade"] = self.v_vel.get()
        cfg["baralhos"] = self.v_bar.get()
        cfg["soft17"] = self.v_soft.get()
        cfg["contagem"] = self.v_cont.get()
        cfg["tema"] = self.v_tema.get()
        guardar(self.app.dados)


# ==========================================================
# ECRÃ: JOGO
# ==========================================================

class Jogo(tk.Frame):

    def __init__(self, app):
        super().__init__(app.root, bg=BG)
        self.app = app
        self.dados = app.dados

        # ---------- barra superior ----------
        barra = tk.Frame(self, bg=BG)
        barra.pack(fill="x", padx=14, pady=(8, 2))
        botao(barra, "◀ MENU", lambda: app.mostrar("menu"),
              largura=9, tam=9).pack(side="left")
        self.lbl_saldo = tk.Label(barra, font=("Arial", 14, "bold"),
                                  fg=DOURADO, bg=BG, width=24, anchor="e")
        self.lbl_saldo.pack(side="right")
        tk.Label(barra, text="♠  BLACKJACK ROYALE  ♥",
                 font=("Georgia", 20, "bold"), fg=DOURADO, bg=BG
                 ).pack(side="left", expand=True)

        # ---------- canvas ----------
        self.cv = tk.Canvas(self, width=CW, height=CH, bg=BG,
                            highlightthickness=0)
        self.cv.pack()
        self.cv.bind("<ButtonPress-1>", self.rato_premir)
        self.cv.bind("<B1-Motion>", self.rato_mover)
        self.cv.bind("<ButtonRelease-1>", self.rato_largar)

        # ---------- botões ----------
        ctrl = tk.Frame(self, bg=BG)
        ctrl.pack(pady=8)
        defs = [
            ("dar", "DAR CARTAS", self.comecar_ronda, DOURADO),
            ("rep", "REPETIR", self.repetir, "#7fa8d6"),
            ("lim", "LIMPAR", self.limpar, "#b0b0b0"),
            ("pedir", "PEDIR (H)", self.pedir, "#5cc48a"),
            ("ficar", "FICAR (S)", self.ficar, "#e0715f"),
            ("dobrar", "DOBRAR (D)", self.dobrar, "#e8a54a"),
            ("desistir", "DESISTIR", self.desistir, "#9a9aa5"),
            ("novo", "NOVA RONDA", self.nova_ronda, DOURADO),
        ]
        self.btn = {}
        for chave, txt, cmd, cor in defs:
            b = botao(ctrl, txt, cmd, largura=12, cor=cor, tam=9)
            b.pack(side="left", padx=4)
            self.btn[chave] = b

        # ---------- estado ----------
        self.estado = "apostar"
        self.ocupado = False
        self.aposta = 0
        self.fichas_aposta = []
        self.mao = {"j": [], "d": []}
        self.itens = []
        self.particulas = []
        self.arrastar = None
        self.mensagem = "Faz a tua aposta!"
        self.msg_cor = DOURADO
        self.sujo = True
        self.contagem = 0
        self.tema_desenhado = None

        self.criar_sapato()
        self.after(50, self.tick)

    # ------------------------------------------------------
    # ecrã visível
    # ------------------------------------------------------

    def ao_mostrar(self):
        if self.estado == "apostar" and self.dados["saldo"] < 10:
            self.falencia()
        self.atualizar_saldo()
        self.atualizar_botoes()
        self.tema_desenhado = None
        self.desenhar_fundo()
        self.sujo = True

    def reiniciar(self):
        """Chamado quando o progresso é reposto."""
        self.estado = "apostar"
        self.ocupado = False
        self.aposta = 0
        self.fichas_aposta = []
        self.mao = {"j": [], "d": []}
        self.itens = []
        self.mensagem = "Faz a tua aposta!"
        self.msg_cor = DOURADO
        self.criar_sapato()
        self.sujo = True

    @property
    def cfg(self):
        return self.dados["config"]

    # ------------------------------------------------------
    # utilitários
    # ------------------------------------------------------

    def agendar(self, ms, fn):
        self.after(int(ms * FATOR_VEL[self.cfg["velocidade"]]), fn)

    def msg(self, texto, cor=DOURADO):
        self.mensagem = texto
        self.msg_cor = cor
        self.sujo = True

    def atualizar_saldo(self):
        self.lbl_saldo.config(text=f"SALDO: {fmt(self.dados['saldo'])} FICHAS")

    def total(self, dono):
        return calcular([i["carta"] for i in self.mao[dono]])

    def atualizar_botoes(self):
        b = self.btn
        d = self.dados
        livre = not self.ocupado
        ap = self.estado == "apostar" and livre
        jg = self.estado == "jogador" and livre
        fim = self.estado == "fim" and livre
        duas = len(self.mao["j"]) == 2

        ativar(b["dar"], ap and self.aposta >= 10)
        ativar(b["rep"], ap and self.aposta == 0
               and d["ultima_aposta"] >= 10 and d["saldo"] >= 10)
        ativar(b["lim"], ap and self.aposta > 0)
        ativar(b["pedir"], jg)
        ativar(b["ficar"], jg)
        ativar(b["dobrar"], jg and duas and d["saldo"] >= self.aposta)
        ativar(b["desistir"], jg and duas)
        ativar(b["novo"], fim)
        b["novo"].config(text="RECOMEÇAR" if d["saldo"] < 10 else "NOVA RONDA")

    # ------------------------------------------------------
    # sapato e contagem
    # ------------------------------------------------------

    def criar_sapato(self):
        n = self.cfg["baralhos"]
        self.sapato = [(v, s) for _ in range(n)
                       for s in NAIPES for v in VALORES]
        random.shuffle(self.sapato)
        self.baralhos_atuais = n
        self.limite = int(52 * n * 0.25)
        self.contagem = 0

    def tirar(self):
        if not self.sapato:
            self.criar_sapato()
        return self.sapato.pop()

    def contar(self, carta):
        v = carta[0]
        if v in ("2", "3", "4", "5", "6"):
            self.contagem += 1
        elif v in ("10", "J", "Q", "K", "A"):
            self.contagem -= 1

    # ------------------------------------------------------
    # apostas (fichas)
    # ------------------------------------------------------

    @staticmethod
    def decompor(valor):
        fichas = []
        for f in sorted(COR_FICHA, reverse=True):
            while valor >= f:
                fichas.append(f)
                valor -= f
        return fichas

    def adicionar_ficha(self, valor):
        if self.aposta + valor > self.dados["saldo"]:
            self.msg("Não tens fichas suficientes!", VERMELHO)
        else:
            self.fichas_aposta.append(valor)
            self.aposta += valor
            self.msg(f"Aposta: {fmt(self.aposta)} fichas", DOURADO)
        self.atualizar_botoes()

    def limpar(self):
        if self.estado != "apostar" or self.ocupado:
            return
        self.fichas_aposta = []
        self.aposta = 0
        self.msg("Aposta limpa. Escolhe novamente.", DOURADO)
        self.atualizar_botoes()

    def repetir(self):
        if self.estado != "apostar" or self.ocupado:
            return
        v = min(self.dados["ultima_aposta"], self.dados["saldo"] // 5 * 5)
        self.fichas_aposta = self.decompor(v)
        self.aposta = sum(self.fichas_aposta)
        self.msg(f"Aposta repetida: {fmt(self.aposta)} fichas", DOURADO)
        self.atualizar_botoes()

    # ------------------------------------------------------
    # rato
    # ------------------------------------------------------

    def rato_premir(self, e):
        if self.estado != "apostar" or self.ocupado:
            return
        for f in FICHAS_TIPOS:
            if abs(e.x - CHIP_X) <= 30 and abs(e.y - f["y"]) <= 30:
                self.arrastar = {"valor": f["valor"], "cor": f["cor"],
                                 "x": e.x, "y": e.y, "x0": e.x, "y0": e.y}
                self.sujo = True
                return
        x1, y1, x2, y2 = ZONA_APOSTA
        if x1 <= e.x <= x2 and y1 <= e.y <= y2 and self.fichas_aposta:
            v = self.fichas_aposta.pop()
            self.aposta -= v
            self.msg(f"Ficha removida. Aposta: {fmt(self.aposta)}", DOURADO)
            self.atualizar_botoes()

    def rato_mover(self, e):
        if self.arrastar:
            self.arrastar["x"], self.arrastar["y"] = e.x, e.y
            self.sujo = True

    def rato_largar(self, e):
        a = self.arrastar
        if not a:
            return
        self.arrastar = None
        x1, y1, x2, y2 = ZONA_APOSTA
        dentro = x1 <= e.x <= x2 and y1 <= e.y <= y2
        clique = math.hypot(e.x - a["x0"], e.y - a["y0"]) < 6
        if dentro or clique:
            self.adicionar_ficha(a["valor"])
        self.sujo = True

    # ------------------------------------------------------
    # cartas (lógica visual)
    # ------------------------------------------------------

    def relayout(self, dono):
        mao = self.mao[dono]
        n = len(mao)
        esp = min(56, (560 - CARTA_W) / max(n - 1, 1))
        largura = CARTA_W + (n - 1) * esp
        x0 = CX - largura / 2
        y = 50 if dono == "d" else 285
        for i, it in enumerate(mao):
            it["tx"] = x0 + i * esp
            it["ty"] = y

    def dar(self, dono, oculta=False):
        carta = self.tirar()
        it = {"carta": carta, "x": SHOE_X, "y": SHOE_Y, "tx": SHOE_X,
              "ty": SHOE_Y, "oculta": oculta, "sx": 1.0, "virar": 0}
        self.mao[dono].append(it)
        self.itens.append(it)
        self.relayout(dono)
        if not oculta:
            self.contar(carta)
        self.sujo = True

    def revelar_dealer(self):
        for it in self.mao["d"]:
            if it["oculta"] and not it["virar"]:
                it["virar"] = -1
                self.contar(it["carta"])

    # ------------------------------------------------------
    # fluxo da ronda
    # ------------------------------------------------------

    def comecar_ronda(self):
        if self.estado != "apostar" or self.ocupado:
            return
        if self.aposta < 10:
            self.msg("Aposta mínima: 10 fichas!", VERMELHO)
            return
        d = self.dados
        if self.aposta > d["saldo"]:
            self.msg("Não tens fichas suficientes!", VERMELHO)
            return

        d["saldo"] -= self.aposta
        d["ultima_aposta"] = self.aposta
        self.atualizar_saldo()

        aviso = ""
        if (len(self.sapato) < self.limite
                or self.baralhos_atuais != self.cfg["baralhos"]):
            self.criar_sapato()
            aviso = "Sapato novo baralhado! "

        self.itens = []
        self.mao = {"j": [], "d": []}
        self.estado = "distribuir"
        self.ocupado = True
        self.msg(aviso + "A distribuir as cartas...", BRANCO)
        self.atualizar_botoes()

        passos = [("j", False), ("d", False), ("j", False), ("d", True)]

        def passo(i):
            if i < len(passos):
                dono, oculta = passos[i]
                self.dar(dono, oculta)
                self.agendar(380, lambda: passo(i + 1))
            else:
                self.agendar(250, self.fim_distribuicao)

        passo(0)

    def fim_distribuicao(self):
        self.estado = "jogador"
        self.ocupado = False
        pj, _ = self.total("j")
        pd, _ = self.total("d")
        if pj == 21 or pd == 21:
            self.ocupado = True
            self.revelar_dealer()
            self.atualizar_botoes()
            self.agendar(900, lambda: self.naturais(pj == 21, pd == 21))
            return
        self.msg("A tua vez! Pedir, ficar, dobrar ou desistir?", BRANCO)
        self.atualizar_botoes()

    def naturais(self, nat_j, nat_d):
        if nat_j and nat_d:
            self.terminar("empate", "Blackjack para os dois! Empate.")
        elif nat_j:
            self.terminar("blackjack", "BLACKJACK! Pagamento 3 para 2!")
        else:
            self.terminar("derrota", "O dealer tem Blackjack.")

    def pedir(self):
        if self.estado != "jogador" or self.ocupado:
            return
        self.ocupado = True
        self.dar("j")
        self.atualizar_botoes()
        self.agendar(500, self.depois_pedir)

    def depois_pedir(self):
        p, _ = self.total("j")
        if p > 21:
            self.revelar_dealer()
            self.agendar(800, lambda: self.terminar(
                "derrota", f"Rebentaste com {p}!"))
        elif p == 21:
            self.iniciar_dealer()
        else:
            self.ocupado = False
            self.msg("Queres outra carta ou ficar?", BRANCO)
            self.atualizar_botoes()

    def dobrar(self):
        if (self.estado != "jogador" or self.ocupado
                or len(self.mao["j"]) != 2
                or self.dados["saldo"] < self.aposta):
            return
        self.dados["saldo"] -= self.aposta
        self.fichas_aposta = self.fichas_aposta * 2
        self.aposta *= 2
        self.atualizar_saldo()
        self.ocupado = True
        self.msg("Aposta dobrada! Só mais uma carta...", "#e8a54a")
        self.dar("j")
        self.atualizar_botoes()
        self.agendar(700, self.depois_dobrar)

    def depois_dobrar(self):
        p, _ = self.total("j")
        if p > 21:
            self.revelar_dealer()
            self.agendar(800, lambda: self.terminar(
                "derrota", f"Rebentaste ao dobrar com {p}!"))
        else:
            self.iniciar_dealer()

    def desistir(self):
        if (self.estado != "jogador" or self.ocupado
                or len(self.mao["j"]) != 2):
            return
        self.ocupado = True
        self.terminar("desistir", "Desististe. Recuperas metade da aposta.")

    def ficar(self):
        if self.estado != "jogador" or self.ocupado:
            return
        self.iniciar_dealer()

    def iniciar_dealer(self):
        self.estado = "dealer"
        self.ocupado = True
        self.msg("Vez do dealer...", BRANCO)
        self.revelar_dealer()
        self.atualizar_botoes()
        self.agendar(750, self.passo_dealer)

    def passo_dealer(self):
        p, soft = self.total("d")
        if p < 17 or (p == 17 and soft and self.cfg["soft17"]):
            self.dar("d")
            self.agendar(700, self.passo_dealer)
        else:
            self.resolver()

    def resolver(self):
        pj, _ = self.total("j")
        pd, _ = self.total("d")
        if pd > 21:
            self.terminar("vitoria", f"O dealer rebentou com {pd}! Ganhaste!")
        elif pj > pd:
            self.terminar("vitoria", f"Ganhaste! {pj} contra {pd}.")
        elif pj < pd:
            self.terminar("derrota", f"O dealer ganhou. {pd} contra {pj}.")
        else:
            self.terminar("empate", f"Empate com {pj}. Aposta devolvida.")

    def terminar(self, resultado, texto):
        d = self.dados
        ap = self.aposta
        d["rondas"] += 1

        if resultado == "vitoria":
            d["saldo"] += ap * 2
            ganho = ap
            d["vitorias"] += 1
        elif resultado == "blackjack":
            extra = int(ap * 1.5)
            d["saldo"] += ap + extra
            ganho = extra
            d["vitorias"] += 1
            d["blackjacks"] += 1
        elif resultado == "empate":
            d["saldo"] += ap
            ganho = 0
            d["empates"] += 1
        elif resultado == "desistir":
            volta = ap // 2
            d["saldo"] += volta
            ganho = -(ap - volta)
            d["derrotas"] += 1
        else:
            ganho = -ap
            d["derrotas"] += 1

        d["maior_ganho"] = max(d["maior_ganho"], ganho)
        d["saldo_max"] = max(d["saldo_max"], d["saldo"])
        guardar(d)

        sinal = "+" if ganho > 0 else ""
        texto = f"{texto}  ({sinal}{fmt(ganho)})"
        if resultado in ("vitoria", "blackjack"):
            self.msg(texto, VERDE)
            self.confetti()
        elif resultado == "empate":
            self.msg(texto, "#7fa8d6")
        else:
            self.msg(texto, "#ff7b6b")

        if d["saldo"] < 10:
            self.msg(texto + "  Ficaste sem fichas!", "#ff7b6b")

        self.estado = "fim"
        self.ocupado = False
        self.atualizar_saldo()
        self.atualizar_botoes()

    def nova_ronda(self):
        if self.estado != "fim" or self.ocupado:
            return
        if self.dados["saldo"] < 10:
            self.falencia()
        self.estado = "apostar"
        self.aposta = 0
        self.fichas_aposta = []
        self.mao = {"j": [], "d": []}
        self.itens = []
        self.msg("Faz a tua aposta!", DOURADO)
        self.atualizar_saldo()
        self.atualizar_botoes()

    def falencia(self):
        self.dados["falencias"] += 1
        self.dados["saldo"] = 1000
        guardar(self.dados)
        self.atualizar_saldo()

    # ------------------------------------------------------
    # efeitos
    # ------------------------------------------------------

    def confetti(self):
        cores = [DOURADO, BRANCO, "#ff7b6b", VERDE, "#7fa8d6"]
        for _ in range(80):
            ang = random.uniform(math.pi, 2 * math.pi)
            vel = random.uniform(3, 11)
            self.particulas.append({
                "x": CX, "y": 235,
                "vx": math.cos(ang) * vel,
                "vy": math.sin(ang) * vel,
                "vida": random.randint(45, 85),
                "cor": random.choice(cores),
                "t": random.randint(3, 6),
            })

    def tick(self):
        if self.winfo_ismapped():
            mexeu = False
            vel = self.cfg["velocidade"]
            f = 0.2 + 0.08 * vel
            passo_virar = 0.10 + 0.07 * vel

            for it in self.itens:
                dx, dy = it["tx"] - it["x"], it["ty"] - it["y"]
                if abs(dx) > 0.5 or abs(dy) > 0.5:
                    it["x"] += dx * f
                    it["y"] += dy * f
                    mexeu = True
                elif dx or dy:
                    it["x"], it["y"] = it["tx"], it["ty"]
                    mexeu = True

                if it["virar"] == -1:
                    it["sx"] -= passo_virar
                    if it["sx"] <= 0:
                        it["sx"] = 0
                        it["oculta"] = False
                        it["virar"] = 1
                    mexeu = True
                elif it["virar"] == 1:
                    it["sx"] += passo_virar
                    if it["sx"] >= 1:
                        it["sx"] = 1.0
                        it["virar"] = 0
                    mexeu = True

            if self.particulas:
                for p in self.particulas:
                    p["x"] += p["vx"]
                    p["y"] += p["vy"]
                    p["vy"] += 0.35
                    p["vida"] -= 1
                self.particulas = [p for p in self.particulas if p["vida"] > 0]
                mexeu = True

            if mexeu or self.sujo:
                self.desenhar()
                self.sujo = False
        self.after(20, self.tick)

    # ------------------------------------------------------
    # desenho
    # ------------------------------------------------------

    def desenhar_fundo(self):
        tema = self.cfg["tema"]
        if self.tema_desenhado == tema:
            return
        self.tema_desenhado = tema
        c = self.cv
        c.delete("fundo")
        escuro, claro = TEMAS[tema]

        # mesa
        rrect(c, 6, 6, 874, 554, 46, tags="fundo", fill="#3b2417",
              outline=DOURADO, width=3)
        rrect(c, 18, 18, 862, 542, 36, tags="fundo", fill=escuro,
              outline="#0a0a0a", width=2)
        for i in range(14):
            col = misturar(escuro, claro, i / 13)
            rx, ry = 410 - i * 26, 250 - i * 16
            c.create_oval(CX - rx, 280 - ry, CX + rx, 280 + ry,
                          fill=col, outline="", tags="fundo")
        c.create_text(CX, 182,
                      text="BLACKJACK PAGA 3 PARA 2   •   DEALER PARA NOS 17",
                      fill=misturar(claro, "#ffffff", 0.4),
                      font=("Georgia", 11, "italic bold"), tags="fundo")

        # painel de fichas
        rrect(c, 890, 10, 1090, 550, 22, tags="fundo",
              fill=misturar(escuro, "#000000", 0.5),
              outline=DOURADO, width=2)
        c.create_text(990, 34, text="FICHAS", fill=DOURADO,
                      font=("Georgia", 16, "bold"), tags="fundo")
        c.create_text(990, 58, text="clica ou arrasta",
                      fill=BRANCO, font=("Arial", 9, "italic"), tags="fundo")
        for f in FICHAS_TIPOS:
            ficha_topo(c, CHIP_X, f["y"], f["valor"], f["cor"], tags="fundo")
        c.create_text(990, 524, text="Clica na aposta para\nremover a última ficha",
                      fill="#9aa5a0", font=("Arial", 8), justify="center",
                      tags="fundo")
        c.tag_lower("fundo")

    def chegou(self, it):
        return abs(it["x"] - it["tx"]) < 3 and abs(it["y"] - it["ty"]) < 3

    def placar(self, dono, y, nome):
        c = self.cv
        visiveis = [i["carta"] for i in self.mao[dono]
                    if not i["oculta"] and self.chegou(i)]
        if not visiveis:
            c.create_text(CX, y, text=nome, fill=BRANCO,
                          font=("Georgia", 15, "bold"), tags="dyn")
            return
        tot, soft = calcular(visiveis)
        texto = str(tot)
        if soft and tot < 21:
            texto = f"{tot - 10} / {tot}"
        if tot > 21:
            texto = "REBENTOU"
        if dono == "d" and any(i["oculta"] for i in self.mao["d"]):
            texto += " + ?"
        cor = VERMELHO if tot > 21 else (DOURADO if tot == 21 else "#0b1712")
        fg = BRANCO if tot > 21 else (BG if tot == 21 else DOURADO)

        c.create_text(CX - 10, y, text=nome, fill=BRANCO, anchor="e",
                      font=("Georgia", 15, "bold"), tags="dyn")
        t = c.create_text(CX + 22, y, text=texto, fill=fg, anchor="w",
                          font=("Arial", 12, "bold"), tags="dyn")
        x1, y1, x2, y2 = c.bbox(t)
        p = rrect(c, x1 - 10, y1 - 3, x2 + 10, y2 + 3, 12,
                  fill=cor, outline=DOURADO, width=2)
        c.tag_lower(p, t)

    def desenhar_aposta(self):
        c = self.cv
        cx, base = CX, 505
        if not self.fichas_aposta:
            if self.estado == "apostar":
                c.create_oval(cx - 58, base - 42, cx + 58, base + 22,
                              outline=DOURADO, dash=(6, 5), width=2,
                              tags="dyn")
                c.create_text(cx, base - 10, text="ARRASTA AS\nFICHAS AQUI",
                              fill=DOURADO, font=("Arial", 9, "bold"),
                              justify="center", tags="dyn")
            return
        pilhas = {}
        for v in self.fichas_aposta:
            pilhas[v] = pilhas.get(v, 0) + 1
        chaves = sorted(pilhas)
        k = len(chaves)
        for idx, v in enumerate(chaves):
            sx = cx + (idx - (k - 1) / 2) * 64
            n = min(pilhas[v], 10)
            for j in range(n):
                ficha_plana(c, sx, base - j * 5, v, COR_FICHA[v],
                            j == n - 1)
            if pilhas[v] > 10:
                c.create_text(sx + 34, base - 10, text=f"×{pilhas[v]}",
                              fill=BRANCO, anchor="w",
                              font=("Arial", 9, "bold"), tags="dyn")
        c.create_text(cx, 432, text=f"APOSTA: {fmt(self.aposta)}",
                      fill=DOURADO, font=("Georgia", 14, "bold"), tags="dyn")

    def desenhar(self):
        self.desenhar_fundo()
        c = self.cv
        c.delete("dyn")
        sombra = misturar(TEMAS[self.cfg["tema"]][0], "#000000", 0.6)

        # sapato
        for i in (2, 1, 0):
            carta_cv(c, SHOE_X + i * 3, SHOE_Y - i * 3, None, True,
                     sombra=sombra)
        c.create_text(SHOE_X + 42, SHOE_Y + 140,
                      text=f"SAPATO · {len(self.sapato)}",
                      fill=BRANCO, font=("Arial", 9, "bold"), tags="dyn")

        # nomes e pontuações
        self.placar("d", 24, "DEALER")
        self.placar("j", 268, "JOGADOR")

        # cartas
        for it in self.itens:
            carta_cv(c, it["x"], it["y"], it["carta"], it["oculta"],
                     it["sx"], sombra=sombra)

        # aposta
        self.desenhar_aposta()

        # mensagem
        if self.mensagem:
            t = c.create_text(CX, 228, text=self.mensagem, fill=self.msg_cor,
                              font=("Georgia", 16, "bold"), tags="dyn")
            x1, y1, x2, y2 = c.bbox(t)
            p = rrect(c, x1 - 22, y1 - 9, x2 + 22, y2 + 9, 18,
                      fill="#0b1712", outline=self.msg_cor, width=2)
            c.tag_lower(p, t)

        # contagem Hi-Lo
        if self.cfg["contagem"]:
            baralhos = max(len(self.sapato) / 52, 0.5)
            real = self.contagem / baralhos
            c.create_text(34, 536, anchor="w",
                          text=f"Hi-Lo: {self.contagem:+d}   "
                               f"Verdadeira: {real:+.1f}",
                          fill=DOURADO, font=("Arial", 10, "bold"),
                          tags="dyn")

        # confetti
        for p in self.particulas:
            s = p["t"]
            c.create_rectangle(p["x"], p["y"], p["x"] + s, p["y"] + s,
                               fill=p["cor"], outline="", tags="dyn")

        # ficha a ser arrastada
        if self.arrastar:
            a = self.arrastar
            ficha_topo(c, a["x"], a["y"], a["valor"], a["cor"], r=31)


# ==========================================================
# APLICAÇÃO
# ==========================================================

class App:

    def __init__(self, root):
        self.root = root
        root.title("BLACKJACK ROYALE")
        root.geometry("1100x700")
        root.resizable(False, False)
        root.configure(bg=BG)

        self.dados = carregar()
        self.atual = None
        self.ecras = {
            "menu": Menu(self),
            "jogo": Jogo(self),
            "regras": Regras(self),
            "stats": Estatisticas(self),
            "defs": Definicoes(self),
        }
        root.bind("<Key>", self.tecla)
        root.protocol("WM_DELETE_WINDOW", self.sair)
        self.mostrar("menu")

    def mostrar(self, nome):
        for e in self.ecras.values():
            e.pack_forget()
        self.atual = nome
        ecra = self.ecras[nome]
        ecra.pack(fill="both", expand=True)
        if hasattr(ecra, "ao_mostrar"):
            ecra.ao_mostrar()

    def tecla(self, e):
        if self.atual != "jogo":
            return
        jogo = self.ecras["jogo"]
        k = e.keysym.lower()
        if k == "h":
            jogo.pedir()
        elif k == "s":
            jogo.ficar()
        elif k == "d":
            jogo.dobrar()
        elif k in ("return", "space"):
            if jogo.estado == "apostar":
                jogo.comecar_ronda()
            elif jogo.estado == "fim":
                jogo.nova_ronda()
        elif k == "escape":
            self.mostrar("menu")

    def sair(self):
        guardar(self.dados)
        self.root.destroy()


if __name__ == "__main__":
    janela = tk.Tk()
    App(janela)
    janela.mainloop()