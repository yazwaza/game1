from setuptools import setup
import os

APP = ['valentine-game.py']
DATA_FILES = ['block.png', 'intro_background.png', 'roses.mp4', 'MoveOnlyRegular.ttf']
OPTIONS = {
    'argv_emulation': True,
    'packages': ['pygame', 'cv2', 'numpy'],
    'iconfile': 'icon.icns',  # Optional: Add a custom icon
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
