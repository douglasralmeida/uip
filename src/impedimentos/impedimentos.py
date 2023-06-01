## Codificado por Douglas Rodrigues de Almeida.
## Março de 2023
"""Impedimentos da conclusão de análise"""

from arquivo import carregar_dados
from dataclasses import dataclass
from os import path
from variaveis import Variaveis

ARQUIVO_DADOS = 'impedimentos.json'

@dataclass
class Impedimento:
    """Classe para o impedimento da conclusão da análise."""

    #Identificador do impedimento
    id: str

    #Descrição do impedimento
    desc: str

    def __repr__(self) -> str:
        """Representação de Impedimento"""
        return self.id[3:]

    def __str__(self) -> str:
        """Descrição de Impedimento"""
        return self.desc

@dataclass
class Impedimentos:
    """Classe para a lista dos impedimentos da conclusão da análise."""

    #Lista de impedimentos
    lista: list[Impedimento]

    def __str__(self) -> str:
        """Descrição de Impedimentos"""
        resultado = '\n'.join(f'\t{impedimento!r} - {impedimento!s}' for impedimento in self.lista)
        return 'Impedimentos disponíveis:\n' + resultado

    def carregar(self) -> None:
        """Carrega a lista de impedimentos do arquivo JSON."""
        with carregar_dados(ARQUIVO_DADOS) as dados:
            self.lista = [Impedimento(codigo, item['desc']) for codigo, item in dados.items()]

    def obter(self, valor: str) -> Impedimento:
        """Retorna um impedimento conforme o ID especificado;"""
        for impedimento in self.lista:
            if valor.casefold() == repr(impedimento).casefold():
                return impedimento
        return None
