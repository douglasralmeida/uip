import os

class Arquivo:
    def __init__(self, nome_arquivo) -> None:
        self.carregado = False
        self.conteudo = []
        self.dados = {}
        self.nome_arquivo = nome_arquivo

    def alterar_dados(self, protocolo, dados):
        self.dados[protocolo] = dados

    def carregar(self):
        self.conteudo.clear()
        self.dados.clear()
        if not os.path.exists(self.nome_arquivo):
            print('Erro: Arquivo de entrada para processamento do Prisma não encontrado.')
            return
        with open(self.nome_arquivo, 'r') as arquivo:
            self.conteudo = arquivo.readlines()
        if len(self.conteudo) == 0:
            print('Aviso: O arquivo de entrada para processamento do Prisma está inconsistente. O arquivo está vazio.')
            return
        
    def excluir_dados(self, protocolo):
        self.dados.pop(protocolo)

    def lista_para_string(self, lista):
        return ' '.join(lista)
        
    def obter_dados(self, protocolo):
        return self.dados[protocolo]
    
    def obter_tamanho(self):
        return len(self.dados.items())

    def salvar(self):
        with open(self.nome_arquivo, 'w') as arquivo:
            arquivo.writelines('\n'.join(self.conteudo))
        self.conteudo.clear()