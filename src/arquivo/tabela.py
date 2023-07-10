from .csvexceptions import BadCSVException
from os import path
from variaveis import Variaveis

class carregar_tabela:
    def __init__(self, nome_arquivo: str) -> None:
        self.endereco_arquivo = path.join(Variaveis.obter_pasta_entrada(), nome_arquivo)

    def __enter__(self) -> list[list[str]]:
        num_registros = 0
        num_atributos = 0
        registros = []
        self.obj_arquivo = open(self.endereco_arquivo, 'rt', encoding='utf-8-sig')
        for registro in self.obj_arquivo.readlines():
            dados = registro.split(';')
            if num_registros == 0:
                num_atributos = len(dados)
            else:
                if len(dados) != num_atributos:
                    raise BadCSVException(f"O arquivo CSV está mal formatado. Eram esperadas {num_atributos} colunas, mas foram encontradas {len(dados)} colunas.")
            registros.append(dados)
            num_registros += 1
        return registros

    def __exit__(self, type, val, tb) -> None:
        if self.obj_arquivo:
            self.obj_arquivo.close()