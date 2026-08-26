#define MyAppName "Controle de Obras"
#define MyAppVersion "1.0.1"
#define MyAppPublisher "CASSIO REIS TECH"
#define MyAppExeName "ControleDeObras.exe"

[Setup]
AppId={{7A3C9E41-2B6D-4F5A-9E7B-2C0D1E7F5A10}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL=https://cassioreistech.com
DefaultDirName={autopf}\ControleDeObras
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=installer
OutputBaseFilename=ControleDeObras-Setup-{#MyAppVersion}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\{#MyAppExeName}
SetupIconFile=assets\icon.ico
SetupLogging=yes
; Forcar executor como administrador (instala em Program Files)
PrivilegesRequired=admin
; Nao criar dados em Program Files: o app ja grava em %APPDATA%

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar atalho no Desktop"; GroupDescription: "Atalhos:"; Flags: checkedonce

[Files]
; Copiar toda a pasta dist\ControleDeObras preservando estrutura
Source: "dist\ControleDeObras\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Executar {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Remover arquivos de dados do usuario se existirem (opcional, comentado para nao apagar dados do cliente)
; Name: "{app}"; Type: filesandordirs
