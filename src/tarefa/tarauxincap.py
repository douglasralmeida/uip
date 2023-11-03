from .utils import bool_tostring, valor_tostring
from agendamento import Agendamento
from tarefa import Tarefa

class TarefaAuxilioIncapacidade(Tarefa):
    def __init__(self, dados, i) -> None:
        super().__init__(dados, i)

    def __str__(self) -> str:
        resultado = super().__str__()

        resultado = f'Subtarefa gerada: {bool_tostring(self.obter_fase_subtarefa_gerada())}\n'
        resultado = f'PM agendada: {bool_tostring(self.obter_fase_agendapm())}\n'
        resultado = f'Comprovante de agendameto da PM anexado: {bool_tostring(self.obter_fase_pdfagendapm_anexo())}\n'
        resultado = f'Exigência do agendamento da PM gerada: {bool_tostring(self.obter_fase_possui_exigencia())}\n'
        resultado = f'PM cumprida: {bool_tostring(self.obter_fase_pericia_cumprida())}\n'
        resultado = f'PM realizada: {bool_tostring(self.obter_fase_pericia_realizada())}\n'
        resultado = f'Benefício habilitado: {bool_tostring(self.obter_fase_beneficio_habilitado())}\n'
        resultado = f'Benefício despachado: {bool_tostring(self.obter_fase_beneficio_despachado())}\n'
        return resultado

    def alterar_agendamento(self, agendamento: Agendamento) -> None:
        """Altera os dados do agendamento da PM"""
        self.base_dados.alterar_atributo(self.pos, 'dataagendamento', agendamento.data)
        self.base_dados.alterar_atributo(self.pos, 'horaagendamento', agendamento.hora)
        self.base_dados.alterar_atributo(self.pos, 'localagendamento', agendamento.local)

    def alterar_beneficio_despachado(self, beneficiodespachado: bool) -> None:
        """Altera a informação se o benefício foi ou não despachado."""
        if beneficiodespachado:
            self.base_dados.alterar_atributo(self.pos, 'beneficiodespachado', "1")
        else:
            self.base_dados.alterar_atributo(self.pos, 'beneficiodespachado', "0")

    def concluir_fase_pericia_cumprida(self) -> None:
        """Informa que a fase de PM foi concluída."""
        self.base_dados.alterar_atributo(self.pos, "periciacumprida", "1")
        
    def concluir_fase_pericia_realizada(self) -> None:
        """Informa que a PM foi realizada."""
        self.base_dados.alterar_atributo(self.pos, "periciarealizada", "1")

    def concluir_fase_subtarefa(self) -> None:
        """Informa que a tarefa possui subtarefa."""
        self.base_dados.alterar_atributo(self.pos, "tem_subtarefa", "1")
    
    def concluir_fase_agendapm(self) -> None:
        self.base_dados.alterar_atributo(self.pos, 'tem_agendapm', "1")
        
    def concluir_fase_pdfagendapm_anexo(self) -> None:
        self.base_dados.alterar_atributo(self.pos, "tem_pdfagendapmanexo", "1")
                        
    def concluir_fase_subtarefa_cancelada(self) -> None:
        self.base_dados.alterar_atributo(self.pos, "subtarefacancelada", "1")

    def alterar_subtarefa(self, subtarefa: str) -> None:
        self.base_dados.alterar_atributo(self.pos, "subtarefa", subtarefa)

    def obter_agendamento(self) -> Agendamento:
        return Agendamento(self.base_dados.obter_atributo("dataagendamento"), self.base_dados.obter_atributo("horaagendamento"), self.base_dados.obter_atributo("localagendamento"))

    def obter_fase_subtarefa_gerada(self):
        return self.base_dados.checar_atributo_verdadeiro(self.pos, "tem_subtarefa")
    
    def obter_fase_agendapm(self):
        return self.base_dados.checar_atributo_verdadeiro(self.pos, "tem_agendapm")
    
    def obter_fase_pdfagendapm_anexo(self):
        return self.base_dados.checar_atributo_verdadeiro(self.pos, "tem_pdfagendapmanexo")
    
    def obter_fase_possui_exigencia(self):
        return self.base_dados.checar_atributo_verdadeiro(self.pos, "tem_exigencia")
        
    def obter_fase_pericia_cumprida(self):
        return self.base_dados.checar_atributo_verdadeiro(self.pos, "periciacumprida")
        
    def obter_fase_pericia_realizada(self):
        return self.base_dados.checar_atributo_verdadeiro(self.pos, "periciarealizada")
    
    def obter_fase_subtarefa_cancelda(self):
        return self.base_dados.checar_atributo_verdadeiro(self.pos, "subtarefacancelada")

    def obter_fase_pericia_realizada(self):
        return self.base_dados.checar_atributo_verdadeiro(self.pos, "periciarealizada")

    def obter_fase_beneficio_habilitado(self):
        return self.base_dados.checar_atributo_naonulo(self.pos, "beneficio")

    def obter_fase_beneficio_despachado(self):
        return self.base_dados.checar_atributo_verdadeiro(self.pos, "beneficiodespachado")

    def obter_subtarefa(self):
        return  self.base_dados.obter_atributo(self.pos, 'subtarefa')
        
    def pericia_naofoi_realizada(self):
        self.base_dados.alterar_atributo(self.pos, "periciarealizada", "0")

    