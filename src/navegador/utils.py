from os import path, rename, remove 
from time import sleep

def aguardar_geracao_arquivo(arquivo_gerado: str, arquivo_novo: str) -> None:
    """Aguarda pela geração do arquivo PDF e o renomea."""
    while not path.exists(arquivo_gerado):
        sleep(3)
    if path.exists(arquivo_novo):
        remove(arquivo_novo)
    rename(arquivo_gerado, arquivo_novo)