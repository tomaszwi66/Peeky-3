# Peeky 3 Portable

## Run on Windows x64

1. Install [Python 3.11 x64](https://www.python.org/downloads/windows/) with the Python Launcher (`py`) and [Ollama](https://ollama.com/download/windows).
2. Start Ollama. If the default vision model is missing, run `ollama pull qwen3-vl:4b-instruct` in a terminal. This model ran reliably in local testing. Other image-capable models can be selected in **Settings**, with results varying by model.
3. Extract the entire archive to a writable folder and run `Run-Peeky.cmd`. First-run setup installs dependencies and downloads speech assets. Use the same launcher on later runs.
4. Choose **Screen** or **Camera**, then type a question or click the Peeky logo to begin recording. Click the logo again to submit. Use **Settings** to choose your Ollama models and **PL** or **EN** to switch languages.

For a desktop shortcut, point it at `.venv\Scripts\pythonw.exe` and pass the full path to `Start.pyw` as the argument. On a second PC, extract a fresh copy and run setup there.

## Tools and controls

- **Video Coach.** Set a goal and choose a camera or screen region. **Auto** waits for the current answer to finish playing before taking the next snapshot. It switches off if playback fails. **Check** captures one snapshot. **Stop** ends the session.
- **Count and UI.** Count reports an estimate and shows any boxes returned by the model. UI lists detected controls. Select a row to highlight that control.
- **Depth and 3D Preview.** Inspect relative distance as a heatmap, a point cloud or a mesh. Warmer colors indicate nearer surfaces. The first use may download Depth Anything V2 Small. Drag to rotate and scroll to zoom.
- **Masks.** OpenCV GrabCut refines object boxes returned by the vision model. Mask quality depends on how well the boxes fit and how visible the object boundaries are.
- **Collapse.** Click **-** to shrink the widget and **+** to reopen it. A purple **+** indicates an active Auto session.
- **Voice.** Speech recognition is local by default. The Microsoft online voice receives answer text and falls back to a local voice if available. Turn off the online voice in **Settings** to use local audio output.

## Remove a copy

Close Peeky, run `Uninstall-Peeky.cmd` and enter `YES`. The uninstaller removes the app files and shortcuts for that copy. Its `Data` folder retains settings, history and downloaded assets for reuse.

