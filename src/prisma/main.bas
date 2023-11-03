'MAIN.BAS
'Automação do Prisma
'UIP v.1.0


Sub ProcessarBeneficio(Dados As String)
	Dim DER As String
	Dim Nit As String
	Dim Protocolo As String
	Dim Variaveis() As String

	Variaveis = Split(Dados, " ")
	DER = Variaveis(2)
	Nit = RemoverCaracteresInvalidos(Variaveis(1))
	Protocolo = Variaveis(0)

	Debug.Print("PROGRAMA 'HABILITAR BENEFÍCIO'")
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

Sub Main()

End Sub