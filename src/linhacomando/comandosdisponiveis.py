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
                'requer_pat': False,
				'requer_processador': False,
                'requer_pmfagenda': False,
                'requer_sibe': False,
				'requer_sd': False
            },            
            'abrirget': {
                'funcao': sistema.abrir_get,
                'argsmin': 0,
                'desc': 'Abre o navegador Edge e vai para o site do GET.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': False,
                'requer_pat': False,
				'requer_processador': False,
                'requer_pmfagenda': False,
                'requer_sibe': False,
				'requer_sd': False
            },
            'abrirgpa': {
                'funcao': sistema.abrir_gpa,
                'argsmin': 0,
                'desc': 'Abre o navegador Edge e vai para o site do GERID GPA.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': False,
                'requer_pat': False,
				'requer_processador': False,
                'requer_pmfagenda': False,
                'requer_sibe': False,
				'requer_sd': False
            },
            'abrirperfil': {
                'funcao': sistema.carregar_perfil,
                'argsmin': 2,
                'desc': 'Abre um perfil de tarefas do GET especificado.',
                'requer_subcomando': True,
                'requer_cnis': False,
				'requer_get': False,
                'requer_pat': False,
				'requer_processador': False,
                'requer_pmfagenda': False,
                'requer_sibe': False,
				'requer_sd': False
            },
            'abrirpmfagenda': {
                'funcao': sistema.abrir_pmfagenda,
                'argsmin': 0,
                'desc': 'Abre o navegador Edge e vai para o site do PMF Agenda.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': False,
                'requer_pat': False,
				'requer_processador': False,
                'requer_pmfagenda': False,
                'requer_sibe': False,
				'requer_sd': False
            },
            'abrirsd': {
                'funcao': sistema.abrir_sd,
                'argsmin': 0,
                'desc': 'Abre o navegador Edge e vai para o site do SD.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': False,
                'requer_pat': False,
				'requer_processador': False,
                'requer_pmfagenda': False,
                'requer_sibe': False,
				'requer_sd': False
            },
            'abrirsibe': {
                'funcao': sistema.abrir_sibe,
                'argsmin': 0,
                'desc': 'Abre o navegador Edge e vai para o site do SIBE PU.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': False,
                'requer_pat': False,
				'requer_processador': False,
                'requer_pmfagenda': False,
                'requer_sibe': False,
				'requer_sd': False
            },
            'acumulaben': {
                'funcao': sistema.acumula_ben,
                'argsmin': 0,
                'desc': 'Analisa a acumulação de benefícios',
                'requer_subcomando': False,
                'requer_cnis': True,
				'requer_get': False,
                'requer_pat': False,
				'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_sibe': False,
				'requer_sd': False
            },
            'adicionar': {
                'funcao': sistema.adicionar_tarefas,
                'argsmin': 1,
                'desc': 'Adiciona uma lista de tarefas na base de dados.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': False,
                'requer_pat': False,
				'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_sibe': False,
				'requer_sd': False
            },
            'agendapm': {
                'funcao': sistema.mostrar_agenda_pm,
                'argsmin': 0,
                'desc': 'Executa o programa \'Exibir Agenda PM\' do processador.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': False,
                'requer_pat': False,
				'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_sibe': False,
				'requer_sd': False
            },
            'cadastrarusuarios': {
                'funcao': sistema.gpa_cadastrarusuarios,
                'argsmin': 0,
                'desc': 'Cadastra perfil de uma lista de usuários no GERID GPA.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': False,
                'requer_pat': False,
				'requer_processador': False,
                'requer_pmfagenda': False,
                'requer_sibe': False,
				'requer_sd': False
            },
            'coletardb': {
                'funcao': sistema.coletar_db,
                'argsmin': 0,
                'desc': 'Executa o programa \'Coletar Dados Básicos\' do processador.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': True,
                'requer_pat': False,
				'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_sibe': False,
				'requer_sd': False
            },
            'coletardib': {
                'funcao': sistema.coletar_ben,
                'argsmin': 0,
                'desc': 'Executa o programa \'Coletar Dados de DIB\' do processador.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': False,
                'requer_pat': False,
				'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_sibe': True
            },
            'comunicado': {
                'funcao': sistema.mostrar_comunicado,
                'argsmin': 1,
                'desc': 'Exibe o comunicado de decisão da tarefa especificada.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': False,
                'requer_pat': False,
				'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_sibe': False,
				'requer_sd': False
            },
            'concluir': {
                'funcao': sistema.concluir,
                'argsmin': 0,
                'desc': 'Executa o programa \'Concluir Tarefa\' do processador.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': True,
                'requer_pat': False,
				'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_sibe': False,
				'requer_sd': False
            },
            'contarexig': {
                'funcao': sistema.contar_exig,
                'argsmin': 1,
                'desc': 'Conta o número de exigências registradas na tarefa especificada.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': True,
                'requer_pat': False,
				'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_sibe': False,
				'requer_sd': False
            },
            'contarsub': {
                'funcao': sistema.contar_sub,
                'argsmin': 1,
                'desc': 'Conta o número de subtarefas registradas na tarefa especificada.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': True,
                'requer_pat': False,
				'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_sibe': False,
				'requer_sd': False
            },
            'consultarbenporcpf': {
                'funcao': sistema.consultarcpf_ben,
                'argsmin': 1,
                'desc': 'Consulta benefícios pelo CPF informado no CNIS.',
                'requer_subcomando': False,
                'requer_cnis': True,
				'requer_get': False,
                'requer_pat': False,
				'requer_processador': False,
                'requer_pmfagenda': False,
                'requer_sibe': False,
				'requer_sd': False
            },
            'desimpedir': {
                'funcao': sistema.desimpedir,
                'argsmin': 1,
                'desc': 'Remove os impedimentos de conclusão da tarefa especificada.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': False,
                'requer_pat': False,
				'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_sibe': False,
				'requer_sd': False
            },
            'desistir': {
                'funcao': sistema.desistir,
                'argsmin': 1,
                'desc': 'Registra desistência do requerente na tarefa.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': False,
                'requer_pat': False,
				'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_sibe': False,
				'requer_sd': False
            },
            'despacho': {
                'funcao': sistema.mostrar_despacho,
                'argsmin': 1,
                'desc': 'Exibe o despacho conclusivo da tarefa especificada.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': False,
                'requer_pat': False,
				'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_sibe': False,
				'requer_sd': False
            },
            'editartarefa': {
                'funcao': sistema.editar_tarefas,
                'argsmin': 3,
                'desc': 'Edita o atributo especificado de uma ou mais tarefas.',
                'requer_subcomando': True,
                'requer_cnis': False,
				'requer_get': False,
                'requer_pat': False,
				'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_sibe': False,
				'requer_sd': False
            },
            'fases': {
                'funcao': sistema.exibir_fases,
                'argsmin': 0,
                'desc': 'Exibe as fases do fluxo de trabalho para o perfil aberto.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': False,
                'requer_pat': False,
				'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_sibe': False,
				'requer_sd': False
            },
            'filas': {
                'funcao': sistema.exibir_filas,
                'argsmin': 0,
                'desc': 'Exibe as filas cadastradas no UIP.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': False,
                'requer_pat': False,
				'requer_processador': False,
                'requer_pmfagenda': False,
                'requer_sibe': False,
				'requer_sd': False
            },
            'gerarpa': {
                'funcao': sistema.gerar_pa,
                'argsmin': 0,
                'desc': 'Executa o programa \'Gerar PA\' do processador.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': True,
                'requer_pat': False,
				'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_sibe': False,
				'requer_sd': False
            },
            'gerarsub': {
                'funcao': sistema.gerar_subtarefa,
                'argsmin': 0,
                'desc': 'Executa o programa \'Gerar Subtarefa\' do processador.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': True,
                'requer_pat': False,
				'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_sibe': False,
				'requer_sd': False
            },
            'impedir': {
                'funcao': sistema.impedir,
                'argsmin': 2,
                'desc': 'Marca a tarefa especificada com um impedimento para conclusão.',
                'requer_subcomando': True,
                'requer_cnis': False,
				'requer_get': False,
                'requer_pat': False,
				'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_sibe': False,
				'requer_sd': False
            },
            'juntardocs': {
                'funcao': sistema.juntar_docs,
                'argsmin': 0,
                'desc': 'Junta os documentos da análise em um único arquivo.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': False,
                'requer_pat': False,
				'requer_processador': True,
                'requer_pmfagenda': False,
                'requer_sibe': False,
				'requer_sd': False
            },
            'impedimentos': {
                'funcao': sistema.mostrar_impedimentos,
                'argsmin': 0,
                'desc': 'Exibe os impedimentos de conclusão disponíveis para uso.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': False,
                'requer_pat': False,
				'requer_processador': False,
                'requer_pmfagenda': False,
                'requer_sibe': False,
				'requer_sd': False
            },
            'listar': {
                'funcao': sistema.listar,
                'ajuda': sistema.listar_ajuda,
                'argsmin': 1,
                'desc': 'Exibe uma lista de tarefas de acordo com o filtro especificado.',
                'requer_subcomando': True,
                'requer_cnis': False,
				'requer_get': False,
                'requer_pat': False,
				'requer_processador': True,
                'requer_pmfagenda': False,
                
                'requer_sibe': False,
				'requer_sd': False
            },
            'lotes': {
                'funcao': sistema.exibir_lotes,
                'argsmin': 0,
                'desc': 'Exibe os lotes válidos do UIP.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': False,
                'requer_pat': False,
				'requer_processador': False,
                'requer_pmfagenda': False,
                
                'requer_sibe': False,
				'requer_sd': False
            },
            'marcar': {
                'funcao': sistema.marcar,
                'ajuda': sistema.marcar_ajuda,
                'argsmin': 2,
                'desc': 'Exibe uma lista de tarefas de acordo com o filtro especificado.',
                'requer_subcomando': True,
                'requer_cnis': False,
				'requer_get': False,
                'requer_pat': False,
				'requer_processador': True,
                'requer_pmfagenda': False,
                
                'requer_sibe': False,
				'requer_sd': False
            },
            'meta': {
                'funcao': sistema.exibir_producao_metas,
                'argsmin': 1,
                'desc': 'Exibe a produção e a meta do mês atual.',
                'requer_subcomando': True,
                'requer_cnis': False,
				'requer_get': False,
                'requer_pat': False,
				'requer_processador': False,
                'requer_pmfagenda': False,
                
                'requer_sibe': False,
				'requer_sd': False
            },
            'pdftxt': {
                'funcao': sistema.converter_pdf_txt,
                'argsmin': 2,
                'desc': 'Converte arquivos PDF em somente texto.',
                'requer_subcomando': True,
                'requer_cnis': False,
				'requer_get': False,
                'requer_pat': False,
				'requer_processador': False,
                'requer_pmfagenda': False,
                
                'requer_sibe': False,
				'requer_sd': False
            },
            'regdespacho': {
                'funcao': sistema.registrar_despacho,
                'argsmin': 1,
                'desc': 'Registra um despacho na tarefa.',
                'requer_subcomando': True,
                'requer_cnis': False,
				'requer_get': True,
                'requer_pat': False,
				'requer_processador': True,
                'requer_pmfagenda': False,
                
                'requer_sibe': False,
				'requer_sd': False
            },
            'resumo': {
                'funcao': sistema.exibir_resumo,
                'argsmin': 0,
                'desc': 'Exibe o resumo das tarefas do perfil aberto.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': False,
                'requer_pat': False,
				'requer_processador': True,
                'requer_pmfagenda': False,
                
                'requer_sibe': False,
				'requer_sd': False
            },
            'tarefa': {
                'funcao': sistema.exibir_tarefa,
                'argsmin': 1,
                'desc': 'Exibe o resumo das tarefas do perfil aberto.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': False,
                'requer_pat': False,
				'requer_processador': True,
                'requer_pmfagenda': False,
                
                'requer_sibe': False,
				'requer_sd': False
            },
            'processarlote': {
                'funcao': sistema.processar_lote,
                'argsmin': 1,
                'desc': 'Altera um lote de dados na base de dados do UIP.',
                'requer_subcomando': True,
                'requer_cnis': False,
				'requer_get': False,
                'requer_pat': False,
				'requer_processador': True,
                'requer_pmfagenda': False,
                
                'requer_sibe': False,
				'requer_sd': False
            },            
            'puxar': {
                'funcao': sistema.puxar_tarefa,
                'argsmin': 0,
                'desc': 'Puxa uma tarefa no GET.',
                'requer_subcomando': True,
                'requer_cnis': False,
				'requer_get': True,
                'requer_pat': False,
				'requer_processador': False,
                'requer_pmfagenda': False,
                
                'requer_sibe': False,
				'requer_sd': False
            },
            'reprocessarbpc': {
                'funcao': sistema.reprocessar_bpc,
                'argsmin': 1,
                'desc': 'Reprocessar um lote de BPC com erro de integração GET-SIBE-PU.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': False,
                'requer_pat': True,
				'requer_processador': False,
                'requer_pmfagenda': False,
                
                'requer_sibe': False,
				'requer_sd': False
            },            
            'usarintranet': {
                'funcao': sistema.usar_intranet,
                'argsmin': 0,
                'desc': 'Altera o parâmetro de uso do GET via intranet ou Internet.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': False,
                'requer_pat': False,
				'requer_processador': False,
                'requer_pmfagenda': False,
                
                'requer_sibe': False,
				'requer_sd': False
            },
            'ver': {
                'funcao': sistema.visualizacao_rapida,
                'argsmin': 0,
                'desc': 'Visualiza uma lista de tarefas rapidamente.',
                'requer_subcomando': False,
                'requer_cnis': False,
				'requer_get': True,
                'requer_pat': False,
				'requer_processador': True,
                'requer_pmfagenda': False,
                
                'requer_sibe': False,
				'requer_sd': False         
            }
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
    
    def obter_comandos(self) -> dict:
        """Retorna a lista de comandos especificado."""
        return self._lista