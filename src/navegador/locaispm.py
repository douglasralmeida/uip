from arquivo import carregar_dados
from dataclasses import dataclass
from variaveis import Variaveis

ARQUIVO_DADOS = 'locaispm.json'

@dataclass
class LocalPM:
    """Classe para o local de realização de Perícia Médica."""

    #Identificador do local
    id: str

    #Cidade do local
    cidade: str

    #Estado do local
    estado: str

    def __repr__(self) -> str:
        """Representação do local de PM"""
        return self.id

    def __str__(self) -> str:
        """Descrição do local de PM"""
        return self.cidade + ' - ' + self.estado
    
@dataclass
class LocaisPM:
    """Classe para a lista de locais de PM."""

    #Lista de Locais de PM
    lista: list[LocalPM]

    def __str__(self) -> str:
        """Descrição de LocaisPM"""
        resultado = '\n'.join(f'\t{local!r}: {local!s}' for local in self.lista)
        return 'Locais de PM cadastradas:\n' + resultado

    def carregar(self) -> None:
        """Carrega a lista de locais de PM do arquivo JSON."""
        with carregar_dados(ARQUIVO_DADOS) as dados:
            self.lista = [LocalPM(codigo, item['cidade'], item['estado']) for codigo, item in dados]

    def obter(self, id: str) -> LocalPM:
        """Retorna um impedimento conforme o ID especificado."""
        for local in self.lista:
            if id == repr(local):
                return local
        return None