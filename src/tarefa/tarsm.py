## Codificado por Douglas Rodrigues de Almeida.
## Março de 2023
"""Tarefa de Salário Maternidade"""

from .utils import valor_tostring
from .tarefa import Tarefa
from agendamento import Agendamento
from basedados import BaseDados
from datetime import date

class TarefaSalMaternidade(Tarefa):
    """Classe da Tarefa de Salário Maternidade"""
    def __init__(self, dados: BaseDados, i: int) -> None:
        super().__init__(dados, i)

    def __str__(self) -> str:
        """Descrição da tarefa de auxílio-acidente."""
        resultado = f'Protocolo: {self.obter_protocolo()}\n'
        resultado += f'CPF: {valor_tostring(self.obter_cpf())}\n'
        resultado += f'NB: {valor_tostring(self.obter_beneficio())}\n'
        resultado += f'Status BEN: {valor_tostring(self.obter_statusben())}\n'
        resultado += f'DIB: {valor_tostring(self.obter_dib())}\n'

        return resultado
    
    def alterar_beneficiosanteriores(self, beneficios: str) -> None:
        """Altera o número do benefício."""
        self.base_dados.alterar_atributo(self.pos, 'beneficios_anteriores', beneficios)

    def alterar_dib(self, dib: str) -> None:
        """Altera o status do benefício."""
        self.base_dados.alterar_atributo(self.pos, "dib_anteriores", str(dib))
    
    def alterar_status(self, status: str) -> None:
        """Altera o status do benefício."""
        self.base_dados.alterar_atributo(self.pos, "status_anteriores", str(status))

    def alterar_subtarefa(self, subtarefa: str) -> None:
        """Altera o número da subtarefa."""
        self.base_dados.alterar_atributo(self.pos, "subtarefa", str(subtarefa))
    
    def concluir_fase_dadosben(self) -> None:
        """Informa que a PM foi agendada."""
        self.base_dados.alterar_atributo(self.pos, "tem_dadosben", "1")      

    def obter_fase_dadosben(self) -> bool:
        """Retorna se já coletou dados do benefício."""
        return self.base_dados.checar_atributo_verdadeiro(self.pos, "tem_dadosben")

    def obter_statusben(self) -> str:
        """Retorna o status do benefício."""
        return self.base_dados.obter_atributo(self.pos, 'status_anteriores')
    
    def obter_dib(self) -> str:
        """Retorna a DIB."""
        return self.base_dados.obter_atributo(self.pos, 'dib_anteriores')