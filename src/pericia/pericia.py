## Codificado por Douglas Rodrigues de Almeida.
## Agosto de 2023
"""Perícia Médica"""

from basedados import TipoBooleano, TipoData, TipoHora, TipoTexto

class PericiaMedica:
    """Classe para perícia médica"""
    def __init__(self, cumprida: TipoBooleano, realizada: TipoBooleano) -> None:
        self.relatorio_pdf = TipoBooleano(None)
        self.foicumprida = cumprida
        self.foirealizada = realizada

    def __str__(self) -> str:
        res = ''

        res += f'PM cumprida: {self.foicumprida}. '
        res += f'PM realizada: {self.foirealizada}\n'
        
        return res

    def alterar_relatpdf(self, valor: TipoBooleano) -> None:
        """f"""
        self.relatorio_pdf = valor

    def cumprida(self) -> TipoBooleano:
        """Ra."""
        return self.foicumprida

    def marcar_naocompareceu(self) -> None:
        """a"""
        self.foicumprida = TipoBooleano(True)
        self.foirealizada = TipoBooleano(False)

    def marcar_realizada(self) -> None:
        """a"""
        self.foicumprida = TipoBooleano(True)
        self.foirealizada = TipoBooleano(True)
        self.relatorio_pdf = TipoBooleano(True)

    def possui_relatpdf(self) -> TipoBooleano:
        """a."""
        return self.relatorio_pdf
    
    def realizada(self) -> TipoBooleano:
        """Ra."""
        return self.foirealizada