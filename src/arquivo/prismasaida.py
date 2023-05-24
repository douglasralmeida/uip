from .manipuladorarquivos import Arquivo

class ArquivoPrismaSaida(Arquivo):
    def __init__(self, nome_arquivo, atributos) -> None:
        super().__init__(nome_arquivo)
        self.atributos = atributos
        self.num_atributos = len(atributos)

    def carregar(self):
        i = 0
        super().carregar()
        cabecalho = self.conteudo[0].split(' ')
        cabecalho = [item.strip() for item in cabecalho]
        for item in cabecalho:
            if item != self.atributos[i]:
                print(f'Aviso: O arquivo de entrada do Prisma está inconsistente. O cabecalho difere do esperado ({item}={self.atributos[i]}).')
                break
            i += 1
        for linha in self.conteudo[1:]:
            dado = linha.strip()
            itens = dado.split(' ', 1)
            protocolo = itens[0].strip()
            self.dados[protocolo] = [item.strip() for item in itens[1].split(' ')]
        self.conteudo.clear()
        self.carregado = True

    def salvar(self):
        self.conteudo.append(self.lista_para_string(self.atributos))
        for chave, dados in self.dados.items():
            texto = self.lista_para_string(dados)
            self.conteudo.append(f'{chave} {texto}')
        super().salvar()