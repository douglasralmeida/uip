## Codificado por Douglas Rodrigues de Almeida.
## Junho de 2023
"""Processador base do UIP"""

import pandas as pd
from agendamento import Agendamento
from arquivo import carregar_dados
from basedados import BaseDados
from navegador import Cnis, Get, Pmfagenda
from os import path
from tarefa import Tarefa
from variaveis import Variaveis

ARQUIVO_EXIGENCIAS = 'exigencias.json'

ARQUIVO_DESPACHOS = 'despachos.json'

RES_SUBTAREFA_ERRO = 0

RES_SUBTAREFA_GERADA = 1

RES_SUBTAREFA_COLETADA = 2

colunas_padrao = {'protocolo': 'string',
                  'tem_dadosbasicos': 'string',
                  'cpf': 'string',
                  'nit': 'string',
                  'tem_prim_subtarefa': 'string',
                  'tem_prim_exigencia': 'string',
                  'ms': 'string',
                  'possui_ben_inacumulavel': 'string',
                  'tem_subtarefa': 'string',
                  'subtarefa': 'string',
                  'tem_exigencia': 'string',
                  'subtarefacancelada': 'string',
                  'nb_inacumulavel': 'string',
                  'especie_inacumulavel': 'string',   
                  'tem_pdfresumoanexo': 'string',
                  'resultado': 'string',
                  'impedimentos': 'string',
                  'concluso': 'string',
                  'concluida': 'string',
                  'obs': 'string'
              }

#datas_padrao = []

datas_padrao = ['der', 'data_subtarefa', 'data_exigencia', 'data_conclusao', 'vencim_exigencia']

class Processador:
    """Classe base para o processador do UIP."""
    def __init__(self, base_dados: BaseDados) -> None:
        #Objeto da base de dados
        self.base_dados = base_dados

        #Objeto do Automatizador do Portal CNIS.
        self.cnis = None

        #Comandos disponíveis para o usuário.
        self.comandos = {}

        #Dados coletados no processo Coleta de Dados Básicos.
        self.dadosparacoletar = []

        #Informa se a fila foi aberta.
        self.fila_aberta = False

        #Filtros diponíveis para pesquisa.
        self.filtros = {}

        #Objeto do Automatizador do GET.
        self.get = None

        #Lista de impedimentos para conclusão de tarefa.
        self.impedimentos = None

        #Lista de tarefas carregadas da base de dados.
        self.lista = [Tarefa]

        #Listagens disponíveis para o usuário.
        self.listagens = {}

        #Marcações disponíveis para o usuário.
        self.marcacoes = {}

        #Objeto do Automatizador do PMF Agenda.
        self.pmfagenda = None

        #Colunas e tipos de dados 'Data' padrão para todas filas.
        self.base_dados.definir_colunas(colunas_padrao, datas_padrao)

    def __str__(self) -> None:
        quant_tarefas = len(self.lista)
        resultado = f'TAREFAS DE {self.nome_servico.upper()}\n'
        linha = ''.join(['=' for _ in resultado])
        resultado += linha
        resultado += f'\nTotal: {quant_tarefas} tarefa(s)\n'
        return resultado

    def adicionar_anexo(self, arquivos: list[str]) -> list[bool]:
        """Anexa os arquivos especificados na tarefa do GET."""
        nav = self.get
        resultados = []

        nav.irpara_iniciotela()
        nav.abrir_guia('Anexos')
        nav.irpara_finaltela()
        for arquivo in arquivos:
            arquivopdf = path.join(Variaveis.obter_pasta_pdf(), arquivo)

            ## Checar se arquivo existe
            if path.exists(arquivopdf):
                nav.clicar_botao('formDetalharTarefa:detalheTarefaTabView:btnIncluirAnexo')
                nav.adicionar_anexo(arquivopdf)
                resultados.append(True)
            else:
                resultados.append(False)
        return resultados
    
    def adicionar_tarefas(self, protocolos: list[str]) -> None:
        """Adiciona uma lista de tarefas a base de dados."""
        self.base_dados.adicionar_registros(protocolos)
        self.salvar_emarquivo()
        print("\nInclusões processadas com sucesso.\n")
     
    def carregar_despachos(self) -> None:
        """Carrega os despachos"""
        with carregar_dados(ARQUIVO_EXIGENCIAS) as dados:
            self.exigencias = dados
        with carregar_dados(ARQUIVO_DESPACHOS) as dados:
            self.despachos = dados

    def carregar_entidades(self) -> None:
        """Carrega pessoas"""
        pass
        
    def carregar_fila(self) -> None:
        self.fila_aberta = self.base_dados.carregar_dearquivo()

    def coletar_subtarefas(self, protocolo: str, imprimirpdf: bool) -> list[tuple[str, bool]]:
        """Coleta as subtarefas no GET."""
        nav = self.get

        nav.abrir_guia('Subtarefas')
        nav.irpara_finaltela()
        return nav.coletar_subtarefas(protocolo, self.nome_subservico, imprimirpdf)

    def contar_exigencias(self, protocolos: list[str]) -> None:
        """Conta a quantidade de exigências das tarefas especificadas."""
        cont = 0
        self.pre_processar('CONTAR EXIGÊNCIAS')
        for p in protocolos:
            if self.get.pesquisar_tarefa(p):
                self.get.abrir_tarefa()
                cont = self.get.contar_exigencias()
                self.get.fechar_tarefa()
                print(f'Tarefa {p:<12} {cont}')
            else:
                print(f'Tarefa {p:<12} não encontrada.')

    def contar_subtarefas(self, protocolos: list[str]) -> None:
        """Conta a quantidade de subtarefas das tarefas especificadas."""
        cont = 0
        self.pre_processar('CONTAR SUBTAREFAS')
        for p in protocolos:
            if self.get.pesquisar_tarefa(p):
                self.get.abrir_tarefa()
                self.get.abrir_guia('Subtarefas')
                cont = self.get.contar_subtarefas()
                self.get.fechar_tarefa()
                print(f'Tarefa {p:<12} {cont}')
            else:
                print(f'Tarefa {p:<12} não encontrada.')

    def concluir_tarefa(self, numero: str, texto: str) -> dict:
        """Conclui a tarefa especificada no GET."""
        nav = self.get

        nav.irpara_iniciotela()
        nav.clicar_botao('formDetalharTarefa:detalhe_concluir')
        nav.aguardar_telaprocessamento()
        return nav.concluir_tarefa(numero, texto)
    
    def definir_cnis(self, nav: Cnis) -> None:
        """a"""
        self.cnis = nav

    def definir_exigencia_pm(self, agendamento: Agendamento) -> None:
        """Cadastra uma exigência na tarefa com o agendameto da PM."""
        texto = self.obter_textoexigencia("agendamentoPM")
        local = agendamento.obter_local()
        return self.get.definir_exigencia(texto.format(str(agendamento), local))

    def definir_exigencia_simples(self, tarefa: Tarefa, codigo_exig: str) -> None:
        """Cadastra uma exigência na tarefa"""
        texto = self.obter_textoexigencia(codigo_exig)
        return self.get.definir_exigencia(texto)

    def definir_filtros(self) -> None:
        """Define os filtros básicos de consulta à base de dados"""
        df = self.base_dados.dados
        filto_sem_imp_conc = df['impedimentos'].isna() & df['concluso'].isna() & df['sub_sobrestado'].isna()

        self.filtros['tudo'] = {
            'valor': df['concluida'].isna()
        }
        self.filtros['coletadb'] = {
            'valor': df['tem_dadosbasicos'].isna() & ~df['resultado'].isin(['desistencia']) & filto_sem_imp_conc
        }
        self.filtros['sobrestado'] = {
            'valor': df['sub_sobrestado'].notna()
        }
        self.filtros['impedimentos'] = {
            'valor': df['impedimentos'].notna()
        }
        self.filtros['conclusao'] = {
            'valor': (df['concluso'] == '1') & df['concluida'].isna() & df['impedimentos'].isna() & df['sub_sobrestado'].isna()
        }

    def definir_listagens(self) -> None:
        """Define as listagens básicas"""
        self.listagens['tudo'] = {
            "desc": "Exibe a lista de tarefas não concluídas.",
            "filtro": self.filtros['tudo']['valor'],
            'colunas': ['protocolo'],
            'ordenacao': ['der'],
            'ordem_crescente': True
        }
        self.listagens['coletadb'] = {
            'desc': 'Exibe a lista de tarefas pendentes de coleta de dados básicos.',
            'filtro': self.filtros['coletadb']['valor'],
            'colunas': ['protocolo'],
            'ordenacao': ['der'],
            'ordem_crescente': True
        }
        self.listagens['sobrestado'] = {
            "desc": "Exibe a lista de tarefas sobrestadas.",
            "filtro": (self.filtros['sobrestado']['valor']),
            'colunas': ['protocolo', 'sub_sobrestado'],
            'ordenacao': ['der'],
            'ordem_crescente': True
        }
        self.listagens['conclusao'] = {
            "desc": "Exibe a lista de tarefas com benefício despachado aguardando conclusão da tarefa.",
            "filtro": (self.filtros['conclusao']['valor']),
            'colunas': ['protocolo', 'der', 'resultado'],
            'ordenacao': ['der'],
            'ordem_crescente': True
        }
        self.listagens['impedimentos'] = {
            "desc": "Exibe a lista de tarefas com impedimentos para conclusão.",
            "filtro": (self.filtros['impedimentos']['valor']),
            'colunas': ['protocolo', 'der', 'impedimentos'],
            'ordenacao': ['der'],
            'ordem_crescente': True
        }

    def definir_get(self, nav: Get) -> None:
        """a"""
        self.get = nav
        self.get.alterar_modolinha(self.criarsub_modolinha)

    def definir_pmfagenda(self, nav: Pmfagenda) -> None:
        """Define o automatizador do PMF Agenda."""
        self.pmfagenda = nav

    def editar_tarefas(self, atributo: str, valor: str, protocolos: list[str]) -> None:
        """Edita uma lista de tarefas"""
        if atributo == '?':
            print("Atributos passíveis de edição:")
            for atr, _ in self.atributos.items():
                print(atr)
            return
        if atributo in self.atributos.keys():
            if (tipo := self.atributos[atributo]['tipo']) == 'booleano':
                if valor in (valores := self.atributos[atributo]['valores_possiveis']).keys():
                    valor_dado = valores[valor]
                else:
                    print(f'Erro: O valor \'{valor}\' não foi reconhecido como um valor válido para o atributo \'{atributo}\'.\n')
                    return
            elif tipo == 'data':
                valor_dado = pd.to_datetime(valor, dayfirst=True, format='%d/%m/%Y')
            elif tipo == 'texto':
                valor_dado = valor
            elif tipo == 'inteiro':
                if valor.isnumeric():
                    if atributo in ['beneficio', 'nb_inacumulavel']:
                        valor_dado = f'{valor[0:3]}.{valor[3:6]}.{valor[6:9]}-{valor[9]}'
                    else:
                        valor_dado = valor
                else:
                    print(f'Erro: O valor \'{valor}\' não foi reconhecido como um valor de número inteiro válido.\n')
                    return
            if valor_dado == '':
                valor_dado = pd.NA
            for protocolo in protocolos:
                if self.base_dados.alterar_atributos(protocolo, [self.atributos[atributo]['coluna']], [valor_dado]):
                    print(f'Tarefa {protocolo} foi alterda.')
                else:
                    print(f'Tarefa {protocolo} não foi alterda.')
            self.salvar_emarquivo()
            print('\n')
            return
        else:            
            print(f'Erro: O atributo \'{atributo}\' não foi reconhecido como um atributo editável válido.\n')
            return

    def gerar_subtarefa(self, tarefa: Tarefa, dados_adicionais: dict) -> tuple[bool, bool]:
        """
        Gera a subtarefa obrigatória da tarefa especificada.
        Primeiro valor booleano indica que a subtarefa foi coletada ou gerada.
        Segundo valor booleano indica que a subtrarefa foi coletada.
        """
        res = self.get.gerar_subtarefa(self.nome_subservico, self.id_subtarefa, dados_adicionais)
        if res['sucesso']:
            tarefa.alterar_subtarefa_coletada(False)
            tarefa.alterar_subtarefa(res['numerosub'][0])
            tarefa.concluir_fase_subtarefa()
            return True
        else:
            tarefa.alterar_msg_criacaosub(res['mensagem'])
        return False
    
    def obter_comandos(self) -> dict:
        """Retorna os comandos exclusivos do processador."""
        return self.comandos

    def obter_dados_comfiltro(self, filtro: str):
        """Retorna um conjunto de dados com filtro aplicado."""
        return self.base_dados.obter_dados(self.filtros[filtro]['valor'])
    
    def obter_info(self, filtro: str, texto: str) -> int:
        """Retorna a quantidade de registros retornados na pesquisa com filtro."""
        dd = self.obter_dados_comfiltro(filtro)
        return texto.format(len(dd))
    
    def obter_listagem(self, nome: str, sublista: list[str]) -> tuple[int, str]:
        """Retorna uma lista de tarefas."""
        listagem = self.listagens[nome]
        return self.base_dados.obter_lista(listagem)

    def obter_listagens(self):
        """Retorna as listagems disponíveis."""
        return self.listagens
    
    def obter_marcacoes(self):
        """Retorna as marcações disponíveis."""
        return self.marcacoes
    
    def obter_textoconclusao(self, idx: int, tipo: str) -> str:
        """Retorna o texto do comunicado de conclusão especificado."""
        texto_modelo = self.despachos['dados'][tipo]['conclusao']
        vars_necessarias = self.despachos['dados'][tipo]['conclusao_vars'].split(' ')
        variaveis = {}
        for var in vars_necessarias:
            variaveis[var] =  self.base_dados.obter_atributo(idx, var)
        return texto_modelo.format(**variaveis)    
    
    def obter_textodespacho(self, idx: int, tipo: str) -> str:
        """Retorna o texto do despacho especificado."""
        texto_modelo = self.despachos['dados'][tipo]['despacho']
        vars_necessarias = self.despachos['dados'][tipo]['despacho_vars'].split(' ')
        variaveis = {}
        for var in vars_necessarias:
            variaveis[var] =  self.base_dados.obter_atributo(idx, var)
        return texto_modelo.format(**variaveis)
    
    def obter_textoexigencia(self, tipo: str) -> str:
        """Retorna o texto para geração de exigência especificado."""
        return self.exigencias['dados'][tipo]['texto']
    
    def marcar_resultado(self, tarefa: Tarefa, resultado: str) -> bool:
        """Salva o resultado na lista de tarefas especificada."""
        resultado_existe = False
        for resultados_disponiveis in self.despachos.keys():
            if resultado == resultados_disponiveis:
                resultado_existe = True
                break
        if resultado_existe:
            tarefa.alterar_resultado(resultado)
            return True
        else:
            return False
        
    def mostrar_agendapm(self, protocolo: str) -> None:
        """Exibe a agenda de PM se houver."""
        if (idx := self.base_dados.pesquisar_indice(protocolo)) == None:
            print(f'Erro: Tarefa {protocolo} não foi encontrada.\n')
            return
        t = Tarefa(self.base_dados, idx)
        if (ag := t.obter_agendamento()) is None:
            print('Tarefa sem agendamento registrado.\n')
        else:
            print(f'{self.nome_subservico}')
            print(f'Agendamento para: {ag}.')
            print(f'Endereço: {ag.local}\n')
        
    def mostrar_comunicado(self, protocolo: str) -> None:
        """Exibe o comunicado de conclusão para a tarefa especificada."""
        if (idx := self.base_dados.pesquisar_indice(protocolo)) == None:
            print(f'Erro: Tarefa {protocolo} não foi encontrada.\n')
            return
        resultado = self.base_dados.obter_atributo(idx, 'resultado')
        if pd.isna(resultado):
            print(f'Erro: Tarefa {protocolo} ainda não possui resultado registrado.\n')
            return
        texto = self.obter_textoconclusao(idx, resultado)
        print(texto)
    
    def mostrar_despacho(self, protocolo: str) -> None:
        """Exibe o despacho para a tarefa especificada."""
        if (idx := self.base_dados.pesquisar_indice(protocolo)) == None:
            print(f'Erro: Tarefa {protocolo} não foi encontrada.\n')
            return
        resultado = self.base_dados.obter_atributo(idx, 'resultado')
        if pd.isna(resultado):
            print(f'Erro: Tarefa {protocolo} ainda não possui resultado registrado.\n')
            return
        texto = self.obter_textodespacho(idx, resultado)
        print(texto)

    def pre_processar(self, titulo: str) -> None:
        """Exibe o cabeçalho com o título do processamento."""
        ui_linha = ''
        for _ in (ui_titulo := f'PROGRAMA \'{titulo}\''):
            ui_linha += '-'
        print(f'{ui_titulo}\n{ui_linha}\nExecutando...\n')

    def pos_processar(self, cont: int) -> None:
        """Exibe o rodapé com o número de processamentos."""
        print('\nFinalizando...')
        self.processar_dados()
        print(f'{cont} tarefa(s) processada(s) com sucesso.\n')

    def possui_benativos(self, protocolo: str, cpf: str) -> bool:
        """Verifica se possui beneficio ativo no CPF especificado."""
        if self.cnis.pesquisar_ben_ativos(protocolo, cpf, self.especies_acumulaveis):
            print('Possui BEN inacumulável ativo.')
            return True
        else:
            print('Não possui BEN inacumulável ativo.')
            return False

    def processar_acumulacaoben(self) -> None:
        """Processa a análise da acumulação de benefícios."""
        cont = 0
        protocolo = 0

        self.pre_processar('ANÁLISE DE ACUMULAÇÃO DE BENEFÍCIOS')
        for t in self.lista:
            if t.obter_fase_analise_beninacumulavel() or not t.tem_dadosbasicos():
                continue
            protocolo = t.obter_protocolo()
            print(f'Tarefa {protocolo}...', end=' ')
            cpf = t.obter_cpf()
            if self.possui_benativos(protocolo, cpf):
                t.alterar_beninacumluavel(True)
            else:
                t.alterar_beninacumluavel(False)
            self.salvar_emarquivo()
            cont +=1            
        self.pos_processar(cont)

    def processar_agendamentopm(self) -> None:
        """Agenda uma PM no PMF Agenda."""
        cont = 0
        num_agendamentos = 0
        protocolo = ''

        self.pre_processar('AGENDAR PM')
        for t in self.lista:
            if t.obter_fase_subtarefa_gerada() and not t.obter_fase_agendapm():
                protocolo = t.obter_protocolo()
                print(f'Tarefa {protocolo}...', end=' ')
                cpf = t.obter_cpf()
                subtarefa = t.obter_subtarefa()
                olm = t.obter_olm()
                if num_agendamentos >= 20:
                    self.pmfagenda.reiniciar()
                    num_agendamentos = 0
                dados = self.pmfagenda.agendar(protocolo, cpf, self.nome_servicopm, str(subtarefa), olm)
                t.alterar_agendamento(Agendamento(dados[0], dados[1], dados[2]))
                t.concluir_fase_agendapm()
                print(f'Dia {dados[0]} às {dados[1]}.')
                num_agendamentos += 1
                cont += 1
                self.salvar_emarquivo()
        self.pos_processar(cont)

    def processar_coletadados(self) -> None:
        """Coleta os dados básicos da tarefa no GET."""
        cont = 0        
        protocolo = ''

        self.pre_processar('COLETAR DADOS BÁSICOS')
        for t in self.lista:
            if t.tem_dadosbasicos():
                continue
            protocolo = str(t.obter_protocolo())
            print(f'Tarefa {protocolo}...', end=' ')
            if self.get.pesquisar_tarefa(protocolo):
                self.get.abrir_tarefa()

                dados_coletados = self.get.coletar_dados(protocolo, self.nome_subservico, self.dadosparacoletar)

                if 'der' in self.dadosparacoletar:
                    t.alterar_der(dados_coletados['der'])
                if 'nb' in self.dadosparacoletar:
                    t.alterar_beneficio(dados_coletados['nb'])
                if 'cpf' in self.dadosparacoletar:
                    t.alterar_cpf(dados_coletados['cpf'])
                if 'nit' in self.dadosparacoletar:
                    t.alterar_nit(dados_coletados['nit'])
                if 'quantexig' in self.dadosparacoletar:
                    if int(dados_coletados['quantexig']) > 0:
                        t.marcar_japossui_exigencia()
                if 'quantsub' in self.dadosparacoletar:
                    if int(dados_coletados['quantsub']) > 0:
                        t.marcar_japossui_subtarefa()
                if 'subtarefa' in self.dadosparacoletar:
                    if 'subtarefa' in dados_coletados:
                        self.registrar_subgerada(t, dados_coletados['subtarefa'])
                        t.tarefa.alterar_subtarefa_coletada(True)
                if 'pm' in self.dadosparacoletar:
                    if dados_coletados['pmrealizada']:
                        self.registrar_exigenciagerada(t)
                        resultado = self.processar_relatorio_pm(protocolo)
                        self.registrar_pmfoi_realizada(resultado, t)
                if 'olm' in self.dadosparacoletar:
                    if dados_coletados['olm']:
                        t.alterar_olm(dados_coletados['olm'])
                t.concluir_fase_dadoscoletados()
                print('Dados coletados.')
                self.get.fechar_tarefa()
                self.salvar_emarquivo()
                cont += 1
            else:
                print('Erro: Tarefa não foi encontrada.')
        self.pos_processar(cont)

    def processar_conclusao(self) -> None:
        """Processa a conclusão de tarefas."""
        cont = 0
        protocolo = ''
        nomearquivo = ''
        texto = ''
        numero = 0

        self.pre_processar('CONCLUSÃO DE TAREFAS')
        for t in self.lista:
            if not t.obter_fase_concluso() or t.tem_impedimento():
                continue
            protocolo = str(t.obter_protocolo())
            print(f'Tarefa {protocolo}')
            if self.get.pesquisar_tarefa(protocolo):
                self.get.abrir_tarefa()
                if t.tem_arquivopdfresumo():
                    nomearquivo = path.join(Variaveis.obter_pasta_pdf(), f'{protocolo} - Analise.pdf')
                    resultados = self.adicionar_anexo([nomearquivo])
                    if resultados[0] == False:
                        print('Erro ao anexar arquivo.')
                        continue
                    self.get.irpara_iniciotela()
                    self.get.abrir_guia("Detalhes")
                self.get.irpara_finaltela()
                texto = self.obter_textodespacho(t.obter_idx(), t.obter_resultado())
                self.get.adicionar_despacho(texto)
                self.get.irpara_iniciotela()
                texto = self.obter_textoconclusao(t.obter_idx(), t.obter_resultado())
                numero = t.obter_beneficio()
                resultado = self.concluir_tarefa(numero, texto)
                if resultado['houve_conclusao']:
                    t.concluir_fase_conclusao()
                    self.salvar_emarquivo()
                    cont += 1
                else:
                    print(f'Erro ao concluir tarefa: {resultado["msg"]}')
                self.get.fechar_tarefa()
            else:
                print(f'Erro: Tarefa {protocolo} não foi encontrada.\n')
        self.pos_processar(cont)

    def processar_desimpedimento(self, lista: list[str]) -> None:
        """Marca cada tarefa da lista como desimpedida para conclusão."""
        cont = 0
        self.pre_processar('REMOVER IMPEDIMENTO')
        for protocolo in lista:
            if (idx := self.base_dados.pesquisar_indice(protocolo)) is None:
                print(f'Tarefa {protocolo} não foi encontrada.')
                continue
            t = Tarefa(self.base_dados, idx)
            t.remover_impedimento()
            print(f'Tarefa {protocolo} processada.')
            cont =+ 1
        self.salvar_emarquivo()
        self.pos_processar(cont)

    def processar_desistencia(self, lista: list[str]) -> None:
        """Registra a desistência do requerente nas tarefas especificadas."""
        cont = 0
        self.pre_processar('DESISTÊNCIA')
        for protocolo in lista:
            if (idx := self.base_dados.pesquisar_indice(protocolo)) is None:
                print(f'Tarefa {protocolo} não foi encontrada.')
                continue
            t = Tarefa(self.base_dados, idx)
            t.registrar_desistencia()
            print(f'Tarefa {protocolo} processada.')
            cont =+ 1
        self.salvar_emarquivo()
        self.pos_processar(cont)

    def processar_edicaoemlote(self, lista: list[str]) -> None:
        """Processa um script com edição de tarefas em lote."""
        atributos = lista[0].split(' ')
        num_itens = len(lista)
        for i in range(1, num_itens):
            valores = lista[i].split(' ')
            protocolo = valores[0].strip()
            self.base_dados.alterar_atributos(protocolo, atributos[1:], valores[1:])
        self.salvar_emarquivo()
        print(f'{num_itens-1} tarefa(s) alterada(s) com sucesso.')

    def processar_impedimento(self, impedimento_id: str, lista: list[str]) -> None:
        """Marca cada tarefa da lista com o impedimento de conclusão especificado."""
        cont = 0
        self.pre_processar('ADICIONAR IMPEDIMENTO')
        for protocolo in lista:
            if (idx := self.base_dados.pesquisar_indice(protocolo)) is None:
                print(f'Tarefa {protocolo} não foi encontrada.')
                continue
            t = Tarefa(self.base_dados, idx)
            t.alterar_impedimento(impedimento_id)
            print(f'Tarefa {protocolo} processada.')
            cont =+ 1
        self.salvar_emarquivo()
        self.pos_processar(cont)

    def processar_status(self, t: Tarefa) -> bool:
        """
        Coleta o status da tarefa pesquisada e registra a conclusão se concluída/cancelada.
        Retorna True se concluída/cancelada.
        """
        nav = self.get

        status = nav.coletar_status()
        if status in ['Cancelada', 'Concluída']:
            t.concluir_fase_concluso()
            t.concluir_fase_conclusao()
            return True
        return False

    def salvar_emarquivo(self) -> None:
        """Salva a base de dados."""
        self.base_dados.salvar_emarquivo()

    def sobrestar(self, tarefa: str) -> None:
        """Gera uma tarefa de sobrestamento no GET."""
        numsub = self.get.sobrestar()
        tarefa.alterar_sub_sobrestado(numsub)