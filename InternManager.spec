# -*- mode: python ; coding: utf-8 -*-
import sys
import os

block_cipher = None

PROJ_BASE = os.path.abspath(os.getcwd())

# Define os caminhos relativos à base
resources_path = os.path.join(PROJ_BASE, 'resources')
icon_path = os.path.join(PROJ_BASE, 'additionals', 'favicon.ico')

if not os.path.exists(resources_path):
    print(f"ERRO: Pasta resources não encontrada em {resources_path}")
    sys.exit(1)
# --------------------------------------

a = Analysis(
    [os.path.join('src', 'main.py')],
    pathex=[PROJ_BASE],
    binaries=[],
    datas=[
        (resources_path, 'resources')
    ],
    hiddenimports=[],
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
    [],
    exclude_binaries=True,
    name='InternManager',
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
    icon=['resources\\app_icon.ico'],
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='InternManager',
)

if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='InternManager.app',
        bundle_identifier='com.biomedico.internmanager'
    )