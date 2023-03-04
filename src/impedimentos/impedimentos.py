## Codificado por Douglas Rodrigues de Almeida.
## Março de 2023
"""Impedimentos da conclusão de análise"""

import json
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

    #Variáveis do Sistema
    vars: Variaveis      

    def __str__(self) -> str:
        """Descrição de Impedimentos"""
        resultado = '\n'.join(f'\t{impedimento!r} - {impedimento!s}' for impedimento in self.lista)
        return 'Impedimentos disponíveis:\n' + resultado
    
    def carregar(self) -> None:
        """Carrega a lista de impedimentos do arquivo CSV."""
        nome_arquivo = path.join(self.vars.obter_pasta_dados(), ARQUIVO_DADOS)
        with open(nome_arquivo, 'r', encoding='utf8') as arquivo:
            for codigo, item in json.load(arquivo).items():
                self.lista.append(Impedimento(codigo, item['desc']))

    def existe(self, valor: str) -> bool:
        """Verifica se um impedimento existe na lista de impedimentos."""
        return self.obter(valor) is not None
    
    def obter(self, valor: str) -> Impedimento:
        """Retorna um impedimento conforme o ID especificado;"""
        for impedimento in self.lista:
            if valor.casefold() == repr(impedimento).casefold():
                return impedimento
        return None
