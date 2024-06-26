import json
import time
from os import path
from selenium.webdriver import Edge, EdgeOptions, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from variaveis import Variaveis
from .utils import aguardar_geracao_arquivo

ESPERA_PADRAO = 3

class Navegador:
    def  __init__(self) -> None:

        #Armazena o endereço onde serão gravados os arquivos PDF.
        self.dir_downloads = Variaveis.obter_pasta_pdf()

        #Tarefa
        self.tarefa = ''

        #Desabilita certas opções para agilizar automação
        self.modo_rapido = False

        #Flag a ser utilizado quando as condições de sistema
        #estiverem ruins.
        self.suspender_processamento = False
        
        #Configurações para impressão automática
        impresssao_config = {
            'recentDestinations': [{
                'id': 'Save as PDF',
                'origin': 'local',
                'account': '',
            }],
        'selectedDestinationId': 'Save as PDF',
        'version': 2
        }
        
        #Preferências do navegador
        prefs = {
            'browser.show_hub_popup_on_download_start': False,
            'download.default_directory': self.dir_downloads,
            'download.prompt_for_download': False,
            'download.directory_upgrade': True,
            'plugins.always_open_pdf_externally': True,
            'printing.print_preview_sticky_settings.appState': json.dumps(impresssao_config),
            'savefile.default_directory': self.dir_downloads
        }
        if self.modo_rapido:
            #Desabilita carregamento de imagens
            prefs['profile.managed_default_content_settings.images'] = 2
        self.opcoes = EdgeOptions()
        self.opcoes.add_argument('--allow-running-insecure-content')
        self.opcoes.add_argument('--disable-client-side-phishing-detection')
        self.opcoes.add_argument('--disable-extensions')
        self.opcoes.add_argument('--disable-component-extensions-with-background-pages')
        self.opcoes.add_argument('--disable-default-apps')
        self.opcoes.add_argument('--hide-scrollbars')
        self.opcoes.add_argument('--ignore-certificate-errors')
        self.opcoes.add_argument('--kiosk-printing')
        self.opcoes.add_argument('--no-proxy-server')     
        self.opcoes.add_argument('--enable-automation')
        self.opcoes.add_experimental_option('prefs', prefs)
        self.opcoes.add_experimental_option('excludeSwitches', ['enable-logging'])

        #Navegador de internet
        self.driver = Edge(options=self.opcoes)
        print(f'Navegador: {self.driver.capabilities["browserName"]}')
        print(f'Versão: {self.driver.capabilities["browserVersion"]}')
        self.driver.maximize_window()

        #Nome da tela atual
        self.tela_atual = ''

        #Espera de processamento
        self.tempo_espera = 30
        self.espera = WebDriverWait(self.driver, timeout=self.tempo_espera, poll_frequency=1)

    def aguardar_processamento_AngularJS(self):
        #script_conteudo = "return window.getAllAngularTestabilities().findIndex(x=>!x.isStable()) === -1"
        execucao_ok = False

        while not execucao_ok:
            time.sleep(1)
            #execucao_ok = bool(self.driver.execute_script(script_conteudo))
            execucao_ok = True
            time.sleep(1)

    def aguardar_visibilidade_elemento(self, elemento: str)-> bool:
        """Espera um elemento ficar visível na página"""
        if elemento.startswith('classe:'):
            tipo = By.CLASS_NAME
        elif elemento.startswith('id:'):
            tipo = By.ID
        try:
            self.espera.until(EC.visibility_of_element_located((tipo, elemento)))
        except:
            return False
        return True

    def imprimir_relatpm(self, idx):
        pass

    def capturar_tela(self, protocolo: str, sufixo: str) -> None:
        drv = self.driver

        nome_arquivo = f'{protocolo} - {sufixo}.png'
        arquivo_png = path.join("arquivossaida", nome_arquivo)
        drv.save_screenshot(arquivo_png)
        while not path.exists(arquivo_png):
            time.sleep(3)

    def clicar_botao(self, botao_id: str) -> None:
        """Clica no botão com o ID especificado."""
        drv = self.driver

        WebDriverWait(drv, 30).until(EC.element_to_be_clickable((By.ID, botao_id)))
        drv.find_element(By.ID, botao_id).click()

    def coletar_numero_porclasse(self, elemento_classe: str) -> str:
        """Coleta um número a partir de um texto."""
        drv = self.driver

        texto = drv.find_element(By.CLASS_NAME, elemento_classe).text
        resultado = [s for s in texto.split() if s.isdigit()][0]
        return resultado

    def fechar(self):
        """Encerra o navegador."""
        self.driver.quit()

    def executar_script(self, script):
        """Executa um script JS."""
        self.driver.execute_script(script)

    def irpara_finaltela(self) -> None:
        """Vai para o início da página."""
        ActionChains(self.driver).send_keys(Keys.END).perform()
        time.sleep(2)
    
    def irpara_iniciotela(self) -> None:
        """Vai para o final da página."""
        ActionChains(self.driver).send_keys(Keys.HOME).perform()
        time.sleep(2)

    def renomear_pdf(self, nome_arquivo_gerado: str, nome_arquivo_novo: str) -> None:
        """Muda o nome do arquivo PDF."""
        aguardar_geracao_arquivo(nome_arquivo_gerado, nome_arquivo_novo)

    def manipular_pdf(self, nome_arquivo_gerado: str, nome_arquivo_novo: str) -> None:
        """Salva o PDF gerado com o nome especificado."""
        drv = self.driver

        #Aguardar e trocar para a guia do arquivo PDF
        WebDriverWait(drv, 20).until(EC.number_of_windows_to_be(2))        
        drv.switch_to.window(drv.window_handles[1])
        time.sleep(1)
        
        #Salvar o PDF
        drv.execute_script('window.print();')
        self.renomear_pdf(nome_arquivo_gerado, nome_arquivo_novo)

        #Fecha a guia com o arquivo PDF
        drv.close()
        drv.switch_to.window(drv.window_handles[0])