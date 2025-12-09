; Script MEJORADO para Inno Setup - Label Generator
#define MyAppName "Label Generator"
#define MyAppVersion "2.0"
#define MyAppPublisher "Néstor Segura"
#define MyAppExeName "LabelGenerator.exe"

[Setup]
AppId={{A8F93290-7521-4E68-9635-1234567890AB}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=Output
OutputBaseFilename=Setup_LabelGenerator_v{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; 1. EL PROGRAMA (Tu carpeta dist)
Source: "dist\LabelGenerator\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\LabelGenerator\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; 2. EL MOTOR DE MICROSOFT (¡Lo nuevo!)
; Copiamos el instalador de C++ a la carpeta temporal de la instalación
Source: "vc_redist.x64.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; 1. INSTALAR EL MOTOR DE MICROSOFT (Silenciosamente)
; /install /quiet /norestart -> Lo instala sin preguntar y sin reiniciar
Filename: "{tmp}\vc_redist.x64.exe"; Parameters: "/install /quiet /norestart"; StatusMsg: "Instalando componentes del sistema necesarios..."; Flags: waituntilterminated

; 2. EJECUTAR TU PROGRAMA
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent