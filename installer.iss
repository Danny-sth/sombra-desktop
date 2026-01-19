; Sombra Desktop - Inno Setup Installer Script
; Download Inno Setup: https://jrsoftware.org/isdl.php

#define MyAppName "Sombra"
#define MyAppVersion "0.2.6"
#define MyAppPublisher "Sombra"
#define MyAppURL "https://github.com/Danny-sth/sombra-desktop"
#define MyAppExeName "Sombra.exe"

[Setup]
; App info
AppId={{B8E7F9A1-5C3D-4E2F-8A1B-9C0D2E3F4A5B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Directories
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=installer_output
OutputBaseFilename=SombraSetup-{#MyAppVersion}

; Compression
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes

; Appearance
SetupIconFile=resources\icons\sombra.ico
WizardStyle=modern
WizardSizePercent=100

; Privileges
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; Misc
DisableProgramGroupPage=yes
DisableWelcomePage=no
AllowNoIcons=yes
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startupicon"; Description: "Start Sombra with Windows"; GroupDescription: "Startup:"; Flags: unchecked

[Files]
; Main application files
Source: "dist\Sombra\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Icon for shortcuts
Source: "resources\icons\sombra.ico"; DestDir: "{app}"; Flags: ignoreversion

; Config template
Source: ".env.example"; DestDir: "{app}"; DestName: ".env.example"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\sombra.ico"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\sombra.ico"; Tasks: desktopicon
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\sombra.ico"; Tasks: startupicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// Create default .env if not exists
procedure CurStepChanged(CurStep: TSetupStep);
var
  EnvFile: String;
  EnvExample: String;
begin
  if CurStep = ssPostInstall then
  begin
    EnvFile := ExpandConstant('{app}\.env');
    EnvExample := ExpandConstant('{app}\.env.example');

    if not FileExists(EnvFile) then
    begin
      if FileExists(EnvExample) then
      begin
        FileCopy(EnvExample, EnvFile, False);
      end;
    end;
  end;
end;

[UninstallDelete]
Type: files; Name: "{app}\.env"
Type: dirifempty; Name: "{app}"
