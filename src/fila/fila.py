## Codificado por Douglas Rodrigues de Almeida.
## Março de 2023

"""Fila de Tarefas."""

from basedados import BaseDados

class Fila:
    """Classe para as filas de tarefas do GET."""
    def __init__(self, id: str, nome: str) -> None:
        #Nome da fila
        self._nome = nome

        #ID da tarefa
        self._id = id

        #Pontuação para conclusão da tarefa
        self.pontos_conclusao = 0

        #Pontuação para primeira exigência
        self.pontos_exigencia = 0

        #Pontuação para subtarefa
        self.pontos_subtarefa = 0

    def alterar_pontos_conclusao(self, valor: float) -> None:
        """Altera o valor da pontuação para conclusão da tarefa."""
        self.pontos_conclusao = valor

    def alterar_pontos_exigencia(self, valor) -> None:
        """Altera o valor da pontuação para primeira exigência na tarefa."""
        self.pontos_conclusao = valor

    def alterar_pontos_subtarefa(self, valor) -> None:
        """Altera o valor da pontuação para primeira subtarefa na tarefa."""
        self.pontos_conclusao = valor

    def carregar(self) -> BaseDados:
        base_dados = BaseDados('tarefas/tarefas_' + self._nome + '.csv')
        base_dados.carregar_dearquivo()

        return base_dados

    def processar():
        pass