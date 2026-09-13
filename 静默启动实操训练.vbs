Option Explicit

Dim fso, shell, baseDir, pyw, launcher, cmd, env
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

baseDir = fso.GetParentFolderName(WScript.ScriptFullName)
pyw = baseDir & "\.venv\Scripts\pythonw.exe"
launcher = baseDir & "\tray_launcher.py"

If Not fso.FileExists(pyw) Then
    MsgBox "未找到虚拟环境，请先运行 install_env.bat 或 安装环境.bat。", vbExclamation, "AI Trainer"
    WScript.Quit 1
End If

If Not fso.FileExists(launcher) Then
    MsgBox "未找到 tray_launcher.py，请先执行 git pull。", vbExclamation, "AI Trainer"
    WScript.Quit 1
End If

Set env = shell.Environment("PROCESS")
env("JUPYTERLAB_SETTINGS_DIR") = baseDir & "\jupyter_settings"

shell.CurrentDirectory = baseDir
cmd = Chr(34) & pyw & Chr(34) & " " & Chr(34) & launcher & Chr(34)
shell.Run cmd, 0, False
