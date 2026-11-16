"""Remove one Peeky 3 copy, retaining its Data directory."""
import argparse
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys


# Resolve and remove shortcuts in one Windows shell. A shortcut belonging
# to a different Peeky copy is left alone, even if it has the same name.
SHORTCUTS = r"""
$ErrorActionPreference = 'Stop'
$root = $env:PEEKY_UNINSTALL_ROOT
$paths = @((Join-Path $root 'Peeky 3.lnk'))
foreach ($kind in 'DesktopDirectory', 'Programs') {
    $folder = [Environment]::GetFolderPath($kind)
    if ($folder) { $paths += Join-Path $folder 'Peeky 3.lnk' }
}
$shell = New-Object -ComObject WScript.Shell
foreach ($path in $paths | Select-Object -Unique) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { continue }
    if ((Get-Item -LiteralPath $path).Attributes -band [IO.FileAttributes]::ReparsePoint) { continue }
    $shortcut = $shell.CreateShortcut($path)
    $target = [Environment]::ExpandEnvironmentVariables($shortcut.TargetPath)
    $argsPath = [Environment]::ExpandEnvironmentVariables($shortcut.Arguments.Trim().Trim('"'))
    $relativeLaunchers = 'Start Peeky.pyw','Start.pyw','App\peeky.py'
    $directLaunchers = @($relativeLaunchers + 'Run-Peeky.cmd' | ForEach-Object { Join-Path $root $_ })
    $pythonLauncher = (Split-Path -Leaf $target) -in @('python.exe','pythonw.exe','py.exe')
    if (($target -in $directLaunchers) -or ($pythonLauncher -and ($argsPath -in $directLaunchers))) {
        if ($env:PEEKY_UNINSTALL_PREVIEW -eq '1') {
            Write-Host "Shortcut: $path"
        } else {
            Remove-Item -LiteralPath $path -Force
            Write-Host "Removed shortcut: $path"
        }
    }
}
"""


def checked_path(root, relative):
    path = root / relative
    if not path.resolve().is_relative_to(root):
        raise ValueError(f"Path outside this Peeky folder: {path}")
    try:
        attributes = path.lstat().st_file_attributes
    except FileNotFoundError:
        return path
    if attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
        raise ValueError(f"Linked path requires manual review: {path}")
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preview", action="store_true", help="list the planned removal")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    app = checked_path(root, "App")
    if not (app / "peeky.py").is_file() or not (app / "peeky.ico").is_file():
        raise ValueError(f"Peeky 3 was not found in {root}")

    # App is the installed program payload. Data resides next to App.
    paths = [app, *(checked_path(root, name) for name in
             (".venv", "Start.pyw", "Start Peeky.pyw", "Run-Peeky.cmd", "Setup.py"))]
    paths = [path for path in paths if path.exists()]
    if Path(sys.executable).resolve().is_relative_to(root):
        raise ValueError("Run the uninstaller using Python installed outside this Peeky folder.")

    print(f"Peeky 3: {root}", flush=True)
    for path in paths:
        print(f"Remove: {path}", flush=True)
    print(f"Keep: {root / 'Data'}", flush=True)
    print("Close all windows of this Peeky copy before continuing.", flush=True)
    if not args.preview and input('Type YES to uninstall: ').strip().upper() not in {"TAK", "YES"}:
        print("Cancelled.")
        return

    powershell = Path(os.environ["SystemRoot"]) / "System32/WindowsPowerShell/v1.0/powershell.exe"
    subprocess.run([str(powershell), "-NoProfile", "-NonInteractive", "-Command", SHORTCUTS],
                   env={**os.environ, "PEEKY_UNINSTALL_ROOT": str(root),
                        "PEEKY_UNINSTALL_PREVIEW": "1" if args.preview else "0"}, check=True)
    if not args.preview:
        for path in paths:
            if path.is_dir():
                # Python's Windows rmtree removes directory junctions without following them.
                shutil.rmtree(path)
            else:
                path.unlink()
        print("Peeky 3 removed. Data, Python and Ollama were kept.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"Peeky 3 uninstall: {exc}", file=sys.stderr)
        sys.exit(1)
