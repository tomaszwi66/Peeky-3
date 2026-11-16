"""English and Polish translations and persisted language settings."""
import json
import os
from paths import DATA_DIR

SETTINGS_FILE = DATA_DIR / "settings.json"

SUPPORTED = ("en", "pl")
DEFAULT   = "en"


def load_settings() -> dict:
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("lang") not in SUPPORTED:
            data["lang"] = DEFAULT
        return data
    except Exception:
        return {"lang": DEFAULT}


def save_settings(**kwargs) -> None:
    data = load_settings()
    data.update(kwargs)
    temp = SETTINGS_FILE.with_suffix(".tmp")
    with temp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(temp, SETTINGS_FILE)


# Language-specific runtime config -------------------------------------------
STT = {
    "en": "en-US",
    "pl": "pl-PL",
}

TTS_ONLINE = {
    "en": "en-US-AriaNeural",
    "pl": "pl-PL-ZofiaNeural",
}

# Substring matched against installed Windows SAPI voice names.
TTS_OFFLINE = {
    "en": "Zira",
    "pl": "Paulina",   # falls back to any Polish voice if Paulina missing
}

SYSTEM_PROMPT = {
    "en": (
        "You are Peeky 3, a precise vision-first desktop sidekick powered "
        "by qwen3-vl. Reply in clear, concise English. Speak naturally "
        "without greetings or sign-offs. Never use emoji or special symbols. "
        "Plain text only."
    ),
    "pl": (
        "Jesteś Peeky 3, precyzyjnym asystentem wizualnym na pulpicie "
        "opartym o qwen3-vl. Odpowiadaj w jasnym, zwięzłym języku polskim. "
        "Mów naturalnie, bez powitań i pożegnań. Nigdy nie używaj emoji "
        "ani znaków specjalnych. Tylko zwykły tekst."
    ),
}

COACH_SYSTEM = {
    "en": (
        "You are a precise visual coaching assistant. Reply in clear, "
        "concise English. No greetings, no sign-offs, no emoji. Signal "
        "completion ONLY with the single word: TASK_COMPLETE. Use it only "
        "when there is clear, unambiguous visual evidence the task is "
        "fully done."
    ),
    "pl": (
        "Jesteś precyzyjnym asystentem coachingu wizualnego. Odpowiadaj "
        "po polsku, krótko i jasno. Bez powitań, bez pożegnań, bez emoji. "
        "Zakończenie sygnalizuj WYŁĄCZNIE jednym słowem: TASK_COMPLETE. "
        "Używaj go tylko gdy istnieje jednoznaczny dowód wizualny, że "
        "zadanie zostało w pełni wykonane."
    ),
}


# UI strings -----------------------------------------------------------------
STRINGS = {
    "en": {
        "title":             "Peeky 3",
        "state_idle":        "Ready",
        "state_recording":   "Listening. Click to stop.",
        "state_selecting":   "Select an area",
        "state_thinking":    "Thinking",
        "state_speaking":    "Speaking",
        "state_coaching":    "Video Coach active",
        "state_error":       "Error",

        "btn_screen":        "Screen",
        "btn_camera":        "Camera",
        "btn_clipboard":     "Clipboard",
        "btn_type":          "Type",
        "btn_video_coach":   "Video Coach",
        "btn_video_coach_active": "Video Coach (active)",
        "btn_stop":          "● STOP",
        "btn_stop_op":       "Stop",
        "stopped":           "Stopped",
        "dlg_title":         "Type your question",
        "dlg_label":         "Type your question (Enter to send, Shift+Enter for newline):",
        "dlg_send":          "Send  (Enter)",
        "dlg_cancel":        "Cancel",
        "model_running":     "Model: {model}",
        "result_window":     "Result",

        "tools_header":      "VISION TOOLS",
        "tool_detect":       "Detect",
        "tool_point":        "Point",
        "tool_ocr":          "OCR",
        "tool_count":        "Count",
        "tool_document":     "Document",
        "tool_ui":           "UI",
        "tool_depth":        "Depth",
        "tool_segment":      "Object masks",
        "tool_ask":          "Ask",
        "scene_3d":          "3D Preview",

        "menu_copy":         "⎘  Copy reply",
        "menu_history":      "📖  History",
        "menu_clear":        "🗑  Clear context",
        "menu_log":          "📄  Open log",
        "menu_language":     "🌐  Language",
        "menu_lang_en":      "English",
        "menu_lang_pl":      "Polski",
        "menu_quit":         "✕  Quit",

        "ask_detect":        "What objects should I detect? (e.g. 'cat', 'all faces', 'red buttons')",
        "ask_point":         "What should I point at?",
        "ask_count":         "What should I count?",
        "ask_ask":           "What do you want to ask about the captured region?",

        "clipboard_empty":   "Clipboard is empty",
        "clipboard_prompt":  "Analyze or explain the following text from the clipboard:\n\n{clip}",
        "ctx_cleared":       "Context cleared",
        "copied":            "Copied",
        "ask_about_area":    "Ask about the captured area",
        "lang_saved":        "Language saved. Restart Peeky 3 to apply.",
        "scene_launched":    "3D scene launched",
        "no_mic":            "No microphone detected",
        "found_n":           "Found {n} {target}.",
        "counted_n":         "Counted {n} {target}.",
        "pointed_at":        "Pointed at {target}.",
        "depth_estimated":   "Depth map estimated.",
        "no_text_found":     "No text found.",
        "detected_n_ui":     "Detected {n} UI elements.",
        "no_response":       "No response.",
        "document_parsed":   "Document parsed.",
    },
    "pl": {
        "title":             "Peeky 3",
        "state_idle":        "Gotowy",
        "state_recording":   "Słucham. Kliknij, aby zakończyć.",
        "state_selecting":   "Zaznacz obszar",
        "state_thinking":    "Myślę",
        "state_speaking":    "Mówię",
        "state_coaching":    "Video Coach aktywny",
        "state_error":       "Błąd",

        "btn_screen":        "Ekran",
        "btn_camera":        "Kamera",
        "btn_clipboard":     "Schowek",
        "btn_type":          "Tekst",
        "btn_video_coach":   "Video Coach",
        "btn_video_coach_active": "Video Coach (aktywny)",
        "btn_stop":          "● STOP",
        "btn_stop_op":       "Zatrzymaj",
        "stopped":           "Zatrzymano",
        "dlg_title":         "Wpisz pytanie",
        "dlg_label":         "Wpisz pytanie (Enter wysyła, Shift+Enter to nowa linia):",
        "dlg_send":          "Wyślij  (Enter)",
        "dlg_cancel":        "Anuluj",
        "model_running":     "Model: {model}",
        "result_window":     "Wynik",

        "tools_header":      "NARZĘDZIA WIZJI",
        "tool_detect":       "Wykryj",
        "tool_point":        "Wskaż",
        "tool_ocr":          "OCR",
        "tool_count":        "Policz",
        "tool_document":     "Dokument",
        "tool_ui":           "UI",
        "tool_depth":        "Głębia",
        "tool_segment":      "Maski obiekt\u00f3w",
        "tool_ask":          "Pytaj",
        "scene_3d":          "Podgl\u0105d 3D",

        "menu_copy":         "⎘  Kopiuj odpowiedź",
        "menu_history":      "📖  Historia",
        "menu_clear":        "🗑  Wyczyść kontekst",
        "menu_log":          "📄  Otwórz log",
        "menu_language":     "🌐  Język",
        "menu_lang_en":      "English",
        "menu_lang_pl":      "Polski",
        "menu_quit":         "✕  Zakończ",

        "ask_detect":        "Jakie obiekty mam wykryć? (np. 'kot', 'wszystkie twarze', 'czerwone przyciski')",
        "ask_point":         "Co mam wskazać?",
        "ask_count":         "Co mam policzyć?",
        "ask_ask":           "Co chcesz zapytać o zaznaczony fragment?",

        "clipboard_empty":   "Schowek jest pusty",
        "clipboard_prompt":  "Przeanalizuj lub wyjaśnij poniższy tekst ze schowka:\n\n{clip}",
        "ctx_cleared":       "Kontekst wyczyszczony",
        "copied":            "Skopiowano",
        "ask_about_area":    "Zadaj pytanie o zaznaczony obszar",
        "lang_saved":        "Język zapisany. Uruchom Peeky 3 ponownie, aby zastosować.",
        "scene_launched":    "Scena 3D uruchomiona",
        "no_mic":            "Nie wykryto mikrofonu",
        "found_n":           "Znaleziono {n}: {target}.",
        "counted_n":         "Policzono {n}: {target}.",
        "pointed_at":        "Wskazano: {target}.",
        "depth_estimated":   "Mapa głębi oszacowana.",
        "no_text_found":     "Nie znaleziono tekstu.",
        "detected_n_ui":     "Wykryto {n} elementów UI.",
        "no_response":       "Brak odpowiedzi.",
        "document_parsed":   "Dokument przetworzony.",
    },
}


class Translator:
    def __init__(self, lang: str = None):
        if lang not in SUPPORTED:
            lang = load_settings().get("lang", DEFAULT)
        self.lang = lang

    def t(self, key: str, **fmt) -> str:
        s = STRINGS.get(self.lang, STRINGS[DEFAULT]).get(
            key, STRINGS[DEFAULT].get(key, key))
        return s.format(**fmt) if fmt else s

    @property
    def stt(self):           return STT[self.lang]
    @property
    def tts_online(self):    return TTS_ONLINE[self.lang]
    @property
    def tts_offline(self):   return TTS_OFFLINE[self.lang]
    @property
    def system_prompt(self): return SYSTEM_PROMPT[self.lang]
    @property
    def coach_system(self):  return COACH_SYSTEM[self.lang]
