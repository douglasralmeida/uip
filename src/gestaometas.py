import datetime
from arquivo import carregar_dados

ARQUIVO_METADIARIA = 'meta_diaria.json'

ARQUIVO_METAS = 'metas.json'

class MetaDiaria:
    def __init__(self) -> None:
        self.valores = {}

    def carregar(self):
        with carregar_dados(ARQUIVO_METADIARIA) as dados:
            self.valores = dados

    def exibir_meta_hoje(self):
        data_hoje = datetime.date.today()
        meta_diaria = self.obter_meta_diaria(f'{data_hoje.month}/{data_hoje.year}')
        print(f'Meta diária do mês: {meta_diaria}')

    def obter_meta_diaria(self, competencia):
        data_competencia = datetime.datetime.strptime('01/' + competencia, '%d/%m/%Y').date()
        
        for _, valor in self.valores.items():
            data_inicio = datetime.datetime.strptime(valor['inicio'], '%d/%m/%Y').date()
            data_fim = datetime.datetime.strptime(valor['fim'], '%d/%m/%Y').date()
            if (data_competencia >= data_inicio) and (data_competencia <= data_fim):
                return valor['valor']
        print(f'Erro: Não existe meta diária cadastrada para a competência {competencia}.\n')

class Meta:
    def __init__(self, competencia, dias_uteis) -> None:
        self.competencia = competencia
        self.dias_ferias = 0
        self.dias_licenca = 0
        self.dias_uteis = dias_uteis
        self.abono_ferias = 0
        self.abono_licencas = 0
        self.abono_sistemas = 0
        self.meta_diaria = 0

    def alterar_abono_sistemas(self, abono):
        self.abono_sistemas = abono

    def alterar_ferias(self, dias):
        self.dias_ferias = dias
        self.abono_ferias = dias * self.meta_diaria

    def alterar_licencas(self, dias):
        self.dias_licenca = dias
        self.abono_licencas = dias * self.meta_diaria

    def alterar_meta_diaria(self, meta_diaria):
        self.meta_diaria = meta_diaria

    def obter_competencia(self):
        return self.competencia
    
    def obter_dias_ferias(self):
        return self.dias_ferias

    def obter_dias_licenca(self):
        return self.dias_licenca
    
    def obter_meta_bruta(self):
        return self.dias_uteis * self.meta_diaria
    
    def obter_meta_liquida(self):
        return self.obter_meta_bruta() - self.abono_sistemas - self.abono_ferias - self.abono_licencas
    
    def obter_abono_sistemas(self):
        return self.abono_sistemas

class Producao:
    def __init__(self, competencia) -> None:
        self.competencia = competencia
        self.filas = []
        self.pontos_conclusao = 0
        self.pontos_subtarefas = 0
        self.pontos_exigencias = 0

    def processar():
        pass

class GestaoMetas:
    def __init__(self) -> None:
        self.meta_diaria = MetaDiaria()
        self.metas = []

    def carregar_dados(self):
        self.meta_diaria.carregar()

        with carregar_dados(ARQUIVO_METAS) as metas:
            for item, valor in metas.items():
                meta = Meta(item, valor['dias_uteis'])
                meta.alterar_ferias(valor['dias_ferias'])
                meta.alterar_licencas(valor['dias_licenca'])
                meta.alterar_abono_sistemas(valor['abono_sistemas'])
                meta.alterar_meta_diaria(self.meta_diaria.obter_meta_diaria(item))
                self.metas.append(meta)

    def exibir_meta_atual(self):
        data_hoje = datetime.date.today()
        competencia = f'{data_hoje.month}/{data_hoje.year}'
        self.exibir_meta_competencia(competencia)

    def exibir_meta_competencia(self, competencia):
        possui_cadastro = False
        for item in self.metas:
            if competencia == item.obter_competencia():
                meta = item
                possui_cadastro = True
        if not possui_cadastro:
            print(f'Erro: Competência {competencia} não cadastrada no gestor de metas.\n')
            return
        print(f'META PARA COMPETÊNCIA {competencia}')
        print('-----------------------------')

        print(f'Meta bruta: {meta.obter_meta_bruta():.2f}')
        print(f'Abono de sistemas: {meta.obter_abono_sistemas():.2f}')
        print(f'Dias de férias: {meta.obter_dias_ferias():.2f}')
        print(f'Dias de licença: {meta.obter_dias_licenca():.2f}')
        print(f'Meta líquida: {meta.obter_meta_liquida():.2f}\n')

    def exibir_producao_competencia(self, competencia):
        producao = Producao(competencia)

        print(f'PRODUCAO PARA COMPETÊNCIA {competencia}')
        print('---------------------------------')

        print(f'Producao por conclusão de tarefas: {0:.2f}')
        print(f'Producao por subtarefas: {0:.2f}')
        print(f'Producao por exigências: {0:.2f}')
        print(f'Produção total: {0:.2f}')