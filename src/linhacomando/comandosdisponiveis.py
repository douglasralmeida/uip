## Codificado por Douglas Rodrigues de Almeida.
## Março de 2023
"""Comandos disponibilizados pela linha de comando ao usuário."""

from sistema import Sistema

class ComandosDisponiveis:
    """Classe com comandos disponibilizados para o usuário."""
    def __init__(self, sistema: Sistema):
        #Comandos disponíveis para o usuário.
        self._lista = {
            'abrircnis': {
                'funcao': sistema.abrir_cnis,
                'argsmin': 0,
                'desc': 'Abre o navegador Edge e vai para o site do Portal CNIS.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': False,
                'requer_processador': False,
                'requer_pmfagenda': False,
                'requer_protocolo': False,
                'requer_sibe': False
            },            
            'abrirget': {
                'funcao': sistema.abrir_get,
                'argsmin': 0,
                'desc': 'Abre o navegador Edge e vai para o site do GET.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': False,
                'requer_processador': False,
                'requer_pmfagenda': False,
                'requer_protocolo': False,
                'requer_sibe': False
            },
            'abrirperfil': {
                'funcao': sistema.carregar_perfil,
                'argsmin': 2,
                'desc': 'Abre um perfil de tarefas do GET especificado.',
                'requer_subcomando': True,
                'requer_cnis': False,
				'requer_get': False,
                'requer_processador': False,
                'requer_pmfagenda': False,
                'requer_protocolo': False,
                'requer_sibe': False
            },
            'abrirpmfagenda': {
                'funcao': sistema.abrir_pmfagenda,
                'argsmin': 0,
                'desc': 'Abre o navegador Edge e vai para o site do PMF Agenda.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': False,
                'requer_processador': False,
                'requer_pmfagenda': False,
                'requer_protocolo': False,
                'requer_sibe': False
            },
            'acumulaben': {
                'funcao': sistema.acumula_ben,
                'argsmin': 0,
                'desc': 'Analisa a acumulação de benefícios',
                'requer_subcomando': False,
                'requer_cnis': True,
				'requer_get': False,
                'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_protocolo': False,
                'requer_sibe': False
            },
            'adicionar': {
                'funcao': sistema.adicionar_tarefas,
                'argsmin': 1,
                'desc': 'Adiciona uma lista de tarefas na base de dados.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': False,
                'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_protocolo': True,
                'requer_sibe': False
            },
            'agendapm': {
                'funcao': sistema.mostrar_agenda_pm,
                'argsmin': 0,
                'desc': 'Executa o programa \'Exibir Agenda PM\' do processador.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': False,
                'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_protocolo': True,
                'requer_sibe': False
            },
            'agendarpm': {
                'funcao': sistema.agendar_pm,
                'argsmin': 0,
                'desc': 'Executa o programa \'Agendar PM\' do processador.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': False,
                'requer_processador': True,
                'requer_pmfagenda': True,
                'requer_protocolo': False,
                'requer_sibe': False
            },
            'coletardb': {
                'funcao': sistema.coletar_db,
                'argsmin': 0,
                'desc': 'Executa o programa \'Coletar Dados Básicos\' do processador.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': True,
                'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_protocolo': False,
                'requer_sibe': False
            },
            'comunicado': {
                'funcao': sistema.mostrar_comunicado,
                'argsmin': 1,
                'desc': 'Exibe o comunicado de decisão da tarefa especificada.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': False,
                'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_protocolo': True,
                'requer_sibe': False
            },
            'concluir': {
                'funcao': sistema.concluir,
                'argsmin': 0,
                'desc': 'Executa o programa \'Concluir Tarefa\' do processador.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': True,
                'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_protocolo': False,
                'requer_sibe': False
            },
            'contarexig': {
                'funcao': sistema.contar_exig,
                'argsmin': 1,
                'desc': 'Conta o número de exigências registradas na tarefa especificada.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': True,
                'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_protocolo': True,
                'requer_sibe': False
            },
            'contarsub': {
                'funcao': sistema.contar_sub,
                'argsmin': 1,
                'desc': 'Conta o número de subtarefas registradas na tarefa especificada.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': True,
                'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_protocolo': True,
                'requer_sibe': False
            },
            'desimpedir': {
                'funcao': sistema.desimpedir,
                'argsmin': 1,
                'desc': 'Remove os impedimentos de conclusão da tarefa especificada.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': False,
                'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_protocolo': True,
                'requer_sibe': False
            },
            'desistir': {
                'funcao': sistema.desistir,
                'argsmin': 1,
                'desc': 'Registra desistência do requerente na tarefa.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': False,
                'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_protocolo': True,
                'requer_sibe': False
            },
            'despacho': {
                'funcao': sistema.mostrar_despacho,
                'argsmin': 1,
                'desc': 'Exibe o despacho conclusivo da tarefa especificada.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': False,
                'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_protocolo': True,
                'requer_sibe': False
            },
            'editartarefa': {
                'funcao': sistema.editar_tarefas,
                'argsmin': 3,
                'desc': 'Edita o atributo especificado de uma ou mais tarefas.',
                'requer_subcomando': True,
                'requer_cnis': False,
				'requer_get': False,
                'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_protocolo': True,
                'requer_sibe': False
            },
            'fases': {
                'funcao': sistema.exibir_fases,
                'argsmin': 0,
                'desc': 'Exibe as fases do fluxo de trabalho para o perfil aberto.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': False,
                'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_protocolo': False,
                'requer_sibe': False
            },
            'gerarsub': {
                'funcao': sistema.gerar_subtarefa,
                'argsmin': 0,
                'desc': 'Executa o programa \'Gerar Subtarefa\' do processador.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': True,
                'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_protocolo': False,
                'requer_sibe': False
            },
            'impedir': {
                'funcao': sistema.impedir,
                'argsmin': 2,
                'desc': 'Marca a tarefa especificada com um impedimento para conclusão.',
                'requer_subcomando': True,
                'requer_cnis': False,
				'requer_get': False,
                'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_protocolo': True,
                'requer_sibe': False
            },
            'impedimentos': {
                'funcao': sistema.mostrar_impedimentos,
                'argsmin': 0,
                'desc': 'Exibe os impedimentos de conclusão disponíveis para uso.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': False,
                'requer_processador': False,
                'requer_pmfagenda': False,
                'requer_protocolo': False,
                'requer_sibe': False
            },
            'listar': {
                'funcao': sistema.listar,
                'ajuda': sistema.listar_ajuda,
                'argsmin': 1,
                'desc': 'Exibe uma lista de tarefas de acordo com o filtro especificado.',
                'requer_subcomando': True,
                'requer_cnis': False,
				'requer_get': False,
                'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_protocolo': False,
                'requer_sibe': False
            },
            'marcar': {
                'funcao': sistema.marcar,
                'ajuda': sistema.marcar_ajuda,
                'argsmin': 2,
                'desc': 'Exibe uma lista de tarefas de acordo com o filtro especificado.',
                'requer_subcomando': True,
                'requer_cnis': False,
				'requer_get': False,
                'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_protocolo': True,
                'requer_sibe': False
            },
            'meta': {
                'funcao': sistema.exibir_producao_metas,
                'argsmin': 1,
                'desc': 'Exibe a produção e a meta do mês atual.',
                'requer_subcomando': True,
                'requer_cnis': False,
				'requer_get': False,
                'requer_processador': False,
                'requer_pmfagenda': False,
                'requer_protocolo': False,
                'requer_sibe': False
            },
            'pdftxt': {
                'funcao': sistema.converter_pdf_txt,
                'argsmin': 2,
                'desc': 'Converte arquivos PDF em somente texto.',
                'requer_subcomando': True,
                'requer_cnis': False,
				'requer_get': False,
                'requer_processador': False,
                'requer_pmfagenda': False,
                'requer_protocolo': True,
                'requer_sibe': False
            },
            'resumo': {
                'funcao': sistema.exibir_resumo,
                'argsmin': 0,
                'desc': 'Exibe o resumo das tarefas do perfil aberto.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': False,
                'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_protocolo': False,
                'requer_sibe': False
            },
            'tarefa': {
                'funcao': sistema.exibir_tarefa,
                'argsmin': 1,
                'desc': 'Exibe o resumo das tarefas do perfil aberto.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': False,
                'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_protocolo': True,
                'requer_sibe': False
            },
            'puxar': {
                'funcao': sistema.puxar_tarefa,
                'argsmin': 0,
                'desc': 'Puxa uma tarefa no GET.',
                'requer_subcomando': True,
                'requer_cnis': False,
				'requer_get': True,
                'requer_processador': False,
                'requer_pmfagenda': False,
                'requer_protocolo': False,
                'requer_sibe': False
            },
            'usarintranet': {
                'funcao': sistema.usar_intranet,
                'argsmin': 0,
                'desc': 'Altera o parâmetro de uso do GET via intranet ou Internet.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': False,
                'requer_processador': False,
                'requer_pmfagenda': False,
                'requer_protocolo': False,
                'requer_sibe': False
            },
        }
        
    def executar(self, comando: str, subcomando: str, protocolos: str) -> None:
        """Executa o comando especificado."""
        self._lista[comando]['funcao'](subcomando, protocolos)

    def existe(self, nome_comando: str) -> None:
        """Verifica se o comando especificado existe na lista de comnandos disponíveis."""
        return nome_comando in self._lista
    
    def listar_comandos(self) -> None:
        """Exibe a lista dos comandos disponíveis e sua descrição."""
        for nome, cmd in self._lista.items():
            print(f'{nome} - {cmd["desc"]}')
    
    def obter_comandos(self) -> None:
        """Retorna a lista de comandos especificado."""
        return self._lista