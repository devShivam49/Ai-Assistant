import math
import os
import threading

from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPoint
from PyQt5.QtGui import (QPainter, QColor, QPen, QFont, QPainterPath,
                          QPolygonF, QRadialGradient, QBrush, QPixmap)
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QLabel, QLineEdit)

from core.brain import decide
from core.emotion import detect_emotion
from core.listen import listen
from core.memory import recall, remember
from core.speak import speak
from core.wake_word import WAKE_ONLY, cleanup, detect, init_wake
from features.search import search_google, search_youtube
from features.summary import write_summary
from features.system import (lock_pc, open_chrome, open_explorer, open_google,
                              open_notepad, open_vscode, open_youtube, restart,
                              shutdown, tell_time, volume_down, volume_up)


class GirlWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.phase = 0.0
        self.mode  = "idle"
        self.setFixedSize(200, 300)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Load girl.png from ui/ folder
        img_path = os.path.join(os.path.dirname(__file__), "girl.png")
        if os.path.exists(img_path):
            self.pixmap = QPixmap(img_path).scaled(
                200, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        else:
            self.pixmap = None
            print(f"[GirlWidget] girl.png not found at {img_path}")

        t = QTimer(self)
        t.timeout.connect(self._tick)
        t.start(35)

    def set_mode(self, mode: str):
        self.mode = mode
        self.update()

    def _tick(self):
        self.phase += 0.06
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        bob = math.sin(self.phase) * 4

        if self.pixmap:
            p.translate(0, bob)
            p.drawPixmap(0, 0, self.pixmap)
        else:
            # Fallback simple circle if no image
            ac = {"idle": QColor(120,140,220), "listening": QColor(80,200,140),
                  "thinking": QColor(255,195,60), "speaking": QColor(255,100,180)
                  }.get(self.mode, QColor(120,140,220))
            p.setBrush(ac)
            p.setPen(Qt.NoPen)
            p.translate(0, bob)
            p.drawEllipse(60, 60, 80, 80)
            p.setFont(QFont("Segoe UI", 8))
            p.setPen(QColor(255,255,255))
            p.drawText(50, 170, 100, 30, Qt.AlignCenter, self.mode)


class JarvisApp(QWidget):
    status_sig = pyqtSignal(str)
    mode_sig   = pyqtSignal(str)
    bubble_sig = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.running   = False
        self._busy     = False
        self._drag_pos = None
        self._thread   = None

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(230, 430)

        self.status_sig.connect(lambda m: self.status_lbl.setText(m))
        self.mode_sig.connect(lambda m: self.girl.set_mode(m))
        self.bubble_sig.connect(lambda m: self.bubble.setText(m or "..."))

        self._build_ui()
        self._place()
        # Auto-start voice on launch
        QTimer.singleShot(500, self.start_voice)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 10)
        layout.setSpacing(5)

        # Status
        self.status_lbl = QLabel("Ready")
        self.status_lbl.setAlignment(Qt.AlignCenter)
        self.status_lbl.setFont(QFont("Segoe UI", 8, QFont.Bold))
        self.status_lbl.setStyleSheet(
            "color:#8899ff;background:rgba(8,6,20,200);"
            "border:1px solid rgba(100,110,220,100);border-radius:6px;padding:3px 8px;"
        )
        layout.addWidget(self.status_lbl)

        # Avatar
        self.girl = GirlWidget()
        layout.addWidget(self.girl, 0, Qt.AlignCenter)

        # Speech bubble
        self.bubble = QLabel("Hi Shivam! Say Jarvis.")
        self.bubble.setWordWrap(True)
        self.bubble.setAlignment(Qt.AlignCenter)
        self.bubble.setFont(QFont("Segoe UI", 9))
        self.bubble.setMinimumHeight(52)
        self.bubble.setStyleSheet(
            "color:#fff0f8;background:rgba(10,8,24,215);"
            "border:1px solid rgba(120,110,220,130);border-radius:8px;padding:6px 8px;"
        )
        layout.addWidget(self.bubble)

        # Text input
        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Type to Jarvis...")
        self.input_box.setFont(QFont("Consolas", 9))
        self.input_box.setStyleSheet(
            "background:rgba(8,6,22,200);color:#e8f0ff;"
            "border:1px solid rgba(100,110,220,80);border-radius:6px;padding:4px 7px;"
        )
        self.input_box.returnPressed.connect(self.submit_text)
        layout.addWidget(self.input_box)

        # Buttons
        row = QHBoxLayout()
        row.setSpacing(5)

        btn = ("QPushButton{background:rgba(70,80,180,210);color:white;border:0;"
               "border-radius:6px;padding:5px;font-weight:bold;font-size:10px;}"
               "QPushButton:hover{background:rgba(90,105,215,235);}"
               "QPushButton:disabled{background:rgba(40,38,60,150);color:rgba(255,255,255,70);}")

        self.voice_btn = QPushButton("🎤 Voice")
        self.voice_btn.setStyleSheet(btn)
        self.voice_btn.clicked.connect(self.start_voice)

        self.mute_btn = QPushButton("🔇 Mute")
        self.mute_btn.setStyleSheet(btn)
        self.mute_btn.clicked.connect(self.stop_voice)
        self.mute_btn.setEnabled(False)

        close_btn = QPushButton("✕")
        close_btn.setFixedWidth(30)
        close_btn.setStyleSheet(
            "QPushButton{background:rgba(160,40,60,190);color:white;border:0;"
            "border-radius:6px;padding:5px;font-weight:bold;}"
            "QPushButton:hover{background:rgba(200,55,75,220);}"
        )
        close_btn.clicked.connect(QApplication.quit)

        row.addWidget(self.voice_btn)
        row.addWidget(self.mute_btn)
        row.addWidget(close_btn)
        layout.addLayout(row)

    def _place(self):
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.right() - self.width() - 20,
                  screen.bottom() - self.height() - 40)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag_pos = e.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if self._drag_pos and e.buttons() & Qt.LeftButton:
            self.move(e.globalPos() - self._drag_pos)

    def mouseReleaseEvent(self, _):
        self._drag_pos = None

    def start_voice(self):
        if self.running:
            return
        self.running = True
        self.voice_btn.setEnabled(False)
        self.mute_btn.setEnabled(True)
        self._thread = threading.Thread(target=self._voice_loop, daemon=True)
        self._thread.start()

    def stop_voice(self):
        self.running = False
        self.voice_btn.setEnabled(True)
        self.mute_btn.setEnabled(False)
        self.status_sig.emit("Muted")
        self.mode_sig.emit("idle")

    def submit_text(self):
        cmd = self.input_box.text().strip()
        if not cmd:
            return
        self.input_box.clear()
        threading.Thread(target=self._handle, args=(cmd,), daemon=True).start()

    def _voice_loop(self):
        self.status_sig.emit("Starting...")
        self.mode_sig.emit("thinking")
        porcupine = pa = stream = None
        try:
            porcupine, pa, stream = init_wake()
            self.status_sig.emit("🎤 Say Jarvis!")
            self.bubble_sig.emit("Say 'Jarvis' to wake me up!")
            self.mode_sig.emit("idle")
            print("[Voice] Ready — say 'Jarvis'")

            while self.running:
                try:
                    cmd = detect(porcupine, stream)
                except Exception as e:
                    print(f"[Voice] detect error: {e}")
                    continue

                if not cmd:
                    continue

                print(f"[Voice] Wake detected, cmd='{cmd}'")
                self.mode_sig.emit("listening")

                if cmd == WAKE_ONLY:
                    speak("Yes, I'm listening.")
                    self.bubble_sig.emit("Yes, I'm listening...")
                    self.status_sig.emit("Listening...")
                    import time; time.sleep(0.3)
                    cmd = listen()
                    print(f"[Voice] Command heard: '{cmd}'")
                    if not cmd:
                        self.bubble_sig.emit("I didn't catch that.")
                        self.status_sig.emit("🎤 Say Jarvis!")
                        self.mode_sig.emit("idle")
                        continue

                self._handle(cmd)
                self.status_sig.emit("🎤 Say Jarvis!")
                self.mode_sig.emit("idle")

        except Exception as e:
            self.status_sig.emit("Mic error — type instead")
            self.bubble_sig.emit(f"Voice error: {e}")
            print(f"[Voice Loop Error] {e}")
            import traceback; traceback.print_exc()
            self.mode_sig.emit("idle")
        finally:
            cleanup(porcupine, pa, stream)

    def _handle(self, command: str):
        if self._busy:
            return
        self._busy = True
        try:
            command = command.strip()
            if not command:
                return
            self.status_sig.emit("Thinking...")
            self.bubble_sig.emit("Thinking...")
            self.mode_sig.emit("thinking")

            decision = decide(command)
            action   = decision.get("action", "talk")
            response = decision.get("response", "")
            data     = decision.get("data", "")
            emotion  = detect_emotion(command)

            self.bubble_sig.emit(response)
            self.mode_sig.emit("speaking")
            self._run_action(action, response, data, emotion, decision, command)
        finally:
            self._busy = False
            self.status_sig.emit("Say Jarvis!" if self.running else "Type below")
            self.mode_sig.emit("idle")

    def _run_action(self, action, response, data, emotion, decision, command):
        if action == "talk":
            speak(response, emotion)
        elif action == "search":
            search_google(data or command)
        elif action == "open_youtube":
            search_youtube(data) if data else open_youtube()
        elif action == "open_google":
            open_google()
        elif action == "open_chrome":
            open_chrome()
        elif action == "open_notepad":
            open_notepad()
        elif action == "open_vscode":
            open_vscode()
        elif action == "open_explorer":
            open_explorer()
        elif action == "time":
            tell_time()
        elif action == "shutdown":
            speak(response, emotion); shutdown()
        elif action == "restart":
            speak(response, emotion); restart()
        elif action == "lock":
            lock_pc()
        elif action == "volume_up":
            volume_up()
        elif action == "volume_down":
            volume_down()
        elif action == "summary":
            write_summary()
        elif action == "recall":
            key = decision.get("key", data)
            val = recall(key)
            speak(val if val else f"Nothing saved for {key}.", emotion)
        elif action == "remember":
            key = decision.get("key", "")
            val = decision.get("value", data)
            if key and val:
                remember(key, val)
                speak(f"Got it! {key} is {val}.", emotion)
            else:
                speak("I couldn't figure out what to remember.", emotion)
        else:
            speak(response or "I'm not sure how to handle that.", emotion)