Attribute VB_Name = "ArquivoSaida"
Attribute VB_GlobalNameSpace = True
Attribute VB_Creatable = True
Attribute VB_Exposed = True
Attribute VB_PredeclareID = True
Attribute VB_Description = "ArquivoSaida"

'ARQUIVOSAIDA.CLS
'UIP v.1.0

'File|New Module|Class Module
'Edit|Properties|Name=ArquivoSaida

Option Explicit

'Local do Arquivo
Dim NomeArquivo As String

Dim Arquivo As Integer

Private Sub Class_Initialize()
    Debug.Print("Inicializando Classe ArquivoEntrada...")
End Sub

Private Sub Class_Terminate()
    Debug.Print("Finalizando Classe ArquivoEntrada...")
End Sub

'Salva o arquivo de saída
Sub ArquivoSaida_Salvar(Saida As String)
	Arquivo = FreeFile
	Open NomeArquivo For Append As #Arquivo
	Print #Arquivo,vbCrLf & Saida;
	Close #Arquivo
End Sub

'Altera o nome do arquivo a ser salvo
Public Sub ArquivoSaida_SetNomeArquivo(NovoNome As String)
	NomeArquivo = NovoNome
End Sub