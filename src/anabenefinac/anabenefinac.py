## Codificado por Douglas Rodrigues de Almeida.
## Agosto de 2023
"""Análise de Benefícios Inacumuláveis"""

import pandas as pd
from basedados import TipoBooleano, TipoInteiro, TipoTexto

class AnaliseBenefInac:
    """Classe para análise de benefícios inacumuláveis"""
    def __init__(self, possui_benef: TipoBooleano, especie: TipoInteiro, beneficio: TipoTexto) -> None:
        self.tem = not possui_benef.e_nulo
        self.especie = especie
        self.beneficio = beneficio
        self.possui_benef_inacumulavel = possui_benef

    def __str__(self) -> str:
        """a"""
        res = ''
        if self.tem:
            res += f'\tPossui análise de benefícios inacumuláveis.\n'
            if self.possui_benef_inacumulavel.e_verdadeiro:
                res += f'Benefício inacumulável: {self.especie}/{self.beneficio}'
            else:
                res += f'Não possui benefício inacumulável.'
        else:
            res += '\tSem análise de benefícios inacumuláveis.'
        return res

    def marcar_possuiben(self, especie: str, beneficio: str) -> None:
        """a"""
        self.tem = True
        self.especie = TipoInteiro(especie)
        self.beneficio = TipoTexto(beneficio)
        self.possui_benef_inacumulavel = TipoBooleano(True)

    def marcar_naopossuiben(self) -> None:
        """a"""
        self.tem = False
        self.especie = TipoInteiro(None)
        self.beneficio = TipoTexto(None)
        self.possui_benef_inacumulavel = TipoBooleano(False)

    def obter_beneficio(self) -> TipoTexto:
        """a"""
        return self.beneficio
    
    def obter_especie(self) -> TipoInteiro:
        """a"""
        return self.especie
    
    @property
    def tem_analise(self) -> bool:
        """a"""
        return self.tem
    
    def tem_benef_inacumulavel(self) -> TipoBooleano:
        """a"""
        return self.possui_benef_inacumulavel