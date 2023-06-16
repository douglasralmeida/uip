import pandas as pd
from datetime import date
from tarefa import Tarefa
from .utils import bool_tobit

class TarefaMajoracao25(Tarefa):
    def __init__(self, dados, i) -> None:
        super().__init__(dados, i)

    def alterar_acompanhante(self, indicador: str) -> None:
        """Altera o indicador de acompanhante."""
        self.base_dados.alterar_atributo(self.pos, 'indicador_acompanhante', indicador)

    def alterar_dib(self, dib: date) -> None:
        """Altera a data de início do benefício."""
        self.base_dados.alterar_atributo(self.pos, 'dib', dib)

    def alterar_dcb(self, dcb: date) -> None:
        """Altera a data de cessação do benfício."""
        self.base_dados.alterar_atributo(self.pos, 'dcb', dcb)
    
    def alterar_esta_acamado(self, valor: str) -> None:
        """Grava na tarefe se o requerente informou se está acamado/hospitalizado."""
        self.base_dados.alterar_atributo(self.pos, "esta_acamado", valor)

    def alterar_especie(self, especie: str) -> None:
        """Altera a espécie de benefício."""
        self.base_dados.alterar_atributo(self.pos, 'especie', especie)

    def alterar_sistema_mantenedor(self, sistema: str) -> None:
        """Altera o sistema mantenedor do benefício."""
        self.base_dados.alterar_atributo(self.pos, 'sistema_matenedor', sistema)
     
    def alterar_msg_criacaosub(self, valor: str) -> None:
        """Registra o erro ocorrido quando da criação da subtarefa"""
        self.base_dados.alterar_atributo(self.pos, "msgerro_criacaosub", valor)

    def alterar_olm(self, ol: str) -> None:
        """Altera o OLM do benefício."""
        self.base_dados.alterar_atributo(self.pos, 'olm', ol)

    def alterar_situacaobeneficio(self, status: str) -> None:
        """Altera a situação do benefício."""
        self.base_dados.alterar_atributo(self.pos, 'status_beneficio', status)
    
    def alterar_subtarefa(self, subtarefa: str) -> None:
        """Altera o número da subtarefa."""
        self.base_dados.alterar_atributo(self.pos, "subtarefa", str(subtarefa))

    def alterar_subtarefa_coletada(self, valor: bool) -> None:
        """Grava na tarefe se a subtarefa foi coletada."""
        self.base_dados.alterar_atributo(self.pos, "subtarefa_coletada", bool_tobit(valor))

    def concluir_fase_dadosbencoletados(self) -> None:
        """Marca a tarefa com coleta de dados de benefício concluída."""
        self.base_dados.alterar_atributo(self.pos, "tem_dadosbeneficio", "1")

    def concluir_fase_subtarefa(self) -> None:
        """Informa que a tarefa já possui subtarefa gerada."""
        self.base_dados.alterar_atributo(self.pos, 'tem_subtarefa', "1")
        if self.base_dados.checar_atributo_nulo(self.pos, 'tem_prim_subtarefa'):
            self.base_dados.alterar_atributo(self.pos, "tem_prim_subtarefa", "1")
            self.base_dados.alterar_atributo(self.pos, "data_subtarefa", pd.to_datetime('today').floor('D'))
            
    def obter_fase_coleta_dadosbeneficio(self) -> bool:
        """Retorna se já foi gerada subtarefa de PM."""
        return self.base_dados.checar_atributo_verdadeiro(self.pos, "tem_dadosbeneficio")

    def obter_fase_subtarefa_gerada(self) -> bool:
        """Retorna se já foi gerada subtarefa de PM."""
        return self.base_dados.checar_atributo_verdadeiro(self.pos, "tem_subtarefa")
    
    def tem_erro_geracaosub(self) -> bool:
        """Retorna se houve erro na geração da subtarefa."""
        return self.base_dados.checar_atributo_naonulo(self.pos, "msgerro_criacaosub") 
