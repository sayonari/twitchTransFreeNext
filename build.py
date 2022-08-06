import platform

import PyInstaller.__main__

OS = platform.system()

if OS == 'Windows':
    PyInstaller.__main__.run([
        'twitchTransFN.py',
        '--clean',
        '--onefile',
        '--hidden-import=pywin32',
        '--runtime-tmpdir="."',
        '--icon=icon.ico',
        '--exclude-module=config',
        '--name=twitchTransFN.exe'
    ])
elif OS == 'Darwin':
    PyInstaller.__main__.run([
        'twitchTransFN.py',
        '--clean',
        '--onefile',
        '--runtime-tmpdir="."',
        '--icon=icon.ico',
        '--exclude-module=config',
        '--name=twitchTransFN.command'
    ])
elif OS == 'Linux':
    PyInstaller.__main__.run([
        'twitchTransFN.py',
        '--clean',
        '--onefile',
        '--runtime-tmpdir="."',
        '--icon=icon.ico',
        '--exclude-module=config',
        '--name=twitchTransFN'
    ])
