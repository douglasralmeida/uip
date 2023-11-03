Attribute VB_Name = "Prisma"
Attribute VB_GlobalNameSpace = True
Attribute VB_Creatable = True
Attribute VB_Exposed = True
Attribute VB_PredeclareID = True
Attribute VB_Description = "Prisma"

Option Explicit

'#Uses "utils.bas"

'PRISMA.CLS
'File|New Module|Class Module
'Edit|Properties|Name=Prisma

'Beneficio Inacumulavel
Dim BeneficioInacumulavel As String

'DIB Inacumulavel
Dim DIBInacumulavel As String

'Especie do beneficio
Dim Especie As Integer

'NIT do requerente
Dim Nit As String

'Numero de beneficio gerado
Dim Numero As String

'Protocolo da tarefa GET
Dim Protocolo As String

'Indica que o processamento gerou erro
Dim ErroProcessamento As Boolean

Private Sub Class_Initialize()
    Debug.Print("Inicializando Classe Prisma...")
	ErroProcessamento = False
End Sub

Private Sub Class_Terminate()
    Debug.Print("Finalizando Classe Prisma...")
End Sub

'Processa o despacho de um beneficio para o SUB
Sub Prisma_DespacharBeneficio(NB As String, Resultado As String)
	Dim InformarAcumulacao As Boolean
	Dim Der As String
	Dim I As Integer
	Dim NumRepeticoes As Integer

	InformarAcumulacao = False

	With ActiveSession
		.SetSelection 0, 0, 0, 0
		.InputMode = 0

		Debug.Print("Prisma: Abrindo o beneficio...")
		.Output NB & ChrW$(13) 'Entrar no BEN

		Debug.Print("Prisma: Ir para Tela Despacho...")
		.Output "16" & ChrW$(13) 'Ir para Tela de Despacho
		While Not TextoNaTela(29, 1, "DESPACHO DA CONCESSAO")
			Sleep(1000)
		Wend
		If TextoNaTela(24, 7, "          ") Then
			Der = .GetText(67, 4, 10, 0)
			.Output Der & ChrW$(13) 'DRD
			Debug.Print("DER em " & Der & ". DRD na DER.")
		End If
		.Output "35" & ChrW$(13) 'Despacho

		Debug.Print("Prisma: Escolhendo motivo de indeferimento...")
		I = 0
		If Resultado = "b36NaoEnquadraA3Decreto" Then
			NumRepeticoes = 5
		Elseif Resultado = "b36SemSequela" Then
			NumRepeticoes = 10
		Elseif Resultado = "b36NaoComparecePM" Then
			NumRepeticoes = 11
		Elseif Resultado = "b36RecebeAA" Then
			NumRepeticoes = 0
			InformarAcumulacao = True
		Elseif Resultado = "b36RecebeBenInac" Then
			NumRepeticoes = 0
			InformarAcumulacao = True
		Else
			Debug.Print("Erro: Tipo de despacho nao reconhecido.")
			Exit Sub
		End If

		While I < NumRepeticoes
			.Output "2"
			I = I + 1
		Wend
		Sleep(100)
		.Output "*" & ChrW$(13) 'Marca o motivo de indeferimento
		.Output ChrW$(13) 'Dados OK

		'Aguarda pergunta do resumo
		While Not TextoNaTela(1, 22, "Deseja imprimir o RESUMO")
			Sleep(2000)
		Wend
		'Debug.Print("Nao imprimir resumo.")
		.Output "N" 'Nao Imprimir Resumo
		Sleep(200)

		if InformarAcumulacao Then
			.Output BeneficioInacumulavel & ChrW$(13) 'BEN Anterior
			.Output DIBInacumulavel & ChrW$(13) 'DIB BEN Anterior
			Sleep(1000)
			.Output ChrW$(13)
		End If

		'Debug.Print("Nao imprimir comunicado de decisao.")
		.Output "N" 'Nao Imprimir Comunicado de Decisao
		Sleep(200)
		'Debug.Print("Confirmar formatacao.")
		.Output "S" & ChrW$(13) 'Confirmar formatacao

		'Aguarda formatacao
		Debug.Print("Prisma: Aguarda formatacao...")
		While Not TextoNaTela(1, 22, "Deseja imprimir o Resultado ? (S/N)")
			Sleep(2000)
		Wend

		'Debug.Print("Nao imprimir resultado.")
		.Output "N" & ChrW$(13) 'Nao imprimir resultado

		Debug.Print("Prisma: Aguarda transmissao...")
		While TextoNaTela(1, 21, "TRANSMITINDO, Por Favor, aguarde")
			Sleep(2000)
			If TextoNaTela(1, 22, "Beneficio ainda nao retornou.") Then
				.Output ChrW$(13) 'Tecle Enter
				.Output "S"
			End If
		Wend
		While Not TextoNaTela(1, 21, "Beneficio Processado")
			Sleep(2000)
			If TextoNaTela(1, 22, "Beneficio ainda nao retornou.") Then
				.Output ChrW$(13) 'Tecle Enter
				.Output "S" & ChrW$(13) 'Deseja continuar aguardando? SIM
			End If
		Wend
		.Output ChrW$(13) 'Finaliza

		While Not TextoNaTela(13, 3, "      ")
			Sleep(1000)
		Wend
		Debug.Print("Prisma: Finalizando...")
	End With
End Sub

Function Prisma_EsperaPorStatusOK()
	Prisma_EsperaPorStatusOK =  TextoNaTela(1, 21, "OK <ENTER>")
End Function

'Processa a habilitacao de um beneficio
Public Sub Prisma_HabilitarBeneficio()
	Dim DerColetada, BenColetado As String
	Dim ManterLoopSub As Boolean
	Dim Texto As String

	ManterLoopSub = True
	With ActiveSession
		.SetSelection 0, 0, 0, 0
		.InputMode = 0

		Debug.Print("Prisma: Ir para Tela de dados iniciais...")
		.Output ChrW$(13) 'Gerar Novo NB
		Sleep(250)
		.Output "H" & ChrW$(13) 'DER hoje
		.Output Especie & ChrW$(13) 'Especie
		.Output "0" & ChrW$(13) 'Tipo Normal
		.Output "T" & ChrW$(13) 'Requerente Titular
		.Output "N" & ChrW$(13) 'Acordos Inter. Nao
		.Output "9" & ChrW$(13) 'Atividade Irrelevante
		.Output "0" & ChrW$(13) 'Filiacao Desempregado
		.Output Nit & ChrW$(13) 'NIT
		.Output ChrW$(13) 'Sim
		Sleep(1000)

		'Quadro de msg
		'If TextoNaTela(19, 11, "migrados   CNIS  na  OPCAO  18  da") Then
			'.Output ChrW$(13) 'Sim
		'End If

		'Pergunta Comunicar com o CNIS novamente?
		If TextoNaTela(1, 22, "Houve alteracao nos dados do CNIS apos esta data ?") Then
            Debug.Print("Prisma: Pergunta exibida: Houve altera��o dos dados no CNIS? -> SIM")
			.Output "S" & ChrW$(13) 'Sim
		End If
		Sleep(250)

		'Aguarda comunicar com o CNIS
        Debug.Print("Prisma: Aguardando comunica��o com CNIS...")
		While TextoNaTela(1, 22, "Capturando e tratando dados vindos do CNIS")
			Sleep(3000)
		Wend
		Sleep(1000)

		'Aguardando comunicacao SUB...
		While ManterLoopSub
			If TextoNaTela(1, 22, "Nao encontrou benef�cio.") Then
                Debug.Print("Prisma: Mensagem exibida: N�o encontrou benef�cios")
				.Output ChrW$(13) 'Sim
				ManterLoopSub = False
				Sleep(1000)
			End If

			If TextoNaTela(17, 11, "Confirma os dados do segurado") Then
				Debug.Print("Prisma: Pergunta exibida: Confirma Dados? -> SIM")
				.Output "S" & ChrW$(13) 'Confirma segurado
				Sleep(500)
				ManterLoopSub = False
			End If
			Sleep(1000)
		Wend

		'Caso apareca a tela de homonimos
		If TextoNaTela(23, 10, "Existem Homonimos") Then
            Debug.Print("Prisma: Mensagem exibida: Existe homonimos")
			.Output "N" & ChrW$(13) 'Nao enviar para impressora
			.Output ChrW$(13) 'Fim de Pesquisa
			Sleep(1000)

			While TextoNaTela(2, 24, "Fim de Pesquisa !! Tecle <ENTER>")
				.Output ChrW$(13) 'Fim de Pesquisa
				Sleep(1000)
			Wend
		End If

		Debug.Print("Prisma: Ir para tela de habilitacao...")
		While Not TextoNaTela(57, 19, "PROT.TRAB.")
			Sleep(500)
		Wend
		
		If TextoNaTela(21, 1, "Segurado/titular com data de obito") Then
			Debug.Print("Prisma: Mensagem exibida: Titular com data de obito")
			.Output "S" & ChrW$(13) 'Confirma habilitacao
		End If
		.Output "25" 'Campo Protocolo GET
		.Output Protocolo & ChrW$(13) 'Num Protocolo
		While Not TextoNaTela(1, 22, "DIB e DIP serao recalculadas")
			Sleep(1000)
		Wend
		.Output ChrW$(13) 'Msg DER alerada, DIB e DIP serao recalculadas
		.Output "26" 'Campo Protocolo GET Trab.
		.Output Protocolo & ChrW$(13) 'Num Protocolo
		While Not TextoNaTela(17, 21, "Tela Anterior, ou Modificar")
			Sleep(500)
		Wend
		.Output ChrW$(13) 'Prox Tela
		Sleep(250)
		If TextoNaTela(1, 22, "Os campos do documento de IDENTIDADE estao incompletos.") Then
			Debug.Print("Prisma: ensagem exibida: Doc RG incompletos.")
			.Output ChrW$(13)
		End If
		If TextoNaTela(1, 22, "Os campos da C.T.P.S. estao incompletos.") Then
			Debug.Print("Prisma: Mensagem exibida: CTPS incompleta")
			.Output ChrW$(13)
		End If
	
		'Espera pelo NB
		Debug.Print("Aguardando geracao de NB...")
		While Not TextoNaTela(1, 21, "Anote o numero do BENEFICIO")
			Sleep(1000)
		Wend
		BenColetado = .GetText(42, 21, 13, 0)
		.Output ChrW$(13) 'Depois de mostrar o NB
        Prisma_SetNumero(BenColetado)
		Debug.Print("Prisma: NB gerado. " & BenColetado)

		'Espera pelo OL
		Debug.Print("Debug: Aguarda tela OL Mantenedor.")

		While Not TextoNaTela(1, 22, "Confirma OL Mantenedor")
			Sleep(1000)
		Wend
        Debug.Print("Prisma: Ir para tela DER/OL...")
		Debug.Print("Debug: Confirmando OLM SIM...")
		.Output "S" & ChrW$(13) 'Confirma OLM
		Sleep(250)
		Debug.Print("Ex Combatente NAO...")
		.Output "N" & ChrW$(13) 'Ex combatente Nao
		Sleep(500)


		If TextoNaTela(2, 21, "Nome ou Sobrenome nao pode ser abreviado.") Then
			Debug.Print("Mensagem exibida: Nome ou Sobrenome nao pode ser abreviado.")
			.Output "S" & ChrW$(13)
		End If
		If TextoNaTela(2, 21, "Confirma Nome: IG.") Then
			Debug.Print("Mensagem exibida: Nome IGNORADO sem sobrenome.")
			.Output "S" & ChrW$(13)
		End If

		Debug.Print("Debug: Confirmando...")
        .Output ChrW$(13) 'Confirma
		Sleep(250)
        DerColetada = .GetText(62, 3, 10, 0)
        Debug.Print("Prisma: DER migrada. " & DerColetada)
		.Output DerColetada & ChrW$(13) 'DIB na DER
		.Output ChrW$(13)
		Sleep(250)
		If TextoNaTela(1, 22, "Favor digitar o Nome da Mae") Then
			Debug.Print("Erro: Nao possui nome da mae.")
			ErroProcessamento = True
			Exit Sub
		End If

		While Not TextoNaTela(1, 21, "O Segurado ja' e' Aposentado")
			Sleep(500)

		Wend
		.Output "N" 'Nao e aposentado
		Sleep(500)
		If TextoNaTela(1, 21, "Esta' em gozo de beneficio") Then
			.Output "N" & ChrW$(13)
		End If

		'While Not TextoNaTela(1, 21, "Esta' em gozo de beneficio")
		'	Sleep(500)
		'Wend
		'.Output "N" & ChrW$(13) 'Nao esta em gozo de ben

		'Tela de Ben Anterior
		'Debug.Print("Aguardando Tela de Ben Anterior...")
		'While Not TextoNaTela(31, 1, "BENEFICIO ANTERIOR")
		'	Sleep(500)
		'Wend
		'.Output "/"
		'.Output "/" & ChrW$(13) 'Sai da ben anterior

		'Tela de Tratamento
		Debug.Print("Prisma: Ir para tela de Tratamento para Pagamento...")
		While Not TextoNaTela(5, 6, "TRATAMENTO.....")
			Sleep(500)
		Wend
		.Output "/" & ChrW$(13) 'Sai da tela de tratamento

		.InputMode = 0
	End With
End Sub

Sub Prisma_LancarPM(NB As String, Protocolo As String)
	Dim Arquivo As Integer
	Dim NomeArquivo As String
	Dim Did As String
	Dim Dii As String
	Dim HouveAcidente As String
	Dim DataAcidente As String
	Dim DeferirB94 As String
	Dim SequelaEnquadra As String
	Dim DataMarcacao As String
	Dim Conclusao As String
	Dim Cid As String
	Dim CodigoPerito As String
	Dim DataConclusao As String
	Dim Processando As Boolean
	Dim Texto As String

	Debug.Print("Abrindo arquivo de PM...")
	NomeArquivo	= "C:\Dev\uip\arquivosentrada\" & Protocolo & " - pmparalancar.txt"
	Arquivo = FreeFile
	If FileExists(NomeArquivo) Then
		Open NomeArquivo For Input As #Arquivo
		Line Input #Arquivo,Texto$
		Did = Trim(Texto)
		Line Input #Arquivo,Texto$
		Line Input #Arquivo,Texto$
		Dii = Trim(Texto)
		Line Input #Arquivo,Texto$
		Line Input #Arquivo,Texto$
		HouveAcidente = Trim(Texto)
		Line Input #Arquivo,Texto$
		Line Input #Arquivo,Texto$
		DataAcidente = Trim(Texto)
		Line Input #Arquivo,Texto$
		Line Input #Arquivo,Texto$
		DeferirB94 = Trim(Texto)
		Line Input #Arquivo,Texto$
		Line Input #Arquivo,Texto$
		SequelaEnquadra = Trim(Texto)
		Line Input #Arquivo,Texto$
		Line Input #Arquivo,Texto$
		DataMarcacao = Trim(Texto)
		Line Input #Arquivo,Texto$
		Line Input #Arquivo,Texto$
		Conclusao = Trim(Texto)
		Line Input #Arquivo,Texto$
		Line Input #Arquivo,Texto$
		Cid = Trim(Texto)
		Line Input #Arquivo,Texto$
		Line Input #Arquivo,Texto$
		CodigoPerito = Trim(Texto)
		Line Input #Arquivo,Texto$
		Line Input #Arquivo,Texto$
		DataConclusao = Trim(Texto)
		Close #Arquivo
	Else
		ErroProcessamento = True
		Exit Sub
	End If

	Debug.Print("DID: " & Did)
	Debug.Print("DII: " & Dii)
	Debug.Print("HouveAcidente: " & HouveAcidente)
	Debug.Print("DataAcidente: " & DataAcidente)
	Debug.Print("DeferirB94: " & DeferirB94)
	Debug.Print("SequelaEnquadra: " & SequelaEnquadra)
	Debug.Print("DataMarcacao: " & DataMarcacao)
	Debug.Print("Conclusao: " & Conclusao)
	Debug.Print("CID: " & Cid)
	Debug.Print("CodigoPerito: " & CodigoPerito)
	Debug.Print("DataConclusao: " & DataConclusao)

	With ActiveSession
		.SetSelection 0, 0, 0, 0
		.InputMode = 0

		Debug.Print("Prisma: Abrir beneficio...")
		.Output NB & ChrW$(13) 'Digita o NB

		'Aguarda os campos de PM - Tela 01
		While Not TextoNaTela(7, 7, "D.I.D")
			Sleep(1000)
		Wend
		Debug.Print("Prisma: Informar dados basicos da PM...")
		.Output Did & ChrW$(13)
		'Sleep(1000)
		.Output Dii & ChrW$(13)
		'Sleep(1000)
		.Output "N" & ChrW$(13) 'Nexo Tecnico
		'Sleep(1000)
		.Output "848505" & ChrW$(13) 'Profissao
		'Sleep(1000)
		.Output "50" & ChrW$(13) 'Perc. Reducao
		'Sleep(100)
		.Output HouveAcidente & ChrW$(13) 'Acidente?
		'Sleep(1000)
		.Output DataAcidente & ChrW$(13)
		'Sleep(100)
		.Output DeferirB94 & ChrW$(13) 'Acidente Trabalho?
		'Sleep(100)
		.Output SequelaEnquadra & ChrW$(13) 'Sequela
		'Sleep(100)

		.Output ChrW$(13) 'Mudar de Tela

		'Aguarda os campos do exame - Tela 02
		While Not TextoNaTela(5, 7, "ORDEM DO EXAME")
			Sleep(1000)
		Wend
		Debug.Print("Prisma: Informar dados do exame...")
		.Output DataMarcacao & ChrW$(13)
		'Sleep(100)
		.Output "4" & ChrW$(13) 'Conclusao
		'Sleep(100)
		.Output "888888" & ChrW$(13) 'Data Limite
		'Sleep(100)
		.Output "N" & ChrW$(13) 'Acrescimo
		'Sleep(100)
		.Output Cid & ChrW$(13)
		'Sleep 100
		.Output ChrW$(13) 'CID Secundario
		'Sleep(100)
		.Output "0" & ChrW$(13) 'Codigo da Fase
		'Sleep(100)
		.Output "1" & ChrW$(13) 'Local do Exame
		'Sleep(100)
		.Output "N" & ChrW$(13) 'Exame Requisitado
		'Sleep(100)
		.Output "N" & ChrW$(13) 'Diligencia
		'Sleep(100)
		.Output ChrW$(13) 'Codigo do Perito
		.Output CodigoPerito & ChrW$(13)
		Sleep(100)
		.Output DataConclusao & ChrW$(13)
		'Sleep(100)
		.Output ChrW$(13) 'Dados OK
		Debug.Print("Prisma: Responder perguntas...")

		'Aguarda a pergunta de Impressao da Comunicacao
		While Not TextoNaTela(1, 21, "Deseja imprimir a Comunicacao de Decisao")
			Sleep(1000)
		Wend
		.Output "S" & ChrW$(13)
		.Output ChrW$(13) 'Carta de deferimento nao sera impressa

		Processando = True
		Debug.Print("Prisma: Aguardando processamento...")
		While Processando
			Sleep(1000)
			While TextoNaTela(1, 21, "Formatando")
				Sleep(1000)
			Wend
			If TextoNaTela(1, 22, "Beneficio ainda nao retornou. <TECLE ENTER>") Then
				.Output ChrW$(13)
				Sleep(1000)
			End If
			If TextoNaTela(1, 22, "Deseja continuar aguardando resultado") Then
				.Output "S" & ChrW$(13)
				Sleep(1000)
			End If
			While TextoNaTela(1, 21, "Aguarde")
				Sleep(1000)
			Wend
			If TextoNaTela(1, 22, "Escolha a opcao") Then
				Processando = False
			End If
		Wend
		.Output "/" & ChrW$(13) 'Sair

		Debug.Print("Prisma: Finalizando...")
		While Not TextoNaTela(3, 13, "   ")
			Sleep(1000)
		Wend
	End With
End Sub

Public Function Prisma_GetNumero() As String
	Prisma_GetNumero = Numero
End Function

Public Function Prisma_HouveErroProcessamento() As Boolean
	Prisma_HouveErroProcessamento = ErroProcessamento
End Function

Public Sub Prisma_SetAcumulacao(DIB As String, Numero As String)
	BeneficioInacumulavel = Numero
	DIBInacumulavel = DIB
End Sub

Public Sub Prisma_SetEspecie(NovaEspecie As Integer)
    Especie = NovaEspecie
End Sub

Public Sub Prisma_SetNit(NovoNit As String)
    Nit = NovoNit
End Sub

Public Sub Prisma_SetNumero(NovoNumero As String)
    Numero = NovoNumero
End Sub

Public Sub Prisma_SetProtocolo(NovoProtocolo As String)
    Protocolo = NovoProtocolo
End Sub
