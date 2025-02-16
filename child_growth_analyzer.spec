# -*- mode: python ; coding: utf-8 -*-
import PyInstaller.config
PyInstaller.config.CONF['distpath'] = "dist"

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('app_icon.ico', '.'),
        ('who_data/hfa-boys-perc-who2007-exp.csv', 'who_data'),
        ('who_data/hfa-girls-perc-who2007-exp.csv', 'who_data')
    ],
    hiddenimports=[
        'matplotlib.backends.backend_tkagg',
        'pandas',
        'numpy',
        'scipy.interpolate'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ChildGrowthAnalyzer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='file_version_info.txt',
    icon='app_icon.ico'
) 