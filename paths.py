import os
from pathlib import Path


APP_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("PEEKY_DATA_DIR") or
                Path(os.environ.get("LOCALAPPDATA", Path.home())) / "Peeky3" / "Data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_VISION_MODEL = "qwen3-vl:4b-instruct"
LOCAL_VOICES = {
    "en": ("en/en_US/lessac/medium", "en_US-lessac-medium"),
    "pl": ("pl/pl_PL/gosia/medium", "pl_PL-gosia-medium"),
}
