pyinstaller --onefile -w main.py
move dist\main.exe .
ren "main.exe" "AmongYsRewrite.exe"
del main.spec
rmdir build /S /Q
rmdir __pycache__ /S /Q
rmdir dist
pause