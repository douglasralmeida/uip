import utils
from agendamento import Agendamento
from tarefa import Tarefa

class TarefaCTC(Tarefa):
    def __init__(self, dados, i) -> None:
        super().__init__(dados, i)

    
    def exibir_resumo(self):
        super().exibir_resumo()
        print(f'Subtarefa gerada: {utils.bool_tostring(self.obter_fase_subtarefa_gerada())}')
        print(f'Em exigência: {utils.bool_tostring(self.obter_fase_possui_exigencia())}')
        print(f'CTC habilitada: {utils.bool_tostring(self.obter_fase_ctc_habilitada())}')
        print(f'CTC despachada: {utils.bool_tostring(self.obter_fase_ctc_despachada())}')

    def alterar_ctc_despachada(self, ctcdespachada):
        """Altera a informação se a CTC foi ou não despachada."""
        if ctcdespachada:
            self.base_dados.alterar_atributo(self.pos, 'ctcdespachada', "1")
        else:
            self.base_dados.alterar_atributo(self.pos, 'ctcdespachada', "0")

    def concluir_fase_subtarefa(self) -> None:
        """Informa que a tarefa possui subtarefa."""
        self.dados.loc[self.pos, "tem_subtarefa"] = "1"
         
    def alterar_fase_possui_exigencia(self):
        self.dados.loc[self.pos, "possuiexigencia"] = "1"
        
    def alterar_subtarefa(self, subtarefa):
        self.dados.loc[self.pos, "subtarefa"] = str(subtarefa)

    def obter_agendamento(self):
        return Agendamento(self.registro["dataagendamento"], self.registro["horaagendamento"], self.registro["localagendamento"])

    def obter_fase_subtarefa_gerada(self):
        return self.atributo_ehverdadeiro("tem_subtarefa")
    
    def obter_fase_agendapm(self):
        return self.atributo_ehverdadeiro("tem_agendapm")
    
    def obter_fase_pdfagendapm_anexo(self):
        return self.atributo_ehverdadeiro("tem_pdfagendapmanexo")
    
    def obter_fase_possui_exigencia(self):
        return self.atributo_ehverdadeiro("possuiexigencia")
        
    def obter_fase_pericia_cumprida(self):
        return self.atributo_ehverdadeiro("periciacumprida")
        
    def obter_fase_pericia_realizada(self):
        return self.atributo_ehverdadeiro("periciarealizada")
    
    def obter_fase_subtarefa_cancelda(self):
        return self.atributo_ehverdadeiro("subtarefacancelada")

    def obter_fase_pericia_realizada(self):
        return self.atributo_ehverdadeiro("periciarealizada")

    def obter_fase_beneficio_habilitado(self):
        return self.atributo_ehnaonulo("beneficio")

    def obter_fase_beneficio_despachado(self):
        return self.atributo_ehverdadeiro("beneficiodespachado")

    def obter_subtarefa(self):
        return self.registro['subtarefa']
        
    def pericia_naofoi_realizada(self):
        return self.dados.loc[self.pos, "periciarealizada"] == "0"

    