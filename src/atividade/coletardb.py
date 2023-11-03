## Codificado por Douglas Rodrigues de Almeida.
## Agosto de 2023

"""Atividade Coleta Dados Básicos."""

from .atividadebase import AtividadeBase
from basedados import BaseDados
from tarefa import TarefaBeneficio

class AtividadeColetaDB(AtividadeBase):
    def __init__(self, base_dados: BaseDados) -> None:
        """"""
        super().__init__("Coleta de Dados Básicos", base_dados)

        self.lista_tarefas: list[TarefaBeneficio] = []

        self.nome_filtro = 'coleta_db'

    def executar(self):
        self.pre_execucao()
        
        lista_tarefas = self.obter_tarefas()
        if lista_tarefas is not None:
            for item in lista_tarefas[0]:
                print(f'Tarefa ID {item}...')
                self.cont += 1
            #tarefa = TarefaBeneficio(self.base_dados, 0)
            #protocolo = str(t.obter_protocolo().valor)

        self.pos_execucao()



    