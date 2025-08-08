# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('settings.json', '.'),
        ('docs', 'docs'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'json',
        'os',
        'sys',
        're',
        'pathlib',
        'datetime',
        'threading',
        'time',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pandas', 'openpyxl', 'xlrd', 'numpy', 'scipy', 'matplotlib', 'seaborn', 'plotly', 'bokeh', 'jupyter', 'ipython', 'notebook', 'qtpy', 'pyqt5', 'pyqt6', 'pyside2', 'pyside6', 'wx', 'kivy', 'flask', 'django', 'fastapi', 'sqlalchemy', 'sqlite3', 'mysql', 'postgresql', 'mongodb', 'redis', 'celery', 'dask', 'ray', 'tensorflow', 'pytorch', 'sklearn', 'xgboost', 'lightgbm', 'catboost', 'statsmodels', 'numba', 'cython', 'pyarrow', 'feather', 'parquet', 'hdf5', 'netcdf', 'xarray', 'vaex', 'modin', 'cudf', 'rapids', 'cupy', 'llvmlite', 'llvm'],
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
    name='LOG_Analyzer2',
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
)
