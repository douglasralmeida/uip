## Codificado por Douglas Rodrigues de Almeida.
## Março de 2023
"""Tarefa do GET"""

import pandas as pd
from .utils import bool_tostring, valor_tostring
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
        resultado += f'Tarefa concluída: {bool_tostring(self.obter_fase_conclusao())}\n'
        resultado += f'Dados coletados: {bool_tostring(self.obter_fase_dadoscoletados())}\n'
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

        return resultado
    
    def alterar_beneficio(self, novo_beneficio: str) -> None:
        """Altera o número do benefício."""
        self.base_dados.alterar_atributo(self.pos, 'beneficio', novo_beneficio)

    def alterar_cpf(self, cpf: str) -> None:
        """Altera o CPF."""
        self.base_dados.alterar_atributo(self.pos, 'cpf', cpf)   

    def alterar_der(self, der: date) -> None:
        """Altera a data de entrada do requerimento."""
        self.base_dados.alterar_atributo(self.pos, 'der', der)

    def alterar_nit(self, nit: str) -> None:
        """Altera o NIT."""
        self.base_dados.alterar_atributo(self.pos, 'nit', nit)
        
    def alterar_resultado(self, resultado: str) -> None:
        """Altera o resultado da análise."""
        self.base_dados.alterar_atributo(self.pos, 'resultado', resultado)

    def concluir_fase_dadoscoletados(self) -> None:
        """Informa que a tarefa possui dados básicos coletados'."""
        self.base_dados.alterar_atributo(self.pos, 'tem_dadosbasicos', '1')

    def concluir_fase_exigencia(self) -> None:
        """Informa que a tarefa está aguardando cumprimento de exigência."""
        self.base_dados.alterar_atributo(self.pos, "tem_exigencia", "1")
        if self.checar_atributo_nulo('tem_prim_exigencia'):
            self.base_dados.alterar_atributo(self.pos, "tem_prim_exigencia", "1")
            self.base_dados.alterar_atributo(self.pos, "data_exigencia", pd.to_datetime('today'))
            self.base_dados.alterar_atributo(self.pos, "vencim_exigencia", pd.to_datetime('today') + pd.TimedeltaIndex(35, unit='D'))

    def concluir_fase_conclusao(self) -> None:
        """Informa que a tarefa está concluída e altera a data de conclusão para hoje."""
        self.base_dados.alterar_atributo(self.pos, 'concluida', '1')
        self.base_dados.alterar_atributo(self.pos, 'data_conclusao', pd.to_datetime('today').date())        
     
    def marcar_pdfresumo(self) -> None:
        """Ativa o indicador da tarefa que possui arquivo PDF com resumo da análise."""
        self.base_dados.alterar_atributo(self.pos, 'arquivopdfresumo', '1')

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

    def obter_fase_dadoscoletados(self) -> bool:
        """Indica se a tarefa possui dados básicos coletados."""
        return self.base_dados.checar_atributo_verdadeiro(self.pos, 'tem_dadosbasicos')

    def obter_fase_analise_beninacumulavel(self) -> bool:
        """Indica se a tarefa possui análise de acumulação de benefícios."""
        return self.base_dados.checar_atributo_naonulo(self.pos, 'possui_ben_inacumulavel')
    
    def obter_fase_exigencia(self) -> bool:
        """Indica se a tarefa teve exigência gerada."""
        return self.base_dados.checar_atributo_naonulo(self.pos, "tem_exigencia")

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
    
    def obter_nit(self) -> str:
        """Retorna o NIT."""
        return self.base_dados.obter_atributo(self.pos, 'nit')

    def obter_protocolo(self) -> str:
        """Retorna o protocolo."""
        return self.base_dados.obter_atributo(self.pos, 'protocolo')

    def obter_resultado(self) -> str:
        """Retorna o resultado da análise."""
        return self.base_dados.obter_atributo(self.pos, 'resultado')
    
    def obter_vencimento_exigencia(self) -> str:
        """Retorna a data do vencimento da exigência."""
        return self.base_dados.obter_atributo(self.pos, 'vencim_exigencia')
    
    def tem_arquivopdfresumo(self) -> str:
        """Indica se a tarefa possui arquivo PDF de resumo para anexo ao GET."""
        return self.base_dados.checar_atributo_verdadeiro(self.pos, "arquivopdfresumo")

    def tem_ben_inacumulavel(self) -> str:
        """Indica se o requerente possui benefício inacumulável."""
        return self.base_dados.checar_atributo_verdadeiro(self.pos, 'possui_ben_inacumulavel')

    def tem_dadosbasicos(self) -> bool:
        """Indica se a XXX tem dados básicos."""
        return self.base_dados.checar_atributo_verdadeiro(self.pos, 'tem_dadosbasicos')

    def tem_documentacao(self) -> bool:
         """Indica se a tarefa possui documentação para análise."""
         return self.base_dados.checar_atributo_verdadeiro(self.pos, "tem_documentacao")
    
    def tem_exigencia(self) -> bool:
        """Indica se a tarefa possui exigência para o requerente."""
        return self.base_dados.checar_atributo_naonulo(self.pos, "data_exigencia")