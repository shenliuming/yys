# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['D:\\workspace\\gamehelper\\yys\\YYS_GameHelper\\tasks\\anniversary\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('D:\\workspace\\gamehelper\\yys\\YYS_GameHelper\\config.yaml', '.'), ('D:\\workspace\\gamehelper\\yys\\YYS_GameHelper\\templates', 'templates')],
    hiddenimports=['win32gui', 'win32con', 'win32api', 'pywintypes', 'cv2', 'numpy', 'PIL', 'yaml', 'adbutils'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['torch', 'tensorflow', 'matplotlib', 'scipy', 'pandas', 'sklearn', 'IPython', 'jupyter', 'notebook', 'tkinter'],
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
    name='YYS_Anniversary',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
