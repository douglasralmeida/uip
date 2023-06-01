Attribute VB_Name = "ArquivoEntrada"
Attribute VB_GlobalNameSpace = True
Attribute VB_Creatable = True
Attribute VB_Exposed = True
Attribute VB_Description = "Classe ArquivoEntrada"

'Module ARQUIVOENTRADA.CLS
'UIP v.1.0

'File|New Module|Class Module
'Edit|Properties|Name=ArquivoEntrada

Option Explicit

Dim Arquivo As Integer

'Local do Arquivo
Dim NomeArquivo As String

'Tamanho da lista de entrada
Dim QuantidadeItens As Integer

Private Sub Class_Initialize()
    Debug.Print("Inicializando Classe ArquivoEntrada...")
End Sub

Private Sub Class_Terminate()
    Debug.Print("Finalizando Classe ArquivoEntrada...")
End Sub

'Carrega um arquivo de entrada
Public Sub ArquivoEntrada_Carregar(Entrada() As String)
	Dim I As Integer
	Dim L As String

	Arquivo = FreeFile
	If FileExists(NomeArquivo) Then
		Open NomeArquivo For Input As #Arquivo
		Line Input #Arquivo,L$
		QuantidadeItens = CInt(L$)
		If QuantidadeItens = 0 Then
			MsgBox("O arquivo de entrada não possui registros para processamento.", vbCritical Or vbOkOnly, "Erro")
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
		MsgBox("O arquivo de entrada para habilitação de benefício não foi encontrado.", vbCritical Or vbOkOnly, "Erro")
	End If
End Sub

Sub ArquivoEntrada_Limpar()
	Arquivo = FreeFile
	Open NomeArquivo For Output As #Arquivo
	Print #Arquivo,"0"
	Close #Arquivo
End Sub

'Remove do arquivo de entrada os itens já processados.
Sub ArquivoEntrada_Alterar(ByRef Entrada() As String, QuantidadeProcessados As Integer)
	Dim I As Integer
	Dim Num As Integer
	Dim Item As String

	ArquivoEntrada_Limpar()
	Arquivo = FreeFile
	Num = QuantidadeItens - QuantidadeProcessados
	Open NomeArquivo For Output As #Arquivo
	Print #Arquivo,Str(Num);
	For I = QuantidadeProcessados To UBound(Entrada)
		Item = Trim(Entrada(I))
		Print #Arquivo,vbCr & Item;
	Next I
	Close #Arquivo
End Sub

'Altera o nome do arquivo a ser lido
Public Sub ArquivoEntrada_SetNomeArquivo(NovoNome As String)
	NomeArquivo = NovoNome
End Sub
