## Codificado por Douglas Rodrigues de Almeida.
## Março de 2023

"""Automatizador do PMF Agenda."""

import time
from .locaispm import LocaisPM
from .navegador import Navegador
from os import path
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Edge, Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from PIL import Image

class Pmfagenda(Navegador):
    """Classe do Automatizador do PMF Agenda."""

    locais_pm = None

    def abrir(self):
        self.driver.get("https://geridinss.dataprev.gov.br:8443/cas/login?service=https://www-pmfagenda/agenda/index.html")
        
        #Aguarda autenticação
        time.sleep(4)
        
        #Escolher o domínio
        WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable((By.ID, "domains")))
        selec = Select(self.driver.find_element(By.ID, value="domains"))
        selec.select_by_value("UO:11.001.040.APSBPE")
        time.sleep(1)
        
        #Clica no botão
        botao = self.driver.find_element(By.ID, value="botaoEnviar")
        botao.click()        
        
        #Aguarda a tela inicial
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.ID, "formAgendar:cpfInput")))
        time.sleep(1)

    def abrir_cpf_consulta(self, cpf: str) -> None:
        drv = self.driver

        cpf_preenchido = False
        #Aguarda o campo de CPF
        self.espera.until(EC.element_to_be_clickable((By.ID, "formAgendar:cpfInputConsultar")))
        while not cpf_preenchido:
            #Digita o CPF
            campo = drv.find_element(By.ID, value="formAgendar:cpfInputConsultar")
            campo.clear()
            campo.send_keys(cpf)
            time.sleep(2)

            #Clica no botao Consultar CPF
            botao = drv.find_element(By.ID, value="formAgendar:btnConsultarCpfConsulta")
            botao.click()
            self.aguardar_telaprocessamento()
            time.sleep(2)
            if drv.find_element(By.ID, 'idMessage').is_displayed():
                elemento = drv.find_element(By.ID, 'idMessage')
                lista = elemento.find_elements(By.CLASS_NAME, 'ui-messages-error-icon')
                cpf_preenchido = not len(lista) > 0
            else:
                cpf_preenchido = True

    def abrir_cpf_requerimento(self, cpf: str) -> None:
        drv = self.driver
    
        cpf_preenchido = False
        #Aguarda o campo de CPF
        self.espera.until(EC.element_to_be_clickable((By.ID, "formAgendar:cpfInput")))
        while not cpf_preenchido:
            #Digita o CPF
            campo = drv.find_element(By.ID, value="formAgendar:cpfInput")
            campo.clear()
            campo.send_keys(cpf)
            time.sleep(2)

            #Clica no botao Consultar CPF
            botao = drv.find_element(By.ID, value="formAgendar:btnConsultarCpfAgendamento")
            botao.click()
            self.aguardar_telaprocessamento()
            time.sleep(2)
            if drv.find_element(By.ID, 'idMessage').is_displayed():
                elemento = drv.find_element(By.ID, 'idMessage')
                lista = elemento.find_elements(By.CLASS_NAME, 'ui-messages-error-icon')
                cpf_preenchido = not len(lista) > 0
            else:
                cpf_preenchido = True
    
    def agendar(self, tarefa: str, cpf: str, servico: str, subtarefa: str, olm: str) -> list[str]:
        """Realiza um agendamento de PM."""
        drv = self.driver
        cpf_correto = False
        self.tarefa = tarefa
                
        while not cpf_correto:
            self.abrir_cpf_requerimento(cpf)
            
            #Seleciona o serviço
            self.espera.until(EC.presence_of_element_located((By.ID, 'formAgendar:servicoDrop_input')))
            self.espera.until(EC.element_to_be_clickable((By.ID, 'formAgendar:servicoDrop_input')))
            campo = drv.find_element(By.ID, value="formAgendar:servicoDrop_input")
            campo.clear()
            campo.send_keys(servico)
            time.sleep(2)
        
            #Clica na lista de opções
            campo = drv.find_element(By.ID, value="formAgendar:servicoDrop_panel")
            #campo = campo.find_element(By.TAG_NAME, value="ul")
            campo = campo.find_element(By.TAG_NAME, value="li")
            campo.click()
            time.sleep(2)
            self.aguardar_telaprocessamento()
            self.espera.until(EC.element_to_be_clickable((By.ID, 'formAgendar:btnAvancarParaDadosRequerente')))
        
            #Avança para próxima página
            botao = drv.find_element(By.ID, value="formAgendar:btnAvancarParaDadosRequerente") 
            botao.click()
        
            ##Aguarda pelo campo de tel. celular
            self.espera.until(EC.element_to_be_clickable((By.ID, 'formAgendarConsultar:fixoInput')))

            ## Necessário conferir o CPF
            ## Alguns casos o PMF Agenda agendou para CPF diferente
            ## por causas desconhecidas
            #cpf_completo = cpf.rjust(11, '0')
            #cpf_formatado = f'{cpf_completo[0:3]}.{cpf_completo[3:6]}.{cpf_completo[6:9]}-{cpf_completo[9:11]}'
            cpf_coletado = drv.find_element(By.ID, "formAgendarConsultar:cpfOutput").text
            if cpf != cpf_coletado:
                self.irpara_finaltela()
                drv.find_element(By.ID, 'frmBotoes:btnVoltarParaTelaInicial').click()
                cpf_preenchido = False
            else:
                cpf_correto = True
        
        #Digita um celular
        ActionChains(drv).send_keys(Keys.END).perform()
        campo = drv.find_element(By.ID, value="formAgendarConsultar:fixoInput")
        campo.clear()
        campo.send_keys("2123221100")
                
        #Digita a subtarefa
        campo = drv.find_element(By.ID, value="formAgendarConsultar:inputCampoNumerico0")
        campo.clear()
        campo.send_keys(subtarefa)
        
        #Clica em Avançar
        botao = drv.find_element(By.ID, value="frmBotoes:btnAvancarParaSelecaoVagas") 
        botao.click()
        self.aguardar_telaprocessamento()
               
        #Espera pelo campo CEP
        try:
            WebDriverWait(drv, 10).until(EC.element_to_be_clickable((By.ID, "form1:cepInput")))
            time.sleep(1)
        except TimeoutException:
            if len(elementos := drv.find_elements(By.TAG_NAME, value="h1")) > 0:
                texto = elementos[0].text
                if texto == "Serviço incompatível com o requerimento abaixo:":
                    return self.coletar_agendamento()
                else:
                    print("Erro ao agendar perícia.")
            else:
                print("Erro ao agendar perícia.")
        
        #Clica em Escolha um Município
        botao = drv.find_element(By.ID, value="linkOutroMunicipio") 
        botao.click()
        
        #Espera pelo campo de Estado
        #self.espera.until(EC.element_located_to_be_selected((By.ID, 'formMunicipio:ufDrop2')))
        time.sleep(1)
        self.espera.until(EC.element_to_be_clickable((By.ID, 'formMunicipio:ufDrop2')))

        localpm = self.locais_pm.obter(olm)
        if localpm is None:
            raise Exception(f'Local da PM ({repr(localpm)}) não está cadastrado no UIP.')
        
        #Escolhe o estado
        selec = Select(drv.find_element(By.ID, value="formMunicipio:ufDrop2"))
        selec.select_by_value(localpm.estado)
        time.sleep(2)
        self.espera.until(EC.presence_of_element_located((By.ID, 'formMunicipio:municipioDrop2_input')))
        self.espera.until(EC.element_to_be_clickable((By.ID, 'formMunicipio:municipioDrop2_input')))
        
        sem_vagas = True
        while sem_vagas:
            #Escolhe o município
            campo = drv.find_element(By.ID, value="formMunicipio:municipioDrop2_input")
            campo.clear()
            campo.send_keys(localpm.cidade)
            self.espera.until(EC.visibility_of_element_located((By.ID, 'formMunicipio:municipioDrop2_panel')))

            #Clica na cidade
            campo = drv.find_element(By.ID, value="formMunicipio:municipioDrop2_panel")
            campo = campo.find_element(By.TAG_NAME, "ul")
            campo = campo.find_element(By.TAG_NAME, "li")
            campo.click()
            self.aguardar_telaprocessamento()
            self.espera.until(EC.invisibility_of_element_located((By.ID, 'formMunicipio:municipioDrop2_panel')))
            time.sleep(2)
        
            #Clica em Buscar
            self.espera.until(EC.presence_of_element_located((By.ID, 'formMunicipio:carregarDisponibilidadeCombo')))
            self.espera.until(EC.element_to_be_clickable((By.ID, 'formMunicipio:carregarDisponibilidadeCombo')))
            botao = drv.find_element(By.ID, value="formMunicipio:carregarDisponibilidadeCombo")
            botao.click()
        
            #Espera pelar vagas
            WebDriverWait(drv, 75).until(EC.element_to_be_clickable((By.CLASS_NAME, "vagaSelected"))) 
        
            #Clica em Avançar
            botao = drv.find_element(By.ID, value="form-botoes:btnAvancarParaConfirmacao")
            botao.click()
            self.aguardar_telaprocessamento()
            time.sleep(2)
            sem_vagas = self.obter_msg_erro().startswith('Nesse momento não existe vaga disponível para o serviço solicitado')
        
        #Espera
        self.espera.until(EC.element_to_be_clickable((By.ID, 'form1:checkConcordo')))
        ActionChains(drv).send_keys(Keys.END).perform()
        
        #Excluir o rodapé para permitir clicar no checkbox
        elemento = drv.find_element(By.CLASS_NAME, value="idFooter")
        drv.execute_script("""
            var element = arguments[0];
            element.parentNode.removeChild(element);
        """, elemento)
        elemento = drv.find_element(By.CLASS_NAME, value="infoFooter")
        drv.execute_script("""
            var element = arguments[0];
            element.parentNode.removeChild(element);
        """, elemento)
        time.sleep(1)
        
        #Clicar em Concordo
        botao = drv.find_element(By.ID, value="form1:checkConcordo")
        botao.click()
        time.sleep(1)
        self.espera.until(EC.element_to_be_clickable((By.ID, 'form1:btnConfirmarVaga')))
        
        #Clicar em Confirmar
        botao = drv.find_element(By.ID, value="form1:btnConfirmarVaga")
        botao.click()
        
        #Esperar
        self.espera.until(EC.element_to_be_clickable((By.ID, 'form2:imprimirComprovante')))
        
        #Coletar dados do agendamento
        campo = drv.find_element(By.ID, value="form1:dataAgendaOutput")
        dataagenda = campo.text
        campo = drv.find_element(By.ID, value="form1:horarioOutput")
        horaagenda = campo.text[-5:]
        campo = drv.find_element(By.ID, value="form1:enderecoUoOutput")        
        localagenda = campo.text + " - "
        campo = drv.find_element(By.ID, value="form1:cidadeUoOutput")
        localagenda = localagenda + campo.text
        campo = drv.find_element(By.ID, value="form1:senhaAgendamento")
        protocolo = campo.text
                                               
        #Clicar em Gerar comprovante
        ActionChains(drv).send_keys(Keys.END).perform()
        time.sleep(1)
        botao = drv.find_element(By.ID, value="form2:imprimirComprovante")
        botao.click()
        
        #Aguardar e trocar para a guia do arquivo PDF
        arquivo_gerado = path.join(self.dir_downloads, 'finalizarAtendimento.xhtml.pdf')
        arquivo_novo = path.join(self.dir_downloads, f'{self.tarefa} - AgendaPM.pdf')
        self.manipular_pdf(arquivo_gerado, arquivo_novo)

        #Reinicia agendamento
        botao = drv.find_element(By.ID, value="form2:btnNovoRequerimento")
        botao.click()
        self.espera.until(EC.element_to_be_clickable((By.ID, 'formAgendar:cpfInput')))

        return [dataagenda, horaagenda, localagenda, protocolo]
    
    def aguardar_telaprocessamento(self) -> None:
        """Espera pelo encerramento da tela 'Aguardando processamento'"""
        #Aguarda pela invisibilidade do elemento
        WebDriverWait(self.driver, 60).until(EC.invisibility_of_element((By.CLASS_NAME, 'blockUI')))
    
    def carregar_dados(self):
        self.locais_pm = LocaisPM([])
        self.locais_pm.carregar()

    def obter_lista(self, servico: str) -> list[str]:
        i = 0
        lista = []
        nav = self.driver

        if len(nav.find_elements(By.ID, 'frmAgendamento:tabelaAgendamento:tbody_element')) == 0:
            return []

        tabela = nav.find_element(By.ID, 'frmAgendamento:tabelaAgendamento:tbody_element')
        linhas = tabela.find_elements(By.TAG_NAME, 'tr')
        for linha in linhas:
            colunas = linha.find_elements(By.TAG_NAME, 'td')
            item = colunas[0].find_element(By.TAG_NAME, 'span')
            protocolo = item.text
            item = colunas[1].find_element(By.TAG_NAME, 'span')
            data_agendamento = item.text
            item = colunas[2].find_element(By.TAG_NAME, 'span')
            hora_agendamento = item.text
            item = colunas[3].find_element(By.TAG_NAME, 'span')
            servico_agendamento = item.text.casefold()
            item = colunas[5].find_element(By.TAG_NAME, 'span')
            situacao = item.text
            pos = i
            i += 1
            if servico.casefold().startswith(servico_agendamento):
                lista.append({'protocolo': protocolo, 'data': data_agendamento, 'hora': hora_agendamento, 'situacao': situacao, 'pos': pos})
        return lista
    
    def obter_status(self, protocolo, lista):
        status = None
        pos = -1
        for item in lista:
            if protocolo == item['protocolo']:
                status = item['situacao']
                pos = item['pos']
        if status is None:
            return '', -1
        if status == 'Remarcado':
            remarcado = True
            while remarcado:
                pos -= 1
                remarcado = lista[pos]['situacao'] == 'Remarcado'
            status = lista[pos]['situacao']
        return status, pos

    def checar_comparecimento(self, servico, protocolo_agenda, protocolo_tarefa, cpf) -> str:
        drv = self.driver
        lista_agendamentos = []
        resultado = {'compareceu': False, 'data_remarcacao': '00/00/0000', 'hora_remarcacao': '00:00'}

        self.abrir_cpf_consulta(cpf)

        #Avançar
        self.espera.until(EC.presence_of_element_located((By.ID, 'formAgendar:btnValidarDados')))
        self.espera.until(EC.element_to_be_clickable((By.ID, 'formAgendar:btnValidarDados')))
        botao = drv.find_element(By.ID, value="formAgendar:btnValidarDados")
        botao.click()
        time.sleep(1)
        self.aguardar_telaprocessamento()
        time.sleep(1)

        lista_agendamentos = self.obter_lista(servico)
        status, pos = self.obter_status(protocolo_agenda, lista_agendamentos)
        
        if status in ['Agendado', 'Agendado Impactado']:
            pass
        else:
            if status == 'Cumprido':
                botao = drv.find_element(By.ID, f'frmAgendamento:tabelaAgendamentos:{pos}:linkVisualizarAgendamento')
                botao.click()
                self.aguardar_telaprocessamento()
                time.sleep(2)
            else:
                time.sleep(6)
            if len(drv.find_elements(By.ID, value="frmAgendamento:comparecimentoOutput")) == 0:
                status = ''
            else:
                status = drv.find_element(By.ID, value="frmAgendamento:comparecimentoOutput").text.strip()
            if status == '(não compareceu)':
                self.capturar_tela(protocolo_tarefa, "Tela")
                nome_arquivo_img = f"{protocolo_tarefa} - Tela.png"
                nome_arquivo_pdf = f"{protocolo_tarefa} - Analise.pdf"
                arquivo_imagem = path.join("arquivossaida", nome_arquivo_img)
                arquivo_pdf = path.join("arquivospdf", nome_arquivo_pdf)
                imagem = Image.open(arquivo_imagem)
                caixa = (360, 55, 1510, 740)
                imagem_editada = imagem.crop(caixa)
                imagem_editada.save(arquivo_pdf, "PDF")
            self.irpara_finaltela()
                
            #Voltar
            botao = drv.find_element(By.ID, value="frmAgendamento:btnVoltarInicial")
            botao.click()
            self.aguardar_telaprocessamento()

        self.irpara_finaltela()
        if len(drv.find_elements(By.ID, value="form2:btnAgendarAtendimento")) > 0:
            botao = drv.find_element(By.ID, value="form2:btnAgendarAtendimento")
            botao.click()
            self.aguardar_telaprocessamento()

        return status
    
    def coletar_agendamento(self) -> list[str]:
        """Coleta os dados do agendamento."""
        drv = self.driver

        campo = drv.find_element(By.ID, value="frmAgendamento:dataAgendaOutput")
        dataagenda = campo.text
        campo = drv.find_element(By.ID, value="frmAgendamento:horarioOutput")
        horaagenda = campo.text[-5:]
        campo = drv.find_element(By.ID, value="frmAgendamento:enderecoUoOutput")        
        localagenda = campo.text + " - "
        campo = drv.find_element(By.ID, value="frmAgendamento:cidadeUoOutput")
        localagenda = localagenda + campo.text
        campo = drv.find_element(By.ID, value="frmAgendamento:senhaAgendamento")
        protocolo = campo.text

        self.irpara_finaltela()
        time.sleep(1)
        self.clicar_botao('frmAgendamento:linkComprovanteAgendamentoIncompativel')
                
        #Aguarda e troca para a guia do arquivo PDF
        arquivo_gerado = path.join(self.dir_downloads, 'tratarServicoIncompativel.xhtml.pdf')
        arquivo_novo = path.join(self.dir_downloads, f'{self.tarefa} - AgendaPM.pdf')
        self.manipular_pdf(arquivo_gerado, arquivo_novo)
                
        #Reinicia agendamento
        botao = drv.find_element(By.ID, value="frmAgendamento:idVoltarDeTratarServicoIncompativel")
        botao.click()
        WebDriverWait(drv, 20).until(EC.element_to_be_clickable((By.ID, "formAgendarConsultar:celularInput")))

        #Excluir o rodapé para permitir clicar no checkbox
        elemento = drv.find_element(By.CLASS_NAME, value="idFooter")
        drv.execute_script("""
            var element = arguments[0];
            element.parentNode.removeChild(element);
        """, elemento)
        elemento = drv.find_element(By.CLASS_NAME, value="infoFooter")
        drv.execute_script("""
            var element = arguments[0];
            element.parentNode.removeChild(element);
        """, elemento)
        time.sleep(1)

        #Volta para tela inicial
        botao = drv.find_element(By.ID, value="frmBotoes:btnVoltarParaTelaInicial")
        botao.click()
                
        return [dataagenda, horaagenda, localagenda, protocolo]

    def reiniciar(self):
        self.driver.quit()
        time.sleep(5)
        self.driver = Edge(options=self.opcoes)
        self.driver.maximize_window()
        self.abrir()

    def obter_msg_erro(self) -> str:
        drv = self.driver

        campo = drv.find_element(By.ID, 'idMessage')
        if campo.is_displayed():
            if len(campo.find_elements(By.CLASS_NAME, 'ui-messages-error-detail')) > 0:
                return campo.find_element(By.CLASS_NAME, 'ui-messages-error-detail').text
        return ''