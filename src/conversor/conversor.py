import os
from pypdf import PdfReader
from variaveis import Variaveis

class Conversor:
    def processar(self, origem, destino, relat, lista):
        self.relat = relat
        self.lista = lista
        if origem == 'pdf' and destino == 'txt':
            self.converter_pdf_txt()

    def converter_pdf_txt(self):
        nome_arquivo_pdf = ''
        nome_arquivo_txt = ''
        texto = ''

        for tarefa in self.lista:
            nome_arquivo_pdf = os.path.join(Variaveis.obter_pasta_pdf(), f'{tarefa} - {self.relat}.pdf')
            nome_arquivo_txt = os.path.join(Variaveis.obter_pasta_entrada(), f'{tarefa} - {self.relat}.txt')
            print(f'Processando tarefa {tarefa}...')
            with open(nome_arquivo_pdf, 'rb') as arquivo_pdf:
                leitor = PdfReader(arquivo_pdf)
                for pagina in leitor.pages:
                    texto += pagina.extract_text()
                    texto += '\n'
            with open(nome_arquivo_txt, 'w') as arquivo_txt:
                arquivo_txt.write(texto)