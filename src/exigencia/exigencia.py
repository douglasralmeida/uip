## Codificado por Douglas Rodrigues de Almeida.
## Agosto de 2023
"""Exigência de documentação"""

import pandas as pd
from basedados import TipoBooleano, TipoData, TipoHora, TipoTexto, obter_datahoje


#Prazo para cumprimento de exigência será de 35 dias
PRAZO_EXIGENCIA = 35

class Exigencia:
    """Classe para comunicação de exigências"""
    def __init__(self, tem_exigencia: TipoBooleano) -> None:
        self.com_erro = TipoBooleano(None)
        self.cumprida = TipoBooleano(None)
        self.data_realizacao = TipoData(None)
        self.data_vencimento = TipoData(None)
        self.primeira_exig = TipoBooleano(None)
        self.tem_exig = tem_exigencia

    def __str__(self) -> str:
        """a"""
        res = ''
        if self.tem_exig.e_nulo:
            res += f'{self.tem_exig}'
        else:
            if self.tem_exig.e_verdadeiro:
                res += f'Sim. Vencimento: {self.data_vencimento}. Cumprida: {self.cumprida}'
            else:
                res += 'Não possui.'

        return res

    def alterar_primeira_exig(self, valor: TipoBooleano) -> None:
        """f"""
        self.primeira_exig = valor

    def alterar_realizacao(self, data: TipoData) -> None:
        """f"""
        self.data_realizacao = data

    def alterar_vencimento(self, data: TipoData) -> None:
        """f"""
        self.data_vencimento = data

    def cumprir(self, valor: TipoBooleano) -> None:
        """a"""
        self.cumprida = valor
        self.tem_exig = TipoBooleano(False)

    def esta_comerro(self) -> TipoBooleano:
        """a"""
        return self.com_erro

    def esta_cumprida(self) -> TipoBooleano:
        """a"""
        return self.cumprida

    def iniciar(self, iniciar_em: TipoData | None) -> None:
        """a"""
        #Se não tem exigências...então trata-se de primeira exigência.
        if self.primeira_exig.e_nulo:
            self.primeira_exig = TipoBooleano(True)            
        self.tem_exig = TipoBooleano(True)
        self.cumprida = TipoBooleano(False)
        if iniciar_em is None:
            self.data_realizacao = obter_datahoje()
        else:
            self.data_realizacao = iniciar_em
        self.data_vencimento = TipoData(str(self.data_realizacao))
        self.data_vencimento.somar_dias(PRAZO_EXIGENCIA)

    def marcar_erro(self, erro: TipoBooleano) -> None:
        """a"""
        self.com_erro = erro
    
    def obter_primeira_exig(self) -> TipoBooleano:
        """a"""
        return self.primeira_exig
    
    def obter_realizacao(self) -> TipoData:
        """Ra."""
        return self.data_realizacao

    def obter_vencimento(self) -> TipoData:
        """Ra."""
        return self.data_vencimento
    
    def tem_exigencia(self) -> TipoBooleano:
        """a"""
        return self.tem_exig