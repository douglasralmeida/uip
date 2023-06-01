## Codificado por Douglas Rodrigues de Almeida.
## Março de 2023
"""Tarefa de Prorrogação de Salário-Maternidade"""

from .utils import bool_tobit, bool_tostring
import pandas as pd
from tarefa import Tarefa
from basedados import BaseDados

class TarefaProrrogacaoSalMaternidade(Tarefa):
    """Classe da Tarefa de Prorrogação de Salário Maternidade"""
    def __init__(self, dados: BaseDados, i: int) -> None:
        super().__init__(dados, i)

    def __str__(self) -> str:
        """Descrição da tarefa de auxílio-acidente."""
        resultado = super().__str__()
        resultado += f'Documentação apresentada: {bool_tostring(self.tem_documentacao())}\n'
        resultado += f'Exigência de documentação: {bool_tostring(self.tem_exigencia())}\n'
        if self.tem_exigencia():
            resultado += f'\tFeita em: {"a"}\n'
            resultado += f'\tVence em: {"a"}\n'
            resultado += f'\tCumprida: {"a"}\n'
        resultado += f'Subtarefa PM: {self.obter_subtarefa()}\n'
        resultado += f'PM realizada: {bool_tostring(self.obter_fase_pericia_realizada())}\n'
        #resultado += f'PM lançada: {bool_tostring(self.obter_fase())}\n'
        resultado += f'Atualização despachada: {bool_tostring(self.obter_fase_atualizacao_despachada())}\n'
        resultado += f'Possui PDF com resumo: {bool_tostring(self.tem_arquivopdfresumo())}\n'
        resultado += f'Resultado: {self.obter_resultado()}\n'
        resultado += f'Impedimentos: {self.obter_impedimento()}\n'
        resultado += f'Data de conclusão: {self.obter_data_conclusao()}\n'
        resultado += f'Observações: {"(sem observações)"}\n'
        return resultado
       
    def alterar_msg_criacaosub(self, valor: str) -> None:
        """Registra o erro ocorrido quando da criação da subtarefa"""
        self.base_dados.alterar_atributo(self.pos, "msgerro_criacaosub", valor)
    
    def alterar_subtarefa(self, subtarefa: str) -> None:
        """Altera a subtarefa."""
        self.base_dados.alterar_atributo(self.pos, 'subtarefa', str(subtarefa))

    def alterar_subtarefa_coletada(self, valor: bool) -> None:
        """Grava na tarefe se a subtarefa foi coletada."""
        self.base_dados.alterar_atributo(self.pos, "subtarefa_coletada", bool_tobit(valor))

    def concluir_fase_subtarefa(self) -> None:
        """Informa que a tarefa já possui subtarefa gerada."""
        self.base_dados.alterar_atributo(self.pos, 'tem_subtarefa', "1")
        if self.base_dados.checar_atributo_nulo(self.pos, 'tem_prim_subtarefa'):
            self.base_dados.alterar_atributo(self.pos, "tem_prim_subtarefa", "1")
            self.base_dados.alterar_atributo(self.pos, "data_subtarefa", pd.to_datetime('today'))
        
    def concluir_fase_pericia_realizada(self) -> None:
        """Registra que a tarefa já teve a perícia realizada."""
        self.base_dados.alterar_atributo(self.pos, 'pericia_realizada', "1")

    def concluir_fase_atualizacao(self) -> None:
        """Informa que o benefício foi atualizado."""
        self.base_dados.alterar_atributo(self.pos, 'atualizacao_despachada', '1')

    def marcar_arquivopdf_pericia(self) -> None:
        """Registra que o relatório da perícia em PDF foi gerado."""
        self.base_dados.alterar_atributo(self.pos, 'arquivopdf_pericia', "1")
  
    def obter_fase_subtarefa_gerada(self) -> bool:
        """Retorna se a subtarefa de PM foi gerada."""
        return self.base_dados.checar_atributo_verdadeiro(self.pos, 'tem_subtarefa')       
              
    def obter_fase_pericia_realizada(self) -> bool:
        """Retorna se a PM foi realizada."""
        return self.base_dados.checar_atributo_verdadeiro(self.pos, "pericia_realizada")
    
    def obter_fase_atualizacao_despachada(self) -> bool:
        """Indica se a atualização do benefício foi despachada."""
        return self.base_dados.obter_atributo(self.pos, 'atualizacao_despachada')

    def obter_subtarefa(self) -> str:
        """Retorna o protocolo da subtarefa de PM."""
        return self.base_dados.obter_atributo(self.pos, 'subtarefa')
    
    def tem_erro_geracaosub(self) -> bool:
        """Retorna se houve erro na geração da subtarefa."""
        return self.base_dados.checar_atributo_naonulo(self.pos, "msgerro_criacaosub") 