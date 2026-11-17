"""Estratégia básica de blackjack (usada pela sugestão e pela tabela)."""
from utilitarios import calcular, pontos

NOMES = {"H": "PEDIR", "S": "FICAR", "D": "DOBRAR",
         "P": "DIVIDIR", "R": "DESISTIR"}


def acao_basica(cartas, up, pode_dobrar=True, pode_dividir=True,
                pode_desistir=False):
    """Devolve (letra, descrição). Letras: H S D P R."""
    u = pontos(up)                      # 2..11 (Ás = 11)
    total, soft = calcular(cartas)
    nome_up = "Ás" if u == 11 else str(u)

    def dobrar_ou(alt):
        return "D" if pode_dobrar else alt

    # ---------- pares ----------
    if (len(cartas) == 2 and pode_dividir
            and pontos(cartas[0]) == pontos(cartas[1])):
        p = pontos(cartas[0])
        dividir = False
        if p in (11, 8):
            dividir = True
        elif p == 9:
            dividir = u in (2, 3, 4, 5, 6, 8, 9)
        elif p == 7:
            dividir = u <= 7
        elif p == 6:
            dividir = u <= 6
        elif p == 4:
            dividir = u in (5, 6)
        elif p in (2, 3):
            dividir = u <= 7
        if dividir:
            rotulo = "Ases" if p == 11 else f"{p}s"
            return "P", f"par de {rotulo} vs {nome_up}"

    # ---------- desistir ----------
    if pode_desistir and not soft and len(cartas) == 2:
        if (total == 16 and u in (9, 10, 11)) or (total == 15 and u == 10):
            return "R", f"{total} vs {nome_up}"

    # ---------- soft ----------
    if soft:
        letra = "H"
        if total >= 19:
            letra = "S"
        elif total == 18:
            if u in (3, 4, 5, 6):
                letra = dobrar_ou("S")
            elif u in (2, 7, 8):
                letra = "S"
        elif total == 17:
            letra = dobrar_ou("H") if 3 <= u <= 6 else "H"
        elif total in (15, 16):
            letra = dobrar_ou("H") if 4 <= u <= 6 else "H"
        elif total in (13, 14):
            letra = dobrar_ou("H") if u in (5, 6) else "H"
        return letra, f"soft {total} vs {nome_up}"

    # ---------- hard ----------
    if total >= 17:
        letra = "S"
    elif total >= 13:
        letra = "S" if u <= 6 else "H"
    elif total == 12:
        letra = "S" if 4 <= u <= 6 else "H"
    elif total == 11:
        letra = dobrar_ou("H") if u <= 10 else "H"
    elif total == 10:
        letra = dobrar_ou("H") if u <= 9 else "H"
    elif total == 9:
        letra = dobrar_ou("H") if 3 <= u <= 6 else "H"
    else:
        letra = "H"
    return letra, f"{total} vs {nome_up}"