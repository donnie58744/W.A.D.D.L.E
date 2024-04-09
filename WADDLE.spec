# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('Updater.exe','.'),('res/duckWithVRHeadset.png', 'res'),('setup/config.json', 'setup'),('res/loadingScreen.png', 'res'),('res/checkmarkIcon.png', 'res'),('libs/Config.py', 'libs'),('libs/SystemChanger.py', 'libs'),('libs/UiFunctions.py', 'libs'),('libs/RazerCortex.py', 'libs'),('libs/files/OpenVR/openvr_api.dll', 'libs/files/OpenVR/'),('libs/files/OpenVR/openvr_mod.cfg', 'libs/files/OpenVR/'),('ui/runningProcesses.ui', 'ui'),('ui/settingsMenu.ui', 'ui'),('ui/settings/displaySettings.ui', 'ui/settings'),('ui/settings/powerPlanSettings.ui', 'ui/settings'), ('ui/settings/oculusSettings.ui', 'ui/settings')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='WADDLE',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='C:/Users/leath/OneDrive/Documents/GitHub/WADDLE/res/duckWithVRHeadset.png'
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='WADDLE',
)
