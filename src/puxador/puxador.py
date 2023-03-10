## Codificado por Douglas Rodrigues de Almeida.
## Março de 2023
"""Puxador de Tarefas"""

import pandas as pd
from navegador import Get

colunas_dados = {'protocolo': 'string',
                       'servico': 'string'
                      }

class Puxador:
    """Classe do Puxador de Tarefas do GET."""
    def __init__(self) -> None:
        #Arquivo da lista de tarefas
        self.arquivo_dados = 'tarefas/tarefas_puxadas.csv'

        #Tabela de tarefas puxadas.
        self.tarefas = pd.DataFrame()

        #Automatizador do Get.
        self.get = None

    def __str__(self) -> str:
        if self.obter_tamanho() == 0:
            resultado = 'Lista de tarefas puxadas está vazia.\n'

        return resultado

    def abrir_lista(self) -> None:
        """Abre a lista de tarefas recém-puxadas."""
        self.tarefas = pd.read_csv(self.arquivo_dados, sep=';', dtype=colunas_dados)

    def adicionar_item(self, protocolo: str, servico: str) -> None:
        """Adiciona uma nova tarefa na lista de tarefas recém-puxadas."""
        novo_registro = {'protocolo': protocolo, 'servico': servico}
        self.tarefas.loc[len(self.tarefas)] = novo_registro

    def definir_get(self, get: Get) -> None:
        """Define o navegador para automatização do Get."""
        self.get = get

    def obter_tamanho(self) -> int:
        """Retorna a quantidade de tarefas recém-puxadas."""
        return len(self.tarefas)
    
    def puxar(self) -> bool:
        """Puxa uma tarefa e coleta seu número."""
        drv = self.get

        #Clica no botão puxar Proxima Tarefa
        drv.clicar_botao('formTarefas:puxarTarefaServidorSemAfastamento')

        #Aguarda o processamento
        drv.aguardar_telaprocessamento

        ##Aguarda abertura da tarefa
        drv.aguardar_visibilidade_elemento('panel-title')

        #Coleta o número da tarefa
        protocolo = drv.coletar_numero_porclasse('panel-title')
        servico = drv.coletar_nomeservico()
        print(f'Tarefa {protocolo} puxada.')

        #Salva os dados na lista de tarefas
        self.adicionar_item(protocolo, servico)

        #Fecha a tarefa
        drv.fechar_tarefa()

        return True

    def salvar_lista(self) -> None:
        """Salva a lista de tarefas recém-puxadas."""
        self.tarefas.to_csv(self.arquivo_dados, sep=';', index=False)