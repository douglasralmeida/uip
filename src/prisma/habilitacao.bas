'HABILITACAO.BAS
'#Uses "prisma.cls"
'#Uses "arquivoentrada.cls"
'#Uses "arquivosaida.cls"
'#Uses "utils.bas"

'Habilitacao Automatica
'UIP v.1.0

Dim ProcessamentoComErro As Boolean

Function Processar(ItemEntrada As String) As String
	Dim DER As String 'Não precisa mais de DER
	Dim Beneficio As String
	Dim Nit As String
	Dim Protocolo As String
	Dim Variaveis() As String

	'Extrai as variáveis da entrada
	Variaveis = Split(ItemEntrada, " ")
	DER = Variaveis(2)
	Nit = RemoverCaracteresInvalidos(Variaveis(1))
	Protocolo = Variaveis(0)

	'Realiza o processamento
	Debug.Print("")
	Debug.Print("Tarefa " & Protocolo)
	Prisma_SetEspecie(36)
	Prisma_SetNit(Nit)
	Prisma_SetProtocolo(Protocolo)
	Prisma_HabilitarBeneficio()
	ProcessamentoComErro = Prisma_HouveErroProcessamento()
	Beneficio = Prisma_GetNumero()
	Processar = Protocolo & " " & Beneficio
	Sleep(250)

	'Sai do Prisma
	ActiveSession.Output "O" & ChrW$(13)
	While Not TextoNaTela(13, 3, "      ")
		Sleep(1000)
	Wend
	Debug.Print("Tarefa " & Protocolo & " processada.")
End Function

Sub Main()
	Dim I As Integer
	Dim Item As String
	Dim Entrada() As String

	LocalArquivoEntrada = "C:\Dev\uip\arquivosentrada\tarefas_habilitar.txt"
	LocalArquivoSaida = "C:\Dev\uip\arquivosentrada\ben_habilitados.txt"
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
