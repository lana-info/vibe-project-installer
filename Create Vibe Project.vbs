Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
root = fso.GetParentFolderName(WScript.ScriptFullName)
scriptPath = root & "\scripts\create_vibe_project_gui.py"

shell.Run "pythonw.exe """ & scriptPath & """", 1, False
