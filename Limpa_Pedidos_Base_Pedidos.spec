# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file para Limpeza de Duplicados - BASE_PEDIDOS
Garante que todas as dependências sejam incluídas no executável final
"""

a = Analysis(
    ['start_app.py'],
    pathex=[],
    binaries=[],
    datas=[('app.py', '.')],
    hiddenimports=[
        'streamlit',
        'pandas',
        'openpyxl',
        'altair',
        '_distutils_hack'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'sklearn',
        'tensorflow',
        'torch'
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Limpa_Pedidos_Base_Pedidos',
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
