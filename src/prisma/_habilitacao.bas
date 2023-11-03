'UIP.BAS
'UIP v.1.0

Public Declare Function PlaySound Lib "winmm.dll" Alias "PlaySoundA" _
    (ByVal lpszName As String,                                       _
     ByVal hModule As Long,                                          _
     ByVal dwFlags As Long) As Long

Private Const SND_ASYNC As Long       = &H1

Private Const SND_FILENAME As Long    = &H20000

Private ProcessamentoComErro As Boolean

Private NB As String

Private DirArquivosEntrada As String

Private QuantidadeItens As Integer

Private ItensProcessados As Integer

Private Entrada() As String

Sub Depurar(Lista() As String)
	Dim Variaveis() As String

	Variaveis = Split(Lista(0), " ")
	Debug.Print(Variaveis(0))
End Sub


Sub InserirDERnoPrisma(DER As String)
	Debug.Print("Alterando DER para " & DER & "...")
	With ActiveSession
		.SetSelection 0, 0, 0, 0
		.InputMode = 0
		.Output "1" & ChrW$(13) 'Vai para Pre Habilitacao
		Sleep(250)
		.Output ChrW$(13) 'Tela 2
		Sleep(750)
		.Output ChrW$(13) 'Tela 3
		Sleep(750)
		If TextoNaTela(1, 22, "Os campos do documento de IDENTIDADE estao incompletos.") Then
			Debug.Print("Msg Doc RG incompletos.")
			.Output ChrW$(13)
		End If
		If TextoNaTela(1, 22, "Os campos da C.T.P.S. estao incompletos.") Then
			Debug.Print("Msg CTPS incompleta")
			.Output ChrW$(13)
		End If
		Sleep(250)
		.Output "2" & ChrW$(13) 'Campo DER
		.Output DER & ChrW$(13) 'Informa a DER
		Sleep(250)
		.Output ChrW$(13) 'Campo DIB
		Sleep(750)
		If TextoNaTela(2, 21, "Nome ou Sobrenome nao pode ser abreviado.") Then
			Debug.Print("Msg Nome ou Sobrenome nao pode ser abreviado.")
			.Output "S" & ChrW$(13)
		End If
		.Output DER & ChrW$(13) 'Informa a DIB como DER
		Sleep(250)
		If TextoNaTela(2, 21, "Confirma Nome: IG.") Then
			Debug.Print("Msg Confirmar nome IGNORADO.")
			.Output "S" & ChrW$(13)
		End If		
		.Output "N" 'Informa nao eh aposentado
		Sleep(2500)
		.InputMode = 0
	End With
End Sub

Sub ProcessarDER(DER As String)
	Dim Data As String
	Dim DataInicio As Date
	Dim DataEntrada As Date
	Dim NumDias As Integer
	Dim Especie As Integer

	Dim Dia As Integer
	Dim Mes As Integer
	Dim Ano As Integer

	DataEntrada = CDate(DER)
	Data = ActiveSession.GetText(67, 3, 10, 0)
	DataInicio = CDate(Data)
	NumDias = DateDiff("d", DataEntrada, DataInicio)
	Debug.Print("Processando DER...")
	While NumDias > 180
		DataInicio = DateAdd("d", -180, DataInicio)
		NumDias = DateDiff("d", DataEntrada, DataInicio)
		Dia = DatePart("d", DataInicio)
		Mes = DatePart("m", DataInicio)
		Ano = DatePart("yyyy", DataInicio)
		Data = CStr(Dia) + "/" + CStr(Mes) + "/" + CStr(Ano)
		InserirDERnoPrisma(Data)
	Wend
	InserirDERnoPrisma(DER)
End Sub

Sub DespacharBeneficio(NB As String, Resultado As String)
	Dim I As Integer
	Dim NumRepeticoes As Integer

	With ActiveSession
		.SetSelection 0, 0, 0, 0
		.InputMode = 0

		Debug.Print("Abrindo o benefï¿½cio...")
		.Output NB & ChrW$(13) 'Entrar no BEN

		Debug.Print("Ir para Tela Despacho...")
		.Output "16" & ChrW$(13) 'Ir para Tela de Despacho
		While Not TextoNaTela(29, 1, "DESPACHO DA CONCESSAO")
			Sleep(1000)
		Wend
		'Sleep(1000)
		If TextoNaTela(24, 7, "          ") Then
			.Output ChrW$(13) 'DRD
			Debug.Print("DRD em branco.")
		End If
		.Output "35" & ChrW$(13) 'Despacho

		Debug.Print("Escolhendo motivo...")
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
		Debug.Print("Nao imprimir resumo.")
		.Output "N" 'Nao Imprimir Resumo
		Sleep(200)
		Debug.Print("Nao imprimir comunicado de decisao.")
		.Output "N" 'Nao Imprimir Comunicado de Decisao
		Sleep(200)
		Debug.Print("Confirmar formatacao.")
		.Output "S" & ChrW$(13) 'Confirmar formatacao

		'Aguarda formatacao
		Debug.Print("Aguarda formatacao...")
		While Not TextoNaTela(1, 22, "Deseja imprimir o Resultado ? (S/N)")
			Sleep(2000)
		Wend

		Debug.Print("Nao imprimir resultado.")
		.Output "N" & ChrW$(13) 'Nao imprimir resultado

		Debug.Print("Aguarda transmissao...")
		While TextoNaTela(1, 21, "TRANSMITINDO, Por Favor, aguarde")
			Sleep(2000)
		Wend
		While Not TextoNaTela(1, 21, "Beneficio Processado")
			Sleep(2000)
		Wend
		.Output ChrW$(13) 'Finaliza

		While Not TextoNaTela(13, 3, "      ")
			Sleep(1000)
		Wend
	End With
End Sub

Sub HabilitarBeneficio(Protocolo As String, Nit As String)
	Dim SeMantemLoopSub As Boolean
	Dim Texto As String

	SeMantemLoopSub = True
	ProcessamentoComErro = False

	With ActiveSession
		.SetSelection 0, 0, 0, 0
		.InputMode = 0

		Debug.Print("Ir para Tela de dados iniciais...")

		.Output ChrW$(13) 'Gerar Novo NB
		Sleep(250)
		.Output "H" & ChrW$(13) 'DER hoje
		.Output "36" & ChrW$(13) 'Especie 36
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
			.Output "S" & ChrW$(13) 'Sim
		End If
		Sleep(250)

		'Aguarda comunicar com o CNIS
		Debug.Print("Aguardando captura e tratamento dos dados do CNIS...")
		While TextoNaTela(1, 22, "Capturando e tratando dados vindos do CNIS")
			Sleep(3000)
		Wend
		Sleep(1000)

		'Aguardando comunicaï¿½ï¿½o SUB...
		While SeMantemLoopSub
			If TextoNaTela(1, 22, "Nao encontrou beneficios.") Then
				Debug.Print("Mensagem exibida: Nao encontrou beneficios")
				.Output ChrW$(13) 'Sim
				SeMantemLoopSub = False
				Sleep(1000)
			End If

			If TextoNaTela(17, 11, "Confirma os dados do segurado") Then
				Debug.Print("Pergunta exibida: Confirma dados -> SIM")
				.Output "S" & ChrW$(13) 'Confirma segurado
				Sleep(500)
				SeMantemLoopSub = False
			End If
			Sleep(1000)
		Wend

		'Caso apareï¿½a a tela de homonimos
		If TextoNaTela(23, 10, "Existem Homonimos") Then
			Debug.Print("Tela exibida: Existe Homonimos")
			.Output "N" & ChrW$(13) 'Nao enviar para impressora
			.Output ChrW$(13) 'Fim de Pesquisa
			Sleep(1000)

			While TextoNaTela(2, 24, "Fim de Pesquisa !! Tecle <ENTER>")
				.Output ChrW$(13) 'Fim de Pesquisa
				Sleep(1000)
			Wend
		End If

		Debug.Print("Ira para Tela informar protocolo...")
		While Not TextoNaTela(57, 19, "PROT.GET..")
			Sleep(500)
		Wend
		.Output "25" 'Campo Protocolo GET
		.Output Protocolo & ChrW$(13) 'Protocolo GET
		While Not TextoNaTela(17, 21, "Tela Anterior, ou Modificar")
			Sleep(500)
		Wend
		.Output ChrW$(13) 'Prox Tela

		Sleep(250)
		If TextoNaTela(1, 22, "Os campos do documento de IDENTIDADE estao incompletos.") Then
			Debug.Print("Mensagem exibida: Doc RG incompletos.")
			.Output ChrW$(13)
		End If
		If TextoNaTela(1, 22, "Os campos da C.T.P.S. estao incompletos.") Then
			Debug.Print("Mensagem exibida: CTPS incompleta")
			.Output ChrW$(13)
		End If
	
		'Espera pelo NB
		Debug.Print("Aguardando geraï¿½ï¿½o de NB...")
		While Not TextoNaTela(1, 21, "Anote o numero do BENEFICIO")
			Sleep(1000)
		Wend
		NB = .GetText(42, 21, 13, 0)
		.Output ChrW$(13) 'Depois de mostrar o NB
		Debug.Print("NB gerado: " & NB)

		'Espera pelo OL
		Debug.Print("Ir para tela DER/OL...")
		While Not TextoNaTela(1, 22, "Confirma OL Mantenedor")
			Sleep(1000)
		Wend
		.Output "S" & ChrW$(13) 'Confirma OLM
		Sleep(250)
		.Output "N" & ChrW$(13) 'Ex combatente Nao
		Sleep(500)
		.Output ChrW$(13) 'Confirma
		Sleep(250)
		.Output "S" & ChrW$(13) 'DER hoje
		
		.Output ChrW$(13)
		Sleep(750)

		If TextoNaTela(2, 21, "Nome ou Sobrenome nao pode ser abreviado.") Then
			Debug.Print("Mensagem exibida: Nome ou Sobrenome nao pode ser abreviado.")
			.Output "S" & ChrW$(13)
		End If
		If TextoNaTela(2, 21, "Confirma Nome: IG.") Then
			Debug.Print("Mensagem exibida: Nome IGNORADO sem sobrenome.")
			.Output "S" & ChrW$(13)
		End If
		Debug.Print("Informando DIB na DER")
		.Output "H" & ChrW$(13) 'DIB na DER
		Sleep(250)
		If TextoNaTela(1, 22, "Favor digitar o Nome da Mae") Then
			Debug.Print("Erro: Nao possui nome da mae.")
			ProcessamentoComErro = True
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
		Debug.Print("Aguardando Tela de Ben Anterior...")
		While Not TextoNaTela(31, 1, "BENEFICIO ANTERIOR")
			Sleep(500)
		Wend
		.Output "/"
		.Output "/" & ChrW$(13) 'Sai da ben anterior

		'Tela de Tratamento
		Debug.Print("Aguardando Tela de Tratamento...")
		While Not TextoNaTela(5, 6, "TRATAMENTO.....")
			Sleep(500)
		Wend
		.Output "/" & ChrW$(13) 'Sai da tela de tratamento

		.InputMode = 0
	End With
End Sub

Sub LancarPericia(Protocolo As String, NB As String, Pericia() As String)
	With ActiveSession
		.SetSelection 0, 0, 0, 0
		.InputMode = 0

		'Abre PM do NB
		.Output NB
		.Output ChrW$(13)
		Sleep(1000)

		Debug.Print("TELA 1...")
		'DID e DII
		.Output Pericia(0)
		.Output ChrW$(13)
		.Output Pericia(1)
		.Output ChrW$(13)

		'Nexo
		.Output ChrW$(13)

		'Cod Profissao
		.Output "848505"
		.Output ChrW$(13)
	
		'Percentual
		.Output "50"
		.Output ChrW$(13)

		'Acidente
		.Output Pericia(2)
		.Output ChrW$(13)

		'Dt Acidente
		.Output Pericia(3)
		.Output ChrW$(13)

		'AT
		.Output Pericia(4)
		.Output ChrW$(13)
		'Sequela
		.Output Pericia(5)
		.Output ChrW$(13)

		'Ir para prox tela
		.Output ChrW$(13)
		Sleep(1000)
		Debug.Print("TELA 2...")

		'Dt Marcacao
		.Output Pericia(6)
		.Output ChrW$(13)

		'Conclusao
		.Output Pericia(7)
		.Output ChrW$(13)

		'Data Limite
		.Output "888888"		'LI
		.Output ChrW$(13)

		'Acrescimo 25%
		.Output "N"			'Nao
		.Output ChrW$(13)

		'CID
		.Output Pericia(8)
		.Output ChrW$(13)
		.Output ChrW$(13)	'CID Secundario vazio

		'Codigo Fase
		.Output "0"  		'Normal
		.Output ChrW$(13)

		'Local Exame
		.Output "1"			'Instituto
		.Output ChrW$(13)

		'Exame Requisitado
		.Output "N"
		.Output ChrW$(13)

		'Diligencia
		.Output "N"
		.Output ChrW$(13)

		'Codigo Perito
		.Output ChrW$(13)	'vazio

		'Codigo Per Quadro
		.Output Pericia(9)
		.Output ChrW$(13)

		'Dt Exame
		.Output Pericia(10)
		.Output ChrW$(13)

		'Ir para Prox Tela
		.Output ChrW$(13)
		.Output "N" 		'Sem impressao
		.Output ChrW$(13)
		.Output ChrW$(13)

		Debug.Print("Aguardando BEN ainda nao retornou...")
		While TextoNaTela(1, 21, "Aguarde")
			Sleep(2000)
		Wend
		Sleep(2000)
		If TextoNaTela(0, 23, "Beneficio ainda nao retornou") Then
			.Output ChrW$(13)
			.Output "S"
			.Output ChrW$(13)
		End If

		Sleep(2000)
		While TextoNaTela(2, 21, "Escolha a opcao")
			Sleep(2000)
		Wend
		Debug.Print("Aguardando por Escolha a opcao...")

		'Escolher Impressora ou Terminal
		.Output "/" 		'Finaliza
		.Output ChrW$(13)
		Debug.Print("Finalizando...")
	End With
End Sub

Sub ProcessarBeneficio(Dados As String)
	Dim DER As String
	Dim Nit As String
	Dim Protocolo As String
	Dim Variaveis() As String

	Variaveis = Split(Dados, " ")
	DER = Variaveis(2)
	Nit = RemoverCaracteresInvalidos(Variaveis(1))
	Protocolo = Variaveis(0)

	Debug.Print("PROGRAMA 'HABILITAR BENEFï¿½CIO'")
	Debug.Print("Inicializando processamento da tarefa " & Protocolo & "...")
	HabilitarBeneficio(Protocolo, Nit)

	SalvarDados("ben_habilitados", Protocolo & " " & NB)
	Sleep(250)
	If Not ProcessamentoComErro Then
		ProcessarDER(DER)
	End If

	Debug.Print("Finalizando...")
	ItensProcessados = ItensProcessados + 1
	ActiveSession.Output "O" & ChrW$(13)
	While Not TextoNaTela(13, 3, "      ")
		Sleep(1000)
	Wend	

	Debug.Print("Tarefa " & Protocolo & " processada.")
End Sub

Sub ProcessarDespacho(Dados As String)
	Dim NB As String
	Dim Protocolo As String
	Dim Resultado As String
	
	Variaveis = Split(Dados, " ")
	NB = RemoverCaracteresInvalidos(Variaveis(1))
	Protocolo = Variaveis(0)
	Resultado = Variaveis(2)

	Debug.Print("PROGRAMA 'DESPACHAR BENEFICIO'")
	Debug.Print("Inicializando processamento da tarefa " & Protocolo & "...")

	DespacharBeneficio(NB, Resultado)
	TemResumo = "0"

	SalvarDados("ben_despachados", Protocolo & " 1 " & TemResumo & " " & Resultado & " 1")
	Sleep(250)

	Debug.Print("Finalizando...")
	ItensProcessados = ItensProcessados + 1
	'ActiveSession.Output "O" & ChrW$(13)
	'While Not TextoNaTela(13, 3, "      ")
	'	Sleep(1000)
	'Wend	

	Debug.Print("Tarefa " & Protocolo & " processada.")
End Sub

Sub ProcessarPericia(Dados As String)
	Dim Protocolo As String
	Dim NB As String
	Dim Pericia() As String

	Variaveis = Split(Dados, " ")
	NB = RemoverCaracteresInvalidos(Variaveis(1))
	Protocolo = Variaveis(0)
	Pericia = LerPericia(Protocolo)

	Debug.Print("Processando tarefa " & Protocolo & "...")
	LancarPericia(Protocolo, NB, Pericia)
	Debug.Print("Pericia lancada")
	SalvarDados("pm_lancadas", Protocolo & " 1")
End Sub

Sub AlterarEntrada(NomeArquivo As String)
	Dim I As Integer
	Dim NomeArquivoCompleto As String
	Dim Num As Integer
	Dim Item As String

	Arquivo = FreeFile
	NomeArquivoCompleto = DirArquivosEntrada & NomeArquivo & ".txt"
	Num = QuantidadeItens - ItensProcessados
	If FileExists(NomeArquivoCompleto) Then
		Open NomeArquivoCompleto For Output As #Arquivo
		Print #Arquivo,Str(Num);
		For I = ItensProcessados To UBound(Entrada)
			Item = Trim(Entrada(I))
			Print #Arquivo,vbCr & Item;
		Next I
		Close #Arquivo
	Else
		ExibirErro("Arquivo texto com lote de tarefas para habilitar benefício não encontrado.")
	End If
End Sub

Sub LerEntrada(NomeEntrada As String)
	Dim I As Integer
	Dim NomeArquivo As String

	Arquivo = FreeFile
	NomeArquivo = DirArquivosEntrada & NomeEntrada & ".txt"
	If FileExists(NomeArquivo) Then
		Open NomeArquivo For Input As #Arquivo
		Line Input #Arquivo,L$
		QuantidadeItens = CInt(L$)
		If QuantidadeItens = 0 Then
			ExibirErro("O arquivo de entrada nï¿½o possui registros para processamento.")
			Exit Sub
		End If
		ReDim Entrada(QuantidadeItens) As String
		I = 1
		Do
			Line Input #Arquivo,L$
			Entrada(I-1) = L$
			I = I + 1
		Loop Until I > QuantidadeItens
		Close #Arquivo
	Else
		ExibirErro("Arquivo texto com lote de tarefas para habilitar benefï¿½cio nï¿½o encontrado.")
	End If
End Sub

Function LerPericia(Protocolo As String) As String()
	Dim I As Integer
	Dim NomeArquivo As String
	Dim NumLinhas As Integer
	Dim Resultado(11) As String

	Arquivo = FreeFile
	NomeArquivo = DirArquivosEntrada & Protocolo & " - pmparalancar.txt"
	NumLinhas = 12
	If FileExists(NomeArquivo) Then
		Open NomeArquivo For Input As #Arquivo
		I = 0
		Do
			Line Input #Arquivo,L$
			Resultado(I) = L$
			I = I + 1
		Loop Until I = NumLinhas
		Close #Arquivo
	Else
		ExibirErro("Arquivo de perï¿½cia da tarefa " & Protocolo & " nï¿½o foi localizado.")
	End If

	LerPericia = Resultado
End Function

Sub Main()
	Dim I As Integer
	Dim Modo As Integer
	Dim Modos(3) As String
	Dim Item As String

	Debug.Print("Iniciando processamento...")
	ItensProcessados = 0
	Modo = 0
	Modos(0) = "tarefas_habilitar"
	Modos(1) = "tarefas_lancarpm"
	Modos(2) = "tarefas_indeferir"
	DirArquivosEntrada = "C:\Dev\uip\arquivosentrada\"
	LerEntrada(Modos(Modo))
	For I = 0 To UBound(Entrada)
	'I = 0
		Item = Trim(Entrada(I))
		Select Case Modo
			Case 0
				ProcessarBeneficio(Item)
				AlterarEntrada(Modos(Modo))
				PlaySound "C:\Dev\uip\midia\MusicaSucesso.wav", 0, SND_FILENAME Or SND_ASYNC
				If ProcessamentoComErro Then
					Exit Sub
				End If
			Case 1
				ProcessarPericia(Item)
			Case 2
				ProcessarDespacho(Item)
		End Select
	Next I
End Sub
