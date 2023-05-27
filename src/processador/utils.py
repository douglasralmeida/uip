from arquivo import carregar_dados
from os import path

ARQUIVO_PERITOS = 'peritos.json'

def pesquisar_texto(lista: list[str], info: str) -> int:
    """Pesquisa um texto na lista de textos especificada."""
    tamanho = len(info)
    pos = 0
    for item in lista:
        if item[:tamanho] == info:
            return pos
        pos += 1
    return -1

def analisar_relatoriopm(nome_arquivo: str) -> list[str]:
    """Analisa o arquivo texto da PM."""
    pos = 0
    resultado_pm = 'vazio'
    siape_pm = '0'
    dados_estruturados = ['','','','','','','','','','','', '']
    if path.exists(nome_arquivo):
        with open(nome_arquivo, 'r') as arquivo:
            dados_crus = arquivo.readlines()
    else:
        return None
    with carregar_dados(ARQUIVO_PERITOS) as dados:
        peritos = dados
    pos = pesquisar_texto(dados_crus, 'médico pericial, conclui-se que:Não há sequela')
    if pos > 0:
        resultado_pm = 'indeferido'
        dados_estruturados[11] = 'b36SemSequela'
    pos = pesquisar_texto(dados_crus, 'médico pericial, conclui-se que:Há sequela definitiva, porém')
    if pos > 0:
        resultado_pm = 'indeferido'
        dados_estruturados[11] = 'b36NaoEnquadraA3Decreto'
    pos = pesquisar_texto(dados_crus, 'concessão de Auxílio-Acidente Acidentário (B94).')
    if pos > 0:
        resultado_pm = 'deferido94'
        dados_estruturados[11] = 'b94Deferido'
    pos = pesquisar_texto(dados_crus, 'de Auxílio-Acidente Previdenciário (B36).')
    if pos > 0:
        resultado_pm = 'deferido36'
        dados_estruturados[11] = 'b36Deferido'
    if resultado_pm == 'deferido94' or resultado_pm == 'deferido36':
        #DID
        pos = pesquisar_texto(dados_crus, 'Data do acidente ')
        if pos > 0:
            if len(dados_crus[pos]) == 28:
                data_acidente = dados_crus[pos][-11:].strip()
                dados_estruturados[0] = data_acidente
                #DII
                dados_estruturados[1] = data_acidente
                #Data do Acidente
                dados_estruturados[3] = data_acidente
        #Houve Acidente?
        dados_estruturados[2] = 'S'
        #Acidente de Trabalho?
        if resultado_pm == 'deferido94':
            dados_estruturados[4] = 'S'
        else:
            dados_estruturados[4] = 'N'
        #Sequela Enquadra?
        dados_estruturados[5] = 'S'
        #Conclusão
        dados_estruturados[7] = '4'            
    else:
        dados_estruturados[0] = ''
        dados_estruturados[1] = ''
        dados_estruturados[2] = 'N'
        dados_estruturados[3] = ''
        dados_estruturados[4] = ''
        dados_estruturados[5] = ''
        dados_estruturados[7] = '1'
    #Dt Marcacao
    pos = pesquisar_texto(dados_crus, 'Data de entrada:')
    if pos >= 0:
        dados_estruturados[6] = dados_crus[pos][17:27]
    else:
        dados_estruturados[6] = 'data_marcacao'
    #CID
    pos = pesquisar_texto(dados_crus, 'Procurador(es) / Representante(s)')
    if pos >= 0:
        pos += 1
        while True:
            texto = dados_crus[pos][:6].strip()
            if '-' in texto:
                break
            pos += 1      
        dados_estruturados[8] = dados_crus[pos][:4].strip()
    else:
        dados_estruturados[8] = 'cid10'
    #Código do perito
    pos = pesquisar_texto(dados_crus, 'Matrícula SIAPE do perito')
    if pos >= 0:
        siape_pm = dados_crus[pos][-8:].strip()
        dados_estruturados[9] = f'codigo_perito:{siape_pm}'
        for item, valor in peritos:
            if item == siape_pm:
                dados_estruturados[9] = valor
    else:
        dados_estruturados[9] = 'codigo_perito'
    if dados_estruturados[9] == f'codigo_perito:{siape_pm}':
        print(f'Atenção: Matrícula SIAPE {siape_pm} não encontrada na base de dados do UIP.')
    #Data de Conclusão
    pos = pesquisar_texto(dados_crus, 'FEDERALConcluída')
    if pos >= 0:
        dados_estruturados[10] = dados_crus[pos+1][:10]
    else:
        dados_estruturados[10] = 'data_conclusao'
    return dados_estruturados