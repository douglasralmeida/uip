from os import path
from variaveis import Variaveis

class carregar_texto:
    def __init__(self, nome_arquivo: str) -> None:
        self.endereco_arquivo = path.join(Variaveis.obter_pasta_entrada(), nome_arquivo)

    def __enter__(self) -> list[str]:
       self.obj_arquivo = open(self.endereco_arquivo, 'rt', encoding='utf-8-sig')
       lista = [item.strip() for item in self.obj_arquivo.readlines()]
       return lista

    def __exit__(self, type, val, tb) -> None:
        if self.obj_arquivo:
            self.obj_arquivo.close()