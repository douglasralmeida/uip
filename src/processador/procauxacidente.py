## Codificado por Douglas Rodrigues de Almeida.
## Março de 2023
"""Processador para Auxílio Acidente"""

from os import path
import pandas as pd
from .utils import analisar_relatoriopm
from arquivo import ArquivoPrismaEntrada, ArquivoPrismaSaida
from conversor import Conversor
from tarefa import TarefaAuxilioAcidente
from processador import Processador
from variaveis import Variaveis

colunas_especificas = {'tem_agendapm': 'string',
                       'tem_pdfagendapmanexo': 'string',
                       'horaagendamento': 'string',
                       'localagendamento': 'string',
                       'periciacumprida': 'string',
                       'periciarealizada': 'string',
                       'arquivopdfpericia': 'string',
                       'beneficio': 'string',
                       'pericialancada': 'string',
                       'beneficiodespachado': 'string'
                       }

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

class ProcessadorAuxAcidente(Processador):
    """Classe para o processador de Auxílio Acidente."""
    def __init__(self, base_dados) -> None:
        super().__init__(base_dados)
        
        self.atributos = atributos
        
        self.criarsub_modolinha = True
        
        self.dadosparacoletar = ['der', 'cpf', 'quantexig', 'quantsub', 'subtarefa', 'pm', 'olm']

        self.especies_acumulaveis = ['01', '21', '25', '80', '93']

        #Lista de tarefas carregadas da base de dados.
        self.lista = [TarefaAuxilioAcidente]
       
        self.id_subtarefa = 'pm_aa'

        self.nome_servico = 'Auxílio-Acidente'

        self.nome_servicopm = 'AGENDAMENTO - PERÍCIA MÉDICA DE AUXÍLIO-ACIDENTE (ATENDIMENTO PRESENCIAL - AGENDAMENTO)'
        
        self.nome_subservico = 'Perícia Médica de Auxílio-Acidente'
        
        self.base_dados.definir_colunas(colunas_especificas, datas_especificas)
       
    def __str__(self) -> str:
        resultado = super().__str__()
        resultado += self.obter_info('coletadb', 'Pendentes de coleta de dados: {0} tarefa(s).\n')
        resultado += self.obter_info('analiseacb', 'Pendentes de análise de acumulação de benefício: {0} tarefa(s).\n')
        resultado += self.obter_info('geracaosub', 'Pendentes de geração de subtarefa: {0} tarefa(s).\n')
        resultado += self.obter_info('agendamentopm', 'Pendentes de agendamento de perícia médica: {0} tarefa(s).\n')
        resultado += self.obter_info('anexacaoagendapm', 'Pendentes de anexar PDF do agendamento da perícia médica: {0} tarefa(s).\n')
        resultado += self.obter_info('geracaoexig', 'Pendentes de abertura de exigência: {0} tarefa(s).\n')
        resultado += self.obter_info('aguardapm', 'Aguardando a realização da perícia médica: {0} tarefa(s).\n')
        resultado += self.obter_info('pmvencida', 'Com PM vencida {0} tarefa(s).\n')
        resultado += self.obter_info('cancelarsub', 'Sem comparecimento a PM e pendentes de cancelar subtarefa: {0} tarefa(s).\n')
        resultado += self.obter_info('habilitaben', 'Pendentes de habilitação de benefício: {0} tarefa(s).\n')
        resultado += self.obter_info('pmlancar', 'Pendentes de lançamento da PM no Prisma: {0} tarefa(s).\n')
        resultado += self.obter_info('deferir', 'Pendentes de DEFERIMENTO do benefício: {0} tarefa(s).\n')
        resultado += self.obter_info('pmindefere', 'Pendentes de INDEFERIMENTO por PM contrária: {0} tarefa(s).\n')
        resultado += self.obter_info('possuibeninac', 'Pendentes de INDEFERIMENTO por acumulação de benefício: {0} tarefa(s).\n')
        resultado += self.obter_info('recebeaa', 'Pendentes de INDEFERIMENTO por já receber AA: {0} tarefa(s).\n')
        resultado += self.obter_info('naocompareceupm', 'Pendentes de INDEFERIMENTO por não comparecimento a PM: {0} tarefa(s).\n')
        resultado += self.obter_info('desistir', 'Pendentes de DESISTENCIA do requerente no Prisma: {0} tarefa(s).\n')
        resultado += self.obter_info('sobrestado', 'Sobrestadas: {0} tarefas(s)\n')
        resultado += self.obter_info('impedimentos', 'Com impedimento para concluir: {0} tarefas(s)\n')
        resultado += self.obter_info('concluso', 'Com benefício despachado pendente de envio para conclusão: {0} tarefa(s).\n')
        resultado += self.obter_info('conclusao', 'Pendentes de conclusão da tarefa: {0} tarefa(s).\n')
        return resultado
        
    def definir_comandos(self) -> None:
        """Define os comandos exclusivos deste processador."""
        self.comandos['anexarpdfpm'] = {
            'funcao': self.processar_anexacaopdf,
            'argsmin': 0,
            'desc': 'Anexa o arquivo PDF na tarefa do GET.',
            'requer_subcomando': False,
            'requer_cnis': False,
			'requer_get': True,
            'requer_processador': True,
            'requer_pmfagenda': False,
            'requer_protocolo': False,
            'requer_sibe': False
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
            'requer_sibe': False
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
            'requer_sibe': False
        }
        self.comandos['analisarnb'] = {
            'funcao': self.processar_analiseben,
            'argsmin': 0,
            'desc': 'Recebe a lista de benefícios habilitados no Prisma.',
            'requer_subcomando': False,
            'requer_cnis': False,
			'requer_get': False,
            'requer_processador': True,
            'requer_pmfagenda': False,
            'requer_protocolo': True,
            'requer_sibe': False
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
            'requer_sibe': False
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
            'requer_protocolo': True,
            'requer_sibe': False
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
            'requer_sibe': False
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
            'requer_sibe': False
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
            'requer_sibe': False
        }
    # 
    def definir_filtros(self) -> None:
        """Define os filtros relaticos a Auxílio-Acidente de consulta à base de dados"""
        df = self.base_dados.dados
        filto_sem_imp_conc = df['impedimentos'].isna() & df['concluso'].isna() & df['sub_sobrestado'].isna()
        
        super().definir_filtros()
        self.filtros['geracaosub'] = {
            'valor': (df['possui_ben_inacumulavel'] == '0') & df['tem_subtarefa'].isna() & filto_sem_imp_conc
        }
        self.filtros['analiseacb'] = {
            'valor': (df['tem_dadosbasicos'] == '1') & df['possui_ben_inacumulavel'].isna() & filto_sem_imp_conc
        }
        self.filtros['agendamentopm'] = {
            'valor': (df['tem_subtarefa'] == '1') & df['tem_agendapm'].isna() & filto_sem_imp_conc
        }
        self.filtros['anexacaoagendapm'] = {
            'valor': (df['tem_agendapm'] == '1') & df['tem_pdfagendapmanexo'].isna() & filto_sem_imp_conc
        }
        self.filtros['geracaoexig'] = {
            'valor': (df['tem_pdfagendapmanexo'] == '1') & df['tem_exigencia'].isna() & filto_sem_imp_conc
        }
        self.filtros['aguardapm'] = {
            'valor': (df['tem_exigencia'] == '1') & df['periciacumprida'].isna() & (df['dataagendamento'] >= pd.to_datetime('today')) & 
                     filto_sem_imp_conc
        }
        self.filtros['pmvencida'] = {
            'valor': (df['tem_exigencia'] == '1') & df['periciacumprida'].isna() & (df['dataagendamento'] < pd.to_datetime('today')) &
                     filto_sem_imp_conc
        }
        self.filtros['cancelarsub'] = {
            'valor': (df['periciacumprida'] == '1') & (df ['periciarealizada'] == '0') & df['subtarefacancelada'].isna() &
                     filto_sem_imp_conc
        }
        self.filtros['habilitaben'] = {
            'valor': ((df['periciarealizada'] == '1') | (df['subtarefacancelada'] == '1') | (df['possui_ben_inacumulavel'] == '1') | 
                      (df['resultado'] == 'desistencia')) & df['beneficio'].isna() & filto_sem_imp_conc
        }
        self.filtros['pmlancar'] = {
            'valor': (df ['periciarealizada'] == '1') & df['beneficio'].notna() & df ['pericialancada'].isna() &
                     df['resultado'].isin(['b36Deferido', 'b94Deferido']) & filto_sem_imp_conc
        }
        self.filtros['deferir'] = {
            'valor': (df['pericialancada'] == '1') & df['beneficiodespachado'].isna() & filto_sem_imp_conc
        }
        self.filtros['pmindefere'] = {
            'valor': df['beneficio'].notna() & df['resultado'].isin(['b36SemSequela', 'b36NaoEnquadraA3Decreto']) &
                     df['beneficiodespachado'].isna() & filto_sem_imp_conc
        }
        self.filtros['possuibeninac'] = {
            'valor': df['beneficio'].notna() & (df['resultado'] == 'b36RecebeBenInac') &
                     df['beneficiodespachado'].isna() & filto_sem_imp_conc
        }
        self.filtros['recebeaa'] = {
            'valor': df['beneficio'].notna() & (df['resultado'] == 'b36RecebeAA') &
                     df['beneficiodespachado'].isna() & filto_sem_imp_conc
        }
        self.filtros['naocompareceupm'] = {
            'valor': df['beneficio'].notna() & (df['resultado'] == 'b36NaoComparecePM') &
                     df['beneficiodespachado'].isna() & filto_sem_imp_conc
        }
        self.filtros['desistir'] = {
            'valor': df['beneficio'].notna() & (df['resultado'] == 'desistencia') &
                     df['beneficiodespachado'].isna() & filto_sem_imp_conc
        }
        self.filtros['concluso'] = {
            'valor': (df['beneficiodespachado'] == '1') & filto_sem_imp_conc
        }

    def definir_listagens(self) -> None:
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

    def enviar_tarefa_habilitacao(self, tarefa) -> None:
        nomearquivo_entrada = path.join(Variaveis.obter_pasta_entrada(), 'tarefas_habilitar.txt')
        cabecalho = ['protocolo', 'nit', 'der']
        arquivo_prisma = ArquivoPrismaEntrada(nomearquivo_entrada, cabecalho)
        arquivo_prisma.carregar()
        if arquivo_prisma.carregado:
            dados = [tarefa.obter_nit(), tarefa.obter_der().strftime('%d/%m/%Y')]
            arquivo_prisma.alterar_dados(tarefa.obter_protocolo(), dados)
            arquivo_prisma.salvar()
        else:
            print("Erro. Não foi possível abrir o arquivo de entrada para processamento do Prisma.\n")

    def enviar_lancarpm(self, protocolo: str, beneficio: str) -> None:
        """Envia dados da tarefa para lançamento de PM no Prisma."""
        cabecalho = ['protocolo', 'beneficio']
        nomearquivo_entrada = path.join(Variaveis.obter_pasta_entrada(), 'tarefas_lancarpm.txt')

        # Anota as tarefas no arquivo tarefas_lancarpm
        arquivo_prisma = ArquivoPrismaEntrada(nomearquivo_entrada, cabecalho)
        arquivo_prisma.carregar()
        if arquivo_prisma.carregado:
            arquivo_prisma.alterar_dados(protocolo, [beneficio])
            arquivo_prisma.salvar()
        else:
            print("Erro: Não foi possível abrir o arquivo de entrada para processamento do Prisma.")

    def marcar(self, marca: str, protocolos: list[str]) -> None:
        """Marca a lista de tarefas com a marcação especificada."""
        cont = 0
        
        if marca == 'naocomparecepm':
            self.pre_processar('MARCAR NÃO COMPARECEU A PM')
        if marca == 'jarecebeaa':
            self.pre_processar('JÁ RECEBE AUXÍLIO ACIDENTE')
        for protocolo in protocolos:
            idx = self.base_dados.pesquisar_indice(protocolo)
            if idx is None:
                print(f'Tarefa {protocolo} não encontrada.')
                continue
            print(f'Tarefa {protocolo}')
            tarefa = TarefaAuxilioAcidente(self.base_dados, idx)
            if marca == 'naocomparecepm':
                if tarefa.obter_fase_agendapm():
                    tarefa.marcar_pm_naocompareceu()
                    cont += 1
            if marca == 'jarecebeaa':
                tarefa.alterar_beninacumluavel(True)
                tarefa.alterar_resultado('b36RecebeAA')
                cont += 1
            self.salvar_emarquivo()
            
        self.pos_processar(cont)

    #Verifica se houve habilitações de NB no Prisma.
    #>Recebe a lista de NBs do Accuterm
    #>Processa o relatório de PM em PDF para TXT estruturado
    #>Marca as tarefas com NB habilitados para lançar PM
    #>Encaminha lista de NBs para lançar PM no Accuterm
    def processar_analiseben(self, subcomando: str, lista: list[str]) -> None:
        buffer_linha = ''
        cont = 0
        cont_enviarpm = 0
        lista_sucesso = []
        nomearquivo_saida = path.join(Variaveis.obter_pasta_entrada(), 'ben_habilitados.txt')
        self.pre_processar('ANALISAR HABILITAÇÃO DE BENEFÍCIO')

        #Recebe a lista de NBs habilitados no Prisma
        arquivo_prisma = ArquivoPrismaSaida(nomearquivo_saida, ['protocolo', 'beneficio'])
        arquivo_prisma.carregar()
        if not arquivo_prisma.carregado:
            return
        for protocolo, dados in arquivo_prisma.dados.items():
            buffer_linha = f'Tarefa {protocolo}...'
            print(buffer_linha, end='\r')
            nb = dados[0]
            if len(nb) > 0:
                idx = self.base_dados.pesquisar_indice(protocolo)
                if idx is None:
                    print(buffer_linha + 'Tarefa não encontrada.')
                    continue
                t = TarefaAuxilioAcidente(self.base_dados, idx)
                buffer_linha += f'Habilitado com NB {nb}.'
                print(buffer_linha, end='\r')
                t.alterar_beneficio(nb)
                res = t.obter_resultado()
                if res in ['b36Deferido', 'b94Deferido']:
                    self.enviar_lancarpm(protocolo, nb)
                    print(buffer_linha + 'Enviada para lançamento da PM.')
                    cont_enviarpm += 1
                else:
                    print(buffer_linha + 'Aguarda indeferimento.')
                self.salvar_emarquivo()
                lista_sucesso.append(protocolo)
            cont += 1
        for p in lista_sucesso:
            arquivo_prisma.excluir_dados(p)
        if len(lista_sucesso) > 0:
            arquivo_prisma.salvar()
        #Envia a tarefa para lançamento de PM no Prisma
        print(f'{cont_enviarpm} tarefa(s) enviada(s) para lançamento de PM no Prisma.')
        self.pos_processar(cont)

    #Analisa a PM da tarefa
    #>Quando a data da perícia já passou, pesquisa a situação da sub de PM.
    #>Salva o conteúdo da PM em PDF para lançamento no PRISMA.
    #>Marca os requerimentos que não houve conclusão da sub de PM.
    #>Encaminha lista de tarefas para habilitar NB no Accuterm.
    def processar_analisepm(self, subcomando: str, lista: list[str]) -> None:
        buffer_linha = ''
        cont = 0
        cont_enviados = 0
        protocolo = ''
        subtarefa = ''
        usar_lista_personalizada = False
        subtarefa_encontrada = False
        buffer_linha = ''

        self.pre_processar('ANALISAR PM')
        if len(lista) > 0:
            usar_lista_personalizada = True        
        for t in self.lista:
            protocolo = t.obter_protocolo()
            if usar_lista_personalizada:
                if not protocolo in lista:
                    continue
            else:
                if not t.tem_exigencia() or t.obter_fase_pericia_cumprida() or not t.pericia_esta_vencida():
                    continue
            buffer_linha = f'Tarefa {protocolo}...'
            print(buffer_linha, end='\r')
            subtarefa = t.obter_subtarefa()
            if self.get.pesquisar_tarefa(protocolo):
                self.get.abrir_tarefa()
                lista_subs = self.coletar_subtarefas(protocolo, True)
                for item in lista_subs:
                    numsub = item[0]
                    subconcluida = item[1]
                    if numsub == subtarefa:
                        subtarefa_encontrada = True
                        buffer_linha += f'Subtarefa {numsub}'
                        print(buffer_linha, end='\r')
                        if subconcluida:
                            print(buffer_linha + ' concluída.')
                            resultado = self.processar_relatorio_pm(protocolo)
                            if resultado is None:
                                print(buffer_linha + '. Erro: Relatório PM não foi processado.')
                                continue
                            t.marcar_pm_realizada(resultado)
                            if not t.obter_fase_beneficio_habilitado:
                                self.enviar_tarefa_habilitacao(t)
                                print('Enviada para habilitação.')
                            self.salvar_emarquivo()
                            cont_enviados += 1
                        else:
                            print(buffer_linha + ' não concluída.')
                if not subtarefa_encontrada:
                    print(buffer_linha + 'Erro: Subtarefa não encontrada.')
                self.get.irpara_iniciotela()
                self.get.fechar_tarefa()
                cont += 1
            else:
                print(buffer_linha + 'Erro: Tarefa não encontrada.')
        print(f'{cont_enviados} tarefa(s) enviada(s) para habilitação no Prisma.')
        self.pos_processar(cont)

    #Anexa o PDF do agendamento da PM na tarefa
    def processar_anexacaopdf(self, subcomando: str, lista: list[str]) -> None:
        buffer_linha = ''
        cont = 0
        nome_arquivo_pdf = ''  
        protocolo = ''

        self.pre_processar('ANEXAR PDF AGENDAMENTO PM')
        for t in self.lista:
            if not t.obter_fase_agendapm() or t.obter_fase_pdfagendapm_anexo():
                continue
            protocolo = str(t.obter_protocolo())
            buffer_linha = f'Tarefa {protocolo}...'
            print(buffer_linha)
            if self.get.pesquisar_tarefa(protocolo):
                nome_arquivo_pdf = f'{protocolo} - AgendaPM.pdf'
                self.get.abrir_tarefa()
                if self.adicionar_anexo([nome_arquivo_pdf])[0]:
                    t.concluir_fase_pdfagendapm_anexo()
                    buffer_linha += 'PDF anexado.'
                    print(buffer_linha)
                else:
                    print(buffer_linha + 'Erro: Arquivo não foi anexado.')
                self.get.fechar_tarefa()
                self.salvar_emarquivo()
                cont += 1
            else:
                print(buffer_linha + 'Erro: Tarefa não foi encontrada.')
        self.pos_processar(cont)
    
    def processar_cancelasub(self, subcomando: str, lista: list[str]) -> None:
        """Processa o cancelamento de subtarefas."""
        buffer_linha = ''
        cont = 0
        protocolo = ''
        texto_conclusao = 'Não houve comparecimento do titular do requerimento a perícia médica agendada.'

        self.pre_processar('CANCELAR SUBTAREFA')
        for t in self.lista:
            if t.tem_pericia_realizada() or not t.obter_fase_pericia_cumprida() or t.obter_fase_subtarefa_cancelada() or t.tem_impedimento():
                continue
            protocolo = str(t.obter_protocolo())
            buffer_linha = f'Tarefa {protocolo}...'
            print(buffer_linha)
            if self.get.pesquisar_tarefa(protocolo):
                self.get.abrir_tarefa()
                self.get.irpara_guia('Subtarefas')
                self.get.irpara_finaltela()
                if self.get.cancelar_sub(t.obter_subtarefa(), self.nome_subservico, texto_conclusao):
                    t.concluir_fase_subtarefa_cancelada()
                    print(buffer_linha + 'Cancelada.')
                self.salvar_emarquivo()
                self.get.fechar_tarefa()
                cont += 1
            else:
                print('Erro: Tarefa não encontrada.')
        self.pos_processar(cont)

    def processar_coletanit(self, subcomando: str, lista: list[str]) -> None:
        """
        Coleta o NIT via CNIS da tarefa especificada.
        """
        cont = 0
        self.pre_processar('COLETAR NIT')
        for protocolo in lista:
            if (idx := self.base_dados.pesquisar_indice(protocolo)) is None:
                print(f'Tarefa {protocolo} não foi encontrada.')
                continue
            t = TarefaAuxilioAcidente(self.base_dados, idx)
            nit = self.cnis.pesquisar_nit_decpf(protocolo, t.obter_cpf())
            t.alterar_nit(nit)
            print(f'Tarefa {protocolo} processada.')
            self.salvar_emarquivo()
            cont =+ 1
        self.pos_processar(cont)

    def processar_despachosben(self, subcomando: str, lista: list[str]) -> None:
        """
        Verifica se houve despacho do BEN no Prisma.
        >Recebe a lista de tarefas do Accuterm
        >Marca as tarefas com BEN despachados
        """
        buffer_linha = ''
        cont = 0
        lista_sucesso = []
        nomearquivo_saida = path.join(Variaveis.obter_pasta_entrada(), 'ben_despachados.txt')
        self.pre_processar('ANALISAR DESPACHOS DE BENEFÍCIO')

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
            resultado = dados[2]
            if nb_despachado:
                idx = self.base_dados.pesquisar_indice(protocolo)
                if idx is None:
                    print(buffer_linha + 'Tarefa não encontrada.')
                    continue
                t = TarefaAuxilioAcidente(self.base_dados, idx)
                t.concluir_fase_benef_despachado()
                if pdf_resumo:
                    t.alterar_pdfresumo(True)
                t.alterar_resultado(resultado)
                t.concluir_fase_concluso()
                self.salvar_emarquivo()
                lista_sucesso.append(protocolo)
                print(buffer_linha + f'Conclusa com resultado {resultado}.')
                cont += 1
        for p in lista_sucesso:
            arquivo_prisma.excluir_dados(p)
        if len(lista_sucesso) > 0:
            arquivo_prisma.salvar()
        self.pos_processar(cont)

    def processar_exigenciapm(self, subcomando: str, lista: list[str]) -> None:
        """Cadastra exigência de agendamento de PM."""
        cont = 0
        protocolo = ''

        self.pre_processar('GERAR EXIGÊNCIA DO AGENDAMENTO DA PM')
        for t in self.lista:
            if not t.obter_fase_pdfagendapm_anexo() or t.tem_exigencia():
                continue
            protocolo = str(t.obter_protocolo())
            print(f'Tarefa {protocolo}')
            if self.get.pesquisar_tarefa(protocolo):
                #self.get.abrir_tarefa()
                if self.definir_exigencia_pm(t.obter_agendamento()):
                    t.concluir_fase_exigencia(True)
                else:
                    print("Erro ao atribuir exigência.")
                #self.get.fechar_tarefa()
                self.salvar_emarquivo()
                cont += 1
            else:
                print(f'Erro. Tarefa {protocolo} não foi encontrada.')
        self.pos_processar(cont)

    def processar_dados(self) -> None:
        """Processa os daods carregados."""
        tamanho = self.base_dados.tamanho
        self.lista.clear()
        for i in range(tamanho):
            tarefa = TarefaAuxilioAcidente(self.base_dados, i)
            if not tarefa.obter_fase_conclusao():
                self.lista.append(tarefa)
        self.definir_comandos()
        self.definir_filtros()
        self.definir_listagens()
        self.definir_marcacoes()

    def processar_geracaosubtarefa(self) -> None:
        """Gera subtarefa nas tarefas pendentes de geração de subtarefa."""
        buffer_linha = ''
        cont = 0        
        protocolo = ''

        self.pre_processar('GERAR SUBTAREFA')
        for t in self.lista:
            if not t.obter_fase_analise_beninacumulavel() or t.obter_fase_subtarefa_gerada() or t.tem_ben_inacumulavel() or t.tem_impedimento():
                continue
            protocolo = str(t.obter_protocolo())
            buffer_linha = f'Tarefa {protocolo}...'
            print(buffer_linha, end='\r')
            if self.get.pesquisar_tarefa(protocolo):
                status = self.get.coletar_status()
                if status == 'Cancelada':
                    print(buffer_linha + 'Tarefa cancelada. Subtarefa não foi gerada.')
                    t.concluir_fase_concluso()
                    t.concluir_fase_conclusao()
                if status == 'Concluída':
                    print(buffer_linha + 'Tarefa concluída. Subtarefa não foi gerada.')
                    t.concluir_fase_concluso()
                    t.concluir_fase_conclusao()                    
                self.get.abrir_tarefa()
                (sucesso, subcoletada) = self.gerar_subtarefa(t, {})
                if sucesso:
                    if subcoletada:
                        print(buffer_linha + 'Subtarefa coletada.')
                    else:
                        print(buffer_linha + 'Subtarefa gerada.')
                    self.get.fechar_tarefa()
                    self.salvar_emarquivo()
                    cont += 1
                else:
                    print(buffer_linha + 'Subtarefa não foi gerada.')
            else:
                print(buffer_linha + 'Erro: Tarefa não foi encontrada.')
        self.pos_processar(cont)

    def processar_lancamentopm(self, subcomando: str, lista: list[str]) -> None:
        """
        Verifica se houve lançamento de PM no Prisma.
        >Recebe a lista de tarefas do Accuterm
        >Marca as tarefas com PM lançada
        """
        buffer_linha = ''
        cont = 0
        lista_sucesso = []
        nomearquivo_saida = path.join(Variaveis.obter_pasta_entrada(), 'pm_lancadas.txt')
        self.pre_processar('ANALISAR LANÇAMENTO DE PERÍCIA MÉDICA')

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
                t = TarefaAuxilioAcidente(self.base_dados, idx)
                t.concluir_fase_pericia_lancada()
                self.salvar_emarquivo()
                print(buffer_linha + 'Tarefa processada.')
                cont += 1
        for p in lista_sucesso:
            arquivo_prisma.excluir_dados(p)
        if len(lista_sucesso) > 0:
            arquivo_prisma.salvar()
        self.pos_processar(cont)

    def processar_lista(self, processamento: str, lista: list[str]) -> None:
        num_itens = len(lista)
        super().processar_lista(lista)

    def processar_relatorio_pm(self, protocolo: str) -> str:
        """Processa o relatório PDF da PM."""
        nomearquivo_dadospm = path.join(Variaveis.obter_pasta_entrada(), f'{protocolo} - pmparalancar.txt')
        nomearquivo_relatpm = path.join(Variaveis.obter_pasta_entrada(), f'{protocolo} - relatoriopm.txt')
        
        #Converte o arquivo PDF para Texto
        conv = Conversor()
        conv.processar('pdf', 'txt', 'RelatorioPM', [protocolo])

        #Analisa o arquivo texto convertido e gera outro arquivo estruturado
        #Envia somente se a pericia tiver deferido o benefício.
        dados_pm = analisar_relatoriopm(nomearquivo_relatpm)
        if dados_pm is None:
            return None
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

    def registrar_subgerada(self, tarefa: TarefaAuxilioAcidente, subtarefa: str) -> None:
        """Registra que já foi gerada subtarefa"""
        tarefa.alterar_subtarefa(subtarefa)
        tarefa.concluir_fase_subtarefa()

    def registrar_exigenciagerada(self, tarefa: TarefaAuxilioAcidente) -> None:
        """Registra que já foi gerada exigência"""
        tarefa.concluir_fase_exigencia(False)

    def registrar_pmfoi_realizada(self, resultado: str, tarefa: TarefaAuxilioAcidente) -> None:
        """Registra que já foi realizada perícia."""
        tarefa.marcar_pm_realizada(resultado)
        if not tarefa.obter_fase_beneficio_habilitado:
            self.enviar_tarefa_habilitacao(tarefa)