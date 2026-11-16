"""First-run setup in the extracted folder, using the installed Python."""
import hashlib
import os
import subprocess
import sys
from pathlib import Path


root = Path(__file__).resolve().parent
app = root / "App"
data = root / "Data"
data.mkdir(exist_ok=True)
os.environ["PEEKY_DATA_DIR"] = str(data)
requirements = app / "requirements.txt"
marker = Path(sys.prefix) / "peeky-install.txt"
cpu_stack = ("torch==2.7.1", "torchvision==0.22.1")
fingerprint = hashlib.sha256(requirements.read_bytes() + " ".join(cpu_stack).encode()).hexdigest()

if not marker.is_file() or marker.read_text(encoding="utf-8") != fingerprint:
    print("Installing Peeky dependencies in this folder.", flush=True)
    pip = [sys.executable, "-m", "pip", "--disable-pip-version-check", "install", "--only-binary=:all:"]
    subprocess.run([*pip, *cpu_stack, "--index-url", "https://download.pytorch.org/whl/cpu"], check=True)
    subprocess.run([*pip, "-r", str(requirements)], check=True)
    marker.write_text(fingerprint, encoding="utf-8")

voices = data / "voice-assets-ready"
if not voices.is_file():
    print("Preparing offline speech assets.", flush=True)
    result = subprocess.run([sys.executable, str(app / "prepare_speech.py")], check=False)
    if result.returncode == 0:
        voices.touch()
    else:
        print("Offline speech downloads did not finish. Peeky can still open. Re-run to retry.")
