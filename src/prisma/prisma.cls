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
	Dim I As Integer
	Dim NumRepeticoes As Integer

	With ActiveSession
		.SetSelection 0, 0, 0, 0
		.InputMode = 0

		Debug.Print("Prisma: Abrindo o benefício...")
		.Output NB & ChrW$(13) 'Entrar no BEN

		Debug.Print("Prisma: Ir para Tela Despacho...")
		.Output "16" & ChrW$(13) 'Ir para Tela de Despacho
		While Not TextoNaTela(29, 1, "DESPACHO DA CONCESSAO")
			Sleep(1000)
		Wend
		If TextoNaTela(24, 7, "          ") Then
			.Output ChrW$(13) 'DRD
			Debug.Print("DRD em branco.")
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
            Debug.Print("Prisma: Pergunta exibida: Houve alteração dos dados no CNIS? -> SIM")
			.Output "S" & ChrW$(13) 'Sim
		End If
		Sleep(250)

		'Aguarda comunicar com o CNIS
        Debug.Print("Prisma: Aguardando comunicaï¿½ï¿½o com CNIS...")
		While TextoNaTela(1, 22, "Capturando e tratando dados vindos do CNIS")
			Sleep(3000)
		Wend
		Sleep(1000)

		'Aguardando comunicacao SUB...
		While ManterLoopSub
			If TextoNaTela(1, 22, "Nao encontrou benefício.") Then
                Debug.Print("Prisma: Mensagem exibida: Não encontrou benefícios")
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
            Debug.Print("Prisma: Mensagem exibida: Existe homï¿½nimos")
			.Output "N" & ChrW$(13) 'Nao enviar para impressora
			.Output ChrW$(13) 'Fim de Pesquisa
			Sleep(1000)

			While TextoNaTela(2, 24, "Fim de Pesquisa !! Tecle <ENTER>")
				.Output ChrW$(13) 'Fim de Pesquisa
				Sleep(1000)
			Wend
		End If

		Debug.Print("Prisma: Ir para tela de habilitação...")
		While Not TextoNaTela(57, 19, "PROT.GET..")
			Sleep(500)
		Wend
		.Output "25" 'Campo Protocolo GET
		.Output Protocolo & ChrW$(13) 'Protocolo GET
        .Output ChrW$(13) 'Msg DER alerada, DIB e DIP serao recalculadas
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

Public Function Prisma_GetNumero() As String
	Prisma_GetNumero = Numero
End Function

Public Function Prisma_HouveErroProcessamento() As Boolean
	Prisma_HouveErroProcessamento = ErroProcessamento
End Function

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
