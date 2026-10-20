# PyInstaller spec for the Windows release. Build with:
#   py -m PyInstaller --clean --noconfirm nugget_y1_tool.spec
import os
from pathlib import Path

if os.name != "nt":
    raise SystemExit("This spec builds the Windows release only.")

ROOT = Path(SPECPATH)
datas = []


def add_tree(source, destination, exclude_images=False):
    for path in source.rglob("*"):
        if not path.is_file():
            continue
        if exclude_images and path.suffix.lower() == ".img":
            continue
        relative = path.relative_to(source)
        target = Path(destination) / relative.parent
        datas.append((str(path), str(target)))


add_tree(ROOT / "web", "web")
add_tree(ROOT / "c", "c")
add_tree(ROOT / "screenshots", "screenshots")
add_tree(ROOT / "spflash", "spflash", exclude_images=True)
datas.extend((str(ROOT / name), ".") for name in ("bg.png", "cursor.png", "favi.png", "1.png", "2.png"))

a = Analysis(
    [str(ROOT / "installer.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="nugget-y1-tool",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="nugget-y1-tool",
)
