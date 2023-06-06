import pandas as pd
from tarefa import Tarefa
from .utils import bool_tobit

class TarefaMajoracao25(Tarefa):
    def __init__(self, dados, i) -> None:
        super().__init__(dados, i)

    def alterar_esta_acamado(self, valor: str) -> None:
        """Grava na tarefe se o requerente informou se está acamado/hospitalizado."""
        self.base_dados.alterar_atributo(self.pos, "esta_acamado", valor)
     
    def alterar_msg_criacaosub(self, valor: str) -> None:
        """Registra o erro ocorrido quando da criação da subtarefa"""
        self.base_dados.alterar_atributo(self.pos, "msgerro_criacaosub", valor)
    
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
            self.base_dados.alterar_atributo(self.pos, "data_subtarefa", pd.to_datetime('today'))
            
    def obter_fase_subtarefa_gerada(self) -> bool:
        """Retorna se já foi gerada subtarefa de PM."""
        return self.base_dados.checar_atributo_verdadeiro(self.pos, "tem_subtarefa")
    
    def tem_erro_geracaosub(self) -> bool:
        """Retorna se houve erro na geração da subtarefa."""
        return self.base_dados.checar_atributo_naonulo(self.pos, "msgerro_criacaosub") 
