## Codificado por Douglas Rodrigues de Almeida.
## Março de 2023
"""Tarefa do GET"""

import pandas as pd
from anexacao import Anexacao
from basedados import BaseDados, TipoBooleano, TipoData, TipoInteiro, TipoTexto
from exigencia import Exigencia
from impedimento import Impedimento
from resultado import Resultado

class Tarefa:
    """Classe para a tarefa do GET."""
    def __init__(self, base_dados: BaseDados, i: int) -> None:
        #Índice da tarefa na base de dados.
        self.pos = i

        #Base de dados do UIP.
        self.base_dados = base_dados
    
    def pre_tostr(self) -> str:
        resultado = f'Protocolo: {self.obter_protocolo()}\n'
        resultado += f'Tarefa concluída: {self.esta_concluida()}\n'
        resultado += f'Dados coletados: {self.tem_dadosbasicos()}\n'
        resultado += f'\tCPF: {self.obter_cpf()}\n'
        resultado += f'\tNIT: {self.obter_nit()}\n'
        resultado += f'\tDER: {self.obter_der()}\n'
        exigencia = self.obter_exigencia()
        resultado += f'Exigência: {exigencia}\n'
        resultado += '--------------------------------------------------\n'

        return resultado

    def pos_tostr(self) -> str:
        resultado = '--------------------------------------------------\n'
        sobrest = self.tem_sobrestamento()
        resultado += f'Sobrestado: {sobrest.e_verdadeiro}\n'
        if sobrest.e_verdadeiro:
            resultado += f'\tNº da subtarefa de sobrestamento: {self.obter_sub_sobrestado()}\n'
        anexacao = self.obter_anexacao_analise()
        resultado += f'Anexação PDF Análise: {anexacao}\n'
        resultado += f'Resultado: {self.obter_resultado()}\n'
        resultado += f'Impedimentos: {self.obter_impedimento()}\n'
        resultado += f'Data de conclusão: {self.obter_data_conclusao()}\n'
        resultado += f'Observações: {self.obter_observacoes()}\n'
        resultado += f'Tarefa conclusa: {self.esta_concluso()}\n'

        return resultado
    
    def alterar_anexacao_analise(self, analise: Anexacao) -> None:
        """Altera as informações sobre a anexação do PDF da análise"""
        self.base_dados.alterar_atributo(self.pos, 'tem_pdfresumoanexo', analise.tem_anexo().valor)

    def alterar_cpf(self, cpf: TipoTexto) -> None:
        """Altera o CPF."""
        self.base_dados.alterar_atributo(self.pos, 'cpf', cpf.valor)

    def alterar_der(self, der: TipoData) -> None:
        """Altera a data de entrada do requerimento."""
        self.base_dados.alterar_atributo(self.pos, 'der', der.valor)

    def alterar_exigencia(self, exigencia: Exigencia, exig_pm: bool) -> None:
        """Altera dados da exigência"""
        self.base_dados.alterar_atributo(self.pos, 'tem_exigencia', exigencia.tem_exigencia().valor)
        if not exig_pm:
            self.base_dados.alterar_atributo(self.pos, 'tem_documentacao', exigencia.esta_cumprida().valor)
        self.base_dados.alterar_atributo(self.pos, 'tem_prim_exigencia', exigencia.obter_primeira_exig().valor)
        self.base_dados.alterar_atributo(self.pos, 'data_exigencia', exigencia.obter_realizacao().valor)
        self.base_dados.alterar_atributo(self.pos, 'vencim_exigencia', exigencia.obter_vencimento().valor)
        self.base_dados.alterar_atributo(self.pos, "exigenciapm_comerro", exigencia.esta_comerro().valor)

    def alterar_impedimento(self, impedimento: Impedimento) -> None:
        """Adiciona um impedimento à tarefa."""
        self.base_dados.alterar_atributo(self.pos, 'impedimentos', impedimento.id)

    def alterar_nit(self, nit: TipoTexto) -> None:
        """Altera o NIT."""
        self.base_dados.alterar_atributo(self.pos, 'nit', nit.valor)
        
    def alterar_resultado(self, resultado: Resultado) -> None:
        """Altera o resultado da análise."""
        self.base_dados.alterar_atributo(self.pos, 'resultado', resultado.id)

    def alterar_temdoc(self, valor: TipoBooleano) -> None:
        """Ativa ou desativa o indicador possui documentação."""
        self.base_dados.alterar_atributo(self.pos, 'tem_documentacao', valor.valor)

    def concluir(self, data_conclusao: TipoData | None) -> None:
        """Informa que a tarefa está concluída e altera a data de conclusão para hoje."""
        self.base_dados.alterar_atributo(self.pos, 'concluida', '1')
        if data_conclusao is None:
            self.base_dados.alterar_atributo(self.pos, 'data_conclusao', pd.to_datetime('today').floor('D'))
        else:
            self.base_dados.alterar_atributo(self.pos, 'data_conclusao', data_conclusao.valor)

    def esta_concluida(self) -> TipoBooleano:
        """Indica se a tarefa foi concluída."""
        valor = self.base_dados.obter_atributo(self.pos, 'concluida')
        return TipoBooleano(valor)
    
    def esta_concluso(self) -> TipoBooleano:
        """Indica se a tarefa está pronta para ser concluída."""
        valor = self.base_dados.obter_atributo(self.pos, 'concluso')    
        return TipoBooleano(valor)

    def marcar_conclusa(self) -> None:
        """Informa que a tarefa está pronta para ser concluída'."""
        self.base_dados.alterar_atributo(self.pos, 'concluso', '1')

    def marcar_tem_dadosbasicos(self) -> None:
        """Informa que a tarefa possui dados básicos coletados'."""
        self.base_dados.alterar_atributo(self.pos, 'tem_dadosbasicos', '1')

    def marcar_japossui_exigencia(self) -> None:
        """Informa que a tarefa já possui exigência anterior."""
        self.base_dados.alterar_atributo(self.pos, 'tem_prim_exigencia', '0')

    def obter_anexacao_analise(self) -> Anexacao:
        """Obtem os dados sobre a anexação do PDF da análise"""
        tem_pdf = self.base_dados.checar_atributo_verdadeiro(self.pos, "tem_pdfresumoanexo")
        existe_erro = self.base_dados.checar_atributo_verdadeiro(self.pos, "erro_anexarpdfresumo")
        anexacao = Anexacao(TipoBooleano(tem_pdf), TipoBooleano(existe_erro))
        return anexacao

    def obter_cpf(self) -> TipoTexto:
        """Retorna o CPF."""
        valor = self.base_dados.obter_atributo(self.pos, 'cpf')
        return TipoTexto(valor)

    def obter_data_conclusao(self) -> TipoData:
        """Retorna a data de conclusão da tarefa."""
        data_conclusao = self.base_dados.obter_atributo(self.pos, 'data_conclusao')
        return TipoData(data_conclusao)

    def obter_der(self) -> TipoData:
        """Retorna a DER da tarefa."""
        der = self.base_dados.obter_atributo(self.pos, 'der')
        return TipoData(der)
    
    def obter_exigencia(self) -> Exigencia:
        """Retorna dados de exigência"""
        valor = self.base_dados.obter_atributo(self.pos, 'tem_exigencia')
        exigencia = Exigencia(TipoBooleano(valor))
        data = self.base_dados.obter_atributo(self.pos, 'data_exigencia')
        exigencia.alterar_realizacao(TipoData(data))
        data = self.base_dados.obter_atributo(self.pos, 'vencim_exigencia')
        exigencia.alterar_vencimento(TipoData(data))
        valor = self.base_dados.obter_atributo(self.pos, 'tem_prim_exigencia')
        exigencia.alterar_primeira_exig(TipoBooleano(valor))
        #valor = self.base_dados.obter_atributo(self.pos, "exigenciapm_comerro")
        #exigencia.marcar_erro(TipoBooleano(valor))
        return exigencia
        
    def obter_idx(self) -> int:
        """Retorna o índice da tarefa na base de dados."""
        return self.pos
    
    def obter_impedimento(self) -> TipoTexto:
         """Retorna o id do impedimento da tarefa."""
         impedimento_id = self.base_dados.obter_atributo(self.pos, "impedimentos")
         return TipoTexto(impedimento_id)
    
    def obter_nit(self) -> TipoTexto:
        """Retorna o NIT."""
        nit = self.base_dados.obter_atributo(self.pos, 'nit')
        return TipoTexto(nit)
    
    def obter_modelo_despacho(self, tipo: str) -> TipoTexto:
        """a."""
        texto = self.base_dados.obter_atributo(self.pos, tipo)
        return TipoTexto(texto)
    
    def obter_observacoes(self) -> TipoTexto:
        """"""
        valor = "(sem observações)"
        return TipoTexto(valor)

    def obter_protocolo(self) -> TipoInteiro:
        """Retorna o protocolo."""
        protocolo = self.base_dados.obter_atributo(self.pos, 'protocolo')
        return TipoInteiro(protocolo)

    def obter_resultado(self) -> TipoTexto:
        """Retorna o ID do resultado da análise."""
        resultado_id = self.base_dados.obter_atributo(self.pos, 'resultado')
        return TipoTexto(resultado_id)
    
    def obter_sub_sobrestado(self) -> TipoInteiro:
        """Retorna o protocolo da subtarefa de sobrestamento."""
        subtarefa = self.base_dados.obter_atributo(self.pos, 'sub_sobrestado')
        return TipoInteiro(subtarefa)
    
    def registrar_desistencia(self) -> None:
        """Marca a tarefa com desistência do requerente."""
        self.base_dados.limpar_atributos(self.pos)
        self.base_dados.alterar_atributo(self.pos, 'resultado', 'desistencia')
    
    def remover_impedimento(self) -> None:
        """Remove o impedimento da tarefa."""
        self.base_dados.remover_atributo(self.pos, 'impedimentos')

    def remover_sobrestamento(self) -> None:
        """Remove o sobrestamento da tarefa."""
        self.base_dados.remover_atributo(self.pos, 'sub_sobrestado')

    def sobrestar(self, subtarefa: TipoInteiro) -> None:
        """Altera a subtarefa de sobrestado."""
        self.base_dados.alterar_atributo(self.pos, 'sub_sobrestado', subtarefa.valor)     

    def tem_dadosbasicos(self) -> TipoBooleano:
        """Indica se a tarefa tem dados básicos."""
        valor = self.base_dados.checar_atributo_verdadeiro(self.pos, 'tem_dadosbasicos')
        return TipoBooleano(valor)
    
    def tem_desistencia(self) -> TipoBooleano:
         """Indica se a tarefa possui desistencia."""
         res = self.base_dados.obter_atributo(self.pos, "resultado")
         valor = pd.notna(res) and res in ['desistencia']
         return TipoBooleano(valor)

    def tem_documentacao(self) -> TipoBooleano:
         """Indica se a tarefa possui documentação para análise."""
         valor = self.base_dados.checar_atributo_verdadeiro(self.pos, "tem_documentacao")
         return TipoBooleano(valor)
    
    def tem_sobrestamento(self) -> TipoBooleano:
         """Indica se a tarefa está sobrestada."""
         valor = self.base_dados.checar_atributo_naonulo(self.pos, "sub_sobrestado")
         return TipoBooleano(valor)
    
    def tem_impedimento(self) -> TipoBooleano:
         """Indica se a tarefa possui impedimento para conclusão da análise."""
         valor = self.base_dados.checar_atributo_naonulo(self.pos, "impedimentos")
         return TipoBooleano(valor)