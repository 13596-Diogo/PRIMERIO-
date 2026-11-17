"""Constantes globais do Blackjack Royale."""
import os

PASTA = os.path.dirname(os.path.abspath(__file__))
FICHEIRO_SAVE = os.path.join(PASTA, "blackjack_save.json")

# tamanho da janela / ecrãs
SW, SH = 1100, 720
# tamanho do canvas do jogo
CW, CH = 1100, 560
CX = 440                       # centro horizontal da mesa

BG = "#101820"
PAINEL = "#17261f"
DOURADO = "#E8BD61"
BRANCO = "#FFFFFF"
VERMELHO = "#D94343"
VERDE = "#4FD18B"
AZUL_CLARO = "#7fa8d6"
PRETO = "#171717"
CINZA = "#3a3f47"

TEMAS = {
    "Verde": ("#0b3d2c", "#168062"),
    "Azul": ("#0c2d4d", "#1b6aa5"),
    "Bordô": ("#4a0f1d", "#9b2842"),
}

# (cor do fundo do verso, cor do detalhe)
VERSOS = {
    "Azul": ("#1c3f73", "#E8BD61"),
    "Vermelho": ("#8a1c2b", "#f2d6a0"),
    "Preto": ("#1a1a1a", "#E8BD61"),
    "Verde": ("#17513a", "#e8d9a0"),
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
CHIP_X = 990

CARTA_W, CARTA_H = 80, 116
SHOE_X, SHOE_Y = 770, 46
ZONA_APOSTA = (190, 415, 690, 552)

FATOR_VEL = {1: 1.5, 2: 1.0, 3: 0.6}   # multiplicador dos atrasos

# (id, nome, descrição)
CONQUISTAS = [
    ("primeiro_bj", "Primeiro Blackjack", "Faz o teu primeiro Blackjack natural."),
    ("bj5", "Mestre do 21", "Faz 5 Blackjacks."),
    ("serie5", "Em Chamas", "Ganha 5 mãos seguidas."),
    ("cinco_mil", "Alto Rolador", "Chega às 5.000 fichas no modo Clássico."),
    ("veterano", "Veterano", "Joga 50 rondas."),
    ("dobrar", "Aposta Certeira", "Ganha uma mão depois de dobrar."),
    ("dividir", "Dividir e Conquistar", "Ganha uma mão depois de dividir."),
    ("seguro", "Boa Intuição", "Recebe o pagamento de um Seguro."),
    ("tudo", "Tudo ou Nada", "Ganha uma ronda apostando todas as fichas."),
    ("falencia", "Já Fui Mais Rico", "Fica sem fichas."),
    ("desafio", "Desafio Cumprido", "Completa o modo Desafio."),
    ("relogio", "Contra o Tempo", "Termina o Contra-relógio com 1.000+ fichas."),
]