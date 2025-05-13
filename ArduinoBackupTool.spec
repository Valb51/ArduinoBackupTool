# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\Utilisateur\\Desktop\\ArduinoBackupTool\\v1.1.2\\ArduinoBackupTool\\src\\arduino_backup_tool.py'],
    pathex=[],
    binaries=[('C:\\Users\\Utilisateur\\Desktop\\ArduinoBackupTool\\v1.1.2\\ArduinoBackupTool\\avrdude\\avrdude.exe', '.')],
    datas=[('C:\\Users\\Utilisateur\\Desktop\\ArduinoBackupTool\\v1.1.2\\ArduinoBackupTool\\avrdude\\avrdude.conf', '.'), ('C:\\Users\\Utilisateur\\Desktop\\ArduinoBackupTool\\v1.1.2\\ArduinoBackupTool\\assets\\loader.gif', '.'), ('C:\\Users\\Utilisateur\\Desktop\\ArduinoBackupTool\\v1.1.2\\ArduinoBackupTool\\assets\\app.ico', '.')],
    hiddenimports=['serial.tools.list_ports'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ArduinoBackupTool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:\\Users\\Utilisateur\\Desktop\\ArduinoBackupTool\\v1.1.2\\ArduinoBackupTool\\assets\\app.ico'],
)
