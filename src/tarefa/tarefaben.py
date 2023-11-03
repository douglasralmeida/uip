## Codificado por Douglas Rodrigues de Almeida.
## Agosto de 2023
"""Tarefa do GET para requerimento de benefício"""

from .tarefa import Tarefa
from agendamento import Agendamento
from anabenefinac import AnaliseBenefInac
from anexacao import Anexacao
from basedados import BaseDados, TipoBooleano, TipoData, TipoHora, TipoInteiro, TipoTexto
from pericia import PericiaMedica
from subtarefa import Subtarefa

class TarefaBeneficio(Tarefa):
    """Classe para a tarefa do GET."""
    def __init__(self, dados: BaseDados, i: int) -> None:
        super().__init__(dados, i)

    def __str__(self) -> str:
        """Descrição da tarefa de requerimento de benefício."""
        resultado = super().pre_tostr()

        resultado += f'OL: {self.obter_olm()}\n'
        analise = self.obter_analise_benefinac()
        resultado += f'Análise benefícios inacumuláveis: {analise}\n'
        resultado += f'OL Mantenedor: {self.obter_olm()}\n'
        subtarefa = self.obter_subtarefa()
        resultado += f'Subtarefa PM: {subtarefa}\n'
        agenda = self.obter_agendamento_pm()
        resultado += f'Agendamento PM:{agenda}\n'
        anexacao = self.obter_anexacaopdf_pm()
        resultado += f'Anexação Agendamento PM: {anexacao}\n'
        exigencia = self.obter_exigencia()
        resultado += f'Exigência do Agendamento PM: {exigencia}\n'
        pericia = self.obter_periciamedica()
        resultado += f'PM: {pericia}\n'
        ben_habilitado = self.beneficio_habilitado()
        resultado += f'Benefício habilitado: {ben_habilitado}\n'
        if ben_habilitado:
            resultado += f'Nº do benefício: {self.obter_beneficio()}\n'
        resultado += f'Benefício despachado: {self.obter_fase_beneficio_despachado()}\n'

        return resultado
    
    def alterar_agendamento_pm(self, agendamento: Agendamento) -> None:
        """Altera os dados do agendamento da PM"""
        if agendamento.tem_agendamento().e_verdadeiro:
            self.base_dados.alterar_atributo(self.pos, 'protocoloagendamento', agendamento.obter_protocolo().valor)
            self.base_dados.alterar_atributo(self.pos, 'dataagendamento', agendamento.obter_data().valor)
            self.base_dados.alterar_atributo(self.pos, 'horaagendamento', agendamento.obter_hora().valor)
            self.base_dados.alterar_atributo(self.pos, 'localagendamento', agendamento.obter_local().valor)
            self.base_dados.alterar_atributo(self.pos, "agenda_coletada", agendamento.obter_coletado().valor)
            self.base_dados.alterar_atributo(self.pos, 'tem_agendapm', agendamento.tem_agendamento().valor)
   
    def alterar_analise_benefinac(self, analise: AnaliseBenefInac) -> None:
        """Altera a análise de benefício inacumulável."""
        self.base_dados.alterar_atributo(self.pos, 'possui_ben_inacumulavel', analise.tem_benef_inacumulavel().valor)
        self.base_dados.alterar_atributo(self.pos, 'especie_inacumulavel', analise.obter_especie().valor)
        self.base_dados.alterar_atributo(self.pos, 'nb_inacumulavel', analise.obter_beneficio().valor)
        self.base_dados.alterar_atributo(self.pos, 'dib_inacumulavel', analise.obter_dib().valor)

    def alterar_anexacaopdf_pm(self, anexacao: Anexacao) -> None:
        """Altera os dados da anexação do Agendamento da PM"""
        self.base_dados.alterar_atributo(self.pos, "anexacao_comerro", anexacao.tem_erro().valor)
        self.base_dados.alterar_atributo(self.pos, "tem_pdfagendapmanexo", anexacao.tem_anexo().valor)
    
    def alterar_beneficio(self, beneficio: TipoTexto) -> None:
        """Altera o número do benefício."""
        self.base_dados.alterar_atributo(self.pos, 'beneficio', beneficio.valor)
    
    def alterar_olm(self, orgao: TipoTexto) -> None:
        """Grava na tarefa a APS Mantenedora do benefício."""
        self.base_dados.alterar_atributo(self.pos, "olm", orgao.valor)

    def alterar_periciamedica(self, pericia: PericiaMedica) -> None:
        """Grava informações da PM."""
        self.base_dados.alterar_atributo(self.pos, "arquivopdfpericia", pericia.possui_relatpdf().valor)
        self.base_dados.alterar_atributo(self.pos, "periciacumprida", pericia.cumprida().valor)
        self.base_dados.alterar_atributo(self.pos, "periciarealizada", pericia.realizada().valor)

    def alterar_subtarefa(self, subtarefa: Subtarefa) -> None:
        """Altera os dados da subtarefa."""
        self.base_dados.alterar_atributo(self.pos, "subtarefa", subtarefa.obter_protocolo().valor)
        self.base_dados.alterar_atributo(self.pos, "subtarefa_coletada", subtarefa.coletada().valor)
        self.base_dados.alterar_atributo(self.pos, "msgerro_criacaosub", subtarefa.obter_msgerro().valor)
        self.base_dados.alterar_atributo(self.pos, "subtarefacancelada", subtarefa.cancelada().valor)
        self.base_dados.alterar_atributo(self.pos, "tem_prim_subtarefa", subtarefa.e_primeira().valor)
        self.base_dados.alterar_atributo(self.pos, "data_subtarefa", subtarefa.obter_criacao().valor)
        self.base_dados.alterar_atributo(self.pos, "tem_subtarefa", subtarefa.tem_subtarefa().valor)

    def beneficio_habilitado(self) -> bool:
        """Retorna se o benefício já foi habilitado no Prisma."""
        return self.base_dados.checar_atributo_naonulo(self.pos, "beneficio")
        
    def despachar_beneficio(self) -> None:
        """Informa que o benefício foi desapachado para o SUB."""
        self.base_dados.alterar_atributo(self.pos, "beneficiodespachado", "1")

    def marcar_japossui_subtarefa(self) -> None:
        """Informa que a tarefa já possui subtarefa criada anteriormente."""
        self.base_dados.alterar_atributo(self.pos, 'tem_prim_subtarefa', '0')

    def marcar_pm_indeferiu(self) -> None:
        """Grava na tarefa as informações relativas ao indeferimento pela PM."""
        self.base_dados.alterar_atributo(self.pos, "pericialancada", "0")
        self.base_dados.alterar_atributo(self.pos, "tem_pdfresumoanexo", "0")

    def marcar_pm_naocompareceu(self) -> None:
        """Grava na tarefa as informações relativas ao não comparecimento à PM."""
        #self.concluir_fase_agendapm()
        #self.concluir_fase_pdfagendapm_anexo()  
        #self.concluir_fase_exigencia(None)
        #self.concluir_fase_pericia_cumprida()
        self.base_dados.alterar_atributo(self.pos, "periciarealizada", "0")
        self.base_dados.alterar_atributo(self.pos, "tem_pdfresumoanexo", "1")
        self.base_dados.alterar_atributo(self.pos, "resultado", "b36NaoComparecePM")

    def marcar_pm_lancada(self) -> None:
        self.base_dados.alterar_atributo(self.pos, "pericialancada", "1")

    def marcar_pm_realizada(self, resultado: str) -> None:
        """Grava na tarefa as informações relativas a realização da PM."""
        #self.concluir_fase_agendapm()
        #self.concluir_fase_pdfagendapm_anexo()
        #self.concluir_fase_exigencia(None)
        #self.concluir_fase_pericia_cumprida()
        self.base_dados.alterar_atributo(self.pos, "periciarealizada", "1")
        self.base_dados.alterar_atributo(self.pos, "arquivopdfpericia", "1")
        self.base_dados.alterar_atributo(self.pos, "resultado", resultado)        

    def obter_agendamento_pm(self) -> Agendamento:
        """Retorna as informações do agendamento de PM."""
        tem_agenda = TipoBooleano(self.base_dados.obter_atributo(self.pos, 'tem_agendapm'))
        agendamento = Agendamento(tem_agenda)
        if tem_agenda.e_verdadeiro:
            da = TipoData(self.base_dados.obter_atributo(self.pos, 'dataagendamento'))
            ha = TipoHora(self.base_dados.obter_atributo(self.pos, 'horaagendamento'))
            la = TipoTexto(self.base_dados.obter_atributo(self.pos, 'localagendamento'))
            pa = TipoInteiro(self.base_dados.obter_atributo(self.pos, 'protocoloagendamento'))
            ac = TipoBooleano(self.base_dados.obter_atributo(self.pos, "agenda_coletada"))
            agendamento.alterar(da, ha, la, pa, ac)
        
        return agendamento
    
    def obter_analise_benefinac(self) -> AnaliseBenefInac:
        """a"""
        possui_ben = TipoBooleano(self.base_dados.obter_atributo(self.pos, 'possui_ben_inacumulavel'))
        if possui_ben:
            especie = TipoInteiro(self.base_dados.obter_atributo(self.pos, 'especie_inacumulavel'))
            nb = TipoTexto(self.base_dados.obter_atributo(self.pos, 'nb_inacumulavel'))
            dib = TipoData(self.base_dados.obter_atributo(self.pos, 'dib_inacumulavel'))
        else:
            especie = TipoInteiro(None)
            nb = TipoTexto(None)
            dib = TipoData(None)
        analise = AnaliseBenefInac(possui_ben, especie, nb, dib)

        return analise
        
    def obter_anexacaopdf_pm(self) -> Anexacao:
        """Retorna dados da anexação PDF do agendamento da PM."""                                       
        valor_anexacao = TipoBooleano(self.base_dados.obter_atributo(self.pos, 'tem_pdfagendapmanexo'))
        valor_erro = TipoBooleano(self.base_dados.obter_atributo(self.pos, 'anexacao_comerro'))
        anexacao = Anexacao(valor_anexacao, valor_erro)
        
        return anexacao

    def obter_beneficio(self) -> TipoTexto:
        """Retorna o número do benefício."""
        valor = self.base_dados.obter_atributo(self.pos, 'beneficio')
        
        return TipoTexto(valor)

    def obter_fase_beneficio_despachado(self) -> bool:
        """Retorna se o benefício já foi despachado."""
        return self.base_dados.checar_atributo_verdadeiro(self.pos, "beneficiodespachado")    
    
    def obter_olm(self) -> TipoTexto:
        """Retorna o OL da APS Mantenedora."""
        valor = self.base_dados.obter_atributo(self.pos, 'olm')
        
        return TipoTexto(valor)
    
    def obter_periciamedica(self) -> PericiaMedica:
        """a"""
        tem_pdfpm = TipoBooleano(self.base_dados.obter_atributo(self.pos, "arquivopdfpericia"))
        pm_realizada = TipoBooleano(self.base_dados.obter_atributo(self.pos, "periciarealizada"))
        pm_cumprida = TipoBooleano(self.base_dados.obter_atributo(self.pos, "periciacumprida"))
        pericia = PericiaMedica(pm_cumprida, pm_realizada)
        pericia.alterar_relatpdf(tem_pdfpm)

        return pericia
    
    def obter_subtarefa(self) -> Subtarefa:
        """Retorna o número da subtarefa."""
        valor = self.base_dados.obter_atributo(self.pos, "tem_subtarefa")
        erro = self.base_dados.obter_atributo(self.pos, "msgerro_criacaosub")
        subtarefa = Subtarefa(TipoBooleano(valor))
        subtarefa.alterar_msgerro(TipoTexto(erro))
        if TipoBooleano(valor).e_verdadeiro:
            protocolo = self.base_dados.obter_atributo(self.pos, 'subtarefa')
            coletada = self.base_dados.obter_atributo(self.pos, "subtarefa_coletada")
            cancelada = self.base_dados.obter_atributo(self.pos, "subtarefacancelada")
            e_primeira = self.base_dados.obter_atributo(self.pos, "tem_prim_subtarefa")
            data = (self.base_dados.obter_atributo(self.pos, "data_subtarefa"))
            subtarefa.alterar(TipoInteiro(protocolo), TipoBooleano(cancelada), TipoBooleano(e_primeira), TipoData(data))
            subtarefa.alterar_coletada(TipoBooleano(coletada))

        return subtarefa
    
    def tem_analiseacb(self) -> TipoBooleano:
        """Indica se a tarefa tem dados básicos."""
        possui_analise = not TipoBooleano(self.base_dados.obter_atributo(self.pos, 'possui_ben_inacumulavel')).e_nulo
        return TipoBooleano(possui_analise)  
    
    def tem_subtarefa(self) -> TipoBooleano:
        """Indica se a tarefa tem dados básicos."""
        possui_subtarefa = TipoBooleano(self.base_dados.obter_atributo(self.pos, 'tem_subtarefa'))
        return possui_subtarefa