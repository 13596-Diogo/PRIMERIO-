"""Apostas laterais: Par Perfeito e 21+3."""

ORDEM = {"A": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8,
         "9": 9, "10": 10, "J": 11, "Q": 12, "K": 13}


def _vermelha(carta):
    return carta[1] in ("♥", "♦")


def perfect_pairs(c1, c2):
    """Devolve (nome, pagamento) ou None."""
    if c1[0] != c2[0]:
        return None
    if c1[1] == c2[1]:
        return "Par Perfeito", 25
    if _vermelha(c1) == _vermelha(c2):
        return "Par Colorido", 12
    return "Par Misto", 5


def _sequencia(cartas):
    vals = sorted(ORDEM[c[0]] for c in cartas)
    if len(set(vals)) < 3:
        return False
    if vals[2] - vals[0] == 2:
        return True
    if 1 in vals:   # Ás também vale 14 (Q-K-A)
        alto = sorted(14 if v == 1 else v for v in vals)
        return alto[2] - alto[0] == 2
    return False


def vinte_e_tres(c1, c2, up):
    """Pontos de póquer com as 2 cartas do jogador + carta do dealer."""
    cartas = [c1, c2, up]
    mesmo_naipe = len({c[1] for c in cartas}) == 1
    trio = len({c[0] for c in cartas}) == 1
    seq = _sequencia(cartas)
    if trio and mesmo_naipe:
        return "Trio do mesmo naipe", 100
    if seq and mesmo_naipe:
        return "Sequência de cor", 40
    if trio:
        return "Trio", 30
    if seq:
        return "Sequência", 10
    if mesmo_naipe:
        return "Flush", 5
    return None