## Codificado por Douglas Rodrigues de Almeida.
## Junho de 2023

"""Filas cadastradas no UIP."""

from .fila import Fila
from arquivo import carregar_dados
from dataclasses import dataclass

ARQUIVO_DADOS = 'filas.json'

@dataclass
class Filas:
    '''Classe para as filas de tarefas cadastradas no UIP.'''

    #Lista de filas
    lista: list[Fila]

    def __str__(self) -> str:
        """Descrição das filas"""
        resultado = '\n'.join(f'\t{fila!r} - {fila!s}' for fila in self.lista if fila.ativa)
        return 'Filas disponíveis:\n' + resultado
    
    def carregar(self) -> bool:
        """Carrega a lista de filas do arquivo JSON."""
        try:
            with carregar_dados(ARQUIVO_DADOS) as dados:
                self.lista = [Fila(codigo,
                                   item['nome'], 
                                   item['id'], 
                                   item['codigo'],
                                   item['valor_exigencia'], 
                                    item['valor_subtarefa'], 
                                    item['valor_conclusao'],
                                    item['ativa'] == 1) for codigo, item in dados.items()]
        except OSError as err:
            print(f"Erro ao abrir lista de filas: {err.strerror}.")
            return False
        return True

    def obter(self, valor: str) -> Fila | None:
        """Retorna uma fila conforme o ID especificado"""
        for fila in self.lista:
            if valor.casefold() == fila.get_id():
                return fila
        return None