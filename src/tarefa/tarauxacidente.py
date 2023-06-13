## Codificado por Douglas Rodrigues de Almeida.
## Março de 2023
"""Tarefa de Auxílio-Acidente"""

import pandas as pd
from .utils import bool_tobit, bool_tostring
from .tarefa import Tarefa
from agendamento import Agendamento
from basedados import BaseDados

class TarefaAuxilioAcidente(Tarefa):
    """Classe da Tarefa de Auxílio-Acidente"""
    def __init__(self, dados: BaseDados, i: int) -> None:
        super().__init__(dados, i)

    def __str__(self) -> str:
        """Descrição da tarefa de auxílio-acidente."""
        resultado = super().__str__()
        resultado += f'OL Mantenedor: {self.obter_olm()}\n'
        resultado += f'Subtarefa PM: {self.obter_subtarefa()}\n'
        resultado += f'Perícia agendada: {bool_tostring(self.obter_fase_agendapm())}\n'
        if self.obter_fase_agendapm():
            agenda = self.obter_agendamento()
            resultado += f'\tPerícia em {agenda}\n'
        resultado += f'Comprovante de agendameto da PM anexado: {bool_tostring(self.obter_fase_pdfagendapm_anexo())}\n'
        resultado += f'Exigência do agendamento da PM gerada: {bool_tostring(self.tem_exigencia())}\n'
        resultado += f'PM cumprida: {bool_tostring(self.obter_fase_pericia_cumprida())}\n'
        resultado += f'PM realizada: {bool_tostring(self.tem_pericia_realizada())}\n'
        resultado += f'Subtarefa PM cancelada: {bool_tostring(self.obter_fase_subtarefa_cancelada())}\n'
        resultado += f'Benefício habilitado: {bool_tostring(self.obter_fase_beneficio_habilitado())}\n'
        if self.obter_fase_beneficio_habilitado():
            resultado += f'Nº do benefício: {self.obter_beneficio()}\n'
        resultado += f'PM lançada: {bool_tostring(self.tem_pericia_lancada())}\n'
        resultado += f'Benefício despachado: {bool_tostring(self.obter_fase_beneficio_despachado())}\n'
        resultado += f'Possui PDF com resumo: {bool_tostring(self.tem_arquivopdfresumo())}\n'
        resultado += f'Resultado: {self.obter_resultado()}\n'
        resultado += f'Impedimentos: {self.obter_impedimento()}\n'
        resultado += f'Data de conclusão: {self.obter_data_conclusao()}\n'
        resultado += f'Observações: {"(sem observações)"}\n'

        return resultado
    
    def agendamento_foicoletado(self) -> bool:
        """Retorna se o agendamento foi gerado ou coletado."""
        return self.base_dados.checar_atributo_verdadeiro(self.pos, "agenda_coletada")

    def alterar_agendamento(self, agendamento: Agendamento) -> None:
        """Altera os dados do agendamento da PM"""
        data = pd.to_datetime(agendamento.data, dayfirst=True, format='%d/%m/%Y').floor('D')
        self.base_dados.alterar_atributo(self.pos, 'dataagendamento', data)
        self.base_dados.alterar_atributo(self.pos, 'horaagendamento', agendamento.hora)
        self.base_dados.alterar_atributo(self.pos, 'localagendamento', agendamento.local)

    def alterar_agendamento_coletado(self, valor: bool) -> None:
        """Grava na tarefe se o agendamento foi coletado."""
        self.base_dados.alterar_atributo(self.pos, "agenda_coletada", bool_tobit(valor))

    def alterar_anexacao_comerro(self, valor: bool) -> None:
        """Grava na tarefe se a anexação de PDF não foi processada por erro."""
        self.base_dados.alterar_atributo(self.pos, "anexacao_comerro", bool_tobit(valor))

    def alterar_arquivopdf_pericia(self, valor: bool) -> None:
        """Grava na tarefa se o relatório da perícia em PDF foi gerado."""
        self.base_dados.alterar_atributo(self.pos, "arquivopdfpericia", bool_tobit(valor))

    def alterar_exigenciapm_comerro(self, valor: bool) -> None:
        """Grava na tarefe se a geração de exigência do agendamento de PM não foi processada por erro."""
        self.base_dados.alterar_atributo(self.pos, "exigenciapm_comerro", bool_tobit(valor))

    def alterar_msg_criacaosub(self, valor: str) -> None:
        """Registra o erro ocorrido quando da criação da subtarefa"""
        self.base_dados.alterar_atributo(self.pos, "msgerro_criacaosub", valor)

    def alterar_olm(self, valor: str) -> None:
        """Grava na tarefa a APS Mantenedora do benefício."""
        self.base_dados.alterar_atributo(self.pos, "olm", valor)
    
    def alterar_pericia_realizada(self, valor: bool) -> None:
        """Grava na tarefe se a PM foi realizada."""
        self.base_dados.alterar_atributo(self.pos, "periciarealizada", bool_tobit(valor))

    def alterar_subtarefa(self, subtarefa: str) -> None:
        """Altera o número da subtarefa."""
        self.base_dados.alterar_atributo(self.pos, "subtarefa", str(subtarefa))

    def alterar_subtarefa_coletada(self, valor: bool) -> None:
        """Grava na tarefe se a subtarefa foi coletada."""
        self.base_dados.alterar_atributo(self.pos, "subtarefa_coletada", bool_tobit(valor))

    def concluir_fase_subtarefa(self) -> None:
        """Informa que a tarefa já possui subtarefa gerada."""
        self.base_dados.alterar_atributo(self.pos, 'tem_subtarefa', "1")
        if self.base_dados.checar_atributo_nulo(self.pos, 'tem_prim_subtarefa'):
            self.base_dados.alterar_atributo(self.pos, "tem_prim_subtarefa", "1")
            self.base_dados.alterar_atributo(self.pos, "data_subtarefa", pd.to_datetime('today').floor('D'))
    
    def concluir_fase_agendapm(self) -> None:
        """Informa que a PM foi agendada."""
        self.base_dados.alterar_atributo(self.pos, "tem_agendapm", "1")
        
    def concluir_fase_pdfagendapm_anexo(self) -> None:
        """Informa que o comprovante do agendamento da PM foi anexado à tarefa."""
        self.base_dados.alterar_atributo(self.pos, "tem_pdfagendapmanexo", "1")
               
    def concluir_fase_pericia_cumprida(self) -> None:
        """Informa que a fase de PM foi concluída."""
        self.base_dados.alterar_atributo(self.pos, "periciacumprida", "1")
        
    def concluir_fase_subtarefa_cancelada(self) -> None:
        """Informa que a subtarefa de PM foi cancelada."""
        self.base_dados.alterar_atributo(self.pos, "subtarefacancelada", "1")

    def concluir_fase_pericia_lancada(self) -> None:
        """Informa que a perícia foi lançada no Prisma."""
        self.base_dados.alterar_atributo(self.pos, "pericialancada", "1")

    def concluir_fase_benef_despachado(self) -> None:
        """Informa que o benefício foi desapachado no Prisma."""
        self.base_dados.alterar_atributo(self.pos, "beneficiodespachado", "1")

    def marcar_pm_naocompareceu(self) -> None:
        """Grava na tarefa as informações relativas ao não comparecimento à PM."""
        self.concluir_fase_agendapm()
        self.concluir_fase_pdfagendapm_anexo()
        self.concluir_fase_exigencia(False)
        self.concluir_fase_pericia_cumprida()
        self.base_dados.alterar_atributo(self.pos, "periciarealizada", "0")
        self.base_dados.alterar_atributo(self.pos, "tem_pdfresumoanexo", "1")
        self.base_dados.alterar_atributo(self.pos, "resultado", "b36NaoComparecePM")

    def marcar_pm_indeferiu(self) -> None:
        """Grava na tarefa as informações relativas ao indeferimento pela PM."""
        self.base_dados.alterar_atributo(self.pos, "pericialancada", "0")
        self.base_dados.alterar_atributo(self.pos, "tem_pdfresumoanexo", "0")

    def marcar_pm_realizada(self, resultado: str) -> None:
        """Grava na tarefa as informações relativas a realização da PM."""
        self.concluir_fase_agendapm()
        self.concluir_fase_pdfagendapm_anexo()
        self.concluir_fase_exigencia(False)
        self.concluir_fase_pericia_cumprida()
        self.base_dados.alterar_atributo(self.pos, "periciarealizada", "1")
        self.base_dados.alterar_atributo(self.pos, "arquivopdfpericia", "1")
        self.base_dados.alterar_atributo(self.pos, "resultado", resultado)

    def obter_fase_subtarefa_gerada(self) -> bool:
        """Retorna se já foi gerada subtarefa de PM."""
        return self.base_dados.checar_atributo_verdadeiro(self.pos, "tem_subtarefa")

    def obter_fase_agendapm(self) -> bool:
        """Retorna se já foi agendada a PM."""
        return self.base_dados.checar_atributo_verdadeiro(self.pos, "tem_agendapm")

    def obter_fase_pdfagendapm_anexo(self) -> bool:
        """Retorna se foi gerado arquivo PDF com agendamento da PM."""
        return self.base_dados.checar_atributo_verdadeiro(self.pos, "tem_pdfagendapmanexo")
            
    def obter_fase_pericia_cumprida(self) -> bool:
        """
        Retorna se a PM já foi cumprida.
        PM está cumprida se já foi realizada ou se o requerente faltou a PM.
        """
        return self.base_dados.checar_atributo_verdadeiro(self.pos, "periciacumprida")

    def obter_fase_subtarefa_cancelada(self) -> bool:
        """Retorna se a subtarefa já foi cancelada."""
        return self.base_dados.checar_atributo_verdadeiro(self.pos, "subtarefacancelada")

    def obter_fase_beneficio_habilitado(self) -> bool:
        """Retorna se o benefício já foi habilitado no Prisma."""
        return self.base_dados.checar_atributo_naonulo(self.pos, "beneficio")

    def obter_fase_beneficio_despachado(self) -> bool:
        """Retorna se o benefício já foi despachado."""
        return self.base_dados.checar_atributo_verdadeiro(self.pos, "beneficiodespachado")
    
    def obter_olm(self) -> str:
        """Retorna o OL da APS Mantenedora."""
        return self.base_dados.obter_atributo(self.pos, 'olm')

    def obter_subtarefa(self) -> str:
        """Retorna o número da subtarefa."""
        return self.base_dados.obter_atributo(self.pos, 'subtarefa')

    def pericia_esta_vencida(self) -> bool:
        """Retorna se a data da PM já passou."""
        valor = self.base_dados.obter_atributo(self.pos, 'dataagendamento')
        return valor < pd.to_datetime('today').floor('D')
    
    def subtarefa_foicoletada(self) -> bool:
        """Retorna se a subtarefa foi gerada ou coletada."""
        return self.base_dados.checar_atributo_verdadeiro(self.pos, "subtarefa_coletada")
    
    def tem_erro_anexacaopdfpm(self) -> bool:
        """Retorna se anexação de arquivos PDF não foi processada por erro."""
        return self.base_dados.checar_atributo_verdadeiro(self.pos, "anexacao_comerro")
    
    def tem_erro_exigenciapm(self) -> bool:
        """Retorna se a geração de exigência para agendamento de PM não foi processada por erro."""
        return self.base_dados.checar_atributo_verdadeiro(self.pos, "exigenciapm_comerro")
    
    def tem_erro_geracaosub(self) -> bool:
        """Retorna se houve erro na geração da subtarefa."""
        return self.base_dados.checar_atributo_naonulo(self.pos, "msgerro_criacaosub") 
    
    def tem_pericia_lancada(self) -> bool:
        """Retorna se a PM já foi lançada no PM."""
        return self.base_dados.checar_atributo_verdadeiro(self.pos, "pericialancada")
    
    def tem_pericia_realizada(self) -> bool:
        """Retorna se a PM já foi realizada."""
        return self.base_dados.checar_atributo_verdadeiro(self.pos, "periciarealizada")
    
    def tem_pdfpericia(self) -> bool:
        """Retorna se há relatório de PM para lançar."""
        return self.base_dados.checar_atributo_verdadeiro(self.pos, "arquivopdfpericia")