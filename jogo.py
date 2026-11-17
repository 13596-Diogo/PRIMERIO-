"""Mesa de jogo: split, seguro, dobrar, desistir, sugestões, modos, etc."""
import math
import random
import tkinter as tk

from constantes import *
from utilitarios import (misturar, fmt, rrect, ficha_topo, ficha_plana,
                         carta_cv, botao, ativar, calcular, pontos)
from dados import guardar
from estrategia import acao_basica, NOMES

NOMES_RES = {"vitoria": "ganhou", "blackjack": "blackjack", "empate": "empate",
             "derrota": "perdeu", "desistir": "desistiu"}


class Jogo(tk.Frame):

    def __init__(self, app):
        super().__init__(app.root, bg=BG)
        self.app = app
        self.som = app.som
        self.geracao = 0

        # ---------- barra superior ----------
        barra = tk.Frame(self, bg=BG)
        barra.pack(fill="x", padx=14, pady=(8, 2))
        botao(barra, "◀ MENU", lambda: app.ir("menu"),
              largura=9, tam=9, pady=5).pack(side="left")
        self.lbl_saldo = tk.Label(barra, font=("Arial", 14, "bold"),
                                  fg=DOURADO, bg=BG, width=30, anchor="e")
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

        # botões do seguro (ficam por cima do canvas)
        self.b_seg_sim = botao(self, "ACEITAR SEGURO",
                               lambda: self.decidir_seguro(True),
                               largura=17, cor=VERDE, tam=9, pady=4)
        self.b_seg_nao = botao(self, "RECUSAR",
                               lambda: self.decidir_seguro(False),
                               largura=17, cor="#e0715f", tam=9, pady=4)
        self.w_seg = [
            self.cv.create_window(CX - 100, 245, window=self.b_seg_sim,
                                  state="hidden"),
            self.cv.create_window(CX + 100, 245, window=self.b_seg_nao,
                                  state="hidden"),
        ]

        # ---------- botões de ação ----------
        ctrl = tk.Frame(self, bg=BG)
        ctrl.pack(pady=3)
        linha1 = tk.Frame(ctrl, bg=BG)
        linha1.pack(pady=2)
        linha2 = tk.Frame(ctrl, bg=BG)
        linha2.pack(pady=2)
        defs = [
            (linha1, "dar", "DAR CARTAS", self.comecar_ronda, DOURADO),
            (linha1, "rep", "REPETIR", self.repetir, AZUL_CLARO),
            (linha1, "lim", "LIMPAR", self.limpar, "#b0b0b0"),
            (linha1, "novo", "NOVA RONDA", self.nova_ronda, DOURADO),
            (linha2, "pedir", "PEDIR (H)", self.pedir, "#5cc48a"),
            (linha2, "ficar", "FICAR (S)", self.ficar, "#e0715f"),
            (linha2, "dobrar", "DOBRAR (D)", self.dobrar, "#e8a54a"),
            (linha2, "dividir", "DIVIDIR (P)", self.dividir, "#a98be0"),
            (linha2, "desistir", "DESISTIR", self.desistir, "#9a9aa5"),
            (linha2, "dica", "SUGESTÃO (C)", self.sugestao, "#5fb4d9"),
        ]
        self.btn = {}
        for pai, chave, txt, cmd, cor in defs:
            b = botao(pai, txt, cmd, largura=13, cor=cor, tam=9, pady=4)
            b.pack(side="left", padx=4)
            self.btn[chave] = b

        # ---------- estado geral ----------
        self.modo = "classico"
        self._saldo = self.dados["saldo"]
        self.contagem = 0
        self.tema_desenhado = None
        self.toasts = []
        self.sujo = True
        self.mensagem = ""
        self.msg_cor = DOURADO
        self.iniciar_modo("classico")
        self.after(50, self.tick)

    # ------------------------------------------------------
    # propriedades
    # ------------------------------------------------------

    @property
    def dados(self):
        return self.app.dados

    @property
    def cfg(self):
        return self.app.cfg

    @property
    def saldo(self):
        return self._saldo

    @saldo.setter
    def saldo(self, v):
        self._saldo = v
        if self.modo == "classico":
            self.dados["saldo"] = v

    # ------------------------------------------------------
    # modos
    # ------------------------------------------------------

    def iniciar_modo(self, modo):
        self.geracao += 1
        self.modo = modo
        self.modo_terminado = False
        self.objetivo = None
        self.rondas_rest = None
        if modo == "classico":
            if self.dados["saldo"] < 10:
                self.dados["saldo"] = 1000
            self._saldo = self.dados["saldo"]
        elif modo == "desafio":
            self._saldo = 100
            self.objetivo = 1000
        else:
            self._saldo = 500
            self.rondas_rest = 20
        self.limpar_estado_ronda()
        self.criar_sapato()
        self.toasts = []
        self.msg("Faz a tua aposta!", DOURADO)
        self.mostrar_seguro(False)
        self.atualizar_saldo()
        self.atualizar_botoes()

    def limpar_estado_ronda(self):
        self.estado = "apostar"
        self.ocupado = False
        self.aposta = 0
        self.fichas_aposta = []
        self.maos = []
        self.dealer = []
        self.itens = []
        self.ativa = 0
        self.seguro = 0
        self.seguro_net = 0
        self.voos = []
        self.particulas = []
        self.mostrar_fichas = True
        self.all_in = False
        self.arrastar = None
        self.sujo = True

    def ao_mostrar(self):
        self.atualizar_saldo()
        self.atualizar_botoes()
        self.tema_desenhado = None
        self.desenhar_fundo()
        self.sujo = True

    # ------------------------------------------------------
    # utilitários
    # ------------------------------------------------------

    def agendar(self, ms, fn):
        g = self.geracao

        def corre():
            if g == self.geracao:
                fn()
        self.after(int(ms * FATOR_VEL[self.cfg["velocidade"]]), corre)

    def msg(self, texto, cor=DOURADO):
        self.mensagem = texto
        self.msg_cor = cor
        self.sujo = True

    def atualizar_saldo(self):
        self.lbl_saldo.config(
            text=f"{self.app.save['perfil']}  •  SALDO: {fmt(self.saldo)}")
        self.sujo = True

    def tot(self, x):
        itens = x["itens"] if isinstance(x, dict) else x
        return calcular([i["carta"] for i in itens])

    def mostrar_seguro(self, ver):
        for w in self.w_seg:
            self.cv.itemconfigure(w, state="normal" if ver else "hidden")

    def desbloquear(self, cid):
        d = self.dados
        if cid in d["conquistas"]:
            return
        d["conquistas"].append(cid)
        nome = next(n for i, n, _ in CONQUISTAS if i == cid)
        self.toasts.append({"nome": nome, "tempo": 170})
        self.som.tocar("conquista")
        self.sujo = True

    # ------------------------------------------------------
    # botões
    # ------------------------------------------------------

    def pode_dobrar(self):
        if self.estado != "jogador" or self.ocupado or not self.maos:
            return False
        h = self.maos[self.ativa]
        return len(h["itens"]) == 2 and self.saldo >= h["aposta"]

    def pode_dividir(self):
        if not self.pode_dobrar():
            return False
        h = self.maos[self.ativa]
        return (pontos(h["itens"][0]["carta"]) == pontos(h["itens"][1]["carta"])
                and len(self.maos) < 4)

    def pode_desistir(self):
        if self.estado != "jogador" or self.ocupado or len(self.maos) != 1:
            return False
        return len(self.maos[0]["itens"]) == 2

    def atualizar_botoes(self):
        b = self.btn
        livre = not self.ocupado
        ap = self.estado == "apostar" and livre
        jg = self.estado == "jogador" and livre
        fim = self.estado == "fim" and livre

        ativar(b["dar"], ap and self.aposta >= 10)
        ativar(b["rep"], ap and self.aposta == 0
               and self.dados["ultima_aposta"] >= 10 and self.saldo >= 10)
        ativar(b["lim"], ap and self.aposta > 0)
        ativar(b["pedir"], jg)
        ativar(b["ficar"], jg)
        ativar(b["dobrar"], self.pode_dobrar())
        ativar(b["dividir"], self.pode_dividir())
        ativar(b["desistir"], self.pode_desistir())
        ativar(b["dica"], jg)
        ativar(b["novo"], fim)
        if self.modo_terminado:
            txt = "OUTROS MODOS"
        elif self.modo == "classico" and self.saldo < 10:
            txt = "RECOMEÇAR"
        else:
            txt = "NOVA RONDA"
        b["novo"].config(text=txt)

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
    # apostas
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
        if self.aposta + valor > self.saldo:
            self.msg("Não tens fichas suficientes!", VERMELHO)
        else:
            self.fichas_aposta.append(valor)
            self.aposta += valor
            self.som.tocar("ficha")
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
        v = min(self.dados["ultima_aposta"], self.saldo // 5 * 5)
        self.fichas_aposta = self.decompor(v)
        self.aposta = sum(self.fichas_aposta)
        self.som.tocar("ficha")
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
    # cartas e mãos
    # ------------------------------------------------------

    @staticmethod
    def nova_mao(aposta, fichas):
        return {"itens": [], "aposta": aposta, "fichas": fichas,
                "dobrada": False, "fim": False, "split": False,
                "so_uma": False, "desistiu": False, "res": None,
                "motivo": "", "cx": CX}

    def novo_item(self, carta, oculta):
        return {"carta": carta, "x": SHOE_X, "y": SHOE_Y, "tx": SHOE_X,
                "ty": SHOE_Y, "oculta": oculta, "sx": 1.0, "virar": 0}

    def relayout_dealer(self):
        n = len(self.dealer)
        esp = min(56, (560 - CARTA_W) / max(n - 1, 1))
        x0 = CX - (CARTA_W + (n - 1) * esp) / 2
        for i, it in enumerate(self.dealer):
            it["tx"], it["ty"] = x0 + i * esp, 50

    def relayout_jogador(self):
        n = len(self.maos)
        if not n:
            return
        slot = min(320, 800 / n)
        for i, h in enumerate(self.maos):
            cx = CX + (i - (n - 1) / 2) * slot
            m = len(h["itens"])
            if n == 1:
                esp = min(56, (560 - CARTA_W) / max(m - 1, 1))
            else:
                esp = min(56, max(16, (slot - CARTA_W - 20) / max(m - 1, 1)))
            x0 = cx - (CARTA_W + (m - 1) * esp) / 2
            h["cx"] = cx
            for k, it in enumerate(h["itens"]):
                it["tx"], it["ty"] = x0 + k * esp, 285

    def dar_mao(self, i):
        carta = self.tirar()
        it = self.novo_item(carta, False)
        self.maos[i]["itens"].append(it)
        self.itens.append(it)
        self.relayout_jogador()
        self.contar(carta)
        self.som.tocar("carta")
        self.sujo = True

    def dar_dealer(self, oculta=False):
        carta = self.tirar()
        it = self.novo_item(carta, oculta)
        self.dealer.append(it)
        self.itens.append(it)
        self.relayout_dealer()
        if not oculta:
            self.contar(carta)
        self.som.tocar("carta")
        self.sujo = True

    def revelar_dealer(self):
        for it in self.dealer:
            if it["oculta"] and not it["virar"]:
                it["virar"] = -1
                self.contar(it["carta"])
                self.som.tocar("virar")

    def fichas_display(self):
        if self.estado == "apostar":
            return self.fichas_aposta
        todas = []
        for h in self.maos:
            todas += h["fichas"]
        return todas

    # ------------------------------------------------------
    # fluxo da ronda
    # ------------------------------------------------------

    def comecar_ronda(self):
        if self.estado != "apostar" or self.ocupado:
            return
        if self.aposta < 10:
            self.msg("Aposta mínima: 10 fichas!", VERMELHO)
            return
        if self.aposta > self.saldo:
            self.msg("Não tens fichas suficientes!", VERMELHO)
            return

        self.all_in = (self.aposta == self.saldo)
        self.saldo -= self.aposta
        self.dados["ultima_aposta"] = self.aposta
        self.atualizar_saldo()

        aviso = ""
        if (len(self.sapato) < self.limite
                or self.baralhos_atuais != self.cfg["baralhos"]):
            self.criar_sapato()
            aviso = "Sapato novo baralhado! "

        self.itens = []
        self.dealer = []
        self.maos = [self.nova_mao(self.aposta, list(self.fichas_aposta))]
        self.ativa = 0
        self.seguro = 0
        self.seguro_net = 0
        self.estado = "distribuir"
        self.ocupado = True
        self.msg(aviso + "A distribuir as cartas...", BRANCO)
        self.atualizar_botoes()

        passos = [("j", False), ("d", False), ("j", False), ("d", True)]

        def passo(i):
            if i < len(passos):
                quem, oculta = passos[i]
                if quem == "j":
                    self.dar_mao(0)
                else:
                    self.dar_dealer(oculta)
                self.agendar(380, lambda: passo(i + 1))
            else:
                self.agendar(250, self.fim_distribuicao)

        passo(0)

    def fim_distribuicao(self):
        h = self.maos[0]
        up = self.dealer[0]["carta"]
        meio = h["aposta"] // 2
        if up[0] == "A" and meio >= 5 and self.saldo >= meio:
            self.estado = "seguro"
            self.ocupado = False
            self.mostrar_seguro(True)
            self.msg(f"Dealer mostra Ás. Seguro por {fmt(meio)}?", AZUL_CLARO)
            self.atualizar_botoes()
            return
        self.verificar_naturais()

    def decidir_seguro(self, aceita):
        if self.estado != "seguro":
            return
        self.mostrar_seguro(False)
        if aceita:
            self.seguro = self.maos[0]["aposta"] // 2
            self.saldo -= self.seguro
            self.atualizar_saldo()
            self.som.tocar("ficha")
        self.verificar_naturais()

    def verificar_naturais(self):
        self.ocupado = True
        pj, _ = self.tot(self.maos[0])
        pd, _ = self.tot(self.dealer)
        nat_j, nat_d = pj == 21, pd == 21
        prefixo = ""
        if self.seguro:
            if nat_d:
                self.saldo += self.seguro * 3
                self.seguro_net = self.seguro * 2
            else:
                self.seguro_net = -self.seguro
                prefixo = "Sem blackjack: seguro perdido. "
            self.atualizar_saldo()
        if nat_j or nat_d:
            self.estado = "jogador"
            self.revelar_dealer()
            self.atualizar_botoes()
            self.agendar(900, lambda: self.naturais(nat_j, nat_d))
            return
        self.estado = "jogador"
        self.ocupado = False
        self.msg(prefixo + "A tua vez!", BRANCO)
        self.atualizar_botoes()

    def naturais(self, nat_j, nat_d):
        h = self.maos[0]
        if nat_j and nat_d:
            h["res"], h["motivo"] = "empate", "Blackjack para os dois! Empate."
        elif nat_j:
            h["res"], h["motivo"] = "blackjack", "BLACKJACK! Paga 3 para 2!"
        else:
            h["res"], h["motivo"] = "derrota", "O dealer tem Blackjack."
        self.fechar_ronda()

    # ---------- ações do jogador ----------

    def pedir(self):
        if self.estado != "jogador" or self.ocupado:
            return
        self.ocupado = True
        self.dar_mao(self.ativa)
        self.atualizar_botoes()
        self.agendar(500, self.depois_pedir)

    def depois_pedir(self):
        h = self.maos[self.ativa]
        p, _ = self.tot(h)
        if p > 21:
            h["fim"] = True
            self.msg(f"Rebentaste com {p}!", VERMELHO)
            self.agendar(800, self.proxima_mao)
        elif p == 21:
            h["fim"] = True
            self.agendar(450, self.proxima_mao)
        else:
            self.ocupado = False
            self.msg_vez()
            self.atualizar_botoes()

    def msg_vez(self):
        if len(self.maos) == 1:
            self.msg("Queres outra carta ou ficar?", BRANCO)
        else:
            self.msg(f"Mão {self.ativa + 1}: pedir ou ficar?", BRANCO)

    def ficar(self):
        if self.estado != "jogador" or self.ocupado:
            return
        self.maos[self.ativa]["fim"] = True
        self.proxima_mao()

    def dobrar(self):
        if not self.pode_dobrar():
            return
        h = self.maos[self.ativa]
        self.saldo -= h["aposta"]
        h["fichas"] = h["fichas"] * 2
        h["aposta"] *= 2
        h["dobrada"] = True
        self.ocupado = True
        self.atualizar_saldo()
        self.som.tocar("ficha")
        self.msg("Aposta dobrada! Só mais uma carta...", "#e8a54a")
        self.dar_mao(self.ativa)
        self.atualizar_botoes()
        self.agendar(750, self.depois_dobrar)

    def depois_dobrar(self):
        h = self.maos[self.ativa]
        h["fim"] = True
        p, _ = self.tot(h)
        if p > 21:
            self.msg(f"Rebentaste ao dobrar com {p}!", VERMELHO)
        self.agendar(600, self.proxima_mao)

    def dividir(self):
        if not self.pode_dividir():
            return
        h = self.maos[self.ativa]
        self.saldo -= h["aposta"]
        segunda = h["itens"].pop()
        nova = self.nova_mao(h["aposta"], list(h["fichas"]))
        nova["itens"] = [segunda]
        h["split"] = nova["split"] = True
        if h["itens"][0]["carta"][0] == "A":
            h["so_uma"] = nova["so_uma"] = True
        self.maos.insert(self.ativa + 1, nova)
        self.relayout_jogador()
        self.ocupado = True
        self.atualizar_saldo()
        self.som.tocar("ficha")
        self.msg("Mão dividida!", "#a98be0")
        self.atualizar_botoes()
        self.agendar(450, self.depois_dividir)

    def depois_dividir(self):
        self.dar_mao(self.ativa)
        self.agendar(600, self.depois_chegar_mao)

    def desistir(self):
        if not self.pode_desistir():
            return
        h = self.maos[0]
        h["desistiu"] = True
        h["fim"] = True
        self.ocupado = True
        self.atualizar_botoes()
        self.fim_vez_jogador()

    def sugestao(self):
        if self.estado != "jogador" or self.ocupado:
            return
        h = self.maos[self.ativa]
        cartas = [i["carta"] for i in h["itens"]]
        letra, motivo = acao_basica(
            cartas, self.dealer[0]["carta"], self.pode_dobrar(),
            self.pode_dividir(), self.pode_desistir())
        self.msg(f"Sugestão: {NOMES[letra]}  ({motivo})", AZUL_CLARO)

    # ---------- avançar entre mãos ----------

    def proxima_mao(self):
        self.ocupado = True
        self.atualizar_botoes()
        prox = None
        for i in range(self.ativa + 1, len(self.maos)):
            if not self.maos[i]["fim"]:
                prox = i
                break
        if prox is None:
            self.fim_vez_jogador()
            return
        self.ativa = prox
        h = self.maos[prox]
        if len(h["itens"]) == 1:
            self.dar_mao(prox)
            self.agendar(600, self.depois_chegar_mao)
        else:
            self.depois_chegar_mao()

    def depois_chegar_mao(self):
        h = self.maos[self.ativa]
        p, _ = self.tot(h)
        if h["so_uma"] or p >= 21:
            h["fim"] = True
            self.agendar(450, self.proxima_mao)
        else:
            self.ocupado = False
            self.msg_vez()
            self.atualizar_botoes()

    def fim_vez_jogador(self):
        vivas = [h for h in self.maos
                 if not h["desistiu"] and self.tot(h)[0] <= 21]
        if vivas:
            self.iniciar_dealer()
        elif any(self.tot(h)[0] > 21 for h in self.maos):
            self.revelar_dealer()
            self.agendar(800, self.resolver)
        else:
            self.resolver()

    # ---------- dealer ----------

    def iniciar_dealer(self):
        self.estado = "dealer"
        self.ocupado = True
        self.msg("Vez do dealer...", BRANCO)
        self.revelar_dealer()
        self.atualizar_botoes()
        self.agendar(750, self.passo_dealer)

    def passo_dealer(self):
        p, soft = self.tot(self.dealer)
        if p < 17 or (p == 17 and soft and self.cfg["soft17"]):
            self.dar_dealer()
            self.agendar(700, self.passo_dealer)
        else:
            self.resolver()

    def resolver(self):
        pd, _ = self.tot(self.dealer)
        for h in self.maos:
            if h["desistiu"]:
                h["res"] = "desistir"
                h["motivo"] = "Desististe. Recuperas metade da aposta."
                continue
            pj, _ = self.tot(h)
            if pj > 21:
                h["res"], h["motivo"] = "derrota", f"Rebentaste com {pj}."
            elif pd > 21:
                h["res"] = "vitoria"
                h["motivo"] = f"O dealer rebentou com {pd}! Ganhaste!"
            elif pj > pd:
                h["res"], h["motivo"] = "vitoria", f"Ganhaste! {pj} contra {pd}."
            elif pj < pd:
                h["res"] = "derrota"
                h["motivo"] = f"O dealer ganhou. {pd} contra {pj}."
            else:
                h["res"] = "empate"
                h["motivo"] = f"Empate com {pj}. Aposta devolvida."
        self.fechar_ronda()

    # ---------- pagamento e estatísticas ----------

    def fechar_ronda(self):
        d = self.dados
        net_total = 0
        d["rondas"] += 1
        ctx = {"dobrar": False, "dividir": False}

        for h in self.maos:
            ap, res = h["aposta"], h["res"]
            if res == "vitoria":
                self.saldo += ap * 2
                net = ap
                d["vitorias"] += 1
                d["serie"] += 1
            elif res == "blackjack":
                extra = int(ap * 1.5)
                self.saldo += ap + extra
                net = extra
                d["vitorias"] += 1
                d["blackjacks"] += 1
                d["serie"] += 1
            elif res == "empate":
                self.saldo += ap
                net = 0
                d["empates"] += 1
            elif res == "desistir":
                volta = ap // 2
                self.saldo += volta
                net = -(ap - volta)
                d["derrotas"] += 1
                d["serie"] = 0
            else:
                net = -ap
                d["derrotas"] += 1
                d["serie"] = 0
            d["melhor_serie"] = max(d["melhor_serie"], d["serie"])
            if res in ("vitoria", "blackjack"):
                ctx["dobrar"] |= h["dobrada"]
                ctx["dividir"] |= h["split"]
            net_total += net

        net_total += self.seguro_net
        d["maior_ganho"] = max(d["maior_ganho"], net_total)
        if self.modo == "classico":
            d["saldo_max"] = max(d["saldo_max"], self.saldo)
            d["historico"].append(self.saldo)
            d["historico"] = d["historico"][-100:]
        d["recentes"].append("V" if net_total > 0 else
                             "D" if net_total < 0 else "E")
        d["recentes"] = d["recentes"][-10:]

        # texto final
        if len(self.maos) == 1:
            base = self.maos[0]["motivo"]
        else:
            base = " | ".join(f"Mão {i + 1}: {NOMES_RES[h['res']]}"
                              for i, h in enumerate(self.maos))
        if self.seguro_net > 0:
            base += " Seguro pago!"
        elif self.seguro_net < 0:
            base += " Seguro perdido."
        sinal = "+" if net_total > 0 else ""
        texto = f"{base} ({sinal}{fmt(net_total)})"

        tem_bj = any(h["res"] == "blackjack" for h in self.maos)
        if net_total > 0:
            self.msg(texto, VERDE)
            self.confetti()
            self.som.tocar("blackjack" if tem_bj else "vitoria")
            self.voo_fichas(True)
        elif net_total < 0:
            self.msg(texto, "#ff7b6b")
            self.som.tocar("derrota")
            self.voo_fichas(False)
        else:
            self.msg(texto, AZUL_CLARO)
            self.som.tocar("empate")

        # conquistas gerais
        if d["blackjacks"] >= 1:
            self.desbloquear("primeiro_bj")
        if d["blackjacks"] >= 5:
            self.desbloquear("bj5")
        if d["melhor_serie"] >= 5:
            self.desbloquear("serie5")
        if d["saldo_max"] >= 5000:
            self.desbloquear("cinco_mil")
        if d["rondas"] >= 50:
            self.desbloquear("veterano")
        if ctx["dobrar"]:
            self.desbloquear("dobrar")
        if ctx["dividir"]:
            self.desbloquear("dividir")
        if self.seguro_net > 0:
            self.desbloquear("seguro")
        if self.all_in and net_total > 0:
            self.desbloquear("tudo")
        if self.saldo < 10:
            self.desbloquear("falencia")

        self.estado = "fim"
        self.ocupado = False
        self.mostrar_seguro(False)
        self.verificar_fim_modo()
        guardar(self.app.save)
        self.atualizar_saldo()
        self.atualizar_botoes()

    def verificar_fim_modo(self):
        d = self.dados
        if self.modo == "classico":
            if self.saldo < 10:
                self.msg(self.mensagem + "  Ficaste sem fichas!", "#ff7b6b")
        elif self.modo == "desafio":
            if self.saldo >= self.objetivo:
                self.modo_terminado = True
                d["desafios_ganhos"] += 1
                self.desbloquear("desafio")
                self.confetti()
                self.msg(f"DESAFIO CONCLUÍDO! {fmt(self.saldo)} fichas!",
                         DOURADO)
            elif self.saldo < 10:
                self.modo_terminado = True
                self.msg("Desafio falhado: ficaste sem fichas.", "#ff7b6b")
        else:
            self.rondas_rest -= 1
            if self.rondas_rest <= 0 or self.saldo < 10:
                self.modo_terminado = True
                texto = f"FIM DO TEMPO! Saldo final: {fmt(self.saldo)}."
                if self.saldo > d["relogio_melhor"]:
                    d["relogio_melhor"] = self.saldo
                    texto += " NOVO RECORDE!"
                if self.saldo >= 1000:
                    self.desbloquear("relogio")
                self.msg(texto, DOURADO)

    def nova_ronda(self):
        if self.estado != "fim" or self.ocupado:
            return
        if self.modo_terminado:
            self.app.mostrar("modos")
            return
        if self.modo == "classico" and self.saldo < 10:
            self.dados["falencias"] += 1
            self.saldo = 1000
            guardar(self.app.save)
        self.geracao += 1
        self.limpar_estado_ronda()
        self.msg("Faz a tua aposta!", DOURADO)
        self.atualizar_saldo()
        self.atualizar_botoes()

    # ------------------------------------------------------
    # efeitos
    # ------------------------------------------------------

    def confetti(self):
        cores = [DOURADO, BRANCO, "#ff7b6b", VERDE, AZUL_CLARO]
        for _ in range(80):
            ang = random.uniform(math.pi, 2 * math.pi)
            vel = random.uniform(3, 11)
            self.particulas.append({
                "x": CX, "y": 235, "vx": math.cos(ang) * vel,
                "vy": math.sin(ang) * vel, "vida": random.randint(45, 85),
                "cor": random.choice(cores), "t": random.randint(3, 6),
            })

    def voo_fichas(self, ganhou):
        """Fichas a voar: da banca para o jogador (vitória) ou para o dealer."""
        fichas = self.fichas_display()[:8] or [25]
        for i, v in enumerate(fichas):
            cor = COR_FICHA.get(v, "#D94343")
            if ganhou:
                x0, y0, x1, y1 = CX, 40, CX + (i - len(fichas) / 2) * 14, 490
            else:
                x0, y0 = CX + (i - len(fichas) / 2) * 14, 490
                x1, y1 = CX, -40
            self.voos.append({"x": x0, "y": y0, "tx": x1, "ty": y1,
                              "valor": v, "cor": cor, "atraso": i * 4})
        if not ganhou:
            self.mostrar_fichas = False

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

            if self.voos:
                for v in self.voos:
                    if v["atraso"] > 0:
                        v["atraso"] -= 1
                    else:
                        v["x"] += (v["tx"] - v["x"]) * 0.16
                        v["y"] += (v["ty"] - v["y"]) * 0.16
                self.voos = [v for v in self.voos
                             if v["atraso"] > 0
                             or abs(v["ty"] - v["y"]) > 6
                             or abs(v["tx"] - v["x"]) > 6]
                mexeu = True

            if self.toasts:
                self.toasts[0]["tempo"] -= 1
                if self.toasts[0]["tempo"] <= 0:
                    self.toasts.pop(0)
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

        rrect(c, 890, 10, 1090, 550, 22, tags="fundo",
              fill=misturar(escuro, "#000000", 0.5),
              outline=DOURADO, width=2)
        c.create_text(990, 34, text="FICHAS", fill=DOURADO,
                      font=("Georgia", 16, "bold"), tags="fundo")
        c.create_text(990, 58, text="clica ou arrasta", fill=BRANCO,
                      font=("Arial", 9, "italic"), tags="fundo")
        for f in FICHAS_TIPOS:
            ficha_topo(c, CHIP_X, f["y"], f["valor"], f["cor"], tags="fundo")
        c.create_text(990, 524,
                      text="Clica na aposta para\nremover a última ficha",
                      fill="#9aa5a0", font=("Arial", 8), justify="center",
                      tags="fundo")
        c.tag_lower("fundo")

    @staticmethod
    def chegou(it):
        return abs(it["x"] - it["tx"]) < 3 and abs(it["y"] - it["ty"]) < 3

    def placar(self, itens, cx, y, nome, dealer=False, ativo=False):
        c = self.cv
        cor_nome = DOURADO if ativo else BRANCO
        visiveis = [i["carta"] for i in itens
                    if not i["oculta"] and self.chegou(i)]
        if not visiveis:
            c.create_text(cx, y, text=nome, fill=cor_nome,
                          font=("Georgia", 15, "bold"), tags="dyn")
            return
        tot, soft = calcular(visiveis)
        texto = str(tot)
        if soft and tot < 21:
            texto = f"{tot - 10} / {tot}"
        if tot > 21:
            texto = "REBENTOU"
        if dealer and any(i["oculta"] for i in itens):
            texto += " + ?"
        cor = VERMELHO if tot > 21 else (DOURADO if tot == 21 else "#0b1712")
        fg = BRANCO if tot > 21 else (BG if tot == 21 else DOURADO)
        c.create_text(cx - 10, y, text=nome, fill=cor_nome, anchor="e",
                      font=("Georgia", 15, "bold"), tags="dyn")
        t = c.create_text(cx + 22, y, text=texto, fill=fg, anchor="w",
                          font=("Arial", 12, "bold"), tags="dyn")
        x1, y1, x2, y2 = c.bbox(t)
        p = rrect(c, x1 - 10, y1 - 3, x2 + 10, y2 + 3, 12,
                  fill=cor, outline=DOURADO, width=2)
        c.tag_lower(p, t)

    def desenhar_aposta(self):
        c = self.cv
        cx, base = CX, 505
        fichas = self.fichas_display() if self.mostrar_fichas else []
        if not fichas:
            if self.estado == "apostar":
                c.create_oval(cx - 58, base - 42, cx + 58, base + 22,
                              outline=DOURADO, dash=(6, 5), width=2,
                              tags="dyn")
                c.create_text(cx, base - 10, text="ARRASTA AS\nFICHAS AQUI",
                              fill=DOURADO, font=("Arial", 9, "bold"),
                              justify="center", tags="dyn")
            return
        pilhas = {}
        for v in fichas:
            pilhas[v] = pilhas.get(v, 0) + 1
        chaves = sorted(pilhas)
        k = len(chaves)
        for idx, v in enumerate(chaves):
            sx = cx + (idx - (k - 1) / 2) * 64
            n = min(pilhas[v], 10)
            for j in range(n):
                ficha_plana(c, sx, base - j * 5, v, COR_FICHA[v], j == n - 1)
            if pilhas[v] > 10:
                c.create_text(sx + 34, base - 10, text=f"×{pilhas[v]}",
                              fill=BRANCO, anchor="w",
                              font=("Arial", 9, "bold"), tags="dyn")
        total = self.aposta if self.estado == "apostar" else \
            sum(h["aposta"] for h in self.maos)
        c.create_text(cx, 432, text=f"APOSTA: {fmt(total)}", fill=DOURADO,
                      font=("Georgia", 14, "bold"), tags="dyn")

    def desenhar_hud(self):
        c = self.cv
        if self.modo == "desafio":
            c.create_text(34, 38, anchor="w", fill=DOURADO, tags="dyn",
                          text=f"DESAFIO: chegar a {fmt(self.objetivo)}",
                          font=("Arial", 10, "bold"))
        elif self.modo == "relogio":
            c.create_text(34, 38, anchor="w", fill=DOURADO, tags="dyn",
                          text=f"CONTRA-RELÓGIO: {self.rondas_rest} rondas",
                          font=("Arial", 10, "bold"))
        # últimas rondas
        rec = self.dados["recentes"][-7:]
        if rec:
            c.create_text(34, 482, text="ÚLTIMAS", anchor="w", fill="#cfd8d3",
                          font=("Arial", 8, "bold"), tags="dyn")
            cores = {"V": VERDE, "D": VERMELHO, "E": AZUL_CLARO}
            for i, r in enumerate(rec):
                x = 44 + i * 22
                c.create_oval(x - 9, 498, x + 9, 516, fill=cores[r],
                              outline="", tags="dyn")
                c.create_text(x, 507, text=r, fill=BG,
                              font=("Arial", 8, "bold"), tags="dyn")

    def desenhar(self):
        self.desenhar_fundo()
        c = self.cv
        c.delete("dyn")
        sombra = misturar(TEMAS[self.cfg["tema"]][0], "#000000", 0.6)

        self.desenhar_hud()

        # sapato
        for i in (2, 1, 0):
            carta_cv(c, SHOE_X + i * 3, SHOE_Y - i * 3, None, True,
                     sombra=sombra)
        c.create_text(SHOE_X + 42, SHOE_Y + 140,
                      text=f"SAPATO · {len(self.sapato)}", fill=BRANCO,
                      font=("Arial", 9, "bold"), tags="dyn")

        # nomes e pontuações
        self.placar(self.dealer, CX, 24, "DEALER", dealer=True)
        n = len(self.maos)
        if not n:
            self.placar([], CX, 268, "JOGADOR")
        for i, h in enumerate(self.maos):
            nome = "JOGADOR" if n == 1 else f"MÃO {i + 1}"
            ativo = n > 1 and self.estado == "jogador" and i == self.ativa
            self.placar(h["itens"], h["cx"], 268, nome, ativo=ativo)
            if n > 1:
                c.create_text(h["cx"], 414, text=f"Aposta {fmt(h['aposta'])}",
                              fill=BRANCO, font=("Arial", 10, "bold"),
                              tags="dyn")
            if ativo and h["itens"]:
                x0 = min(it["tx"] for it in h["itens"]) - 9
                x1 = max(it["tx"] for it in h["itens"]) + CARTA_W + 9
                rrect(c, x0, 276, x1, 285 + CARTA_H + 9, 14, fill="",
                      outline=DOURADO, width=2, dash=(6, 4))

        # cartas
        for it in self.itens:
            carta_cv(c, it["x"], it["y"], it["carta"], it["oculta"],
                     it["sx"], sombra=sombra)

        self.desenhar_aposta()

        # mensagem
        if self.mensagem:
            y = 205 if self.estado == "seguro" else 228
            t = c.create_text(CX, y, text=self.mensagem, fill=self.msg_cor,
                              font=("Georgia", 16, "bold"), tags="dyn")
            x1, y1, x2, y2 = c.bbox(t)
            p = rrect(c, x1 - 22, y1 - 9, x2 + 22, y2 + 9, 18,
                      fill="#0b1712", outline=self.msg_cor, width=2)
            c.tag_lower(p, t)

        # contagem Hi-Lo
        if self.cfg["contagem"]:
            baralhos = max(len(self.sapato) / 52, 0.5)
            real = self.contagem / baralhos
            c.create_text(34, 536, anchor="w", fill=DOURADO, tags="dyn",
                          text=f"Hi-Lo: {self.contagem:+d}   "
                               f"Verdadeira: {real:+.1f}",
                          font=("Arial", 10, "bold"))

        # fichas a voar
        for v in self.voos:
            if v["atraso"] <= 0:
                ficha_topo(c, v["x"], v["y"], v["valor"], v["cor"], r=20)

        # confetti
        for p in self.particulas:
            s = p["t"]
            c.create_rectangle(p["x"], p["y"], p["x"] + s, p["y"] + s,
                               fill=p["cor"], outline="", tags="dyn")

        # conquista desbloqueada
        if self.toasts:
            t = self.toasts[0]
            rrect(c, 26, 60, 262, 122, 14, fill="#0b1712", outline=DOURADO,
                  width=2)
            c.create_text(40, 80, anchor="w", text="★ CONQUISTA DESBLOQUEADA",
                          fill=DOURADO, font=("Arial", 8, "bold"), tags="dyn")
            c.create_text(40, 103, anchor="w", text=t["nome"], fill=BRANCO,
                          font=("Georgia", 13, "bold"), tags="dyn")

        # ficha a ser arrastada
        if self.arrastar:
            a = self.arrastar
            ficha_topo(c, a["x"], a["y"], a["valor"], a["cor"], r=31)