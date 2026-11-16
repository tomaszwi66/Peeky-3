from pathlib import Path

from faster_whisper.utils import download_model
from huggingface_hub import hf_hub_download
from piper import PiperVoice

from paths import DATA_DIR, LOCAL_VOICES


download_model("base", cache_dir=str(DATA_DIR / "whisper"))
voice_dir = DATA_DIR / "voices"
for folder, name in LOCAL_VOICES.values():
    location = voice_dir / folder
    for filename in (name + ".onnx", name + ".onnx.json", "MODEL_CARD"):
        if not (location / filename).is_file():
            hf_hub_download("rhasspy/piper-voices", filename,
                            subfolder=folder, local_dir=voice_dir)
    PiperVoice.load(Path(location / (name + ".onnx")))
print("English and Polish speech assets ready.")
