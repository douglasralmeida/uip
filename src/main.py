#!/usr/bin/env python3

from linhacomando import LinhaComando
from sistema import Sistema

sistema = Sistema()
if sistema.carregar_dados():
    lc = LinhaComando(sistema)
    lc.carregar()
    lc.exibir_cabecalho()
    lc.exibir()