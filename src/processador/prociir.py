## Codificado por Douglas Rodrigues de Almeida.
## Junho de 2023
"""Processador para Isenção de IR"""

import pandas as pd
from tarefa import TarefaIsencaoIR
from processador import Processador

colunas_especificas = {
               'tem_pdfagendapmanexo': 'string',
               'tem_exigencia': 'string',
               'tem_documentacao': 'string',
               'subtarefa_coletada': 'string',
               'subtarefaconcluida': 'string',
               'periciarealizada': 'string',
               'beneficio': 'string',
               'atualizacaodespachada': 'string'
              }

datas_especificas = ['vencim_exigencia']

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

        self.dadosparacoletar = ['quantexig', 'quantsub', 'subtarefa']

        #self.dadosparacoletar = ['der', 'cpf', 'quantexig', 'quantsub', 'beneficio', 'subtarefa']

        #TODO Checar depois
        self.criarsub_modolinha = False

        #Lista de tarefas carregadas da base de dados.
        self.lista = [TarefaIsencaoIR]

        self.id = 'iri'
        
        self.id_subtarefa = 'pm_iir'

        self.nome_servico = 'Isenção de Imposto de Renda'

        self.nome_servicopm = ''
        
        self.nome_subservico = 'Análise para Isenção de Imposto de Renda'

        self.base_dados.definir_colunas(colunas_especificas, datas_especificas)

    def __str__(self) -> str:
        resultado = super().__str__()
        resultado += self.obter_info('coletadb', 'Pendentes de coleta de dados: {0} tarefa(s).\n')
        resultado += self.obter_info('analisedoc', 'Pendentes de análise da documentação: {0} tarefa(s).\n')
        
        resultado += self.obter_info('aguardaexig', 'Aguardando cumprimento de exigência: {0} tarefa(s).\n')
        resultado += self.obter_info('exigvencida', 'Com exigência vencida: {0} tarefa(s).\n')

        resultado += self.obter_info('geracaosub', 'Pendentes de geração de subtarefa de PM: {0} tarefa(s).\n')
        resultado += self.obter_info('subcomerro', 'Com erro na geração de subtarefa de PM: {0} tarefa(s).\n')
        resultado += self.obter_info('aguardapm', 'Pendentes de análise da PM: {0} tarefa(s).\n')

        resultado += self.obter_info('sobrestado', 'Sobrestadas: {0} tarefas(s)\n')
        resultado += self.obter_info('impedimentos', 'Com impedimento para concluir: {0} tarefas(s)\n')
        resultado += self.obter_info('conclusao', 'Pendentes de conclusão da tarefa: {0} tarefa(s).\n')
        return resultado

    def alterar_ben(self, subcomando: str, lista: list[str]) -> None:
        beneficio = lista[0]
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

    def definir_filtros(self) -> None:
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
        self.filtros['geracaosub'] = {
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

    def definir_listagens(self) -> None:
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

    def definir_marcacoes(self) -> None:
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