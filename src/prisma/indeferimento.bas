'INDEFERIMENTO.BAS
'#Uses "prisma.cls"
'#Uses "arquivoentrada.cls"
'#Uses "arquivosaida.cls"
'#Uses "utils.bas"

'Indeferimento Automatico
'UIP v.1.0

Dim ProcessamentoComErro As Boolean

Function Processar(ItemEntrada As String) As String
	Dim NB As String
	Dim Protocolo As String
	Dim Resultado As String
	
	'Extrai as vari�veis da entrada
	Variaveis = Split(ItemEntrada, " ")
	NB = RemoverCaracteresInvalidos(Variaveis(1))
	Protocolo = Variaveis(0)
	Resultado = Variaveis(2)
	DIB_Anterior = "0"
	NB_Anterior = "0"

	'Realiza o processamento
	Debug.Print("")
	Debug.Print("Tarefa " & Protocolo)

	Prisma_SetAcumulacao(DIB_Anterior, NB_Anterior)
	Prisma_DespacharBeneficio(NB, Resultado)
	If Resultado = "b36NaoComparecePM" Then
		TemResumo = "1"
	ElseIf Resultado = "b36RecebeAA" Then
		TemResumo = "1"
	ElseIf Resultado = "b36RecebeBenInac" Then
		TemResumo = "1"
	Else
		TemResumo = "0"
	End If

	Processar = Protocolo & " 1 " & TemResumo & " " & Resultado & " 1"
	Sleep(250)

	Debug.Print("Tarefa " & Protocolo & " processada.")
End Function

Sub Main()
	Dim I As Integer
	Dim Item As String
	Dim Entrada() As String

	LocalArquivoEntrada = "C:\Dev\uip\arquivosentrada\tarefas_indeferir.txt"
	LocalArquivoSaida = "C:\Dev\uip\arquivosentrada\ben_despachados.txt"
	QuantidadeProcessados = 0

	Debug.Print("Iniciando processamento...")
	ArquivoEntrada_SetNomeArquivo(LocalArquivoEntrada)
	ArquivoSaida_SetNomeArquivo(LocalArquivoSaida)
	ArquivoEntrada_Carregar(Entrada)
	For I = 0 To UBound(Entrada)
		Item = Trim(Entrada(I))
		Saida = Processar(Item)
		If ProcessamentoComErro Then
			Exit Sub
		End If		
		ArquivoSaida_Salvar(Saida)
		ArquivoEntrada_Alterar(Entrada, QuantidadeProcessados)
		'PlaySound "C:\Dev\uip\midia\MusicaSucesso.wav", 0, SND_FILENAME Or SND_ASYNC
		QuantidadeProcessados = QuantidadeProcessados + 1
	Next I
	Debug.Print("Finalizando processamento...")
	Debug.Print("Processados " + CStr(QuantidadeProcessados) + " iten(s).")
End Sub
