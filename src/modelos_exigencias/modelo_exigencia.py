## Codificado por Douglas Rodrigues de Almeida.
## Agosto de 2023
"""Modelos de Exigência"""

from arquivo import carregar_dados, carregar_tabela
from dataclasses import dataclass

ARQUIVO_DADOS = 'exigencias.json'

@dataclass
class ModeloExigencia:
    """Classe para o texto modelo de exigência."""

    #Identificador do modelo
    id: str

    #Texto do modelo
    texto: str

    def __repr__(self) -> str:
        """Representação do Modelo"""
        return self.id

    def __str__(self) -> str:
        """Descrição do Modelo"""
        return self.texto

@dataclass
class ListaModelosExigencia:
    """Classe para a lista de modelos."""

    #Lista de modelos
    lista: list[ModeloExigencia]

    def __str__(self) -> str:
        """Descrição de Lista de Modelos"""
        resultado = '\n'.join(f'\t{modelo!r} - {modelo!s}' for modelo in self.lista)
        return 'Modelos disponíveis:\n' + resultado

    def carregar(self) -> bool:
        """Carrega a lista de modelos do arquivo JSON."""
        try:
            with carregar_dados(ARQUIVO_DADOS) as dados:
                self.lista = [ModeloExigencia(codigo, item['texto']) for codigo, item in dados.items()]
        except OSError as err:
            print(f"Erro ao abrir arquivo de lista de modelos: {err.strerror}.")
            return False
        return True

    def obter(self, valor: str) -> ModeloExigencia | None:
        """Retorna um modelo conforme o ID especificado;"""
        for modelo in self.lista:
            if valor.casefold() == repr(modelo).casefold():
                return modelo
        return None