import time
from arquivo import carregar_texto
from conversor import Conversor
from datetime import date
from despacho import Despachos
from fila import Filas
from filtro import Filtros
from gestaometas import GestaoMetas
from impedimento import Impedimentos
from listagem import Listagens
from lote import Lotes
from modelos_exigencias import ListaModelosExigencia
from navegador import Cnis, Get, Pmfagenda, Sibe, SD, Gpa
from puxador import Puxador
from processador import Processador, ProcessadorAposentadoria, ProcessadorAuxAcidente, ProcessadorAuxIncapacidade, ProcessadorBenAssDeficiente, ProcessadorBenAssIdoso, ProcessadorMajoracao25, ProcessadorProrrogSalMaternidade, ProcessadorIsencaoIR, ProcessadorSalMaternidade, ProcessadorSeguroDefeso
from resultado import Resultados

perfis_disponiveis: dict[str, type[Processador]] = {
    'aa': ProcessadorAuxAcidente,
    'ai': ProcessadorAuxIncapacidade,
    'ap': ProcessadorAposentadoria,
    'bpcd': ProcessadorBenAssDeficiente,
    'bpci': ProcessadorBenAssIdoso,
    'iir': ProcessadorIsencaoIR,
    'maj': ProcessadorMajoracao25,
    'psm': ProcessadorProrrogSalMaternidade,
    'sm': ProcessadorSalMaternidade,
    'sd': ProcessadorSeguroDefeso
}

class Sistema:
    def __init__(self) -> None:
        #Data da compilação
        self.datacompilado = '26/09/2023'

        #Versão da aplicação
        self.ver = '1.0.0 protótipo'

        #Despachos
        self.despachos = Despachos([])

        #Fila aberta
        self.fila_aberta = None

        #Lista de filas disponíveis
        self.filas = Filas([])

        #Lista de filtros
        self.filtros = Filtros([])

        #Lista de impedimentos de conclusão
        self.impedimentos = Impedimentos([])

        #Lista de listagens
        self.listagens = Listagens([])

        #Lista de lotes válidos
        self.lotes = Lotes([])

        self.modelos_exigencia = ListaModelosExigencia([])

        self.resultados = Resultados([])

        #Automatizador do CNIS
        self.cnis = None

        #Automatizador do GERID GPA
        self.gpa = None

        #Automatizador do GET
        self.get = None

        #Automatizador do PAT
        self.pat = None

        #Automatizador do PMF Agenda
        self.pmfagenda = None

        #Automatizador do SIBE PU
        self.sibe = None

        #Automatizador do SD
        self.sd = None

        #Puxador de Tarefas
        self.puxador = Puxador()

        self.perfil_aberto = ""

        self.processador = None

        self.usarintranet = True

    def abrir_cnis(self, subcomandos: list[str]) -> None:
        """Abre o navegador Edge e vai para o site do Portal CNIS."""
        self.cnis = Cnis()
        self.cnis.abrir()
        if self.processador is not None:
            self.processador.definir_cnis(self.cnis)

    def abrir_get(self, subcomandos: list[str]) -> None:
        """Abre o navegador Edge e vai para o site do GET."""
        self.get = Get(False)
        self.get.abrir(self.usarintranet)
        if self.fila_aberta is not None:
            if self.get.selecionar_fila(self.fila_aberta.get_codigo()):
                self.get.irpara_pesquisa_protocolo()
        if self.processador is not None:
            self.processador.definir_get(self.get)
        self.puxador.definir_get(self.get)

    def abrir_gpa(self, subcomandos: list[str]) -> None:
        """Abre o navegador Edge e vai para o site do GERID GPA."""
        self.gpa = Gpa()
        self.gpa.abrir()

    def abrir_pmfagenda(self, subcomandos: list[str]) -> None:
        """Abre o navegador Edge e vai para o site do PMF Agenda."""
        self.pmfagenda = Pmfagenda()
        self.pmfagenda.carregar_dados()
        self.pmfagenda.abrir()
        if self.processador is not None:
            self.processador.definir_pmfagenda(self.pmfagenda)

    def abrir_sibe(self, subcomandos: list[str]) -> None:
        """Abre o navegador Edge e vai para o site do SIBE PU."""
        self.sibe = Sibe()
        self.sibe.abrir()
        if self.processador is not None:
            self.processador.definir_sibe(self.sibe)

    def abrir_sd(self, subcomandos: list[str]) -> None:
        """Abre o navegador Edge e vai para o site do SD."""
        self.sd = SD()
        self.sd.abrir()
        if self.processador is not None:
            self.processador.definir_sd(self.sd)

    def acumula_ben(self, subcomandos: list[str]) -> None:
        """Analisa a acumulação de benefícios."""
        if self.processador is None:
            return
        #if len(lista) > 0 and (lista[0] == 'ulp'):
        #    self.processador.coletar_dadosbasicos_lote()
        #else:
        #    self.processador.coletar_dadosbasicos_base()
        self.processador.analisar_acumulaben()

    def adicionar_tarefas(self, subcomandos: list[str]) -> None:
        """Adiciona uma lista de tarefas a base de dados."""
        self.processador.adicionar_tarefas(subcomandos)

    def carregar_dados(self) -> bool:
        """Carrega dados utilizados pelo sistema."""
        if not self.despachos.carregar():
            return False
        if not self.filas.carregar():
            return False
        if not self.filtros.carregar():
            return False
        if not self.impedimentos.carregar():
            return False
        if not self.listagens.carregar():
            return False
        if not self.lotes.carregar():
            return False
        if not self.modelos_exigencia.carregar():
            return False
        if not self.resultados.carregar():
            return False

        return True

    def carregar_perfil(self, subcomandos: list[str]) -> None:
        """Abre o perfil de tarefas do GET especificado."""
        perfil = subcomandos[0]
        nome_fila = perfil + '_' + subcomandos[1]

        if nome_fila == self.perfil_aberto:
            print('Erro: O perfil informado já está aberto.\n')
            return
        print(f'Abrindo {nome_fila}...')
        if self.filas is None:
            return
        fila = self.filas.obter(nome_fila)
        if fila is None:
            print('Erro. O perfil informado não existe.\n')
            return
        else:
            tipo = fila.get_tipo()
        if tipo in perfis_disponiveis:
            base_dados = fila.carregar()
            self.fila_aberta = fila
            self.processador = perfis_disponiveis[tipo](base_dados)
            if not self.processador.carregar_fila():
                return
            self.perfil_aberto = nome_fila
            self.processador.definir_cnis(self.cnis)
            self.processador.definir_get(self.get)
            self.processador.definir_pmfagenda(self.pmfagenda)
            self.processador.definir_sibe(self.sibe)
            self.processador.definir_sd(self.sd)
            self.processador.definir_mod_exigencias(self.modelos_exigencia)
            self.processador.definir_despachos(self.despachos)
            self.processador.definir_filtros(self.filtros)
            self.processador.definir_resultados(self.resultados)
            self.processador.processar_dados()
            print("Perfil aberto com sucesso.\n")
            self.exibir_perfil()
            return
        else:
            print('Erro. O perfil informado não é suportado pelo UIP.\n')
        
    def coletar_ben(self, subcomando: str, lista: list[str]) -> None:
        if self.processador is None:
            return
        if len(lista) > 0 and (lista[0] == 'ulp'):
            self.processador.coletar_dadosbeneficio_lote()
        else:
            self.processador.coletar_dadosbeneficio_base()        

    def coletar_db(self, subcomando: str, lista: list[str]) -> None:
        """Executa o programa 'Coletar Dados Básicos' do processador."""
        if self.processador is None:
            return
        if len(lista) > 0 and (lista[0] == 'ulp'):
            self.processador.coletar_dadosbasicos_lote()
        else:
            self.processador.coletar_dadosbasicos_base()
    
    def concluir(self, subcomandos: list[str]) -> None:
        """Executa o programa 'Concluir Tarefa' do processador."""
        usar_lista = len(subcomandos) > 0 and subcomandos[0] == 'ulp'
        if self.processador is not None:
            self.processador.concluir_tarefa(usar_lista)

    def consultarcpf_ben(self, subcomando: str, lista: list[str]) -> None:
        """aa."""
        cnis = self.cnis
        if cnis is None:
            print('Erro. CNIS não está aberto.')
            return
        usar_lista = len(lista) > 0 and lista[0] == 'ulp'
        if usar_lista:
            lista_cpf = self.obter_listapersonalizada()
            for cpf in lista_cpf:
                cnis.pesquisar_ben_ativos('', cpf, ['25'])

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

    def gpa_cadastrarusuarios(self, subcomandos: list[str]) -> None:
        """a"""
        if self.gpa is None:
            print('Erro: Este comando requer o GERID GPA aberto.')
        else:
            self.gpa.abrir_novo_multiplos_papeis()
            self.gpa.cadastrar_usuario_lista()
            print("\nProcessamento concluído.")

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

    def exibir_lotes(self, subcomando: str, lista: list[str]) -> None:
        """Exibe os lotes válidos disponíveis no UIP."""
        print(self.lotes)

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
            if protocolo == str(t.obter_protocolo()):
                print(t)
                return
        print("Erro. Tarefa não foi encontrada.\n")

    def exibir_resumo(self, subcomandos: list[str]) -> None:
        """Exibe o resumo das tarefas do perfil aberto."""
        print(self.processador)

    def gerar_pa(self, subcomandos: list[str]) -> None:
        """Gerar PA da tarefa"""
        if self.processador is None:
            return
        if len(subcomandos) > 0 and (subcomandos[0]) == 'ulp':
            self.processador.gerar_pa_lote()
        else:
            self.processador.gerar_pa_base()

    def gerar_subtarefa(self, subcomando: str, lista: list[str]) -> None:
        """Executa o programa 'Gerar Subtarefa' do processador."""
        if self.processador is None:
            return
        if len(lista) > 0 and (lista[0] == 'ulp'):
            self.processador.processar_gerarsubtarefa_lote()
        else:
            self.processador.processar_gerarsubtarefa_base()

    def impedir(self, subcomando: str, lista: list[str]) -> None:
        """Marca a tarefa especificada com um impedimento para conclusão."""
        impedimento_id = subcomando
        protocolos = lista
        if (impedimento := self.impedimentos.obter(impedimento_id)) is not None:
            self.processador.processar_impedimento(impedimento, protocolos)
        else:
            print(f'O impedimento {impedimento_id} não existe.\n')

    def juntar_docs(self, subcomandos: list[str]) -> None:
        """Junta documentos da análise."""
        if self.processador is None:
            return
        if len(subcomandos) > 0 and (subcomandos[0] == 'ulp'):
            self.processador.juntar_docs()
        else:
            print('Requer ulp.')
    
    def listar(self, subcomandos: list[str]) -> None:
        """Exibe uma lista de tarefas de acordo com o filtro especificado."""
        nome_lista = subcomandos[0]
        if self.processador is None:
            return
        listagem = self.listagens.obter(nome_lista, self.processador.tags)
        if listagem is None:
            print(f'Erro. A listagem \'{nome_lista}\' não foi reconhecida.\n')
        else:
            filtro = self.filtros.obter(listagem.filtro)
            if filtro is None:
                print(f'Erro. O filtro \'{listagem.filtro}\' não foi reconhecido.\n')
            else:                
                (quant, resultado) = self.processador.listar(listagem, filtro)
                print(resultado)
                print(f'\nTotal de itens: {quant}.\n')            

    def listar_ajuda(self) -> None:
        """Exibe as listagens disponíveis."""
        if self.processador is None:
            return
        _lista = Listagens([])
        for lista in self.listagens:
            if lista.processador in self.processador.tags:
                _lista.adicionar(lista)
        print(_lista)

    def marcar(self, subcomandos: list[str]) -> None:
        """Marca a tarefa especificada com uma marcação."""
        marca = subcomandos[0]
        marcas_disponiveis = self.processador.obter_marcacoes()
        protocolos = subcomandos[1:]
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
    
    def obter_listapersonalizada(self) -> list[str]:
        print("Abrindo lote de protocolos...")
        with carregar_texto('lista_protocolos.txt') as lista:
            if len(lista) == 0:
                print('Erro: Lista com lote de protocolos está vazia.\n')
            return lista    
    
    def processar_lote(self, subcomandos: list[str]) -> None:
        if self.processador is None:
            return
        if self.lotes is not None:
            lote = self.lotes.obter(subcomandos[0])
            if lote is not None:
                self.processador.processar_lote(lote)
            else:
                print('Erro. Lote não encontrado.')

    def puxar_tarefa(self, subcomando: str, lista: list[str]) -> bool:
        """Puxa uma tarefa no GET."""
        cont = 0

        if not subcomando.isnumeric():
            print(f'O argumento informado não é um número inteiro válido.\n')
            return False
        quant = int(subcomando)
        if quant == 0:
            print(f'O argumento informado deve ser um número inteiro maior que zero.\n')
            return False
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
        return True
    
    def registrar_despacho(self, subcomando: str, lista: list[str]) -> None:
        """a"""
        if self.processador is None:
            return
        tipo_despacho = subcomando
        if len(lista) > 0 and (lista[0] == 'ulp'):
            self.processador.registrar_despacho_lote(tipo_despacho)
        else:
            print('Requer ulp.')
    
    def reprocessar_bpc(self, subcomando: str, lista: list[str]) -> None:
        """Reprocessa um lote de BPC com erro de validação PAT-Portal SIBE."""
        if self.pat is None:
            return        

    def usar_intranet(self, subcomandos: list[str]) -> None:
        """Altera o parâmetro de uso do GET via intranet ou Internet."""
        if len(subcomandos) == 0:
            if self.usarintranet:
                valor = 'sim'
            else:
                valor = 'não'
            print(f'A confirugação usar_intranet está configurada para {valor}.\n')
            return
        valor = subcomandos[0]
        if valor != 'sim' and valor != 'nao':
            print('Erro. O argumento esperado era \'sim\' ou \'nao\', mas outro arqumento foi informado.\n')
            return
        self.usarintranet = valor == 'sim'
        if valor == 'sim':
            print('Configuração usar_intranet foi alterada para sim.\n')
        else:
            print('Configuração usar_intranet foi alterada para não.\n')

    def visualizacao_rapida(self, subcomando: str, lista: list[str]) -> None:
        """"""
        if self.processador is None:
            return
        if len(lista) > 0 and (lista[0] == 'ulp'):
            self.processador.visualizar_rapido_lote()