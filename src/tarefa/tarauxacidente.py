## Codificado por Douglas Rodrigues de Almeida.
## Agosto de 2023
"""Tarefa para o requerimento Auxílio-Acidente"""

import pandas as pd
from .tarefaben import TarefaBeneficio
from basedados import BaseDados

class TarefaAuxilioAcidente(TarefaBeneficio):
    """Classe da Tarefa de Auxílio-Acidente"""
    def __init__(self, dados: BaseDados, i: int) -> None:
        super().__init__(dados, i)

    def __str__(self) -> str:
        """Descrição da tarefa de auxílio-acidente."""
        resultado = super().__str__()

        resultado += f'PM lançada: {self.tem_pericia_lancada()}\n'
        resultado += super().pos_tostr()

        return resultado
        
    def marcar_pm_lancada(self) -> None:
        """Informa que a perícia foi lançada no Prisma."""
        self.base_dados.alterar_atributo(self.pos, "pericialancada", "1")
    
    def tem_pericia_lancada(self) -> bool:
        """Retorna se a PM já foi lançada no PM."""
        return self.base_dados.checar_atributo_verdadeiro(self.pos, "pericialancada")