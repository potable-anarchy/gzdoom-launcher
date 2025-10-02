"""
py2app setup script for GZDoom Launcher
"""

from setuptools import setup

APP = ['doom-launcher-gui.py']
DATA_FILES = [
    ('', ['LICENSE', 'README.md']),
]
OPTIONS = {
    'argv_emulation': False,
    'packages': ['PySide6'],
    'iconfile': 'doom-launcher.icns',
    'strip': True,  # Strip debug symbols
    'optimize': 2,  # Python optimization level
    'excludes': [
        'numpy', 'scipy', 'matplotlib', 'pandas',  # Exclude common but unused packages
        'test', 'unittest', 'distutils', 'setuptools',  # Exclude test/build tools
    ],
    'plist': {
        'CFBundleName': 'GZDoom Launcher',
        'CFBundleDisplayName': 'GZDoom Launcher',
        'CFBundleIdentifier': 'com.gzdoom.launcher',
        'CFBundleVersion': '1.1.0',
        'CFBundleShortVersionString': '1.1.0',
        'LSMinimumSystemVersion': '12.0',
    },
}

setup(
    name='GZDoom Launcher',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
