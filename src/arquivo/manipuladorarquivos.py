## Codificado por Douglas Rodrigues de Almeida.
## Julho de 2023
"""Arquivo"""

from os import path

ERRO_ARQUIVO_NAOENCONTRADO = 'Erro: O Arquivo de Entrada do Prisma não foi encontrado.'

ERRO_ARQUIVO_INCONSISTENTE = 'Aviso: O Arquivo de Entrada do Prisma está inconsistente. O arquivo está vazio.'

class Arquivo:
    """Classe para representar um arquivo texto."""
    def __init__(self, nome_arquivo: str) -> None:
        self.carregado = False
        self.conteudo = []
        self.dados = {}
        self.nome_arquivo = nome_arquivo

    def alterar_dados(self, protocolo: str, dados: list[str]):
        """Adiciona um protocolo no arquivo."""
        self.dados[protocolo] = dados

    def carregar(self) -> bool:
        """Carrega um arquivo texto na memória."""
        self.conteudo.clear()
        self.dados.clear()
        if not path.exists(self.nome_arquivo):
            print(ERRO_ARQUIVO_NAOENCONTRADO)
            return False
        with open(self.nome_arquivo, 'rt') as arquivo:
            self.conteudo = arquivo.readlines()
        if len(self.conteudo) == 0:
            print(ERRO_ARQUIVO_INCONSISTENTE)
            return False
        return True
        
    def excluir_dados(self, protocolo: str):
        """Exclui um protocolo do arquivo."""
        self.dados.pop(protocolo)
       
    def obter_dados(self, protocolo: str) -> list[str]:
        """Obtém os dados de um protocolo que está no arquivo."""
        return self.dados[protocolo]
    
    def obter_tamanho(self) -> int:
        """Obtém o número de linhas do arquivo."""
        return len(self.conteudo)

    def salvar(self):
        """Salva o arquivo na unidade de armazenamento."""
        with open(self.nome_arquivo, 'w') as arquivo:
            arquivo.writelines('\n'.join(self.conteudo))
        self.conteudo.clear()