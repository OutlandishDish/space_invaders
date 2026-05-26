# Space Invaders (Python + Pygame)

A small Space Invaders clone built with Pygame and packaged for Windows using a custom `spaceicon`.

## Run Locally

```powershell
c:/Users/Rabbi/PythonProjects/space_invaders/.venv/Scripts/python.exe -m pip install -r requirements.txt
c:/Users/Rabbi/PythonProjects/space_invaders/.venv/Scripts/python.exe src/main.py
```

Controls:
- Left/Right or A/D: Move
- Space or Up: Shoot
- Enter (menu): Start game
- P: Pause/Resume
- R (game over): Restart
- Esc (paused/game over): Back to menu

## Build Windows EXE with Icon

```powershell
./build.ps1
```

This generates:
- `assets/spaceicon.ico`
- `dist/SpaceInvaders.exe`

## GitHub Sync

```powershell
git init
git add .
git commit -m "Initial Space Invaders game"
git branch -M main
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
```

If your remote already exists:

```powershell
git remote set-url origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
```
