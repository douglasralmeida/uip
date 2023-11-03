## Codificado por Douglas Rodrigues de Almeida.
## Agosto de 2023
"""Processador para requerimento de benefícios"""

import pandas as pd
from .processador import Processador
from anexacao import Anexacao
from arquivo import ArquivoPrismaSaida
from atividade import AtividadeBase, AtividadeColetaDB
from arquivo import ArquivoPrismaEntrada
from basedados import BaseDados, TipoBooleano, TipoData, TipoHora, TipoInteiro, TipoTexto
from filtro import Filtro
from impedimento import Impedimento
from listagem import Listagem
from lote import Lote
from os import path
from tarefa import TarefaBeneficio
from variaveis import Variaveis

RES_SUBTAREFA_ERRO = 0

RES_SUBTAREFA_GERADA = 1

RES_SUBTAREFA_COLETADA = 2

datas_padrao = ['data_subtarefa', 'dib_inacumulavel']

class ProcessadorBeneficio(Processador):
    """Classe o processador de benefícios do UIP."""
    def __init__(self, base_dados: BaseDados) -> None:
        super().__init__(base_dados)

        #Dados a serem coletados pela atividade Coleta de Dados Básicos.
        self.dadosparacoletar = []

        #Colunas e tipos de dados 'Data' padrão para todas filas.
        self.base_dados.definir_colunas(datas_padrao)

        self.especies_acumulaveis: list[str] = []

        self.id_subtarefa = ""

        self.lista: list[TarefaBeneficio] = []

        self.nome_servicopm = ''

        #Tag para benefício
        self.tags.append('ben')

        self.atividades: dict[str, AtividadeBase] = {}
        self.atividades['coletadb'] = AtividadeColetaDB(self.base_dados)

    def __str__(self) -> str:
        """"""
        return super().__str__()
    
    ###===  AGENDAMENTO DE PERÍCIA MÉDICA ===###

    def comando_agendar_pm(self, subcomando: str, lista: list[str]) -> None:
        """Executa o programa 'Agendar PM' do processador."""
        if len(lista) > 0 and lista[0] == 'ulp':
            self.processar_agendar_pm_lote()
        else:
            self.processar_agendar_pm_base()

    def processar_agendar_pm_base(self) -> None:
        cont = 0
        self.pre_processar('AGENDAR PM')
        for t in self.lista:
            agendamento = t.obter_agendamento_pm()
            subtarefa = t.obter_subtarefa()
            if not subtarefa.tem or agendamento.tem_agendamento().e_verdadeiro or t.tem_impedimento().e_verdadeiro or t.esta_concluida().e_verdadeiro:
                continue
            if self.agendar_pm(t):
                cont += 1
        self.pos_processar(cont)

    def processar_agendar_pm_lote(self) -> None:
        cont = 0
        self.pre_processar('AGENDAR PM')
        print("Usando lista personalizada.")

        for item in self.obter_listapersonalizada():
            if (idx := self.base_dados.pesquisar_indice(item)) == None:
                print(f"Erro: Tarefa {item} não foi encontrada na fila atual.\n")
                continue
            t = TarefaBeneficio(self.base_dados, idx)
            if self.agendar_pm(t):
                cont += 1
        self.pos_processar(cont)
    
    def agendar_pm(self, tarefa: TarefaBeneficio) -> bool:
        """Agenda uma PM no PMF Agenda."""
        buffer_linha = ''
        cont = 0
        protocolo = ''

        if self.pmfagenda is None:
            return False

        protocolo = str(tarefa.obter_protocolo())
        agendamento = tarefa.obter_agendamento_pm()
        subtarefa = tarefa.obter_subtarefa()
        buffer_linha = f'Tarefa {protocolo}...'
        print(buffer_linha, end='\r')
        cpf = str(tarefa.obter_cpf())
        subtarefa = str(subtarefa.protocolo)
        olm = str(tarefa.obter_olm())
        dados_agenda = self.pmfagenda.agendar(protocolo, cpf, self.nome_servicopm, str(subtarefa), olm)
        agendamento.gravar_novo(TipoData(dados_agenda[0]), TipoHora(dados_agenda[1]), TipoTexto(dados_agenda[2]), TipoInteiro(dados_agenda[3]), TipoBooleano(False))
        anexacao = Anexacao(TipoBooleano(None), TipoBooleano(None))
        tarefa.alterar_agendamento_pm(agendamento)
        tarefa.alterar_anexacaopdf_pm(anexacao)
        print(f'{buffer_linha}Dia {dados_agenda[0]} às {dados_agenda[1]}.')
        self.salvar_emarquivo()

        return True
    
    #== ANEXAÇÃO DE PDF DA AGENDA PM ==#
    def comando_anexar_pdfpm(self, subcomando: str, lista: list[str]) -> None:
        """Executa o programa 'Anexar PDF da PM' do processador."""
        self.pre_processar('ANEXAR PDF DA PM')
        if len(lista) > 0 and lista[0] == 'ulp':
            self.processar_anexarpdf_pm_lote()
        else:
            self.processar_anexarpdf_pm_base()

    def processar_anexarpdf_pm_base(self) -> None:
        cont = 0
        for t in self.lista:
            agendamento = t.obter_agendamento_pm()
            anexacao = t.obter_anexacaopdf_pm()
            if not agendamento.tem_agendamento().e_verdadeiro or anexacao.tem_anexo().e_verdadeiro or t.tem_impedimento().e_verdadeiro or t.esta_concluida().e_verdadeiro:
                continue
            if self.anexar_agendamentopm(t):
                cont += 1
        self.pos_processar(cont)

    def processar_anexarpdf_pm_lote(self) -> None:
        cont = 0
        print("Usando lista personalizada.")
        for item in self.obter_listapersonalizada():
            if (idx := self.base_dados.pesquisar_indice(item)) == None:
                print(f"Erro: Tarefa {item} não foi encontrada na fila atual.\n")
                continue
            t = TarefaBeneficio(self.base_dados, idx)
            if self.anexar_agendamentopm(t):
                cont += 1
        self.pos_processar(cont)

    def anexar_agendamentopm(self, tarefa: TarefaBeneficio) -> bool:
        """"""
        buffer_linha = ''
        cont = 0
        get = self.get
        protocolo = ''

        if get is None:
            return False
        resultado = False
        protocolo = str(tarefa.obter_protocolo())
        buffer_linha = f"Tarefa {protocolo}..."
        print(buffer_linha, end='\r')
        if get.pesquisar_tarefa(protocolo):

            #Verifica se tarefa está cancelada/concluída
            if self.processar_status(tarefa):
                print(buffer_linha + 'Tarefa cancelada/concluída. Anexação de PDF não foi processada.')
                cont += 1
                return False

            #Anexa o arquivo PDF para os demais casos
            get.abrir_tarefa()
            
            arquivo_pdf = f'{protocolo} - AgendaPM.pdf'
            caminho_pdf = path.join(Variaveis.obter_pasta_pdf(), arquivo_pdf)
            res_anexacao = get.adicionar_anexos([caminho_pdf])
            anexacao = tarefa.obter_anexacaopdf_pm()
            if len(res_anexacao) > 0 and res_anexacao[0]:
                buffer_linha += "PDF Anexado."
                anexacao.alterar_anexacao(TipoBooleano(True))
                anexacao.marcar_erro(TipoBooleano(None))
                resultado = True
            else:
                buffer_linha += "Erro ao anexar."
                anexacao.alterar_anexacao(TipoBooleano(None))
                anexacao.marcar_erro(TipoBooleano(True))
            tarefa.alterar_anexacaopdf_pm(anexacao)
            get.fechar_tarefa()
        else:
            buffer_linha += 'Erro: Tarefa não foi encontrada.'
            return False
        self.salvar_emarquivo()
        print(buffer_linha)
        return resultado
    
    #==
    
    def analisar_acumulaben(self) -> None:
        """Analisa a existência de benefícios inacumuláveis."""
        buffer_linha = ''
        cont = 0
        protocolo = ''
        lista_checarmanual: list[str] = []

        if self.cnis is None:
            return

        self.pre_processar('ANÁLISE SOBRE ACUMULAÇÃO DE BENEFÍCIOS')
        for t in self.lista:
            analise = t.obter_analise_benefinac()
            if analise.tem_analise or not t.tem_dadosbasicos().e_verdadeiro:
                continue
            protocolo = str(t.obter_protocolo())
            cpf = str(t.obter_cpf())
            buffer_linha = f"Tarefa {protocolo}..."
            print(buffer_linha, end='\r')
            if self.cnis.pesquisar_ben_ativos(protocolo, cpf, self.especies_acumulaveis
            ):
                buffer_linha += "Possui BEN inacumulável ativo."
                lista_checarmanual.append(protocolo)
            else:
                buffer_linha += "Não possui BEN inacumulável ativo."
                analise.marcar_naopossuiben()
                t.alterar_analise_benefinac(analise)
            print(buffer_linha)
            self.salvar_emarquivo()
            cont +=1            
        print("\nTarefas com suspeita de acumulação:")
        print("\n".join(lista_checarmanual))
        self.pos_processar(cont)

    ###===  CHECAR DE AGENDAMENTO DA PERÍCIA MÉDICA ===###
    def comando_checar_agendapm(self, subcomando: str, lista: list[str]) -> None:
        """Executa o programa 'Checar Agenda PM' do processador."""
        if len(lista) > 0 and lista[0] == 'ulp':
            self.processar_checar_agendapm_lote()
        else:
            self.processar_checar_agendapm_base()

    def processar_checar_agendapm_base(self) -> None:
        print("FUNÇÃO INATIVA. Use arquivo pra processamento em lote.")

    def processar_checar_agendapm_lote(self) -> None:
        cont = 0
        print("Usando lista personalizada.")
        for item in self.obter_listapersonalizada():
            if (idx := self.base_dados.pesquisar_indice(item)) == None:
                print(f"Erro: Tarefa {item} não foi encontrada na fila atual.\n")
                continue
            t = TarefaBeneficio(self.base_dados, idx)
            if self.checar_agendapm(t):
                cont += 1
        self.pos_processar(cont)

    def checar_agendapm(self, tarefa: TarefaBeneficio) -> bool:
        """Agenda uma PM no PMF Agenda."""
        buffer_linha = ''
        protocolo = ''

        if self.pmfagenda is None:
            return False

        protocolo = str(tarefa.obter_protocolo())
        agendamento = tarefa.obter_agendamento_pm()
        protocolo_agenda = str(agendamento.obter_protocolo())
        cpf = str(tarefa.obter_cpf())
        buffer_linha = f'Tarefa {protocolo}...'
        print(buffer_linha, end='\r')
        status = self.pmfagenda.checar_comparecimento(self.nome_servicopm, protocolo_agenda, protocolo, cpf)
        if status == '(não compareceu)':
            buffer_linha += "Não compareceu. Comprovante impresso."
        elif status == '':
            buffer_linha += "Info. comparecimento não disponível."
        elif status in ['Agendado', 'Agendado Impactado']:
            buffer_linha += "Reagendado."
        else:
            buffer_linha += "Compareceu."
            
        print(buffer_linha)
        return True

    ###=== ===###

    def cancelar_subtarefa(self) -> None:
        """Processa o cancelamento de subtarefas."""
        buffer_linha = ''
        cont = 0
        get = self.get
        texto_conclusao = 'Não houve comparecimento do titular do requerimento a perícia médica agendada.'

        if get is None:
            return

        self.pre_processar('CANCELAR SUBTAREFA')

        for t in self.lista:
            pericia = t.obter_periciamedica()
            subtarefa = t.obter_subtarefa()
            if pericia.realizada().e_verdadeiro or not pericia.cumprida().e_verdadeiro or subtarefa.cancelada().e_verdadeiro or t.tem_impedimento().e_verdadeiro or t.esta_concluida().e_verdadeiro:
                continue
            protocolo = str(t.obter_protocolo())
            buffer_linha = f'Tarefa {protocolo}...'
            print(buffer_linha, end='\r')
            if get.pesquisar_tarefa(protocolo):
                
                #Verifica se tarefa está cancelada/concluída
                if self.processar_status(t):
                    print(buffer_linha + 'Tarefa cancelada/concluída. Cancelamento de sub não foi processada.')
                    cont += 1
                    continue

                get.abrir_tarefa()
                get.abrir_guia('Subtarefas')
                get.irpara_finaltela()
                if get.cancelar_sub(str(subtarefa.obter_protocolo()), self.nome_subservico, texto_conclusao):
                    subtarefa.cancelar()
                    der = str(t.obter_der())
                    nit = str(t.obter_nit())
                    self.enviar_tarefa_habilitacao(protocolo, der, nit)
                    t.alterar_subtarefa(subtarefa)
                    print(buffer_linha + 'Subtarefa cancelada. Benefício enviado para habilitação.')
                    self.salvar_emarquivo()
                else:
                    print(buffer_linha + 'Erro ao cancelar subtarefa.')
                get.fechar_tarefa()
                cont += 1
            else:
                print(buffer_linha + 'Erro: Tarefa não encontrada.')
        self.pos_processar(cont)

    #== COLETA DE DADOS BASICOS ==#
    
    def coletar_dadosbasicos_base(self) -> None:
        cont = 0
        self.pre_processar('COLETA DE DADOS BÁSICOS')
        for t in self.lista:
            tem_db = t.tem_dadosbasicos().e_verdadeiro
            esta_concluida = t.esta_concluida().e_verdadeiro
            if tem_db or esta_concluida:
                continue
            if self.coletar_dados(t):
                cont += 1
        self.pos_processar(cont)

    def coletar_dadosbasicos_lote(self) -> None:
        cont = 0
        self.pre_processar('COLETA DE DADOS BÁSICOS')
        print("Usando lista personalizada.")
        for item in self.obter_listapersonalizada():
            if (idx := self.base_dados.pesquisar_indice(item)) == None:
                print(f"Erro: Tarefa {item} não foi encontrada na fila atual.\n")
                continue
            t = TarefaBeneficio(self.base_dados, idx)
            if self.coletar_dados(t):
                cont += 1
        self.pos_processar(cont)

    def coletar_dados(self, tarefa: TarefaBeneficio) -> bool:
        """Coleta os dados básicos da tarefa de benefícios no GET."""
        buffer_linha = ''
        get = self.get

        if get is None:
            return False
        protocolo = str(tarefa.obter_protocolo())
        buffer_linha = f"Tarefa {protocolo}..."
        print(buffer_linha, end='\r')
        if get.pesquisar_tarefa(protocolo):
            if self.coletar_status(tarefa):
                buffer_linha += "Concluida/Cancelada. Coleta não processada."
                print(buffer_linha)
                return False
            get.abrir_tarefa()
            dados_coletados = get.coletar_dados(protocolo, self.nome_subservico, self.dadosparacoletar)
            if 'der' in self.dadosparacoletar:
                tarefa.alterar_der(TipoData(dados_coletados['der']))
            if 'beneficio' in self.dadosparacoletar:
                tarefa.alterar_beneficio(TipoTexto(dados_coletados['nb']))
            if 'cpf' in self.dadosparacoletar:
                tarefa.alterar_cpf(TipoTexto(dados_coletados['cpf']))
            if 'nit' in self.dadosparacoletar:
                tarefa.alterar_nit(TipoTexto(dados_coletados['nit']))
            if 'quantexig' in self.dadosparacoletar:
                if dados_coletados['quantexig'] > 0:
                    tarefa.marcar_japossui_exigencia()
            if 'quantsub' in self.dadosparacoletar:
                if dados_coletados['quantsub'] > 0:
                    tarefa.marcar_japossui_subtarefa()
            if 'subtarefa' in self.dadosparacoletar:
                if 'subtarefa' in dados_coletados:
                    self.registrar_subgerada(tarefa, dados_coletados['subtarefa'])
            if 'olm' in self.dadosparacoletar:
                if dados_coletados['olm']:
                    tarefa.alterar_olm(TipoTexto(dados_coletados['olm']))
            if 'pm' in self.dadosparacoletar:
                if dados_coletados['pmrealizada']:
                    self.registrar_subgerada(tarefa, dados_coletados['subtarefa'])
                    resultado = self.processar_relatorio_pm(protocolo)
                    self.registrar_pmfoi_realizada(resultado, tarefa)
            if 'esta_acamado' in self.dadosparacoletar:
                tarefa.alterar_esta_acamado(dados_coletados['esta_acamado'])
            tarefa.marcar_tem_dadosbasicos()
            buffer_linha += "Dados coletados."
            print(buffer_linha)
            get.fechar_tarefa()
            self.salvar_emarquivo()
        else:
            buffer_linha += "Erro: Tarefa não foi encontrada."
            print(buffer_linha)
            return False
        return True
    
    #== COLETAR DIB ==#
    def coletar_dadosbeneficio_base(self) -> None:
        cont = 0
        self.pre_processar('COLETA DE DADOS DO BENEFICIO')
        for t in self.lista:
            pass
            #tem_db = t.tem_dadosbasicos().e_verdadeiro
            #esta_concluida = t.esta_concluida().e_verdadeiro
            #if tem_db or esta_concluida:
            #    continue
            #if self.coletar_dados(t):
            #    cont += 1
        self.pos_processar(cont)

    def coletar_dadosbeneficio_lote(self) -> None:
        cont = 0
        self.pre_processar('COLETA DE DADOS DO BENEFICIO')
        print("Usando lista personalizada.")
        for item in self.obter_listapersonalizada():
            if (idx := self.base_dados.pesquisar_indice(item)) == None:
                print(f"Erro: Tarefa {item} não foi encontrada na fila atual.\n")
                continue
            t = TarefaBeneficio(self.base_dados, idx)
            if self.coletar_ben(t):
                cont += 1
        self.pos_processar(cont)

    def coletar_ben(self, tarefa: TarefaBeneficio) -> bool:
        """Coleta os dados básicos da tarefa de benefícios no GET."""
        buffer_linha = ''
        sibe = self.sibe

        if sibe is None:
            return False

        analise = tarefa.obter_analise_benefinac()
        protocolo = str(tarefa.obter_protocolo())
        buffer_linha = f'Tarefa {protocolo}...'
        print(buffer_linha, end='\r')
        if not analise.obter_beneficio().e_nulo:
            beneficio = str(analise.obter_beneficio())
            dados = sibe.coletar_dados_beneficio(beneficio)
            if dados['sucesso']:
                analise.alterar_dib(dados['dib'])
                tarefa.alterar_analise_benefinac(analise)
                self.salvar_emarquivo()
                buffer_linha += 'DIB coletada. Alterado.'
                print(buffer_linha)                
                return True
            else:
                buffer_linha += 'Não coletado.'
                print(buffer_linha)
        else:
                buffer_linha += 'Sem informação de NB.'
                print(buffer_linha)
        return False

    #== ENVIO HABILITACAO PRISMA ==#

    def enviar_habilitacao_lote(self) -> None:
        """Gera a lista de benefícios para habilitação no Prisma."""

        cont = 0
        protocolo = ''
        print("Usando lista personalizada.")

        for item in self.obter_listapersonalizada():
            if (idx := self.base_dados.pesquisar_indice(item)) == None:
                print(f"Erro: Tarefa {item} não foi encontrada na fila atual.\n")
                continue
            t = TarefaBeneficio(self.base_dados, idx)
            protocolo = str(t.obter_protocolo())
            print(f'Tarefa {protocolo}.')
            der = str(t.obter_der())
            nit = str(t.obter_nit())
            self.enviar_tarefa_habilitacao(protocolo, der, nit)
            cont += 1
        self.pos_processar(cont)

    def enviar_tarefa_habilitacao(self, protocolo: str, der: str, nit: str) -> None:
        """Envia dados da tarefa para habilitação do benefício no Prisma."""
        cabecalho = ['protocolo', 'nit', 'der']
        nomearquivo_entrada = path.join(Variaveis.obter_pasta_entrada(), 'tarefas_habilitar.txt')
        
        # Anota as tarefas no arquivo tarefas_habilitar
        arquivo_prisma = ArquivoPrismaEntrada(nomearquivo_entrada, cabecalho)
        arquivo_prisma.carregar()
        if arquivo_prisma.carregado:
            dados = [nit, der]
            arquivo_prisma.alterar_dados(protocolo, dados)
            arquivo_prisma.salvar()

    #== A ==

    def enviar_tarefa_lancarpm(self, protocolo: str, beneficio: str) -> None:
        """Envia dados da tarefa para lançamento de PM no Prisma."""
        cabecalho = ['protocolo', 'beneficio']
        nomearquivo_entrada = path.join(Variaveis.obter_pasta_entrada(), 'tarefas_lancarpm.txt')

        # Anota as tarefas no arquivo tarefas_lancarpm
        arquivo_prisma = ArquivoPrismaEntrada(nomearquivo_entrada, cabecalho)
        arquivo_prisma.carregar()
        if arquivo_prisma.carregado:
            arquivo_prisma.alterar_dados(protocolo, [beneficio])
            arquivo_prisma.salvar()

    #== INDEFERIMENTO ==#
    def enviar_indeferimento_lote(self) -> None:
        """a"""
        cont = 0
        protocolo = ''
        print("Usando lista personalizada.")
        for item in self.obter_listapersonalizada():
            if (idx := self.base_dados.pesquisar_indice(item)) == None:
                print(f"Erro: Tarefa {item} não foi encontrada na fila atual.\n")
                continue
            t = TarefaBeneficio(self.base_dados, idx)
            protocolo = str(t.obter_protocolo())
            beneficio = str(t.obter_beneficio())
            analise = t.obter_analise_benefinac()
            dib_anterior = str(analise.obter_dib())
            ben_anterior = str(analise.obter_beneficio())            
            resultado = str(t.obter_resultado())
            print(f'Tarefa {protocolo}.')
            self.enviar_tarefa_indeferir(protocolo, beneficio, resultado, dib_anterior, ben_anterior)
            cont += 1
        self.pos_processar(cont)

    def enviar_tarefa_indeferir(self, protocolo: str, beneficio: str, res: str, dib_ant: str, nb_ant: str) -> None:
        """Envia dados da tarefa para indeferimento do benefício no Prisma."""
        cabecalho = ['protocolo', 'beneficio', 'resultado']
        nomearquivo_entrada = path.join(Variaveis.obter_pasta_entrada(), 'tarefas_indeferir.txt')

        # Anota as tarefas no arquivo tarefas_indeferir
        arquivo_prisma = ArquivoPrismaEntrada(nomearquivo_entrada, cabecalho)
        arquivo_prisma.carregar()
        if arquivo_prisma.carregado:
            arquivo_prisma.alterar_dados(protocolo, [beneficio, res, dib_ant, nb_ant])
            arquivo_prisma.salvar()

    ###===  GERACAO DE EXIGENCIAS DE PM ===###

    def processar_gerarexigencia_pm_base(self) -> None:
        cont = 0
        for t in self.lista:
            anexacao = t.obter_anexacaopdf_pm()
            exigencia = t.obter_exigencia()
            if not anexacao.tem_anexo().e_verdadeiro or exigencia.tem_exigencia().e_verdadeiro or exigencia.esta_comerro().e_verdadeiro or t.tem_impedimento().e_verdadeiro or t.esta_concluida().e_verdadeiro:
                continue
            if self.gerarexigencia_pm(t):
                cont += 1
        self.pos_processar(cont)

    def processar_gerarexigencia_pm_lote(self) -> None:
        cont = 0
        print("Usando lista personalizada.")

        for item in self.obter_listapersonalizada():
            if (idx := self.base_dados.pesquisar_indice(item)) == None:
                print(f"Erro: Tarefa {item} não foi encontrada na fila atual.\n")
                continue
            t = TarefaBeneficio(self.base_dados, idx)
            if self.gerarexigencia_pm(t):
                cont += 1
        self.pos_processar(cont)

    def gerarexigencia_pm(self, tarefa: TarefaBeneficio) -> bool:
        """"""
        buffer_linha = ''
        get = self.get
        protocolo = ''

        if get is None:
            return False
        protocolo = str(tarefa.obter_protocolo())
        buffer_linha = f'Tarefa {protocolo}...'
        print(buffer_linha, end='\r')
        if get.pesquisar_tarefa(protocolo):

            #Verifica se tarefa está cancelada/concluída
            if self.processar_status(tarefa):
                print(buffer_linha + 'Tarefa cancelada/concluída. Exigência não foi gerada.')
                return True
            
            #Gera o conteúdo da exigência
            texto = self.obter_textoexigencia("agendamentoPM")
            if len(texto) == 0:
                print(buffer_linha + "Tipo de modelo de exigência não contrado.")
                return False
            agendamento = tarefa.obter_agendamento_pm()
            exigencia = tarefa.obter_exigencia()
            data = str(agendamento.obter_data()) + ' ÀS ' + str(agendamento.obter_hora())
            local = str(agendamento.obter_local())
            texto_formatado = texto.format(data, local)

            #Registra a exigência no GET
            if get.definir_exigencia(texto_formatado):
                exigencia.iniciar(None)
                print(buffer_linha + "Exigência processada.")
            else:
                print(buffer_linha + "Tarefa já está em exigência. Exigência não gerada.")
                exigencia.marcar_erro(TipoBooleano(True))

            #Salva no UIP a info de exigência gerada
            tarefa.alterar_exigencia(exigencia, True)
            self.salvar_emarquivo()
            return True
        else:
            print(buffer_linha + 'Erro. Tarefa não foi encontrada.')
            return False
        
    ###===  GERACAO DE SUBTAREFAS ===###

    def processar_gerarsubtarefa_base(self) -> None:
        cont = 0
        self.pre_processar('GERAR SUBTAREFA')
        for t in self.lista:

            #Não irá gerar subtarefa se:
            # >não passou pela fase de analise de benefício inacumulável
            # >tem benefício inacumulável ativo
            # >ja foi gerada a subtarefa
            # >houve erro durante a geração de subtarefa no processamento anterior
            # >tarefa tem impedimento
            analise = t.obter_analise_benefinac()
            subtarefa = t.obter_subtarefa()
            if not analise.tem_analise or analise.tem_benef_inacumulavel().e_verdadeiro or subtarefa.tem or subtarefa.tem_erro or t.tem_impedimento().e_verdadeiro:
                continue            
            if self.gerar_subtarefa(t):
                cont += 1
        self.pos_processar(cont)

    def processar_gerarsubtarefa_lote(self) -> None:
        cont = 0
        self.pre_processar('GERAR SUBTAREFA')
        print("Usando lista personalizada.")

        for item in self.obter_listapersonalizada():
            if (idx := self.base_dados.pesquisar_indice(item)) == None:
                print(f"Erro: Tarefa {item} não foi encontrada na fila atual.\n")
                continue
            t = TarefaBeneficio(self.base_dados, idx)
            if self.gerar_subtarefa(t):
                cont += 1
        self.pos_processar(cont)        
        
    def gerar_subtarefa(self, tarefa: TarefaBeneficio) -> bool:
        """Gera subtarefa nas tarefas pendentes de geração de subtarefa."""
        buffer_linha = ''
        necessario_fechartarefa = False
        get = self.get
        protocolo = ''

        if get is None:
            return False

        protocolo = str(tarefa.obter_protocolo())
        buffer_linha = f'Tarefa {protocolo}...'
        print(buffer_linha, end='\r')

        #Pesquisa a tarefa no GET
        if get.pesquisar_tarefa(protocolo):

            #Verifica se tarefa está cancelada/concluída
            if self.coletar_status(tarefa):
                print(buffer_linha + 'Concluída/Cancelada. Subtarefa não foi gerada.')
                return False

            #Abre a tarefa no GET
            get.abrir_tarefa()
            necessario_fechartarefa = True

            #Verifica já existe subtarefa gerada e a coleta
            subtarefa = tarefa.obter_subtarefa()
            numsub = get.coletar_subtarefa(self.nome_subservico)
            if numsub[0] != 0:
                subtarefa.alterar_msgerro(TipoTexto(None))
                subtarefa.alterar(TipoInteiro(numsub[0]), TipoBooleano(False), TipoBooleano(False), TipoData(None))
                subtarefa.alterar_coletada(TipoBooleano(True))
                print(buffer_linha + 'Subtarefa coletada.')
            else:
                #Cria a subtarefa
                res = get.gerar_subtarefa(self.nome_subservico, self.id_subtarefa, {})
                if res['sucesso']:
                    num_novasub = res['numerosub'][0]
                    subtarefa.alterar_msgerro(TipoTexto(None))
                    subtarefa.gerar_nova(TipoInteiro(num_novasub))
                    print(buffer_linha + 'Subtarefa gerada.')
                else:
                    #Erro na geração de sub. Registra.
                    subtarefa.alterar_msgerro(TipoTexto(res['mensagem']))
                    print(buffer_linha + 'Subtarefa não foi gerada.')
                    necessario_fechartarefa = False
            tarefa.alterar_subtarefa(subtarefa)
            if necessario_fechartarefa:
                get.fechar_tarefa()
            self.salvar_emarquivo()
            return True
        else:
            print(buffer_linha + 'Erro: Tarefa não foi encontrada.')
            return False

    def listar(self, listagem: Listagem, filtro: Filtro) -> tuple[int, str]:
        """Retorna uma lista de tarefas."""
        return self.base_dados.obter_lista(listagem, filtro)
    
    #Verifica se houve habilitações de NB no Prisma.
    #>Recebe a lista de NBs do Accuterm
    #>Processa o relatório de PM em PDF para TXT estruturado
    #>Marca as tarefas com NB habilitados para lançar PM
    #>Encaminha lista de NBs para lançar PM no Accuterm
    def receber_beneficios(self) -> None:
        buffer_linha = ''
        dib_anterior = ''
        cont = 0
        cont_enviarpm = 0
        cont_indef = 0
        lista_sucesso = []
        nb_anterior = ''
        
        self.pre_processar('ANALISAR HABILITAÇÃO DE BENEFÍCIO')
        nomearquivo_saida = path.join(Variaveis.obter_pasta_entrada(), 'ben_habilitados.txt')

        #Recebe a lista de NBs habilitados no Prisma
        arquivo_prisma = ArquivoPrismaSaida(nomearquivo_saida, ['protocolo', 'beneficio'])
        arquivo_prisma.carregar()
        if not arquivo_prisma.carregado:
            return
        for protocolo, dados in arquivo_prisma.dados.items():
            buffer_linha = f'Tarefa {protocolo}...'
            print(buffer_linha, end='\r')
            nb = dados[0].strip()            
            if len(nb) > 0:
                idx = self.base_dados.pesquisar_indice(protocolo)
                if idx is None:
                    print(buffer_linha + 'Tarefa não encontrada.')
                    continue
                t = TarefaBeneficio(self.base_dados, idx)
                buffer_linha += f'Habilitado com NB {nb}.'
                print(buffer_linha, end='\r')
                t.alterar_beneficio(TipoTexto(nb))
                res = str(t.obter_resultado())
                if res in ['b36Deferido', 'b94Deferido']:
                    self.enviar_tarefa_lancarpm(protocolo, nb)
                    print(buffer_linha + ' Enviada para lançamento da PM.')
                    cont_enviarpm += 1
                else:
                    if res in ['b36RecebeBenInac', 'b36RecebeAA']:
                        analise = t.obter_analise_benefinac()
                        dib_anterior = str(analise.obter_dib())
                        nb_anterior = str(analise.obter_beneficio())
                    self.enviar_tarefa_indeferir(protocolo, nb, res, dib_anterior, nb_anterior)
                    print(buffer_linha + ' Enviada para indeferimento.')
                    cont_indef += 1
                self.salvar_emarquivo()
                lista_sucesso.append(protocolo)
            cont += 1
        for p in lista_sucesso:
            arquivo_prisma.excluir_dados(p)
        if len(lista_sucesso) > 0:
            arquivo_prisma.salvar()

        #Envia a tarefa para lançamento de PM no Prisma
        print(f'\n{cont_enviarpm} tarefa(s) enviada(s) para lançamento de PM no Prisma.')
        print(f'{cont_indef} tarefa(s) enviada(s) para indeferimento no Prisma.')
        self.pos_processar(cont)

    def receber_despachos(self) -> None:
        """
        Verifica se houve despacho do BEN no Prisma.
        >Recebe a lista de tarefas do Accuterm
        >Marca as tarefas com BEN despachados
        """
        buffer_linha = ''
        cont = 0
        lista_sucesso = []
    
        self.pre_processar('ANALISAR DESPACHOS DE BENEFÍCIO')
        nomearquivo_saida = path.join(Variaveis.obter_pasta_entrada(), 'ben_despachados.txt')

        #Recebe a lista de tarefas com benefícios despachados
        arquivo_prisma = ArquivoPrismaSaida(nomearquivo_saida, ['protocolo', 'beneficiodespachado', 'tem_pdfresumoanexo', 'resultado', 'concluso'])
        arquivo_prisma.carregar()
        if not arquivo_prisma.carregado:
            return
        for protocolo, dados in arquivo_prisma.dados.items():
            buffer_linha = f'Tarefa {protocolo}...'
            print(buffer_linha, end='\r')
            nb_despachado = dados[0] == '1'
            pdf_resumo = dados[1] == '1'
            resultado_id = dados[2]
            if nb_despachado:
                idx = self.base_dados.pesquisar_indice(protocolo)
                if idx is None:
                    print(buffer_linha + 'Tarefa não encontrada.')
                    continue
                t = TarefaBeneficio(self.base_dados, idx)
                anexacao = t.obter_anexacao_analise()
                anexacao.alterar_anexacao(TipoBooleano(pdf_resumo))
                resultado = self.resultados.obter(resultado_id)
                if resultado is None:
                    print(buffer_linha + 'Erro: Resultado inválido.')
                    continue
                t.alterar_anexacao_analise(anexacao)
                t.alterar_resultado(resultado)
                t.despachar_beneficio()
                t.marcar_conclusa()
                self.salvar_emarquivo()
                lista_sucesso.append(protocolo)
                print(buffer_linha + f'Conclusa com resultado {resultado}.')
                cont += 1
        for p in lista_sucesso:
            arquivo_prisma.excluir_dados(p)
        if len(lista_sucesso) > 0:
            arquivo_prisma.salvar()
        self.pos_processar(cont)

    def receber_lancamentospm(self) -> None:
        """
        Verifica se houve lançamento de PM no Prisma.
        >Recebe a lista de tarefas do Accuterm
        >Marca as tarefas com PM lançada
        """
        buffer_linha = ''
        cont = 0
        lista_sucesso = []
        
        self.pre_processar('ANALISAR LANÇAMENTO DE PERÍCIA MÉDICA')
        nomearquivo_saida = path.join(Variaveis.obter_pasta_entrada(), 'pm_lancadas.txt')

        #Recebe a lista de tarefas com PM lançadas no Prisma
        arquivo_prisma = ArquivoPrismaSaida(nomearquivo_saida, ['protocolo', 'pericialancada'])
        arquivo_prisma.carregar()
        if not arquivo_prisma.carregado:
            return
        for protocolo, dados in arquivo_prisma.dados.items():
            buffer_linha = f'Tarefa {protocolo}...'
            print(buffer_linha, end='\r')
            pm_lancada = dados[0] == '1'
            if pm_lancada:
                idx = self.base_dados.pesquisar_indice(protocolo)
                if idx is None:
                    print(buffer_linha + 'Tarefa não encontrada.')
                    continue
                t = TarefaBeneficio(self.base_dados, idx)
                t.marcar_pm_lancada()
                self.salvar_emarquivo()
                print(buffer_linha + 'Tarefa processada.')
                cont += 1
        for p in lista_sucesso:
            arquivo_prisma.excluir_dados(p)
        if len(lista_sucesso) > 0:
            arquivo_prisma.salvar()
        self.pos_processar(cont)
    
    def registrar_subgerada(self, tarefa: TarefaBeneficio, num_subtarefa: str) -> None:
        """Registra que já foi gerada subtarefa"""
        subtarefa = tarefa.obter_subtarefa()
        subtarefa.alterar(TipoInteiro(num_subtarefa), TipoBooleano(False), TipoBooleano(False), TipoData(None))
        subtarefa.alterar_coletada(TipoBooleano(True))
        tarefa.alterar_subtarefa(subtarefa)

    def registrar_pmfoi_realizada(self, resultado: str, tarefa: TarefaBeneficio) -> None:
        """Registra que já foi realizada perícia."""
        tarefa.marcar_pm_realizada(resultado)
        if not tarefa.beneficio_habilitado():
            protocolo = str(tarefa.obter_protocolo())
            der = str(tarefa.obter_der())
            nit = str(tarefa.obter_nit())
            self.enviar_tarefa_habilitacao(protocolo, der, nit)

    #===========================================================================================================#
    
    def adicionar_tarefas(self, protocolos: list[str]) -> None:
        """Adiciona uma lista de tarefas a base de dados."""
        self.base_dados.adicionar_registros(protocolos)
        self.salvar_emarquivo()
        print("\nInclusões processadas com sucesso.\n")

    def contar_exigencias(self, protocolos: list[str]) -> None:
        """Conta a quantidade de exigências das tarefas especificadas."""
        cont = 0
        self.pre_processar('CONTAR EXIGÊNCIAS')
        for p in protocolos:
            if self.get.pesquisar_tarefa(p):
                self.get.abrir_tarefa()
                cont = self.get.contar_exigencias()
                self.get.fechar_tarefa()
                print(f'Tarefa {p:<12} {cont}')
            else:
                print(f'Tarefa {p:<12} não encontrada.')

    def contar_subtarefas(self, protocolos: list[str]) -> None:
        """Conta a quantidade de subtarefas das tarefas especificadas."""
        cont = 0
        self.pre_processar('CONTAR SUBTAREFAS')
        for p in protocolos:
            if self.get.pesquisar_tarefa(p):
                self.get.abrir_tarefa()
                self.get.abrir_guia('Subtarefas')
                cont = self.get.contar_subtarefas()
                self.get.fechar_tarefa()
                print(f'Tarefa {p:<12} {cont}')
            else:
                print(f'Tarefa {p:<12} não encontrada.')

    def editar_tarefas(self, atributo: str, valor: str, protocolos: list[str]) -> None:
        """Edita uma lista de tarefas"""
        if atributo == '?':
            print("Atributos passíveis de edição:")
            for atr, _ in self.atributos.items():
                print(atr)
            return
        if atributo in self.atributos.keys():
            if (tipo := self.atributos[atributo]['tipo']) == 'booleano':
                if valor in (valores := self.atributos[atributo]['valores_possiveis']).keys():
                    valor_dado = valores[valor]
                else:
                    print(f'Erro: O valor \'{valor}\' não foi reconhecido como um valor válido para o atributo \'{atributo}\'.\n')
                    return
            elif tipo == 'data':
                valor_dado = pd.to_datetime(valor, dayfirst=True, format='%d/%m/%Y').floor('D')
            elif tipo == 'texto':
                valor_dado = valor
            elif tipo == 'inteiro':
                if valor.isnumeric():
                    if atributo in ['beneficio', 'nb_inacumulavel']:
                        valor_dado = f'{valor[0:3]}.{valor[3:6]}.{valor[6:9]}-{valor[9]}'
                    else:
                        valor_dado = valor
                else:
                    print(f'Erro: O valor \'{valor}\' não foi reconhecido como um valor de número inteiro válido.\n')
                    return
            if valor_dado == '':
                valor_dado = pd.NA
            for protocolo in protocolos:
                if self.base_dados.alterar_atributos(protocolo, [self.atributos[atributo]['coluna']], [valor_dado], " "):
                    print(f'Tarefa {protocolo} foi alterda.')
                else:
                    print(f'Tarefa {protocolo} não foi alterda.')
            self.salvar_emarquivo()
            print('\n')
            return
        else:            
            print(f'Erro: O atributo \'{atributo}\' não foi reconhecido como um atributo editável válido.\n')
            return
    
    def obter_comandos(self) -> dict:
        """Retorna os comandos exclusivos do processador."""
        return self.comandos
    
    def obter_marcacoes(self):
        """Retorna as marcações disponíveis."""
        return self.marcacoes   
        
    def mostrar_agendapm(self, protocolo: str) -> None:
        """Exibe a agenda de PM se houver."""
        if (idx := self.base_dados.pesquisar_indice(protocolo)) == None:
            print(f'Erro: Tarefa {protocolo} não foi encontrada.\n')
            return
        t = TarefaBeneficio(self.base_dados, idx)
        if (ag := t.obter_agendamento()) is None:
            print('Tarefa sem agendamento registrado.\n')
        else:
            print(f'{self.nome_subservico}')
            print(f'Agendamento para: {ag}.')
            print(f'Endereço: {ag.local}\n')   

    def processar_conclusao(self) -> None:
        """Processa a conclusão de tarefas."""
        cont = 0
        protocolo = ''
        nomearquivo = ''
        texto = ''
        numero = 0

        self.pre_processar('CONCLUSÃO DE TAREFAS')
        for t in self.lista:
            if self.get.suspender_processamento:
                print('Processamento suspenso.\n')
                break
            if not t.obter_fase_concluso() or t.tem_impedimento():
                continue
            protocolo = str(t.obter_protocolo())
            print(f'Tarefa {protocolo}')
            if self.get.pesquisar_tarefa(protocolo):
                self.get.abrir_tarefa()
                if t.tem_arquivopdfresumo():
                    nomearquivo = path.join(Variaveis.obter_pasta_pdf(), f'{protocolo} - Analise.pdf')
                    resultados = self.adicionar_anexo([nomearquivo])
                    if resultados[0] == False:
                        self.get.fechar_tarefa()
                        print('Erro ao anexar arquivo.')
                        continue
                    self.get.irpara_iniciotela()
                    self.get.abrir_guia("Detalhes")
                self.get.irpara_finaltela()
                texto = self.obter_textodespacho(t.obter_idx(), t.obter_resultado())
                self.get.adicionar_despacho(texto)
                self.get.irpara_iniciotela()
                texto = self.obter_textoconclusao(t.obter_idx(), t.obter_resultado())
                numero = t.obter_beneficio()
                resultado = self.concluir_tarefa(numero, texto)
                if resultado['houve_conclusao']:
                    t.concluir_fase_conclusao()
                    self.salvar_emarquivo()
                    cont += 1
                else:
                    print(f'Erro ao concluir tarefa: {resultado["msg"]}')
                self.get.fechar_tarefa()
            else:
                print(f'Erro: Tarefa {protocolo} não foi encontrada.\n')
        self.pos_processar(cont)

    def processar_desimpedimento(self, lista: list[str]) -> None:
        """Marca cada tarefa da lista como desimpedida para conclusão."""
        cont = 0
        self.pre_processar('REMOVER IMPEDIMENTO')
        for protocolo in lista:
            if (idx := self.base_dados.pesquisar_indice(protocolo)) is None:
                print(f'Tarefa {protocolo} não foi encontrada.')
                continue
            t = Tarefa(self.base_dados, idx)
            t.remover_impedimento()
            print(f'Tarefa {protocolo} processada.')
            cont += 1
        self.salvar_emarquivo()
        self.pos_processar(cont)

    def processar_desistencia(self, lista: list[str]) -> None:
        """Registra a desistência do requerente nas tarefas especificadas."""
        cont = 0
        self.pre_processar('DESISTÊNCIA')
        for protocolo in lista:
            if (idx := self.base_dados.pesquisar_indice(protocolo)) is None:
                print(f'Tarefa {protocolo} não foi encontrada.')
                continue
            t = Tarefa(self.base_dados, idx)
            t.registrar_desistencia()
            print(f'Tarefa {protocolo} processada.')
            cont += 1
        self.salvar_emarquivo()
        self.pos_processar(cont)

    def processar_edicaoemlote(self, lista: list[str]) -> None:
        """Processa um script com edição de tarefas em lote."""
        atributos = lista[0].split(' ')
        num_itens = len(lista)
        for i in range(1, num_itens):
            valores = lista[i].split(' ')
            protocolo = valores[0].strip()
            self.base_dados.alterar_atributos(protocolo, atributos[1:], valores[1:], " ")
        self.salvar_emarquivo()
        print(f'{num_itens-1} tarefa(s) alterada(s) com sucesso.')

    def processar_impedimento(self, impedimento: Impedimento, lista: list[str]) -> None:
        """Marca cada tarefa da lista com o impedimento de conclusão especificado."""
        cont = 0
        self.pre_processar('ADICIONAR IMPEDIMENTO')
        for protocolo in lista:
            if (idx := self.base_dados.pesquisar_indice(protocolo)) is None:
                print(f'Tarefa {protocolo} não foi encontrada.')
                continue
            t = Tarefa(self.base_dados, idx)
            t.alterar_impedimento(impedimento)
            print(f'Tarefa {protocolo} processada.')
            cont += 1
        self.salvar_emarquivo()
        self.pos_processar(cont)

    def processar_lote(self, lote: Lote) -> None:
        """Processa um lote de edição de dados"""
        cont = 0
        self.pre_processar('PROCESSAR LOTE')
        print(f"Lote: {lote}")
        itens = lote.carregar_dados()
        atributos = lote.obter_atributos()[1:]
        for registro in itens:
            print(f"Tarefa {registro[0]}...")
            if self.base_dados.alterar_atributos2(registro[0].strip(), atributos, registro[1:]):
                cont += 1
        self.salvar_emarquivo()
        self.pos_processar(cont)

    def sobrestar(self, tarefa: str) -> None:
        """Gera uma tarefa de sobrestamento no GET."""
        numsub = self.get.sobrestar()
        tarefa.alterar_sub_sobrestado(numsub)