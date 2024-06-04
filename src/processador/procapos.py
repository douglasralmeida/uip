## Codificado por Douglas Rodrigues de Almeida.
## Dezembro de 2023
"""Processador para Aposentadoria"""

import pandas as pd
from arquivo import carregar_texto
from .procben import ProcessadorBeneficio
from arquivo import ArquivoPrismaEntrada
from conversor import Conversor
from os import path
from tarefa import TarefaBeneficio
from variaveis import Variaveis

datas_especificas = []

atributos = {
}

class ProcessadorAposentadoria(ProcessadorBeneficio):
    """Classe para o processador de Aposentadoria."""
    def __init__(self, base_dados) -> None:
        super().__init__(base_dados)
        
        self.atributos = atributos
        
        self.criarsub_modolinha = True
        
        self.dadosparacoletar = ['der', 'cpf', 'quantsub']

        self.especies_acumulaveis = ['21', '93']
        
        self.id_subtarefa = 'pm_ae'

        #Lista de tarefas carregadas da base de dados.
        #self.lista: list[TarefaAposentadoria] = []        

        self.nome_servico = 'Aposentadoria'

        self.nome_servicopm = ''
        
        self.nome_subservico = 'Análise de Atividade Especial - Perícia Médica'

        #Tag para benefício
        self.tags.append('ap')
        
        self.base_dados.definir_colunas(datas_especificas)
       
    def __str__(self) -> str:
        resultado = super().__str__()

        resultado += f"Pendentes de coleta de dados: {self.obter_info('coletadb')} tarefa(s).\n"
        return resultado
        
    def definir_comandos(self) -> None:
        """Define os comandos exclusivos deste processador."""
        self.comandos['gerarae'] = {
            'funcao': self.processar_gerarsub_ae,
            'argsmin': 0,
            'desc': 'NONONO.',
            'requer_subcomando': True,
            'requer_cnis': False,
			'requer_get': True,
            'requer_processador': True,
            'requer_pmfagenda': False,
            'requer_protocolo': False,
            'requer_sibe': False,
            'requer_sd': False
        }
        self.comandos['coletarsub'] = {
            'funcao': self.processar_coletarsub_ae,
            'argsmin': 0,
            'desc': 'NONONO.',
            'requer_subcomando': True,
            'requer_cnis': False,
			'requer_get': True,
            'requer_processador': True,
            'requer_pmfagenda': False,
            'requer_protocolo': False,
            'requer_sibe': False,
            'requer_sd': False
        }

    def _definir_listagens(self) -> None:
        """Define as listagens relativas a Auxílio Acidente."""
        super().definir_listagens()

    def definir_marcacoes(self) -> None:
        """Define as marcações relativas a Auxílio Acidente."""
        pass

    def exibir_fases(self) -> None:
        print("FASES DO FLUXO DA TAREFA DE APOSENTADORIA\n")

        print("FASE 1:  Coletar Dados Básicos\n\tcomando coletardb")

    def processar_dados(self) -> None:
        """Processa os daods carregados."""
        tamanho = self.base_dados.tamanho
        self.lista.clear()
        self.definir_comandos()
        self.definir_marcacoes()

    ##== COLETAR SUB PM AE ==#
    def processar_coletarsub_ae(self, subcomando: str, lista: list[str]) -> None:
        cont = 0
        self.pre_processar('COLETAR SUBTAREFA PM AE')
        print("Usando lista personalizada.")

        for item in self.obter_listapersonalizada():
            if self.processar_coletar_subpm(item):
                cont += 1
        self.pos_processar(cont)

    def processar_coletar_subpm(self, tarefa: str) -> None:
        """Coletar sub PM"""
        buffer_linha = ''
        necessario_fechartarefa = False
        get = self.get
        protocolo = ''

        if get is None:
            return None

        protocolo = tarefa
        buffer_linha = f'Tarefa {protocolo}...'
        print(buffer_linha, end='\r')

        #Pesquisa a tarefa no GET
        if get.pesquisar_tarefa(protocolo):

            #Verifica se tarefa está cancelada/concluída
            (status, data) = get.checar_concluida()
            if status in ['Cancelada', 'Concluída']:
                print(buffer_linha + 'Concluída/Cancelada. Subtarefa não foi coletada.')
                return None

            #Abre a tarefa no GET
            get.abrir_tarefa()
            necessario_fechartarefa = True

            #Verifica já existe subtarefa gerada e a coleta
            subtarefas = get.coletar_subtarefas_canceladas('Análise Processual de Exposição a Ag. Nocivos para Fins de Conversão de Tempo Especial')
            if len(subtarefas) > 0:
                with carregar_texto('arquivo_saida.txt') as lista:
                    print(buffer_linha + f'Subtarefas: {subtarefas}.')
                    lista.append(subtarefas)
                    nome_arquivo = path.join(Variaveis.obter_pasta_entrada(), 'arquivo_saida.txt')
                    with open(nome_arquivo, 'w') as arquivo:
                        arquivo.writelines('\n'.join(lista))
            else:
                print(buffer_linha + 'Sem subtarefa.')                
            if necessario_fechartarefa:
                get.fechar_tarefa()
            self.salvar_emarquivo()
        else:
            print(buffer_linha + 'Erro: Tarefa não foi encontrada.')

    ##== GERAR SUB AE ==##

    def processar_gerarsub_ae(self, subcomando: str, lista: list[str]) -> None:
        cont = 0
        self.pre_processar('GERAR SUBTAREFA AE')
        print("Usando lista personalizada.")

        for item in self.obter_listapersonalizada():
            if self.processar_gerar_sub(item):
                cont += 1
        self.pos_processar(cont)

    def processar_gerar_sub(self, tarefa: str) -> None:
        """Gera subtarefa nas tarefas pendentes de geração de subtarefa."""
        buffer_linha = ''
        necessario_fechartarefa = False
        get = self.get
        protocolo = ''

        if get is None:
            return None

        protocolo = tarefa
        buffer_linha = f'Tarefa {protocolo}...'
        print(buffer_linha, end='\r')

        #Pesquisa a tarefa no GET
        if get.pesquisar_tarefa(protocolo):

            #Verifica se tarefa está cancelada/concluída
            (status, data) = get.checar_concluida()
            if status in ['Cancelada', 'Concluída']:
                print(buffer_linha + 'Concluída/Cancelada. Subtarefa não foi gerada.')
                return None

            #Abre a tarefa no GET
            get.abrir_tarefa()
            necessario_fechartarefa = True

            #Verifica já existe subtarefa gerada e a coleta
            lista = get.coletar_subtarefa(self.nome_subservico)
            if lista[0] != 0:
                print(buffer_linha + 'Subtarefa coletada.')
            else:
                #Cria a subtarefa
                res = get.gerar_subtarefa(self.nome_subservico, self.id_subtarefa, {})
                if res['sucesso']:
                    num_novasub = res['numerosub'][0]
                    print(buffer_linha + 'Subtarefa gerada.')
                else:
                    #Erro na geração de sub. Registra.
                    print(buffer_linha + 'Subtarefa não foi gerada.')
                    necessario_fechartarefa = False
            if necessario_fechartarefa:
                get.fechar_tarefa()
            self.salvar_emarquivo()
        else:
            print(buffer_linha + 'Erro: Tarefa não foi encontrada.')
