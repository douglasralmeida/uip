## Codificado por Douglas Rodrigues de Almeida.
## Agosto de 2023
"""Anexação de PDF"""

from basedados import TipoBooleano, TipoData, TipoHora, TipoTexto

class Anexacao:
    """Classe para anexacao de arquivos PDF"""
    def __init__(self, existe_anexo: TipoBooleano, existe_erro: TipoBooleano) -> None:
        self.existe_anexo = existe_anexo
        self.com_erro = existe_erro

    def __str__(self) -> str:
        """a"""
        return f'(info. indisponível)'

    def alterar_anexacao(self, existe_anexacao: TipoBooleano) -> None:
        """f"""
        self.existe_anexo = existe_anexacao

    def marcar_erro(self, erro: TipoBooleano) -> None:
        """a"""
        self.com_erro = erro

    def tem_erro(self) -> TipoBooleano:
        """a."""
        return self.com_erro        
    
    def tem_anexo(self) -> TipoBooleano:
        """Ra."""
        return self.existe_anexo