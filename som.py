"""Efeitos sonoros gerados em código (sem ficheiros externos)."""
import math
import os
import random
import shutil
import struct
import subprocess
import sys
import tempfile
import wave

RATE = 22050

# (tipo, duração, volume, frequência)
SONS = {
    "carta": [("ruido", 0.06, 0.30, 0)],
    "virar": [("ruido", 0.05, 0.22, 0)],
    "ficha": [("seno", 0.04, 0.40, 1900), ("seno", 0.05, 0.35, 1500)],
    "clique": [("seno", 0.04, 0.30, 900)],
    "vitoria": [("seno", 0.10, 0.45, 523), ("seno", 0.10, 0.45, 659),
                ("seno", 0.10, 0.45, 784), ("seno", 0.28, 0.45, 1047)],
    "blackjack": [("seno", 0.09, 0.45, 523), ("seno", 0.09, 0.45, 659),
                  ("seno", 0.09, 0.45, 784), ("seno", 0.09, 0.45, 1047),
                  ("seno", 0.09, 0.45, 784), ("seno", 0.09, 0.45, 1047),
                  ("seno", 0.35, 0.45, 1319)],
    "derrota": [("quad", 0.16, 0.25, 330), ("quad", 0.16, 0.25, 277),
                ("quad", 0.30, 0.25, 220)],
    "empate": [("seno", 0.10, 0.40, 440), ("seno", 0.16, 0.40, 440)],
    "conquista": [("seno", 0.10, 0.40, 784), ("seno", 0.10, 0.40, 988),
                  ("seno", 0.32, 0.40, 1319)],
}


def _gerar(tipo, dur, vol, freq):
    n = int(RATE * dur)
    out = []
    for i in range(n):
        t = i / RATE
        env = math.exp(-5.0 * i / n)
        if tipo == "ruido":
            s = random.uniform(-1, 1)
        elif tipo == "quad":
            s = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
        else:
            s = math.sin(2 * math.pi * freq * t)
        out.append(s * env * vol)
    return out


def _gravar(caminho, amostras):
    with wave.open(caminho, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(b"".join(
            struct.pack("<h", int(max(-1.0, min(1.0, a)) * 32767))
            for a in amostras))


class Som:

    def __init__(self, root, ativo=True):
        self.root = root
        self.ativo = ativo
        self.ficheiros = {}
        try:
            pasta = tempfile.mkdtemp(prefix="blackjack_sons_")
            for nome, partes in SONS.items():
                amostras = []
                for p in partes:
                    amostras += _gerar(*p)
                caminho = os.path.join(pasta, nome + ".wav")
                _gravar(caminho, amostras)
                self.ficheiros[nome] = caminho
        except Exception:
            self.ficheiros = {}

    def tocar(self, nome):
        if not self.ativo:
            return
        caminho = self.ficheiros.get(nome)
        if not caminho:
            return
        try:
            if sys.platform.startswith("win"):
                import winsound
                winsound.PlaySound(
                    caminho,
                    winsound.SND_FILENAME | winsound.SND_ASYNC
                    | winsound.SND_NODEFAULT)
            elif sys.platform == "darwin":
                subprocess.Popen(["afplay", caminho],
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
            else:
                for cmd in (["paplay"], ["aplay", "-q"]):
                    if shutil.which(cmd[0]):
                        subprocess.Popen(cmd + [caminho],
                                         stdout=subprocess.DEVNULL,
                                         stderr=subprocess.DEVNULL)
                        break
        except Exception:
            pass