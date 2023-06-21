## Codificado por Douglas Rodrigues de Almeida.
## Julho de 2023
"""Arquivo de Saída Prisma"""

from .manipuladorarquivos import Arquivo
from .utils import lista_para_string

class ArquivoPrismaSaida(Arquivo):
    """Classe para arquivos de saída para processamento Prisma."""
    def __init__(self, nome_arquivo: str, atributos: list[str]) -> None:
        super().__init__(nome_arquivo)
        self.atributos = atributos
        self.num_atributos = len(atributos)

    def carregar(self) -> bool:
        """Carrega um arquivo de saída do Prisma na memória."""
        i = 0
        sucesso = super().carregar()
        if not sucesso:
            return False
        cabecalho = [item.strip() for item in self.conteudo[0].split(' ')]
        for item in cabecalho:
            if item != self.atributos[i]:
                print(f'Aviso: O arquivo de saída do Prisma está inconsistente. O cabeçalho difere do esperado ({item} != {self.atributos[i]}).')
                return False
            i += 1
        for linha in self.conteudo[1:]:
            dado = linha.strip()
            itens = dado.split(' ', 1)
            protocolo = itens[0].strip()
            self.dados[protocolo] = [item.strip() for item in itens[1].split(' ')]
        self.conteudo.clear()
        self.carregado = True
        return True

    def salvar(self):
        """Salva o arquivo de saída Prisma na unidade de armazenamento."""
        self.conteudo.append(lista_para_string(self.atributos))
        for chave, dados in self.dados.items():
            texto = lista_para_string(dados)
            self.conteudo.append(f'{chave} {texto}')
        super().salvar()