## Codificado por Douglas Rodrigues de Almeida.
## Março de 2023

"""Base de dados do UIP."""

import pandas as pd

class BaseDados:
    """Classe para a base de dados do UIP armazenada em arquivos CSV."""
    def __init__(self, arquivo_dados: str) -> None:
        #Tamanho da base de dados.
        self._tamanho = 0

        #Nome do arquivo CSV da base de dados.
        self.arquivo_dados = arquivo_dados

        #Configuração das colunas que possui o tipo data.
        self.colunas_data = None

        #Dataframe da base de dados.
        self.dados = pd.DataFrame()

        #Configuração com os tipos de valores de cada coluna da base de dados.
        self.tipo_colunas = None

    def adicionar_registros(self, protocolos: list[str]) -> None:
        novos_registros = []
        colunas = list(self.dados)
        for p in protocolos:
            novo_registro = ['' for _ in colunas]
            novo_registro[0] = p
            novos_registros.append(novo_registro)
        df = pd.DataFrame(novos_registros, columns=list(self.dados))
        self.dados = pd.concat([self.dados, df])

    def alterar_atributo(self, idx: int, atributo: str, valor: str) -> None:
        """Altera o atributo especificado do regsitro."""
        self.dados.loc[idx, atributo] = valor

    def alterar_atributo_paraverdadeiro(self, idx: int, atributo: str) -> None:
        """Altera o atributo especificado do regsitro para verdadeiro, com valor igual a 1."""
        self.dados.loc[idx, atributo] = '1'

    def alterar_atributos(self, protocolo: str, atributos: str, valores: str) -> None:
        """Altera múltiplos atributos do registro."""
        num_atributos = len(atributos)
        if (idx := self.pesquisar_indice(protocolo)) is None:
            print(f'Tarefa {protocolo} não foi encontrada.')
            return False
        for i in range(num_atributos):
            self.alterar_atributo(idx, atributos[i].strip(), valores[i].strip())
        return True

    def alterar_atributos_delista(self, lista: list[str]) -> None:
        """
        Altera uma lista de tarefas com uma lista de atributos
        *entrada esperada:
           lista -->
               protocolo nome_atributo1 nome_atributo2 ...
               protocolo1 valor1 valor2 ...
               protocolo2 valor1 valor2 ...
               ....
        Alterações darefas não encontradas na base de dados são descartadas.
        """
        num_alteracoes = 0
        cabecalho = lista[0].strip().split(' ')
        for item in lista[1:]:
            valores = item.strip().split(' ')
            protocolo = valores[0].strip()
            if self.alterar_atributos(protocolo, cabecalho[1:], valores[1:]):
                num_alteracoes += 1
        self.salvar_emarquivo()
        print(f'{num_alteracoes} tarefa(s) alteradas com sucesso.')

    def carregar_dearquivo(self) -> None:
        """Carrega a base de dados do arquivo CSV."""
        if self.colunas_data is None:
            raise Exception()
        if self.tipo_colunas is None:
            raise Exception()
        self.dados = pd.read_csv(self.arquivo_dados, sep=';', dtype=self.tipo_colunas, parse_dates=self.colunas_data)
        self._tamanho = len(self.dados)

    def checar_atributo_nulo(self, idx: int, atributo: str) -> bool:
        """Checa se o atributo especificado é nulo."""
        return pd.isna(self.obter_atributo(idx, atributo))
    
    def checar_atributo_naonulo(self, idx: int, atributo: str) -> bool:
        """Checa se o atributo especificado não é nulo."""
        return pd.notna(self.obter_atributo(idx, atributo))
    
    def checar_atributo_verdadeiro(self, idx: int, atributo: str) -> bool:
        """Checa se o atributo especificado é verdadeiro, com valor igual a 1."""
        return self.checar_atributo_naonulo(idx, atributo) and self.obter_atributo(idx, atributo) == '1'

    def definir_colunas(self, tipocols: dict, colsdata: dict) -> None:
        """Define as configurações de colunas de valores do tipo data."""
        if self.tipo_colunas is None:
            self.tipo_colunas = tipocols
        else:
            self.tipo_colunas |= tipocols
        if self.colunas_data is None:
            self.colunas_data = colsdata
        else:
            self.colunas_data += colsdata

    def limpar_atributos(self, idx: int) -> None:
        """Limpa todos os atributos do registro, exceto o protocolo."""
        colunas = self.dados.columns.tolist()
        lista = 'protocolo;cpf;der;nit;tem_prim_subtarefa;data_subtarefa;tem_prim_exigencia;data_exigencia'.split(';')
        for item in lista:
            colunas.remove(item)
        for coluna in colunas:
            self.dados.loc[idx, coluna] = pd.NA

    def obter_atributo(self, idx: int, atributo: str) -> str:
        """Retorna o valor de um atributo."""
        return self.dados.iloc[idx][atributo]
        
    def obter_dados(self, filtro):
        """Retorna um conjunto de valores filtrados."""
        return self.dados[filtro]

    def obter_lista(self, listagem: dict) -> tuple[int, str]:
        """Retorna uma lista de valores ordenados e sua quantidade."""
        resultado = ''

        with pd.option_context('mode.chained_assignment', None):
            df = self.dados[listagem["filtro"]]
            if (quant := len(df)) > 0:
                df.sort_values(by=listagem["ordenacao"], ascending=listagem["ordem_crescente"], inplace=True)
                resultado = df[listagem["colunas"]].to_string(index=False)
        return (quant, resultado)
       
    def pesquisar_indice(self, protocolo: str):
        """Retorna o índice do protocolo especificado.""" 
        if (df := self.dados[self.dados['protocolo'] == protocolo]).empty:
            return None
        else:
            return df.index[0]
        
    def remover_atributo(self, idx: int, atributo: str) -> None:
        """Exclui o valor do atributo especificado."""
        self.dados.loc[idx, atributo] = pd.NA
    
    def salvar_emarquivo(self) -> None:
        """Salva a base de dados no arquivo CSV."""
        self.dados.to_csv(self.arquivo_dados, sep=';', index=False, date_format='%Y-%m-%d')

    @property
    def tamanho(self) -> int:
        """Retorna o tamanho da base de dados."""
        return self._tamanho
