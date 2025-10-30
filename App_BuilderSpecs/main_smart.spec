# -*- mode: python ; coding: utf-8 -*-
import sys ; sys.setrecursionlimit(sys.getrecursionlimit() * 5)

# Smart optimization - keep essential functionality, remove only confirmed unnecessary components
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('public', 'public'), 
        ('Documentation', 'Documentation')
    ],
    hiddenimports=[
        'serial.tools.list_ports',
        'PySide6.QtCore',
        'PySide6.QtWidgets', 
        'PySide6.QtGui',
        'PySide6.QtWebEngineWidgets'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Only exclude PyQt5 (definitely not needed)
        'PyQt5',
        'PyQt5.QtCore', 
        'PyQt5.QtWidgets',
        'PyQt5.QtGui',
        
        # Only exclude very heavy ML/AI libraries that dashboard definitely doesn't need
        'torch',
        'torchvision',
        'tensorflow',
        'sklearn',
        'astropy',  # Astronomy library
        'geopandas',  # Geographic data
        'shapely',   # Geographic shapes
        'folium',    # Maps
        'bokeh',     # Alternative plotting (keep matplotlib)
        'altair',    # Alternative plotting
        'sympy',     # Symbolic math
        'numba',     # JIT compiler
        'llvmlite',  # LLVM bindings
        'dask',      # Parallel computing
        
        # Exclude development/documentation tools
        'IPython',
        'jupyter',
        'notebook',
        'sphinx',
        'docutils',
        'nbformat',
        'nbconvert',
        'mistune',
        
        # Exclude only the heaviest Qt3D modules (definitely not needed)
        'PySide6.Qt3DCore',
        'PySide6.Qt3DRender',
        'PySide6.Qt3DInput',
        'PySide6.Qt3DLogic',
        'PySide6.Qt3DAnimation',
        'PySide6.Qt3DExtras',
        
        # Exclude heavy visualization modules if not essential
        'PySide6.QtQuick3D',
        'PySide6.QtDataVisualization',
        
        # Exclude test frameworks
        'pytest',
        'unittest',
        'doctest',
        
        # Exclude web frameworks (definitely not needed)
        'flask',
        'django',
        'fastapi',
        
        # Exclude very large libraries that dashboard probably doesn't need
        'cv2',       # Computer vision (very large)
        'opencv',    # Computer vision
        'skimage',   # Image processing (very large)
        'imageio',   # Image I/O
        'pywt',      # Wavelets
        
        # Keep essential libraries like numpy, pyqtgraph, matplotlib (needed for dashboard)
        # Keep pandas (might be used for data handling)
        # Keep scipy (might be used by pyqtgraph)
    ],
    noarchive=False,
    optimize=1,  # Light optimization
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Dashboard-Smart',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,    # Don't strip to avoid breaking functionality
    upx=True,       # Keep UPX compression
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='public/ign_logo_wht.ico',
)