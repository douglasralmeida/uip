## Codificado por Douglas Rodrigues de Almeida.
## Março de 2023
"""Tarefa do GET"""

import pandas as pd
from .utils import bool_tostring, bool_tobit, valor_tostring
from agendamento import Agendamento
from basedados import BaseDados
from datetime import date

class Tarefa:
    """Classe para a tarefa do GET."""
    def __init__(self, base_dados: BaseDados, i: int) -> None:
        #Índice da tarefa na base de dados.
        self.pos = i

        #Base de dados do UIP.
        self.base_dados = base_dados

    def __str__(self) -> str:
        resultado = f'Protocolo: {self.obter_protocolo()}\n'
        resultado += f'Tarefa conclusa: {bool_tostring(self.obter_fase_concluso())}\n'
        resultado += f'Tarefa concluída: {bool_tostring(self.obter_fase_conclusao())}\n'
        resultado += f'Dados coletados: {bool_tostring(self.tem_dadosbasicos())}\n'
        resultado += f'CPF: {valor_tostring(self.obter_cpf())}\n'
        resultado += f'NIT: {valor_tostring(self.obter_nit())}\n'
        resultado += f'DER: {valor_tostring(self.obter_der())}\n'
        resultado += f'NB: {valor_tostring(self.obter_beneficio())}\n'
        resultado += f'Análise benefícios inacumuláveis realizada: {bool_tostring(self.obter_fase_analise_beninacumulavel())}\n'
        if self.obter_fase_analise_beninacumulavel():
            resultado += f'Possui benefício inacumulável: {bool_tostring(self.tem_ben_inacumulavel())}\n'
            if self.tem_ben_inacumulavel():
                resultado += f'Benefício inacumulável: {self.obter_beneficio_inacumulavel()}\n'
        else:
            resultado += 'Possui benefício inacumulável: não informado\n'
            resultado += 'Benefício inacumulável: não informado\n'
        resultado += f'Tem exigência: {self.tem_exigencia()}\n'
        resultado += f'Data do vencimento da exigência: {self.obter_vencimento_exigencia()}\n'
        resultado += f'Sobrestado: {bool_tostring(self.tem_sobrestamento())}\n'
        if self.tem_sobrestamento():
            resultado += f'Nº da subtarefa de sobrestamento: {self.obter_sub_sobrestado()}\n'

        return resultado
    
    def alterar_beneficio(self, novo_beneficio: str) -> None:
        """Altera o número do benefício."""
        self.base_dados.alterar_atributo(self.pos, 'beneficio', novo_beneficio)

    def alterar_beninacumluavel(self, valor: bool) -> None:
        """Ativa ou desativa o indicador de benefício inacumulável."""
        self.base_dados.alterar_atributo(self.pos, 'possui_ben_inacumulavel', bool_tobit(valor))

    def alterar_cpf(self, cpf: str) -> None:
        """Altera o CPF."""
        self.base_dados.alterar_atributo(self.pos, 'cpf', cpf)   

    def alterar_der(self, der: date) -> None:
        """Altera a data de entrada do requerimento."""
        self.base_dados.alterar_atributo(self.pos, 'der', der)

    def alterar_impedimento(self, impedimento_id: str) -> None:
        """Adiciona um impedimento à tarefa."""
        self.base_dados.alterar_atributo(self.pos, 'impedimentos', impedimento_id)

    def alterar_nit(self, nit: str) -> None:
        """Altera o NIT."""
        self.base_dados.alterar_atributo(self.pos, 'nit', nit)

    def alterar_pdfresumo(self, valor: bool) -> None:
        """Ativa ou desativa o indicador da tarefa que não possui arquivo PDF com resumo da análise."""
        self.base_dados.alterar_atributo(self.pos, 'tem_pdfresumoanexo', bool_tobit(valor))
        
    def alterar_resultado(self, resultado_id: str) -> None:
        """Altera o resultado da análise."""
        self.base_dados.alterar_atributo(self.pos, 'resultado', resultado_id)

    def alterar_sub_sobrestado(self, subtarefa: str) -> None:
        """Altera a subtarefa de sobrestado."""
        self.base_dados.alterar_atributo(self.pos, 'sub_sobrestado', subtarefa)

    def alterar_temdoc(self, valor: bool) -> None:
        """Ativa ou desativa o indicador possui documentação."""
        self.base_dados.alterar_atributo(self.pos, 'tem_documentacao', bool_tobit(valor))

    def concluir_fase_dadoscoletados(self) -> None:
        """Informa que a tarefa possui dados básicos coletados'."""
        self.base_dados.alterar_atributo(self.pos, 'tem_dadosbasicos', '1')

    def concluir_fase_exigencia(self, registrar_data: bool) -> None:
        """Informa que a tarefa está aguardando cumprimento de exigência."""
        self.base_dados.alterar_atributo(self.pos, "tem_exigencia", "1")
        if self.base_dados.checar_atributo_nulo(self.pos, 'tem_prim_exigencia'):
            self.base_dados.alterar_atributo(self.pos, "tem_prim_exigencia", "1")
        if registrar_data:
            self.base_dados.alterar_atributo(self.pos, "data_exigencia", pd.to_datetime('today'))
            self.base_dados.alterar_atributo(self.pos, "vencim_exigencia", pd.to_datetime('today') + pd.TimedeltaIndex([35], unit='D'))

    def concluir_fase_concluso(self) -> None:
        """Informa que a tarefa está pronta para ser concluída'."""
        self.base_dados.alterar_atributo(self.pos, 'concluso', '1')

    def concluir_fase_conclusao(self) -> None:
        """Informa que a tarefa está concluída e altera a data de conclusão para hoje."""
        self.base_dados.alterar_atributo(self.pos, 'concluida', '1')
        self.base_dados.alterar_atributo(self.pos, 'data_conclusao', pd.to_datetime('today').date())

    def marcar_japossui_exigencia(self) -> None:
        """Informa que a tarefa já possui exigência anterior."""
        self.base_dados.alterar_atributo(self.pos, "tem_prim_exigencia", "0")

    def marcar_japossui_subtarefa(self) -> None:
        """Informa que a tarefa já possui subtarefa criada anteriormente."""
        self.base_dados.alterar_atributo(self.pos, "tem_prim_subtarefa", "0")

    def cumprir_exigencia(self) -> None:
        """Cumpre a exigência."""
        self.base_dados.alterar_atributo(self. pos, 'tem_exigencia', '0')
        self.base_dados.alterar_atributo(self. pos, 'tem_documentacao', bool_tobit(True))

    def obter_agendamento(self) -> Agendamento:
        """Retorna as informações do agendamento de PM."""
        da = self.base_dados.obter_atributo(self.pos, 'dataagendamento')
        ha = self.base_dados.obter_atributo(self.pos, 'horaagendamento')
        la = self.base_dados.obter_atributo(self.pos, 'localagendamento')
        if pd.isna(da) | pd.isna(ha) | pd.isna(la):
            return None
        else:
            return Agendamento(da, ha, la)

    def obter_beneficio(self) -> str:
        """Retorna o número do benefício."""
        return self.base_dados.obter_atributo(self.pos, 'beneficio')        
   
    def obter_beneficio_inacumulavel(self) -> str:
        """Retorna a espécie e o número do benefício incacumulável."""
        especie = self.base_dados.obter_atributo(self.pos, 'especie_inacumulavel')
        nb = self.base_dados.obter_atributo(self.pos, 'nb_inacumulavel')
        return f'{especie}/{nb}'

    def obter_cpf(self) -> str:
        """Retorna o CPF."""
        return self.base_dados.obter_atributo(self.pos, 'cpf')

    def obter_fase_analise_beninacumulavel(self) -> bool:
        """Indica se a tarefa possui análise de acumulação de benefícios."""
        return self.base_dados.checar_atributo_naonulo(self.pos, 'possui_ben_inacumulavel')
    
    def obter_fase_concluso(self) -> bool:
        """Indica se a tarefa está pronta para ser concluída."""
        return self.base_dados.checar_atributo_verdadeiro(self.pos, 'concluso')

    def obter_fase_conclusao(self) -> bool:
        """Indica se a tarefa foi concluída."""
        return self.base_dados.checar_atributo_verdadeiro(self.pos, 'concluida')

    def obter_data_conclusao(self) -> bool:
        """Retorna a data de conclusão da tarefa."""
        return self.base_dados.obter_atributo(self.pos, 'data_conclusao')

    def obter_der(self) -> str:
        """Retorna a DER da tarefa."""
        return self.base_dados.obter_atributo(self.pos, 'der')
    
    def obter_idx(self) -> int:
        """Retorna o índice da tarefa na base de dados."""
        return self.pos
    
    def obter_impedimento(self) -> str:
         """Retorna o impedimento da tarefa."""
         return self.base_dados.obter_atributo(self.pos, "impedimentos")
    
    def obter_nit(self) -> str:
        """Retorna o NIT."""
        return self.base_dados.obter_atributo(self.pos, 'nit')

    def obter_protocolo(self) -> str:
        """Retorna o protocolo."""
        return self.base_dados.obter_atributo(self.pos, 'protocolo')

    def obter_resultado(self) -> str:
        """Retorna o resultado da análise."""
        return self.base_dados.obter_atributo(self.pos, 'resultado')
    
    def obter_sub_sobrestado(self) -> str:
        """Retorna o protocolo da subtarefa de sobrestamento."""
        return self.base_dados.obter_atributo(self.pos, 'sub_sobrestado')
    
    def obter_vencimento_exigencia(self) -> str:
        """Retorna a data do vencimento da exigência."""
        return self.base_dados.obter_atributo(self.pos, 'vencim_exigencia')
    
    def registrar_desistencia(self) -> None:
        """Marca a tarefa com desistência do requerente."""
        self.base_dados.limpar_atributos(self.pos)
        self.base_dados.alterar_atributo(self.pos, 'resultado', 'desistencia')
    
    def remover_impedimento(self) -> None:
        """Remove o impedimento da tarefa."""
        self.base_dados.remover_atributo(self.pos, 'impedimentos')
    
    def tem_arquivopdfresumo(self) -> str:
        """Indica se a tarefa possui arquivo PDF de resumo para anexo ao GET."""
        return self.base_dados.checar_atributo_verdadeiro(self.pos, "tem_pdfresumoanexo")

    def tem_ben_inacumulavel(self) -> str:
        """Indica se o requerente possui benefício inacumulável."""
        return self.base_dados.checar_atributo_verdadeiro(self.pos, 'possui_ben_inacumulavel')

    def tem_dadosbasicos(self) -> bool:
        """Indica se a XXX tem dados básicos."""
        return self.base_dados.checar_atributo_verdadeiro(self.pos, 'tem_dadosbasicos')
    
    def tem_desistencia(self) -> bool:
         """Indica se a tarefa possui desistencia."""
         res = self.base_dados.obter_atributo(self.pos, "resultado")
         return pd.notna(res) and res in ['desistencia']

    def tem_documentacao(self) -> bool:
         """Indica se a tarefa possui documentação para análise."""
         return self.base_dados.checar_atributo_verdadeiro(self.pos, "tem_documentacao")
    
    def tem_exigencia(self) -> bool:
        """Indica se a tarefa possui exigência para o requerente."""
        return self.base_dados.checar_atributo_verdadeiro(self.pos, "tem_exigencia")
    
    def tem_sobrestamento(self) -> bool:
         """Indica se a tarefa está sobrestada."""
         return self.base_dados.checar_atributo_naonulo(self.pos, "sub_sobrestado")
    
    def tem_impedimento(self) -> bool:
         """Indica se a tarefa possui impedimento para conclusão da análise."""
         return self.base_dados.checar_atributo_naonulo(self.pos, "impedimentos")