## Codificado por Douglas Rodrigues de Almeida.
## Março de 2023
"""Processador para Auxílio por Incapacidade Temporária"""

import pandas as pd
from tarefa import TarefaAuxilioIncapacidade
from processador import Processador

colunas_especificas = {'tem_agendapm': 'string',
               'tem_pdfagendapmanexo': 'string',
               'horaagendamento': 'string',
               'localagendamento': 'string',
               'tem_pdfagendapmanexo': 'string',
               'tem_exigencia': 'string',
               'tem_documentacao': 'string',
               'periciacumprida': 'string',
               'periciarealizada': 'string',
               'beneficio': 'string',
               'beneficiodespachado': 'string'
              }

datas_especificas = ['dataagendamento']

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
            'beneficio':    {'coluna': 'beneficio',
                             'tipo': 'inteiro'
                            }
            }

class ProcessadorAuxIncapacidade(Processador):
    """Classe para o processador de Auxílio por Incapacidade Temporária."""
    def __init__(self, base_dados) -> None:
        super().__init__(base_dados)

        self.atributos = atributos

        self.dadosparacoletar = ['der', 'nit', 'cpf', 'quantexig', 'quantsub']

        #TODO Checar depois
        self.criarsub_modolinha = False

        #Lista de tarefas carregadas da base de dados.
        self.lista = [TarefaAuxilioIncapacidade]

        self.id = 'ai'
        
        self.id_subtarefa = 'pm_ai'

        self.nome_servico = 'Auxílio por Incapacidade Temporária'

        self.nome_servicopm = ''
        
        self.nome_subservico = ''

        self.base_dados.definir_colunas(colunas_especificas, datas_especificas)

    def __str__(self) -> str:
        resultado = super().__str__()
        resultado += self.obter_info('coletadb', 'Pendentes de coleta de dados: {0} tarefa(s).\n')
        resultado += self.obter_info('analisedoc', 'Pendentes de análise da documentação: {0} tarefa(s).\n')
        resultado += self.obter_info('aguardaexig', 'Aguardando cumprimento de exigência: {0} tarefa(s).\n')
        resultado += self.obter_info('exigvencida', 'Com exigência vencida: {0} tarefa(s).\n')
        resultado += self.obter_info('sobrestado', 'Sobrestadas: {0} tarefas(s)\n')
        resultado += self.obter_info('impedimentos', 'Com impedimento para concluir: {0} tarefas(s)\n')
        resultado += self.obter_info('conclusao', 'Pendentes de conclusão da tarefa: {0} tarefa(s).\n')
        return resultado

    def anexar_pdf_pm(self, tarefa: TarefaAuxilioIncapacidade) -> None:
        """Adiciona o PDF do agendamento da perícia na tarefa."""
        num_tarefa = tarefa.obter_protocolo()
        arquivo_pdf = num_tarefa + " - AgendaPM.pdf"
        if self.adicionar_anexo([arquivo_pdf])[0]:
            tarefa.alterar_fase_pdfagendapm_anexo()
        else:
            print("Erro ao anexar arquivo PDF do agendamento da PM.")

    def alterar_ben(self, subcomando: str, lista: list[str]) -> None:
        beneficio = lista[0]
        idx = self.base_dados.pesquisar_indice(lista[1])
        if idx is None:
            print('Tarefa não encontrada.\n')
            return
        t = TarefaAuxilioIncapacidade(self.base_dados, idx)
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
            'requer_sibe': False
        }

    def definir_filtros(self) -> None:
        """Define os filtros relativos a Auxílio por Incapacidade de consulta à base de dados"""
        df = self.base_dados.dados
        super().definir_filtros()
        self.filtros['analisedoc'] = {
            'valor': (df['tem_dadosbasicos'] == '1') & (df['tem_documentacao'].isna() & (df['impedimentos'].isna()))
        }
        self.filtros['aguardapm'] = {
            'valor': (df['tem_agendapm'] == '1') & (df['periciacumprida'].isna()) 
        }
        self.filtros['aguardaexig'] = {
            'valor': (df['tem_exigencia'] == '1') & (df['data_exigencia'] >= pd.to_datetime('today').floor('D'))
        }
        self.filtros['exigvencida'] = {
            'valor': (df['tem_exigencia'] == '1') & (df['data_exigencia'] < pd.to_datetime('today').floor('D'))
        }

    def definir_listagens(self) -> None:
        """Define as listagens relativas a Auxílio por Incapacidade."""
        super().definir_listagens()
        self.listagens['analisedoc'] = {
            "desc": "Exibe a lista de tarefas pendentes de análise da documentação.",
            "filtro": (self.filtros['analisedoc']['valor']),
            'colunas': ['protocolo', 'der'],
            'ordenacao': ['der'],
            'ordem_crescente': True
        }
        self.listagens['aguardapm'] = {
            "desc": "Exibe a lista de tarefas pendentes de perícia médica.",
            "filtro": (self.filtros['aguardapm']['valor']),
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
        """Define as marcações relativas a Auxílio por Incapacidade."""
        self.marcacoes['cumpriuexig'] = {
            "desc": "Marca a tarefa como exigência cumprida."
        }
        self.marcacoes['deferido'] = {
            "desc": "Marca a tarefa com o benefício deferido."
        }
        self.marcacoes['semcarenciareing'] = {
            "desc": "Marca a tarefa com o benefício indeferido por falta de carência no reingresso."
        }
        self.marcacoes['naosegurado'] = {
            "desc": "Marca a tarefa com o benefício indeferido por falta de qualidade de segurado."
        }
        self.marcacoes['pmindefere'] = {
            "desc": "Marca a tarefa com o benefício indeferido por PM contrária."
        }
        self.marcacoes['semresumo'] = {
            "desc": "Marca a tarefa com a informação de ausência de resumo em PDF."
        }

    def marcar(self, marca: str, protocolos: list[str]) -> None:
        """Marca a lista de tarefas com a marcação especificada."""
        cont = 0
        if marca == 'semresumo':
            self.pre_processar('MARCAR SEM RESUMO EM PDF')
        if marca == 'cumpriuexig':
            self.pre_processar('MARCAR EXIGÊNCIA CUMPRIDA')
        if marca == 'deferido':
            self.pre_processar('MARCAR BENEFÍCIOS DEFERIDOS')
        if marca in ['semcarenciareing', 'naosegurado']:
            self.pre_processar('MARCAR BENEFÍCIOS INDEFERIDOS')
        for protocolo in protocolos:
            idx = self.base_dados.pesquisar_indice(protocolo)
            if idx is None:
                print(f'Tarefa {protocolo} não encontrada.')
                continue
            print(f'Tarefa {protocolo}')
            tarefa = TarefaAuxilioIncapacidade(self.base_dados, idx)
            if marca == 'cumpriuexig':
                if tarefa.tem_exigencia():
                    tarefa.cumprir_exigencia()
                cont += 1
            elif marca == 'deferido':
                if tarefa.tem_exigencia():
                    tarefa.cumprir_exigencia()
                tarefa.alterar_beninacumluavel(False)
                tarefa.alterar_temdoc(True)
                tarefa.alterar_pdfresumo(True)
                tarefa.concluir_fase_pericia_realizada()
                tarefa.concluir_fase_pericia_cumprida()
                tarefa.concluir_fase_benef_despachado()
                tarefa.alterar_resultado('b31Deferido')
                tarefa.concluir_fase_concluso()
                cont += 1
            elif marca == 'semcarenciareing':
                if tarefa.tem_exigencia():
                    tarefa.cumprir_exigencia()
                tarefa.alterar_beninacumluavel(False)
                tarefa.alterar_temdoc(True)
                tarefa.alterar_pdfresumo(False)
                tarefa.concluir_fase_pericia_realizada()
                tarefa.concluir_fase_pericia_cumprida()
                tarefa.concluir_fase_benef_despachado()
                tarefa.alterar_resultado('b31SemCarReing')
                tarefa.concluir_fase_concluso()
                cont += 1
            elif marca == 'naosegurado':
                if tarefa.tem_exigencia():
                    tarefa.cumprir_exigencia()
                tarefa.alterar_beninacumluavel(False)
                tarefa.alterar_temdoc(True)
                tarefa.alterar_pdfresumo(False)
                tarefa.concluir_fase_pericia_realizada()
                tarefa.concluir_fase_pericia_cumprida()
                tarefa.concluir_fase_benef_despachado()
                tarefa.alterar_resultado('b31NaoSegurado')
                tarefa.concluir_fase_concluso()
                cont += 1
            elif marca == 'pmindefere':
                if tarefa.tem_exigencia():
                    tarefa.cumprir_exigencia()
                tarefa.alterar_beninacumluavel(False)
                tarefa.alterar_temdoc(True)
                tarefa.alterar_pdfresumo(False)
                tarefa.concluir_fase_pericia_realizada()
                tarefa.concluir_fase_pericia_cumprida()
                tarefa.concluir_fase_benef_despachado()
                tarefa.alterar_resultado('b31PMContraria')
                tarefa.concluir_fase_concluso()
                cont += 1
            elif marca == 'semresumo':
                tarefa.alterar_pdfresumo(False)
                cont += 1
            self.salvar_emarquivo()            
        self.pos_processar(cont)

    def processar_dados(self) -> None:
        """Processa os daods carregados."""
        tamanho = self.base_dados.tamanho
        self.lista.clear()
        for i in range(tamanho):
            tarefa = TarefaAuxilioIncapacidade(self.base_dados, i)
            if not tarefa.obter_fase_conclusao():
                self.lista.append(tarefa)
        self.definir_comandos()
        self.definir_filtros()
        self.definir_listagens()
        self.definir_marcacoes()
    
    def processar_subtarefa(self, tarefa) -> None:
        """"""
        numsub, subconcluida = self.coletar_subtarefa()
        if len(numsub) > 0:
            tarefa.alterar_subtarefa(numsub)
            tarefa.concluir_fase_subtarefa()
            if subconcluida:
                tarefa.alterar_fase_agendapm()
                tarefa.alterar_fase_pdf_agendapmanexo()
                tarefa.alterar_fase_possui_exigencia()
                tarefa.alterar_fase_pericia_cumprida()
                tarefa.alterar_fase_pericia_realizada()