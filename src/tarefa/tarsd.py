## Codificado por Douglas Rodrigues de Almeida.
## Outubro de 2023
"""Tarefa de Seguro Defeso"""

from tarefa import Tarefa
from basedados import BaseDados, TipoBooleano, TipoData, TipoHora, TipoInteiro, TipoTexto

class TarefaSeguroDefeso(Tarefa):
    """Classe da Tarefa de Seguro Defeso"""
    def __init__(self, dados: BaseDados, i: int) -> None:
        super().__init__(dados, i)

    def __str__(self) -> str:
        """Descrição da tarefa de seguro defeso."""
        resultado = super().__str__()

        sd_habilitado = self.sd_habilitado()
        resultado += f'SD habilitado: {sd_habilitado}\n'
        if sd_habilitado:
            resultado += f'Nº do SD: {self.obter_segurodefeso()}\n'

        return resultado
    
    def alterar_defeso(self, defeso: TipoTexto) -> None:
        """Altera o número do benefício."""
        self.base_dados.alterar_atributo(self.pos, 'defeso', defeso.valor)

    def alterar_periodocontrib(self, inicio: TipoTexto, fim: TipoTexto) -> None:
        """Altera o período da contrbuição previdenciária."""
        periodo = TipoTexto(f'{inicio} a {fim}')
        self.base_dados.alterar_atributo(self.pos, 'periodocontrib', periodo.valor)

    def alterar_portaria(self, portaria: TipoTexto) -> None:
        """Altera o número do benefício."""
        self.base_dados.alterar_atributo(self.pos, 'portaria', portaria.valor)

    def alterar_uf(self, uf: TipoTexto) -> None:
        """Altera o número do benefício."""
        self.base_dados.alterar_atributo(self.pos, 'uf', uf.valor)

    def obter_segurodefeso(self) -> TipoTexto:
        """Retorna o número do SD."""
        valor = self.base_dados.obter_atributo(self.pos, 'sd')
        
        return TipoTexto(valor)
    
    def sd_habilitado(self) -> bool:
        """Retorna se o SD já foi habilitado no SDMTE."""
        return self.base_dados.checar_atributo_naonulo(self.pos, "sd")