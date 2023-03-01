import pandas as pd

def bool_tostring(valor):
    if valor:
        return 'Sim'
    else:
        return 'Não'

def valor_tostring(valor):
    if pd.isna(valor):
        return '(nenhum)'
    else:
        return valor