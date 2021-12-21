%localappdata%/Programs/Python/Python38-32/Scripts/pyinstaller.exe -w -F -i="img/icon.png" --add-data "img;img" --add-data "moves;moves" --add-data "arlrdbd.ttf;." --main.py
move dist\main.exe .
ren "main.exe" "AmongYsRewrite.exe"
