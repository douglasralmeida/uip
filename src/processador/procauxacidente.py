## Codificado por Douglas Rodrigues de Almeida.
## Março de 2023
"""Processador para Auxílio Acidente"""

import pandas as pd
from .procben import ProcessadorBeneficio
from .utils import analisar_relatoriopm
from arquivo import ArquivoPrismaEntrada
from conversor import Conversor
from os import path
from tarefa import TarefaAuxilioAcidente
from variaveis import Variaveis

datas_especificas = ['dataagendamento']

atributos = {'tembeninac':   {'coluna': 'possui_ben_inacumulavel',
                              'tipo': 'booleano',
                              'valores_possiveis': {'sim': '1',
                                                    'nao': '0',
                                                    'vazio': ''
                                                   }
                            },
            'ms':           {'coluna': 'ms',
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
            'nbinac':        {'coluna': 'nb_inacumulavel',
                              'tipo': 'texto'
            },
            'espinac':       {'coluna': 'especie_inacumulavel',
                              'tipo': 'inteiro'
            }
}

class ProcessadorAuxAcidente(ProcessadorBeneficio):
    """Classe para o processador de Auxílio Acidente."""
    def __init__(self, base_dados) -> None:
        super().__init__(base_dados)
        
        self.atributos = atributos
        
        self.criarsub_modolinha = True
        
        self.dadosparacoletar = ['der', 'cpf', 'quantexig', 'quantsub', 'subtarefa', 'pm', 'olm']

        self.especies_acumulaveis = ['01', '21', '25', '80', '93']
        
        self.id_subtarefa = 'pm_aa'

        #Lista de tarefas carregadas da base de dados.
        self.lista: list[TarefaAuxilioAcidente] = []        

        self.nome_servico = 'Auxílio-Acidente'

        self.nome_servicopm = 'AGENDAMENTO - PERÍCIA MÉDICA DE AUXÍLIO-ACIDENTE (ATENDIMENTO PRESENCIAL - AGENDAMENTO)'
        
        self.nome_subservico = 'Perícia Médica de Auxílio-Acidente'

        #Tag para benefício
        self.tags.append('aa')
        
        self.base_dados.definir_colunas(datas_especificas)
       
    def __str__(self) -> str:
        resultado = super().__str__()

        resultado += f"Pendentes de coleta de dados: {self.obter_info('coletadb')} tarefa(s).\n"
        resultado += f"Pendentes de análise sobre acumulação de benefício: {self.obter_info('analiseacb')} tarefa(s).\n"
        resultado += f"Pendentes de geração de subtarefa: {self.obter_info('geracaosub')} tarefa(s).\n"
        resultado += f"Com erro na geração de subtarefa de PM: {self.obter_info('subcomerro')} tarefa(s).\n"
        resultado += f"Pendentes de agendamento da PM: {self.obter_info('agendamentopm')} tarefa(s).\n"
        resultado += f"Com agendamento e aguardando anexação do comprovante: {self.obter_info('anexacaoagendapm')} tarefa(s).\n"
        resultado += f"Com agendamento e erro na anexação do comprovante: {self.obter_info('anexacaoagendacomerro')} tarefa(s).\n"
        resultado += f"Pendentes de geração da exigência do agendamento da PM: {self.obter_info('gerarexig')} tarefa(s).\n"
        resultado += f"Com agendamento e aguardando a realização da PM: {self.obter_info('aguardapm')} tarefa(s).\n"
        resultado += f"Com agendamento vencido: {self.obter_info('pmvencida')} tarefa(s).\n"
        resultado += f"Pendentes de cancelamento de subtarefa: {self.obter_info('cancelarsub')} tarefa(s).\n"
        resultado += f"Pendentes de habilitação de benefício: {self.obter_info('habilitaben')} tarefa(s).\n"
        resultado += f"Pendentes de lançamento da PM no Prisma: {self.obter_info('pmlancar')} tarefa(s).\n"
        resultado += f"Pendentes de DEFERIMENTO do benefício: {self.obter_info('deferir')} tarefa(s).\n"
        resultado += f"Pendentes de INDEFERIMENTO/DESISTENCIA do benefício: {self.obter_info('indeferir')} tarefa(s).\n"
        resultado += f"Pendentes de INDEFERIMENTO por acumulação indevida: {self.obter_info('indeferirinac')} tarefa(s).\n"
        resultado += f"Sobrestadas: {self.obter_info('sobrestado')} tarefa(s).\n"
        resultado += f"Com impedimentos: {self.obter_info('impedimentos')} tarefa(s).\n"
        resultado += f"Pendentes de envio para conclusão: {self.obter_info('conclusos')} tarefa(s).\n"
        return resultado
        
    def definir_comandos(self) -> None:
        """Define os comandos exclusivos deste processador."""
        self.comandos['agendarpm'] = {
                'funcao': self.comando_agendar_pm,
                'argsmin': 0,
                'desc': 'Executa o programa \'Agendar PM\' do processador.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': False,
                'requer_processador': True,
                'requer_pmfagenda': True,
                'requer_protocolo': False,
                'requer_sibe': False,
                'requer_sd': False
                
        }        
        self.comandos['anexarpdfpm'] = {
            'funcao': self.comando_anexar_pdfpm,
            'argsmin': 0,
            'desc': 'Anexa o arquivo PDF na tarefa do GET.',
            'requer_subcomando': False,
            'requer_cnis': False,
			'requer_get': True,
            'requer_processador': True,
            'requer_pmfagenda': False,
            'requer_protocolo': False,
            'requer_sibe': False,
                'requer_sd': False
        }
        self.comandos['checarpm'] = {
                'funcao': self.comando_checar_agendapm,
                'argsmin': 0,
                'desc': 'Executa o programa \'Checar Agenda PM\' do processador.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': False,
                'requer_processador': True,
                'requer_pmfagenda': True,
                'requer_protocolo': False,
                'requer_sibe': False,
                'requer_sd': False
        }  
        self.comandos['gerarexigpm'] = {
            'funcao': self.processar_exigenciapm,
            'argsmin': 0,
            'desc': 'Enviar uma exigência no GET com o agendamento da PM.',
            'requer_subcomando': False,
            'requer_cnis': False,
			'requer_get': True,
            'requer_processador': True,
            'requer_pmfagenda': False,
            'requer_protocolo': False,
            'requer_sibe': False,
                'requer_sd': False
        }
        self.comandos['analisarpm'] = {
            'funcao': self.processar_analisepm,
            'argsmin': 0,
            'desc': 'Verifica se a PM foi realizada no GET e gera seu relatório.',
            'requer_subcomando': False,
            'requer_cnis': False,
			'requer_get': True,
            'requer_processador': True,
            'requer_pmfagenda': False,
            'requer_protocolo': False,
            'requer_sibe': False,
                'requer_sd': False
        }
        self.comandos['receberben'] = {
            'funcao': self.processar_recebimentoben,
            'argsmin': 0,
            'desc': 'Recebe a lista de benefícios habilitados no Prisma.',
            'requer_subcomando': False,
            'requer_cnis': False,
			'requer_get': False,
            'requer_processador': True,
            'requer_pmfagenda': False,
            'requer_protocolo': True,
            'requer_sibe': False,
                'requer_sd': False
        }
        self.comandos['cancelarsub'] = {
            'funcao': self.processar_cancelasub,
            'argsmin': 0,
            'desc': 'Cancela a subtarefa de PM para as tarefas com não comparecimento a PM.',
            'requer_subcomando': False,
            'requer_cnis': False,
			'requer_get': True,
            'requer_processador': True,
            'requer_pmfagenda': False,
            'requer_protocolo': False,
            'requer_sibe': False,
                'requer_sd': False
        }
        self.comandos['coletarnit'] = {
            'funcao': self.processar_coletanit,
            'argsmin': 1,
            'desc': 'Coleta o NIT do CNIS para a tarefa especificada.',
            'requer_subcomando': False,
            'requer_cnis': True,
			'requer_get': False,
            'requer_processador': True,
            'requer_pmfagenda': False,
            'requer_protocolo': False,
            'requer_sibe': False,
                'requer_sd': False
        }
        self.comandos['enviarhabilitacao'] = {
            'funcao': self.processar_enviohabilitacao,
            'argsmin': 0,
            'desc': 'Gera a lista de benefícios para habilitação no Prismna.',
            'requer_subcomando': False,
            'requer_cnis': False,
			'requer_get': False,
            'requer_processador': True,
            'requer_pmfagenda': False,
            'requer_protocolo': False,
            'requer_sibe': False,
            'requer_sd': False
        }
        self.comandos['enviarindeferimento'] = {
            'funcao': self.processar_envioindeferimento,
            'argsmin': 0,
            'desc': 'Gera a lista de benefícios para indeferimento no Prismna.',
            'requer_subcomando': False,
            'requer_cnis': False,
			'requer_get': False,
            'requer_processador': True,
            'requer_pmfagenda': False,
            'requer_protocolo': False,
            'requer_sibe': False,
            'requer_sd': False
        }
        self.comandos['enviarlancarpm'] = {
            'funcao': self.processar_enviolancarpm,
            'argsmin': 0,
            'desc': 'Gera a lista de benefícios para lançar PM no Prisma.',
            'requer_subcomando': False,
            'requer_cnis': False,
			'requer_get': False,
            'requer_processador': True,
            'requer_pmfagenda': False,
            'requer_protocolo': False,
            'requer_sibe': False,
            'requer_sd': False
        }
        self.comandos['processardataspm'] = {
            'funcao': self.processar_dataspm,
            'argsmin': 0,
            'desc': 'Consulta novamente as datas de agendamento de PM.',
            'requer_subcomando': False,
            'requer_cnis': False,
			'requer_get': False,
            'requer_processador': True,
            'requer_pmfagenda': True,
            'requer_protocolo': False,
            'requer_sibe': False,
                'requer_sd': False
        }
        self.comandos['receberlpm'] = {
            'funcao': self.processar_lancamentopm,
            'argsmin': 0,
            'desc': 'Recebe a lista de perícias lançadas no Prisma.',
            'requer_subcomando': False,
            'requer_cnis': False,
			'requer_get': False,
            'requer_processador': True,
            'requer_pmfagenda': False,
            'requer_protocolo': False,
            'requer_sibe': False,
                'requer_sd': False
        }
        self.comandos['receberdespachos'] = {
            'funcao': self.processar_despachosben,
            'argsmin': 0,
            'desc': 'Recebe a lista de benefícios despachados no Prisma.',
            'requer_subcomando': False,
            'requer_cnis': False,
			'requer_get': False,
            'requer_processador': True,
            'requer_pmfagenda': False,
            'requer_protocolo': False,
            'requer_sibe': False,
                'requer_sd': False
        }
        self.comandos['pm'] = {
            'funcao': self.exibir_pm,
            'argsmin': 1,
            'desc': 'Exibe a perícia médica da tarefa especificida.',
            'requer_subcomando': False,
            'requer_cnis': False,
			'requer_get': False,
            'requer_processador': True,
            'requer_pmfagenda': False,
            'requer_protocolo': True,
            'requer_sibe': False,
                'requer_sd': False
        }
        self.comandos['transformarpm'] = {
            'funcao': self.transformar_pmtxt_pmestruturado,
            'argsmin': 0,
            'desc': 'Gerar o arquivo de PM estruturado a partir do relatório PDF.',
            'requer_subcomando': False,
            'requer_cnis': False,
			'requer_get': False,
            'requer_processador': True,
            'requer_pmfagenda': False,
            'requer_protocolo': False,
            'requer_sibe': False,
                'requer_sd': False
        }

    def coletar_pm(self) -> None:
        pass

    ###===  ANALISE DAS PERICIAS MEDICAS ===###

    def processar_analisar_pm_base(self) -> None:
        cont = 0
        self.pre_processar('ANALISAR PM')
        for t in self.lista:
            agendamento = t.obter_agendamento_pm()
            exigencia = t.obter_exigencia()
            pericia = t.obter_periciamedica()
            subtarefa = t.obter_subtarefa()
            if not exigencia.tem_exigencia().e_verdadeiro or pericia.cumprida().e_verdadeiro or not agendamento.esta_vencido() or subtarefa.cancelada().e_verdadeiro or t.tem_impedimento().e_verdadeiro or t.esta_concluida().e_verdadeiro:
                continue
            if self.analisar_pm(t):
                cont += 1
        self.pos_processar(cont)

    def processar_analisar_pm_lote(self) -> None:
        cont = 0
        self.pre_processar('ANALISAR PM')
        print("Usando lista personalizada.")

        for item in self.obter_listapersonalizada():
            if (idx := self.base_dados.pesquisar_indice(item)) == None:
                print(f"Erro: Tarefa {item} não foi encontrada na fila atual.\n")
                continue
            t = TarefaAuxilioAcidente(self.base_dados, idx)
            if self.analisar_pm(t):
                cont += 1
        self.pos_processar(cont)
    
    #Analisa a PM da tarefa
    #>Quando a data da perícia já passou, pesquisa a situação da sub de PM.
    #>Salva o conteúdo da PM em PDF para lançamento no PRISMA.
    #>Marca os requerimentos que não houve conclusão da sub de PM.
    #>Encaminha lista de tarefas para habilitar NB no Accuterm.
    def analisar_pm(self, tarefa: TarefaAuxilioAcidente) -> bool:
        buffer_linha = ''
        cont = 0
        get = self.get
        protocolo = ''
        subtarefa_encontrada = False

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
            pericia = tarefa.obter_periciamedica()
            lista_subs = self.coletar_subtarefas(protocolo, True)

            #Checa se a subtarefa registrada é uma subtarefa da tarefa no GET
            for item in lista_subs:
                numsub = item[0]
                subconcluida = item[1]
                if numsub == str(subtarefa.obter_protocolo()):
                    subtarefa_encontrada = True
                    buffer_linha += f'Subtarefa {numsub} '
                    print(buffer_linha, end='\r')

                    #Se a subtarefa encontrada estiver concluída, analisa o relatorio,
                    #envia o protocolo para habilitação de NB no Prisma
                    if subconcluida:
                        buffer_linha += ' concluída. '
                        print(buffer_linha, end='\r')
                        resultado_id = self.processar_relatorio_pm(protocolo)
                        if resultado_id is None:
                            print(buffer_linha + ' Erro: Erro ao processar relatório PM.')
                            return False
                        pericia.marcar_realizada()
                        tarefa.alterar_periciamedica(pericia)
                        if self.resultados is None:
                            raise Exception()
                        resultado = self.resultados.obter(resultado_id)
                        if resultado is None:
                            print(buffer_linha + ' Erro: Resultado de benefício não é válido.')
                        else:
                            tarefa.alterar_resultado(resultado)
                        buffer_linha += ' Relatório PM processado. '
                        print(buffer_linha, end='\r')
                        if tarefa.beneficio_habilitado():
                            ben = str(tarefa.obter_beneficio())
                            print(buffer_linha + f' Benfício já está habilitado. NB: {ben}.')
                        else:
                            der = str(tarefa.obter_der())
                            nit = str(tarefa.obter_nit())
                            self.enviar_tarefa_habilitacao(protocolo, der, nit)
                            print(buffer_linha + ' Benefício enviado para habilitação.')
                                
                        self.salvar_emarquivo()
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
    
    def marcar(self, marca: str, protocolos: list[str]) -> None:
        """Marca a lista de tarefas com a marcação especificada."""
        buffer_linha = ''
        cont = 0
        
        if marca == 'naocomparecepm':
            self.pre_processar('MARCAR NÃO COMPARECEU A PM')
        if marca == 'jarecebeaa':
            self.pre_processar('JÁ RECEBE AUXÍLIO ACIDENTE')

        for protocolo in protocolos:
            idx = self.base_dados.pesquisar_indice(protocolo)
            buffer_linha = f'Tarefa {protocolo}...'
            print(buffer_linha, end='\r')
            if idx is None:
                print(buffer_linha + 'Não encontrada.')
                continue
            tarefa = TarefaAuxilioAcidente(self.base_dados, idx)
            if marca == 'naocomparecepm':
                pericia = tarefa.obter_periciamedica()
                pericia.marcar_naocompareceu()
                tarefa.alterar_periciamedica(pericia)
                if self.resultados is None: 
                    return
                resultado = self.resultados.obter('b36NaoComparecePM')
                if resultado is None:
                    raise Exception()
                tarefa.alterar_resultado(resultado)
                if tarefa.beneficio_habilitado():
                    ben = str(tarefa.obter_beneficio())
                    buffer_linha += f'Não compareceu. Benfício já está habilitado. NB: {ben}.'
                else:
                    der = str(tarefa.obter_der())
                    nit = str(tarefa.obter_nit())
                    self.enviar_tarefa_habilitacao(protocolo, der, nit)
                    buffer_linha += 'Não compareceu. Benefício enviado para habilitação.'
                print(buffer_linha)
                cont += 1
            if marca == 'jarecebeaa':
                #tarefa.alterar_beninacumluavel(True)
                #tarefa.alterar_resultado('b36RecebeAA')
                cont += 1
            self.salvar_emarquivo()
            
        self.pos_processar(cont)

    def _definir_listagens(self) -> None:
        """Define as listagens relativas a Auxílio Acidente."""
        super().definir_listagens()
        self.listagens['analiseacb'] = {
            "desc": "Exibe a lista de tarefas pendentes de análise de acumulação de benefícios.",
            "filtro": self.filtros['analiseacb']['valor'],
            'colunas': ['protocolo', 'cpf'],
            'ordenacao': ['der'],
            'ordem_crescente': True
        }
        self.listagens['geracaosub'] = {
            "desc": "Exibe a lista de tarefas pendentes de geração de subtarefa de PM.",
            "filtro": (self.filtros['geracaosub']['valor']),
            'colunas': ['protocolo', 'der'],
            'ordenacao': ['der'],
            'ordem_crescente': True
        }
        self.listagens['agendamentopm'] = {
            "desc": "Exibe a lista de tarefas pendentes de agendamento da PM.",
            "filtro": (self.filtros['agendamentopm']['valor']),
            'colunas': ['protocolo', 'cpf', 'der'],
            'ordenacao': ['der'],
            'ordem_crescente': True
        }
        self.listagens['anexacaoagendapm'] = {
            "desc": "Exibe a lista de tarefas pendentes de anexação do PDF do agendamento da PM.",
            "filtro": (self.filtros['anexacaoagendapm']['valor']),
            'colunas': ['protocolo' 'der'],
            'ordenacao': ['der'],
            'ordem_crescente': True
        }
        self.listagens['geracaoexig'] = {
            "desc": "Exibe a lista de tarefas pendentes de geração de exigência com o agendamento da PM.",
            "filtro": (self.filtros['geracaoexig']['valor']),
            'colunas': ['protocolo', 'der'],
            'ordenacao': ['der'],
            'ordem_crescente': True
        }
        self.listagens['aguardapm'] = {
            "desc": "Exibe a lista de tarefas pendentes de realização de PM.",
            "filtro": (self.filtros['aguardapm']['valor']),
            'colunas': ['protocolo', 'dataagendamento', 'horaagendamento'],
            'ordenacao': ['dataagendamento'],
            'ordem_crescente': True
        }
        self.listagens['pmvencida'] = {
            "desc": "Exibe a lista de tarefas com PM vencida.",
            "filtro": (self.filtros['pmvencida']['valor']),
            'colunas': ['protocolo', 'cpf', 'dataagendamento', 'horaagendamento'],
            'ordenacao': ['dataagendamento'],
            'ordem_crescente': True
        }
        self.listagens['cancelasub'] = {
            "desc": "Exibe a lista de tarefas sem comparecimento a PM e pedentes de cancelamento de subtarefa.",
            "filtro": (self.filtros['cancelarsub']['valor']),
            'colunas': ['protocolo'],
            'ordenacao': ['der'],
            'ordem_crescente': True
        }        
        self.listagens['habilitaben'] = {
            "desc": "Exibe a lista de tarefas pedentes de habilitação no Prisma.",
            "filtro": (self.filtros['habilitaben']['valor']),
            'colunas': ['protocolo', 'nit', 'der'],
            'ordenacao': ['der'],
            'ordem_crescente': True
        }
        self.listagens['lancarpm'] = {
            "desc": "Exibe a lista de tarefas com benefício habilitado aguardando lançamento da PM.",
            "filtro": (self.filtros['pmlancar']['valor']),
            'colunas': ['protocolo', 'beneficio'],
            'ordenacao': ['der'],
            'ordem_crescente': True
        }
        self.listagens['deferir'] = {
            "desc": "Exibe a lista de tarefas com PM lançada aguardando despacho de deferimento do benefício.",
            "filtro": (self.filtros['deferir']['valor']),
            'colunas': ['protocolo', 'beneficio', 'resultado'],
            'ordenacao': ['der'],
            'ordem_crescente': True
        }
        self.listagens['pmindefere'] = {
            "desc": "Exibe a lista de tarefas com PM lançada aguardando despacho de indeferimento do benefício.",
            "filtro": (self.filtros['pmindefere']['valor']),
            'colunas': ['protocolo', 'beneficio', 'resultado'],
            'ordenacao': ['resultado', 'der'],
            'ordem_crescente': True
        }
        self.listagens['jarecebe'] = {
            "desc": "Exibe a lista de tarefas cujo requerente já recebe AA aguardando despacho de indeferimento do benefício.",
            "filtro": (self.filtros['recebeaa']['valor']),
            'colunas': ['protocolo', 'beneficio'],
            'ordenacao': ['der'],
            'ordem_crescente': True
        }   
        self.listagens['acumula'] = {
            "desc": "Exibe a lista de tarefas com acumulação indevida aguardando despacho de indeferimento do benefício.",
            "filtro": (self.filtros['possuibeninac']['valor']),
            'colunas': ['protocolo', 'beneficio'],
            'ordenacao': ['der'],
            'ordem_crescente': True
        }
        self.listagens['naocompareceupm'] = {
            "desc": "Exibe a lista de tarefas sem comparecimento a PM aguardando despacho de indeferimento do benefício.",
            "filtro": (self.filtros['naocompareceupm']['valor']),
            'colunas': ['protocolo', 'beneficio'],
            'ordenacao': ['der'],
            'ordem_crescente': True
        }
        self.listagens['desistencia'] = {
            "desc": "Exibe a lista de tarefas com desistencia do requerente aguardando despacho do benefício.",
            "filtro": (self.filtros['desistir']['valor']),
            'colunas': ['protocolo', 'beneficio'],
            'ordenacao': ['der'],
            'ordem_crescente': True
        }
        self.listagens['semnit'] = {
            "desc": "Exibe a lista de tarefas sem NIT.",
            "filtro": (self.filtros['semnit']['valor']),
            'colunas': ['protocolo', 'cpf'],
            'ordenacao': ['der'],
            'ordem_crescente': True
        }        

    def definir_marcacoes(self) -> None:
        """Define as marcações relativas a Auxílio Acidente."""
        self.marcacoes['naocomparecepm'] = {
            "desc": "Marca a tarefa com o não comparecimento do titular a PM."
        }
        self.marcacoes['jarecebeaa'] = {
            "desc": "Marca a tarefa com a existência de benefício de auxílio-acidente."
        }

    def exibir_fases(self) -> None:
        print("FASES DO FLUXO DA TAREFA DE AUXÍLIO-ACIDENTE\n")

        print("FASE 1:  Coletar Dados Básicos\n\tcomando coletardb")
        print("FASE 2:  Analisar incompatibilidade com benefícios ativos\n\tcomando acumulaben")
        print("\tPasso 1: Para casos com acumulação: avaliar o relatório geradp se de fato há acumulação.")
        print("\tPasso 1: Para casos que inacumulação detectada: comando editartarefa espinac num_especie num_tarefa")
        print("\tPasso 1: Para casos que inacumulação detectada: comando editartarefa nbinac num_beneficio num_tarefa")
        print("\tPasso 2: Para casos que já recebe AA: comando marcar recebeaa num_tarefa")
        print("\tPasso 3: Para casos que recebe benefício inacumulável: comando marcar recebebeninac num_tarefa*")
        print("FASE 3:  Gerar subtarefa no GET\n\tcomando gerarsub")
        print("FASE 4:  Agendar PM no PMF Agenda\n\tcomando agendarpm")
        print("FASE 5:  Anexar PDF do agendamento PM no GET\n\tcomando anexarpdfpm")
        print("FASE 6:  Abrir exigência do agendamento da PM\n\tcomando gerarexigpm")
        print("FASE 7:  Analisar PM\n\tPasso 1: Coletar dados da PM e salvar relatório em PDF da PM: comando analisarpm*")
        print("\tPasso 2: Verificar casos de reagendamento de PM: procedimento manual")
        print("\tPasso 3: Marcar tarefas com não comparecimento: comando marcar naocomparecepm tarefa1 tarefa2 tarefa3...*")
        print("\tPasso 4: Cancelar subtarefa de não comparecidos: comando cancelasub")
        print("\tPasso 5: Gerar arquivo texto do relatório da PM: comando processarpm")
        print("FASE 8:  Habilitar benefício no Prisma")
        print("\tPasso 1: Gerar lista de tarefas para habilitação: comando gerarlista habilitaben")
        print("\tPasso 2: Processar habilitação no Prisma: usar módulo de automação do Accuterm")
        print("\tPasso 3: Processar lista de benefícios habilitados: comando processar benhabilita")
        print("FASE 9:  Lançar dados PM no Prisma")
        print("\tPasso 1: Gerar lista de tarefas para lançar PM: comando gerarlista lancarpm")
        print("\tPasso 2: Processar habilitação no Prisma: usar módulo de automação do Accuterm")
        print("\tPasso 3: Processar lista de benefícios com PM lançadas: comando processar pmlancadas")
        print("FASE 10: Despachar benefício no Prisma\n\tprocedimento manual")
        print("FASE 11: Registrar resultado do benefício\n\tprocedimento manual")
        print("FASE 12: Concluir tarefa no GET\n\tcomando concluirtarefa")

    def exibir_pm(self, subtarefa: str, lista: list[str]) -> None:
        """Exibe uma PM da tarefa especificada."""
        for p in lista:
            nomearquivo_dadospm = path.join(Variaveis.obter_pasta_entrada(), f'{p} - pmparalancar.txt')
            try:
                with open(nomearquivo_dadospm, 'rt', newline='\r\n') as arquivo:
                    texto = [s.strip() for s in arquivo.readlines()]
                    print(f'PERÍCIA MÉDICA DA TAREFA {p}')
                    print(f'------------------------------------')
                    print(f'DID: {texto[0]}')
                    print(f'DII: {texto[1]}')
                    print(f'Houve acidente: {texto[2]}')
                    print(f'Data do Acidente: {texto[3]}')
                    print(f'Acidente de Trabalho: {texto[4]}')
                    print(f'Sequela enquadra: {texto[5]}')
                    print(f'Data da marcação: {texto[6]}')
                    print(f'Conclusão: {texto[7]}')
                    print(f'CID: {texto[8]}')
                    print(f'Código do perito: {texto[9]}')
                    print(f'Data da conclusão: {texto[10]}')
                    print(f'Resultado: {texto[11]}\n')
            except FileNotFoundError as e:
                print('A tarefa especificada não possui perícia médica.\n')

    def enviar_tarefas_habilitacao(self, tarefas: list[TarefaAuxilioAcidente]) -> None:
        nomearquivo_entrada = path.join(Variaveis.obter_pasta_entrada(), 'tarefas_habilitar.txt')
        cabecalho = ['protocolo', 'nit', 'der']
        arquivo_prisma = ArquivoPrismaEntrada(nomearquivo_entrada, cabecalho)
        arquivo_prisma.carregar()
        if arquivo_prisma.carregado:
            for tarefa in tarefas:
                der = tarefa.obter_der()
                if not isinstance(der, str):
                    der = der.strftime('%d/%m/%Y')
                dados = [tarefa.obter_nit(), der]
                arquivo_prisma.alterar_dados(tarefa.obter_protocolo(), dados)    
        else:
            print("Erro. Não foi possível abrir o arquivo de entrada para processamento do Prisma.\n")
        arquivo_prisma.salvar()    

    #Verifica se houve habilitações de NB no Prisma.
    #>Recebe a lista de NBs do Accuterm
    #>Processa o relatório de PM em PDF para TXT estruturado
    #>Marca as tarefas com NB habilitados para lançar PM
    #>Encaminha lista de NBs para lançar PM no Accuterm
    def processar_recebimentoben(self, subcomando: str, lista: list[str]) -> None:
        self.receber_beneficios()

    def processar_analisepm(self, subcomando: str, lista: list[str]) -> None:
        if len(lista) > 0 and lista[0] == 'ulp':
            self.processar_analisar_pm_lote()
        else:
            self.processar_analisar_pm_base()

    def processar_anexopmpdf(self, subcomando: str, lista: list[str]) -> None:
        self.anexar_agendamentopm()    
    
    def processar_cancelasub(self, subcomando: str, lista: list[str]) -> None:
        self.cancelar_subtarefa()

    def processar_coletanit(self, subcomando: str, lista: list[str]) -> None:
        """
        Coleta o NIT via CNIS da tarefa especificada.
        """
        self.coletar_nit_lote()

    def processar_dataspm(self, subcomando: str, lista: list[str]) -> None:
        "Consulta novamente as datas das perícias agendadas no PMF Agenda."
        buffer_linha = ''
        cont = 0
        self.pre_processar("PROCESSAMENTO DATA AGENDAMENTO DE PM")
        for t in self.lista:
            if t.obter_fase_agendapm():
                agendamento = self.pmfagenda.consultar_data(t.obter_cpf())
                t.alterar_agendamento(agendamento)
                t.alterar_agendareproc(True)
                self.salvar_emarquivo()
                print(f'Tarefa {t.obter_protocolo()} processada.')
                cont += 1
        self.pos_processar(cont)

    def processar_despachosben(self, subcomando: str, lista: list[str]) -> None:
        self.receber_despachos()

    def obter_listaauxilio_acidente(self) -> list[TarefaAuxilioAcidente]:
        lista_tarefas: list[TarefaAuxilioAcidente] = []

        for item in self.obter_listapersonalizada():
            if (idx := self.base_dados.pesquisar_indice(item)) == None:
                print(f'Erro: Tarefa {item} não foi encontrada.\n')
                continue
            t = TarefaAuxilioAcidente(self.base_dados, idx)
            lista_tarefas.append(t)
        return lista_tarefas
    
    def processar_enviohabilitacao(self, subcomando: str, lista: list[str]) -> None:
        """a """
        self.pre_processar('ENVIAR PARA HABILITAÇÃO')
        if len(lista) > 0 and lista[0] == 'ulp':
            self.enviar_habilitacao_lote()
        else:
            print("Erro: Sem suporte a envio de processos para habilitação fora do lote lista_protocolos.txt no momento.\n")

    def processar_envioindeferimento(self, subcomando: str, lista: list[str]) -> None:
        """a"""
        self.pre_processar('ENVIAR PARA INDEFERIMENTO')
        if len(lista) > 0 and lista[0] == 'ulp':
            self.enviar_indeferimento_lote()
        else:
            print("Erro: Sem suporte a envio de processos para indeferimento fora do lote lista_protocolos.txt no momento.\n")

    def processar_enviolancarpm(self, sucomando: str, lista: list[str]) -> None:
        """a"""
        self.pre_processar('ENVIAR PARA LANÇAMENTO DE PM')
        if len(lista) > 0 and lista[0] == 'ulp':
            self.enviar_lancarpm_lote()
        else:
            print("Erro: Sem suporte a envio de processos para lançamento de PM fora do lotelista_protocolos.txt no momento.\n")

    def processar_exigenciapm(self, subcomando: str, lista: list[str]) -> None:
        """Cadastra exigência de agendamento de PM."""

        self.pre_processar('GERAR EXIGÊNCIA DO AGENDAMENTO DA PM')
        if len(lista) > 0 and lista[0] == 'ulp':
            self.processar_gerarexigencia_pm_lote()
        else:
            self.processar_gerarexigencia_pm_base()

    def processar_dados(self) -> None:
        """Processa os daods carregados."""
        tamanho = self.base_dados.tamanho
        self.lista.clear()
        for i in range(tamanho):
            tarefa = TarefaAuxilioAcidente(self.base_dados, i)
            if not tarefa.esta_concluida().e_verdadeiro:
                self.lista.append(tarefa)
        self.definir_comandos()
        self.definir_marcacoes()

    def processar_lancamentopm(self, subcomando: str, lista: list[str]) -> None:
        self.receber_lancamentospm()

    def processar_lista(self, processamento: str, lista: list[str]) -> None:
        num_itens = len(lista)
        super().processar_lista(lista)

    def processar_relatorio_pm(self, protocolo: str) -> str | None:
        """Processa o relatório PDF da PM. Retornao ID do resultado."""
        nomearquivo_dadospm = path.join(Variaveis.obter_pasta_entrada(), f'{protocolo} - pmparalancar.txt')
        nomearquivo_relatpm = path.join(Variaveis.obter_pasta_entrada(), f'{protocolo} - relatoriopm.txt')
        
        #Converte o arquivo PDF para Texto
        conv = Conversor()
        conv.processar('pdf', 'txt', 'RelatorioPM', [protocolo])

        #Analisa o arquivo texto convertido e gera outro arquivo estruturado
        #Envia somente se a pericia tiver deferido o benefício.
        dados_pm = analisar_relatoriopm(nomearquivo_relatpm)
        if dados_pm is None:
            return 'None'
        if dados_pm[11] != 'b36SemSequela' and dados_pm[11] != 'b36NaoEnquadraA3Decreto':
            with open(nomearquivo_dadospm, 'w') as arquivo:
                arquivo.writelines(item + '\r\n' for item in dados_pm)

        #Retorna o resultado
        return dados_pm[11]

    def processar_subtarefa(self, tarefa: str) -> None:
        "Pesquisa se a tarefa já possui sub de PM e retorna status"
        lista = self.coletar_subtarefa()
        for item in lista:
            numsub = item(0)
            subconcluida = item(1)
            if len(numsub) > 0:
                self.registrar_subgerada(tarefa, numsub)
                if subconcluida:
                    self.registrar_pmfoi_realizada(tarefa)

    def transformar_pmtxt_pmestruturado(self, subcomando: str, lista: list[str]) -> None:
        cont = 0
        for protocolo in lista:
            self.processar_relatorio_pm(protocolo)
            print(f'Tarefa {protocolo}.')
            cont += 1
        print(f'Processados: {cont} item(ns).')