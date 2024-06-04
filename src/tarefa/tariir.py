## Codificado por Douglas Rodrigues de Almeida.
## Fevereiro de 2024

import pandas as pd
from basedados import TipoBooleano, TipoTexto, TipoInteiro, TipoData
from subtarefa import Subtarefa
from tarefa import Tarefa

class TarefaIsencaoIR(Tarefa):
    def __init__(self, dados, i) -> None:
        super().__init__(dados, i)
    
    def __str__(self) -> str:
        """Descrição da tarefa de requerimento de isenção de IR."""
        resultado = super().pre_tostr()

        return resultado
    
    def alterar_beneficio(self, beneficio: TipoTexto) -> None:
        """Altera o número do benefício."""
        self.base_dados.alterar_atributo(self.pos, 'beneficio', beneficio.valor)

    def alterar_exigpm(self, exigencia_pm: TipoBooleano) -> None:
        """Alterar o campo pm em exigência."""
        self.base_dados.alterar_atributo(self.pos, 'pm_exigencia', exigencia_pm.valor)

    def alterar_arquivopdfpm(self, arquivopdfpm: bool) -> None:
        if arquivopdfpm:
            valor = "1"
        else:
            valor = "0"
        self.base_dados.alterar_atributo(self.pos, 'arquivopdfpericia', valor)

    def alterar_ultimaconsultasubtarefa(self) -> None:
        valor = pd.to_datetime('today').floor('D')
        self.base_dados.alterar_atributo(self.pos, 'ultimaconsultasubtarefa', valor)
    
    def alterar_subtarefa(self, subtarefa: Subtarefa) -> None:
        """Altera os dados da subtarefa."""
        self.base_dados.alterar_atributo(self.pos, "subtarefa", subtarefa.obter_protocolo().valor)
        self.base_dados.alterar_atributo(self.pos, "subtarefa_coletada", subtarefa.coletada().valor)
        self.base_dados.alterar_atributo(self.pos, "msgerro_criacaosub", subtarefa.obter_msgerro().valor)
        self.base_dados.alterar_atributo(self.pos, "tem_prim_subtarefa", subtarefa.e_primeira().valor)
        self.base_dados.alterar_atributo(self.pos, "data_subtarefa", subtarefa.obter_criacao().valor)
        self.base_dados.alterar_atributo(self.pos, "tem_subtarefa", subtarefa.tem_subtarefa().valor)

    def concluir_subtarefa(self) -> None:
        self.base_dados.alterar_atributo(self.pos, "subtarefaconcluida", "1")

    def obter_subtarefa(self) -> Subtarefa:
        """Retorna o número da subtarefa."""
        valor = self.base_dados.obter_atributo(self.pos, "tem_subtarefa")
        erro = self.base_dados.obter_atributo(self.pos, "msgerro_criacaosub")
        subtarefa = Subtarefa(TipoBooleano(valor))
        subtarefa.alterar_msgerro(TipoTexto(erro))
        if TipoBooleano(valor).e_verdadeiro:
            protocolo = self.base_dados.obter_atributo(self.pos, 'subtarefa')
            coletada = self.base_dados.obter_atributo(self.pos, "subtarefa_coletada")
            e_primeira = self.base_dados.obter_atributo(self.pos, "tem_prim_subtarefa")
            data = (self.base_dados.obter_atributo(self.pos, "data_subtarefa"))
            subtarefa.alterar(TipoInteiro(protocolo), TipoBooleano(False), TipoBooleano(e_primeira), TipoData(data))
            subtarefa.alterar_coletada(TipoBooleano(coletada))

        return subtarefa
    
    def subtarefa_concluida(self) -> TipoBooleano:
        valor = self.base_dados.checar_atributo_verdadeiro(self.pos, "subtarefaconcluida")
        return TipoBooleano(valor)
    
    def tem_analisedoc(self) -> TipoBooleano:
        valor = self.base_dados.checar_atributo_naonulo(self.pos, "tem_documentacao")
        return TipoBooleano(valor)
       
    def tem_erro_geracaosub(self) -> TipoBooleano:
        """Retorna se houve erro na geração da subtarefa."""
        valor = self.base_dados.checar_atributo_naonulo(self.pos, "msgerro_criacaosub")
        return TipoBooleano(valor)
    
    def tem_exig_pm(self) -> TipoBooleano:
        """Retorna se a perícia médica abriu ecxigência."""
        valor = self.base_dados.checar_atributo_verdadeiro(self.pos, "pm_exigencia")
        return TipoBooleano(valor)
