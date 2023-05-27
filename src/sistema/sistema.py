import time
from conversor import Conversor
from datetime import date
from fila import Filas
from gestaometas import GestaoMetas
from impedimentos import Impedimentos
from navegador import Cnis, Get, Pmfagenda
from puxador import Puxador
from processador import ProcessadorAuxAcidente
from processador import ProcessadorAuxIncapacidade
from processador import ProcessadorProrrogSalMaternidade
from processador import ProcessadorIsencaoIR
from processador import ProcessadorSalMaternidade
from variaveis import Variaveis

perfis_disponiveis = {
    'aa': ProcessadorAuxAcidente,
    'psm': ProcessadorProrrogSalMaternidade,
    'ai': ProcessadorAuxIncapacidade,
    'iir': ProcessadorIsencaoIR,
    'sm': ProcessadorSalMaternidade
}

class Sistema:
    def __init__(self) -> None:
        self.getconectado = False

        #Fila aberta
        self.fila_aberta = None

        #Lista de filas disponíveis
        self.filas = None

        #Lista de impedimentos de conclusão
        self.impedimentos = None

        #Data da compilação
        self.datacompilado = '22/05/2023'

        #Versão da aplicação
        self.ver = '1.0.0 protótipo'

        #Automatizador do CNIS
        self.cnis = None

        #Automatizador do GET
        self.get = None

        #Automatizador do PMF Agenda
        self.pmfagenda = None

        #Puxador de Tarefas
        self.puxador = Puxador()

        self.perfil_aberto = ""

        self.processador = None

        self.usarintranet = True

    def abrir_cnis(self, subcomando: str, lista: list[str]) -> None:
        """Abre o navegador Edge e vai para o site do Portal CNIS."""
        self.cnis = Cnis()
        self.cnis.abrir()
        if self.processador_estaaberto():
            self.processador.definir_cnis(self.cnis)

    def abrir_get(self, subcomando: str, lista: list[str]) -> None:
        """Abre o navegador Edge e vai para o site do GET."""
        self.get = Get(False)
        self.get.abrir(self.usarintranet)
        if self.processador_estaaberto():
            self.processador.definir_get(self.get)
        self.puxador.definir_get(self.get)

    def abrir_pmfagenda(self, subcomando: str, lista: list[str]) -> None:
        """Abre o navegador Edge e vai para o site do PMF Agenda."""
        self.pmfagenda = Pmfagenda()
        self.pmfagenda.carregar_dados()
        self.pmfagenda.abrir()
        if self.processador_estaaberto():
            self.processador.definir_pmfagenda(self.pmfagenda)

    def acumula_ben(self, subcomando: str, lista: list[str]) -> None:
        """Analisa a acumulação de benefícios."""
        self.processador.processar_acumulacaoben()

    def adicionar_tarefas(self, subcomando: str, lista: list[str]) -> None:
        """Adiciona uma lista de tarefas a base de dados."""
        self.processador.adicionar_tarefas(lista)

    def agendar_pm(self, subcomando: str, lista: list[str]) -> None:
        """Executa o programa 'Agendar PM' do processador."""
        self.processador.processar_agendamentopm()

    def carregar_dados(self) -> None:
        """Carrega dados utilizados pelo sistema."""
        self.impedimentos = Impedimentos([])
        self.impedimentos.carregar()

        self.filas = Filas([])
        self.filas.carregar()

    def carregar_perfil(self, subcomando: str, lista: list[str]) -> None:
        """Abre o perfil de tarefas do GET especificado."""
        perfil = subcomando
        fila = lista[0]

        nome_fila = perfil + '_' + fila
        if nome_fila == self.perfil_aberto:
            print('Erro: O perfil informado já está aberto.\n')
            return
        if self.getconectado:
            self.processador.driver.fechar()
        print(f'Abrindo {nome_fila}...')
        fila = self.filas.obter(nome_fila)
        if fila is None:
            print('Erro. O perfil informado não existe.\n')
            return
        tipo = fila.get_tipo()
        if tipo in perfis_disponiveis:
            base_dados = fila.carregar()
            self.fila_aberta = fila
            self.processador = perfis_disponiveis[tipo](base_dados)
            self.processador.carregar_fila()
            self.processador.carregar_entidades()
            self.processador.carregar_despachos()
            self.processador.processar_dados()
            self.perfil_aberto = nome_fila
            if self.cnis_estaberto():
                self.processador.definir_cnis(self.cnis)
            if self.get_estaberto():
                self.processador.definir_get(self.get)
            if self.pmfagenda_estaberto():
                self.processador.definir_pmfagenda(self.pmfagenda)
            print("Perfil aberto com sucesso.\n")
            self.exibir_perfil()
            return
        else:
            print('Erro. O perfil informado não é suportado pelo UIP.\n')

    def cnis_estaberto(self) -> bool:
        """Retorna verdadeiro caso o CNIS esteja aberto e autenticado."""
        return self.cnis is not None

    def coletar_db(self, subcomando: str, lista: list[str]) -> None:
        """Executa o programa 'Coletar Dados Básicos' do processador."""
        self.processador.processar_coletadados()
    
    def concluir(self, subcomando: str, lista: list[str]) -> None:
        """Executa o programa 'Concluir Tarefa' do processador."""
        self.processador.processar_conclusao()

    def contar_exig(self, subcomando: str, lista: list[str]) -> None:
        """Conta o número de exigências registradas na tarefa especificada."""
        protocolos = lista
        self.processador.contar_exigencias(protocolos)

    def contar_sub(self, subcomando: str, lista: list[str]) -> None:
        """Conta o número de subtarefas registradas na tarefa especificada."""
        protocolos = lista
        self.processador.contar_subtarefas(protocolos)

    def converter_pdf_txt(self, subcomando: str, lista: list[str]) -> None:
        """Converte arquivos PDF em somente texto."""
        relat = subcomando
        protocolos = lista
        conv = Conversor()
        conv.processar('pdf', 'txt', relat, protocolos)
        print(f'\n{len(protocolos)} processada(s) com sucesso.\n')

    def desimpedir(self, subcomando: str, lista: list[str]) -> None:
        """Remove os impedimentos de conclusão da tarefa especificada."""
        protocolos = lista
        self.processador.processar_desimpedimento(protocolos)

    def desistir(self, subcomando: str, lista: list[str]) -> None:
        """Registr desistência do requerente na tarefa."""
        protocolos = lista
        self.processador.processar_desistencia(protocolos)

    def editar_tarefas(self, subcomando: str, lista: list[str]) -> None:
        """Edita o atributo especificado de uma ou mais tarefas."""
        atributo = subcomando
        valor = lista[0]
        tarefas = lista[1:]
        self.processador.editar_tarefas(atributo, valor, tarefas)

    def exibir_cabecalho(self) -> None:
        """Exibe informações de versão e compilação."""
        print(f'UIP v.{self.ver}')
        print(f'Compilação em {self.datacompilado}\n')

    def exibir_fases(self, subcomando: str, lista: list[str]) -> None:
        """Exibe as fases do fluxo de trabalho para o perfil aberto."""
        self.processador.exibir_fases()

    def exibir_filas(self, subcomando: str, lista: list[str]) -> None:
        """Exibe as filas cadastradas no UIP."""
        print(self.filas)

    def exibir_perfil(self):
        """Exibe o nome do perfil e fila atribuída."""
        print(f'Fila {self.fila_aberta}\n{repr(self.fila_aberta)}')

    def exibir_producao_metas(self, subcomando: str, lista: list[str]) -> None:
        """Exibe a produção e a meta do mês atual."""
        if subcomando == 'atual':
            data_hoje = date.today()
            competencia = f'{data_hoje.month:0>2}/{data_hoje.year}'
        else:
            competencia = subcomando
        gestor_metas = GestaoMetas()
        gestor_metas.carregar_dados()
        gestor_metas.exibir_meta_competencia(competencia)
        gestor_metas.exibir_producao_competencia(competencia)

    def exibir_tarefa(self, subcomando: str, lista: list[str]) -> None:
        """Exibe informações sobre a tarefa especificada."""
        protocolo = lista[0]
        for t in self.processador.lista:
            if protocolo == t.obter_protocolo():
                print(t)
                return
        print("Erro. Tarefa não foi encontrada.\n")

    def exibir_resumo(self, subcomando: str, lista: list[str]) -> None:
        """Exibe o resumo das tarefas do perfil aberto."""
        print(self.processador)

    def get_estaberto(self) -> bool:
        """Retorna verdadeiro caso o GET esteja aberto e autenticado."""
        return self.get is not None

    def gerar_subtarefa(self, subcomando: str, lista: list[str]) -> None:
        """Executa o programa 'Gerar Subtarefa' do processador."""
        self.processador.processar_geracaosubtarefa()

    def impedir(self, subcomando: str, lista: list[str]) -> None:
        """Marca a tarefa especificada com um impedimento para conclusão."""
        impedimento_id = subcomando
        protocolos = lista
        if (impedimento := self.impedimentos.obter(impedimento_id)) is not None:
            self.processador.processar_impedimento(impedimento.id, protocolos)
        else:
            print(f'O impedimento {impedimento_id} não existe.\n')
    
    def listar(self, subcomando: str, sublistas: list[str]) -> None:
        """Exibe uma lista de tarefas de acordo com o filtro especificado."""
        nome_lista = subcomando
        if len(sublistas) > 0:
            sublista = sublistas[0]
        else:
            sublista = None
        listas_disponiveis = self.processador.obter_listagens()         
        if nome_lista in listas_disponiveis.keys():
            (quant, resultado) = self.processador.obter_listagem(nome_lista, sublista)
            print(resultado)
            print(f'\nTotal de itens: {quant}.\n')
        else:
            print(f'Erro. A listagem \'{nome_lista}\' não foi reconhecida.\n')

    def listar_ajuda(self) -> None:
        """Exibe as listagens disponíveis."""
        print("Listas disponíveis:")
        if self.processador is None:
            return
        listas_disponiveis = self.processador.obter_listagens()  
        for chave, item in listas_disponiveis.items():
            desc = item['desc']
            print(f'{chave} - {desc}')
        print('')

    def marcar(self, subcomando: str, lista: list[str]) -> None:
        """Marca a tarefa especificada com uma marcação."""
        marca = subcomando
        marcas_disponiveis = self.processador.obter_marcacoes()
        protocolos = lista          
        if marca in marcas_disponiveis.keys():
            self.processador.marcar(marca, protocolos)
        else:
            print(f'Erro: A marcação \'{marca}\' informada não foi reconhecida.\n')

    def marcar_ajuda(self) -> None:
        """Exibe as marcações de tarefas disponíveis."""
        print('Marcacoes disponíveis:')
        if self.processador is None:
            return
        marcas_disponiveis = self.processador.obter_marcacoes()
        for chave, item in marcas_disponiveis.items():
            desc = item['desc']
            print(f'{chave} - {desc}')

    def mostrar_agenda_pm(self, subcomando: str, lista: list[str]) -> None:
        """Exibe o agendamento de PM da tarefa."""
        self.processador.mostrar_agendapm(lista[0])

    def mostrar_comunicado(self, subcomando: str, lista: list[str]) -> None:
        """Exibe o comunicado de decisão da tarefa especificada."""
        self.processador.mostrar_comunicado(lista[0])

    def mostrar_despacho(self, ssubcomando: str, lista: list[str]) -> None:
        """Exibe o despacho conclusivo da tarefa especificada."""
        self.processador.mostrar_despacho(lista[0])

    def mostrar_impedimentos(self, ssubcomando: str, lista: list[str]) -> None:
        """Exibe os impedimentos de conclusão disponíveis para uso."""
        print(self.impedimentos)

    def obter_comando_doprocessador(self) -> dict:
        if self.processador is None:
            return {}
        return self.processador.obter_comandos()
    
    def pmfagenda_estaberto(self) -> bool:
        """Retorna verdadeiro caso o PMF Agenda esteja aberto e autenticado."""
        return self.pmfagenda is not None
    
    def processador_estaaberto(self) -> bool:
        """Retorna verdadeiro caso exista um processador carregado na memória."""
        return self.processador is not None

    def puxar_tarefa(self, subcomando: str, lista: list[str]) -> bool:
        """Puxa uma tarefa no GET."""
        cont = 0

        if not subcomando.isnumeric():
            print(f'O argumento informado não é um número inteiro válido.\n')
            return        
        quant = int(subcomando)
        if quant == 0:
            print(f'O argumento informado deve ser um número inteiro maior que zero.\n')
            return
        self.puxador.abrir_lista()
        while cont < quant:
            if self.puxador.puxar():
                self.puxador.salvar_lista()
                cont += 1
            else:
                break
            time.sleep(3)
        if cont > 0:
            print(f'{cont} tarefa(s) puxada(s) com sucesso\n')
        else:
            print('Nenhuma tarefa foi puxada.\n')

    def usar_intranet(self, subcomando: str, lista: list[str]) -> None:
        """Altera o parâmetro de uso do GET via intranet ou Internet."""
        if len(lista) == 0:
            if self.usarintranet:
                valor = 'sim'
            else:
                valor = 'não'
            print(f'A confirugação usar_intranet está configurada para {valor}.\n')
            return
        valor = lista[0]
        if valor != 'sim' and valor != 'nao':
            print('Erro. O argumento esperado era \'sim\' ou \'nao\', mas outro arqumento foi informado.\n')
            return
        self.usarintranet = valor == 'sim'
        if valor == 'sim':
            print('Configuração usar_intranet foi alterada para sim.\n')
        else:
            print('Configuração usar_intranet foi alterada para não.\n')