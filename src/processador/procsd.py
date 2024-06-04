## Codificado por Douglas Rodrigues de Almeida.
## Outubro de 2023
"""Processador para Seguro Defeso"""

import time
from .processador import Processador
from arquivo import carregar_dados
from basedados import BaseDados, TipoBooleano, TipoData, TipoHora, TipoInteiro, TipoTexto
from impedimento import Impedimento
from lote import Lote
from manipuladorpdf import ManipuladorPDF
from os import path, system
from tarefa import TarefaSeguroDefeso
from variaveis import Variaveis

tipocolunas = {'sd': 'string'
               
}

datas_padrao = []

atributos = {
                                 
            }

ARQUIVO_DEFESOS = "defesos.json"

class ProcessadorSeguroDefeso(Processador):
    """Classe para o processador de Seguro Defeso."""
    def __init__(self, base_dados):      
        super().__init__(base_dados)

        self.atributos = atributos

        self.criarsub_modolinha = False 

        #Dados a serem coletados pela atividade Coleta de Dados Básicos.
        self.dadosparacoletar = ['der', 'cpf', 'uf', 'portaria', 'defeso', 'quantexig']

        #Colunas e tipos de dados 'Data' padrão para todas filas.
        self.base_dados.definir_colunas(datas_padrao)

        try:
            with carregar_dados(ARQUIVO_DEFESOS) as dados:
                self.defesos = dados
        except OSError as err:
            print(f"Erro ao abrir dados de defesos: {err.strerror}.")

        self.especies_acumulaveis: list[str] = []

        self.lista: list[TarefaSeguroDefeso] = []

        self.nome_servico = 'Seguro Defeso'

        #Tag para Seguro Defeso
        self.tags.append('sd')

        self.tipo_docs.extend(['SD', 'ExtratoCNIS', 'ExtratoPJ', 'DocArrecadacao', 'RGP'])

    def __str__(self) -> str:
        """"""
        resultado = super().__str__()

        resultado += f"Pendentes de coleta de dados: {self.obter_info('coletadb')} tarefa(s).\n"
        resultado += f"Pendentes da análise de direito: {self.obter_info('analisesd')} tarefa(s).\n"
        resultado += f"Pendentes de conclusão: {self.obter_info('conclusos')} tarefa(s).\n"

        return resultado
     
    #== COLETA DE DADOS BASICOS ==#
    
    def coletar_dadosbasicos_base(self) -> None:
        cont = 0
        self.pre_processar('COLETA DE DADOS BÁSICOS')
        for t in self.lista:
            tem_db = t.tem_dadosbasicos().e_verdadeiro
            esta_concluida = t.esta_concluida().e_verdadeiro
            if tem_db or esta_concluida:
                continue
            if self.coletar_dados(t):
                cont += 1
        self.pos_processar(cont)

    def coletar_dadosbasicos_lote(self) -> None:
        cont = 0
        self.pre_processar('COLETA DE DADOS BÁSICOS')
        print("Usando lista personalizada.")
        for item in self.obter_listapersonalizada():
            if (idx := self.base_dados.pesquisar_indice(item)) == None:
                print(f"Erro: Tarefa {item} não foi encontrada na fila atual.\n")
                continue
            t = TarefaSeguroDefeso(self.base_dados, idx)
            if self.coletar_dados(t):
                cont += 1
        self.pos_processar(cont)

    def coletar_dados(self, tarefa: TarefaSeguroDefeso) -> bool:
        """Coleta os dados básicos da tarefa de SD no GET."""
        buffer_linha = ''
        get = self.get

        if get is None:
            return False
        protocolo = str(tarefa.obter_protocolo())
        buffer_linha = f"Tarefa {protocolo}..."
        print(buffer_linha, end='\r')
        if get.pesquisar_tarefa(protocolo):
            if self.checar_concluida(tarefa):
                buffer_linha += "Concluida/Cancelada. Coleta não processada."
                print(buffer_linha)
                return False
            get.abrir_tarefa()
            dados_coletados = get.coletar_dados(protocolo, self.nome_subservico, self.dadosparacoletar)
            if 'der' in self.dadosparacoletar:
                tarefa.alterar_der(TipoData(dados_coletados['der']))
            if 'cpf' in self.dadosparacoletar:
                tarefa.alterar_cpf(TipoTexto(dados_coletados['cpf']))
            if 'nit' in self.dadosparacoletar:
                tarefa.alterar_nit(TipoTexto(dados_coletados['nit']))
            if 'quantexig' in self.dadosparacoletar:
                if dados_coletados['quantexig'] > 0:
                    tarefa.marcar_japossui_exigencia()
            if 'uf' in self.dadosparacoletar:
                tarefa.alterar_uf(TipoTexto(dados_coletados['uf']))
            if 'defeso' in self.dadosparacoletar:
                tarefa.alterar_defeso(TipoTexto(dados_coletados['defeso']))
            if 'portaria' in self.dadosparacoletar:
                tarefa.alterar_portaria(TipoTexto(dados_coletados['portaria']))

            #competencia_pgto = self.obter_competenciapgto(dados_coletados['portaria'], dados_coletados['portaria'])
            #tarefa.alterar_comp_pgto(competencia_pgto)
            tarefa.marcar_tem_dadosbasicos()
            buffer_linha += "Dados coletados."
            print(buffer_linha)
            get.fechar_tarefa()
            self.salvar_emarquivo()
        else:
            buffer_linha += "Erro: Tarefa não foi encontrada."
            print(buffer_linha)
            return False
        return True

    #== CONSULTAR SD ==#    
    def consultar_sd(self, subcomandos: list[str]) -> None:
        """Executa o programa 'Consulta SD' do processador."""
        if self.sd is None:
            return
        self.sd.abrir_consulta()
        if len(subcomandos) > 0 and (subcomandos[0] == 'ulp'):
            self.consultar_sd_lote()
        else:
            self.consultar_sd_base()
    
    def consultar_sd_base(self) -> None:
        cont = 0
        self.pre_processar('CONSULTAR SD')
        for t in self.lista:
            tem_db = t.tem_dadosbasicos().e_verdadeiro
            esta_concluida = t.esta_concluida().e_verdadeiro
            if not tem_db or esta_concluida:
                continue
            if self.consultar_sd_item(t):
                cont += 1
                time.sleep(3)
        self.pos_processar(cont)

    def consultar_sd_lote(self) -> None:
        cont = 0
        self.pre_processar('CONSULTAR SD')
        print("Usando lista personalizada.")
        for item in self.obter_listapersonalizada():
            if (idx := self.base_dados.pesquisar_indice(item)) == None:
                print(f"Erro: Tarefa {item} não foi encontrada na fila atual.\n")
                continue
            t = TarefaSeguroDefeso(self.base_dados, idx)
            if self.consultar_sd_item(t):
                cont += 1
                time.sleep(3)
        self.pos_processar(cont)

    def consultar_sd_item(self, tarefa: TarefaSeguroDefeso) -> bool:
        """Gera o documento de arrecadação."""
        buffer_linha = ''
        sd = self.sd

        if sd is None:
            return False
        protocolo = str(tarefa.obter_protocolo())
        cpf = str(tarefa.obter_cpf())
        buffer_linha = f"Tarefa {protocolo}..."
        print(buffer_linha, end='\r')
        
        if sd.consultar_cpf(protocolo, cpf):
            buffer_linha += "Extrato gerado."
            print(buffer_linha)
            return True
        else:
            buffer_linha += "Erro: Extrato não gerado."
            print(buffer_linha)
            return False
    
    def definir_comandos(self) -> None:
        """Define os comandos exclusivos deste processador."""
        self.comandos['defeso'] = {
                'funcao': self.exibir_defeso,
                'argsmin': 0,
                'desc': 'Exibe informações de um defeso especificado',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': False,
                'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_protocolo': False,
                'requer_sibe': False,
                'requer_sd': False
        }
        self.comandos['extraircnis'] = {
                'funcao': self.gerar_cnis,
                'argsmin': 0,
                'desc': 'Executa o programa \'Extrair CNIS\' do processador.',
                'requer_subcomando': False,
                'requer_cnis': True,
				'requer_get': False,
                'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_protocolo': False,
                'requer_sibe': False,
                'requer_sd': False
        }
        self.comandos['extrairpj'] = {
                'funcao': self.gerar_extratopj,
                'argsmin': 0,
                'desc': 'Executa o programa \'Extrair PJ\' do processador.',
                'requer_subcomando': False,
                'requer_cnis': True,
				'requer_get': False,
                'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_protocolo': False,
                'requer_sibe': False,
                'requer_sd': False
        }
        self.comandos['extrairdocarrecada'] = {
                'funcao': self.gerar_docarrecada,
                'argsmin': 0,
                'desc': 'Executa o programa \'Extrair Documento de Arrecadacao\' do processador.',
                'requer_subcomando': False,
                'requer_cnis': True,
				'requer_get': False,
                'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_protocolo': False,
                'requer_sibe': False,
                'requer_sd': False
        }
        self.comandos['rgp'] = {
                'funcao': self.gerar_rgp,
                'argsmin': 0,
                'desc': 'Executa o programa \'Gerar RGP\' do processador.',
                'requer_subcomando': False,
                'requer_cnis': True,
				'requer_get': False,
                'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_protocolo': False,
                'requer_sibe': False,
                'requer_sd': False
        }
        self.comandos['consultarsd'] = {
                'funcao': self.consultar_sd,
                'argsmin': 0,
                'desc': 'Executa o programa \'Consultar SD\' do processador.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': False,
                'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_protocolo': False,
                'requer_sibe': False,
                'requer_sd': True
        }
        self.comandos['exibirdoc'] = {
                'funcao': self.exibir_proc,
                'argsmin': 0,
                'desc': 'Exibe artefatos do processo.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': False,
                'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_protocolo': False,
                'requer_sibe': False,
                'requer_sd': False
        }
        self.comandos['gerarres'] = {
                'funcao': self.gerar_resultaoo,
                'argsmin': 0,
                'desc': 'Gera o PDF do requerimento SD.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': False,
                'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_protocolo': False,
                'requer_sibe': False,
                'requer_sd': True
        }
        self.comandos['finalizardoc'] = {
                'funcao': self.finalizar_doc,
                'argsmin': 0,
                'desc': 'Junta os PDFs no arquivo de analise final.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': False,
                'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_protocolo': False,
                'requer_sibe': False,
                'requer_sd': False
        }

    def definir_marcacoes(self) -> None:
        """Define as marcações relativas a Auxílio Acidente."""
        pass

    def exibir_defeso(self, subcomandos: list[str]) -> None:
        """"""
        if len(subcomandos) < 2:
            print("Erro: Número de argumentos insuficientes. Informe o número da portaria e o número do defeso e tente novamente.\n")
            return
        portaria_info = subcomandos[0]
        defeso_info = subcomandos[1]
        consulta = f'{portaria_info},{defeso_info}'

        if consulta in self.defesos:
            print(f"Portaria {portaria_info} - Defeso {defeso_info}")
            defeso = self.defesos[consulta]
            print(f"Início em: {defeso['inicio_periodo']}")
            print(f"Fim em: {defeso['fim_periodo']}")
            print(f"Período contributivo: {defeso['inicio_contribuicao']} a {defeso['fim_contribuicao']}")
            print(f"Estados: {defeso['estados']}")
            print(f"Áreas: {defeso['areas']} - Produtos: {defeso['produtos']}")
            print(f"Descrição: {defeso['descricao']}\n")
        else:
            print("Erro: Não foi encontrado nenhum defeso com os parâmetros informados.\n")

    def exibir_proc(self, subcomandos: list[str]) -> None:
        if len(subcomandos) < 1:
            print("Erro: Necessário informar os números de protocolo.\n")
            return
        for item in subcomandos:
            nomearquivo = path.join(Variaveis.obter_pasta_pdf(), f'{item} - PA.pdf')
            system(f'"{nomearquivo}"')
            nomearquivo = path.join(Variaveis.obter_pasta_pdf(), f'{item} - PreAnalise.pdf')
            system(f'"{nomearquivo}"')
            print(f'Tarefa {item}...Arquivo aberto.')
        print('')
        
    def finalizar_doc(self, subcomandos: list[str]) -> None:
        cont = 0
        if len(subcomandos) < 1:
            print("Erro: Necessário informar os números de protocolo ou ULP.\n")
            return
        if (subcomandos[0] == 'ulp'):
            self.finalizar_doc_lote()
        else:
            self.pre_processar('FINALIZAR DOCS ANÁLISE')
            for item in subcomandos:
                if (idx := self.base_dados.pesquisar_indice(item)) == None:
                    print(f"Erro: Tarefa {item} não foi encontrada na fila atual.\n")
                    continue
                t = TarefaSeguroDefeso(self.base_dados, idx)
                if self.finalizar_doc_item(t):
                    cont += 1
            self.pos_processar(cont)

    def finalizar_doc_lote(self):
        cont = 0
        self.pre_processar('FINALIZAR DOCS ANÁLISE')
        print("Usando lista personalizada.")
        for item in self.obter_listapersonalizada():
            if (idx := self.base_dados.pesquisar_indice(item)) == None:
                print(f"Erro: Tarefa {item} não foi encontrada na fila atual.\n")
                continue
            t = TarefaSeguroDefeso(self.base_dados, idx)
            if self.finalizar_doc_item(t):
                cont += 1
        self.pos_processar(cont)

    def finalizar_doc_item(self, t: TarefaSeguroDefeso) -> bool:
        lista = []
        protocolo = str(t.obter_protocolo())
        lista.append(f'{protocolo} - PreAnalise')
        lista.append(f'{protocolo} - Resultado')
        manipulador = ManipuladorPDF()
        manipulador.juntar(lista, f'{protocolo} - Analise')
        print(f'Tarefa {protocolo}...Juntado.') 

        return True

    #== GERAR DOCUMENTO DE ARRECADACAO ==#
    def gerar_docarrecada(self, subcomandos: list[str]) -> None:
        """Executa o programa 'Extrair Doc. Arrecadação' do processador."""
        if len(subcomandos) > 0 and (subcomandos[0] == 'ulp'):
            self.gerar_docarrecada_lote()
        else:
            self.gerar_docarrecada_base()
    
    def gerar_docarrecada_base(self) -> None:
        cont = 0
        self.pre_processar('DOC. ARRECADAÇÃO')
        for t in self.lista:
            tem_db = t.tem_dadosbasicos().e_verdadeiro
            esta_concluida = t.esta_concluida().e_verdadeiro
            if not tem_db or esta_concluida:
                continue
            if self.gerar_docarrecada_item(t):
                cont += 1
        self.pos_processar(cont)

    def gerar_docarrecada_lote(self) -> None:
        cont = 0
        self.pre_processar('DOC. ARRECADAÇÃO')
        print("Usando lista personalizada.")
        for item in self.obter_listapersonalizada():
            if (idx := self.base_dados.pesquisar_indice(item)) == None:
                print(f"Erro: Tarefa {item} não foi encontrada na fila atual.\n")
                continue
            t = TarefaSeguroDefeso(self.base_dados, idx)
            if self.gerar_docarrecada_item(t):
                cont += 1
        self.pos_processar(cont)

    def gerar_docarrecada_item(self, tarefa: TarefaSeguroDefeso) -> bool:
        """Gera o documento de arrecadação."""
        buffer_linha = ''
        cnis = self.cnis

        if cnis is None:
            return False
        protocolo = str(tarefa.obter_protocolo())
        cpf = str(tarefa.obter_cpf())
        buffer_linha = f"Tarefa {protocolo}..."
        print(buffer_linha, end='\r')
        if cnis.gerar_docarrecada(protocolo, cpf):
            buffer_linha += "Extrato gerado."
            print(buffer_linha)
            return True
        else:
            buffer_linha += "Erro: Extrato não gerado."
            print(buffer_linha)
            return False

    #== GERAR EXTRATO CNIS ==#
    def gerar_cnis(self, subcomandos: list[str]) -> None:
        """Executa o programa 'Extrair CNIS' do processador."""
        if len(subcomandos) > 0 and (subcomandos[0] == 'ulp'):
            self.gerar_cnis_lote()
        else:
            self.gerar_cnis_base()
    
    def gerar_cnis_base(self) -> None:
        cont = 0
        self.pre_processar('EXTRATO DO CNIS')
        for t in self.lista:
            tem_db = t.tem_dadosbasicos().e_verdadeiro
            esta_concluida = t.esta_concluida().e_verdadeiro
            if not tem_db or esta_concluida:
                continue
            if self.gerar_cnis_item(t):
                cont += 1
        self.pos_processar(cont)

    def gerar_cnis_lote(self) -> None:
        cont = 0
        self.pre_processar('EXTRATO DO CNIS')
        print("Usando lista personalizada.")
        for item in self.obter_listapersonalizada():
            if (idx := self.base_dados.pesquisar_indice(item)) == None:
                print(f"Erro: Tarefa {item} não foi encontrada na fila atual.\n")
                continue
            t = TarefaSeguroDefeso(self.base_dados, idx)
            if self.gerar_cnis_item(t):
                cont += 1
        self.pos_processar(cont)

    def gerar_cnis_item(self, tarefa: TarefaSeguroDefeso) -> bool:
        """Gera o extrato do CNIS."""
        buffer_linha = ''
        cnis = self.cnis

        if cnis is None:
            return False
        protocolo = str(tarefa.obter_protocolo())
        cpf = str(tarefa.obter_cpf())
        buffer_linha = f"Tarefa {protocolo}..."
        print(buffer_linha, end='\r')
        if cnis.gerar_extratosibe(protocolo, cpf):
            buffer_linha += "Extrato gerado."
            print(buffer_linha)
            return True
        else:
            buffer_linha += "Erro: Extrato não gerado."
            print(buffer_linha)
            return False
        
    #== GERAR EXTRATO PJ ==#
    def gerar_extratopj(self,subcomandos: list[str]) -> None:
        """Executa o programa 'Extrair PJ' do processador."""
        if len(subcomandos) > 0 and (subcomandos[0] == 'ulp'):
            self.gerar_extratopj_lote()
        else:
            self.gerar_extratopj_base()
    
    def gerar_extratopj_base(self) -> None:
        cont = 0
        self.pre_processar('EXTRATO DE PJ')
        for t in self.lista:
            tem_db = t.tem_dadosbasicos().e_verdadeiro
            esta_concluida = t.esta_concluida().e_verdadeiro
            if not tem_db or esta_concluida:
                continue
            if self.gerar_extratopj_item(t):
                cont += 1
        self.pos_processar(cont)

    def gerar_extratopj_lote(self) -> None:
        cont = 0
        self.pre_processar('EXTRATO DE PJ')
        print("Usando lista personalizada.")
        for item in self.obter_listapersonalizada():
            if (idx := self.base_dados.pesquisar_indice(item)) == None:
                print(f"Erro: Tarefa {item} não foi encontrada na fila atual.\n")
                continue
            t = TarefaSeguroDefeso(self.base_dados, idx)
            if self.gerar_extratopj_item(t):
                cont += 1
        self.pos_processar(cont)

    def gerar_extratopj_item(self, tarefa: TarefaSeguroDefeso) -> bool:
        """Gera o extrato do PJ."""
        buffer_linha = ''
        cnis = self.cnis

        if cnis is None:
            return False
        protocolo = str(tarefa.obter_protocolo())
        cpf = str(tarefa.obter_cpf())
        buffer_linha = f"Tarefa {protocolo}..."
        print(buffer_linha, end='\r')
        if cnis.gerar_extratopj(protocolo, cpf):
            buffer_linha += "Extrato gerado."
            print(buffer_linha)
            return True
        else:
            buffer_linha += "Erro: Extrato não gerado."
            print(buffer_linha)
            return False
        
    #== GERAR RGP ==#
    def gerar_rgp(self, subcomandos: list[str]) -> None:
        """Executa o programa 'Extrair Doc. Arrecadação' do processador."""
        if len(subcomandos) > 0 and (subcomandos[0] == 'ulp'):
            self.gerar_rgp_lote()
        else:
            self.gerar_rgp_base()
    
    def gerar_rgp_base(self) -> None:
        cont = 0
        self.pre_processar('CONSULTA RGP')
        for t in self.lista:
            tem_db = t.tem_dadosbasicos().e_verdadeiro
            esta_concluida = t.esta_concluida().e_verdadeiro
            if not tem_db or esta_concluida:
                continue
            if self.gerar_rgp_item(t):
                cont += 1
        self.pos_processar(cont)

    def gerar_rgp_lote(self) -> None:
        cont = 0
        self.pre_processar('CONSULTA RGP')
        print("Usando lista personalizada.")
        for item in self.obter_listapersonalizada():
            if (idx := self.base_dados.pesquisar_indice(item)) == None:
                print(f"Erro: Tarefa {item} não foi encontrada na fila atual.\n")
                continue
            t = TarefaSeguroDefeso(self.base_dados, idx)
            if self.gerar_rgp_item(t):
                cont += 1
        self.pos_processar(cont)

    def gerar_rgp_item(self, tarefa: TarefaSeguroDefeso) -> bool:
        """Gera o RGP."""
        buffer_linha = ''
        cnis = self.cnis

        if cnis is None:
            return False
        protocolo = str(tarefa.obter_protocolo())
        cpf = str(tarefa.obter_cpf())
        buffer_linha = f"Tarefa {protocolo}..."
        print(buffer_linha, end='\r')
        if cnis.gerar_rgp(protocolo, cpf):
            buffer_linha += "Extrato gerado."
            print(buffer_linha)
            return True
        else:
            buffer_linha += "Erro: Extrato não gerado."
            print(buffer_linha)
            return False
        
    #== GERAR REQ. RESULTADO ==#    
    def gerar_resultaoo(self, subcomandos: list[str]) -> None:
        """Gera o PDF com req. do SD processado."""
        if self.sd is None:
            return
        self.sd.abrir_consulta()
        if len(subcomandos) > 0 and (subcomandos[0] == 'ulp'):
            self.gerar_resultado_lote()
        else:
            self.gerar_resultado_base()
    
    def gerar_resultado_base(self) -> None:
        cont = 0
        self.pre_processar('GERAR RESULTADO SD')
        for t in self.lista:
            tem_db = t.tem_dadosbasicos().e_verdadeiro
            esta_concluida = t.esta_concluida().e_verdadeiro
            if not tem_db or esta_concluida:
                continue
            if self.consultar_sd_item(t):
                cont += 1
                time.sleep(3)
        self.pos_processar(cont)

    def gerar_resultado_lote(self) -> None:
        cont = 0
        self.pre_processar('GERAR RESULTADO SD')
        print("Usando lista personalizada.")
        for item in self.obter_listapersonalizada():
            if (idx := self.base_dados.pesquisar_indice(item)) == None:
                print(f"Erro: Tarefa {item} não foi encontrada na fila atual.\n")
                continue
            t = TarefaSeguroDefeso(self.base_dados, idx)
            if self.gerar_resultado_item(t):
                cont += 1
                time.sleep(3)
        self.pos_processar(cont)

    def gerar_resultado_item(self, tarefa: TarefaSeguroDefeso) -> bool:
        """Gera o documento de arrecadação."""
        buffer_linha = ''
        sd = self.sd

        if sd is None:
            return False
        protocolo = str(tarefa.obter_protocolo())
        nsd = str(tarefa.obter_segurodefeso())
        buffer_linha = f"Tarefa {protocolo}..."
        print(buffer_linha, end='\r')
        
        if sd.gerar_resultado(protocolo, nsd):
            buffer_linha += "Resultado gerado."
            print(buffer_linha)
            return True
        else:
            buffer_linha += "Erro: Resultado não gerado."
            print(buffer_linha)
            return False
      
    def obter_comandos(self) -> dict:
        """Retorna os comandos exclusivos do processador."""
        return self.comandos
    
    def obter_marcacoes(self):
        """Retorna as marcações disponíveis."""
        return self.marcacoes
    
    def obter_defeso(self, portaria: str, defeso: str) -> dict:
        """."""
        #defeso = self.defesos[portaria, defeso]
        return dict()

    def processar_conclusao(self) -> None:
        """Processa a conclusão de tarefas."""
        cont = 0
        protocolo = ''
        nomearquivo = ''
        texto = ''
        numero = 0

        self.pre_processar('CONCLUSÃO DE TAREFAS')
        for t in self.lista:
            if self.get.suspender_processamento:
                print('Processamento suspenso.\n')
                break
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
                        self.get.fechar_tarefa()
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

    def processar_dados(self) -> None:
        """Processa os daods carregados."""
        tamanho = self.base_dados.tamanho
        self.lista.clear()
        for i in range(tamanho):
            tarefa = TarefaSeguroDefeso(self.base_dados, i)
            if not tarefa.esta_concluida().e_verdadeiro:
                self.lista.append(tarefa)
        self.definir_comandos()
        self.definir_marcacoes()

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