
import tkinter as tk
import random

# ---------- CONFIGURACAO ----------
BG = "#0B382B"
PANEL = "#124838"
GOLD = "#E5BD61"
WHITE = "#FFFFFF"

saldo = 1000
aposta = 100
baralho = []
jogador = []
dealer = []
em_jogo = False


# ---------- CARTAS E REGRAS ----------
def criar_baralho():
    naipes = ["♠", "♥", "♦", "♣"]
    valores = [
        ("A", 11), ("2", 2), ("3", 3), ("4", 4),
        ("5", 5), ("6", 6), ("7", 7), ("8", 8),
        ("9", 9), ("10", 10), ("J", 10),
        ("Q", 10), ("K", 10)
    ]

    cartas = [
        {"nome": nome, "valor": valor, "naipe": naipe}
        for naipe in naipes
        for nome, valor in valores
    ]
    random.shuffle(cartas)
    return cartas


def pontuacao(mao):
    total = sum(carta["valor"] for carta in mao)
    ases = sum(1 for carta in mao if carta["nome"] == "A")

    while total > 21 and ases > 0:
        total -= 10
        ases -= 1

    return total


def texto_cartas(mao):
    return "   ".join(
        f'{c["nome"]}{c["naipe"]}' for c in mao
    )


def cor_cartas(mao):
    return "#F06464" if any(
        c["naipe"] in ("♥", "♦") for c in mao
    ) else WHITE


def atualizar_saldo():
    lbl_saldo.config(text=f"Saldo: {saldo} fichas")


def atualizar_mesa(esconder_dealer=False):
    lbl_jogador.config(text=texto_cartas(jogador))
    lbl_pontos_jogador.config(
        text=f"Pontos: {pontuacao(jogador)}"
    )
    lbl_jogador.config(fg=cor_cartas(jogador))

    if esconder_dealer:
        lbl_dealer.config(text=f"{dealer[0]['nome']}{dealer[0]['naipe']}   🂠")
        lbl_pontos_dealer.config(text="Pontos: ?")
    else:
        lbl_dealer.config(text=texto_cartas(dealer))
        lbl_pontos_dealer.config(
            text=f"Pontos: {pontuacao(dealer)}"
        )

    lbl_dealer.config(fg=cor_cartas(dealer))


# ---------- FIM DA RONDA ----------
def terminar_ronda():
    global saldo, em_jogo

    while pontuacao(dealer) < 17:
        dealer.append(baralho.pop())

    pontos_jogador = pontuacao(jogador)
    pontos_dealer = pontuacao(dealer)

    atualizar_mesa()

    if pontos_jogador > 21:
        mensagem = "Ultrapassaste 21! Perdeste."
    elif pontos_dealer > 21:
        saldo += aposta * 2
        mensagem = "A banca passou 21! Ganhaste!"
    elif pontos_jogador > pontos_dealer:
        saldo += aposta * 2
        mensagem = "Parabens! Ganhaste!"
    elif pontos_jogador == pontos_dealer:
        saldo += aposta
        mensagem = "Empate! A aposta foi devolvida."
    else:
        mensagem = "A banca ganhou. Tenta novamente!"

    lbl_estado.config(text=mensagem)
    atualizar_saldo()

    em_jogo = False
    btn_pedir.config(state="disabled")
    btn_parar.config(state="disabled")
    btn_nova.config(state="normal")


# ---------- JOGADAS ----------
def nova_ronda():
    global saldo, aposta, baralho, jogador, dealer, em_jogo

    if em_jogo:
        return

    if saldo < 100:
        lbl_estado.config(text="Saldo insuficiente para jogar.")
        return

    aposta = 100
    saldo -= aposta
    baralho = criar_baralho()
    jogador = [baralho.pop(), baralho.pop()]
    dealer = [baralho.pop(), baralho.pop()]
    em_jogo = True

    btn_pedir.config(state="normal")
    btn_parar.config(state="normal")
    btn_nova.config(state="disabled")

    lbl_estado.config(text="É a tua vez! Pede carta ou para.")
    atualizar_saldo()
    atualizar_mesa(esconder_dealer=True)

    # Blackjack natural: A + carta de valor 10
    if pontuacao(jogador) == 21:
        terminar_ronda()


def pedir_carta():
    if not em_jogo:
        return

    jogador.append(baralho.pop())
    atualizar_mesa(esconder_dealer=True)

    if pontuacao(jogador) >= 21:
        terminar_ronda()


def parar():
    if em_jogo:
        terminar_ronda()


# ---------- INTERFACE ----------
janela = tk.Tk()
janela.title("Blackjack Casino")
janela.geometry("850x650")
janela.minsize(650, 550)
janela.configure(bg=BG)

tk.Label(
    janela, text="BLACKJACK",
    font=("Arial", 30, "bold"),
    fg=GOLD, bg=BG
).pack(pady=(20, 5))

lbl_saldo = tk.Label(
    janela, text="", font=("Arial", 14, "bold"),
    fg=WHITE, bg=BG
)
lbl_saldo.pack(pady=5)

mesa = tk.Frame(janela, bg=PANEL, padx=20, pady=20)
mesa.pack(fill="both", expand=True, padx=25, pady=15)

tk.Label(
    mesa, text="BANCA", font=("Arial", 15, "bold"),
    fg=GOLD, bg=PANEL
).pack(pady=(10, 5))

lbl_dealer = tk.Label(
    mesa, text="", font=("Arial", 28),
    fg=WHITE, bg=PANEL
)
lbl_dealer.pack(pady=5)

lbl_pontos_dealer = tk.Label(
    mesa, text="Pontos: ?", font=("Arial", 12),
    fg=WHITE, bg=PANEL
)
lbl_pontos_dealer.pack(pady=5)

tk.Frame(mesa, bg=GOLD, height=2).pack(fill="x", pady=20)

tk.Label(
    mesa, text="JOGADOR", font=("Arial", 15, "bold"),
    fg=GOLD, bg=PANEL
).pack(pady=5)

lbl_jogador = tk.Label(
    mesa, text="", font=("Arial", 28),
    fg=WHITE, bg=PANEL
)
lbl_jogador.pack(pady=5)

lbl_pontos_jogador = tk.Label(
    mesa, text="Pontos: 0", font=("Arial", 12),
    fg=WHITE, bg=PANEL
)
lbl_pontos_jogador.pack(pady=5)

lbl_estado = tk.Label(
    janela, text="Carrega em NOVO JOGO para começar.",
    font=("Arial", 12, "bold"),
    fg=GOLD, bg=BG, wraplength=750
)
lbl_estado.pack(pady=10)

botoes = tk.Frame(janela, bg=BG)
botoes.pack(pady=(0, 20))

btn_nova = tk.Button(
    botoes, text="NOVO JOGO", command=nova_ronda,
    bg=GOLD, fg="#17271F", font=("Arial", 11, "bold"),
    width=14, pady=10
)
btn_nova.pack(side="left", padx=6)

btn_pedir = tk.Button(
    botoes, text="PEDIR CARTA", command=pedir_carta,
    bg="#237653", fg=WHITE, font=("Arial", 11, "bold"),
    width=14, pady=10, state="disabled"
)
btn_pedir.pack(side="left", padx=6)

btn_parar = tk.Button(
    botoes, text="PARAR", command=parar,
    bg="#8C3434", fg=WHITE, font=("Arial", 11, "bold"),
    width=14, pady=10, state="disabled"
)
btn_parar.pack(side="left", padx=6)

atualizar_saldo()
janela.mainloop()
