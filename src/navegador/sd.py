## Codificado por Douglas Rodrigues de Almeida.
## Outubro de 2023

"""Automatizador do Seguro Defeso MTE."""

import time
import os
from PIL import Image
from .navegador import Navegador
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL_SD = 'https://sd.mte.gov.br/'

URL_CONSULTA = 'sd/paginas/requerimentopescador/pesquisar.jsf'

class SD(Navegador):
    """Classe do Automatizador do sd."""
    def __init__(self) -> None:
        super().__init__()

    def abrir(self):
        """Abre o sd."""
        self.driver.get(URL_SD)
        #Aguarda autenticação
        time.sleep(10)

    def aguardar_processamento(self) -> None:
        """Espera pelo encerramento da tela 'Aguardando processamento'"""
        #espera = WebDriverWait(self.driver, 60, poll_frequency=1)
        #Aguarda pela invisibilidade do elemento
        #espera.until(EC.invisibility_of_element((By.CLASS_NAME, '')))

    def abrir_consulta(self):
        """Abre a tela de consulta de benefício."""
        nav = self.driver

        nav.get(URL_SD + URL_CONSULTA)
        self.tela_atual = 'SD_ConsultaCPF'
        WebDriverWait(self.driver, timeout=60).until(EC.visibility_of_element_located((By.ID, 'PesqRequerimento:txtCPF')))

    def consultar_cpf(self, protocolo, cpf) -> bool:
        """Consulta SD por CPF"""
        encontrou_sd = False
        nav = self.driver
        self.tarefa = protocolo

        #Informar o CPF
        campo = nav.find_element(By.ID, 'PesqRequerimento:txtCPF')
        campo.clear()
        campo.send_keys(Keys.HOME)
        campo.send_keys(cpf)

        #Clicar no botao de Pesquisa
        botao = nav.find_element(By.ID, 'PesqRequerimento:consultar')
        botao.click()

        #Espera pelo resultado
        try: 
            WebDriverWait(self.driver, timeout=4).until(EC.visibility_of_element_located((By.ID, 'ResultadoPesqRequerimentoPesquisarPescador:listaRequerimentos')))
            encontrou_sd = True
        except:
            if len(campo := nav.find_elements(By.ID, 'aviso2')) > 0:
                texto = campo[0].text.strip()
                if not texto.startswith('Nenhum Requerimento'):
                    return False

        #Gerar PDF da tela
        self.gerarpdf_tela('SD')
        if encontrou_sd:
            time.sleep(2)

        return True
    
    def gerarpdf_tela(self, nome_tela: str) -> None:
        nav = self.driver

        pagina = nav.find_element(By.ID, 'conteudo')
        altura = pagina.size['height']
        largura = pagina.size['width']
        ponto_esquerda = nav.get_window_rect()['width'] / 2 - largura / 2 - 33
        ponto_direita = nav.get_window_rect()['width'] / 2 + largura / 2 - 33

        self.capturar_tela(self.tarefa, 'Tela')
        nome_arquivo_img = f"{self.tarefa} - Tela.png"
        nome_arquivo_pdf = f"{self.tarefa} - {nome_tela}.pdf"
        arquivo_imagem = os.path.join("arquivossaida", nome_arquivo_img)
        arquivo_pdf = os.path.join("arquivospdf", nome_arquivo_pdf)
        imagem = Image.open(arquivo_imagem)
        largura, _ = imagem.size
        caixa = (ponto_esquerda, 140, ponto_direita, 140 + altura)
        imagem_editada = imagem.crop(caixa)
        imagem_editada.save(arquivo_pdf, "PDF")

    def gerar_resultado(self, protocolo: str, nsd: str) -> bool:
        nav = self.driver
        encontrou_sd = False
        self.tarefa = protocolo

        #Informar o NSD
        campo = nav.find_element(By.ID, 'PesqRequerimento:txtNumRequerimento')
        campo.clear()
        campo.send_keys(Keys.HOME)
        campo.send_keys(nsd)

        #Clicar no botao de Pesquisa
        botao = nav.find_element(By.ID, 'PesqRequerimento:consultar')
        botao.click()

        #Espera pelo resultado
        try: 
            WebDriverWait(nav, timeout=6).until(EC.visibility_of_element_located((By.ID, 'ResultadoPesqRequerimentoPesquisarPescador:listaRequerimentos:0:visualizarRequerimento')))
            encontrou_sd = True
        except:
            if len(campo := nav.find_elements(By.ID, 'aviso2')) > 0:
                texto = campo[0].text.strip()
                if not texto.startswith('Nenhum Requerimento'):
                    return False

        #Clicar no req. correspondente
        lista_idx = 0
        botao = nav.find_element(By.ID, f'ResultadoPesqRequerimentoPesquisarPescador:listaRequerimentos:{lista_idx}:visualizarRequerimento')
        botao.click()

        #Espera pelo requerimento
        WebDriverWait(nav, timeout=4).until(EC.visibility_of_element_located((By.ID, 'f:BtImprimeAgente')))

        #Gerar PDF
        botao = nav.find_element(By.ID, 'f:BtImprimeAgente')
        botao.click()

        arquivo_gerado = os.path.join(self.dir_downloads, 'situacaoRequerimento.jsf.pdf')
        arquivo_novo = os.path.join(self.dir_downloads, f'{self.tarefa} - Resultado.pdf')
        self.manipular_pdf(arquivo_gerado, arquivo_novo)

        # Voltar
        self.irpara_finaltela()
        botao = nav.find_element(By.ID, 'f:BtVoltar')
        botao.click()
        WebDriverWait(self.driver, timeout=10).until(EC.visibility_of_element_located((By.ID, 'PesqRequerimento:txtCPF')))
        time.sleep(2)
        
        return True