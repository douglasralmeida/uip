## Codificado por Douglas Rodrigues de Almeida.
## Março de 2023
"""Impedimentos da conclusão de análise"""

from arquivo import carregar_dados
from dataclasses import dataclass

ARQUIVO_DADOS = 'filtros.json'

@dataclass
class Filtro:
    """Classe para filtro de tarefas."""

    #Identificador do filtro
    id: str

    #Processador do filtro
    processador: str

    #Valor do filtro
    valor: str

    def __repr__(self) -> str:
        """Representação de Impedimento"""
        return self.id

    def __str__(self) -> str:
        """Descrição de Impedimento"""
        return self.valor

@dataclass
class Filtros:
    """Classe para a lista dos filtros de tarefas."""

    #Lista de filtros
    lista: list[Filtro]

    def __iter__(self):
        yield from self.lista

    def __str__(self) -> str:
        """Descrição de Filtros"""
        resultado = '\n'.join(f'\t{filtro!r} - {filtro!s}' for filtro in self.lista)
        return 'Filtros disponíveis:\n' + resultado
    
    def adicionar(self, filtro: Filtro) -> None:
        """"""
        self.lista.append(filtro)

    def carregar(self) -> bool:
        """Carrega a lista de filtros do arquivo JSON."""
        try:
            with carregar_dados(ARQUIVO_DADOS) as dados:
                self.lista = []
                for codigo, item in dados.items():
                    filtro = Filtro(codigo, item['processador'], item['valor'])
                    if item['sem_desis_conc_imp'] == '1':
                        filtro.valor += " & not resultado.isin(['desistencia']) & impedimentos.isna() & concluso.isna()"
                    self.lista.append(filtro)
        except OSError as err:
            print(f"Erro ao abrir arquivo de filtros: {err.strerror}.")
            return False
        return True

    def obter(self, valor: str) -> Filtro | None:
        """Retorna um filtro conforme o ID especificado;"""
        for filtro in self.lista:
            if valor.casefold() == repr(filtro):
                return filtro
        return None
