## Codificado por Douglas Rodrigues de Almeida.
## Agosto de 2023
"""Processamento em Lote"""

from arquivo import carregar_dados, carregar_tabela
from dataclasses import dataclass
from os import path
from variaveis import Variaveis

ARQUIVO_DADOS = 'lotes.json'

@dataclass
class Lote:
    """Classe para o item do lote."""

    #Identificador do lote
    id: str

    #Descrição do lote
    desc: str

    #Atributos que são alterados pelo lote
    atributos: str

    #Entrada do lote
    entrada: str

    def __repr__(self) -> str:
        """Representação de Lote"""
        return self.id

    def __str__(self) -> str:
        """Descrição de Lote"""
        return self.desc
       
    def carregar_dados(self) -> list[list[str]]:
        with carregar_tabela(self.entrada) as tabela:
            return tabela[1:]
        
    def obter_atributos(self) -> list[str]:
        return self.atributos.split(';')

@dataclass
class Lotes:
    """Classe para o lote."""

    #Lista de impedimentos
    lista: list[Lote]

    def __str__(self) -> str:
        """Descrição de Impedimentos"""
        resultado = '\n'.join(f'\t{lote!r} - {lote!s}' for lote in self.lista)
        return 'Lotes válidos:\n' + resultado

    def carregar(self) -> bool:
        """Carrega a lista de impedimentos do arquivo JSON."""
        try:
            with carregar_dados(ARQUIVO_DADOS) as dados:
                self.lista = [Lote(codigo, item['desc'], item['atributos'], item['entrada']) for codigo, item in dados.items()]
        except OSError as err:
            print(f"Erro ao abrir arquivo de lotes: {err.strerror}.")
            return False
        return True

    def obter(self, valor: str) -> Lote | None:
        """Retorna um impedimento conforme o ID especificado;"""
        for lote in self.lista:
            if valor.casefold() == repr(lote):
                return lote
        return None