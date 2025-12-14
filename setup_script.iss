; Script para Inno Setup - SynapseCargo (v3.2)
; Enterprise Edition - NSLabs

#define MyAppName "SynapseCargo"
#define MyAppVersion "3.3"
#define MyAppPublisher "NSLabs"
#define MyAppExeName "SynapseCargo.exe"

[Setup]
; AppId único (No lo cambies para que detecte que es una actualización del mismo programa)
AppId={{A8F93290-7521-4E68-9635-1234567890AB}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
; Carpeta de salida
OutputDir=Output
OutputBaseFilename=Setup_SynapseCargo_v{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
SetupIconFile=app_icon.ico

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; 1. EL EJECUTABLE PRINCIPAL (Buscamos en la carpeta SynapseCargo)
Source: "dist\SynapseCargo\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; 2. TODOS LOS RECURSOS
Source: "dist\SynapseCargo\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; 3. LIBRERÍAS DE MICROSOFT (VC Redist)
Source: "vc_redist.x64.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; 1. Instalar librerías silenciosamente
Filename: "{tmp}\vc_redist.x64.exe"; Parameters: "/install /quiet /norestart"; StatusMsg: "Instalando componentes del sistema..."; Flags: waituntilterminated

; 2. Ejecutar programa al terminar
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent