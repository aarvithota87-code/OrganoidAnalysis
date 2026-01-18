# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['desktop_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('methods_explanation.html', '.'),
        ('organoid_analysis.py', '.'),
        ('organoid_analysis_watershed.py', '.'),
        ('organoid_analysis_hough.py', '.'),
        ('organoid_analysis_morphology.py', '.'),
        ('organoid_analysis_commercial_sims.py', '.'),
        ('organoid_analysis_stardist.py', '.'),
        ('organoid_analysis_unet.py', '.'),
        ('organoid_analysis_cellpose.py', '.'),
    ],
    hiddenimports=[
        'flask',
        'cv2',
        'numpy',
        'werkzeug',
        'jinja2',
        'organoid_analysis',
        'organoid_analysis_watershed',
        'organoid_analysis_hough',
        'organoid_analysis_morphology',
        'organoid_analysis_commercial_sims',
        'organoid_analysis_stardist',
        'organoid_analysis_unet',
        'organoid_analysis_cellpose',
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

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='OrganoidAnalysis',
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
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='OrganoidAnalysis',
)

