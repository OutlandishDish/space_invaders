$ErrorActionPreference = "Stop"

$python = "c:/Users/Rabbi/PythonProjects/space_invaders/.venv/Scripts/python.exe"

& $python tools/make_spaceicon.py
& $python -m PyInstaller --noconfirm --windowed --onefile --name SpaceInvaders --icon assets/spaceicon.ico src/main.py

Write-Host "Build complete. EXE is in dist/SpaceInvaders.exe"
