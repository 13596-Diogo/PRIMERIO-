"""Todos os ecrãs, exceto a mesa de jogo."""
import copy
import random
import tkinter as tk
from tkinter import messagebox

from constantes import *
from utilitarios import (misturar, fmt, rrect, carta_cv, fundo_gradiente,
                         botao, ESTILO)
from dados import guardar, perfil_padrao
from estrategia import acao_basica


class EcraCanvas(tk.Frame):
    """Base: um canvas do tamanho da janela com fundo em degradê."""

    def __init__(self, app):
        super().__init__(app.root, bg=BG)
        self.app = app
        self.cv = tk.Canvas(self, width=SW, height=SH, bg=BG,
                            highlightthickness=0)
        self.cv.pack()

    def fundo(self):
        self.cv.delete("fundo")
        self.cv.delete("dyn")
        fundo_gradiente(self.cv, SW, SH, self.app.cfg["tema"])
        self.cv.tag_lower("fundo")

    def titulo(self, texto, y=48):
        self.cv.create_text(SW / 2, y, text=texto, fill=DOURADO,
                            font=("Georgia", 30, "bold"), tags="dyn")

    def sombra(self):
        return misturar(TEMAS[self.app.cfg["tema"]][0], "#000000", 0.6)


# ==========================================================
# ABERTURA ANIMADA
# ==========================================================

class Splash(EcraCanvas):

    PASSOS = 150

    def __init__(self, app):
        super().__init__(app)
        self.passo = 0
        self.suits = []
        self.cv.bind("<Button-1>", lambda e: self.acabar())

    def ao_mostrar(self):
        self.passo = 0
        self.suits = [{
            "x": random.randint(20, SW - 20),
            "y": random.randint(SH, SH + 700),
            "v": random.uniform(2, 6),
            "s": random.choice(NAIPES),
            "t": random.randint(28, 80),
        } for _ in range(32)]
        self.animar()

    def acabar(self):
        if self.app.atual == "splash":
            self.app.mostrar("menu")

    def animar(self):
        if self.app.atual != "splash":
            return
        c = self.cv
        c.delete("all")
        tema = self.app.cfg["tema"]
        fundo_gradiente(c, SW, SH, tema, tag="x")
        claro = misturar(TEMAS[tema][1], BG, 0.7)
        for s in self.suits:
            s["y"] -= s["v"]
            if s["y"] < -80:
                s["y"] = SH + 60
            c.create_text(s["x"], s["y"], text=s["s"], fill=claro,
                          font=("Arial", s["t"], "bold"))

        # cartas que deslizam para o centro e viram
        p = self.passo
        prog = min(max((p - 5) / 40, 0), 1)
        ease = 1 - (1 - prog) ** 3
        sx = 1.0
        oculta = True
        if p > 50:
            f = min((p - 50) / 20, 1)
            sx = abs(1 - 2 * f)
            oculta = f < 0.5
        sombra = misturar(TEMAS[tema][0], "#000000", 0.6)
        xa = -100 + (462 + 100) * ease
        xb = SW + 20 - (SW + 20 - 508) * ease
        carta_cv(c, xa, 70, ("A", "♠"), oculta, sx, tags="x", sombra=sombra)
        carta_cv(c, xb, 82, ("K", "♥"), oculta, sx, tags="x", sombra=sombra)

        # título letra a letra
        palavra = "BLACKJACK"
        n = max(0, min(len(palavra), (p - 60) // 4))
        if n:
            c.create_text(553, 303, text=palavra[:n], fill="#000000",
                          font=("Georgia", 58, "bold"))
            c.create_text(550, 300, text=palavra[:n], fill=DOURADO,
                          font=("Georgia", 58, "bold"))
        if p > 100:
            c.create_text(550, 372, text="R  O  Y  A  L  E", fill=BRANCO,
                          font=("Georgia", 20, "bold"))
            c.create_line(300, 402, 800, 402, fill=DOURADO, width=2)
        if p > 110 and (p // 12) % 2 == 0:
            c.create_text(550, 640, text="clica para continuar",
                          fill="#9aa5a0", font=("Arial", 12, "italic"))

        self.passo += 1
        if self.passo >= self.PASSOS:
            self.acabar()
        else:
            self.after(25, self.animar)


# ==========================================================
# MENU PRINCIPAL
# ==========================================================

class Menu(EcraCanvas):

    def __init__(self, app):
        super().__init__(app)
        b = botao(self, "JOGAR", lambda: app.ir("modos"), largura=44,
                  tam=14)
        self.cv.create_window(550, 346, window=b, tags="ui")

        outros = [
            ("PERFIS", "perfis"), ("ESTATÍSTICAS", "stats"),
            ("CONQUISTAS", "conquistas"), ("RECORDES", "recordes"),
            ("ESTRATÉGIA", "estrategia"), ("REGRAS", "regras"),
            ("DEFINIÇÕES", "defs"), ("SAIR", None),
        ]
        for i, (txt, destino) in enumerate(outros):
            cmd = app.sair if destino is None else \
                (lambda d=destino: app.ir(d))
            bt = botao(self, txt, cmd, largura=22, tam=11, cor="#d9d2bd")
            x = 400 if i % 2 == 0 else 700
            y = 410 + (i // 2) * 52
            self.cv.create_window(x, y, window=bt, tags="ui")

    def ao_mostrar(self):
        c = self.cv
        self.fundo()
        tema = self.app.cfg["tema"]
        claro = misturar(TEMAS[tema][1], BG, 0.75)
        for x, y, s in [(90, 90, "♠"), (1010, 110, "♥"), (150, 330, "♦"),
                        (960, 360, "♣"), (80, 640, "♥"), (1020, 650, "♠"),
                        (250, 150, "♣"), (850, 190, "♦")]:
            c.create_text(x, y, text=s, fill=claro, tags="fundo",
                          font=("Arial", 70, "bold"))
        c.tag_lower("fundo")

        sombra = self.sombra()
        carta_cv(c, 462, 22, ("A", "♠"), False, sombra=sombra)
        carta_cv(c, 508, 34, ("K", "♥"), False, sombra=sombra)

        c.create_text(553, 203, text="BLACKJACK", fill="#000000",
                      font=("Georgia", 58, "bold"), tags="dyn")
        c.create_text(550, 200, text="BLACKJACK", fill=DOURADO,
                      font=("Georgia", 58, "bold"), tags="dyn")
        c.create_text(550, 262, text="R  O  Y  A  L  E", fill=BRANCO,
                      font=("Georgia", 20, "bold"), tags="dyn")
        c.create_line(300, 290, 800, 290, fill=DOURADO, width=2, tags="dyn")

        d = self.app.dados
        c.create_text(550, 690,
                      text=f"Perfil: {self.app.save['perfil']}    •    "
                           f"Saldo: {fmt(d['saldo'])}    •    "
                           f"Recorde: {fmt(d['saldo_max'])}",
                      fill=DOURADO, font=("Arial", 12, "bold"), tags="dyn")


# ==========================================================
# ESCOLHA DO MODO
# ==========================================================

class Modos(EcraCanvas):

    def __init__(self, app):
        super().__init__(app)
        info = [("classico", "JOGAR"), ("desafio", "JOGAR"),
                ("relogio", "JOGAR")]
        for i, (modo, txt) in enumerate(info):
            b = botao(self, txt, lambda m=modo: app.iniciar_jogo(m),
                      largura=18, tam=11)
            self.cv.create_window(215 + i * 335, 520, window=b, tags="ui")
        self.cv.create_window(
            550, 660,
            window=botao(self, "◀ VOLTAR AO MENU", lambda: app.ir("menu"),
                         largura=22, tam=11, cor="#d9d2bd"),
            tags="ui")

    def ao_mostrar(self):
        c = self.cv
        self.fundo()
        self.titulo("ESCOLHE O MODO")
        d = self.app.dados
        modos = [
            ("CLÁSSICO", "♠",
             ["Jogo livre sem limites.", "O saldo e as estatísticas",
              "ficam guardados no perfil."],
             f"Saldo: {fmt(d['saldo'])}"),
            ("DESAFIO", "♥",
             ["Começas com 100 fichas.", "Chega às 1.000 antes de",
              "ficares sem nada!"],
             f"Desafios ganhos: {d['desafios_ganhos']}"),
            ("CONTRA-RELÓGIO", "♦",
             ["Tens 500 fichas e só", "20 rondas. Ganha o máximo",
              "que conseguires!"],
             f"Melhor resultado: {fmt(d['relogio_melhor'])}"),
        ]
        for i, (nome, simbolo, linhas, rec) in enumerate(modos):
            x = 65 + i * 335
            rrect(c, x, 110, x + 300, 560, 22, fill=PAINEL,
                  outline=DOURADO, width=2)
            c.create_text(x + 150, 190, text=simbolo, fill=DOURADO,
                          font=("Arial", 70, "bold"), tags="dyn")
            c.create_text(x + 150, 280, text=nome, fill=BRANCO,
                          font=("Georgia", 19, "bold"), tags="dyn")
            for j, ln in enumerate(linhas):
                c.create_text(x + 150, 330 + j * 24, text=ln, fill="#cfd8d3",
                              font=("Arial", 12), tags="dyn")
            c.create_text(x + 150, 450, text=rec, fill=DOURADO,
                          font=("Arial", 12, "bold"), tags="dyn")


# ==========================================================
# REGRAS
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
              "2. DAR CARTAS: recebes duas cartas e o dealer fica com uma "
              "virada para baixo.\n"
              "3. PEDIR (H) dá-te mais uma carta. FICAR (S) termina a tua vez.\n"
              "4. DOBRAR (D): dobras a aposta, recebes só mais uma carta e "
              "ficas. Só nas duas primeiras cartas.\n"
              "5. DIVIDIR (P): com duas cartas do mesmo valor, separas em duas "
              "mãos (até 4), cada uma com a aposta inicial. Nos Ases só "
              "recebes uma carta por mão.\n"
              "6. DESISTIR: recuperas metade da aposta. Só nas duas primeiras "
              "cartas e sem dividir.\n"
              "7. SEGURO: se o dealer mostrar um Ás, podes apostar metade da "
              "aposta que ele tem blackjack. Paga 2 para 1.\n"
              "8. SUGESTÃO (C): diz-te a jogada recomendada pela estratégia "
              "básica.\n"),
        ("h", "PAGAMENTOS"),
        ("p", "• Vitória normal: paga 1 para 1\n"
              "• Blackjack natural (Ás + 10/figura): paga 3 para 2\n"
              "• Empate (push): a aposta é devolvida\n"
              "• Derrota ou rebentar (mais de 21): perdes a aposta\n"),
        ("h", "REGRAS DO DEALER"),
        ("p", "O dealer pede carta até chegar a 17 e depois fica. Nas "
              "Definições podes ativar a variante em que também pede num "
              "17 \"soft\" (17 com um Ás a valer 11).\n"),
        ("h", "MODOS DE JOGO"),
        ("p", "• Clássico: jogo livre, o progresso fica guardado\n"
              "• Desafio: de 100 até 1.000 fichas sem falir\n"
              "• Contra-relógio: 20 rondas para fazer o maior saldo\n"),
        ("h", "CONTAGEM HI-LO (TREINO)"),
        ("p", "Ativa-a nas Definições. 2-6 contam +1, 7-9 contam 0 e "
              "10/J/Q/K/Ás contam -1. Uma contagem alta significa que restam "
              "mais cartas altas no sapato, o que favorece o jogador.\n"),
        ("h", "ATALHOS"),
        ("p", "H pedir • S ficar • D dobrar • P dividir • C sugestão • "
              "Enter/Espaço dar cartas / nova ronda • Esc menu\n"),
    ]

    def __init__(self, app):
        super().__init__(app.root, bg=BG)
        tk.Label(self, text="REGRAS DO JOGO", font=("Georgia", 30, "bold"),
                 fg=DOURADO, bg=BG).pack(pady=(25, 10))
        moldura = tk.Frame(self, bg=DOURADO, padx=2, pady=2)
        moldura.pack()
        txt = tk.Text(moldura, width=88, height=23, bg=PAINEL, fg=BRANCO,
                      font=("Arial", 12), wrap="word", padx=25, pady=15,
                      relief="flat", spacing1=2, spacing3=2,
                      highlightthickness=0, cursor="arrow")
        barra = tk.Scrollbar(moldura, command=txt.yview)
        txt.config(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y")
        txt.pack(side="left")
        txt.tag_config("h", font=("Georgia", 14, "bold"),
                       foreground=DOURADO, spacing1=10)
        txt.tag_config("p", foreground=BRANCO)
        for tag, t in self.TEXTO:
            txt.insert("end", t + ("\n" if tag == "h" else ""), tag)
        txt.config(state="disabled")
        botao(self, "◀ VOLTAR AO MENU", lambda: app.ir("menu"),
              largura=22, tam=11).pack(pady=15)


# ==========================================================
# ESTATÍSTICAS
# ==========================================================

class Estatisticas(EcraCanvas):

    def __init__(self, app):
        super().__init__(app)
        self.cv.create_window(
            400, 672, tags="ui",
            window=botao(self, "◀ VOLTAR AO MENU", lambda: app.ir("menu"),
                         largura=22, tam=11))
        self.cv.create_window(
            700, 672, tags="ui",
            window=botao(self, "REPOR PERFIL", self.repor, largura=22,
                         cor="#e0715f", tam=11))

    def repor(self):
        nome = self.app.save["perfil"]
        if messagebox.askyesno(
                "Repor perfil",
                f"Apagar saldo, estatísticas e conquistas de \"{nome}\"?"):
            self.app.save["perfis"][nome] = perfil_padrao()
            guardar(self.app.save)
            self.ao_mostrar()

    def ao_mostrar(self):
        c = self.cv
        self.fundo()
        d = self.app.dados
        self.titulo(f"ESTATÍSTICAS  •  {self.app.save['perfil']}", 42)

        total = d["vitorias"] + d["derrotas"] + d["empates"]
        taxa = (d["vitorias"] / total * 100) if total else 0
        caixas = [
            ("SALDO ATUAL", fmt(d["saldo"])),
            ("SALDO MÁXIMO", fmt(d["saldo_max"])),
            ("RONDAS JOGADAS", str(d["rondas"])),
            ("TAXA DE VITÓRIA", f"{taxa:.1f}%"),
            ("BLACKJACKS", str(d["blackjacks"])),
            ("MELHOR SÉRIE", str(d["melhor_serie"])),
        ]
        for i, (titulo, valor) in enumerate(caixas):
            x = 70 + (i % 3) * 330
            y = 85 + (i // 3) * 95
            rrect(c, x, y, x + 300, y + 80, 14, fill=PAINEL,
                  outline=DOURADO, width=2)
            c.create_text(x + 150, y + 21, text=titulo, fill=BRANCO,
                          font=("Arial", 10, "bold"), tags="dyn")
            c.create_text(x + 150, y + 53, text=valor, fill=DOURADO,
                          font=("Georgia", 22, "bold"), tags="dyn")

        # barras
        rrect(c, 70, 285, 530, 640, 16, fill=PAINEL, outline=DOURADO, width=2)
        c.create_text(300, 312, text="RESULTADOS", fill=DOURADO,
                      font=("Georgia", 14, "bold"), tags="dyn")
        barras = [("Vitórias", d["vitorias"], VERDE),
                  ("Derrotas", d["derrotas"], VERMELHO),
                  ("Empates", d["empates"], AZUL_CLARO)]
        for i, (nome, v, cor) in enumerate(barras):
            y = 345 + i * 52
            c.create_text(88, y + 14, text=nome, fill=BRANCO, anchor="w",
                          font=("Arial", 11, "bold"), tags="dyn")
            rrect(c, 175, y, 420, y + 28, 9, fill="#0b1712", outline="")
            larg = int(245 * v / total) if total else 0
            if larg > 12:
                rrect(c, 175, y, 175 + larg, y + 28, 9, fill=cor, outline="")
            pc = (v / total * 100) if total else 0
            c.create_text(430, y + 14, text=f"{v} ({pc:.0f}%)", fill=BRANCO,
                          anchor="w", font=("Arial", 10, "bold"), tags="dyn")
        c.create_text(88, 520, anchor="w", fill="#cfd8d3",
                      font=("Arial", 11), tags="dyn",
                      text=f"Maior ganho numa ronda: {fmt(d['maior_ganho'])}")
        c.create_text(88, 548, anchor="w", fill="#cfd8d3",
                      font=("Arial", 11), tags="dyn",
                      text=f"Falências: {d['falencias']}")
        c.create_text(88, 576, anchor="w", fill="#cfd8d3",
                      font=("Arial", 11), tags="dyn",
                      text=f"Conquistas: {len(d['conquistas'])}/{len(CONQUISTAS)}")

        # gráfico do saldo
        rrect(c, 560, 285, 1030, 640, 16, fill=PAINEL, outline=DOURADO,
              width=2)
        c.create_text(795, 312, text="EVOLUÇÃO DO SALDO (modo clássico)",
                      fill=DOURADO, font=("Georgia", 14, "bold"), tags="dyn")
        dados = d["historico"][-60:]
        if len(dados) < 2:
            c.create_text(795, 470, text="Joga algumas rondas para ver "
                                         "o gráfico.", fill="#9aa5a0",
                          font=("Arial", 12, "italic"), tags="dyn")
            return
        x0, x1, y0, y1 = 610, 1005, 345, 600
        lo, hi = min(dados), max(dados)
        if hi == lo:
            hi = lo + 1
        for k in range(4):
            yy = y0 + (y1 - y0) * k / 3
            c.create_line(x0, yy, x1, yy, fill="#2b4338", tags="dyn")
        pts = []
        for i, v in enumerate(dados):
            px = x0 + (x1 - x0) * i / (len(dados) - 1)
            py = y1 - (y1 - y0) * (v - lo) / (hi - lo)
            pts += [px, py]
        c.create_line(*pts, fill=DOURADO, width=3, tags="dyn")
        c.create_oval(pts[-2] - 5, pts[-1] - 5, pts[-2] + 5, pts[-1] + 5,
                      fill=BRANCO, outline=DOURADO, width=2, tags="dyn")
        c.create_text(x0 - 6, y0, text=fmt(hi), fill=BRANCO, anchor="e",
                      font=("Arial", 9), tags="dyn")
        c.create_text(x0 - 6, y1, text=fmt(lo), fill=BRANCO, anchor="e",
                      font=("Arial", 9), tags="dyn")


# ==========================================================
# DEFINIÇÕES
# ==========================================================

class Definicoes(tk.Frame):

    def __init__(self, app):
        super().__init__(app.root, bg=BG)
        self.app = app
        tk.Label(self, text="DEFINIÇÕES", font=("Georgia", 30, "bold"),
                 fg=DOURADO, bg=BG).pack(pady=(30, 14))

        painel = tk.Frame(self, bg=PAINEL, padx=40, pady=18,
                          highlightbackground=DOURADO, highlightthickness=2)
        painel.pack()

        self.v_vel = tk.IntVar()
        self.v_bar = tk.IntVar()
        self.v_soft = tk.BooleanVar()
        self.v_cont = tk.BooleanVar()
        self.v_som = tk.BooleanVar()
        self.v_tema = tk.StringVar()
        self.v_verso = tk.StringVar()

        def linha(r, texto):
            tk.Label(painel, text=texto, font=("Arial", 13, "bold"),
                     fg=BRANCO, bg=PAINEL, anchor="w", width=26
                     ).grid(row=r, column=0, sticky="w", pady=9)
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

        def check(f, var):
            tk.Checkbutton(
                f, text="Ativado", variable=var, command=self.aplicar,
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
        f = linha(3, "Verso das cartas")
        for t in VERSOS:
            radio(f, t, self.v_verso, t)
        f = linha(4, "Dealer pede em 17 \"soft\"")
        check(f, self.v_soft)
        f = linha(5, "Mostrar contagem Hi-Lo")
        check(f, self.v_cont)
        f = linha(6, "Efeitos sonoros")
        check(f, self.v_som)

        tk.Label(self, text="Mudar o nº de baralhos baralha um sapato novo "
                            "na próxima ronda.",
                 font=("Arial", 10, "italic"), fg="#9aa5a0", bg=BG
                 ).pack(pady=(10, 0))
        botao(self, "◀ VOLTAR AO MENU", lambda: app.ir("menu"),
              largura=22, tam=11).pack(pady=14)

    def ao_mostrar(self):
        cfg = self.app.cfg
        self.v_vel.set(cfg["velocidade"])
        self.v_bar.set(cfg["baralhos"])
        self.v_soft.set(cfg["soft17"])
        self.v_cont.set(cfg["contagem"])
        self.v_som.set(cfg["som"])
        self.v_tema.set(cfg["tema"])
        self.v_verso.set(cfg["verso"])

    def aplicar(self):
        cfg = self.app.cfg
        cfg["velocidade"] = self.v_vel.get()
        cfg["baralhos"] = self.v_bar.get()
        cfg["soft17"] = self.v_soft.get()
        cfg["contagem"] = self.v_cont.get()
        cfg["som"] = self.v_som.get()
        cfg["tema"] = self.v_tema.get()
        cfg["verso"] = self.v_verso.get()
        ESTILO["verso"] = cfg["verso"]
        self.app.som.ativo = cfg["som"]
        self.app.som.tocar("clique")
        guardar(self.app.save)


# ==========================================================
# PERFIS
# ==========================================================

class Perfis(tk.Frame):

    def __init__(self, app):
        super().__init__(app.root, bg=BG)
        self.app = app
        tk.Label(self, text="PERFIS DE JOGADOR", font=("Georgia", 30, "bold"),
                 fg=DOURADO, bg=BG).pack(pady=(40, 6))
        tk.Label(self, text="Cada perfil tem o seu saldo, estatísticas e "
                            "conquistas.", font=("Arial", 11, "italic"),
                 fg="#9aa5a0", bg=BG).pack(pady=(0, 16))

        moldura = tk.Frame(self, bg=DOURADO, padx=2, pady=2)
        moldura.pack()
        self.lista = tk.Listbox(
            moldura, font=("Courier", 13, "bold"), bg=PAINEL, fg=BRANCO,
            selectbackground=DOURADO, selectforeground=BG, height=8,
            width=58, relief="flat", highlightthickness=0,
            activestyle="none", exportselection=False)
        self.lista.pack(padx=2, pady=2)

        linha = tk.Frame(self, bg=BG)
        linha.pack(pady=14)
        botao(linha, "SELECIONAR", self.selecionar, largura=16,
              tam=10).pack(side="left", padx=6)
        botao(linha, "APAGAR", self.apagar, largura=16, cor="#e0715f",
              tam=10).pack(side="left", padx=6)

        novo = tk.Frame(self, bg=BG)
        novo.pack(pady=10)
        tk.Label(novo, text="Novo perfil:", font=("Arial", 12, "bold"),
                 fg=BRANCO, bg=BG).pack(side="left", padx=6)
        self.entrada = tk.Entry(novo, font=("Arial", 13), width=18,
                                bg=PAINEL, fg=BRANCO, insertbackground=BRANCO,
                                relief="flat")
        self.entrada.pack(side="left", padx=6, ipady=4)
        botao(novo, "CRIAR", self.criar, largura=10, cor=VERDE,
              tam=10).pack(side="left", padx=6)

        self.aviso = tk.Label(self, text="", font=("Arial", 11, "bold"),
                              fg=DOURADO, bg=BG)
        self.aviso.pack(pady=6)
        botao(self, "◀ VOLTAR AO MENU", lambda: app.ir("menu"),
              largura=22, tam=11).pack(pady=10)

    def ao_mostrar(self):
        self.aviso.config(text="")
        self.atualizar()

    def atualizar(self):
        save = self.app.save
        self.nomes = list(save["perfis"])
        self.lista.delete(0, "end")
        for n in self.nomes:
            p = save["perfis"][n]
            marca = "★ " if n == save["perfil"] else "  "
            self.lista.insert(
                "end", f"{marca}{n:<14} saldo {fmt(p['saldo']):>8}   "
                       f"recorde {fmt(p['saldo_max']):>8}")
        if save["perfil"] in self.nomes:
            self.lista.selection_set(self.nomes.index(save["perfil"]))

    def _escolhido(self):
        sel = self.lista.curselection()
        return self.nomes[sel[0]] if sel else None

    def selecionar(self):
        nome = self._escolhido()
        if nome:
            self.app.save["perfil"] = nome
            guardar(self.app.save)
            self.atualizar()
            self.aviso.config(text=f"Perfil ativo: {nome}", fg=VERDE)

    def criar(self):
        nome = self.entrada.get().strip()[:14]
        save = self.app.save
        if not nome:
            self.aviso.config(text="Escreve um nome.", fg=VERMELHO)
        elif nome in save["perfis"]:
            self.aviso.config(text="Esse perfil já existe.", fg=VERMELHO)
        elif len(save["perfis"]) >= 8:
            self.aviso.config(text="Máximo de 8 perfis.", fg=VERMELHO)
        else:
            save["perfis"][nome] = perfil_padrao()
            save["perfil"] = nome
            guardar(save)
            self.entrada.delete(0, "end")
            self.atualizar()
            self.aviso.config(text=f"Perfil \"{nome}\" criado e ativo!",
                              fg=VERDE)

    def apagar(self):
        nome = self._escolhido()
        save = self.app.save
        if not nome:
            return
        if len(save["perfis"]) == 1:
            self.aviso.config(text="Tem de existir pelo menos um perfil.",
                              fg=VERMELHO)
            return
        if messagebox.askyesno("Apagar perfil",
                               f"Apagar o perfil \"{nome}\" para sempre?"):
            del save["perfis"][nome]
            if save["perfil"] == nome:
                save["perfil"] = next(iter(save["perfis"]))
            guardar(save)
            self.atualizar()
            self.aviso.config(text="Perfil apagado.", fg=DOURADO)


# ==========================================================
# CONQUISTAS
# ==========================================================

class Conquistas(EcraCanvas):

    def __init__(self, app):
        super().__init__(app)
        self.cv.create_window(
            550, 678, tags="ui",
            window=botao(self, "◀ VOLTAR AO MENU", lambda: app.ir("menu"),
                         largura=22, tam=11))

    def ao_mostrar(self):
        c = self.cv
        self.fundo()
        d = self.app.dados
        self.titulo(f"CONQUISTAS  {len(d['conquistas'])}/{len(CONQUISTAS)}",
                    42)
        for i, (cid, nome, desc) in enumerate(CONQUISTAS):
            x = 70 + (i % 2) * 495
            y = 90 + (i // 2) * 92
            ganha = cid in d["conquistas"]
            rrect(c, x, y, x + 470, y + 78, 16,
                  fill=PAINEL if ganha else "#0e1713",
                  outline=DOURADO if ganha else "#33423b", width=2)
            c.create_oval(x + 14, y + 14, x + 64, y + 64,
                          fill=DOURADO if ganha else "#26332d",
                          outline="", tags="dyn")
            c.create_text(x + 39, y + 39, text="★" if ganha else "?",
                          fill=BG if ganha else "#5a6a62",
                          font=("Arial", 22, "bold"), tags="dyn")
            c.create_text(x + 80, y + 26, text=nome, anchor="w",
                          fill=DOURADO if ganha else "#7b8a82",
                          font=("Georgia", 14, "bold"), tags="dyn")
            c.create_text(x + 80, y + 54, text=desc, anchor="w",
                          fill=BRANCO if ganha else "#5f6d66",
                          font=("Arial", 10), tags="dyn")


# ==========================================================
# RECORDES
# ==========================================================

class Recordes(EcraCanvas):

    def __init__(self, app):
        super().__init__(app)
        self.cv.create_window(
            550, 668, tags="ui",
            window=botao(self, "◀ VOLTAR AO MENU", lambda: app.ir("menu"),
                         largura=22, tam=11))

    def ao_mostrar(self):
        c = self.cv
        self.fundo()
        self.titulo("TABELA DE RECORDES")
        perfis = self.app.save["perfis"]
        tabelas = [
            ("MAIOR SALDO (CLÁSSICO)",
             sorted(((n, p["saldo_max"]) for n, p in perfis.items()),
                    key=lambda t: -t[1])),
            ("CONTRA-RELÓGIO",
             sorted(((n, p["relogio_melhor"]) for n, p in perfis.items()
                     if p["relogio_melhor"] > 0), key=lambda t: -t[1])),
        ]
        medalhas = ["#E8BD61", "#C0C0C0", "#CD7F32", "#6b7a72", "#6b7a72"]
        for t, (titulo, linhas) in enumerate(tabelas):
            x = 60 + t * 500
            rrect(c, x, 100, x + 480, 600, 20, fill=PAINEL, outline=DOURADO,
                  width=2)
            c.create_text(x + 240, 135, text=titulo, fill=DOURADO,
                          font=("Georgia", 16, "bold"), tags="dyn")
            for i in range(5):
                y = 185 + i * 78
                rrect(c, x + 20, y, x + 460, y + 64, 14,
                      fill="#0e1713", outline="")
                c.create_oval(x + 32, y + 14, x + 68, y + 50,
                              fill=medalhas[i], outline="", tags="dyn")
                c.create_text(x + 50, y + 32, text=str(i + 1), fill=BG,
                              font=("Arial", 14, "bold"), tags="dyn")
                if i < len(linhas):
                    nome, valor = linhas[i]
                    c.create_text(x + 85, y + 32, text=nome, anchor="w",
                                  fill=BRANCO, font=("Arial", 14, "bold"),
                                  tags="dyn")
                    c.create_text(x + 445, y + 32, text=fmt(valor),
                                  anchor="e", fill=DOURADO,
                                  font=("Georgia", 16, "bold"), tags="dyn")
                else:
                    c.create_text(x + 85, y + 32, text="—", anchor="w",
                                  fill="#5f6d66", font=("Arial", 14),
                                  tags="dyn")


# ==========================================================
# TABELA DE ESTRATÉGIA
# ==========================================================

class TabelaEstrategia(EcraCanvas):

    CORES = {"H": ("#c0483c", BRANCO), "S": ("#d9b13b", BG),
             "D": ("#3f8fd6", BRANCO), "P": ("#3fa76a", BRANCO),
             "R": ("#8a8f98", BRANCO)}

    def __init__(self, app):
        super().__init__(app)
        self.cv.create_window(
            550, 680, tags="ui",
            window=botao(self, "◀ VOLTAR AO MENU", lambda: app.ir("menu"),
                         largura=22, tam=11))

    @staticmethod
    def carta(v):
        return ("A" if v == 11 else str(v), "♠")

    def ao_mostrar(self):
        c = self.cv
        self.fundo()
        self.titulo("ESTRATÉGIA BÁSICA", 40)

        t10 = ("10", "♠")
        duros = [("≤8", [("5", "♠"), ("3", "♠")]),
                 ("9", [("5", "♠"), ("4", "♠")]),
                 ("10", [("6", "♠"), ("4", "♠")]),
                 ("11", [("6", "♠"), ("5", "♠")]),
                 ("12", [t10, ("2", "♠")]), ("13", [t10, ("3", "♠")]),
                 ("14", [t10, ("4", "♠")]), ("15", [t10, ("5", "♠")]),
                 ("16", [t10, ("6", "♠")]), ("17+", [t10, ("7", "♠")])]
        soft = [(f"A{k}", [("A", "♠"), (str(k), "♠")]) for k in range(2, 10)]
        pares = [("AA", [("A", "♠")] * 2)] + \
                [(f"{k}{k}", [(str(k), "♠")] * 2) for k in range(2, 10)] + \
                [("TT", [t10, ("K", "♠")])]

        tabelas = [("MÃOS DURAS", duros), ("MÃOS SOFT", soft),
                   ("PARES", pares)]
        cw, ch = 29, 32
        for t, (nome, linhas) in enumerate(tabelas):
            x0 = 38 + t * 358
            c.create_text(x0 + 170, 92, text=nome, fill=DOURADO,
                          font=("Georgia", 14, "bold"), tags="dyn")
            c.create_text(x0 + 25, 122, text="vs", fill=BRANCO,
                          font=("Arial", 9, "bold"), tags="dyn")
            for j, u in enumerate(range(2, 12)):
                c.create_text(x0 + 50 + j * cw + cw / 2, 122,
                              text="A" if u == 11 else str(u), fill=BRANCO,
                              font=("Arial", 10, "bold"), tags="dyn")
            for i, (rot, cartas) in enumerate(linhas):
                y = 140 + i * ch
                c.create_text(x0 + 25, y + ch / 2, text=rot, fill=BRANCO,
                              font=("Arial", 10, "bold"), tags="dyn")
                for j, u in enumerate(range(2, 12)):
                    letra, _ = acao_basica(cartas, self.carta(u), True, True,
                                           True)
                    bg, fg = self.CORES[letra]
                    x = x0 + 50 + j * cw
                    c.create_rectangle(x, y, x + cw - 2, y + ch - 2,
                                       fill=bg, outline="", tags="dyn")
                    c.create_text(x + cw / 2 - 1, y + ch / 2 - 1, text=letra,
                                  fill=fg, font=("Arial", 10, "bold"),
                                  tags="dyn")

        legenda = [("H", "Pedir"), ("S", "Ficar"), ("D", "Dobrar"),
                   ("P", "Dividir"), ("R", "Desistir")]
        for i, (letra, nome) in enumerate(legenda):
            x = 110 + i * 195
            bg, fg = self.CORES[letra]
            c.create_rectangle(x, 585, x + 30, 615, fill=bg, outline="",
                               tags="dyn")
            c.create_text(x + 15, 600, text=letra, fill=fg,
                          font=("Arial", 11, "bold"), tags="dyn")
            c.create_text(x + 40, 600, text=nome, anchor="w", fill=BRANCO,
                          font=("Arial", 12, "bold"), tags="dyn")
        c.create_text(550, 640, fill="#9aa5a0", font=("Arial", 10, "italic"),
                      tags="dyn",
                      text="Linhas = a tua mão  •  Colunas = carta visível do "
                           "dealer  •  Se não puderes dobrar, pede (ou fica "
                           "no soft 18).")