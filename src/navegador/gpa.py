## Codificado por Douglas Rodrigues de Almeida.
## Maio de 2024

"""Automatizador do GERID GPA."""

import time
import os
from PIL import Image
from arquivo import carregar_texto
from .navegador import Navegador
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select

URL_GPA = 'https://geridinss.dataprev.gov.br/gpa/'

class Atribuicao():
    def __init__(self, sistema: str, subsistema: str, papel: str) -> None:
        self.sistema = sistema
        self.subsistema = subsistema
        self.papel = papel
        self.data_validade = '30/12/2024'
        self.hora_inicio = '00:00'
        self.hora_fim = '23:59'

class Usuario():
    def __init__(self, dominio: str, valor: str) -> None:
        self.dominio = dominio
        self.valor = valor

class Gpa(Navegador):
    """Classe do Automatizador do sd."""
    def __init__(self) -> None:
        super().__init__()
        self.atribuicao: Atribuicao = Atribuicao('SUB', 'PAB.SUB', 'USUARIO_PAB_SUP.PAB.SUB')
        self.usuarios: list[Usuario] = []
        self.tem_mensagem = False
        self.mensagem = ''

    def abrir(self):
        """Abre o sd."""
        self.driver.get(URL_GPA)
        #Aguarda autenticação
        time.sleep(10)

    def aguardar_processamento(self) -> None:
        """Espera pelo encerramento da tela 'Aguardando processamento'"""
        espera = WebDriverWait(self.driver, 60, poll_frequency=1)
        #Aguarda pela invisibilidade do elemento
        espera.until(EC.invisibility_of_element((By.ID, 'loading')))

    def abrir_dadospapeis(self):
        None

    def abrir_dadosusuarios(self):
        with carregar_texto('lista_usuarios.csv') as lista:
            for item in lista:
                valores = item.split(';')
                dominio = valores[0]
                valor = valores[1]
                self.usuarios.append(Usuario(dominio, valor))

    def abrir_novo_multiplos_papeis(self):
        """Abre a tela de consulta de benefício."""
        nav = self.driver

        script = f"jsfcljs(document.getElementById('formMenu'),{{'formMenu:btAtribAcesso':'formMenu:btAtribAcesso'}},'');"
        self.executar_script(script)
        self.aguardar_processamento()
        WebDriverWait(nav, timeout=60).until(EC.visibility_of_element_located((By.ID, 'form2:novo')))
        self.tela_atual = 'GPA_VerAtribuicoes'

        self.clicar_botao('form2:novoMultiUsuarios')
        self.aguardar_processamento()
        WebDriverWait(nav, timeout=60).until(EC.visibility_of_element_located((By.ID, 'form2:avancar')))

    def cadastrar_usuario_lista(self):
        cadastrou_usuario = False
        nav = self.driver

        self.abrir_dadospapeis()
        self.abrir_dadosusuarios()
        
        elemento = nav.find_element(By.ID, 'form:sistema')
        seletor = Select(elemento)
        seletor.select_by_value(self.atribuicao.sistema)
        self.aguardar_processamento()

        elemento = nav.find_element(By.ID, 'form:subsistema')
        seletor = Select(elemento)
        seletor.select_by_value(self.atribuicao.subsistema)
        self.aguardar_processamento()

        elemento = nav.find_element(By.ID, 'form2:papel')
        seletor = Select(elemento)
        seletor.select_by_value(self.atribuicao.papel)  

        elemento = nav.find_element(By.ID, 'form2:tipoDominio')
        seletor = Select(elemento)
        seletor.select_by_value('UO')

        elemento = nav.find_element(By.ID, 'form2:dataValidade')
        elemento.send_keys(Keys.HOME)
        elemento.send_keys(self.atribuicao.data_validade)

        elemento = nav.find_element(By.ID, 'form2:periodo:0')
        elemento.click()

        elemento = nav.find_element(By.ID, 'form2:periodo:6')
        elemento.click()

        elemento = nav.find_element(By.ID, 'form2:periodo:7')
        elemento.click()

        elemento = nav.find_element(By.ID, 'form2:horaAcessoInicio')
        elemento.send_keys(Keys.HOME)
        elemento.send_keys(self.atribuicao.hora_inicio)

        elemento = nav.find_element(By.ID, 'form2:horaAcessoFim')
        elemento.send_keys(Keys.HOME)
        elemento.send_keys(self.atribuicao.hora_fim)

        elemento = nav.find_element(By.ID, 'form2:avancar')
        elemento.click()
        self.aguardar_processamento()
        WebDriverWait(nav, timeout=60).until(EC.visibility_of_element_located((By.ID, 'form2:voltar')))

        for usuario in self.usuarios:
            elemento = nav.find_element(By.ID, 'form2:dominio')
            elemento.send_keys(Keys.CONTROL, 'A')
            elemento.send_keys(Keys.DELETE)
            elemento.send_keys(usuario.dominio)
            elemento = nav.find_element(By.ID, 'form2:usuario')
            elemento.send_keys(usuario.valor)

            elemento = nav.find_element(By.ID, 'form2:inserirUsuario')
            elemento.click()
            self.aguardar_processamento()
            self.coletar_mensagem()
            if self.tem_mensagem:
                print(f"Erro ao inserir usuário {usuario.valor}: {self.mensagem}")
            else:
                print(f"Usuário {usuario.valor} inserido com sucesso.")
                cadastrou_usuario = True
        #if cadastrou_usuario:
            #elemento = nav.find_element(By.ID, 'form2:concluir')
            #elemento.click()
            #self.aguardar_processamento()

    def coletar_mensagem(self):
        nav = self.driver
        if len(elemento := nav.find_elements(By.CLASS_NAME, value='erro')) > 0:
            self.mensagem = elemento[0].text
            self.tem_mensagem = True
        else:
            self.mensagem = ''
            self.tem_mensagem = False
