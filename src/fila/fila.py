## Codificado por Douglas Rodrigues de Almeida.
## Março de 2023

"""Fila de Tarefas."""

from basedados import BaseDados

class Fila:
    """Classe para as filas de tarefas do GET."""
    def __init__(self, id: str, nome: str, tipo: str, codigo: str, valor_exigencia: float, valor_subtarefa: float, valor_conclusao: float, ativa: bool) -> None:
        #Código da fila
        self._codigo = codigo
        
        #Nome da fila
        self._nome = nome

        #ID da tarefa
        self._id = id

        #Tipo de tarefa
        self._tipo = tipo

        #Pontuação para conclusão da tarefa
        self.pontos_conclusao = valor_conclusao

        #Pontuação para primeira exigência
        self.pontos_exigencia = valor_exigencia

        #Pontuação para subtarefa
        self.pontos_subtarefa = valor_subtarefa

        #Fila está ativa?
        self.ativa = ativa

    def __repr__(self) -> str:
        """Representação de Fila"""
        return self._id + ' (' + self._codigo + ')'

    def __str__(self) -> str:
        """Descrição de Fila"""
        return self._nome

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
        base_dados = BaseDados('tarefas/tarefas_' + self._id + '.csv')
        return base_dados
    
    def get_codigo(self):
        return self._codigo

    def get_id(self):
        """Retorna o ID da fila."""
        return self._id
       
    def get_tipo(self) -> str:
        """Retorna o tipo da fila."""
        return self._tipo

    def processar():
        pass