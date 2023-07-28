## Codificado por Douglas Rodrigues de Almeida.
## Agosto de 2023
"""Listagem de dados"""

from arquivo import carregar_dados
from dataclasses import dataclass

ARQUIVO_DADOS = 'listagens.json'

@dataclass
class Listagem:
    """Classe para listagem de tarefas."""

    #Identificador da listagem
    id: str

    #Descricao da listagem
    desc: str

    #Filtro da listagem
    filtro: str

    #Colunas da listagem
    colunas: list[str]

    #Ordenação da listagem
    ordenacao: list[str]

    #Ordem Crescente/Decrescente
    ordem_crescente: bool

    #Processador da listagem
    processador: str

    def __repr__(self) -> str:
        """Representação de listagem"""
        return self.id

    def __str__(self) -> str:
        """Descrição de listagem"""
        return self.desc

@dataclass
class Listagens:
    """Classe para a lista de listagem das tarefas."""

    #Lista de listagem
    lista: list[Listagem]

    def __iter__(self):
        yield from self.lista    

    def __str__(self) -> str:
        """Descrição de Listagem"""
        resultado = '\n'.join(f'\t{listagem!r} - {listagem!s}' for listagem in self.lista)
        return 'Listagem disponíveis:\n' + resultado
    
    def adicionar(self, listagem: Listagem) -> None:
        """A"""
        self.lista.append(listagem)

    def carregar(self) -> bool:
        """Carrega a lista de listagem do arquivo JSON."""
        try:
            with carregar_dados(ARQUIVO_DADOS) as dados:
                self.lista = [Listagem(codigo, 
                                       item['desc'], 
                                       codigo,
                                       item['colunas'].split(';'), 
                                       item['ordenacao'].split(';'), 
                                       bool(item['ordem_crescente']), 
                                       item['processador']) for codigo, item in dados.items()]
        except OSError as err:
            print(f"Erro ao abrir arquivo de lotes: {err.strerror}.")
            return False
        return True

    def obter(self, valor: str, tipos: list[str]) -> Listagem | None:
        """Retorna um filtro conforme o ID especificado;"""
        for listagem in self.lista:
            if listagem.processador in tipos and valor.casefold() == repr(listagem):
                return listagem
        return None