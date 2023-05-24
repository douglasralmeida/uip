import os

class Variaveis:
    @staticmethod
    def obter_pasta_dados():
        return os.path.join(os.getcwd(), 'dados')

    @staticmethod
    def obter_pasta_entrada():
        return os.path.join(os.getcwd(), 'arquivosentrada')

    @staticmethod
    def obter_pasta_pdf():
        return os.path.join(os.getcwd(), 'arquivospdf')
    
    @staticmethod
    def obter_pasta_saida():
        return os.path.join(os.getcwd(), 'arquivossaida')