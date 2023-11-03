import os
from pypdf import PdfWriter
from variaveis import Variaveis

class ManipuladorPDF:
    def juntar(self, lista: list[str], destino: str) -> bool:
        nome_arquivopdf_destino = os.path.join(Variaveis.obter_pasta_pdf(), f'{destino}.pdf')

        juntador = PdfWriter()

        #Junta os PDFs
        for arquivo in lista:
            nome_arquivopdf = os.path.join(Variaveis.obter_pasta_pdf(), f'{arquivo}.pdf')
            if os.path.exists(nome_arquivopdf):
                juntador.append(nome_arquivopdf)
        juntador.write(nome_arquivopdf_destino)

        #Excluir os arquivos juntados, exceto pre-analise.
        #for arquivo in lista:
        #    if not arquivo.endswith('PreAnalise'):
        #        nome_arquivopdf = os.path.join(Variaveis.obter_pasta_pdf(), f'{arquivo}.pdf')
        #        if os.path.exists(nome_arquivopdf):
        #            os.remove(nome_arquivopdf)
        return True