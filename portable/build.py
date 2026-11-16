"""Package only release files. No environments, settings, or session data."""
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


portable = Path(__file__).resolve().parent
source = portable.parent
output = source / "dist" / "Peeky3-Portable.zip"
output.parent.mkdir(exist_ok=True)
app_files = ("peeky.py", "spatial.py", "qwen_vision.py", "paths.py", "i18n.py",
             "peeky.ico", "requirements.txt", "LICENSE")
ui_files = ("__init__.py", "layout.py", "overlay_draw.py", "scene_view.py")

with ZipFile(output, "w", compression=ZIP_DEFLATED) as archive:
    for name in ("Start.pyw", "Run-Peeky.cmd", "Setup.py", "README.md", "Uninstall-Peeky.cmd", "Uninstall.py"):
        archive.write(portable / name, f"Peeky3-Portable/{name}")
    for name in app_files:
        archive.write(source / name, f"Peeky3-Portable/App/{name}")
    for name in ui_files:
        archive.write(source / "ui" / name, f"Peeky3-Portable/App/ui/{name}")
    archive.write(source / "installer" / "prepare_speech.py", "Peeky3-Portable/App/prepare_speech.py")
print(output)
