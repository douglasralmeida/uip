## Codificado por Douglas Rodrigues de Almeida.
## Março de 2023

"""Automatizador do CNIS."""

import time
from PIL import Image
from manipuladorpdf import ManipuladorPDF
from os import path, rename
from .navegador import Navegador
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
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
        campo.clear()
        campo.send_keys(Keys.HOME)
        campo.send_keys(cpf_completo)
        drv.find_element(By.ID, 'formNovo:acaoPesquisar').click()
        self.aguardar_processamento()
        try:
            WebDriverWait(self.driver, timeout=15).until(EC.presence_of_element_located((By.ID, 'formNovo:lista:0:botaoAcao'))).click()
            #WebDriverWait(self.driver, timeout=50).until(EC.visibility_of_element_located((By.ID, 'formNovo:lista:0:botaoAcao'))).click()
        except Exception:

            return False
        self.aguardar_processamento()
        return True
    
    def abrir_formulario(self, nome_form: str) -> None:
        """Abre um form na UI do CNIS"""
        script = f"mojarra.jsfcljs(document.getElementById('formMenu'),{{'{nome_form}':'{nome_form}'}},'')"
        self.executar_script(script)

        #Excluir rodapé
        self.excluir_rodape()

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
    
    def excluir_rodape(self) -> None:
        script = """
                    var element = document.querySelector("footer");
                    if (element)
                        element.parentNode.removeChild(element);
                 """
        self.executar_script(script)
    
    def gerar_docarrecada(self, protocolo: str, cpf: str) -> bool:
        """Gera uma copia PDF dos Documentos de Arrecadação"""
        nav = self.driver
        self.tarefa = protocolo

        #Abrir tela
        if self.tela_atual != 'CNIS_ConsultaDocArrecadao':
            self.abrir_formulario('formMenu:filtrarDocumentoArrecadacao')
            self.tela_atual = 'CNIS_ConsultaDocArrecadao'
        
        #Pesquisar o CPF especificado.
        WebDriverWait(self.driver, timeout=4).until(EC.visibility_of_element_located((By.ID, 'formDocumentoArrecadacao:nuDocumentoCPF')))
        campo = nav.find_element(By.ID, 'formDocumentoArrecadacao:nuDocumentoCPF')
        campo.send_keys(Keys.HOME)
        campo.send_keys(cpf)
        botao = nav.find_element(By.ID, 'formDocumentoArrecadacao:consultar')
        botao.click()
        self.aguardar_processamento()
        WebDriverWait(self.driver, timeout=60).until(EC.visibility_of_element_located((By.ID, 'formDocumentoArrecadacao:tabelaDocumentoArrecadacao')))
        time.sleep(1)

        #Gerar PDF
        pagina = nav.find_element(By.ID, 'formDocumentoArrecadacao:tabelaDocumentoArrecadacao')
        tabela = pagina.find_element(By.TAG_NAME, 'table')
        altura_tabela = tabela.size['height']

        if len(campo := nav.find_elements(By.CLASS_NAME, 'ui-messages-warn-detail')) > 0:
            altura_tabela += 50

        self.capturar_tela(self.tarefa, 'Tela')
        nome_arquivo_img = f"{self.tarefa} - Tela.png"
        nome_arquivo_pdf = f"{self.tarefa} - DocArrecadacao.pdf"
        arquivo_imagem = path.join("arquivossaida", nome_arquivo_img)
        arquivo_pdf = path.join("arquivospdf", nome_arquivo_pdf)
        imagem = Image.open(arquivo_imagem)
        largura, _ = imagem.size
        caixa = (20, 120, largura-20, 260 + altura_tabela)
        imagem_editada = imagem.crop(caixa)
        imagem_editada.save(arquivo_pdf, "PDF")

        botao = nav.find_element(By.ID, 'formDocumentoArrecadacao:voltar')
        botao.click()
        self.aguardar_processamento()
    
        return True
    
    def gerar_extratopj(self, protocolo: str, cpf: str) -> bool:
        """Gera uma copia PDF do Extrato PJ"""
        nav = self.driver
        self.tarefa = protocolo

        #Clicar no menu e reabrir a tela de pesquisa.
        if self.tela_atual != 'CNIS_ConsultaPJ':
            self.abrir_formulario('formMenu:consultarEmpregador')
            self.pesquisacpf_aberto = False

            #Espera pelo campo de consulta ao CNPJ
            WebDriverWait(self.driver, timeout=4).until(EC.visibility_of_element_located((By.ID, 'formNovo:opcoesConsulta:inputNumeroConsulta')))
            self.tela_atual = 'CNIS_ConsultaPJ'

        #Clica em consulta por CPF
        #time.sleep(3)
        if not self.pesquisacpf_aberto:
            nav.find_elements(By.CLASS_NAME, 'ui-accordion-header')[1].click()
            self.pesquisacpf_aberto = True
            time.sleep(2)
        self.aguardar_processamento()

        #Espera pelo campo de consulta por CPF, clica nele e informa o CPF
        WebDriverWait(self.driver, timeout=4).until(EC.visibility_of_element_located((By.ID, 'formNovo:opcoesConsulta:inputNumeroConsultaCpfQsa')))
        
        cpf_preenchido = False

        while not cpf_preenchido:
            controle = nav.find_element(By.ID, 'formNovo:opcoesConsulta:inputNumeroConsultaCpfQsa')
            controle.click()
            controle.send_keys(Keys.HOME)
            controle.send_keys(cpf)

            #Clica em pesquisar
            nav.find_element(By.ID, 'formNovo:acaoPesquisar').click()
            self.aguardar_processamento()
            time.sleep(1.2)

            cpf_preenchido = len((campos := nav.find_elements(By.CLASS_NAME, 'ui-messages-error-detail'))) == 0

        #Espera pela tabela de resultados
        try:
            WebDriverWait(self.driver, timeout=4).until(EC.visibility_of_element_located((By.ID, 'formNovo:tabelaEmpregador_data')))
        except:
            if len((campos := nav.find_elements(By.CLASS_NAME, 'ui-messages-warn-detail'))) > 0:
                msg = campos[0].text.strip()
                if msg.endswith('não encontrado'):
                    self.capturar_tela(self.tarefa, 'Tela')
                    nome_arquivo_img = f"{self.tarefa} - Tela.png"
                    nome_arquivo_pdf = f"{self.tarefa} - ExtratoPJ.pdf"
                    arquivo_imagem = path.join("arquivossaida", nome_arquivo_img)
                    arquivo_pdf = path.join("arquivospdf", nome_arquivo_pdf)
                    imagem = Image.open(arquivo_imagem)
                    largura, _ = imagem.size
                    caixa = (20, 110, largura-20, 370)
                    imagem_editada = imagem.crop(caixa)
                    imagem_editada.save(arquivo_pdf, "PDF")
                    return True
                else:
                    return False
        time.sleep(4)

        #Coleta CAEPF e CNPJ
        lista_caepf = []
        objeto = nav.find_element(By.ID, 'formNovo:tabelaEmpregador_data')
        tabela = objeto.find_elements(By.TAG_NAME, 'tr')
        lista_pdf_gerados = []
        linha_idx = 0
        for linha in tabela:
            tipo = linha.find_elements(By.TAG_NAME, 'td')[1].text.strip()
            if tipo in ['CAEPF', 'CNPJ']:
                botao = linha.find_element(By.ID, f'formNovo:tabelaEmpregador:{linha_idx}:imprimir')
                botao.click()
                arquivo_gerado = path.join(self.dir_downloads, 'consultarEmpregador.xhtml.pdf')
                arquivo_novo = path.join(self.dir_downloads, f'{self.tarefa} - ExtratoPJ_{len(lista_pdf_gerados)}.pdf')
                self.manipular_pdf(arquivo_gerado, arquivo_novo)
                lista_pdf_gerados.append(f'{self.tarefa} - ExtratoPJ_{len(lista_pdf_gerados)}')
            linha_idx += 1
        if len(lista_pdf_gerados) == 1:
            arquivo_antigo = path.join(self.dir_downloads, f'{self.tarefa} - ExtratoPJ_0.pdf')
            arquivo_novo = path.join(self.dir_downloads, f'{self.tarefa} - ExtratoPJ.pdf')
            rename(arquivo_antigo, arquivo_novo)
        if len(lista_pdf_gerados) > 1:
            manipulador = ManipuladorPDF()
            manipulador.juntar(lista_pdf_gerados, f'{self.tarefa} - ExtratoPJ')
        
        return True
    
    def gerar_extratosibe(self, protocolo: str, cpf: str) -> bool:
        """Gera uma copia PDF do Extrato CNIS SIBE"""
        nav = self.driver

        #Abrir tela
        if self.tela_atual != 'CNIS_ConsultaExtratoSIBE':
            self.abrir_formulario('formMenu:identificarFiliadoConsultaExtrato')
            self.tela_atual = 'CNIS_ConsultaExtratoSIBE'
        
        #Pesuisar o CPF especificado.
        self.abrir_cpf(cpf)
        self.tarefa = protocolo
        self.excluir_rodape()
        try:
            WebDriverWait(self.driver, timeout=4).until(EC.presence_of_element_located((By.ID, 'listarRelacoesPrevidenciarias')))
        except:
            if len((campos := nav.find_elements(By.CLASS_NAME, 'ui-messages-error-detail'))) > 0:
                return False
        
        #Gerar PDF
        botao = nav.find_element(By.ID, 'listarRelacoesPrevidenciarias:imprimirConsultaExtrato')
        ActionChains(nav).move_to_element(botao).perform()        
        #WebDriverWait(self.driver, timeout=4).until(EC.visibility_of_element_located((By.ID, 'listarRelacoesPrevidenciarias:imprimirConsultaExtrato')))
        botao.click()

        arquivo_gerado = path.join(self.dir_downloads, 'listarRelacoesPrevidenciarias.xhtml.pdf')
        arquivo_novo = path.join(self.dir_downloads, f'{self.tarefa} - ExtratoCNIS.pdf')
        self.manipular_pdf(arquivo_gerado, arquivo_novo)

        botao = nav.find_element(By.ID, 'listarRelacoesPrevidenciarias:identificarFiliadoConsultaExtrato')
        botao.click()

        return True
    
    def gerar_rgp(self, protocolo: str, cpf: str) -> bool:
        """Gera uma copia PDF da consulta RGP"""
        nav = self.driver
        self.tarefa = protocolo

        #Abrir tela
        self.abrir_formulario('formMenu:consultaRegistroPesca')
        self.tela_atual = 'CNIS_ConsultaRGP'
        
        #Pesquisar o CPF especificado.
        WebDriverWait(self.driver, timeout=4).until(EC.visibility_of_element_located((By.ID, 'formConsultaRGP:cpf')))
        campo = nav.find_element(By.ID, 'formConsultaRGP:cpf')
        campo.send_keys(Keys.HOME)
        campo.send_keys(cpf)
        botao = nav.find_element(By.ID, 'formConsultaRGP:consultar')
        botao.click()
    
        WebDriverWait(self.driver, timeout=60).until(EC.visibility_of_element_located((By.ID, 'formConsultaRGP:outputPanelInformacoesRGP')))

        #Gerar PDF
        pagina = nav.find_element(By.ID, 'formConsultaRGP:outputPanelInformacoesRGP')
        #tabela = pagina.find_element(By.TAG_NAME, 'table')
        altura_tabela = pagina.size['height']

        if len(campo := nav.find_elements(By.CLASS_NAME, 'ui-messages-error-detail')) > 0:
            texto = campo[0].text.strip()
            if texto.startswith('Registro geral de pesca não encontrado.'):
                altura_tabela += 50

        self.capturar_tela(self.tarefa, 'Tela')
        nome_arquivo_img = f"{self.tarefa} - Tela.png"
        nome_arquivo_pdf = f"{self.tarefa} - RGP.pdf"
        arquivo_imagem = path.join("arquivossaida", nome_arquivo_img)
        arquivo_pdf = path.join("arquivospdf", nome_arquivo_pdf)
        imagem = Image.open(arquivo_imagem)
        largura, _ = imagem.size
        caixa = (20, 90, largura-20, 260 + altura_tabela)
        imagem_editada = imagem.crop(caixa)
        imagem_editada.save(arquivo_pdf, "PDF")

        time.sleep(1)
    
        return True

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
        time.sleep(3)
        self.aguardar_processamento()

        num_itens = 0
        while num_itens < 2:
            tabela = drv.find_element(By.ID, 'formNovo:lista_data')
            try:
                itens = tabela.find_elements(By.TAG_NAME, 'td')
                num_itens = len(itens)
            except:
                num_itens = 0
        nit = itens[1].text
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