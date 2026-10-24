@echo off
call .venv\Scripts\activate
pip install pyinstaller
pyinstaller --noconsole --onefile --name PdfPageEditor main.py
echo Xong: dist\PdfPageEditor.exe
