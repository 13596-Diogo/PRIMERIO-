"""Perfis, definições e gravação em JSON."""
import copy
import json
from constantes import FICHEIRO_SAVE, TEMAS, VERSOS

CONFIG_PADRAO = {
    "velocidade": 2,
    "baralhos": 6,
    "soft17": False,
    "contagem": False,
    "tema": "Verde",
    "verso": "Azul",
    "som": True,
}


def perfil_padrao():
    return {
        "saldo": 1000, "vitorias": 0, "derrotas": 0, "empates": 0,
        "blackjacks": 0, "rondas": 0, "falencias": 0,
        "saldo_max": 1000, "maior_ganho": 0, "ultima_aposta": 0,
        "serie": 0, "melhor_serie": 0,
        "conquistas": [], "historico": [1000], "recentes": [],
        "desafios_ganhos": 0, "relogio_melhor": 0,
    }


def _completar_perfil(p):
    base = perfil_padrao()
    for k, v in base.items():
        p.setdefault(k, v)
    return p


def carregar():
    save = {"perfil": "Jogador", "perfis": {},
            "config": copy.deepcopy(CONFIG_PADRAO)}
    try:
        with open(FICHEIRO_SAVE, "r", encoding="utf-8") as f:
            bruto = json.load(f)
    except (OSError, ValueError):
        bruto = None

    if isinstance(bruto, dict):
        if isinstance(bruto.get("perfis"), dict):
            save["perfis"] = {n: _completar_perfil(p)
                              for n, p in bruto["perfis"].items()
                              if isinstance(p, dict)}
            save["perfil"] = bruto.get("perfil", "Jogador")
        else:   # migrar ficheiro antigo (versão 1)
            p = perfil_padrao()
            for k in p:
                if k in bruto and k != "config":
                    p[k] = bruto[k]
            save["perfis"]["Jogador"] = p
        if isinstance(bruto.get("config"), dict):
            for k in CONFIG_PADRAO:
                if k in bruto["config"]:
                    save["config"][k] = bruto["config"][k]

    if not save["perfis"]:
        save["perfis"]["Jogador"] = perfil_padrao()
    if save["perfil"] not in save["perfis"]:
        save["perfil"] = next(iter(save["perfis"]))
    if save["config"]["tema"] not in TEMAS:
        save["config"]["tema"] = "Verde"
    if save["config"]["verso"] not in VERSOS:
        save["config"]["verso"] = "Azul"
    return save


def guardar(save):
    try:
        with open(FICHEIRO_SAVE, "w", encoding="utf-8") as f:
            json.dump(save, f, indent=2, ensure_ascii=False)
    except OSError:
        pass