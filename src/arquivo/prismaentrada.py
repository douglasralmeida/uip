## Codificado por Douglas Rodrigues de Almeida.
## Julho de 2023
"""Arquivo de Entrada Prisma"""

from .manipuladorarquivos import Arquivo
from .utils import lista_para_string

ERRO_ARQUIVO_SEMQUANTIDADE = 'Erro: O arquivo de entrada do Prisma está inconsistente. Informação sobre a quantidade de registros não foi encontrada.\n'

class ArquivoPrismaEntrada(Arquivo):
    """Classe para arquivos de entrada para processamento Prisma."""
    def __init__(self, nome_arquivo: str, atributos: list[str]) -> None:
        super().__init__(nome_arquivo)
        self.atributos = atributos
        self.num_atributos = len(atributos)

    def carregar(self) -> bool:
        """Carrega um arquivo de entrada Prisma na memória."""
        sucesso = super().carregar()
        if not sucesso:
            return False
        num_linhas = self.conteudo[0].strip()
        if not num_linhas.isnumeric():
            print(ERRO_ARQUIVO_SEMQUANTIDADE)
            return False
        num_linhas = int(num_linhas)
        num_registros = super().obter_tamanho()  - 1
        if num_linhas != num_registros:
            print(f'Erro: O arquivo de entrada do Prisma está inconsistente. Era(m) esperada(s) {num_linhas} entradas, mas foi(ram) encontrada(s) {num_registros} entrada(s).\n')
            return False
        for linha in self.conteudo[1:]:
            dado = linha.strip()
            itens = dado.split(' ', 1)
            protocolo = itens[0].strip()
            self.dados[protocolo] = [item.strip() for item in itens[1].split(' ')]
        self.conteudo.clear()
        self.carregado = True
        return True
    
    def obter_tamanho(self) -> int:
        return len(self.dados.items())

    def salvar(self):
        """Salva o arquivo de entrada Prisma na unidade de armazenamento."""
        self.conteudo = [f'{self.obter_tamanho()}']
        for chave, dados in self.dados.items():
            texto = lista_para_string(dados)
            self.conteudo.append(f'{chave} {texto}')
        super().salvar()