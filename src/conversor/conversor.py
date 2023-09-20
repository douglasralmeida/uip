import os
from pypdf import PdfReader, PdfWriter
from PIL import Image
from variaveis import Variaveis

class Conversor:
    def processar(self, origem: str, destino: str, relat: str, lista: list[str]) -> bool:
        self.relat = relat
        self.lista = lista
        if origem == 'pdf' and destino == 'txt':
            return self.converter_pdf_txt()
        else:
            return False

    def converter_pdf_txt(self) -> bool:
        nome_arquivo_pdf = ''
        nome_arquivo_txt = ''
        texto = ''

        for tarefa in self.lista:
            nome_arquivo_pdf = os.path.join(Variaveis.obter_pasta_pdf(), f'{tarefa} - {self.relat}.pdf')
            nome_arquivo_txt = os.path.join(Variaveis.obter_pasta_entrada(), f'{tarefa} - {self.relat}.txt')
            print(f"Processando tarefa {tarefa}...")
            try:
                with open(nome_arquivo_pdf, 'rb') as arquivo_pdf:
                    leitor = PdfReader(arquivo_pdf)
                    texto = leitor.pages[0].extract_text()
                    if len(leitor.pages) > 1:
                        texto += '\n'
                        texto += leitor.pages[1].extract_text()
                        texto += '\n'
            except OSError as err:
                print(f"Erro ao abrir arquivo PDF {tarefa} - {self.relat}.pdf: {err.strerror}.")
                return False
            try:
                with open(nome_arquivo_txt, 'w') as arquivo_txt:
                    arquivo_txt.write(texto)
            except OSError as err:
                print(f"Erro ao salvar arquivo texto {tarefa} - {self.relat}.txt: {err.strerror}.")
                return False
        return True