## Codificado por Douglas Rodrigues de Almeida.
## Março de 2023
"""Interface de Linha de Comando."""

from .comandosdisponiveis import ComandosDisponiveis
from sistema import Sistema

class LinhaComando:
    """Classe para a Interface de Liinha de Comando"""
    def __init__(self, sistema: Sistema):
        #Indica se existe algum perfil aberto
        self.perfilaberto = False

        #Comandos disponíveis
        self.cmds = None

        #Sistema
        self.sistema = sistema
    
    def avaliar_comando(self, nome_comando: str, args: str) -> None:
        """
        Verifica se o comando obedece às regras pré-estabelecidas e o executa.
        Retorna Verdadeiro se o comando existe na lista de comandos disponíveis.
        Retorna Falso se não existe.
        """
        subcomando = ''
        lista = []
        protocolos = []
        comandos_disponiveis = self.cmds.obter_comandos()
        comandos_disponiveis |= self.sistema.obter_comando_doprocessador()
        if nome_comando == '?':
            self.exibir_ajuda(args)
            return True
        try:
            comando = comandos_disponiveis[nome_comando]
        except KeyError:
            return False
        if args is not None and args.split(' ', 1)[0] == '?':
            try:
                funcao_ajuda = comando['ajuda']
                funcao_ajuda()
                return True
            except KeyError:
                print('Nenhuma ajuda foi encontrada para o comando informado.\n')
                return True
        if comando['requer_processador']:
            if not self.sistema.processador_estaaberto():
                print('Erro: Nenhum perfil está aberto.\n')
                return True
        if comando['requer_get']:
            if not self.sistema.get_estaberto():
                print('Erro: O GET não foi aberto.\n')
                return True
        if comando['requer_pmfagenda']:
            if not self.sistema.pmfagenda_estaberto():
                print('Erro: O PMF Agenda não foi aberto.\n')
                return True
        if args is not None:
            lista = args.split(' ')
        if len(lista) < comando['argsmin']:
            print(f'Erro: Pelo menos {comando["argsmin"]} argumento(s) era(m) esperado(s), mas foi(ram) informado(s) {len(lista)} argumento(s).\n')
            return True
        if comando['requer_subcomando']:
            subcomando = lista[0]
            protocolos = lista[1:]
        else:
            protocolos = lista
        if comando['requer_protocolo']:
            for item in protocolos:
                if not item.isnumeric():
                    print(f'Erro: {item} não é um número de protocolo de tarefa válido.\n')
                    return True
        comando['funcao'](subcomando, protocolos)
        return True
        
    def carregar(self) -> None:
        """Carrega recursos para a linha de comando."""
        self.cmds = ComandosDisponiveis(self.sistema)

    def exibir_cabecalho(self) -> None:
        """Exibe o cabeçalho da linha de comando."""
        self.sistema.exibir_cabecalho()

    def exibir(self) -> None:
        """Exibe a linha de comando."""
        while True:
            lista =  input("UIP:> ").casefold().split(' ', 1)
            comando = lista[0]
            if len(lista) > 1:
                args = lista[1]
            else:
                args = None
            if comando == 'sair':
                break
            if not self.avaliar_comando(comando, args):
                print(f'O comando \'{comando}\' não foi reconhecido como um comando válido.\n')

    def exibir_ajuda(self, args: str) -> None:
        """Exibe os comandos disponíveis e sua descrição."""
        print("\nComandos disponíveis:")
        self.cmds.listar_comandos()