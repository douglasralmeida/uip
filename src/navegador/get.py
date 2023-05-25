## Codificado por Douglas Rodrigues de Almeida.
## Março de 2023

"""Automatizador do GET."""

import time
from .navegador import Navegador
from .utils import aguardar_geracao_arquivo
from os import path
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL_GET_INTRANET = 'https://geridinss.dataprev.gov.br:8443/cas/login?service=https://www-tarefas/tarefas'
URL_GET_INTERNET = 'https://geridinss.dataprev.gov.br:8443/cas/login?service=https://www.tarefas.inss.gov.br/tarefasinternet'
URL_DOMINIOS_INTRANET = 'https://www-tarefas/tarefas/pages/comum/domainSelection.xhtml'
URL_DOMINIOS_INTERNET = 'https://www.tarefas.inss.gov.br/tarefasinternet/pages/comum/domainSelection.xhtml'

class Get(Navegador):
    """Classe do Automatizador do GET."""
    def __init__(self, criarsub_modolinha) -> None:
        super().__init__()
        
        #Modo de preencher os campos adicionais de uma subtarefa
        self.criarsub_modolinha = criarsub_modolinha
    
    def abrir(self, intranet):
        """Abre o GET."""
        if intranet:
            self.driver.get(URL_GET_INTRANET)
        else:
            self.driver.get(URL_GET_INTERNET)
        
        #Aguarda autenticação
        time.sleep(10)
        if intranet:
            self.driver.get(URL_DOMINIOS_INTRANET)
        else:
            self.driver.get(URL_DOMINIOS_INTERNET)

    def abrir_tarefa(self) -> None:
        """Abre a primeira tarefa da lsita de tarefas exibidas."""
        #Clica em detalhar tarefa
        self.clicar_botao('formTarefas:gridTarefa:0:cmdLinkDetalharTarefa')
        self.aguardar_telaprocessamento()
    
        ##Aguarda abertura da tarefa
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.CLASS_NAME, 'panel-title')))
        time.sleep(1)

    def adicionar_despacho(self, texto: str) -> None:
        """Adiciona despacho na tarefa."""
        drv = self.driver
    
        #Inserir texto
        campo = drv.find_element(By.CLASS_NAME, value="ql-editor")
        campo.click()
        campo.send_keys(texto)    
        drv.execute_script("document.activeElement.blur();", "")
        drv.execute_script("window.getSelection().removeAllRanges();", "")
        time.sleep(3)
    
        ##Clicar no botão
        drv.execute_script("window.scrollBy(0, document.body.scrollHeight)", "")
        botao = drv.find_element(By.ID, value="formDetalharTarefa:detalheTarefaTabView:btNovoComentario")
        botao.click()
    
        ##Aguarda pela msg Despcho incluído com sucesso
        WebDriverWait(drv, 20).until(EC.visibility_of_element_located((By.CLASS_NAME, "ui-messages-info"))).get_attribute("value")
        time.sleep(1)

    def adicionar_anexo(self, nomearquivo: str) -> None:
        """Anexa o arquivo PDF na tarefa."""
        drv = self.driver

        #Informa o nome do arquivo para anexar
        elem = drv.find_element(By.ID, 'formAnexo:uploadAnexo_input')
        elem.send_keys(nomearquivo)
        WebDriverWait(drv, 30).until(EC.element_to_be_clickable((By.ID, 'formAnexo:dtblAnexo:0:txtNomeArquivoAnexo')))

        #Clica no botão Incluir Anexo
        drv.find_element(By.ID, 'formAnexo:btIncluirAnexo').click()
        self.aguardar_telaprocessamento()
        time.sleep(1)

    def aguardar_telaprocessamento(self) -> None:
        """Espera pelo encerramento da tela 'Aguardando processamento'"""
        #Aguarda pela invisibilidade do elemento
        WebDriverWait(self.driver, 60).until(EC.invisibility_of_element((By.ID, 'loaderBlock')))

    def alterar_modolinha(self, valor: bool) -> None:
        """Altera o modo de criação de subtarefa."""
        self.criarsub_modolinha = valor

    def cancelar_sub(self, protocolo: str, nome_servico: str, texto_justificativa: str) -> bool:
        """Cancela no GET a subtarefa especificada."""
        drv = self.driver
        idx = 0

        #Coleta as subtarefas
        lista_subtarefas = self.coletar_subtarefas('', nome_servico, False)
        for item in lista_subtarefas:
            numsub = item[0]
            status = item[1]
            if numsub == protocolo:
                if status == "Concluida":
                    print('Erro: Subtarefa já está concluída.\n')
                    return
                
                # Clica no botão de cancelar subtarefa
                self.irpara_finaltela()
                self.clicar_botao(f'formDetalharTarefa:detalheTarefaTabView:dtblSubtarefasPericias:{idx}:cmdLinkCancelarPericia')
                time.sleep(1)
                WebDriverWait(drv, 20).until(EC.element_to_be_clickable((By.ID, 'formDetalharTarefa:detalheTarefaTabView:formMudancaSituacaoTarefaDialog_cancelarPericia:motivoCancelamento')))

                # Clica no item Motivo do Cancelamento
                self.clicar_botao('formDetalharTarefa:detalheTarefaTabView:formMudancaSituacaoTarefaDialog_cancelarPericia:motivoCancelamento')
                time.sleep(1)

                #Escolhe o motivo de cancelamento
                self.clicar_botao('formDetalharTarefa:detalheTarefaTabView:formMudancaSituacaoTarefaDialog_cancelarPericia:motivoCancelamento_2')

                #Despacho de cancelamento
                campo = drv.find_element(By.ID, 'formDetalharTarefa:detalheTarefaTabView:formMudancaSituacaoTarefaDialog_cancelarPericia:justificativaMudancaSituacaoTarefa_cancelarPericia_editor')
                campo = campo.find_element(By.CLASS_NAME, value="ql-editor")
                campo.click()
                campo.send_keys(Keys.CONTROL, 'A')
                campo.send_keys(Keys.DELETE)    
                campo.send_keys(texto_justificativa)

                # Clica no botão Cancelar
                self.clicar_botao('formDetalharTarefa:detalheTarefaTabView:formMudancaSituacaoTarefaDialog_cancelarPericia:btnCancelar')
                self.aguardar_telaprocessamento()
                try:
                    WebDriverWait(drv, 8).until(EC.visibility_of_element_located((By.CLASS_NAME, "ui-messages-info")))
                except:
                    WebDriverWait(drv, 5).until(EC.visibility_of_element_located((By.CLASS_NAME, "ui-messages-error-summary")))
                    campo = drv.find_element(By.CLASS_NAME, 'ui-messages-error-summary')
                    print(f'Erro: {campo.text}')
                    return False
                time.sleep(1)
            idx += 1
        return True

    def coletar_dados(self, tarefa: str, nome_servico: str, atributos: list) -> dict:
        """Coleta os dados especificados no GET."""
        drv = self.driver
        resultado = dict()
        
        #Coleta a DER
        if 'der' in atributos:
            campo = drv.find_element(By.CLASS_NAME, value="dtp-resume-info")
            campo = campo.find_elements(By.CLASS_NAME, value="row")[1]
            campo = campo.find_elements(By.CLASS_NAME, value="col-sm-5")[0]
            texto = campo.find_element(By.TAG_NAME, value="p").text
            resultado["der"] = texto[:10] #somente a data
        
        #Coleta o NB
        if 'nb' in atributos:
            campo = drv.find_element(By.ID, value="formDetalharTarefa:detalheTarefaTabView:panelCamposAdicionaisTarefa")
            campo = campo.find_element(By.CLASS_NAME, value="form-group")
            descricao = campo.find_element(By.TAG_NAME, value="label").text
            if descricao.casefold() in ['nb']:
                texto = campo.find_element(By.TAG_NAME, value="div").text
                resultado['nb'] = texto
            else:
                resultado['nb'] = ''
        
        #Coleta o CPF
        if 'cpf' in atributos:
            campo = drv.find_element(By.ID, value="formDetalharTarefa:detalheTarefaTabView:dtblInteressadosPessoaFisica_data")
            drv.execute_script("arguments[0].scrollIntoView();", campo)
            ActionChains(drv).send_keys(Keys.PAGE_UP).perform()
            time.sleep(1)
            campo = campo.find_element(By.TAG_NAME, value="tr")
            texto = campo.find_elements(By.TAG_NAME, value="td")[0].text
            resultado['cpf'] = texto

        #Conta a quantidade de exigencias
        if 'quantexig' in atributos:
            quant = self.contar_exigencias()
            resultado['quantexig'] = quant
        
        #Coleta o NIT
        if 'nit' in atributos:
            self.irpara_iniciotela()
            res = True
            while res:
                ##clica em CNIS
                self.irpara_guia('Cnis')
                self.aguardar_telaprocessamento()
                res, texto = self.obter_erro()
                if res:
                    print(f'Erro: {texto}. Tentando novamente...')
                    self.irpara_guia('Subtarefas')
                    self.aguardar_telaprocessamento()
    
            ##pega o nit
            campo = drv.find_element(By.ID, value="formDetalharTarefa:detalheTarefaTabView:detalheCnisTarefaTabView:pnlDadosBasicosLeitura_content")
            campo = campo.find_element(By.CLASS_NAME, value="panel-default")
            campo = campo.find_element(By.CLASS_NAME, value="panel-body")
            campo = campo.find_elements(By.CLASS_NAME, value="row")[0]
            campo = campo.find_element(By.CLASS_NAME, value="col-lg-12")
            campo = campo.find_element(By.CLASS_NAME, value="col-md-2")
            texto = campo.find_element(By.TAG_NAME, value="p").text
            resultado['nit'] = texto

        #Coleta as subtarefas
        if 'subtarefa' in atributos:
            self.irpara_iniciotela()
            
            #Clica em Subtarefa
            self.irpara_guia('Subtarefas')

            #coleta todas as subtarefas
            subs = self.coletar_subtarefas(tarefa, nome_servico, 'pm' in atributos)
            if len(subs) > 0:
                resultado['subtarefa'] = subs[len(subs)-1][0]
                resultado['pmrealizada'] = subs[len(subs)-1][1]
            else:
                resultado['pmrealizada'] = False

        if 'quantsub' in atributos:
            quant = self.contar_subtarefas()
            resultado['quantsub'] = quant

        #Coleta o código do OLM
        if 'olm' in atributos:
            self.irpara_iniciotela()

            #Clica em Histórico
            self.irpara_guia('Historico')

            #Coleta a informação de Transferência
            campo = drv.find_element(By.ID, value="formDetalharTarefa:detalheTarefaTabView:dtblHistorico_data")
            linhas = campo.find_elements(By.TAG_NAME, value="tr")
            detalhes = []
            for linha in linhas:
                texto = linha.text
                if texto.startswith('Transferiu da unidade'):
                    detalhes.append(texto)
            palavras = detalhes[-1].split()
            resultado['olm'] = palavras[3]

            #quant_linhas = len(campo.find_elements(By.TAG_NAME, value="tr"))
            #campo = drv.find_element(By.ID, value=f'formDetalharTarefa:detalheTarefaTabView:dtblHistorico:{quant_linhas-1}:dtblDetalheHistorico_data')
            #texto = campo.find_element(By.TAG_NAME, value='td').text
            #palavras = texto.split()
            #resultado['olm'] = palavras[3]            
            
        return resultado
    
    def coletar_nomeservico(self) -> str:
        """Coleta o nome do serviço da tarefa aberta."""
        drv = self.driver

        elemento = drv.find_element(By.CLASS_NAME, 'title-content')
        #elemento = elemento.find_element(By.CLASS_NAME, 'row')
        texto = elemento.find_element(By.TAG_NAME, 'p').text.strip()
        return texto

    def coletar_subtarefas(self, tarefa: str, nome_servico: str, gerarpdf: bool) -> list[tuple[str, bool]]:
        """Coleta no. da subtarefa, seu status e gera relatorio da PM."""
        TEXTO_CONCLUIDA = 'Concluída'
        numero_sub = ''
        subconcluida = False
        resultado = []
                
        self.tarefa = tarefa
        self.irpara_finaltela()
        campo = self.driver.find_element(By.ID, value="formDetalharTarefa:detalheTarefaTabView:dtblSubtarefasPericias_data")
        lista_sub = campo.find_elements(By.TAG_NAME, "tr")
        item_id = 0
        for item_sub in lista_sub:
            campos = item_sub.find_elements(By.TAG_NAME, "td")            
            if len(campos[0].find_elements(By.TAG_NAME, "span")) > 0:
                if campos[1].find_element(By.TAG_NAME, "span").text == nome_servico:
                    numero_sub = campos[0].find_element(By.TAG_NAME, "span").text
                    subconcluida = campos[2].find_element(By.TAG_NAME, "span").text == TEXTO_CONCLUIDA
                    resultado.append((numero_sub, subconcluida))
                    if subconcluida and gerarpdf:
                        botao = campos[3].find_element(By.ID, f'formDetalharTarefa:detalheTarefaTabView:dtblSubtarefasPericias:{item_id}:cmdLinkLaudoPericia')
                        botao.click()
                        self.aguardar_telaprocessamento()                        
                        arquivo_gerado = path.join(self.dir_downloads, f'relatorio_tarefa_pericia_{numero_sub}.pdf')
                        arquivo_novo = path.join(self.dir_downloads, f'{self.tarefa} - RelatorioPM.pdf')
                        aguardar_geracao_arquivo(arquivo_gerado, arquivo_novo)
            item_id = item_id + 1
        self.irpara_iniciotela()
        return resultado

    def concluir_tarefa(self, numero: str, texto: str) -> dict:
        """Conclui a tarefa especificada no GET."""
        drv = self.driver
        
        resultado = dict()
        resultado['houve_conclusao'] = False
        resultado['msg'] = ''

        #Espera o formulário
        WebDriverWait(drv, 20).until(EC.presence_of_element_located((By.ID, "formMudancaSituacaoTarefaDialog_concluir")))

        #Informa NB/NCTC
        elementos = drv.find_elements(By.ID, value="formMudancaSituacaoTarefaDialog_concluir:camposModelo:0:campoAdicionalModelo")
        if len(elementos) > 0:
            campo = elementos[0]
            campo.send_keys(numero)
    
        ##Insere texto
        try:
            WebDriverWait(drv, 20).until(EC.visibility_of_element_located((By.ID, "formMudancaSituacaoTarefaDialog_concluir:justificativaMudancaSituacaoTarefa_concluir_editor")))
            campo = drv.find_element(By.ID, value="formMudancaSituacaoTarefaDialog_concluir:justificativaMudancaSituacaoTarefa_concluir_editor")
            campo.click()
        except:
            pass
        campo = drv.find_elements(By.CLASS_NAME, value="ql-editor")[1]    
        campo.click()
        campo.send_keys(Keys.CONTROL, 'A')
        campo.send_keys(Keys.DELETE)    
        campo.send_keys(texto)
    
        ##Clica no botão Concluir
        botao = drv.find_element(By.ID, value="formMudancaSituacaoTarefaDialog_concluir:btnConcluir")
        botao.click()
        time.sleep(2)
        dlg = drv.find_element(By.ID, 'formMudancaSituacaoTarefaDialog_concluir')
        if len(dlg.find_elements(By.CLASS_NAME, 'ui-messages-error-summary')) > 0:
            msg_erro = dlg.find_element(By.CLASS_NAME, 'ui-messages-error-summary').text
            resultado['msg'] = msg_erro
            dlg.find_element(By.ID, 'formMudancaSituacaoTarefaDialog_concluir:j_idt1789').click
        else:
            resultado['houve_conclusao'] = True
    
        ##Aguarda pela msg Conclusão da tarefa efetuado com sucesso
        self.aguardar_telaprocessamento()
        WebDriverWait(drv, 20).until(EC.visibility_of_element_located((By.CLASS_NAME, "ui-messages-info")))
        time.sleep(1)
        return resultado
    
    def contar_exigencias(self) -> int:
        """Conta quantas exigências foram feitas na tarefa."""
        TEXTO_EXIGENCIA = "Despacho inserido ao mudar status para exigência."
        drv = self.driver
        cont = 0
        
        campo = drv.find_element(By.ID, value="collapse-comentario")
        campos = campo.find_elements(By.XPATH, value="./child::*")
        for c in campos:
            if c.get_attribute("class") == "panel-body well":
                h8 = c.find_elements(By.TAG_NAME, value="h8")
                secao = h8[1].find_elements(By.TAG_NAME, value="div")
                texto = secao[5].text
                if texto == TEXTO_EXIGENCIA:
                    cont += 1
        return cont

    def contar_subtarefas(self) -> int:
        """Conta quantas subtarefas a tarefa possui."""
        cont = 0
        tipos = ['Manuais_data', 'Pericias_data']
        for tipo in tipos:
            tabela = self.driver.find_element(By.ID, value=f'formDetalharTarefa:detalheTarefaTabView:dtblSubtarefas{tipo}')
            linha = tabela.find_element(By.TAG_NAME, "tr")
            linhas = tabela.find_elements(By.TAG_NAME, "tr")
            classes = linha.get_attribute('class').split()
            if 'ui-datatable-empty-message' in classes:
                continue
            else:
                cont += len(linhas)
        return cont

    def definir_exigencia(self, conteudo) -> bool:
        """Registra uma exigência na tarefa."""             
        drv = self.driver
        
        campo = drv.find_element(By.ID, value="formTarefas:gridTarefa_data")
        campo = campo.find_element(By.TAG_NAME, value="tr")
        campo = campo.find_elements(By.TAG_NAME, value="td")[9]
        texto = campo.find_element(By.TAG_NAME, value="span").text
        if texto != "Pendente":
            return False
        
        #Clica em atribuir exigencia
        botao = drv.find_element(By.ID, value="formTarefas:gridTarefa:0:lista_cumprimento_de_exigencia")
        botao.click()
        self.aguardar_telaprocessamento()
        
        ##Aguarda pelo form Atribuir Exigencia
        WebDriverWait(drv, 20).until(EC.element_to_be_clickable((By.ID, 'formMudancaSituacaoTarefaDialog_atribuirExigencia:btnCumprimentoDeExigencia')))
        time.sleep(1)
        
        ##Insere texto
        campo = drv.find_element(By.ID, value="formMudancaSituacaoTarefaDialog_atribuirExigencia:justificativaMudancaSituacaoTarefa_atribuirExigencia")       
        campo = campo.find_element(By.CLASS_NAME, value="ql-editor")
        campo.click()
        campo.send_keys(Keys.CONTROL, 'A')
        campo.send_keys(Keys.DELETE)    
        campo.send_keys(conteudo)  
        
        ##Clica no botão Colocar em exig.
        botao = drv.find_element(By.ID, value="formMudancaSituacaoTarefaDialog_atribuirExigencia:btnCumprimentoDeExigencia")
        botao.click()
    
        ##Aguarda pela msg Exigência atribuída da tarefa efetuado com sucesso
        self.aguardar_telaprocessamento()    
        WebDriverWait(drv, 20).until(EC.visibility_of_element_located((By.CLASS_NAME, "ui-messages-info")))
        time.sleep(1)
        
        return True
    
    def fechar_tarefa(self) -> None:
        """Fecha a tarefa no GET e volta para página de pesquisa."""
        drv = self.driver
        
        #Clica em Voltar
        botao = drv.find_element(By.ID, value="formDetalharTarefa:detalhe_voltar")
        botao.click()
        self.aguardar_telaprocessamento()
    
        ##Aguarda pelo campo de Pesquisa de Protocolo
        WebDriverWait(drv, 20).until(EC.element_to_be_clickable((By.ID, "formTarefas:btnAtualizarListaTarefas")))
        time.sleep(1)
        
        self.tarefa = ""

    def possui_anexos(self) -> bool:
        drv = self.driver

        #Clica em Anexos
        self.irpara_guia('Anexos')
        tem_tabela = len(campo := drv.find_elements(By.ID, 'formDetalharTarefa:detalheTarefaTabView:dtbltodosAnexos_data')) > 0
        if tem_tabela:
            tem_linha_unica = len(campo := campo[0].find_elements(By.TAG_NAME, 'tr')) == 1
            if tem_linha_unica:
                tem_cel_unica = len(campo := campo[0].find_elements(By.TAG_NAME, 'td')) == 1
                if tem_cel_unica:
                    if campo[0].text == 'Nenhum registro encontrado.':
                        return False
        return True

    def gerar_subtarefa(self, servico: str, tipo_sub: str, dados) -> str:
        """Gera uma subtarefa no GET e retorna seu número."""
        drv = self.driver
        
        #Clica em Subtarefa
        atalho = drv.find_element(By.XPATH, "//a[@href='#formDetalharTarefa:detalheTarefaTabView:tabSubtarefas']")
        atalho.click()
        self.aguardar_telaprocessamento()
        
        #Clica no botao Nova Subtarefa
        botao = drv.find_element(By.ID, value="formDetalharTarefa:detalheTarefaTabView:btnIncluirServicoSubTarefa")
        botao.click()
        WebDriverWait(drv, 20).until(EC.element_to_be_clickable((By.ID, "formDetalharTarefa:detalheTarefaTabView:servicoBusca_input")))
        time.sleep(2)
        
        #Escolhe o Serviço
        campo = drv.find_element(By.ID, value="formDetalharTarefa:detalheTarefaTabView:servicoBusca_input")
        campo.click()
        campo.send_keys(servico)
        #time.sleep(2)
        self.aguardar_telaprocessamento()
        campo = drv.find_element(By.ID, value="formDetalharTarefa:detalheTarefaTabView:servicoBusca_panel")
        #time.sleep(2)
        self.aguardar_telaprocessamento()
        WebDriverWait(campo, self.tempo_espera).until(EC.visibility_of_element_located((By.CLASS_NAME, 'ui-autocomplete-row')))
        linhatabela = campo.find_element(By.CLASS_NAME, value='ui-autocomplete-row')
        linhatabela.click()
        
        #Clica no botao Solicitar Perícia
        self.aguardar_telaprocessamento()
        #self.aguardar_visibilidade_elemento('id:formDetalharTarefa:detalheTarefaTabView:btnSolicitarPericia')
        drv.find_element(By.ID, value="formDetalharTarefa:detalheTarefaTabView:btnSolicitarPericia").click()
        WebDriverWait(drv, self.tempo_espera).until(EC.element_to_be_clickable((By.ID, "formNovaTarefa:gridPanelNovaTarefa")))
        
        #Coleta o código usado na identificação dos campos adicionais
        cont = 0
        numero_id = ''
        campo = drv.find_element(By.ID, value="formNovaTarefa:gridPanelCamposAdicionais")
        campo = campo.find_element(By.CLASS_NAME, value="dtp-required")
        if self.criarsub_modolinha:
            campo = campo.find_element(By.CLASS_NAME, value="row")
            campo = campo.find_elements(By.XPATH, value="./child::*")
            campo = campo[0].find_element(By.XPATH, value="./child::*")
        else:
            campo = campo.find_element(By.TAG_NAME, value="label")
        cid = campo.get_attribute("id")
        for c in cid:
            if c.isdigit():
                numero_id += c
            if c == ':':
                cont += 1
            if cont == 2:
                break
        
        #Preenche os campos adicionais da subtarefa
        self.preencher_camposadic(numero_id, tipo_sub, dados)
       
        #Clica no botão Salvar
        self.aguardar_telaprocessamento()
        campo  = drv.find_element(By.ID, value="formNovaTarefa:btCriarTarefa")
        drv.execute_script("arguments[0].scrollIntoView();", campo)
        ActionChains(drv).send_keys(Keys.END).perform()
        campo.click()
        
        #Espera pela cx diálogo sobre ausência de responsáveis e anexos.
        WebDriverWait(drv, 20).until(EC.element_to_be_clickable((By.ID, "formNovaTarefa:simIncluirTarefaSemResponsavelAnexo")))
        
        #Clica em Sim
        campo  = drv.find_element(By.ID, value="formNovaTarefa:simIncluirTarefaSemResponsavelAnexo")
        campo.click()
        
        #espera pela tela de bloqueio
        self.aguardar_telaprocessamento()
        
        #Coleta o número da subtarefa
        res, texto = self.obter_mensagem()
        if res:
            numsub = [int(s) for s in texto.split() if s.isdigit()]
        else:
            print(f'Erro: {texto}')
            numsub = [0]
            self.irpara_finaltela()
            self.clicar_botao('formNovaTarefa:btCancelarTarefa')
            self.espera.until(EC.visibility_of_element_located((By.ID, 'formTarefas:gridTarefa:0:cmdLinkDetalharTarefa')))
        
        return numsub[0]
    
    def irpara_guia(self, nome: str) -> None:
        """Clica na guia do GET especificada."""
        drv = self.driver

        elem = drv.find_element(By.XPATH, f"//a[@href='#formDetalharTarefa:detalheTarefaTabView:tab{nome}']") 
        elem.click()
        self.aguardar_telaprocessamento()

    def obter_erro(self):
        drv = self.driver

        time.sleep(2)
        if len(campo := drv.find_elements(By.CLASS_NAME, value='ui-messages-error-summary')) > 0:
            texto = campo[0].text
            resultado = True
        else:
            texto = ''
            resultado = False
        return resultado, texto

    def obter_mensagem(self):
        drv = self.driver

        WebDriverWait(drv, 20).until(EC.visibility_of_element_located((By.ID, "mMensagens")))
        time.sleep(1)
        if len(campo := drv.find_elements(By.CLASS_NAME, value='ui-messages-info-summary')) > 0:
            texto = campo[0].text
            resultado = True
        elif len(campo := drv.find_elements(By.CLASS_NAME, value='ui-messages-warn-detail')) > 0:
            texto = campo[0].text
            resultado = False
        return resultado, texto

    def pesquisar_tarefa(self, tarefa: str) -> None:
        """Pesquisa uma tarefa por protocolo."""
        drv = self.driver
        
        #Digitar a tarefa
        campo = drv.find_element(By.ID, value="formTarefas:filtroProtocolo")
        campo.clear()
        campo.send_keys(tarefa)
    
        #Clicar em Pesquisar
        botao = drv.find_element(By.ID, value="formTarefas:btnBuscar")
        botao.click()
        self.aguardar_telaprocessamento()
        
        self.tarefa = tarefa
        try:
            WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.ID, "formTarefas:gridTarefa:0:cmdLinkDetalharTarefa")))
        except TimeoutException:
            return False
        return True
    
    def preencher_camposadic(self, num_id: str, tipo_sub: str, dados: dict) -> None:
        """Preeche os campos adicionais da subtarefa."""
        drv = self.driver

        if tipo_sub == 'pm_aa':
            #>Escolhe a forma de filiação ao RGPS
            campo = drv.find_element(By.ID, value=f'formNovaTarefa:j_idt{num_id}:0:campoAdicional_cb_relacionado_')
            campo.click()
            time.sleep(1)
            campo  = drv.find_element(By.ID, value=f'formNovaTarefa:j_idt{num_id}:0:campoAdicional_cb_relacionado__7')
            campo.click()
            time.sleep(1)
        elif tipo_sub == 'pm_psm':
            #>NB
            campo = drv.find_element(By.ID, value=f'formNovaTarefa:j_idt{num_id}:0:campoAdicional')
            campo.click()
            campo.send_keys(dados['nb'])
        
            #>NR
            campo = drv.find_element(By.ID, value=f'formNovaTarefa:j_idt{num_id}:1:campoAdicional')
            campo.click()
            campo.send_keys("123456")
        
            #>CPF
            campo = drv.find_element(By.ID, value=f'formNovaTarefa:j_idt{num_id}:2:campoAdicional')
            campo.click()
            campo.send_keys(dados['cpf'])

    def sobrestar(self) -> None:
        """Gera uma subtarefa de sobrestamento."""
        drv = self.driver
        numero = self .gerar_subtarefa("Processo Sobrestado", False)
        
        #Preenche os campos (TODO: REVER ESSE CODIGO)
        #->Motivo
        campo = drv.find_element(By.ID, value=f'formNovaTarefa:j_idt{numero}:0:campoAdicional_cb_relacionado_')
        campo.click()
        item = drv.find_element(By.ID, value=f'formNovaTarefa:j_idt{numero}:0:campoAdicional_cb_relacionado__1')
        if item.text == 'Adequação ACP':
            item.click()
        else:
            print("Erro ao selecionar motivo de sobrestamento")
            return ""
        time.sleep(1)
        
        # Clica em Salvar
        campo  = drv.find_element(By.ID, value="formNovaTarefa:btCriarTarefa")
        drv.execute_script("arguments[0].scrollIntoView();", campo)        
        ActionChains(drv).send_keys(Keys.END).perform()
        campo.click()
        WebDriverWait(drv, 20).until(EC.element_to_be_clickable((By.ID, "formNovaTarefa:simIncluirTarefaSemResponsavelAnexo")))
        
        #Clica em Sim
        campo  = drv.find_element(By.ID, value="formNovaTarefa:simIncluirTarefaSemResponsavelAnexo")
        campo.click()
        self.aguardar_telaprocessamento()
        
        #Coleta número da subtarefa
        WebDriverWait(drv, 20).until(EC.visibility_of_element_located((By.ID, "mMensagens")))
        time.sleep(1)
        texto = drv.find_element(By.CLASS_NAME, value="ui-messages-info-summary").text
        numsub = [int(s) for s in texto.split() if s.isdigit()]
        return numsub[0] 