# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

# Get the project root directory
project_root = Path(os.getcwd())
sys.path.insert(0, str(project_root))

# Data files to include
datas = []

# Include template files
template_dir = project_root / 'dvge' / 'templates'
if template_dir.exists():
    for template_file in template_dir.glob('*.json'):
        datas.append((str(template_file), 'dvge/templates'))

# Include any other data files
data_dirs = [
    'dvge/constants',
    'dvge/templates',
]

for data_dir in data_dirs:
    data_path = project_root / data_dir
    if data_path.exists():
        for file_path in data_path.rglob('*'):
            if file_path.is_file() and not file_path.name.startswith('.'):
                relative_path = file_path.relative_to(project_root)
                dest_dir = str(relative_path.parent)
                datas.append((str(file_path), dest_dir))

# Hidden imports (modules that PyInstaller might miss)
hiddenimports = [
    'customtkinter',
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    'tkinter',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'tkinter.simpledialog',
    'tkinter.colorchooser',
    'tkinter.ttk',
    'json',
    'os',
    'sys',
    'threading',
    'queue',
    'datetime',
    'markdown',
    'reportlab',
    'reportlab.pdfgen',
    'reportlab.lib',
    'reportlab.lib.pagesizes',
    'reportlab.platypus',
    'base64',
    'uuid',
    'pathlib',
    'typing',
    'dataclasses',
    'abc',
    'functools',
    'itertools',
    'collections',
    'webbrowser',
    'tempfile',
    'shutil',
    'traceback',
    'subprocess',
    'platform',
]

a = Analysis(
    ['main.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'pytest',
        'black',
        'flake8',
        'mypy',
        'pre-commit',
        'isort',
        'coverage',
        'tkinter.test',
        'test',
        'tests',
        'unittest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DialogueVenture',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for windowed app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon file path if you have one
    version_info={
        'version': '1.0.0',
        'description': 'Dialogue Venture Game Engine - Create Interactive Stories',
        'company': 'Dice Verce',
        'product': 'Dialogue Venture Game Engine',
        'copyright': 'Copyright (c) 2024',
        'file_description': 'Visual Node-Based Story Editor',
    }
)