import os
import runpy
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
app = root / "App"
os.environ["PEEKY_DATA_DIR"] = str(root / "Data")
sys.path.insert(0, str(app))
runpy.run_path(str(app / "peeky.py"), run_name="__main__")
