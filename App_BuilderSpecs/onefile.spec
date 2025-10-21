# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

# Compute paths relative to this spec file so PyInstaller finds the real entry
# When PyInstaller runs a spec, __file__ may not be defined; use cwd instead.
SPEC_DIR = os.getcwd()  # PyInstaller executes the spec with cwd set to the project root
REPO_ROOT = os.path.abspath(os.path.join(SPEC_DIR, '.'))
MAIN_PY = os.path.join(REPO_ROOT, 'main.py')
ICON_PATH = os.path.abspath(os.path.join(REPO_ROOT, 'docs', 'public', 'Glance_nobg_jl.ico'))
    
# Minimal one-file spec for Glance
hiddenimports = [
    'serial.tools.list_ports',
]

# Collect pyqtgraph/numpy if necessary (pyinstaller usually handles)

a = Analysis(
    [MAIN_PY],
    pathex=[REPO_ROOT],
    binaries=[],
    # Build datas list dynamically so we only include files that exist on disk
    datas=(lambda: [
        (os.path.join(REPO_ROOT, 'docs', 'public'), 'docs/public')
    ] + [
        (p, 'docs/public') for p in [
            os.path.join(REPO_ROOT, 'docs', 'public', 'Glance_nobg_jl.png'),
            os.path.join(REPO_ROOT, 'docs', 'public', 'Glance_nobg _jl.png'),
            os.path.join(REPO_ROOT, 'docs', 'public', 'Glance_nobg_jl.svg'),
            os.path.join(REPO_ROOT, 'docs', 'public', 'ign_logo_wht.svg'),
            os.path.join(REPO_ROOT, 'docs', 'public', 'Glance_nobg.png'),
        ] if os.path.exists(p)
    ])(),
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        'PyQt5', 'torch', 'tensorflow', 'cv2', 'skimage', 'jupyter', 'pytest'
    ],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='Glance',
    debug=False,
    strip=False,
    upx=True,
    console=False,
    icon=ICON_PATH
)

# One-file build
coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, strip=False, upx=False, name='Glance')
