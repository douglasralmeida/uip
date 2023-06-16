## Codificado por Douglas Rodrigues de Almeida.
## Junho de 2023

"""Automatizador do SIBE BU."""

import time
from os import path
from .navegador import Navegador
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL_SIBE = 'http://www-portalsibe/'
URL_SISBEN = 'https://psibepuapr01a.prevnet/sisben-web/content/pesnb'

class Sibe(Navegador):
    """Classe do Automatizador do SIBE PU."""
    def __init__(self) -> None:
        super().__init__()

    def abrir(self):
        """Abre o SIBE."""
        self.driver.get(URL_SIBE)
        #Aguarda autenticação
        time.sleep(10)

    def aguardar_processamento(self) -> None:
        """Espera pelo encerramento da tela 'Aguardando processamento'"""
        espera = WebDriverWait(self.driver, 60, poll_frequency=1)
        #Aguarda pela invisibilidade do elemento
        espera.until(EC.invisibility_of_element((By.CLASS_NAME, '')))

    def abrir_sisben(self):
        """Abre a tela de consulta de benefícios."""
        drv = self.driver

        drv.get(URL_SISBEN)

    def coletar_dados_beneficio(self, beneficio) -> dict:
        """Coleta dados de benefício"""
        drv = self.driver
        res = {}
        res['sucesso'] = False

        self.aguardar_processamento_AngularJS()
        campo_nb = drv.find_element(By.TAG_NAME, 'input')
        campo_nb.send_keys(beneficio)

        botao_ok = drv.find_element(By.TAG_NAME, 'button')
        botao_ok.click()
        self.aguardar_processamento_AngularJS()

        time.sleep(4)
        lista = drv.find_elements(By.TAG_NAME, 'dtp-atributo')
        res['acompanhante'] = ''
        res['dcb'] = ''
        for campo in lista:
            if campo.get_dom_attribute('chave') is None:
                if len(campo.find_elements(By.TAG_NAME, 'label')) > 0:
                    if campo.find_element(By.TAG_NAME, 'label').text.startswith('DCB'):
                        if len(campo.find_elements(By.TAG_NAME, 'span')) > 0:
                            texto = campo.find_element(By.TAG_NAME, 'span').get_attribute('textContent')
                            res['dcb'] = texto
                continue            
            if campo.get_dom_attribute('chave').casefold() == 'espécie':
                texto = campo.find_element(By.TAG_NAME, 'span').get_attribute('textContent')
                res['especie'] = texto[:2]
                continue
            if campo.get_dom_attribute('chave').casefold() == 'situação':
                texto = campo.find_element(By.TAG_NAME, 'span').get_attribute('textContent')
                res['status_beneficio'] = texto
                continue                
            if campo.get_dom_attribute('chave').casefold() == 'dib':
                texto = campo.find_element(By.TAG_NAME, 'span').get_attribute('textContent')
                res['dib'] = texto
                continue
            if campo.get_dom_attribute('chave').casefold() == 'ol mantenedor':
                texto = campo.find_element(By.TAG_NAME, 'span').get_attribute('textContent')
                res['olm'] = texto[:10]
                continue
            if campo.get_dom_attribute('chave').casefold() == 'sistema de origem':
                texto = campo.find_element(By.TAG_NAME, 'span').get_attribute('textContent')
                res['sistema_mantenedor'] = texto
                continue
            if res['especie'] == '32':
                if campo.get_dom_attribute('chave').casefold() == 'acompanhante':
                    texto = campo.find_element(By.TAG_NAME, 'span').get_attribute('textContent')
                    res['acompanhante'] = texto
                    continue
        res['sucesso'] = True
        
        #self.executar_script('history.back();')
        self.sisben_clicarbotao('voltar')


        #if len(drv.find_elements(By.ID, 'mat-tab-label-0-11')) > 0:
        #    botao_voltar = drv.find_element(By.ID, 'mat-tab-label-0-11')
        #else:
        #    botao_voltar = drv.find_element(By.ID, 'mat-tab-label-1-11')
        #botao_voltar.click()

        return res

    def sisben_clicarbotao(self, nome):
        nav = self.driver

        barra_ferramentas = nav.find_element(By.CLASS_NAME, 'mat-tab-labels')
        botoes = barra_ferramentas.find_elements(By.CLASS_NAME, 'mat-ripple')
        for botao in botoes:
            if botao.get_dom_attribute('aria-label') == nome:
                botao.click()
                break