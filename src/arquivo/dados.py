from json import load as load_fromjson
from os import path
from variaveis import Variaveis

class carregar_dados:
    def __init__(self, nome_arquivo: str) -> None:
        self.endereco_arquivo = path.join(Variaveis.obter_pasta_dados(), nome_arquivo)

    def __enter__(self) -> dict:
       self.obj_arquivo = open(self.endereco_arquivo, 'rt', encoding='utf-8-sig')
       return load_fromjson(self.obj_arquivo)

    def __exit__(self, type, val, tb) -> None:
        if self.obj_arquivo:
            self.obj_arquivo.close()
        