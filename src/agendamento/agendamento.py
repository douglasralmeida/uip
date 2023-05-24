## Codificado por Douglas Rodrigues de Almeida.
## Março de 2023
"""Agendamento"""

class Agendamento:
    """Classe para Agendamento"""
    def __init__(self, novadata, novahora, novolocal) -> None:
        self.arquivopdf = False
        self.data = novadata
        self.hora = novahora
        self.local = novolocal

    def __str__(self) -> str:
        return f'{self.data.strftime("%d/%m/%Y")} às {self.hora}'

    def alterar_arquivopdf(self, novoarquivopdf: bool) -> None:
        """Altera a informação da existência de arquivo PDF com comprovante de agendamento."""
        self.arquivopdf = novoarquivopdf
    
    def obter_arquivopdf(self) -> bool:
        """Retorna se existe arquivo PDF com comprovante de agendamento."""
        return self.arquivopdf
        
    def obter_data(self) -> str:
        """Retorna a data do agendamento."""
        return self.data
    
    def obter_hora(self) -> str:
        """Retorna a hora do agendamento."""
        return self.hora
    
    def obter_local(self) -> str:
        """Retorna o local do agendamento."""
        return self.local