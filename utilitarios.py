"""Funções auxiliares: cores, desenho de cartas/fichas, botões, pontuação."""
import math
import tkinter as tk
from constantes import *

# estilo partilhado (alterado nas Definições)
ESTILO = {"verso": "Azul"}


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def misturar(a, b, t):
    ra, rb = hex_rgb(a), hex_rgb(b)
    return "#%02x%02x%02x" % tuple(
        int(ra[i] + (rb[i] - ra[i]) * t) for i in range(3))


def fmt(n):
    return f"{n:,}".replace(",", ".")


def pontos(carta):
    """Valor de uma carta (Ás = 11)."""
    v = carta[0]
    if v == "A":
        return 11
    if v in ("J", "Q", "K", "10"):
        return 10
    return int(v)


def calcular(cartas):
    """Devolve (total, soft). soft=True se houver um Ás a valer 11."""
    total, ases = 0, 0
    for c in cartas:
        p = pontos(c)
        total += p
        if p == 11:
            ases += 1
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
    """Ficha vista de cima."""
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
    """Ficha em perspetiva (pilhas)."""
    rv = r * 0.55
    cv.create_oval(x - r, y - rv + 5, x + r, y + rv + 5,
                   fill=misturar(cor, "#000000", 0.5), outline="", tags=tags)
    cv.create_oval(x - r, y - rv, x + r, y + rv,
                   fill=cor, outline=BRANCO, width=2, tags=tags)
    cv.create_oval(x - r + 7, y - rv + 4, x + r - 7, y + rv - 4,
                   outline=BRANCO, dash=(3, 3), tags=tags)
    if topo:
        cv.create_text(x, y, text=str(valor), fill=BRANCO,
                       font=("Arial", 9, "bold"), tags=tags)


def carta_cv(cv, x, y, carta, oculta, sx=1.0, tags="dyn",
             sombra="#06140e", w=CARTA_W, h=CARTA_H):
    """Desenha uma carta. sx = escala horizontal (efeito de virar)."""
    cx = x + w / 2
    meia = w / 2 * sx
    x1, x2 = cx - meia, cx + meia
    if meia < 1:
        return
    rrect(cv, x1 + 4, y + 5, x2 + 4, y + h + 5, 10,
          tags=tags, fill=sombra, outline="")

    if oculta:
        fundo, detalhe = VERSOS.get(ESTILO["verso"], VERSOS["Azul"])
        rrect(cv, x1, y, x2, y + h, 10, tags=tags,
              fill=BRANCO, outline="#cccccc")
        rrect(cv, x1 + 5, y + 5, x2 - 5, y + h - 5, 7, tags=tags,
              fill=fundo, outline=detalhe, width=2)
        if sx > 0.6:
            my = y + h / 2
            cv.create_polygon(cx, my - 30, cx + 20 * sx, my, cx, my + 30,
                              cx - 20 * sx, my, fill="", outline=detalhe,
                              width=2, tags=tags)
            cv.create_text(cx, my, text="♠", fill=detalhe,
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


def botao(parent, texto, comando, largura=14, cor=DOURADO, fg=BG, tam=10,
          pady=8):
    b = tk.Button(
        parent, text=texto, command=comando,
        font=("Arial", tam, "bold"), bg=cor, fg=fg,
        activebackground=misturar(cor, "#ffffff", 0.25),
        activeforeground=fg, disabledforeground="#8a8f98",
        relief="flat", bd=0, cursor="hand2", width=largura,
        pady=pady, takefocus=0,
    )
    b.cor = cor

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