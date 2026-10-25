; Trình cài đặt PDF Page Editor (Inno Setup 6). Gỡ cài đặt (unins000.exe) do Inno tự tạo và đăng ký
; vào "Apps & features" của Windows; có thêm lối tắt "Gỡ cài đặt" trong Start Menu.
#define AppName "PDF Page Editor"
#define AppExe "PdfPageEditor.exe"
#ifndef AppVersion
  #define AppVersion "1.0.0"
#endif

[Setup]
AppId={{6B1D2E54-7C0A-4E5B-9F43-2A8D5C7E1B90}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=PdfPageEditor
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesInstallIn64BitMode=x64compatible
SetupIconFile=app.ico
UninstallDisplayIcon={app}\{#AppExe}
UninstallDisplayName={#AppName}
OutputDir=..\dist
OutputBaseFilename=PdfPageEditor_Setup_{#AppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\{#AppExe}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExe}"
Name: "{autoprograms}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExe}"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Registry]
; Xóa cài đặt ngôn ngữ app (QSettings) khi gỡ cài đặt.
Root: HKCU; Subkey: "Software\PdfPageEditor"; Flags: uninsdeletekey
