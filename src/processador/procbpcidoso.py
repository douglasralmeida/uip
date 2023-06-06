## Codificado por Douglas Rodrigues de Almeida.
## Junho de 2023
"""Processador para Benefício Assistencial ao Idoso"""

from tarefa import TarefaBenAssIdoso
from processador import Processador

tipocolunas = {'beneficio': 'string',
               'status': 'string',
               'tem_dadosben': 'string',
               'beneficios_anteriores': 'string',
               'especie_anteriores': 'string',
               'status_anteriores': 'string',
               'dib_anteriores': 'string',
               'tem_dadosben': 'string'
}

colunasdata = ['der']

atributos = {
            'dadosben': {'coluna': 'tem_dadosben',
                                   'tipo': 'booleano',
                                   'valores_possiveis': {'sim': '1',
                                                         'nao': '0',
                                                         'vazio': ''
                                                         }
                                  }
            }

class ProcessadorBenAssIdoso(Processador):
    """Classe para o processador de Salário Maternidade."""
    def __init__(self, base_dados):      
        super().__init__(base_dados)
        
        self.atributos = atributos
        
        self.criarsub_modolinha = False
        
        self.dadosparacoletar = []
        
        self.nome_subservico = ''
        
        self.nome_servico = ''
        
        self.id = 'sm'
        
        self.id_subtarefa = ''

        #Lista de tarefas carregadas da base de dados.
        self.lista = [TarefaBenAssIdoso]

        self.base_dados.definir_colunas(tipocolunas, colunasdata)

    def __str__(self) -> str:
        resultado = self.obter_info('coletarben', 'Pendentes de coleta de dados do benefício: {0} tarefa(s).\n')
        resultado += self.obter_info('concluso', 'Com a coleta de dados do benefício processada: {0} tarefa(s).\n')
        
        return resultado

    def definir_comandos(self):
        self.comandos['coletarben'] = {
            'funcao': self.processar_coletaben,
            'argsmin': 0,
            'desc': 'Coleta dados do benefício.',
            'requer_subcomando': False,
            'requer_cnis': True,
			'requer_get': False,
            'requer_pmfagenda': False,
            'requer_protocolo': False,
            'requer_sibe': False,
            'requer_processador': True
        }

    def definir_filtros(self) -> None:
        """Define os filtros relativos de Salário Maternidade de consulta à base de dados."""
        df = self.base_dados.dados
        self.filtros['coletarben'] = {
            'valor': (df['tem_dadosben'].isna())
        }
        self.filtros['concluso'] = {
            'valor': (df['tem_dadosben'] == '1')
        }

    def definir_listagens(self):
        self.listagens['coletarben'] = {
            "desc": "Exibe a lista de tarefas pendentes de coleta de dados do benefício.",
            "filtro": (self.filtros['coletarben']['valor']),
            'colunas': ['protocolo', 'cpf'],
            'ordenacao': ['protocolo'],
            'ordem_crescente': True
        }
        self.listagens['concluso'] = {
            "desc": "Exibe a lista de tarefas com a coleta concluída.",
            "filtro": (self.filtros['concluso']['valor']),
            'colunas': ['protocolo', 'cpf', 'nb'],
            'ordenacao': ['protocolo'],
            'ordem_crescente': True
        }
    
    def definir_marcacoes(self) -> None:
        """Define as marcações que podem ser utilizadas pelo usuário."""
        self.marcacoes['semnome'] = {
            "desc": "Sem descrição."
        }

    def exibir_fases(self) -> None:
        """Exibe as fases do fluxo de trabalho da Tarefa de Sal. Maternidade."""
        print("FASES DO FLUXO DA TAREFA DE SALÁRIO-MATERNIDADE\n")

        print("FASE 1:  Coletar Dados de Benefício\n\tcomando coletarben")


    def processar_coletaben(self, subcomando: str, lista: list[str]) -> None:
        """Processa a coleta de benefícios no Portal CNIS."""
        buffer_linha = ''
        cont = 0
        protocolo = 0

        self.pre_processar('COLETA DE DADOS DE BENEFÍCIO')
        for t in self.lista:
            if t.obter_fase_dadosben():
                continue
            protocolo = t.obter_protocolo()
            cpf = t.obter_cpf()
            buffer_linha = f'Tarefa {protocolo}...'
            print(buffer_linha, end='\r')

            dados = self.cnis.coletar_beneficios(cpf, ['01', '02', '03', '04', '07', '21', '25', '30', '31', '32', '36', '41', '42', '46', '57', '80', '87', '88'])
            if dados['quantidade'] > 0:
                print(f'{buffer_linha}Dados coletados. Beneficio {dados["beneficio"]}.')
                t.alterar_beneficiosanteriores(dados['beneficio'])
                t.alterar_especieanteriores(dados['especie'])
                t.alterar_status(dados['status'])
                t.alterar_dib(dados['dib'])
                t.concluir_fase_dadosben()
            else:
                print(f'{buffer_linha}Dados coletados. Sem benefício.')
                t.concluir_fase_dadosben()
            self.salvar_emarquivo()
            cont +=1
        self.pos_processar(cont)

    def processar_dados(self) -> None:
        """Processa os daods carregados."""
        tamanho = self.base_dados.tamanho
        self.lista.clear()
        for i in range(tamanho):
            tarefa = TarefaBenAssIdoso(self.base_dados, i)
            if not tarefa.obter_fase_conclusao():
                self.lista.append(tarefa)
        self.definir_comandos()
        self.definir_filtros()
        self.definir_listagens()
        self.definir_marcacoes()