Set WshShell = CreateObject("WScript.Shell")
' Obtener la ruta del directorio donde está este script
Set fso = CreateObject("Scripting.FileSystemObject")
scriptPath = fso.GetParentFolderName(WScript.ScriptFullName)

' Cambiar al directorio del proyecto
WshShell.CurrentDirectory = scriptPath

' Ejecutar el script de Python de forma oculta
WshShell.Run "python src\start.py", 0, False

' 0 = ventana oculta
' False = no esperar a que termine
