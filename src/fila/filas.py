## Codificado por Douglas Rodrigues de Almeida.
## Junho de 2023

"""Filas cadastradas no UIP."""

import json
from .fila import Fila
from dataclasses import dataclass
from os import path
from variaveis import Variaveis

ARQUIVO_DADOS = 'filas.json'

@dataclass
class Filas:
    '''Classe para as filas de tarefas cadastradas no UIP.'''
           
    #Lista de filas
    lista: list[Fila]

    #Variáveis do Sistema
    vars: Variaveis

    def __str__(self) -> str:
        """Descrição das filas"""
        resultado = '\n'.join(f'\t{fila!r} - {fila!s}' for fila in self.lista)
        return 'Filas disponíveis:\n' + resultado
    
    def carregar(self) -> None:
        """Carrega a lista de filas do arquivo JSON."""
        nome_arquivo = path.join(self.vars.obter_pasta_dados(), ARQUIVO_DADOS)
        with open(nome_arquivo, 'r', encoding='utf8') as arquivo:
            self.lista = [Fila(codigo,
                               item['nome'], 
                               item['id'], 
                               item['codigo'],
                               item['valor_exigencia'], 
                               item['valor_subtarefa'], 
                               item['valor_conclusao'],
                               item['ativa'] == 1) for codigo, item in json.load(arquivo).items()]    

    def obter(self, valor: str) -> Fila:
        """Retorna uma fila conforme o ID especificado"""
        for fila in self.lista:
            if valor.casefold() == fila.get_id().casefold():
                return fila
        return None