; ============================================================
; Installer do Controle de Obras (Inno Setup 6)
; Gerado a partir do build PyInstaller (dist\ControleDeObras)
;
; IMPORTANTE: os dados do usuario ficam em %APPDATA%\ControleDeObras
; (fora da pasta de instalacao). Atualizar/reinstalar NAO apaga cadastros.
; ============================================================

#define MyAppName "Controle de Obras"
#define MyAppVersion "1.0.1"
#define MyAppPublisher "CASSIO REIS TECH"
#define MyAppExeName "ControleDeObras.exe"

[Setup]
AppId={{7A3E0D5C-2F1B-4C6E-9A0B-8D5E2F1C3A4B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Controle de Obras
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=installer
OutputBaseFilename=Setup_ControleDeObras_{#MyAppVersion}
SetupIconFile=assets\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=6.1
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=Instalador do Controle de Obras
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}

; Portugues Brasileiro
[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\ControleDeObras\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[Registry]
; Registra instalacao para futuras deteccoes
Root: HKCU; Subkey: "Software\ControleDeObras"; ValueType: string; ValueName: "InstallDir"; ValueData: "{app}"; Flags: uninsdeletekey

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    MsgBox('Atencao: os seus dados (obras, lancamentos, etc) ficam em %APPDATA%\ControleDeObras e NAO serao apagados ao reinstalar ou atualizar.', mbInformation, MB_OK);
  end;
end;
