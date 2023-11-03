## Codificado por Douglas Rodrigues de Almeida.
## Agosto de 2023
"""Subtarefa"""

from basedados import TipoBooleano, TipoData, TipoInteiro, TipoTexto

class Subtarefa:
    """Classe para subtarefas"""
    def __init__(self, tem_subtarefa: TipoBooleano) -> None:
        self.protocolo = TipoInteiro(None)
        self.temsubtarefa = tem_subtarefa
        self.esta_cancelada = TipoBooleano(None)
        self.e_coletada = TipoBooleano(None)
        self.e_primeira_sub = TipoBooleano(None)
        self.data_criacao = TipoData(None)
        self.msg_erro = TipoTexto(None)

    def __str__(self) -> str:
        """a"""
        return f'(info. indisponível)'

    def alterar(self, protocolo: TipoInteiro, cancelada: TipoBooleano, e_primeira: TipoBooleano, data_criacao: TipoData) -> None:
        """a"""
        self.protocolo = protocolo
        self.esta_cancelada = cancelada
        self.e_coletada = TipoBooleano(None)
        self.e_primeira_sub = e_primeira
        self.data_criacao = data_criacao
        self.temsubtarefa = TipoBooleano(not protocolo.e_nulo)

    def alterar_coletada(self, e_coletada: TipoBooleano) -> None:
        """a"""
        self.e_coletada = e_coletada

    def alterar_msgerro(self, msg_erro: TipoTexto) -> None:
        """a"""
        self.msg_erro = msg_erro
        
    def cancelada(self) -> TipoBooleano:
        """a"""
        return self.esta_cancelada

    def cancelar(self) -> None:
        """a."""
        self.esta_cancelada = TipoBooleano(True)

    def coletada(self) -> TipoBooleano:
        """a"""
        return self.e_coletada

    def e_primeira(self) -> TipoBooleano:
        """a"""
        return self.e_primeira_sub
    
    def gerar_nova(self, novo_protocolo: TipoInteiro) -> None:
        """f"""
        self.temsubtarefa = TipoBooleano(True)
        if self.e_primeira_sub.e_nulo:
            self.e_primeira_sub = TipoBooleano(True)
            self.data_criacao = TipoData('hoje')
        if self.data_criacao.e_nulo:
            self.data_criacao = TipoData('hoje')
        self.protocolo = novo_protocolo
        self.e_coletada = TipoBooleano(False)
        self.esta_cancelada = TipoBooleano(None)
        self.msg_erro = TipoTexto(None)
    
    def obter_msgerro(self) -> TipoTexto:
        """a"""
        return self.msg_erro
    
    def obter_protocolo(self) -> TipoInteiro:
        """a"""
        return self.protocolo
    
    def obter_criacao(self) -> TipoData:
        """a"""
        return self.data_criacao
    
    def tem_subtarefa(self) -> TipoBooleano:
        """a"""
        return self.temsubtarefa
        
    @property
    def tem(self) -> bool:
        """a"""
        return self.temsubtarefa.e_verdadeiro
    
    @property
    def tem_erro(self) -> bool:
        """a"""
        return not self.msg_erro.e_nulo