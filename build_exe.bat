@echo off
call .venv\Scripts\activate
pip install pyinstaller
pyinstaller --noconsole --onefile --exclude-module pymupdf.layout --exclude-module pymupdf4llm --exclude-module onnxruntime --name PdfPageEditor main.py
echo Xong: dist\PdfPageEditor.exe
