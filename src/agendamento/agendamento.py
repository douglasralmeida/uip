## Codificado por Douglas Rodrigues de Almeida.
## Junho de 2023
"""Agendamento"""

import pandas as pd
from basedados import TipoBooleano, TipoData, TipoHora, TipoInteiro, TipoTexto, obter_datahoje

class Agendamento:
    """Classe para agendamentos"""
    def __init__(self,  tem_agenda: TipoBooleano) -> None:
        self.arquivopdf = TipoBooleano(False)
        self.tem_agenda = tem_agenda
        self.coletado = TipoBooleano(None)
        self.data = TipoData(None)
        self.hora = TipoHora(None)
        self.local = TipoTexto(None)
        self.protocolo = TipoInteiro(None)

    def __str__(self) -> str:
        if self.tem_agenda:
            return f'\tPerícia em {self.data} às {self.hora}'
        else:
            return '\tNão possui agendamento de PM.'

    def alterar(self, novadata: TipoData, novahora: TipoHora, novolocal: TipoTexto, novoprotocolo: TipoInteiro, novocoletado: TipoBooleano):
        self.coletado = novocoletado
        self.data = novadata
        self.hora = novahora
        self.local = novolocal
        self.protocolo = novoprotocolo

    def alterar_arquivopdf(self, novoarquivopdf: TipoBooleano) -> None:
        """Altera a informação da existência de arquivo PDF com comprovante de agendamento."""
        self.arquivopdf = novoarquivopdf

    def esta_vencido(self) -> bool:
        """Retorna se a data da PM já passou."""
        if self.data.e_nulo:
            raise Exception("Não é possível checar vencimento em data nula.")
        else:
            return self.data.valor < obter_datahoje().valor
        
    def gravar_novo(self, novadata: TipoData, novahora: TipoHora, novolocal: TipoTexto, novoprotocolo: TipoInteiro, novocoletado: TipoBooleano):
        self.coletado = novocoletado
        self.data = novadata
        self.hora = novahora
        self.local = novolocal
        self.protocolo = novoprotocolo
        self.tem_agenda = TipoBooleano(True)
    
    def obter_arquivopdf(self) -> TipoBooleano:
        """Retorna se existe arquivo PDF com comprovante de agendamento."""
        return self.arquivopdf
    
    def obter_coletado(self) -> TipoBooleano:
        """Retorna se o agendamento foi coletado ou processado."""
        return self.coletado
        
    def obter_data(self) -> TipoData:
        """Retorna a data do agendamento."""
        return self.data
    
    def obter_hora(self) -> TipoHora:
        """Retorna a hora do agendamento."""
        return self.hora
    
    def obter_local(self) -> TipoTexto:
        """Retorna o local do agendamento."""
        return self.local
    
    def obter_protocolo(self) -> TipoInteiro:
        """a"""
        return self.protocolo
    
    def tem_agendamento(self) -> TipoBooleano:
        """a"""
        return self.tem_agenda