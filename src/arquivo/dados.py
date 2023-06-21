from json import load as load_fromjson
from os import path
from variaveis import Variaveis

class carregar_dados:
    def __init__(self, nome_arquivo: str):
        self.endereco_arquivo = path.join(Variaveis.obter_pasta_dados(), nome_arquivo)

    def __enter__(self):
       self.obj_arquivo = open(self.endereco_arquivo, 'r', encoding='utf8')
       return load_fromjson(self.obj_arquivo)

    def __exit__(self, type, val, tb):
        if self.obj_arquivo:
            self.obj_arquivo.close()
        