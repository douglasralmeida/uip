import pandas as pd
from tarefa import Tarefa

class TarefaIsencaoIR(Tarefa):
    def __init__(self, dados, i) -> None:
        super().__init__(dados, i)
    
    def alterar_subtarefa(self, subtarefa: str) -> None:
        """Altera o número da subtarefa."""
        self.base_dados.alterar_atributo(self.pos, "subtarefa", str(subtarefa))

    def concluir_fase_subtarefa(self) -> None:
        """Informa que a tarefa já possui subtarefa gerada."""
        self.base_dados.alterar_atributo(self.pos, 'tem_subtarefa', "1")
        if self.base_dados.checar_atributo_nulo(self.pos, 'tem_prim_subtarefa'):
            self.base_dados.alterar_atributo(self.pos, "tem_prim_subtarefa", "1")
            self.base_dados.alterar_atributo(self.pos, "data_subtarefa", pd.to_datetime('today'))
            
    def obter_fase_subtarefa_gerada(self) -> bool:
        """Retorna se já foi gerada subtarefa de PM."""
        return self.base_dados.checar_atributo_verdadeiro(self.pos, "tem_subtarefa")
