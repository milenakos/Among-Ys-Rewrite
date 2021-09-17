pyinstaller --onefile server.py
move dist\main.exe .
ren "main.exe" "Server.exe"
del main.spec
rmdir build /S /Q
rmdir __pycache__ /S /Q
rmdir dist
pause