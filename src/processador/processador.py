## Codificado por Douglas Rodrigues de Almeida.
## Junho de 2023
"""Processador base do UIP"""

import pandas as pd
import time
from arquivo import carregar_texto
from basedados import BaseDados, TipoBooleano, TipoData, TipoTexto
from despacho import Despacho, Despachos
from filtro import Filtro, Filtros
from impedimento import Impedimento
from listagem import Listagem
from lote import Lote
from manipuladorpdf import ManipuladorPDF
from modelos_exigencias import ListaModelosExigencia
from navegador import Cnis, Get, Pmfagenda, Sibe, SD
from os import path
from resultado import Resultado, Resultados
from tarefa import Tarefa
from variaveis import Variaveis

RES_SUBTAREFA_ERRO = 0

RES_SUBTAREFA_GERADA = 1

RES_SUBTAREFA_COLETADA = 2

SEGUNDOS_VISUALIZACAO_RAPIDA = 3

datas_padrao = ['der', 'data_conclusao', 'data_exigencia', 'vencim_exigencia']

class Processador:
    """Classe base para o processador do UIP."""
    def __init__(self, base_dados: BaseDados) -> None:
        #Objeto da base de dados
        self.base_dados = base_dados

        #Comandos disponíveis para o usuário.
        self.comandos = {}

        #Dados coletados no processo Coleta de Dados Básicos.
        self.dadosparacoletar = []

        #
        self.despachos = None

        #Informa se a fila foi aberta.
        self.fila_aberta = False

        #Lista de tarefas carregadas da base de dados.
        self.lista: list[Tarefa] = []

        #Marcações disponíveis para o usuário.
        self.marcacoes = {}

        self.modelos_exigencia = None

        #Marcas
        self.tags = ['todos']

        #Colunas e tipos de dados 'Data' padrão para todas filas.
        self.base_dados.definir_colunas(datas_padrao)

        #Campos de outros
        self.nome_servico = ""

        self.nome_subservico = ""

        self.resultados = None

        self.tipo_docs = []

        self.criarsub_modolinha = False

    def __str__(self) -> str:
        quant_tarefas = self.obter_info("tudo")
        resultado = f'TAREFAS DE {self.nome_servico.upper()}\n'
        linha = ''.join(['=' for _ in resultado])
        resultado += linha
        resultado += f'\nTotal: {quant_tarefas} tarefa(s)\n'
        return resultado
    
    def adicionar_tarefas(self, protocolos: list[str]) -> None:
        """Adiciona uma lista de tarefas a base de dados."""
        self.base_dados.adicionar_registros(protocolos)
        self.salvar_emarquivo()
        print("\nInclusões processadas com sucesso.\n")
             
    def carregar_fila(self) -> bool:
        """"""
        try:
            self.fila_aberta = self.base_dados.carregar_dearquivo()
        except OSError as err:
            print(f"Erro ao abrir fila de tarefas: {err.strerror}")
            return False
        return True
    
    def coletar_nit_lote(self) -> None:
        """."""
        cont = 0
        protocolo = ''
        self.pre_processar('COLETAR NIT')
        print("Usando lista personalizada.")

        for item in self.obter_listapersonalizada():
            if (idx := self.base_dados.pesquisar_indice(item)) == None:
                print(f"Erro: Tarefa {item} não foi encontrada na fila atual.\n")
                continue
            t = Tarefa(self.base_dados, idx)
            if self.coletar_nit(t):
                cont += 1
        self.pos_processar(cont)
    
    def coletar_nit(self, tarefa: Tarefa) -> bool:
        """
        Coleta o NIT via CNIS da tarefa especificada.
        """
        cont = 0

        if self.cnis is None:
            return False

        cpf = str(tarefa.obter_cpf())
        protocolo = str(tarefa.obter_protocolo())
        nit = self.cnis.pesquisar_nit_decpf(protocolo, cpf)
        tarefa.alterar_nit(TipoTexto(nit))
        print(f'Tarefa {protocolo} processada.')
        self.salvar_emarquivo()
        return True
    
    def checar_concluida(self, t: Tarefa) -> bool:
        """
        Coleta o status da tarefa pesquisada e registra a conclusão se concluída/cancelada.
        Retorna True se concluída/cancelada.
        """
        nav = self.get
        if nav is None:
            return False

        (status, data) = nav.coletar_status()
        if status in ['Cancelada', 'Concluída']:
            t.marcar_conclusa()
            t.concluir(TipoData(data))
            return True
        return False
    
    def coletar_subtarefas(self, protocolo: str, imprimirpdf: bool) -> list[tuple[str, bool]]:
        """Coleta as subtarefas no GET."""
        nav = self.get

        if nav is None:
            return []

        nav.abrir_guia('Subtarefas')
        nav.irpara_finaltela()
        return nav.coletar_subtarefas(protocolo, self.nome_subservico, imprimirpdf)
    
    def concluir_tarefa(self, ulp: bool) -> None:
        """Processa a conclusão de tarefas."""
        buffer_linha = ''
        cont = 0
        get = self.get
        protocolo = ''

        if get is None:
            return
        if self.resultados is None:
            return

        self.pre_processar('CONCLUSÃO DE TAREFAS')
        for t in self.lista:

            if get.suspender_processamento:
                print('Processamento suspenso.\n')
                break
            anexacao = t.obter_anexacao_analise()
            if not t.esta_concluso().e_verdadeiro or t.esta_concluida().e_verdadeiro or t.tem_impedimento().e_verdadeiro:
                continue
            protocolo = str(t.obter_protocolo())
            buffer_linha = f'Tarefa {protocolo}...'
            print(buffer_linha, end='\r')
            if get.pesquisar_tarefa(protocolo):
                
                #Verifica se tarefa está cancelada/concluída
                if self.processar_status(t):
                    print(buffer_linha + 'Tarefa já cancelada/concluída. Conclusão não foi processada.')
                    cont += 1
                    continue
                get.abrir_tarefa()
                if anexacao.tem_anexo().e_verdadeiro:
                    arquivo_pdf = f'{protocolo} - Analise.pdf'
                    caminho_pdf = path.join(Variaveis.obter_pasta_pdf(), arquivo_pdf)
                    res_anexacao = get.adicionar_anexos([caminho_pdf])
                    if len(res_anexacao) > 0 and res_anexacao[0]:
                        buffer_linha += "PDF Anexado."
                        print(buffer_linha, end='\r')
                        anexacao.alterar_anexacao(TipoBooleano(True))
                        anexacao.marcar_erro(TipoBooleano(None))
                        t.alterar_anexacao_analise(anexacao)
                    else:
                        buffer_linha += "Erro ao anexar arquivo."
                        print(buffer_linha)
                        anexacao.marcar_erro(TipoBooleano(True))
                        t.alterar_anexacao_analise(anexacao)
                        self.salvar_emarquivo()
                        get.fechar_tarefa()
                        continue
                get.irpara_iniciotela()
                get.abrir_guia("Detalhes")
                get.irpara_finaltela()
                resultado_id = str(t.obter_resultado().valor)
                resultado = self.resultados.obter(resultado_id)
                if resultado is None:
                    buffer_linha += " Erro ao obter resultado do requerimento."
                    print(buffer_linha)
                    get.fechar_tarefa()
                    continue
                despacho_texto = self.formatar_textodespacho(t.obter_idx(), resultado)
                get.adicionar_despacho(despacho_texto)
                buffer_linha += " Despacho gerado e incluído."
                print(buffer_linha, end='\r')
                get.irpara_iniciotela()
                conclusao_texto = self.formatar_textoconclusao(t.obter_idx(), resultado)
                get.irpara_iniciotela()
                get.clicar_botao('formDetalharTarefa:detalhe_concluir')
                get.aguardar_telaprocessamento()
                numero_processo = ''
                if 'ben' in self.tags:
                    numero_processo = str(t.obter_beneficio())
                elif 'sd' in self.tags:
                    numero_processo = str(t.obter_segurodefeso())
                res_conclusao = get.concluir_tarefa(numero_processo, conclusao_texto)
                if res_conclusao['houve_conclusao']:
                    buffer_linha += ' Concluída.'
                    print(buffer_linha)
                    t.concluir(None)
                    self.salvar_emarquivo()
                    cont += 1
                else:
                    buffer_linha += f' Erro ao concluir tarefa: {res_conclusao["msg"]}'
                    print(buffer_linha)
                get.fechar_tarefa()
            else:
                buffer_linha += 'Erro: Tarefa não encontrada.\n'
                print(buffer_linha)
        self.pos_processar(cont)

    def definir_cnis(self, nav: Cnis | None) -> None:
        """a"""
        self.cnis = nav

    def definir_despachos(self, despachos: Despachos) -> None:
        self.despachos = despachos
    
    def definir_filtros(self, filtros: Filtros) -> None:
        self.filtros = filtros        

    def definir_get(self, nav: Get | None) -> None:
        """a"""
        self.get = nav
        if self.get is not None:
            self.get.alterar_modolinha(self.criarsub_modolinha)

    def definir_mod_exigencias(self, lista: ListaModelosExigencia) -> None:
        """"""
        self.modelos_exigencia = lista

    def definir_pmfagenda(self, nav: Pmfagenda | None) -> None:
        """Define o automatizador do PMF Agenda."""
        self.pmfagenda = nav

    def definir_resultados(self, resultados: Resultados) -> None:
        self.resultados = resultados

    def definir_sibe(self, nav: Sibe | None) -> None:
        """Define o automatizador do SIBE PU."""
        self.sibe = nav

    def definir_sd(self, nav: SD | None) -> None:
        """a"""
        self.sd = nav

    def formatar_textoconclusao(self, idx: int, resultado: Resultado) -> str:
        """Retorna o texto do comunicado de conclusão especificado."""
        texto_modelo = resultado.conclusao
        vars_necessarias = resultado.vars_conclusao.split(' ')
        variaveis = {}
        for var in vars_necessarias:
            variaveis[var] =  self.base_dados.obter_atributo(idx, var)
        return texto_modelo.format(**variaveis)        

    def formatar_textodespacho(self, idx: int, resultado: Resultado) -> str:
        """Retorna o texto do despacho especificado."""
        texto_modelo = resultado.despacho
        vars_necessarias = resultado.vars_despacho.split(' ')
        variaveis = {}
        for var in vars_necessarias:
            variaveis[var] =  self.base_dados.obter_atributo(idx, var)
        return texto_modelo.format(**variaveis)
    
    #== GERAR PA ==#
    
    def gerar_pa_base(self) -> None:
        cont = 0
        self.pre_processar('GERAR PA')
        for t in self.lista:
            tem_db = t.tem_dadosbasicos().e_verdadeiro
            esta_concluida = t.esta_concluida().e_verdadeiro
            if tem_db or esta_concluida:
                continue
            if self.gerar_pa(t):
                cont += 1
        self.pos_processar(cont)

    def gerar_pa_lote(self) -> None:
        cont = 0
        self.pre_processar('GERAR PA')
        print("Usando lista personalizada.")
        for item in self.obter_listapersonalizada():
            if (idx := self.base_dados.pesquisar_indice(item)) == None:
                print(f"Erro: Tarefa {item} não foi encontrada na fila atual.\n")
                continue
            t = Tarefa(self.base_dados, idx)
            if self.gerar_pa(t):
                cont += 1
        self.pos_processar(cont)

    def gerar_pa(self, tarefa: Tarefa) -> bool:
        """Gerar cópia do PA da tarefa GE."""
        buffer_linha = ''
        get = self.get

        if get is None:
            return False
        protocolo = str(tarefa.obter_protocolo())
        buffer_linha = f"Tarefa {protocolo}..."
        print(buffer_linha, end='\r')
        if get.pesquisar_tarefa(protocolo):

            #Verifica se tarefa está cancelada/concluída
            if self.checar_concluida(tarefa):
                buffer_linha += "Concluida/Cancelada. Coleta não processada."
                print(buffer_linha)
                return False
            
            #GET gera PDF do PA
            if get.gerar_pa(protocolo):
                buffer_linha += "PA gerado."
            print(buffer_linha)
            #self.salvar_emarquivo()
        else:
            buffer_linha += "Erro: Tarefa não foi encontrada."
            print(buffer_linha)
            return False
        return True

    
    #== REGISTRAR DESPACHOS ==#
    def registrar_despacho_lote(self, tipo: str) -> None:
        cont = 0
        self.pre_processar('REGISTRAR DESPACHO')
        print("Usando lista personalizada.")
        for item in self.obter_listapersonalizada():
            if (idx := self.base_dados.pesquisar_indice(item)) == None:
                print(f"Erro: Tarefa {item} não foi encontrada na fila atual.\n")
                continue
            t = Tarefa(self.base_dados, idx)
            if self.registrar_despacho(t, tipo):
                cont += 1
        self.pos_processar(cont)

    def registrar_despacho(self, tarefa: Tarefa, tipo: str) -> bool:
        """Registra um despacho no GET."""
        buffer_linha = ''
        get = self.get

        if get is None:
            return False
        if self.despachos is None:
            return False
        protocolo = str(tarefa.obter_protocolo())
        buffer_linha = f"Tarefa {protocolo}..."
        print(buffer_linha, end='\r')
        modelo = tarefa.obter_modelo_despacho(tipo)
        if modelo.e_nulo:
            buffer_linha += " Sem despacho para registrar."
            print(buffer_linha)
            return False
        despacho = self.despachos.obter(str(modelo))
        if despacho is None:
            buffer_linha += f' Tipo de despacho ({modelo}) não disponível.'
            print(buffer_linha)
            return False
        conteudo_despacho = despacho.conteudo
        if get.pesquisar_tarefa(protocolo):

            #Verifica se tarefa está cancelada/concluída
            if self.checar_concluida(tarefa):
                buffer_linha += " Concluida/Cancelada. Despacho não registrado."
                print(buffer_linha)
                return False            
            get.abrir_tarefa()
            get.irpara_finaltela()
            get.adicionar_despacho(conteudo_despacho)

            buffer_linha += " Despacho gerado e incluído."
            print(buffer_linha)
            get.irpara_iniciotela()
            get.fechar_tarefa()
            return True
        else:
            buffer_linha += " Tarefa não encontrada no GET."
            print(buffer_linha)
            return False
    
    def juntar_docs(self):
        cont = 0
        lista = []
        self.pre_processar('JUNTAR DOCUMENTOS DA ANÁLISE')
        print("Usando lista personalizada.")
        manipulador = ManipuladorPDF()
        for item in self.obter_listapersonalizada():
            if (idx := self.base_dados.pesquisar_indice(item)) == None:
                print(f"Erro: Tarefa {item} não foi encontrada na fila atual.\n")
                continue
            for tipo_doc in self.tipo_docs:
                lista.append(f'{item} - {tipo_doc}')
            manipulador.juntar(lista, f'{item} - PreAnalise')
            print(f'Tarefa {item}...Juntado.')
            cont += 1
            lista.clear()
        self.pos_processar(cont)

    def listar(self, listagem: Listagem, filtro: Filtro) -> tuple[int, str]:
        """Retorna uma lista de tarefas."""
        return self.base_dados.obter_lista(listagem, filtro)

    def obter_info(self, nome_filtro) -> int:
        if (filtro := self.filtros.obter(nome_filtro)) is not None:
            res = self.base_dados.obter_quantidades(filtro)
        else:
            res = 0
        return res
    
    def obter_listapersonalizada(self) -> list[str]:
        print("Abrindo lote de protocolos...")
        with carregar_texto('lista_protocolos.txt') as lista:
            if len(lista) == 0:
                print('Erro: Lista com lote de protocolos está vazia.\n')
            return lista
        
    def obter_textoexigencia(self, tipo: str) -> str:
        """Retorna o texto para geração de exigência especificado."""
        if self.modelos_exigencia is None:
            return ''
        modelo = self.modelos_exigencia.obter(tipo)
        if modelo is None:
            return ''
        else:
            return modelo.texto
        
    def registrar_exigenciagerada(self, tarefa: Tarefa) -> None:
        """Registra que já foi gerada uma exigência na tarefa"""
        exigencia = tarefa.obter_exigencia()
        exigencia.cumprir(TipoBooleano(True))
        tarefa.alterar_exigencia(exigencia)

    def visualizar_rapido(self, segundos: int, tarefa: Tarefa) -> None:
        """Abre a tarefa na lista de despachos por segundos"""
        get = self.get

        if get is None:
            return
        protocolo = str(tarefa.obter_protocolo())
        if get.pesquisar_tarefa(protocolo):
            if self.checar_concluida(tarefa):
                self.salvar_emarquivo()
                print(f'Tarefa {protocolo} concluída/cancelada.')
                return
            get.abrir_tarefa()
            get.irpara_finaltela()
            get.subir_pagina()
            time.sleep(segundos)
            get.irpara_iniciotela()
            get.fechar_tarefa()
            print(f'Tarefa {protocolo} visualizada.')
        else:
            print(f'Tarefa {protocolo} não encontrada.')
        return
    
    def visualizar_rapido_lote(self) -> None:
        """."""
        cont = 0
        protocolo = ''
        self.pre_processar('VISUALIZAR TAREFA')
        print("Usando lista personalizada.")

        for item in self.obter_listapersonalizada():
            if (idx := self.base_dados.pesquisar_indice(item)) == None:
                print(f"Erro: Tarefa {item} não foi encontrada na fila atual.\n")
                continue
            t = Tarefa(self.base_dados, idx)
            if self.visualizar_rapido(SEGUNDOS_VISUALIZACAO_RAPIDA, t):
                cont += 1
        self.pos_processar(cont)

    #===========================================================================================================#
    
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

    #def definir_exigencia_simples(self, tarefa: Tarefa, codigo_exig: str) -> None:
        #"""Cadastra uma exigência na tarefa"""
        #texto = self.obter_textoexigencia(codigo_exig)
        #return self.get.definir_exigencia(texto)
    
    #def definir_filtros(self, filtros: Filtros) -> None:
        """"""
        #for filtro in filtros:
            #if filtro.processador == 'todos':
                #self.filtros_processador.adicionar(filtro)

    #def definir_listagens(self, listagens: Listagens) -> None:
        """"""
        #for listagem in listagem:
            #if listagem.processador == 'todos':
                #self.listagem_processador.adicionar(listagem)

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
                valor_dado = pd.to_datetime(valor, dayfirst=True, format='%d/%m/%Y').floor('D')
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
                if self.base_dados.alterar_atributos(protocolo, [self.atributos[atributo]['coluna']], [valor_dado], " "):
                    print(f'Tarefa {protocolo} foi alterda.')
                else:
                    print(f'Tarefa {protocolo} não foi alterda.')
            self.salvar_emarquivo()
            print('\n')
            return
        else:            
            print(f'Erro: O atributo \'{atributo}\' não foi reconhecido como um atributo editável válido.\n')
            return
    
    def obter_comandos(self) -> dict:
        """Retorna os comandos exclusivos do processador."""
        return self.comandos
    
    def obter_marcacoes(self):
        """Retorna as marcações disponíveis."""
        return self.marcacoes
    
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
        resultado_id = self.base_dados.obter_atributo(idx, 'resultado')
        if pd.isna(resultado_id):
            print(f'Erro: Tarefa {protocolo} ainda não possui resultado registrado.\n')
            return
        resultado = self.resultados.obter(resultado_id)
        if resultado is None:
            print(" Erro ao obter resultado do requerimento.")
            return
        texto = self.formatar_textoconclusao(idx, resultado)
        print(texto)
    
    def mostrar_despacho(self, protocolo: str) -> None:
        """Exibe o despacho para a tarefa especificada."""
        if (idx := self.base_dados.pesquisar_indice(protocolo)) == None:
            print(f'Erro: Tarefa {protocolo} não foi encontrada.\n')
            return
        resultado_id = self.base_dados.obter_atributo(idx, 'resultado')
        if pd.isna(resultado_id):
            print(f'Erro: Tarefa {protocolo} ainda não possui resultado registrado.\n')
            return
        resultado = self.resultados.obter(resultado_id)
        if resultado is None:
            print(" Erro ao obter resultado do requerimento.")
            return        
        texto = self.formatar_textodespacho(idx, resultado)
        print(texto)

    def pre_processar(self, titulo: str) -> None:
        """Exibe o cabeçalho com o título do processamento."""
        ui_linha = ''
        for _ in (ui_titulo := f'PROGRAMA \'{titulo}\''):
            ui_linha += '-'
        print(f'{ui_titulo}\n{ui_linha}\nExecutando...\n')
        
        if not self.get is None:
            self.get.suspender_processamento = False

    def pos_processar(self, cont: int) -> None:
        """Exibe o rodapé com o número de processamentos."""
        print('\nFinalizando...')
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
            cont += 1
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
            cont += 1
        self.salvar_emarquivo()
        self.pos_processar(cont)

    def processar_edicaoemlote(self, lista: list[str]) -> None:
        """Processa um script com edição de tarefas em lote."""
        atributos = lista[0].split(' ')
        num_itens = len(lista)
        for i in range(1, num_itens):
            valores = lista[i].split(' ')
            protocolo = valores[0].strip()
            self.base_dados.alterar_atributos(protocolo, atributos[1:], valores[1:], " ")
        self.salvar_emarquivo()
        print(f'{num_itens-1} tarefa(s) alterada(s) com sucesso.')

    def processar_impedimento(self, impedimento: Impedimento, lista: list[str]) -> None:
        """Marca cada tarefa da lista com o impedimento de conclusão especificado."""
        cont = 0
        self.pre_processar('ADICIONAR IMPEDIMENTO')
        for protocolo in lista:
            if (idx := self.base_dados.pesquisar_indice(protocolo)) is None:
                print(f'Tarefa {protocolo} não foi encontrada.')
                continue
            t = Tarefa(self.base_dados, idx)
            t.alterar_impedimento(impedimento)
            print(f'Tarefa {protocolo} processada.')
            cont += 1
        self.salvar_emarquivo()
        self.pos_processar(cont)

    def processar_lote(self, lote: Lote) -> None:
        """Processa um lote de edição de dados"""
        cont = 0
        self.pre_processar('PROCESSAR LOTE')
        print(f"Lote: {lote}")
        itens = lote.carregar_dados()
        atributos = lote.obter_atributos()[1:]
        for registro in itens:
            print(f"Tarefa {registro[0]}...")
            if self.base_dados.alterar_atributos2(registro[0].strip(), atributos, registro[1:]):
                cont += 1
        self.salvar_emarquivo()
        self.pos_processar(cont)

    def processar_status(self, t: Tarefa) -> bool:
        """
        Coleta o status da tarefa pesquisada e registra a conclusão se concluída/cancelada.
        Retorna True se concluída/cancelada.
        """
        nav = self.get

        if nav is None:
            return False
        status = nav.coletar_status()
        if status[0] in ['Cancelada', 'Concluída']:
            t.marcar_conclusa()
            t.concluir(TipoData(status[1]))
            return True
        return False

    def salvar_emarquivo(self) -> None:
        """Salva a base de dados."""
        self.base_dados.salvar_emarquivo()

    def sobrestar(self, tarefa: str) -> None:
        """Gera uma tarefa de sobrestamento no GET."""
        numsub = self.get.sobrestar()
        tarefa.alterar_sub_sobrestado(numsub)

    def _definir_filtros(self) -> None:
        df = self.base_dados.dados
        filto_sem_imp_conc = df['impedimentos'].isna() & df['concluso'].isna() & df['sub_sobrestado'].isna()

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

    def _definir_listagens(self) -> None:
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