## Codificado por Douglas Rodrigues de Almeida.
## Fevereiro de 2024
"""Processador para Isenção de IR"""

import pandas as pd
from basedados import TipoBooleano, TipoTexto, TipoInteiro, TipoData
from conversor import Conversor
from tarefa import TarefaIsencaoIR
from os import path
from processador import Processador
from .utils import analisar_relatoriopm_iir
from variaveis import Variaveis

datas_padrao = ['der', 'vencim_exigencia', 'data_subtarefa', 'data_exigencia', 'data_pm', 'data_conclusao']

atributos = {'ms':           {'coluna': 'ms',
                              'tipo': 'booleano',
                              'valores_possiveis': {'sim': '1',
                                                    'nao': '0',
                                                    'vazio': ''
                               }
            },
            'primexig':      {'coluna': 'tem_prim_subtarefa',
                              'tipo': 'booleano',
                              'valores_possiveis': {'sim': '1',
                                                    'nao': '0',
                                                    'vazio': ''
                              }
            },
            'primsub':       {'coluna': 'tem_prim_exigencia',
                              'tipo': 'booleano',
                              'valores_possiveis': {'sim': '1',
                                                    'nao': '0',
                                                    'vazio': ''
                               }
            },
            'dataexig':      {'coluna': 'data_exigencia',
                              'tipo': 'data'
            },
            'vencexig':      {'coluna': 'vencim_exigencia',
                              'tipo': 'data'
            },
            'beneficio':    {'coluna': 'beneficio',
                             'tipo': 'inteiro'
                            }
            }

class ProcessadorIsencaoIR(Processador):
    """Classe para o processador de Isenção de IR."""
    def __init__(self, base_dados) -> None:
        super().__init__(base_dados)

        self.atributos = atributos

        #Colunas e tipos de dados 'Data' padrão para todas filas.
        self.base_dados.definir_colunas(datas_padrao)

        #Dados a serem coletados pela atividade Coleta de Dados Básicos.
        self.dadosparacoletar = ['quantexig', 'quantsub', 'subtarefa', 'temdoc']

        #TODO Checar depois
        self.criarsub_modolinha = False

        self.id = 'iri'
        
        self.id_subtarefa = 'pm_iir'

        #Lista de tarefas carregadas da base de dados.
        self.lista: list[TarefaIsencaoIR] = []

        self.nome_servico = 'Isenção de Imposto de Renda'

        self.nome_servicopm = ''
        
        self.nome_subservico = 'Análise para Isenção de Imposto de Renda'

        self.tipo_subservicopm = True

        #Tag para benefício
        self.tags.append('man')

    def __str__(self) -> str:
        resultado = super().__str__()

        resultado += f"Pendentes de coleta de dados: {self.obter_info('coletadb')} tarefa(s).\n"
        resultado += f"Pendentes de análise de documentação: {self.obter_info('iir_analisedoc')} tarefa(s).\n"

        resultado += f"Pendentes de abertura de exigência de documentação: {self.obter_info('iir_abrirexig')} tarefa(s).\n"
        resultado += f"Pendentes de cumprimento de exigência: {self.obter_info('iir_aguardarexig')} tarefa(s).\n"
        resultado += f"Com exigencia vencida: {self.obter_info('iir_exigvencida')} tarefa(s).\n"

        resultado += f"Pendentes de geração de subtarefa: {self.obter_info('iir_geracaosub')} tarefa(s).\n"
        resultado += f"Com erro na geração de subtarefa: {self.obter_info('iir_subcomerro')} tarefa(s).\n"

        resultado += f"Pendentes de análise da PMF: {self.obter_info('iir_analisepm')} tarefa(s).\n"
        #resultado += f"Pendentes de abertura de exigência feita pela PMF: {self.obter_info('sub_aguardapm')} tarefa(s).\n"
        #resultado += f"Pendentes de atualização do benefício: {self.obter_info('atualizaben')} tarefa(s).\n"
        #resultado += f"Com exigência não cumprida aguardando análise da PMF: {self.obter_info('atualizaben')} tarefa(s).\n"

        resultado += f"Sobrestadas: {self.obter_info('sobrestado')} tarefa(s).\n"
        resultado += f"Com impedimento: {self.obter_info('impedimentos')} tarefa(s).\n"

        resultado += f"Pendentes de conclusão da tarefa: {self.obter_info('conclusos')} tarefa(s).\n"
        return resultado

    def alterar_ben(self, subcomando: str, lista: list[str]) -> None:
        beneficio = TipoTexto(lista[0])
        idx = self.base_dados.pesquisar_indice(lista[1])
        if idx is None:
            print('Tarefa não encontrada.\n')
            return
        t = TarefaIsencaoIR(self.base_dados, idx)
        t.alterar_beneficio(beneficio)
        self.salvar_emarquivo()
        print('Alterado.\n')

    def definir_comandos(self) -> None:
        """Define os comandos exclusivos deste processador."""
        self.comandos['ben'] = {
            'funcao': self.alterar_ben,
            'argsmin': 2,
            'desc': 'Alterar o número do benefício da tarefa especificada.',
            'requer_subcomando': False,
            'requer_cnis': False,
			'requer_get': False,
            'requer_processador': True,
            'requer_pmfagenda': False,
            'requer_protocolo': False,
            'requer_sibe': False,
            'requer_sd': False
        }
        self.comandos['analisarpm'] = {
            'funcao': self.cmd_analisar_pm,
            'argsmin': 0,
            'desc': 'Analisa as subtarefas de PM para as tarefas informadas.',
            'requer_subcomando': False,
            'requer_cnis': False,
			'requer_get': True,
            'requer_processador': True,
            'requer_pmfagenda': False,
            'requer_protocolo': False,
            'requer_sibe': False,
            'requer_sd': False
        }
        self.comandos['gerarexig'] = {
            'funcao': self.cmd_gerar_exigencia,
            'argsmin': 0,
            'desc': 'Enviar uma exigência de documentação no GET.',
            'requer_subcomando': False,
            'requer_cnis': False,
			'requer_get': True,
            'requer_processador': True,
            'requer_pmfagenda': False,
            'requer_protocolo': False,
            'requer_sibe': False,
            'requer_sd': False
        }
        self.comandos['gerarsub'] = {
            'funcao': self.cmd_gerar_subtarefa,
            'argsmin': 0,
            'desc': 'Gerar subtarefas para as tarefas informadas.',
            'requer_subcomando': False,
            'requer_cnis': False,
			'requer_get': True,
            'requer_processador': True,
            'requer_pmfagenda': False,
            'requer_protocolo': False,
            'requer_sibe': False,
            'requer_sd': False
        }

    def _definir_filtros(self) -> None:
        """Define os filtros relativos a Isenção de IR de consulta à base de dados"""
        df = self.base_dados.dados
        super().definir_filtros()
        self.filtros['analisedoc'] = {
            'valor': (df['tem_dadosbasicos'] == '1') & (df['tem_documentacao'].isna() & (df['impedimentos'].isna()))
        }
        self.filtros['aguardaexig'] = {
            'valor': (df['tem_exigencia'] == '1') & (df['vencim_exigencia'] >= pd.to_datetime('today').floor('D'))
        }
        self.filtros['exigvencida'] = {
            'valor': (df['tem_exigencia'] == '1') & (df['vencim_exigencia'] < pd.to_datetime('today').floor('D'))
        }
        self.filtros['iir_geracaosub'] = {
            'valor': (df['tem_exigencia'] == '0') & (df['tem_documentacao'] == '1') & df['tem_subtarefa'].isna() & (df['msgerro_criacaosub'].isna()) & (df['impedimentos'].isna())
        }
        self.filtros['subcomerro'] = {
            'valor': (df['tem_exigencia'] == '0') & (df['tem_documentacao'] == '1') & df['tem_subtarefa'].isna() & (df['msgerro_criacaosub'].notna()) & (df['impedimentos'].isna())
        }
        self.filtros['aguardapm'] = {
            'valor': (df['tem_exigencia'] == '0') & (df['tem_subtarefa'] == '1') & df['subtarefaconcluida'].isna() & (df['impedimentos'].isna())
        }
        self.filtros['convocapm'] = {
            'valor': (df['subtarefaconcluida'] == '1') & (df['convocarpm'] == '1') & (df['impedimentos'].isna())
        }
        self.filtros['atualizadespacho'] = {
            'valor': (df['subtarefaconcluida'] == '1') & (df['convocarpm'].isna()) & (df['tem_exigencia'] == '0') & df['atualizacaodespachada'].isna() & (df['impedimentos'].isna())
        }

    def _definir_listagens(self) -> None:
        """Define as listagens relativas a Isenção de IR."""
        super().definir_listagens()
        self.listagens['analisedoc'] = {
            "desc": "Exibe a lista de tarefas pendentes de análise da documentação.",
            "filtro": (self.filtros['analisedoc']['valor']),
            'colunas': ['protocolo', 'der'],
            'ordenacao': ['der'],
            'ordem_crescente': True
        }
        self.listagens['aguardaexig'] = {
            "desc": "Exibe a lista de tarefas pendentes de cumprimento de exigência.",
            "filtro": (self.filtros['aguardaexig']['valor']),
            'colunas': ['protocolo', 'der'],
            'ordenacao': ['der'],
            'ordem_crescente': True
        }
        self.listagens['exigvencida'] = {
            "desc": "Exibe a lista de tarefas com exigência vencida.",
            "filtro": (self.filtros['exigvencida']['valor']),
            'colunas': ['protocolo', 'der'],
            'ordenacao': ['der'],
            'ordem_crescente': True
        }

    def _definir_marcacoes(self) -> None:
        """Define as marcações relativas a Isenção de IR."""
        self.marcacoes['cumpriuexig'] = {
            "desc": "Marca a tarefa como exigência cumprida."
        }
        self.marcacoes['deferido'] = {
            "desc": "Marca a tarefa como atualização deferida."
        }

    def marcar(self, marca: str, protocolos: list[str]) -> None:
        """Marca a lista de tarefas com a marcação especificada."""
        cont = 0

        for protocolo in protocolos:
            idx = self.base_dados.pesquisar_indice(protocolo)
            if idx is None:
                print(f'Tarefa {protocolo} não encontrada.')
                continue
            print(f'Tarefa {protocolo}')
            tarefa = TarefaIsencaoIR(self.base_dados, idx)
                #cont += 1
            self.salvar_emarquivo()            
        self.pos_processar(cont)

    def processar_dados(self) -> None:
        """Processa os daods carregados."""
        tamanho = self.base_dados.tamanho
        self.lista.clear()
        for i in range(tamanho):
            tarefa = TarefaIsencaoIR(self.base_dados, i)
            if not tarefa.esta_concluida().e_verdadeiro:
                self.lista.append(tarefa)
        self.definir_comandos()
        #self.definir_filtros()
        #self.definir_listagens()
        #self.definir_marcacoes()
        
    def obter_lista_iir(self) -> list[TarefaIsencaoIR]:
        lista_tarefas: list[TarefaIsencaoIR] = []
        for item in self.obter_listapersonalizada():
            if (idx := self.base_dados.pesquisar_indice(item)) == None:
                print(f"Erro: Tarefa {item} não foi encontrada na fila atual.\n")
                continue
            t = TarefaIsencaoIR(self.base_dados, idx)
            lista_tarefas.append(t)
        return lista_tarefas
    
    ###===  ANALISE PM ===###

    def processar_relatorio_pm(self, protocolo: str) -> str | None:
        """Processa o relatório PDF da PM. Retornao ID do resultado."""
        #nomearquivo_dadospm = path.join(Variaveis.obter_pasta_entrada(), f'{protocolo} - pmparalancar.txt')
        nomearquivo_relatpm = path.join(Variaveis.obter_pasta_entrada(), f'{protocolo} - relatoriopm.txt')
        
        #Converte o arquivo PDF para Texto
        conv = Conversor()
        conv.processar('pdf', 'txt', 'RelatorioPM', [protocolo])

        #Analisa o arquivo texto convertido e gera outro arquivo estruturado
        #Envia somente se a pericia tiver deferido o benefício.
        dados_pm = analisar_relatoriopm_iir(nomearquivo_relatpm)
        if dados_pm is None:
            return None
        #if dados_pm[11] != 'b36SemSequela' and dados_pm[11] != 'b36NaoEnquadraA3Decreto':
        #    with open(nomearquivo_dadospm, 'w') as arquivo:
        #        arquivo.writelines(item + '\r\n' for item in dados_pm)

        #Retorna o resultado
        return dados_pm[0]
    
    def cmd_analisar_pm(self, subcomandos: list[str]) -> None:
        lista_tarefas: list[TarefaIsencaoIR]
        cont = 0
        self.pre_processar('ANALISAR PM')

        if 'ulp' in subcomandos:
            lista_tarefas = self.obter_lista_iir()
        else:
            lista_tarefas = []
            for t in self.lista:

                #Não irá processar PM se:
                # >não gerou subtarefa
                # >subtarefa está concluída
                # >está em exigência
                # >tarefa tem impedimento
                subtarefa = t.obter_subtarefa()
                exigencia = t.obter_exigencia()
                pm_exigencia = t.tem_exig_pm()
                if not subtarefa.tem or t.subtarefa_concluida().e_verdadeiro or pm_exigencia.e_verdadeiro or exigencia.tem_exigencia().e_verdadeiro or t.tem_impedimento().e_verdadeiro:
                    continue
                lista_tarefas.append(t)
        print(f"{len(lista_tarefas)} tarefa(s) pendente(s) de processamento.")
        for t in lista_tarefas:
            if self.analisar_pm(t):
                cont += 1
        self.pos_processar(cont) 

    def analisar_pm(self, tarefa: TarefaIsencaoIR) -> bool:
        TEXTO_CONCLUIDA = 'Concluída'
        TEXTO_CANCELADA = 'Cancelada'
        TEXTO_EXIGENCIA = 'Exigência'

        buffer_linha = ''
        necessario_fechartarefa = False
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
                print(buffer_linha + 'Tarefa cancelada/concluída. PM não analisada.')
                return False
                
            get.abrir_tarefa()
            subtarefa = tarefa.obter_subtarefa()
            #pericia = tarefa.obter_periciamedica()
            lista_subs = self.coletar_subtarefas(protocolo, True)

            #Checa se a subtarefa registrada é uma subtarefa da tarefa no GET
            for item in lista_subs:
                numsub = item[0]
                statussub = item[1]
                if numsub == str(subtarefa.obter_protocolo()):
                    subtarefa_encontrada = True
                    buffer_linha += f'Subtarefa {numsub} '
                    print(buffer_linha, end='\r')

                    #Se a subtarefa encontrada estiver concluída, analisa o relatorio,
                    #envia o protocolo para habilitação de NB no Prisma
                    if statussub == TEXTO_CONCLUIDA:
                        buffer_linha += 'concluída. '
                        print(buffer_linha, end='\r')
                        resultado_id = self.processar_relatorio_pm(protocolo)
                        if resultado_id is None:
                            print(buffer_linha + ' Erro: Erro ao processar relatório PM.')
                            return False
                        if self.resultados is None:
                            raise Exception()
                        resultado = self.resultados.obter(resultado_id)
                        if resultado is None:
                            print(buffer_linha + ' Erro: Resultado de benefício não é válido.')
                        else:
                            tarefa.alterar_arquivopdfpm(True)
                            tarefa.alterar_resultado(resultado)
                        tarefa.concluir_subtarefa()
                        buffer_linha += ' Relatório PM processado. '
                        print(buffer_linha, end='\r')
                        if resultado == 'iirDeferido':
                            print(buffer_linha + ' Benefício enviado para atualização.')
                        else:
                            tarefa.marcar_conclusa()
                            print(buffer_linha + ' Tarefa marcada para conclusão.')
                        self.salvar_emarquivo()
                    elif statussub == TEXTO_EXIGENCIA:
                        print(buffer_linha + ' em exigência.')
                        tarefa.alterar_exigpm(TipoBooleano(True))
                        self.salvar_emarquivo()
                    elif statussub == TEXTO_CANCELADA:
                        print(buffer_linha + ' cancelada.')
                    else:
                        print(buffer_linha + ' não concluída.')
            if not subtarefa_encontrada:
                print(buffer_linha + ' Erro: Subtarefa não encontrada.')
            get.irpara_iniciotela()
            get.fechar_tarefa()
            return True
        else:
            print(buffer_linha + 'Erro: Tarefa não encontrada.')
            return False
    
    ###===  GERACAO DE EXIGÊNCIAS ===###
    def cmd_gerar_exigencia(self, subcomandos: list[str]) -> None:
        lista_tarefas: list[TarefaIsencaoIR]
        cont = 0
        self.pre_processar('GERAR EXIGÊNCIA')

        if 'ulp' in subcomandos:
            lista_tarefas = self.obter_lista_iir()
        else:
            lista_tarefas = []
            for t in self.lista:

                #Não irá gerar exigência se:
                # >não passou pela análise documental
                # >passou pela análise documental e tem documentos necessários
                # >já foi gerada exigência
                # >tarefa tem impedimento
                exigencia = t.obter_exigencia()
                if not t.tem_analisedoc().e_verdadeiro or t.tem_documentacao().e_verdadeiro or exigencia.tem_exigencia().e_verdadeiro or t.tem_impedimento().e_verdadeiro:
                    continue
                lista_tarefas.append(t)
        print(f"{len(lista_tarefas)} tarefa(s) pendente(s) de processamento.")
        for t in lista_tarefas:
            if self.gerar_exigencia(t):
                cont += 1
        self.pos_processar(cont) 

    def gerar_exigencia(self, tarefa: TarefaIsencaoIR) -> bool:
        """Gera exigência de documentação nas tarefas pendentes de geração de exigência."""
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

            #Verifica se tarefa está em exigencia/cancelada/concluída
            (status, data) = get.coletar_status()
            if status in ['Cancelada', 'Concluída']:
                tarefa.marcar_conclusa()
                tarefa.concluir(TipoData(data))
                print(buffer_linha + 'Concluída/Cancelada. Exigência não foi gerada.')
                return False
            if status == 'Em Exigência':
                print(buffer_linha + 'Tarefa já está em exigência.')
                return False
            
            #Prepara texto da exigência
            texto = self.obter_textoexigencia("documentacaoIIR")
            if len(texto) == 0:
                print(buffer_linha + "Tipo de modelo de exigência não encontrado.")
                return False
            exigencia = tarefa.obter_exigencia()
            
             #Registra a exigência no GET
            if get.definir_exigencia(texto):
                exigencia.iniciar(None)
                print(buffer_linha + "Exigência processada.")
            tarefa.alterar_exigencia(exigencia, True)
            self.salvar_emarquivo()
            return True
        else:
            print(buffer_linha + 'Erro. Tarefa não foi encontrada.')
            return False
    
    ###===  GERACAO DE SUBTAREFAS ===###

    def cmd_gerar_subtarefa(self, subcomandos: list[str]) -> None:
        lista_tarefas: list[TarefaIsencaoIR]
        cont = 0
        self.pre_processar('GERAR SUBTAREFA')

        if 'ulp' in subcomandos:
            lista_tarefas = self.obter_lista_iir()
        else:
            lista_tarefas = []
            for t in self.lista:

                #Não irá gerar subtarefa se:
                # >não tem a documentação médica
                # >ja foi gerada a subtarefa
                # >houve erro durante a geração de subtarefa no processamento anterior
                # >tarefa tem impedimento
                subtarefa = t.obter_subtarefa()
                if not t.tem_documentacao().e_verdadeiro or subtarefa.tem or subtarefa.tem_erro or t.tem_impedimento().e_verdadeiro:
                    continue
                lista_tarefas.append(t)
        print(f"{len(lista_tarefas)} tarefa(s) pendente(s) de processamento.")
        for t in lista_tarefas:
            if self.gerar_subtarefa(t):
                cont += 1
        self.pos_processar(cont)
        
    def gerar_subtarefa(self, tarefa: TarefaIsencaoIR) -> bool:
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

            if self.checar_concluida(tarefa):
                print(buffer_linha + 'Concluída/Cancelada. Subtarefa não foi gerada.')
                return False

            #Abre a tarefa no GET
            get.abrir_tarefa()
            necessario_fechartarefa = True

            #Verifica já existe subtarefa gerada e a coleta
            subtarefa = tarefa.obter_subtarefa()
            dadossub = get.coletar_subtarefa(self.nome_subservico)
            if dadossub[0] != 0:
                subtarefa.alterar_msgerro(TipoTexto(None))
                subtarefa.alterar(TipoInteiro(dadossub[0]), TipoBooleano(False), TipoBooleano(False), TipoData(None))
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

    def processar_geracaosubtarefa(self) -> None:
        """Gera subtarefa nas tarefas pendentes de geração de subtarefa."""
        buffer_linha = ''
        cont = 0
        necessario_fechartarefa = False
        get = self.get
        protocolo = ''

        self.pre_processar('GERAR SUBTAREFA')
        for t in self.lista:

            #Não irá gerar subtarefa se:
            # >não tem documentação
            # >ja foi gerada a subtarefa
            # >houve erro durante a geração de subtarefa no processamento anterior
            # >tarefa tem impedimento
            if not t.tem_documentacao() or t.obter_fase_subtarefa_gerada() or t.tem_erro_geracaosub() or t.tem_impedimento():
                continue

            protocolo = str(t.obter_protocolo())
            buffer_linha = f'Tarefa {protocolo}...'
            print(buffer_linha, end='\r')

            #Pesquisa pela tarefa no GET
            if get.pesquisar_tarefa(protocolo):

                #Verifica se tarefa está cancelada/concluída
                if self.processar_status(t):
                    print(buffer_linha + 'Tarefa cancelada/concluída. Subtarefa não foi gerada.')
                    cont += 1
                    continue

                #Abre a tarefa no GET
                get.abrir_tarefa()
                necessario_fechartarefa = True

                #Verifica a tarefa possui anexos
                if get.possui_anexos():

                    #Verifica já existe subtarefa gerada e a coleta
                    numsub = get.coletar_subtarefa(self.nome_subservico)
                    if numsub != 0:
                        t.alterar_msg_criacaosub('')
                        t.alterar_subtarefa_coletada(True)
                        t.alterar_subtarefa(numsub)
                        t.concluir_fase_subtarefa()
                        print(buffer_linha + 'Subtarefa coletada.')
                    else:
                        #Cria a subtarefa
                        res = get.gerar_subtarefa(self.nome_subservico, self.id_subtarefa, {})
                        if res['sucesso']:
                            t.alterar_msg_criacaosub('')
                            t.alterar_subtarefa_coletada(False)
                            t.alterar_subtarefa(res['numerosub'][0])
                            t.concluir_fase_subtarefa()
                            print(buffer_linha + 'Subtarefa gerada.')
                        else:
                            #Erro na geração de sub. Registra.
                            t.alterar_msg_criacaosub(res['mensagem'])
                            print(buffer_linha + 'Subtarefa não foi gerada.')
                            necessario_fechartarefa = False
                else:
                    print(buffer_linha + 'Tarefa sem anexos. Subtarefa não foi gerada.')
                    t.alterar_temdoc(False)
                if necessario_fechartarefa:
                    get.fechar_tarefa()
                self.salvar_emarquivo()
                cont += 1
            else:
                print(buffer_linha + 'Erro: Tarefa não foi encontrada.')
        self.pos_processar(cont)

    def processar_subtarefa(self, tarefa) -> None:
        """"""
        numsub, subconcluida = self.coletar_subtarefa()
        if len(numsub) > 0:
            tarefa.alterar_subtarefa(numsub)
            tarefa.concluir_fase_subtarefa()
            #if subconcluida:

    def registrar_subgerada(self, tarefa: TarefaIsencaoIR, subtarefa: str) -> None:
        """Registra que já foi gerada subtarefa"""
        tarefa.alterar_subtarefa(subtarefa)
        tarefa.concluir_fase_subtarefa()