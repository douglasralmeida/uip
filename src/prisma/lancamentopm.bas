'LANCAMENTOPM.BAS
'#Uses "prisma.cls"
'#Uses "arquivoentrada.cls"
'#Uses "arquivosaida.cls"
'#Uses "utils.bas"

'Lancamento PM Automatico
'UIP v.1.0

Dim ProcessamentoComErro As Boolean

Function Processar(ItemEntrada As String) As String
	Dim NB As String
	Dim Protocolo As String
	Dim Resultado As String
	
	'Extrai as variaveis da entrada
	Variaveis = Split(ItemEntrada, " ")
	NB = RemoverCaracteresInvalidos(Variaveis(1))
	Protocolo = Variaveis(0)

	'Realiza o processamento
	Debug.Print("")
	Debug.Print("Tarefa " & Protocolo)

	Prisma_LancarPM(NB, Protocolo)

	Processar = Protocolo & " 1"
	Sleep(250)

	Debug.Print("Tarefa " & Protocolo & " processada.")
End Function

Sub Main()
	Dim I As Integer
	Dim Item As String
	Dim Entrada() As String

	LocalArquivoEntrada = "C:\Dev\uip\arquivosentrada\tarefas_lancarpm.txt"
	LocalArquivoSaida = "C:\Dev\uip\arquivosentrada\pm_lancadas.txt"
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
