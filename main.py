"""
BLACKJACK ROYALE - Trabalho final de módulo (tkinter)

Executar:  python main.py
"""
import tkinter as tk

from constantes import BG
from utilitarios import ESTILO
from dados import carregar, guardar
from som import Som
from ecras import (Splash, Menu, Modos, Regras, Estatisticas, Definicoes,
                   Perfis, Conquistas, Recordes, TabelaEstrategia)
from jogo import Jogo


class App:

    def __init__(self, root):
        self.root = root
        root.title("BLACKJACK ROYALE")
        root.geometry("1100x720")
        root.resizable(False, False)
        root.configure(bg=BG)

        self.save = carregar()
        ESTILO["verso"] = self.cfg["verso"]
        self.som = Som(root, self.cfg["som"])
        self.atual = None
        self.ecras = {
            "splash": Splash(self),
            "menu": Menu(self),
            "modos": Modos(self),
            "jogo": Jogo(self),
            "regras": Regras(self),
            "stats": Estatisticas(self),
            "defs": Definicoes(self),
            "perfis": Perfis(self),
            "conquistas": Conquistas(self),
            "recordes": Recordes(self),
            "estrategia": TabelaEstrategia(self),
        }
        root.bind("<Key>", self.tecla)
        root.protocol("WM_DELETE_WINDOW", self.sair)
        self.mostrar("splash")

    # perfil ativo e definições
    @property
    def dados(self):
        return self.save["perfis"][self.save["perfil"]]

    @property
    def cfg(self):
        return self.save["config"]

    def mostrar(self, nome):
        for e in self.ecras.values():
            e.pack_forget()
        self.atual = nome
        ecra = self.ecras[nome]
        ecra.pack(fill="both", expand=True)
        if hasattr(ecra, "ao_mostrar"):
            ecra.ao_mostrar()

    def ir(self, nome):
        self.som.tocar("clique")
        self.mostrar(nome)

    def iniciar_jogo(self, modo):
        self.som.tocar("clique")
        self.ecras["jogo"].iniciar_modo(modo)
        self.mostrar("jogo")

    def tecla(self, e):
        k = e.keysym.lower()
        if self.atual == "jogo":
            jogo = self.ecras["jogo"]
            if k == "h":
                jogo.pedir()
            elif k == "s":
                jogo.ficar()
            elif k == "d":
                jogo.dobrar()
            elif k == "p":
                jogo.dividir()
            elif k == "c":
                jogo.sugestao()
            elif k in ("return", "space"):
                if jogo.estado == "apostar":
                    jogo.comecar_ronda()
                elif jogo.estado == "fim":
                    jogo.nova_ronda()
            elif k == "escape":
                self.mostrar("menu")
        elif self.atual == "splash":
            self.mostrar("menu")
        elif k == "escape" and self.atual != "menu":
            self.mostrar("menu")

    def sair(self):
        guardar(self.save)
        self.root.destroy()


if __name__ == "__main__":
    janela = tk.Tk()
    App(janela)
    janela.mainloop()