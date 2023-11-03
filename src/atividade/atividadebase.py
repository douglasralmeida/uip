## Codificado por Douglas Rodrigues de Almeida.
## Agosto de 2023

"""Atividade."""

from pandas import DataFrame
from basedados import BaseDados
from filtro import Filtros
from navegador import Get
from tarefa import Tarefa

class AtividadeBase:
    def __init__(self, nome_atividade: str, base_dados: BaseDados) -> None:
        """"""
        self.cont = 0

        self.nome_atividade = nome_atividade
    
        self.base_dados = base_dados

        self.filtros_tarefas: Filtros | None = None

        self.lista_tarefas: list[Tarefa] = []

        self.nome_filtro = ''

        self.navs = {}

    def alterar_get(self, get: Get) -> None:
        self.navs['get'] = get

    def definir_filtros(self, filtros: Filtros) -> None:
        self.filtros_tarefas = filtros

    def executar(self) -> None:
        pass

    def obter_tarefas(self) -> DataFrame | None:
        if self.filtros_tarefas is not None:
            filtro = self.filtros_tarefas.obter(self.nome_filtro)
            return self.base_dados.obter_dados(filtro)
        else:
            return None
        
    def pos_execucao(self) -> None:
        """"""
        print('\nFinalizando...')
        print(f'{self.cont} tarefa(s) processada(s) com sucesso.\n')

    def pre_execucao(self) -> None:
        """"""
        ui_linha = ''
        for _ in (ui_titulo := f'PROGRAMA \'{self.nome_atividade}\''):
            ui_linha += '-'
        print(f'{ui_titulo}\n{ui_linha}\nExecutando...\n')
        
        if self.navs['get'] is not None:
            self.navs['get'].suspender_processamento = False