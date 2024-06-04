## Codificado por Douglas Rodrigues de Almeida.
## Dezembro de 2023
"""Despachos da análise"""

from arquivo import carregar_dados
from dataclasses import dataclass
from os import path
from variaveis import Variaveis

ARQUIVO_DADOS = 'despachos.json'

@dataclass
class Despacho:
    """Classe para despacho."""

    #Identificador do despacho
    id: str

    #Conteúdo do despacho
    conteudo: str

    #Variáveis necessárias para o despacho
    variaveis: str


    def __repr__(self) -> str:
        """Representação de Despacho"""
        return self.id

    def __str__(self) -> str:
        """Descrição de Despacho"""
        return self.conteudo

@dataclass
class Despachos:
    """Classe para a lista de despachos da análise de direito."""

    #Lista de Despachos
    lista: list[Despacho]

    def __str__(self) -> str:
        """Descrição de Despachos"""
        res = '\n'.join(f'\t{despacho!r} - {despacho!s}' for despacho in self.lista)
        return 'Despachos disponíveis:\n' + res
    
    def __iter__(self):
        yield from self.lista

    def carregar(self) -> bool:
        """Carrega a lista de despachos do arquivo JSON."""
        try:
            with carregar_dados(ARQUIVO_DADOS) as dados:
                self.lista = [Despacho(codigo, item['conteudo'], item['variaveis']) for codigo, item in dados.items()]
        except OSError as err:
            print(f"Erro ao abrir arquivo de despachos: {err.strerror}.")
            return False
        return True    

    def obter(self, valor: str) -> Despacho | None:
        """Retorna um resultado conforme o ID especificado;"""
        for despacho in self.lista:
            if valor.casefold() == repr(despacho).casefold():
                return despacho
        return None
