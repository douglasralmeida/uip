## Codificado por Douglas Rodrigues de Almeida.
## Agosto de 2023
"""Resultados de análise"""

from arquivo import carregar_dados
from dataclasses import dataclass
from os import path
from variaveis import Variaveis

ARQUIVO_DADOS = 'resultados.json'

@dataclass
class Resultado:
    """Classe para o impedimento da conclusão da análise."""

    #Identificador do impedimento
    id: str

    #Descrição do impedimento
    desc: str

    #Despacho de conclusão
    conclusao: str    

    #Despacho de análise de direito
    despacho: str

    #Variáveis necessárias para o despacho de conclusão
    vars_conclusao: str

    #Variáveis necessárias para o despacho da análise de direito
    vars_despacho: str

    def __repr__(self) -> str:
        """Representação de Resultado"""
        return self.id

    def __str__(self) -> str:
        """Descrição de Resultado"""
        return self.desc

@dataclass
class Resultados:
    """Classe para a lista dos resultados da análise de direito."""

    #Lista de impedimentos
    lista: list[Resultado]

    def __str__(self) -> str:
        """Descrição de Resultados"""
        res = '\n'.join(f'\t{resultado!r} - {resultado!s}' for resultado in self.lista)
        return 'Resultados disponíveis:\n' + res
    
    def __iter__(self):
        yield from self.lista

    def carregar(self) -> bool:
        """Carrega a lista de resultados do arquivo JSON."""
        try:
            with carregar_dados(ARQUIVO_DADOS) as dados:
                self.lista = [Resultado(codigo, item['descricao'], item['conclusao'], item['despacho'], item['conclusao_vars'], item['despacho_vars']) for codigo, item in dados.items()]
        except OSError as err:
            print(f"Erro ao abrir arquivo de resultados: {err.strerror}.")
            return False
        return True    

    def obter(self, valor: str) -> Resultado | None:
        """Retorna um resultado conforme o ID especificado;"""
        for resultado in self.lista:
            if valor.casefold() == repr(resultado).casefold():
                return resultado
        return None
