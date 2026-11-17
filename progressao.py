"""Níveis, XP e missões diárias."""
import datetime
import random

RECOMPENSA_XP = 150
RECOMPENSA_FICHAS = 100
BONUS_DIARIO = 50


def xp_total(n):
    """XP acumulado necessário para chegar ao nível n."""
    return 50 * n * (n - 1)


def nivel_de_xp(xp):
    n = 1
    while xp >= xp_total(n + 1):
        n += 1
    return n


def info_nivel(xp):
    """(nível, xp neste nível, xp necessário para o próximo)."""
    n = nivel_de_xp(xp)
    base = xp_total(n)
    return n, xp - base, xp_total(n + 1) - base


# (id, evento, alvo, texto)
POOL = [
    ("vit5", "vitorias", 5, "Ganha 5 mãos"),
    ("vit10", "vitorias", 10, "Ganha 10 mãos"),
    ("bj1", "blackjack", 1, "Faz 1 Blackjack"),
    ("rondas10", "rondas", 10, "Joga 10 rondas"),
    ("rondas20", "rondas", 20, "Joga 20 rondas"),
    ("dobrar1", "dobrar_ganho", 1, "Ganha uma mão depois de dobrar"),
    ("dividir1", "dividir", 1, "Divide um par (split)"),
    ("lado1", "lado_ganho", 1, "Ganha uma aposta lateral"),
    ("serie3", "serie", 3, "Ganha 3 mãos seguidas"),
    ("treino10", "treino_certas", 10, "Acerta 10 jogadas no Treino"),
    ("seguro1", "seguro", 1, "Aceita um Seguro"),
]
MISSAO = {m[0]: m for m in POOL}


def hoje():
    return datetime.date.today().isoformat()


def garantir_missoes(dados):
    """Sorteia 3 missões novas se o dia mudou (iguais para todos no mesmo dia)."""
    m = dados["missoes"]
    h = hoje()
    if m.get("data") != h:
        rng = random.Random(h)
        pool = POOL[:]
        rng.shuffle(pool)
        lista, eventos = [], set()
        for p in pool:
            if p[1] not in eventos:
                lista.append(p[0])
                eventos.add(p[1])
            if len(lista) == 3:
                break
        m.update({"data": h, "lista": lista, "prog": {}, "feitas": []})
    return m


def registar(dados, evento, n=1, absoluto=False):
    """Regista progresso. Devolve as missões que ficaram completas agora."""
    m = garantir_missoes(dados)
    completas = []
    for mid in m["lista"]:
        _, ev, alvo, _txt = MISSAO[mid]
        if ev != evento or mid in m["feitas"]:
            continue
        atual = m["prog"].get(mid, 0)
        m["prog"][mid] = max(atual, n) if absoluto else atual + n
        if m["prog"][mid] >= alvo:
            m["feitas"].append(mid)
            completas.append(MISSAO[mid])
    return completas