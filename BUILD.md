# Building Sombra Desktop

## Windows Build

### Prerequisites

1. **Python 3.10+** - https://python.org/downloads/
2. **Git** - https://git-scm.com/download/win
3. **Inno Setup 6** (for installer) - https://jrsoftware.org/isdl.php

### Quick Build

```cmd
git clone https://github.com/Danny-sth/sombra-desktop.git
cd sombra-desktop
build_windows.bat
```

This will:
- Create virtual environment
- Install dependencies
- Build executable to `dist/Sombra/`

### Create Installer

After build completes:

```cmd
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

Output: `installer_output/SombraSetup-0.1.0.exe`

### Manual Build

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
pyinstaller --clean --noconfirm sombra.spec
```

## Linux Build

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pyinstaller --clean --noconfirm sombra.spec
```

Output: `dist/Sombra/Sombra`

### Create AppImage (optional)

```bash
# Install appimagetool
wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage

# Create AppDir structure
mkdir -p AppDir/usr/bin AppDir/usr/share/applications AppDir/usr/share/icons/hicolor/256x256/apps
cp -r dist/Sombra/* AppDir/usr/bin/
cp sombra.desktop AppDir/usr/share/applications/
cp resources/icons/sombra-256.png AppDir/usr/share/icons/hicolor/256x256/apps/sombra.png
cp resources/icons/sombra-256.png AppDir/sombra.png
ln -sf usr/bin/Sombra AppDir/AppRun

# Build AppImage
./appimagetool-x86_64.AppImage AppDir Sombra-0.1.0-x86_64.AppImage
```

## macOS Build

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pyinstaller --clean --noconfirm sombra.spec
```

Output: `dist/Sombra.app`

Note: For proper macOS distribution, you'll need to:
1. Create .icns icon file
2. Sign the app with Apple Developer certificate
3. Notarize for Gatekeeper

## Build Size

The build includes PyTorch which makes it large (~1.5-2 GB). To reduce:

1. Use CPU-only torch: `pip install torch --index-url https://download.pytorch.org/whl/cpu`
2. Or exclude torch and disable Silero VAD

## Configuration

After installation, edit `.env` file:

```env
SOMBRA_API_URL=http://90.156.230.49:8080
SOMBRA_SESSION_ID=owner
STT_URL=http://100.87.46.63:5000/transcribe
THEME=dark
GLOBAL_HOTKEY=ctrl+shift+s
PICOVOICE_ACCESS_KEY=your-key-here
```

Get Picovoice key at: https://console.picovoice.ai/
