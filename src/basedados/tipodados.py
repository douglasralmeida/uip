## Codificado por Douglas Rodrigues de Almeida.
## Agosto de 2023

"""Tipos de dados do UIP."""

import pandas as pd
from pandas import Timestamp
from pandas._libs.missing import NAType

NAO_DISPONIVEL = str("(não disponível)")

class TipoBase:
    def __init__(self, valor: str | None) -> None:
        #Dado armazenado.
        if valor is None:
            self._valor = str('')
            self._tamanho = 0
        else:
            self._valor = valor
            self._tamanho = len(self._valor)

    def __repr__(self) -> str:
        """Retorna a representação de valor."""
        return self._valor

    def __str__(self) -> str:
        """Retorna o valor formatado para cadeia de caracteres."""
        if self._tamanho == 0:
            return NAO_DISPONIVEL
        else:
            return self._valor
        
    @property
    def e_nulo(self) -> bool:
        """Retorna se valor é nulo."""
        return self._tamanho == 0
        
    @property
    def tamanho(self) -> int:
        """Retorna o tamanho do valor."""
        return self._tamanho
    
    @property
    def valor(self) -> str | NAType:
        "Retorna o valor conforme salvo na base de dados."
        if self._tamanho == 0:
            return pd.NA
        else:
            return self._valor

class TipoTexto(TipoBase):
    """Classe para dados do tipo texto."""
    def __init__(self, valor: str | None) -> None:
        #Texto armazenado.
        if valor is None or pd.isna(valor):
            super().__init__(None)
        else:
            _valor = valor.strip()
            if len(_valor) == 0:
                super().__init__(None)
            else:
                super().__init__(_valor)

    def __repr__(self) -> str:
        return f'Texto: {super().__repr__()}'
    
    @property
    def e_nulo(self) -> bool:
        """Retorna se valor é nulo."""
        return super().e_nulo
        
    @property
    def tamanho(self) -> int:
        """Retorna o tamanho do valor."""
        return super().tamanho
    
    @property
    def valor(self) -> str | NAType:
        "Retorna o valor conforme salvo na base de dados."
        return super().valor

class TipoInteiro(TipoBase):
    """Classe para dados do tipo número inteiro."""
    def __init__(self, valor: int | str | None) -> None:
        #Dado armazenado.
        if valor is None or pd.isna(valor):
            super().__init__(None)
        elif type(valor) is int:
            super().__init__(str(valor))
        elif type(valor) is str:
            _valor = str(valor).strip()
            if _valor.isnumeric():
                super().__init__(_valor)
            else:
                raise Exception("Valor não é um número inteiro.")

    def __repr__(self) -> str:
        return f'Inteiro: {super().__repr__()}'
    
    @property
    def e_nulo(self) -> bool:
        """Retorna se valor é nulo."""
        return super().e_nulo
        
    @property
    def tamanho(self) -> int:
        """Retorna o tamanho do valor."""
        return super().tamanho
    
    @property
    def valor(self) -> str | NAType:
        "Retorna o valor conforme salvo na base de dados."
        return super().valor    
    
class TipoData:
    """Classe para dados do tipo data."""
    def __init__(self, valor: Timestamp | str | None) -> None:
        #Dado armazenado.
        if valor is None or pd.isna(valor):
            self._valor = pd.NA
            self._tamanho = 0
        elif type(valor) is Timestamp:
            self._valor = valor.floor('D')
            self._tamanho = 10
        elif type(valor) is str:
            _valor = valor.strip()
            if len(_valor) == 0:
                self._valor = pd.NA
                self._tamanho = 0
            elif _valor == 'hoje':
                self._valor = pd.to_datetime('today').floor('D')
                self._tamanho = 10
            else:
                self._valor = pd.to_datetime(valor, format="%d/%m/%Y").floor('D')
                self._tamanho = 10
        else:
            Exception('Formato de data não suportado.')

    def __repr__(self) -> str:
        return f'Data: {self._valor}'

    def __str__(self) -> str:
        """Retorna o valor formatado para cadeia de caracteres."""
        if self._tamanho == 0:
            return NAO_DISPONIVEL
        else:
            return self._valor.strftime('%d/%m/%Y')
        
    def somar_dias(self, num_dias) -> None:
        """Soma um número de dias a data atual."""
        if self._tamanho == 0:
            raise Exception("Não é possível somar dias a uma data nula.")
        else:
            self._valor = self._valor + pd.TimedeltaIndex([num_dias], unit='D')

    @property
    def ja_passou(self) -> bool:
        """a"""
        if self._tamanho == 0:
            raise Exception("Não é possível checar data nula.")
        else:
            return bool(self._valor < pd.to_datetime('today').floor('D'))
    
    @property
    def e_nulo(self) -> bool:
        """Retorna se valor é nulo."""
        return self.tamanho == 0

    @property
    def tamanho(self) -> int:
        """Retorna o tamanho da base de dados."""
        return self._tamanho
    
    @property
    def valor(self) -> Timestamp | NAType:
        "Retorna o valor conforme salvo na base de dados."
        return self._valor
    
def obter_datahoje() -> TipoData:
    return TipoData('hoje')
    
class TipoHora(TipoBase):
    """Classe para dados do tipo hora."""
    def __init__(self, valor: str | None) -> None:
        #Dado armazenado.
        if valor is None or pd.isna(valor):
            super().__init__(None)
        else:
            _valor = valor.strip()
            if len(_valor) == 0:
                super().__init__(None)
            else:
                super().__init__(_valor[:5])

    def __repr__(self) -> str:
        return f'Hora: {super().__repr__()}'
    
    @property
    def e_nulo(self) -> bool:
        """Retorna se valor é nulo."""
        return super().e_nulo
        
    @property
    def tamanho(self) -> int:
        """Retorna o tamanho do valor."""
        return super().tamanho
    
    @property
    def valor(self) -> str | NAType:
        "Retorna o valor conforme salvo na base de dados."
        return super().valor    
    
class TipoBooleano(TipoBase):
    """Classe para dados do tipo booleano."""
    def __init__(self, valor: str | bool | None) -> None:
        #Dado armazenado.
        if valor is None or pd.isna(valor):
            super().__init__(None)
        else:
            if type(valor) is bool:
                if valor:
                    super().__init__('1')
                else:
                    super().__init__('0')
            elif type(valor) is str:
                _valor = str(valor).strip()
                if len(_valor) == 0:
                    super().__init__(None)
                else:
                    super().__init__(_valor)
            else:
                raise Exception("Ops!")

    def __eq__(self, __value: object) -> bool:
        """Implementa o uso do operador =="""
        if isinstance(__value, TipoBooleano):
            return self.valor == __value.valor
        else:
            return False

    def __repr__(self) -> str:
        return f'Booleano: {super().__repr__()}'

    def __str__(self) -> str:
        """Retorna o valor formatado para cadeia de caracteres."""
        if self._valor == '':
            return NAO_DISPONIVEL
        elif self._valor == '1':
            return 'Sim'
        else:   
            return 'Não'
    
    @property
    def e_nulo(self) -> bool:
        """Retorna se valor é nulo."""
        return super().e_nulo
        
    @property
    def e_verdadeiro(self) -> bool:
        """a"""
        return type(self._valor) is str and self._valor == '1'

    @property
    def tamanho(self) -> int:
        """Retorna o tamanho do valor."""
        return super().tamanho
    
    @property
    def valor(self) -> str | NAType:
        "Retorna o valor conforme salvo na base de dados."
        return super().valor    