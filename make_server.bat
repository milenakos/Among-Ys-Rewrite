pyinstaller --onefile server.py
move dist\server.exe .
del server.spec
rmdir build /S /Q
rmdir __pycache__ /S /Q
rmdir dist
pause