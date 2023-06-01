'UTILS.BAS
'Automação do Prisma
'UIP v.1.0

Sub ExibirErro(Msg As String)
	MsgBox(Msg, vbCritical Or vbOkOnly, "Erro")
End Sub

Function RemoverCaracteresInvalidos(Texto As String) As String
  Dim TextoSaida As String

  For I = 1 To Len(Texto)
    c = Mid(Texto, I, 1) 'Seleciona o caractere na posicao i
    If (c >= "0" And c <= "9") Or (c >= "A" And c <= "Z") Or (c = " ") Then
      TextoSaida = TextoSaida & c 'adiciona o caractere na saida
    End If
  Next

  RemoverCaracteresInvalidos = TextoSaida
End Function

Function TextoNaTela(X As Integer, Y As Integer, Texto As String) As Boolean
	Dim Tam As Integer
	Dim TextoObtido As String

	Tam = Len(Texto)
	TextoObtido = ActiveSession.GetText(X, Y, Tam, 0)
	'Debug.Print("'" & TextoObtido & "'")
	If Texto = TextoObtido Then
		TextoNaTela = True
	Else
		TextoNaTela = False
	End If
End Function