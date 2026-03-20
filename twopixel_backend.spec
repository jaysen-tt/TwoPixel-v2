# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# 1. Fix missing data dir error
if not os.path.exists('data'):
    os.makedirs('data', exist_ok=True)

# 2. Bundle full Python env + toolchains
hidden_imports = [
    'ast', 'asyncio', 'logging', 'json', 'yaml', 'aiohttp', 
    'astrbot', 'astrbot.core', 'astrbot.dashboard'
]

if hasattr(sys, 'stdlib_module_names'):
    # Add standard library modules (excluding internal ones starting with '_')
    stdlib_modules = [m for m in sys.stdlib_module_names if not m.startswith('_')]
    hidden_imports.extend(stdlib_modules)

for pkg in ['pip', 'setuptools', 'wheel']:
    try:
        hidden_imports.extend(collect_submodules(pkg))
    except Exception:
        pass

datas = [('data', 'data')]

for pkg in ['pip', 'setuptools', 'wheel']:
    try:
        datas.extend(collect_data_files(pkg))
    except Exception:
        pass

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='twopixel-backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)