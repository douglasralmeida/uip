## Codificado por Douglas Rodrigues de Almeida.
## Março de 2023

"""Automatizador do CNIS."""

import time
from os import path
from .navegador import Navegador
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL_CNIS_INTRANET = 'https://geridinss.dataprev.gov.br:8443/cas/login?service=http://pcnisapr02.prevnet/cnis/index.html'

class Cnis(Navegador):
    """Classe do Automatizador do Cnis."""
    def __init__(self) -> None:
        super().__init__()

    def abrir(self):
        """Abre o CNIS."""
        self.driver.get(URL_CNIS_INTRANET)
        #Aguarda autenticação
        time.sleep(10)

    def abrir_cpf(self, cpf: str) -> bool:
        """"""
        #drv = form
        drv = self.driver

        cpf_completo = cpf.rjust(11, '0')
        WebDriverWait(self.driver, timeout=7).until(EC.visibility_of_element_located((By.ID, 'formNovo:opcoesConsulta:inputNumeroConsulta')))
        campo = drv.find_element(By.ID, 'formNovo:opcoesConsulta:inputNumeroConsulta')
        campo.click()
        campo.send_keys(cpf_completo)
        drv.find_element(By.ID, 'formNovo:acaoPesquisar').click()
        self.aguardar_processamento()
        try:
            WebDriverWait(self.driver, timeout=50).until(EC.presence_of_element_located((By.ID, 'formNovo:lista:0:botaoAcao'))).click()
            #WebDriverWait(self.driver, timeout=50).until(EC.visibility_of_element_located((By.ID, 'formNovo:lista:0:botaoAcao'))).click()
        except Exception:

            return False
        self.aguardar_processamento()
        return True

    def aguardar_processamento(self) -> None:
        """Espera pelo encerramento da tela 'Aguardando processamento'"""
        espera = WebDriverWait(self.driver, 60, poll_frequency=1)
        #Aguarda pela invisibilidade do elemento
        espera.until(EC.invisibility_of_element((By.CLASS_NAME, 'blockUI')))

    def coletar_beneficios(self, cpf, especies):
        """Coleta os benefícios de uma determinada lista de espécie."""
        drv = self.driver
        lista_beneficio = []
        lista_dib = []
        lista_status = []
        lista_especie = []
        resultado = {}

        resultado['quantidade'] = 0
        #Clicar no menu e reabrir a tela de pesquisa.
        drv.find_element(By.ID, 'itemMenuConsultasDoSistema').click()
        drv.find_element(By.ID, 'formMenu:historicoBeneficio').click()

        #Pesuisar o CPF especificado.
        if not self.abrir_cpf(cpf):
            return resultado
        try:
            WebDriverWait(self.driver, timeout=5).until(EC.presence_of_element_located((By.ID, 'exibirHistoricoBeneficios')))
        except:
            if len((campos := drv.find_elements(By.CLASS_NAME, 'ui-messages-error-detail'))) > 0:
                if campos[0].text == 'Filiado sem benefícios':
                    return resultado
                
        #Raspagem no histórico de benefícios
        form = drv.find_element(By.ID, 'exibirHistoricoBeneficios')           
        campo = form.find_element(By.ID, 'exibirHistoricoBeneficios:list:tbody_element')
        resultado['quantidade'] = len(campo.find_elements(By.TAG_NAME, 'tr'))
        for item in campo.find_elements(By.TAG_NAME, 'tr'):
            nb = item.find_elements(By.TAG_NAME, 'td')[0].text.strip()
            dib = item.find_elements(By.TAG_NAME, 'td')[1].text.strip()
            status = item.find_elements(By.TAG_NAME, 'td')[3].text.strip()[:1]
            especie = item.find_elements(By.TAG_NAME, 'td')[4].text.strip()[:2]
            if len(especies) == 0 or especie in especies:
                resultado['quantidade'] += 1
                lista_beneficio.append(nb)
                lista_dib.append(dib)
                lista_status.append(status)
                lista_especie.append(especie)
        resultado['beneficio'] = ' '.join(lista_beneficio)
        resultado['dib'] = ' '.join(lista_dib)
        resultado['status'] = ' '.join(lista_status)
        resultado['especie'] = ' '.join(lista_especie)
        return resultado

    def pesquisar_nit_decpf(self, protocolo: str, cpf: str) -> str:
        """Retorna um NIT relacionado ao CPF informado."""
        drv = self.driver

        #Clicar no menu e reabrir a tela de pesquisa.
        drv.find_element(By.ID, 'itemMenuConsultasDoSistema').click()
        drv.find_element(By.ID, 'formMenu:identificarFiliadoConsultaExtratoCidadao').click()
        WebDriverWait(self.driver, timeout=5).until(EC.visibility_of_element_located((By.ID, 'formNovo:opcoesConsulta:inputNumeroConsulta')))
        campo = drv.find_element(By.ID, 'formNovo:opcoesConsulta:inputNumeroConsulta')
        campo.click()
        campo.send_keys(cpf)
        drv.find_element(By.ID, 'formNovo:acaoPesquisar').click()
        self.aguardar_processamento()
        tabela = drv.find_element(By.ID, 'formNovo:lista_data')
        nit = tabela.find_elements(By.TAG_NAME, 'td')[1].text
        return f'{nit[0:3]}.{nit[3:8]}.{nit[8:10]}-{nit[10]}'

    def pesquisar_ben_ativos(self, protocolo: str, cpf: str, especies: list[str]) -> bool:
        """Verifica se existe BEN ativo para o CPF informado e gera seu relatório."""
        STATUS_ATIVO = '0 - ATIVO'
        drv = self.driver

        #Clicar no menu e reabrir a tela de pesquisa.
        drv.find_element(By.ID, 'itemMenuConsultasDoSistema').click()
        drv.find_element(By.ID, 'formMenu:historicoBeneficio').click()
        

        #Pesuisar o CPF especificado.
        self.abrir_cpf(cpf)
        self.tarefa = protocolo
        try:
            WebDriverWait(self.driver, timeout=4).until(EC.presence_of_element_located((By.ID, 'exibirHistoricoBeneficios')))
        except:
            if len((campos := drv.find_elements(By.CLASS_NAME, 'ui-messages-error-detail'))) > 0:
                if campos[0].text == 'Filiado sem benefícios':
                    return False
                
        #Raspagem no histórico de benefícios
        form = drv.find_element(By.ID, 'exibirHistoricoBeneficios')           
        campo = form.find_element(By.ID, 'exibirHistoricoBeneficios:list:tbody_element')
        for item in campo.find_elements(By.TAG_NAME, 'tr'):
            nb = item.find_elements(By.TAG_NAME, 'td')[0].text.strip()
            status = item.find_elements(By.TAG_NAME, 'td')[3].text.strip()
            especie = item.find_elements(By.TAG_NAME, 'td')[4].text.strip()[2]
            if (status == STATUS_ATIVO and not especie in especies):
                form.find_element(By.ID, 'exibirHistoricoBeneficios:Imprimir').click()
                arquivo_gerado = path.join(self.dir_downloads, 'exibirHistoricoBeneficios.xhtml.pdf')
                arquivo_novo = path.join(self.dir_downloads, f'{self.tarefa} - Analise.pdf')
                self.manipular_pdf(arquivo_gerado, arquivo_novo)
                return True
        return False