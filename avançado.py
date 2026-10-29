
import tkinter as tk
import random

# ==========================================
# CONFIGURACOES
# ==========================================

BG = "#101820"
MESA = "#126044"
DOURADO = "#E8BD61"
BRANCO = "#FFFFFF"
VERMELHO = "#D94343"
PRETO = "#171717"

LARGURA = 1100
ALTURA = 520

NAIPES = ["♠", "♥", "♦", "♣"]

VALORES = [
    "A", "2", "3", "4", "5", "6", "7",
    "8", "9", "10", "J", "Q", "K"
]

# Fichas disponiveis
FICHAS_TIPOS = [
    {"valor": 10, "cor": "#2878D0", "y": 145},
    {"valor": 25, "cor": "#D94343", "y": 225},
    {"valor": 50, "cor": "#269B62", "y": 305},
    {"valor": 100, "cor": "#252525", "y": 385}
]


class Blackjack:

    def __init__(self, root):

        self.root = root
        self.root.title("BLACKJACK ROYALE")
        self.root.geometry("1100x700")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        # Sistema de fichas
        self.fichas = 1000
        self.aposta = 0
        self.fichas_aposta = []

        # Estatisticas
        self.vitorias = 0
        self.derrotas = 0
        self.empates = 0

        # Cartas
        self.jogador = []
        self.dealer = []
        self.cartas_visuais = []
        self.baralho = []

        # Estado do jogo
        self.estado = "inicio"
        self.animacao = False
        self.mensagem = "Arrasta as fichas para a zona de aposta!"

        # Arrastamento de fichas
        self.arrastar = None

        # ======================================
        # TITULO
        # ======================================

        tk.Label(
            root,
            text="BLACKJACK ROYALE",
            font=("Arial", 27, "bold"),
            fg=DOURADO,
            bg=BG
        ).pack(pady=(7, 2))

        self.saldo_label = tk.Label(
            root,
            text="SALDO: 1.000 FICHAS",
            font=("Arial", 14, "bold"),
            fg=DOURADO,
            bg=BG
        )

        self.saldo_label.pack(pady=3)

        # ======================================
        # MESA
        # ======================================

        self.canvas = tk.Canvas(
            root,
            width=LARGURA,
            height=ALTURA,
            bg=MESA,
            highlightthickness=4,
            highlightbackground=DOURADO
        )

        self.canvas.pack(pady=4)

        # Eventos para arrastar fichas
        self.canvas.bind(
            "<ButtonPress-1>",
            self.iniciar_arrastamento
        )

        self.canvas.bind(
            "<B1-Motion>",
            self.mover_ficha
        )

        self.canvas.bind(
            "<ButtonRelease-1>",
            self.largar_ficha
        )

        # ======================================
        # BOTOES
        # ======================================

        self.controlos = tk.Frame(
            root,
            bg=BG
        )

        self.controlos.pack(pady=7)

        self.btn_comecar = self.criar_botao(
            "COMEÇAR RONDA",
            self.comecar_ronda
        )

        self.btn_pedir = self.criar_botao(
            "PEDIR CARTA",
            self.pedir_carta
        )

        self.btn_ficar = self.criar_botao(
            "FICAR",
            self.ficar
        )

        self.btn_limpar = self.criar_botao(
            "LIMPAR APOSTA",
            self.limpar_aposta
        )

        self.btn_novo = self.criar_botao(
            "NOVA RONDA",
            self.voltar_inicio
        )

        self.atualizar_botoes()
        self.desenhar_mesa()

    # ==========================================
    # CRIAR BOTOES
    # ==========================================

    def criar_botao(self, texto, comando):

        botao = tk.Button(
            self.controlos,
            text=texto,
            command=comando,
            font=("Arial", 9, "bold"),
            bg=DOURADO,
            fg=BG,
            activebackground="#F5D88D",
            relief="flat",
            cursor="hand2",
            width=15,
            height=2
        )

        botao.pack(side="left", padx=5)

        return botao

    # ==========================================
    # ATUALIZAR INTERFACE
    # ==========================================

    def atualizar_saldo(self):

        saldo = f"{self.fichas:,}".replace(",", ".")

        self.saldo_label.config(
            text=f"SALDO: {saldo} FICHAS"
        )

    def atualizar_botoes(self):

        ativo = (
            self.estado == "jogador"
            and not self.animacao
        )

        self.btn_pedir.config(
            state="normal" if ativo else "disabled"
        )

        self.btn_ficar.config(
            state="normal" if ativo else "disabled"
        )

        self.btn_comecar.config(
            state="normal"
            if self.estado == "inicio"
            and self.fichas >= 10
            and self.aposta >= 10
            and not self.animacao
            else "disabled"
        )

        self.btn_limpar.config(
            state="normal"
            if self.estado == "inicio" and self.aposta > 0
            else "disabled"
        )

        self.btn_novo.config(
            state="normal"
            if self.estado == "fim" and not self.animacao
            else "disabled"
        )

    # ==========================================
    # DESENHAR FICHAS
    # ==========================================

    def desenhar_ficha(self, x, y, valor, cor, raio=26):

        # Circulo exterior
        self.canvas.create_oval(
            x - raio, y - raio,
            x + raio, y + raio,
            fill=BRANCO,
            outline=BRANCO,
            width=2
        )

        # Interior
        self.canvas.create_oval(
            x - raio + 4, y - raio + 4,
            x + raio - 4, y + raio - 4,
            fill=cor,
            outline=BRANCO,
            width=2
        )

        # Detalhes
        for angulo in range(0, 360, 45):

            import math

            rad = math.radians(angulo)

            px = x + (raio - 9) * math.cos(rad)
            py = y + (raio - 9) * math.sin(rad)

            self.canvas.create_oval(
                px - 2, py - 2,
                px + 2, py + 2,
                fill=BRANCO,
                outline=BRANCO
            )

        self.canvas.create_text(
            x, y,
            text=str(valor),
            fill=BRANCO,
            font=("Arial", 11, "bold")
        )

    # ==========================================
    # PAINEL DE FICHAS
    # ==========================================

    def desenhar_painel_fichas(self):

        self.canvas.create_rectangle(
            905, 12, 1088, 508,
            fill="#174B3A",
            outline=DOURADO,
            width=2
        )

        self.canvas.create_text(
            996, 48,
            text="AS TUAS FICHAS",
            fill=DOURADO,
            font=("Arial", 12, "bold")
        )

        self.canvas.create_text(
            996, 75,
            text="ARRASTA PARA A MESA",
            fill=BRANCO,
            font=("Arial", 8, "bold")
        )

        for ficha in FICHAS_TIPOS:

            x = 996
            y = ficha["y"]

            self.desenhar_ficha(
                x,
                y,
                ficha["valor"],
                ficha["cor"]
            )

            self.canvas.create_text(
                996, y + 38,
                text=f"{ficha['valor']} FICHAS",
                fill=BRANCO,
                font=("Arial", 9, "bold")
            )

    # ==========================================
    # ZONA DE APOSTA
    # ==========================================

    def desenhar_zona_aposta(self):

        self.canvas.create_rectangle(
            390, 392, 880, 462,
            fill="#104C38",
            outline=DOURADO,
            width=2
        )

        self.canvas.create_text(
            635, 403,
            text="ZONA DE APOSTA",
            fill=DOURADO,
            font=("Arial", 11, "bold")
        )

        self.canvas.create_text(
            635, 447,
            text=f"TOTAL: {self.aposta} FICHAS",
            fill=BRANCO,
            font=("Arial", 12, "bold")
        )

        # Mostrar fichas colocadas
        for i, valor in enumerate(self.fichas_aposta[:18]):

            ficha = next(
                f for f in FICHAS_TIPOS
                if f["valor"] == valor
            )

            x = 425 + (i % 9) * 42
            y = 430 - (i // 9) * 19

            self.desenhar_ficha(
                x,
                y,
                valor,
                ficha["cor"],
                raio=14
            )

        if len(self.fichas_aposta) > 18:

            self.canvas.create_text(
                850, 430,
                text=f"+{len(self.fichas_aposta) - 18}",
                fill=BRANCO,
                font=("Arial", 11, "bold")
            )

    # ==========================================
    # SISTEMA DE ARRASTAR FICHAS
    # ==========================================

    def iniciar_arrastamento(self, evento):

        if self.estado != "inicio":
            return

        if self.animacao:
            return

        x = evento.x
        y = evento.y

        for ficha in FICHAS_TIPOS:

            if (
                abs(x - 996) <= 30
                and abs(y - ficha["y"]) <= 30
            ):

                self.arrastar = {
                    "valor": ficha["valor"],
                    "cor": ficha["cor"],
                    "x": x,
                    "y": y
                }

                self.desenhar_mesa()

                self.desenhar_ficha(
                    x,
                    y,
                    ficha["valor"],
                    ficha["cor"],
                    raio=29
                )

                return

    def mover_ficha(self, evento):

        if self.arrastar is None:
            return

        self.arrastar["x"] = evento.x
        self.arrastar["y"] = evento.y

        self.desenhar_mesa()

        # Ficha a acompanhar o rato
        self.desenhar_ficha(
            evento.x,
            evento.y,
            self.arrastar["valor"],
            self.arrastar["cor"],
            raio=29
        )

    def largar_ficha(self, evento):

        if self.arrastar is None:
            return

        valor = self.arrastar["valor"]

        x = evento.x
        y = evento.y

        # Verificar se foi largada na zona correta
        dentro_da_zona = (
            390 <= x <= 880
            and 392 <= y <= 462
        )

        if dentro_da_zona:

            if self.aposta + valor <= self.fichas:

                self.aposta += valor
                self.fichas_aposta.append(valor)

                self.mensagem = "Ficha adicionada a tua aposta!"

            else:

                self.mensagem = "Nao tens fichas suficientes!"

        self.arrastar = None

        self.atualizar_botoes()
        self.desenhar_mesa()

    def limpar_aposta(self):

        if self.estado != "inicio":
            return

        self.aposta = 0
        self.fichas_aposta = []

        self.mensagem = "Aposta limpa! Escolhe novamente."

        self.atualizar_botoes()
        self.desenhar_mesa()

    # ==========================================
    # BARALHO
    # ==========================================

    def criar_baralho(self):

        self.baralho = [
            (valor, naipe)
            for naipe in NAIPES
            for valor in VALORES
        ]

        random.shuffle(self.baralho)

    def retirar_carta(self):

        if not self.baralho:
            self.criar_baralho()

        return self.baralho.pop()

    # ==========================================
    # PONTUACAO
    # ==========================================

    def calcular_pontos(self, cartas):

        total = 0
        ases = 0

        for valor, naipe in cartas:

            if valor == "A":

                total += 11
                ases += 1

            elif valor in ["J", "Q", "K"]:

                total += 10

            else:

                total += int(valor)

        while total > 21 and ases > 0:

            total -= 10
            ases -= 1

        return total

    # ==========================================
    # DESENHAR CARTAS
    # ==========================================

    def desenhar_carta(self, x, y, carta, oculta=False):

        largura = 65
        altura = 95

        self.canvas.create_rectangle(
            x, y,
            x + largura, y + altura,
            fill=BRANCO,
            outline="#CCCCCC",
            width=2
        )

        if oculta:

            self.canvas.create_rectangle(
                x + 5, y + 5,
                x + largura - 5,
                y + altura - 5,
                fill="#183B69",
                outline=DOURADO,
                width=2
            )

            self.canvas.create_text(
                x + 32, y + 47,
                text="♠",
                fill=DOURADO,
                font=("Arial", 27, "bold")
            )

            return

        valor, naipe = carta

        cor = (
            VERMELHO
            if naipe in ["♥", "♦"]
            else PRETO
        )

        self.canvas.create_text(
            x + 13, y + 14,
            text=valor,
            fill=cor,
            font=("Arial", 13, "bold")
        )

        self.canvas.create_text(
            x + 32, y + 48,
            text=naipe,
            fill=cor,
            font=("Arial", 27)
        )

        self.canvas.create_text(
            x + 52, y + 80,
            text=valor,
            fill=cor,
            font=("Arial", 13, "bold")
        )

    # ==========================================
    # DESENHAR MESA
    # ==========================================

    def desenhar_mesa(self):

        self.canvas.delete("all")

        # Mesa principal
        self.canvas.create_rectangle(
            12, 12, 895, 508,
            outline=DOURADO,
            width=2
        )

        # Dealer
        self.canvas.create_text(
            440, 28,
            text="DEALER",
            font=("Arial", 16, "bold"),
            fill=BRANCO
        )

        # Pontuacao dealer
        if self.estado in [
            "inicio", "distribuindo", "jogador"
        ]:

            pontos = (
                self.calcular_pontos(self.dealer[:1])
                if self.dealer else 0
            )

            texto = f"{pontos} + ?"

        else:

            texto = str(
                self.calcular_pontos(self.dealer)
            )

        self.canvas.create_text(
            440, 52,
            text=f"Pontuacao: {texto}",
            font=("Arial", 12, "bold"),
            fill=DOURADO
        )

        # Jogador
        self.canvas.create_text(
            440, 207,
            text="JOGADOR",
            font=("Arial", 16, "bold"),
            fill=BRANCO
        )

        self.canvas.create_text(
            440, 232,
            text=f"Pontuacao: {self.calcular_pontos(self.jogador)}",
            font=("Arial", 12, "bold"),
            fill=DOURADO
        )

        # Cartas
        for item in self.cartas_visuais:

            self.desenhar_carta(
                item["x"],
                item["y"],
                item["carta"],
                item["oculta"]
            )

        # Zona de aposta
        self.desenhar_zona_aposta()

        # Mensagem
        self.canvas.create_text(
            440, 480,
            text=self.mensagem,
            font=("Arial", 13, "bold"),
            fill=DOURADO
        )

        # Estatisticas
        self.canvas.create_text(
            440, 496,
            text=(
                f"Vitorias: {self.vitorias}    "
                f"Derrotas: {self.derrotas}    "
                f"Empates: {self.empates}"
            ),
            font=("Arial", 10, "bold"),
            fill=BRANCO
        )

        # Painel lateral
        self.desenhar_painel_fichas()

        # Ficha que esta a ser arrastada
        if self.arrastar is not None:

            self.desenhar_ficha(
                self.arrastar["x"],
                self.arrastar["y"],
                self.arrastar["valor"],
                self.arrastar["cor"],
                raio=29
            )

    # ==========================================
    # ANIMACAO DE DISTRIBUICAO
    # ==========================================

    def animar_carta(
        self, carta, jogador, oculta, callback
    ):

        grupo = self.jogador if jogador else self.dealer

        destino_x = 440 - (len(grupo) - 1) * 38

        destino_y = 270 if jogador else 80

        item = {
            "carta": carta,
            "x": 850,
            "y": 250,
            "oculta": oculta
        }

        self.cartas_visuais.append(item)

        inicio_x = item["x"]
        inicio_y = item["y"]

        passos = 15
        passo = 0

        def mover():

            nonlocal passo

            passo += 1

            progresso = passo / passos

            item["x"] = (
                inicio_x +
                (destino_x - inicio_x) * progresso
            )

            item["y"] = (
                inicio_y +
                (destino_y - inicio_y) * progresso
            )

            self.desenhar_mesa()

            if passo < passos:

                self.root.after(18, mover)

            else:

                item["x"] = destino_x
                item["y"] = destino_y

                self.desenhar_mesa()

                callback()

        mover()

    # ==========================================
    # COMEÇAR RONDA
    # ==========================================

    def comecar_ronda(self):

        if self.estado != "inicio" or self.animacao:
            return

        if self.aposta < 10:

            self.mensagem = "Coloca pelo menos 10 fichas na mesa!"
            self.desenhar_mesa()
            return

        if self.aposta > self.fichas:

            self.mensagem = "Nao tens fichas suficientes!"
            self.desenhar_mesa()
            return

        # Descontar fichas
        self.fichas -= self.aposta

        self.atualizar_saldo()

        # Preparar baralho e cartas
        self.jogador = []
        self.dealer = []
        self.cartas_visuais = []

        self.criar_baralho()

        self.estado = "distribuindo"
        self.animacao = True

        self.mensagem = "A distribuir as cartas..."

        self.atualizar_botoes()
        self.desenhar_mesa()

        distribuicao = [
            (self.jogador, True, False),
            (self.dealer, False, False),
            (self.jogador, True, False),
            (self.dealer, False, True)
        ]

        def distribuir(indice):

            if indice >= len(distribuicao):

                self.animacao = False
                self.estado = "jogador"

                self.mensagem = "A tua vez! Escolhe uma opcao."

                self.desenhar_mesa()
                self.atualizar_botoes()

                if self.calcular_pontos(self.jogador) == 21:

                    self.ficar()

                return

            grupo, jogador, oculta = distribuicao[indice]

            carta = self.retirar_carta()

            grupo.append(carta)

            self.animar_carta(
                carta,
                jogador,
                oculta,
                lambda: distribuir(indice + 1)
            )

        distribuir(0)

    # ==========================================
    # PEDIR CARTA
    # ==========================================

    def pedir_carta(self):

        if self.estado != "jogador" or self.animacao:
            return

        carta = self.retirar_carta()

        self.jogador.append(carta)

        self.animacao = True

        self.atualizar_botoes()

        self.animar_carta(
            carta,
            True,
            False,
            self.finalizar_carta
        )

    def finalizar_carta(self):

        self.animacao = False

        pontos = self.calcular_pontos(self.jogador)

        if pontos > 21:

            self.revelar_dealer()

            self.mensagem = "Passaste os 21! Perdeste a ronda."

            self.terminar("derrota")

        elif pontos == 21:

            self.ficar()

        else:

            self.mensagem = "Queres outra carta ou ficar?"

        self.desenhar_mesa()
        self.atualizar_botoes()

    # ==========================================
    # REVELAR CARTA
    # ==========================================

    def revelar_dealer(self):

        for item in self.cartas_visuais:

            item["oculta"] = False

    # ==========================================
    # FICAR
    # ==========================================

    def ficar(self):

        if self.estado != "jogador" or self.animacao:
            return

        self.estado = "dealer"
        self.animacao = True

        self.revelar_dealer()

        self.desenhar_mesa()

        self.jogar_dealer()

    # ==========================================
    # VEZ DO DEALER
    # ==========================================

    def jogar_dealer(self):

        pontos = self.calcular_pontos(self.dealer)

        if pontos < 17:

            carta = self.retirar_carta()

            self.dealer.append(carta)

            self.animar_carta(
                carta,
                False,
                False,
                self.jogar_dealer
            )

        else:

            self.animacao = False

            self.verificar_vencedor()

    # ==========================================
    # VERIFICAR RESULTADO
    # ==========================================

    def verificar_vencedor(self):

        pontos_jogador = self.calcular_pontos(self.jogador)

        pontos_dealer = self.calcular_pontos(self.dealer)

        if pontos_dealer > 21:

            self.mensagem = "O dealer passou dos 21! GANHASTE!"

            self.terminar("vitoria")

        elif pontos_jogador > pontos_dealer:

            self.mensagem = "Parabens! GANHASTE!"

            self.terminar("vitoria")

        elif pontos_jogador < pontos_dealer:

            self.mensagem = "O dealer ganhou. Boa sorte!"

            self.terminar("derrota")

        else:

            self.mensagem = "Empate! Recuperaste as fichas."

            self.terminar("empate")

    # ==========================================
    # PAGAMENTO DAS FICHAS
    # ==========================================

    def terminar(self, resultado):

        self.estado = "fim"
        self.animacao = False

        if resultado == "vitoria":

            self.vitorias += 1

            # Devolver aposta e pagar premio igual
            self.fichas += self.aposta * 2

        elif resultado == "derrota":

            self.derrotas += 1

        elif resultado == "empate":

            self.empates += 1

            # Devolver aposta
            self.fichas += self.aposta

        self.atualizar_saldo()

        if self.fichas < 10:

            self.mensagem = "Saldo insuficiente para outra ronda!"

        self.desenhar_mesa()
        self.atualizar_botoes()

    # ==========================================
    # NOVA RONDA
    # ==========================================

    def voltar_inicio(self):

        if self.animacao:
            return

        self.estado = "inicio"

        self.aposta = 0
        self.fichas_aposta = []

        self.jogador = []
        self.dealer = []
        self.cartas_visuais = []

        self.mensagem = "Arrasta as fichas para a zona de aposta!"

        self.atualizar_saldo()
        self.desenhar_mesa()
        self.atualizar_botoes()


# ==========================================
# EXECUTAR JOGO
# ==========================================

if __name__ == "__main__":

    janela = tk.Tk()

    jogo = Blackjack(janela)

    janela.mainloop()
