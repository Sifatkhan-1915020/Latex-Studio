import os
import shutil
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
WORKSPACES_DIR = DATA_DIR / "workspaces"
DB_PATH = DATA_DIR / "overleaf.db"
BIN_DIR = BASE_DIR / "bin"

# Cross-platform Tectonic executable discovery
def get_tectonic_path() -> Path:
    # 1. Check local bin/ folder (Windows or Linux)
    win_bin = BIN_DIR / "tectonic.exe"
    if win_bin.exists():
        return win_bin
    nix_bin = BIN_DIR / "tectonic"
    if nix_bin.exists():
        return nix_bin
    
    # 2. Check system PATH (Docker, Linux package, or Homebrew)
    which_path = shutil.which("tectonic")
    if which_path:
        return Path(which_path)
    
    # 3. Default standard paths
    if os.name == "nt":
        return win_bin
    return Path("/usr/local/bin/tectonic")

def ensure_tectonic_installed() -> Path:
    target_path = get_tectonic_path()
    if target_path.exists():
        return target_path
    
    # If in Docker or system path found, return it
    which_path = shutil.which("tectonic")
    if which_path:
        return Path(which_path)
        
    print("⏳ Downloading standalone Tectonic LaTeX engine (one-time setup)...")
    import urllib.request
    import zipfile
    import tarfile
    import platform

    os.makedirs(BIN_DIR, exist_ok=True)
    is_windows = platform.system() == "Windows"
    is_darwin = platform.system() == "Darwin"
    
    version = "0.15.0"
    if is_windows:
        url = f"https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%40{version}/tectonic-{version}-x86_64-pc-windows-msvc.zip"
        archive_path = BIN_DIR / "tectonic.zip"
        urllib.request.urlretrieve(url, archive_path)
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(BIN_DIR)
        if archive_path.exists():
            archive_path.unlink()
        print("✓ Tectonic LaTeX compiler downloaded successfully.")
        return BIN_DIR / "tectonic.exe"
    else:
        pkg = "apple-darwin" if is_darwin else "unknown-linux-musl"
        url = f"https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%40{version}/tectonic-{version}-x86_64-{pkg}.tar.gz"
        archive_path = BIN_DIR / "tectonic.tar.gz"
        urllib.request.urlretrieve(url, archive_path)
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(BIN_DIR)
        if archive_path.exists():
            archive_path.unlink()
        dest = BIN_DIR / "tectonic"
        if dest.exists():
            os.chmod(dest, 0o755)
        print("✓ Tectonic LaTeX compiler downloaded successfully.")
        return dest

TECTONIC_EXE = get_tectonic_path()


# Security & JWT
SECRET_KEY = os.environ.get("SECRET_KEY", "overleaf-super-secret-jwt-key-change-in-production-1234567890")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Ensure data folders exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(WORKSPACES_DIR, exist_ok=True)
os.makedirs(BIN_DIR, exist_ok=True)
