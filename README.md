# Nugget Y1 Tool

A small local web app that guides you through installing Nugget on an Innioasis Y1 Type A player. It downloads the current Nugget files from GitHub, flashes the boot image on Windows, and copies the Rockbox files to the player. Local mode lets you supply your own image and archive files.

> **Warning:** Installation replaces the Y1's original software and can malfunction or damage the device. Use this tool only with a supported Y1 Type A and at your own risk. Do not disconnect the player during flashing or file copying.

## Use a packaged release

Download and extract the complete `nugget-y1-tool` folder from the release, then run `nugget-y1-tool.exe`. Keep the extracted folder intact; the executable uses files in its `_internal` directory. The installer opens its interface in your browser and keeps a console window open while it runs.

At startup, the installer copies the bundled SP Flash Tool files to `%LOCALAPPDATA%\Nugget-Y1-Tool` so it can write its runtime configuration there. It also needs an internet connection to download release files; alternatively, use **Local mode** in the app.

## Build on Windows

Use Python 3.8 or newer:

```powershell
py -m pip install --upgrade pyinstaller
py -m PyInstaller --clean --noconfirm nugget_y1_tool.spec
```

The onedir build is created at `dist\nugget-y1-tool`. Distribute the entire folder, preferably as a ZIP, rather than the executable by itself. The spec omits unrelated `.img` files in `spflash/`; the installer supplies the boot image at runtime.

For development, run `py installer.py` from the project directory.

## Credits and license

Nugget and its Y1 installation files are maintained separately; see the links in the app's **Help** menu. This project includes MTKClient source and retains its GPL-3.0 license and upstream notices.
