@echo off
rem Tạo dist\PdfPageEditor_Setup_<phiên bản>.exe (cài đặt + gỡ cài đặt). Cần Inno Setup 6.
setlocal
cd /d "%~dp0"
set ISCC=
for %%P in ("%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" "%ProgramFiles%\Inno Setup 6\ISCC.exe" "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe") do if exist %%P set ISCC=%%~P
if "%ISCC%"=="" (
  echo Chua co Inno Setup 6. Cai bang: winget install JRSoftware.InnoSetup
  exit /b 1
)
call .venv\Scripts\activate
python installer\make_icon.py || exit /b 1
call "%~dp0build_exe.bat" || exit /b 1
"%ISCC%" installer\PdfPageEditor.iss || exit /b 1
echo Xong: dist\PdfPageEditor_Setup_*.exe
