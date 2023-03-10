"""Procedimentos utilitários para o processador"""

import pandas as pd

def bool_tostring(valor: bool) -> str:
    """Converte um valor booleano para string."""
    if valor:
        return 'Sim'
    else:
        return 'Não'
    
def bool_tobit(valor: bool) -> str:
    """Converte um valor booleano para 0 ou 1."""
    if valor:
        return '1'
    else:
        return '0'

def valor_tostring(valor) -> str:
    """Converte um valor da base de dados para string."""
    if pd.isna(valor):
        return '(nenhum)'
    else:
        return valor