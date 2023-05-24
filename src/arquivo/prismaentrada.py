import os
from .manipuladorarquivos import Arquivo

class ArquivoPrismaEntrada(Arquivo):
    def __init__(self, nome_arquivo, atributos) -> None:
        super().__init__(nome_arquivo)
        self.atributos = atributos
        self.num_atributos = len(atributos)

    def carregar(self):        
        super().carregar()
        num_linhas = self.conteudo[0].strip()
        if not num_linhas.isnumeric():
            print('Aviso: O arquivo de entrada para processamento do Prisma está inconsistente. Informação sobre a quantidade de registros não foi encontrada.\n')
        num_registros = len(self.conteudo) - 1
        if int(num_linhas) != num_registros:
            print(f'Aviso: O arquivo de entrada para processamento do Prisma está inconsistente. Era(m) esperada(s) {num_linhas} entradas, mas foi(ram) encontrada(s) {num_registros} entrada(s).\n')
        for linha in self.conteudo[1:]:
            dado = linha.strip()
            itens = dado.split(' ', 1)
            protocolo = itens[0].strip()
            self.dados[protocolo] = [item.strip() for item in itens[1].split(' ')]
        self.conteudo.clear()
        self.carregado = True

    def salvar(self):
        self.conteudo = [f'{self.obter_tamanho()}']
        for chave, dados in self.dados.items():
            texto = self.lista_para_string(dados)
            self.conteudo.append(f'{chave} {texto}')
        super().salvar()