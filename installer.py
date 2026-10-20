#!/usr/bin/env python3
"""Nugget Installer: runs a tiny local web server and opens the UI in your browser."""
import ctypes, json, os, re, shutil, subprocess, sys, threading, time, urllib.request, webbrowser, zipfile
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

IS_FROZEN = getattr(sys, "frozen", False)
RESOURCE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
APP_DIR = Path(sys.executable).resolve().parent if IS_FROZEN else RESOURCE_DIR
WEB_DIR = RESOURCE_DIR / "web"
if IS_FROZEN:
    local_app_data = os.environ.get("LOCALAPPDATA")
    USER_DATA_DIR = (Path(local_app_data) if local_app_data else Path.home() / "AppData" / "Local") / "Nugget-Y1-Tool"
else:
    USER_DATA_DIR = APP_DIR
CACHE = USER_DATA_DIR / "downloads"
LOG = USER_DATA_DIR / "installer.log"
SPFLASH_RESOURCE_DIR = RESOURCE_DIR / "spflash"
SPFLASH_DIR = USER_DATA_DIR / "spflash" if IS_FROZEN else APP_DIR / "spflash"
RELEASE_API = "https://api.github.com/repos/norocoral/nugget-y1/releases/latest"
UA = {"User-Agent": "NuggetInstaller/2.0"}

def log(msg):
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%H:%M:%S')} {msg}\n")
    except OSError:
        pass

# ---------------------------------------------------------------- downloads
assets = {"boot": None, "logo": None, "zip": None, "error": None, "progress": 0, "ready": threading.Event()}

def local_build():
    search_dirs = [APP_DIR / "local", APP_DIR / "release", APP_DIR.parent / "hosted_linux_port" / "release"]
    for base in search_dirs:
        if not base.is_dir():
            continue
        b = next((f for f in base.glob("*.img") if "boot" in f.name.lower()), None) or (base / "boot_rockbox.img")
        z = next((f for f in base.glob("*.zip") if "rockbox" in f.name.lower() or "sdcard" in f.name.lower()), None) or (base / "rockbox_sdcard.zip")
        l = next((f for f in base.glob("*.bin") if "logo" in f.name.lower()), None) or (base / "logo.bin")
        if b.exists() and z.exists():
            return b, (l if l.exists() else None), z
    return None, None, None

def fetch(url, dest, size, on_bytes):
    if dest.exists() and dest.stat().st_size == size:
        on_bytes(size)
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r, open(tmp, "wb") as f:
        while chunk := r.read(65536):
            f.write(chunk)
            on_bytes(len(chunk))
    tmp.replace(dest)

def prefetch():
    try:
        with urllib.request.urlopen(urllib.request.Request(RELEASE_API, headers=UA), timeout=10) as r:
            rel = json.load(r)
        files = rel["assets"]
        boot = next(a for a in files if a["name"].endswith(".img"))
        zipa = next(a for a in files if a["name"].endswith(".zip"))
        logo = next((a for a in files if a["name"] == "logo.bin" or a["name"].endswith("logo.bin")), None)
        
        total, done = boot["size"] + zipa["size"], [0]
        if logo:
            total += logo["size"]

        def tick(n):
            done[0] += n
            assets["progress"] = min(100, int(100 * done[0] / total))

        folder = CACHE / rel["tag_name"]
        fetch(boot["browser_download_url"], folder / boot["name"], boot["size"], tick)
        if logo:
            fetch(logo["browser_download_url"], folder / logo["name"], logo["size"], tick)
            assets["logo"] = folder / logo["name"]
        fetch(zipa["browser_download_url"], folder / zipa["name"], zipa["size"], tick)
        assets["boot"], assets["zip"] = folder / boot["name"], folder / zipa["name"]
    except Exception as e:
        log(f"download failed: {e}")
        b, l, z = local_build()
        if b and z:
            assets["boot"], assets["logo"], assets["zip"] = b, l, z
        else:
            assets["error"] = "We couldn't download Nugget. Check your internet connection and try again."
    assets["ready"].set()

def retry_prefetch():
    assets.update(boot=None, logo=None, zip=None, error=None, progress=0)
    assets["ready"].clear()
    threading.Thread(target=prefetch, daemon=True).start()

# ------------------------------------------------------------------- drives
def drives():
    out = []
    if os.name == "nt":
        k = ctypes.windll.kernel32
        mask = k.GetLogicalDrives()
        for i, l in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
            p = f"{l}:\\"
            if mask >> i & 1 and l not in "AB" and k.GetDriveTypeW(p) == 2 and os.path.exists(p):
                buf = ctypes.create_unicode_buffer(261)
                try: k.GetVolumeInformationW(p, buf, 260, None, None, None, None, 0)
                except Exception: pass
                out.append({"path": p, "label": f"{p} {buf.value}".strip()})
    else:
        user = os.environ.get("USER", "")
        roots = [Path("/Volumes")] if sys.platform == "darwin" else [Path("/media") / user, Path("/run/media") / user, Path("/media")]
        for root in roots:
            if root.is_dir():
                for p in root.iterdir():
                    if p.is_dir() and not p.is_symlink() and os.path.ismount(p) and not p.name.startswith("."):
                        out.append({"path": str(p), "label": p.name})
    return out

def is_y1_drive(d):
    """Checks if a drive belongs to the Y1 player."""
    p = Path(d["path"])
    lbl = d.get("label", "").lower()
    if any(k in lbl for k in ("innioasis", "y1", "rockbox", "nugget")):
        return True
    try:
        if (p / ".rockbox").exists():
            return True
        if (p / "Music").exists() and (p / "Recordings").exists():
            return True
    except (PermissionError, OSError):
        pass
    return False

# -------------------------------------------------------------------- state
S = {"stage": "idle", "step": None, "progress": 0, "message": "", "error": None, "drives": []}
RUN = {"id": 0, "proc": None}
lock = threading.Lock()

def alive(rid):
    return RUN["id"] == rid

def fail(rid, step, msg):
    if alive(rid):
        S.update(stage="error", step=step, error=msg)

def run_flash(partition, rid):
    img = Path(assets["boot"])
    cmd = [sys.executable, "-u", str(APP_DIR / "mtk.py"), "w", partition, img.name]
    log("run: " + " ".join(cmd) + f"   (in {img.parent})")
    env = dict(os.environ, PYTHONUNBUFFERED="1", PYTHONIOENCODING="utf-8")
    flags = 0x08000000 if os.name == "nt" else 0
    p = subprocess.Popen(cmd, cwd=str(img.parent), stdin=subprocess.DEVNULL,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         text=True, bufsize=1, env=env, creationflags=flags)
    RUN["proc"] = p
    found = False
    for line in p.stdout:
        line = line.strip()
        if not line or not alive(rid):
            continue
        log(line)
        low = line.lower()
        if "handshake failed" in low:
            if S["stage"] == "waiting":
                S["message"] = "Y1 spotted. Connecting"
            continue
        if re.search(r"hint|waiting|retrying|failed|not found|please |power off|already connected|for brom|for preloader|^\.+$", low):
            continue
        m = re.search(r"(\d+(?:\.\d+)?)\s*%", line) if re.search(r"progress|sector|write", low) else None
        if m:
            found = True
            S.update(stage="flashing", message="Installing Nugget", progress=int(float(m.group(1))))
        elif S["stage"] == "waiting" and re.search(r"device detected|hw code|cpu:|da_handler|daxflash|uploading|sending|writing|wrote", low):
            found = True
            S.update(stage="flashing", message="Y1 found. Installing Nugget, please don't unplug it.", progress=0)
    p.wait()
    return p.returncode == 0, found

def get_scatter_indices(scatter_path):
    indices = {}
    try:
        with open(scatter_path, "r", encoding="utf-8") as f:
            content = f.read()
        for block in content.split("- partition_index:"):
            m_idx = re.search(r"SYS(\d+)", block)
            m_name = re.search(r"partition_name:\s*([A-Za-z0-9_]+)", block)
            if m_idx and m_name:
                indices[m_name.group(1).upper()] = int(m_idx.group(1))
    except Exception as e:
        log(f"Error reading scatter indices: {e}")
    return indices

def run_spflash(rid):
    exe = SPFLASH_DIR / "flash_tool.exe"
    scatter = SPFLASH_DIR / "MT6572_Android_scatter.txt"
    cfg = SPFLASH_DIR / "console_mode.xml"
    if not exe.exists() or not scatter.exists():
        log("SP Flash Tool or scatter file not found")
        return False, False

    indices = get_scatter_indices(scatter)
    boot_idx = indices.get("BOOTIMG", indices.get("BOOT", 9))
    logo_idx = indices.get("LOGO", 8)

    # Copy boot image to spflash/boot.img
    try:
        shutil.copyfile(Path(assets["boot"]), SPFLASH_DIR / "boot.img")
    except Exception as e:
        log(f"Failed to copy boot image to spflash: {e}")
        return False, False

    # Copy logo if present
    rom_entries = [f'<rom index="{boot_idx}" enable="true">boot.img</rom>']
    if assets.get("logo") and Path(assets["logo"]).exists():
        try:
            shutil.copyfile(Path(assets["logo"]), SPFLASH_DIR / "logo.bin")
            rom_entries.append(f'<rom index="{logo_idx}" enable="true">logo.bin</rom>')
        except Exception as e:
            log(f"Failed to copy logo.bin to spflash: {e}")

    # Generate schema-compliant console_mode.xml
    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<flashtool-config version="2.0">
  <general>
    <chip-name>MT6572</chip-name>
    <storage-type>EMMC</storage-type>
    <download-agent>MTK_AllInOne_DA.bin</download-agent>
    <scatter>{scatter.name}</scatter>
    <rom-list>
      {"".join(rom_entries)}
    </rom-list>
    <connection type="BromUSB" high-speed="true" power="AutoDetect" timeout-count="3600000" com-port="" />
  </general>
  <commands>
    <da-download-all />
  </commands>
</flashtool-config>"""
    try:
        with open(cfg, "w", encoding="utf-8") as f:
            f.write(xml_content)
    except Exception as e:
        log(f"Failed to write console_mode.xml: {e}")
        return False, False

    run_log = SPFLASH_DIR / "spflash_run.log"
    if run_log.exists():
        try: run_log.unlink()
        except Exception: pass

    cmd = [str(exe), "-i", str(cfg)]
    log("run: " + " ".join(cmd) + f"   (in {SPFLASH_DIR})")

    # Pass the log file handle directly to capture stdout/stderr from SP Flash Tool
    flags = 0x08000000 if os.name == "nt" else 0  # CREATE_NO_WINDOW
    out_file = open(run_log, "wb")
    p = subprocess.Popen(cmd, cwd=str(SPFLASH_DIR), stdin=subprocess.DEVNULL,
                         stdout=out_file, stderr=subprocess.STDOUT, creationflags=flags)
    RUN["proc"] = p
    found = False
    success = False
    last_pos = 0

    while alive(rid):
        if run_log.exists():
            try:
                with open(run_log, "r", encoding="utf-8", errors="replace") as f:
                    f.seek(last_pos)
                    new_text = f.read()
                    if new_text:
                        last_pos = f.tell()
                        for line in new_text.splitlines():
                            line = line.strip()
                            if not line: continue
                            log(f"[SPFlash] {line}")
                            low = line.lower()
                            if "usb port detected" in low or "brom connected" in low:
                                found = True
                                S.update(stage="flashing", message="Y1 connected. Preparing flash...", progress=20)
                            elif "connecting to da" in low or "download da now" in low:
                                found = True
                                S.update(stage="flashing", message="Connecting to Download Agent...", progress=40)
                            elif "da connected" in low or "cb_da_report" in low:
                                found = True
                                S.update(stage="flashing", message="DA connected. Initializing flash...", progress=60)
                            elif "downloading images" in low:
                                found = True
                                S.update(stage="flashing", message="Flashing Nugget boot & logo...", progress=80)
                            elif "download succeeded" in low or "all command exec done" in low:
                                success = True
                                found = True
                                S.update(stage="flashing", message="Flashing complete!", progress=100)
            except Exception:
                pass

        if p.poll() is not None:
            break
        time.sleep(0.1)

    try: out_file.close()
    except Exception: pass

    # Final check on log file content after process exits
    if run_log.exists():
        try:
            with open(run_log, "r", encoding="utf-8", errors="replace") as f:
                content = f.read().lower()
                if "download succeeded" in content or "all command exec done" in content:
                    success = True
                    found = True
                    S.update(stage="flashing", message="Flashing complete!", progress=100)
        except Exception:
            pass

    if p.returncode == 0:
        success = True

    return success, found

def flash_task(rid):
    S.update(stage="prep", step="flash", progress=0, message="Getting things ready", error=None)
    while not assets["ready"].is_set():
        S["progress"] = assets["progress"]
        time.sleep(0.3)
        if not alive(rid): return
    if assets["error"]:
        return fail(rid, "flash", assets["error"])

    S.update(stage="waiting", progress=0, message="Waiting for your Y1")
    ok = False
    initial_paths = {d["path"] for d in drives()}

    def check_powered_on():
        current = drives()
        curr_paths = {d["path"] for d in current}
        new_paths = curr_paths - initial_paths
        if any(is_y1_drive(d) for d in current) or any(d["path"] in new_paths for d in current):
            S.update(message="Your Y1 is powered on in USB drive mode. Press the pinhole once to shut down.")
        else:
            S.update(message="Waiting for your Y1")

    if os.name == "nt":
        if not (SPFLASH_DIR / "flash_tool.exe").exists():
            return fail(rid, "flash", "SP Flash Tool files are missing from the spflash folder.")
        
        for _ in range(60):
            check_powered_on()
            ok, found = run_spflash(rid)
            if ok or not alive(rid):
                break
            time.sleep(1)
    else:
        if not (APP_DIR / "mtk.py").exists():
            return fail(rid, "flash", "Some installer files are missing. Please download the installer again.")
        
        for _ in range(60):
            check_powered_on()
            ok, found = run_flash("boot", rid)
            if ok or found or not alive(rid):
                break
            time.sleep(1)

    if not alive(rid): return
    if not ok:
        return fail(rid, "flash", "The installation didn't finish. Unplug your Y1 and try again.")
    
    # ADVANCE TO STAGE 3 (Waiting for Y1 to mount as a drive)
    S.update(stage="waiting_drive", progress=0, message="Waiting for your Y1 to show up as a drive")
    wait_for_drive(rid)

def recovery_task(rid, dest=None):
    """Repairs the .rockbox folder without touching user music."""
    S.update(stage="prep", step="recovery", progress=0, message="Getting recovery files ready", error=None)
    while not assets["ready"].is_set():
        S["progress"] = assets["progress"]
        time.sleep(0.3)
        if not alive(rid): return
    if assets["error"]:
        return fail(rid, "recovery", assets["error"])

    if not dest:
        detected = [d["path"] for d in drives() if is_y1_drive(d)]
        if detected:
            dest = detected[0]
        else:
            S.update(stage="waiting_drive", progress=0, message="Connect your Y1 to your computer as a USB drive")
            while alive(rid) and not dest:
                for d in drives():
                    if is_y1_drive(d):
                        dest = d["path"]
                        break
                time.sleep(1)
    if not alive(rid): return

    S.update(stage="recovering", step="recovery", progress=0, message="Repairing .rockbox (preserving your music)...")
    try:
        with zipfile.ZipFile(assets["zip"]) as z:
            items = z.infolist()
            for i, item in enumerate(items, 1):
                if not alive(rid): return
                z.extract(item, dest)
                S["progress"] = int(100 * i / len(items))
        if hasattr(os, "sync"): os.sync()
        if alive(rid):
            S.update(stage="done", progress=100, message="Recovery complete! Your .rockbox installation has been repaired.")
    except Exception as e:
        log(f"recovery failed: {e}")
        fail(rid, "recovery", "Could not repair files. Ensure the Y1 drive is still mounted and accessible.")

def wait_for_drive(rid):
    before = {d["path"] for d in drives()}
    while alive(rid):
        now = drives()
        paths = {d["path"] for d in now}
        before &= paths
        S["drives"] = now
        new = paths - before
        if new:
            time.sleep(2)  # let it finish mounting
            return copy_task(rid, sorted(new)[0])
        time.sleep(1)

def copy_task(rid, dest):
    S.update(stage="copying", step="copy", progress=0, message="Copying Nugget to your Y1", error=None)
    try:
        with zipfile.ZipFile(assets["zip"]) as z:
            items = z.infolist()
            for i, item in enumerate(items, 1):
                if not alive(rid): return
                z.extract(item, dest)
                S["progress"] = int(100 * i / len(items))
        if hasattr(os, "sync"): os.sync()
        if alive(rid): S.update(stage="done", progress=100, message="")
    except Exception as e:
        log(f"copy failed: {e}")
        fail(rid, "copy", "We couldn't copy the files. Make sure your Y1 is still connected and try again.")

import atexit

def stop_proc():
    p = RUN["proc"]
    if p and p.poll() is None:
        try:
            if os.name == "nt":
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)], capture_output=True)
            else:
                p.kill()
            p.wait(timeout=3)
        except Exception:
            pass

atexit.register(stop_proc)

def spawn(fn, *args):
    with lock:
        RUN["id"] += 1
        stop_proc()
        rid = RUN["id"]
    threading.Thread(target=fn, args=(rid, *args), daemon=True).start()

def reset():
    with lock:
        RUN["id"] += 1
        stop_proc()
    S.update(stage="idle", step=None, progress=0, message="", error=None, drives=[])

# ------------------------------------------------------------------- server
last_poll = [time.time()]

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(WEB_DIR), **k)
    def log_message(self, *a): pass
    def translate_path(self, path):
        p = super().translate_path(path)
        if not os.path.exists(p):
            alt = RESOURCE_DIR / Path(p).relative_to(WEB_DIR)
            if alt.suffix.lower() in (".png", ".jpg", ".jpeg", ".gif", ".webp") and alt.exists():
                return str(alt)
        return p
    def reply(self, obj):
        data = json.dumps(obj).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
    def do_GET(self):
        if self.path == "/api/state":
            last_poll[0] = time.time()
            return self.reply(S)
        super().do_GET()
    def do_POST(self):
        p = self.path
        n = int(self.headers.get("Content-Length") or 0)

        # Direct file stream endpoint for Local Mode uploads
        if p.startswith("/api/upload"):
            import urllib.parse
            query = urllib.parse.parse_qs(urllib.parse.urlparse(p).query)
            ftype = query.get("type", [""])[0]
            fname = query.get("name", ["file.bin"])[0]
            data = self.rfile.read(n)
            local_dir = CACHE / "local"
            local_dir.mkdir(parents=True, exist_ok=True)
            target = local_dir / fname
            with open(target, "wb") as f:
                f.write(data)
            if ftype == "boot":
                assets["boot"] = target
            elif ftype == "logo":
                assets["logo"] = target
            elif ftype == "zip":
                assets["zip"] = target
            if assets["boot"] and assets["zip"]:
                assets["ready"].set()
                assets["error"] = None
            return self.reply({"ok": True, "path": str(target)})

        body = json.loads(self.rfile.read(n) or b"{}")
        if p == "/api/start":
            spawn(flash_task)
        elif p == "/api/start_local":
            b, l, z = local_build()
            if b and z and not assets["boot"]:
                assets["boot"], assets["logo"], assets["zip"] = b, l, z
                assets["ready"].set()
            spawn(flash_task)
        elif p == "/api/recovery":
            spawn(recovery_task, body.get("path"))
        elif p == "/api/retry":
            if S["step"] == "copy": spawn(copy_task, body.get("path") or (drives() or [{"path": None}])[0]["path"])
            else:
                if assets["error"]: retry_prefetch()
                spawn(flash_task)
        elif p == "/api/copy" and body.get("path"):
            spawn(copy_task, body["path"])
        elif p == "/api/reset":
            reset()
        elif p == "/api/quit":
            reset()
            threading.Timer(0.5, lambda: (stop_proc(), os._exit(0))).start()
        self.reply({"ok": True})

def watchdog():
    while True:
        time.sleep(10)
        if time.time() - last_poll[0] > 120 and S["stage"] not in ("flashing", "copying"):
            stop_proc(); os._exit(0)

def main():
    if IS_FROZEN:
        USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copytree(SPFLASH_RESOURCE_DIR, SPFLASH_DIR, dirs_exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    url = f"http://127.0.0.1:{server.server_address[1]}/"
    threading.Thread(target=prefetch, daemon=True).start()
    threading.Thread(target=watchdog, daemon=True).start()
    webbrowser.open(url)
    print("Nugget Installer is open in your browser. Keep this window open until you're done. 브라우저에서 Nugget Installer가 열려 있습니다. 작업이 완료될 때까지 이 창을 그대로 열어 두세요.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        reset()

if __name__ == "__main__":
    main()