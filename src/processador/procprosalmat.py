## Codificado por Douglas Rodrigues de Almeida.
## Março de 2023
"""Processador para Prorrogação de Salário Maternidade"""

import pandas as pd
from arquivo import ArquivoPrismaSaida
from os import path
from tarefa.tarpsalmat import TarefaProrrogacaoSalMaternidade
from processador import Processador
from variaveis import Variaveis

tipocolunas = {'beneficio': 'string',
               'tem_documentacao': 'string',
               'para_sobrestar': 'string',
               'sub_sobrestado': 'string',
               'sobrestamento_cancelado': 'string',
               'pericia_realizada': 'string',
               'arquivopdf_pericia': 'string',
               'pericialancada': 'string',
               'atualizacao_despachada': 'string',
               'enviado_sman': 'string',
               'subtarefa_coletada': 'string',
               'msgerro_criacaosub': 'string'
}

colunasdata = ['vencim_exigencia']

atributos = {'tembenefinac': {'coluna': 'possui_ben_inacumulavel',
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
            'exig_cumprida': {'coluna': 'exigencia_cumprida',
                                   'tipo': 'booleano',
                                   'valores_possiveis': {'sim': '1',
                                                         'nao': '0',
                                                         'vazio': ''
                                                         }
                                  },
            'tem_doc': {'coluna': 'tem_documentacao',
                                   'tipo': 'booleano',
                                   'valores_possiveis': {'sim': '1',
                                                         'nao': '0',
                                                         'vazio': ''
                                                         }
                                  }
            }

class ProcessadorProrrogSalMaternidade(Processador):
    """Classe para o processador de Prorrogação de Salário Maternidade."""
    def __init__(self, base_dados):      
        super().__init__(base_dados)
        
        self.atributos = atributos
        
        self.criarsub_modolinha = False
        
        self.dadosparacoletar = ['nb', 'der', 'nit', 'cpf', 'quantexig', 'quantsub', 'subtarefa']
        
        self.nome_subservico = 'Análise Processual de Prorrogação de Salário-Maternidade'
        
        self.nome_servico = 'Prorrogação do Salário-Maternidade'
        
        self.id = 'psm'
        
        self.id_subtarefa = 'pm_psm'

        #Lista de tarefas carregadas da base de dados.
        self.lista = [TarefaProrrogacaoSalMaternidade]

        self.base_dados.definir_colunas(tipocolunas, colunasdata)

    def __str__(self) -> str:
        resultado = super().__str__()
        resultado += self.obter_info('coletadb', 'Pendentes de coleta de dados: {0} tarefa(s).\n')
        resultado += self.obter_info('analisedoc', 'Pendentes de análise da documentação: {0} tarefa(s).\n')
        resultado += self.obter_info('definirexig', 'Pendentes de abertura de exigência: {0} tarefa(s)\n')
        resultado += self.obter_info('aguardaexig', 'Aguardando cumprimento de exigência: {0} tarefa(s)\n')
        resultado += self.obter_info('exigvencida', 'Pendentes com exigência vencida: {0} tarefa(s)\n')
        resultado += self.obter_info('abrirsub', 'Pendentes de criação de subtarefa de PM: {0} tarefa(s).\n')
        resultado += self.obter_info('aguardasub', 'Aguardando subtarefa de PM: {0} tarefa(s).\n')
        resultado += self.obter_info('analisarpm', 'Pendentes de análise da PM realizada: {0} tarefa(s)\n')
        resultado += self.obter_info('deferir15D', 'Pendentes de DEFERIR por 15 dias no Prisma: {0} tarefas(s)\n')
        resultado += self.obter_info('enviarsman', 'Pendentes de envio para o Serviço de Manutenção: {0} tarefas(s)\n')
        resultado += self.obter_info('aguardasman', 'Aguarda por processamento pelo Serviço de Manutenção: {0} tarefa(s).\n')
        resultado += self.obter_info('sobrestado', 'Sobrestadas: {0} tarefas(s)\n')
        resultado += self.obter_info('impedimentos', 'Com impedimento para concluir: {0} tarefas(s)\n')
        resultado += self.obter_info('conclusao', 'Com resultado para concluir: {0} tarefas(s)\n')
        
        return resultado

    def definir_comandos(self):
        self.comandos['analisarsman'] = {
            'funcao': self.processar_analisesman,
            'argsmin': 0,
            'desc': 'Recebe a lista de benefícios processados pelo Serviço de Manutenção.',
            'requer_subcomando': False,
            'requer_cnis': False,
            'requer_get': False,
            'requer_processador': True,
            'requer_pmfagenda': False,
            'requer_protocolo': False,
            'requer_sibe': False
        }
        self.comandos['checarsub'] = {
            'funcao': self.processar_checagemsub,
            'argsmin': 0,
            'desc': '(sem descrição).',
            'requer_subcomando': False,
            'requer_cnis': False,
            'requer_get': True,
            'requer_processador': True,
            'requer_pmfagenda': False,
            'requer_protocolo': False,
            'requer_sibe': False
        }
        self.comandos['gerarexig'] = {
            'funcao': self.processar_exigencia,
            'argsmin': 0,
            'desc': 'Enviar uma exigência de documentação no GET.',
            'requer_subcomando': False,
            'requer_cnis': False,
			'requer_get': True,
            'requer_processador': True,
            'requer_pmfagenda': False,
            'requer_protocolo': False,
            'requer_sibe': False
        }

    def definir_filtros(self) -> None:
        """Define os filtros relativos a Prorrogação de Salário Maternidade de consulta à base de dados."""
        df = self.base_dados.dados
        super().definir_filtros()
        self.filtros['analisedoc'] = {
            'valor': (df['tem_dadosbasicos'] == '1') & (df['tem_documentacao'].isna()) & (df['impedimentos'].isna()) & (df['concluso'].isna())
        }
        self.filtros['definirexig'] = {
            'valor': (df['tem_documentacao'] == '0') & (df['tem_exigencia'].isna()) & (df['impedimentos'].isna()) & (df['concluso'].isna())
        }
        self.filtros['aguardaexig'] = {
            'valor': (df['tem_exigencia'] == '1') & (df['tem_documentacao'] == '0') & (df['vencim_exigencia'] >= pd.to_datetime('today').floor('D')) & (df['impedimentos'].isna()) & (df['concluso'].isna())
        }
        self.filtros['exigvencida'] = {
            'valor': (df['tem_exigencia'] == '1') & (df['tem_documentacao'] == '0') & (df['vencim_exigencia'] < pd.to_datetime('today').floor('D')) & (df['impedimentos'].isna()) & (df['concluso'].isna())
        }
        self.filtros['abrirsub'] = {
            'valor': (df['tem_documentacao'] == '1') & (df['subtarefa'].isna()) & (df['impedimentos'].isna()) & (df['concluso'].isna())
        }
        self.filtros['aguardasub'] = {
            'valor': (df['subtarefa'].notna()) & (df['pericia_realizada'].isna()) & (df['impedimentos'].isna()) & (df['concluso'].isna())
        }
        self.filtros['analisarpm'] = {
            'valor': (df['pericia_realizada'] == '1') & (df['resultado'].isna()) & (df['impedimentos'].isna()) & (df['concluso'].isna())
        }
        self.filtros['deferir15D'] = {
            'valor': (df['resultado'] == 'pSMDeferido15D') & (df['atualizacao_despachada'].isna() & (df['impedimentos'].isna())) & (df['impedimentos'].isna()) & (df['concluso'].isna())
        }
        self.filtros['enviarsman'] = {
            'valor': (df['resultado'] == 'pSMDeferidoACP') & (df['enviado_sman'].isna()) & (df['impedimentos'].isna()) & (df['concluso'].isna())
        }
        self.filtros['aguardasman'] = {
            'valor': (df['enviado_sman'] == '1') & (df['atualizacao_despachada'].isna())
        }

    def definir_listagens(self):
        super().definir_listagens()
        self.listagens['analisedoc'] = {
            "desc": "Exibe a lista de tarefas pendentes de análise da documentação.",
            "filtro": (self.filtros['analisedoc']['valor']),
            'colunas': ['protocolo', 'der'],
            'ordenacao': ['der'],
            'ordem_crescente': True
        }
        self.listagens['definirexig'] = {
            "desc": "Exibe a lista de tarefas pendentes de geração de exigência.",
            "filtro": (self.filtros['definirexig']['valor']),
            'colunas': ['protocolo', 'der'],
            'ordenacao': ['der'],
            'ordem_crescente': True
        }
        self.listagens['aguardaexig'] = {
            "desc": "Exibe a lista de tarefas aguardando cumprimento de exigência.",
            "filtro": (self.filtros['aguardaexig']['valor']),
            'colunas': ['protocolo', 'vencim_exigencia'],
            'ordenacao': ['vencim_exigencia'],
            'ordem_crescente': True
        }
        self.listagens['exigvencida'] = {
            "desc": "Exibe a lista de tarefas com exigência vencida.",
            "filtro": (self.filtros['exigvencida']['valor']),
            'colunas': ['protocolo', 'vencim_exigencia'],
            'ordenacao': ['vencim_exigencia'],
            'ordem_crescente': True
        }
        self.listagens['abrirsub'] = {
            "desc": "Exibe a lista de tarefas pendentes de abertura de subtarefa de PM.",
            "filtro": (self.filtros['abrirsub']['valor']),
            'colunas': ['protocolo', 'der'],
            'ordenacao': ['der'],
            'ordem_crescente': True
        }
        self.listagens['aguardasub'] = {
            "desc": "Exibe a lista de tarefa aguardando subtarefa de PM.",
            "filtro": (self.filtros['aguardasub']['valor']),
            'colunas': ['protocolo', 'der'],
            'ordenacao': ['der'],
            'ordem_crescente': True
        }
        self.listagens['analisarpm'] = {
            "desc": "Exibe a lista de tarefas pendentes de análise do relatório da PM.",
            "filtro": (self.filtros['analisarpm']['valor']),
            'colunas': ['protocolo', 'der'],
            'ordenacao': ['der'],
            'ordem_crescente': True
        }
        self.listagens['deferir15D'] = {
            "desc": "Exibe a lista de tarefas pendentes de atualização no Prisma para prorrogação por mais 15 dias.",
            "filtro": (self.filtros['deferir15D']['valor']),
            'colunas': ['protocolo', 'der', "beneficio"],
            'ordenacao': ['der'],
            'ordem_crescente': True
        }
        self.listagens['enviarsman'] = {
            "desc": "Exibe a lista de tarefas pendentes de envio para o Serviço de Manutenção para prorrogação via ACP.",
            "filtro": (self.filtros['enviarsman']['valor']),
            'colunas': ['protocolo', 'der', 'beneficio'],
            'ordenacao': ['der'],
            'ordem_crescente': True
        }
        self.listagens['aguardasman'] = {
            "desc": "Exibe a lista de tarefas pendentes de processamento de prorrogação pelo Serviço de Manutenção.",
            "filtro": (self.filtros['aguardasman']['valor']),
            'colunas': ['protocolo', 'der', 'beneficio'],
            'ordenacao': ['der'],
            'ordem_crescente': True
        }
    
    def definir_marcacoes(self) -> None:
        """Define as marcações que podem ser utilizadas pelo usuário."""
        self.marcacoes['cumpriuexig'] = {
            "desc": "Marca a tarefa com cumprimento de exigência."
        }
        
    def exibir_fases(self) -> None:
        """Exibe as fases do fluxo de trabalho da Tarefa de Prorrogação de Sal. Maternidade."""
        print("FASES DO FLUXO DA TAREFA DE PRORROGAÇÃO DE SALÁRIO-MATERNIDADE\n")

        print("FASE 1:  Coletar Dados Básicos\n\tcomando coletardb")
        print("FASE 2:  Analisar documentação apresentada\n\tprocedimento manual")
        print("FASE 3:  Definir exigência de documentação médica\n\ta fazer")
        print("FASE 4:  Verificar cumprimento da exigência\n\ta fazer")
        print("FASE 5:  Gerar subtarefa para PM\n\ta fazer")
        print("FASE 6:  Analisar PM\n\ta fazer")
        print("FASE 7:  Sobrestar\n\ta fazer")
        print("FASE 8:  Atualizar benefício\n\ta fazer")
        print("FASE 9:  Concluir tarefa\n\ta fazer")

    def marcar(self, marca: str, protocolos: list[str]) -> None:
        """Marca a lista de tarefas com a marcação especificada."""
        cont = 0
        
        if marca == 'cumpriuexig':
            self.pre_processar('MARCAR CUMPRIU EXIGÊNCIA')
        for protocolo in protocolos:
            idx = self.base_dados.pesquisar_indice(protocolo)
            if idx is None:
                print(f'Tarefa {protocolo} não encontrada.')
                continue
            print(f'Tarefa {protocolo}')
            tarefa = TarefaProrrogacaoSalMaternidade(self.base_dados, idx)
            if marca == 'cumpriuexig':
                if tarefa.tem_exigencia():
                    tarefa.cumprir_exigencia()
                    cont += 1
            self.salvar_emarquivo()
        self.pos_processar(cont)

    def processar_analisesman(self, subcomando: str, lista: list[str]) -> None:
        """Recebe a listagem de benefícios processados pelo Serviço de Manutenção."""
        cont = 0
        lista_sucesso = []
        nomearquivo_saida = path.join(Variaveis.obter_pasta_entrada(), 'ben_sman.txt')
        self.pre_processar('ANALISAR PROCESSAMENTO DO SERV. MANUTENÇÃO')

        #Recebe a lista de processados
        arquivo_prisma = ArquivoPrismaSaida(nomearquivo_saida, ['protocolo', 'atualizacao_despachada', 'tem_pdfresumoanexo'])
        arquivo_prisma.carregar()
        if not arquivo_prisma.carregado:
            return
        for protocolo, dados in arquivo_prisma.dados.items():
            idx = self.base_dados.pesquisar_indice(protocolo)
            if idx is None:
                print(f'Tarefa {protocolo} não encontrada.')
                continue
            print(f'Tarefa {protocolo}')
            t = TarefaProrrogacaoSalMaternidade(self.base_dados, idx)
            t.concluir_fase_atualizacao()
            t.marcar_pdfresumo()
            t.concluir_fase_concluso()
            self.salvar_emarquivo()
            lista_sucesso.append(protocolo)
            cont += 1
        for p in lista_sucesso:
            arquivo_prisma.excluir_dados(p)
        if len(lista_sucesso) > 0:
            arquivo_prisma.salvar()
        self.pos_processar(cont)

    def processar_checagemsub(self, subcomando: str, args: list[str]) -> None:
        """
        Verifica se o status de cada subtarefa.
        Se concluída, imprime relatório da PM
        e envia tarefa para fase Analise PM
        """
        cont = 0
        protocolo = ''
        subtarefa = ''
        sub_encontrada = False

        self.pre_processar('CHECAR SUBTAREFA')
        for t in self.lista:
            if not t.obter_fase_subtarefa_gerada() or t.obter_fase_pericia_realizada():
                continue
            protocolo = str(t.obter_protocolo())
            subtarefa = str(t.obter_subtarefa())
            print(f'Tarefa {protocolo}...', end=' ')
            if self.get.pesquisar_tarefa(protocolo):
                self.get.abrir_tarefa()
                lista = self.coletar_subtarefas(protocolo, True)
                for item in lista:
                    numsub = item[0]
                    subconcluida = item[1]
                    if numsub == subtarefa:
                        sub_encontrada = True
                        if subconcluida:
                            print('Subtarefa concluída.')
                            t.concluir_fase_pericia_realizada()
                            t.marcar_arquivopdf_pericia()
                        else:
                            print('Subtarefa pendente.')
                if not sub_encontrada:
                    print('Erro: Subtarefa não encontrada.')
                self.get.irpara_iniciotela()
                self.get.fechar_tarefa()
                self.salvar_emarquivo()
                cont += 1
            else:
                print('Erro: Tarefa não foi encontrada.')
        self.pos_processar(cont)

    def processar_exigencia(self, subcomando: str, lista: list[str]) -> None:
        """Cadastra exigência de documentação."""
        cont = 0
        protocolo = ''

        self.pre_processar('GERAR EXIGÊNCIA DE DOCUMENTAÇÃO')
        for t in self.lista:
            print(t.obter_protocolo(), t.tem_dadosbasicos(), t.tem_documentacao(), t.tem_exigencia())
            if not t.tem_dadosbasicos() or t.tem_documentacao() or t.tem_exigencia():
                continue
            protocolo = str(t.obter_protocolo())
            print(f'Tarefa {protocolo}')
            if self.get.pesquisar_tarefa(protocolo):
                #self.get.abrir_tarefa()
                if self.definir_exigencia_simples(t, 'documentacaoPSM'):
                    t.concluir_fase_exigencia(True)
                else:
                    print("Erro ao atribuir exigência.")
                #self.get.fechar_tarefa()
                self.salvar_emarquivo()
                cont += 1
            else:
                print(f'Erro. Tarefa {protocolo} não foi encontrada.')
        self.pos_processar(cont)

    def processar_geracaosubtarefa(self):
        cont = 0        
        protocolo = ''
        dados_adicionais = {}

        self.pre_processar('GERAR SUBTAREFA')
        for t in self.lista:
            if not t.tem_documentacao() or t.obter_fase_subtarefa_gerada():
                continue
            protocolo = str(t.obter_protocolo())
            print(f'Tarefa {protocolo}')
            if self.get.pesquisar_tarefa(protocolo):
                dados_adicionais['nb'] = t.obter_beneficio()
                dados_adicionais['cpf'] = t.obter_cpf()
                self.get.abrir_tarefa()
                if self.gerar_subtarefa(t, dados_adicionais):
                    print(f'Subtarefa gerada.')
                    self.get.fechar_tarefa()
                    self.salvar_emarquivo()
                    cont += 1
                else:
                    print(f'Erro. Subtarefa não gerada.')
            else:
                print(f'Erro. Tarefa {protocolo} não foi encontrada.')
        self.pos_processar(cont)

    def processar_dados(self):
        tamanho = self.base_dados.tamanho
        self.lista.clear()
        for i in range(tamanho):
            tarefa = TarefaProrrogacaoSalMaternidade(self.base_dados, i)
            if not tarefa.obter_fase_conclusao():
                self.lista.append(tarefa)
        self.definir_comandos()
        self.definir_filtros()
        self.definir_listagens()
        self.definir_marcacoes()