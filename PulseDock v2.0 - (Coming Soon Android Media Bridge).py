
from __future__ import annotations

import asyncio
import json
import os
import sys
import threading
from dataclasses import dataclass
from typing import Optional

from PyQt6.QtCore import Qt, QTimer, QPoint, QSize, QThread, pyqtSignal, QObject
from PyQt6.QtGui import QAction, QActionGroup, QIcon, QPen, QPixmap, QPainter, QColor, QPolygon
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMenu,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSystemTrayIcon,
    QToolButton,
    QVBoxLayout,
    QWidget,
    QGraphicsDropShadowEffect,
)

try:
    from winsdk.windows.media.control import (
        GlobalSystemMediaTransportControlsSessionManager as MediaManager,
    )
except Exception:
    MediaManager = None


APP_NAME = "PulseDock Widget"
from pathlib import Path

APP_NAME = "PulseDock Widget"

SETTINGS_DIR = Path.home() / "AppData" / "Local" / APP_NAME
SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
ICON_CACHE_DIR = SETTINGS_DIR / "icon_cache"
ICON_CACHE_DIR.mkdir(parents=True, exist_ok=True)

SETTINGS_FILE = SETTINGS_DIR / "settings.json"
# SETTINGS_FILE = "settings.json"

def resource_path(path):
    try:
        base = sys._MEIPASS
    except:
        base = os.path.abspath(".")
    return os.path.join(base, path)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
# APP_ICON = QIcon(resource_path("PulseDock.ico"))
def exception_hook(exctype, value, tb):
    import traceback
    try:
        with open("crash_log.txt", "w") as f:
            traceback.print_exception(exctype, value, tb, file=f)
    except Exception:
        pass
    sys.__excepthook__(exctype, value, tb)
    sys.exit(1)

sys.excepthook = exception_hook


@dataclass
class Snapshot:
    title: str = "No music playing"
    artist: str = "Start YouTube Music / Spotify"
    status: str = "Stopped"
    can_play: bool = True
    can_pause: bool = True
    can_prev: bool = True
    can_next: bool = True
    aumid: str = ""


SIZE_CONFIGS = {
    50: {
        "play_size": 28,
        "play_radius": 14,
        "skip_size": 24,
        "skip_radius": 12,
        "icon_play": 16,
        "icon_skip": 14,
        "title_size": 11,
        "artist_size": 9,
        "status_size": 8,
    },
    75: {
        "play_size": 30,
        "play_radius": 15,
        "skip_size": 26,
        "skip_radius": 13,
        "icon_play": 18,
        "icon_skip": 16,
        "title_size": 12,
        "artist_size": 10,
        "status_size": 9,
    },
    100: {
        "play_size": 36,
        "play_radius": 18,
        "skip_size": 30,
        "skip_radius": 15,
        "icon_play": 22,
        "icon_skip": 18,
        "title_size": 14,
        "artist_size": 12,
        "status_size": 11,
    },
    125: {
        "play_size": 42,
        "play_radius": 21,
        "skip_size": 34,
        "skip_radius": 17,
        "icon_play": 24,
        "icon_skip": 20,
        "title_size": 15,
        "artist_size": 13,
        "status_size": 12,
    },
    150: {
        "play_size": 44,
        "play_radius": 22,
        "skip_size": 36,
        "skip_radius": 18,
        "icon_play": 26,
        "icon_skip": 22,
        "title_size": 16,
        "artist_size": 13,
        "status_size": 12,
    }
}


def get_friendly_source_name(aumid: str, artist: str = "") -> str:
    if not aumid:
        return ""
    aumid_lower = aumid.lower()
    artist_lower = (artist or "").lower()
    
    if "spotify" in aumid_lower:
        return "Spotify"
    if "ytmusic" in aumid_lower or "youtube music" in aumid_lower or "ytmdesktop" in aumid_lower:
        return "YouTube Music"
    if "youtube" in aumid_lower:
        return "YouTube"
    if "apple" in aumid_lower and "music" in aumid_lower:
        return "Apple Music"
    
    if "chrome" in aumid_lower:
        if "youtube" in artist_lower or "music.youtube" in artist_lower:
            return "YouTube Music (Chrome)"
        return "Chrome"
    if "msedge" in aumid_lower:
        if "youtube" in artist_lower or "music.youtube" in artist_lower:
            return "YouTube Music (Edge)"
        return "Edge"
    if "firefox" in aumid_lower:
        return "Firefox"
        
    if "zunemusic" in aumid_lower or "groove" in aumid_lower:
        return "Media Player"
    if "wmplayer" in aumid_lower:
        return "Windows Media Player"
    if "vlc" in aumid_lower:
        return "VLC"
        
    parts = aumid.split('!')
    candidate = parts[0]
    if '.' in candidate:
        parts_dot = candidate.split('.')
        for p in reversed(parts_dot):
            if p.lower() not in ["exe", "app", "desktop", "zrj5gp2svntom", "8wekyb3d8bbwe"]:
                return p.capitalize()
    return candidate.capitalize()


# Theme Definitions
THEME_CONFIGS = {
    "spotify_black": {
        "name": "Spotify Black",
        "bg_color": (25, 20, 20),
        "text_color": "#FFFFFF",
        "artist_color": "#B3B3B3",
        "dot_color": "#1DB954",
        "icon_color": "#FFFFFF",
        "play_bg": "#1DB954",
        "play_hover_bg": "#1ed760",
        "play_fg": "#191414",
        "light_theme": False
    },
    "spotify_white": {
        "name": "Spotify White",
        "bg_color": (255, 255, 255),
        "text_color": "#191414",
        "artist_color": "#727272",
        "dot_color": "#1DB954",
        "icon_color": "#191414",
        "play_bg": "#1DB954",
        "play_hover_bg": "#1ed760",
        "play_fg": "#FFFFFF",
        "light_theme": True
    },
    "yt_black": {
        "name": "YouTube Music Black",
        "bg_color": (15, 15, 15),
        "text_color": "#FFFFFF",
        "artist_color": "#AAAAAA",
        "dot_color": "#FF0000",
        "icon_color": "#FFFFFF",
        "play_bg": "#FF0000",
        "play_hover_bg": "#ff3333",
        "play_fg": "#FFFFFF",
        "light_theme": False
    },
    "yt_white": {
        "name": "YouTube Music White",
        "bg_color": (249, 249, 249),
        "text_color": "#0F0F0F",
        "artist_color": "#606060",
        "dot_color": "#FF0000",
        "icon_color": "#0F0F0F",
        "play_bg": "#FF0000",
        "play_hover_bg": "#cc0000",
        "play_fg": "#FFFFFF",
        "light_theme": True
    },
    "theme_1": {
        "name": "Midnight Drive (Theme 1)",
        "bg_color": (10, 12, 16),
        "text_color": "#FFFFFF",
        "artist_color": "#8E9AA8",
        "dot_color": "#10B981",
        "icon_color": "#FFFFFF",
        "play_bg": None,
        "play_hover_bg": None,
        "play_fg": "#FFFFFF",
        "light_theme": False
    },
    "theme_2": {
        "name": "Daylight (Theme 2)",
        "bg_color": (236, 236, 236),
        "text_color": "#1C1E21",
        "artist_color": "#5F6368",
        "dot_color": "#1D9BF0",
        "icon_color": "#1C1E21",
        "play_bg": "#1D9BF0",
        "play_hover_bg": "#3baaf5",
        "play_fg": "#FFFFFF",
        "light_theme": True
    },
    "theme_5": {
        "name": "Coffee & Cigarettes (Theme 5)",
        "bg_color": (215, 196, 183),
        "text_color": "#3E2723",
        "artist_color": "#6D4C41",
        "dot_color": "#5C4033",
        "icon_color": "#3E2723",
        "play_bg": "#5C4033",
        "play_hover_bg": "#755241",
        "play_fg": "#FFFFFF",
        "light_theme": True
    }
}


def get_colored_icon(icon_name: str, color_hex: str) -> QIcon:
    # svg_path = f"icons/{icon_name}.svg"
    svg_path = resource_path(f"icons/{icon_name}.svg")
    try:
        if not os.path.exists(svg_path):
            return QIcon()
        with open(svg_path, "r") as f:
            svg_data = f.read()

        # Replace standard fill color (#e3e3e3)
        svg_data = svg_data.replace('fill="#e3e3e3"', f'fill="{color_hex}"')
        svg_data = svg_data.replace('fill="#E3E3E3"', f'fill="{color_hex}"')

        # os.makedirs("temp", exist_ok=True)
        # temp_path = f"temp/{icon_name}_{color_hex.replace('#', '')}.svg"
        temp_path = str(ICON_CACHE_DIR /f"{icon_name}_{color_hex.replace('#', '')}.svg")

        with open(temp_path, "w") as f:
            f.write(svg_data)
        return QIcon(temp_path)
    except Exception:
        return QIcon(svg_path)


def safe_run(coro, default):
    try:
        return asyncio.run(coro)
    except asyncio.CancelledError:
        return default
    except Exception:
        return default


def enum_name(value) -> str:
    if value is None:
        return ""
    name = getattr(value, "name", None)
    if isinstance(name, str) and name:
        return name
    text = str(value)
    if "." in text:
        text = text.split(".")[-1]
    return text


async def read_snapshot_async() -> Snapshot:
    if MediaManager is None:
        return Snapshot(
            title="winsdk missing",
            artist="Install: pip install PyQt6 winsdk",
            status="Error",
            can_play=False,
            can_pause=False,
            can_prev=False,
            can_next=False,
            aumid="",
        )

    try:
        manager = await MediaManager.request_async()
        session = manager.get_current_session()

        if session is None:
            sessions = list(manager.get_sessions() or [])
            session = sessions[0] if sessions else None

        if session is None:
            return Snapshot()

        info = session.get_playback_info()
        status = enum_name(getattr(info, "playback_status", None))
        controls = getattr(info, "controls", None)

        props = await session.try_get_media_properties_async()
        title = (getattr(props, "title", None) or "Unknown title").strip()
        artist = (getattr(props, "artist", None) or "Unknown artist").strip()
        aumid = getattr(session, "source_app_user_model_id", "")

        return Snapshot(
            title=title,
            artist=artist,
            status=status or "Unknown",
            can_play=bool(getattr(controls, "is_play_enabled", True)),
            can_pause=bool(getattr(controls, "is_pause_enabled", True)),
            can_prev=bool(getattr(controls, "is_previous_enabled", True)),
            can_next=bool(getattr(controls, "is_next_enabled", True)),
            aumid=aumid,
        )
    except asyncio.CancelledError:
        return Snapshot()
    except Exception as exc:
        import traceback
        traceback.print_exc()
        return Snapshot(
            title="SMTC error",
            artist=type(exc).__name__,
            status="Error",
            can_play=False,
            can_pause=False,
            can_prev=False,
            can_next=False,
            aumid="",
        )


async def send_control_async(action: str) -> bool:
    if MediaManager is None:
        return False

    try:
        manager = await MediaManager.request_async()
        session = manager.get_current_session()
        if session is None:
            sessions = list(manager.get_sessions() or [])
            session = sessions[0] if sessions else None
        if session is None:
            return False

        method_map = {
            "play_pause": "try_toggle_play_pause_async",
            "play": "try_play_async",
            "pause": "try_pause_async",
            "next": "try_skip_next_async",
            "previous": "try_skip_previous_async",
        }
        method_name = method_map.get(action)
        if not method_name:
            return False

        method = getattr(session, method_name, None)
        if method is None:
            return False

        # WinRT methods return IAsyncOperation objects. They implement __await__
        # so we can await them directly — do NOT use asyncio.wait_for() on them.
        result = method()
        if result is not None and hasattr(result, '__await__'):
            await result
        elif asyncio.iscoroutine(result):
            await result
        # else: void/fire-and-forget — WinRT handles it on its own thread pool
        return True
    except Exception as exc:
        import traceback
        traceback.print_exc()
        return False


def icon_for_app() -> QIcon:
    from PyQt6.QtCore import QRectF
    from PyQt6.QtGui import (
        QPainter,
        QPixmap,
        QColor,
        QPainterPath,
        QPolygon,
        QIcon
    )

    pix = QPixmap(128, 128)
    pix.fill(Qt.GlobalColor.transparent)

    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Main rounded red pill
    pill = QPainterPath()
    pill.addRoundedRect(QRectF(8, 20, 112, 88), 28, 28)

    p.fillPath(pill, QColor("#FF2747"))

    # Play button
    play = QPolygon([
        QPoint(52, 42),
        QPoint(52, 86),
        QPoint(88, 64)
    ])

    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("white"))
    p.drawPolygon(play)

    # Left waveform
    p.setBrush(QColor("white"))
    p.drawRoundedRect(24, 52, 6, 24, 3, 3)
    p.drawRoundedRect(34, 42, 8, 44, 4, 4)

    # Right waveform
    p.drawRoundedRect(96, 52, 6, 24, 3, 3)
    p.drawRoundedRect(106, 42, 8, 44, 4, 4)

    # Small black dots
    p.setBrush(QColor("#111111"))
    p.drawEllipse(16, 60, 6, 6)
    p.drawEllipse(44, 60, 6, 6)
    p.drawEllipse(88, 60, 6, 6)

    # Music note stem
    p.setBrush(QColor("#111111"))
    p.drawRoundedRect(112, 58, 10, 4, 2, 2)

    # White note circle
    p.setBrush(QColor("white"))
    p.drawEllipse(102, 82, 16, 16)

    p.end()

    return QIcon(pix)


class MarqueeLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._scroll_offset = 0.0
        self._scroll_speed = 0.8  # Speed in pixels per frame
        self._text_width = 0
        self._is_scrolling = False
        self._gap = 60  # Gap between scrolling repetitions

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_scroll)

        self._delay_timer = QTimer(self)
        self._delay_timer.setSingleShot(True)
        self._delay_timer.timeout.connect(self._start_scroll)

    def setText(self, text):
        if text == self.text():
            return
        super().setText(text)
        self._scroll_offset = 0.0
        self._timer.stop()
        self._delay_timer.stop()
        self._is_scrolling = False
        self.update_geometry_and_scroll()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_geometry_and_scroll()

    def update_geometry_and_scroll(self):
        fm = self.fontMetrics()
        self._text_width = fm.horizontalAdvance(self.text())

        if self._text_width > self.width() and self.width() > 0:
            if not self._is_scrolling:
                self._delay_timer.start(2000)  # Pause before scrolling
        else:
            self._timer.stop()
            self._delay_timer.stop()
            self._scroll_offset = 0.0
            self._is_scrolling = False
            self.update()

    def _start_scroll(self):
        self._is_scrolling = True
        self._timer.start(25)  # Loop ~40 FPS

    def _update_scroll(self):
        if not self._is_scrolling:
            return
        self._scroll_offset += self._scroll_speed
        if self._scroll_offset >= (self._text_width + self._gap):
            self._scroll_offset = 0.0
            self._timer.stop()
            self._is_scrolling = False
            self._delay_timer.start(1500)
        self.update()

    def paintEvent(self, event):
        if not self._is_scrolling or self._text_width <= self.width():
            super().paintEvent(event)
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        color = self.palette().color(self.foregroundRole())
        painter.setPen(color)
        painter.setFont(self.font())

        fm = painter.fontMetrics()
        y = (self.height() - fm.height()) // 2 + fm.ascent()

        x1 = -int(self._scroll_offset)
        painter.drawText(x1, y, self.text())

        x2 = x1 + self._text_width + self._gap
        if x2 < self.width():
            painter.drawText(x2, y, self.text())

        painter.end()


class SMTCWorker(QThread):
    """
    Background worker that polls SMTC every second.

    Uses asyncio.run() per poll call — the same pattern as the backup code
    that is known to work with winsdk WinRT IAsyncOperation objects.
    asyncio.wait_for() and persistent loops are NOT used because they are
    incompatible with WinRT IAsyncOperation's __await__ implementation.
    """
    snapshot_updated = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._running = True
        # threading.Event lets trigger_refresh() wake the sleep immediately
        self._wake = threading.Event()

    def run(self):
        import ctypes
        try:
            ctypes.windll.ole32.CoInitializeEx(None, 0)
        except Exception:
            pass

        while self._running:
            try:
                snap = asyncio.run(read_snapshot_async())
                if isinstance(snap, Snapshot):
                    self.snapshot_updated.emit(snap)
            except Exception:
                pass

            # Wait up to 1 second, but wake immediately on trigger_refresh()
            self._wake.wait(timeout=1.0)
            self._wake.clear()

        try:
            ctypes.windll.ole32.CoUninitialize()
        except Exception:
            pass

    def trigger_refresh(self):
        """Wake the polling loop immediately instead of waiting for next tick."""
        self._wake.set()

    def stop(self):
        self._running = False
        self._wake.set()  # Unblock the wait() so the thread exits quickly


class MusicWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._drag_offset = QPoint()
        self.snapshot = Snapshot()
        self.last_theme_code = None
        self.last_transparency_pct = None
        self.last_playing_status = None

        # Load persisted settings
        self.settings = self.load_settings()
        self.current_theme_code = self.settings.get("theme", "auto")
        self.current_transparency_pct = self.settings.get("transparency", 82)
        self.always_on_top = self.settings.get("always_on_top", True)
        self.current_scale_pct = self.settings.get("scale", 100)

        self.setWindowTitle(APP_NAME)
        
        # Configure window flags
        flags = (
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
        )
        if self.always_on_top:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        
        # Size matching compact horizontal layout (card and window are both 330x76 with 0px margins)
        # Scale is applied after UI is built via _apply_scale()
        
        # Restore position
        self.move(self.settings.get("x", 100), self.settings.get("y", 100))

        self._build_ui()
        self._build_tray()

        # Apply scale first so window size is correct before styling
        self._apply_scale()
        
        # Apply style sheet based on loaded settings
        self._apply_theme_style()

        # Connect cleanup on app quit
        QApplication.instance().aboutToQuit.connect(self._cleanup)

        # Setup and start Worker Thread (non-blocking QThread with COM MTA)
        self.worker = SMTCWorker(self)
        self.worker.snapshot_updated.connect(self._handle_snapshot)
        self.worker.start()

    def load_settings(self) -> dict:
        defaults = {
            "theme": "auto",
            "transparency": 82,
            "always_on_top": True,
            "scale": 100,
            "x": 100,
            "y": 100
        }
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    data = json.load(f)
                    defaults.update(data)
            except Exception:
                pass
        return defaults

    def save_settings(self):
        settings = {
            "theme": self.current_theme_code,
            "transparency": self.current_transparency_pct,
            "always_on_top": self.always_on_top,
            "scale": self.current_scale_pct,
            "x": self.x(),
            "y": self.y()
        }
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(settings, f, indent=4)
        except Exception:
            pass

    def moveEvent(self, event):
        super().moveEvent(event)
        self.save_settings()

    def _build_ui(self):
        # Window-level layout (outer margin set to 0 as requested)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Floating card container
        self.card = QFrame()
        self.card.setObjectName("card")
        outer.addWidget(self.card)

        # Initialize labels as children of self.card
        self.title = MarqueeLabel("No music playing", self.card)
        self.title.setObjectName("title")
        self.title.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.artist = QLabel("Start YouTube Music / Spotify", self.card)
        self.artist.setObjectName("artist")
        self.artist.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.status_dot = QLabel(self.card)
        self.status_dot.setObjectName("status_dot")
        self.status_dot.setFixedSize(8, 8)

        self.status_text = QLabel("Stopped", self.card)
        self.status_text.setObjectName("status_text")

        # Initialize buttons as children of self.card
        self.prev_btn = QToolButton(self.card)
        self.prev_btn.setObjectName("skip_btn")
        self.prev_btn.clicked.connect(lambda: self.send_control("previous"))

        self.play_btn = QToolButton(self.card)
        self.play_btn.setObjectName("play_btn")
        self.play_btn.clicked.connect(lambda: self.send_control("play_pause"))

        self.next_btn = QToolButton(self.card)
        self.next_btn.setObjectName("skip_btn")
        self.next_btn.clicked.connect(lambda: self.send_control("next"))

        # Subtle absolute-positioned minimize button in top-right of the card
        self.min_btn = QToolButton(self.card)
        self.min_btn.setObjectName("min_btn")
        self.min_btn.clicked.connect(self.hide_to_tray)

    def _rebuild_card_layout(self, scale: int):
        # pyrefly: ignore [missing-import]
        from PyQt6.sip import delete as sip_delete
        
        # 1. Safely clear old layout
        old_layout = self.card.layout()
        if old_layout is not None:
            while old_layout.count():
                old_layout.takeAt(0)
            sip_delete(old_layout)
            
        # 2. Get size parameters
        size_cfg = SIZE_CONFIGS.get(scale, SIZE_CONFIGS[100])
        
        # Configure button dimensions
        self.play_btn.setFixedSize(size_cfg["play_size"], size_cfg["play_size"])
        self.prev_btn.setFixedSize(size_cfg["skip_size"], size_cfg["skip_size"])
        self.next_btn.setFixedSize(size_cfg["skip_size"], size_cfg["skip_size"])
        
        self.play_btn.setIconSize(QSize(size_cfg["icon_play"], size_cfg["icon_play"]))
        self.prev_btn.setIconSize(QSize(size_cfg["icon_skip"], size_cfg["icon_skip"]))
        self.next_btn.setIconSize(QSize(size_cfg["icon_skip"], size_cfg["icon_skip"]))
        
        # Configure minimize button
        if scale == 50:
            self.min_btn.hide()
        elif scale == 75:
            self.min_btn.show()
            self.min_btn.setFixedSize(14, 14)
            self.min_btn.setIconSize(QSize(7, 7))
        elif scale == 100:
            self.min_btn.show()
            self.min_btn.setFixedSize(16, 16)
            self.min_btn.setIconSize(QSize(8, 8))
        else: # 125, 150
            self.min_btn.show()
            self.min_btn.setFixedSize(18, 18)
            self.min_btn.setIconSize(QSize(9, 9))
            
        # Reset text alignments
        if scale != 150:
            self.title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.artist.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.status_text.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        # 3. Create the appropriate layout based on size mode
        if scale == 50:  # Extra Small (XS) - Only 3 buttons
            self.title.hide()
            self.artist.hide()
            self.status_dot.hide()
            self.status_text.hide()
            
            self.prev_btn.show()
            self.play_btn.show()
            self.next_btn.show()
            
            layout = QHBoxLayout(self.card)
            layout.setContentsMargins(12, 6, 12, 6)
            layout.setSpacing(8)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(self.prev_btn)
            layout.addWidget(self.play_btn)
            layout.addWidget(self.next_btn)
            
        elif scale == 75:  # Small (S) - Title/Artist, no status, media buttons centered
            self.title.show()
            self.artist.show()
            self.status_dot.hide()
            self.status_text.hide()
            
            self.prev_btn.show()
            self.play_btn.show()
            self.next_btn.show()
            
            left_layout = QVBoxLayout()
            left_layout.setSpacing(2)
            left_layout.setContentsMargins(0, 0, 0, 0)
            left_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
            left_layout.addWidget(self.title)
            left_layout.addWidget(self.artist)
            
            right_layout = QHBoxLayout()
            right_layout.setSpacing(6)
            right_layout.setContentsMargins(0, 0, 0, 0)
            right_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
            right_layout.addWidget(self.prev_btn)
            right_layout.addWidget(self.play_btn)
            right_layout.addWidget(self.next_btn)
            
            layout = QHBoxLayout(self.card)
            layout.setContentsMargins(12, 8, 12, 8)
            layout.setSpacing(12)
            layout.addLayout(left_layout, 1)
            layout.addLayout(right_layout, 0)
            
        elif scale in (100, 125):  # Normal (N) / Wide (W) - Full horizontal details
            self.title.show()
            self.artist.show()
            self.status_dot.show()
            self.status_text.show()
            
            self.prev_btn.show()
            self.play_btn.show()
            self.next_btn.show()
            
            left_layout = QVBoxLayout()
            left_layout.setSpacing(2)
            left_layout.setContentsMargins(0, 0, 0, 0)
            left_layout.addWidget(self.title)
            left_layout.addWidget(self.artist)
            
            status_layout = QHBoxLayout()
            status_layout.setSpacing(6)
            status_layout.setContentsMargins(0, 0, 0, 0)
            status_layout.addWidget(self.status_dot)
            status_layout.addWidget(self.status_text)
            status_layout.addStretch(1)
            left_layout.addLayout(status_layout)
            
            right_layout = QHBoxLayout()
            right_layout.setSpacing(6)
            right_layout.setContentsMargins(0, 0, 0, 0)
            right_layout.addWidget(self.prev_btn)
            right_layout.addWidget(self.play_btn)
            right_layout.addWidget(self.next_btn)
            
            layout = QHBoxLayout(self.card)
            margins = (18, 14, 18, 14) if scale == 125 else (16, 12, 16, 12)
            layout.setContentsMargins(*margins)
            layout.setSpacing(14 if scale == 125 else 12)
            layout.addLayout(left_layout, 1)
            layout.addLayout(right_layout, 0)
            
        elif scale == 150:  # Large (L) - Vertical Square
            self.title.show()
            self.artist.show()
            self.status_dot.show()
            self.status_text.show()
            
            self.prev_btn.show()
            self.play_btn.show()
            self.next_btn.show()
            
            # Center-align texts for Square mode
            self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.artist.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.status_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            layout = QVBoxLayout(self.card)
            layout.setContentsMargins(16, 20, 16, 16)
            layout.setSpacing(8)
            
            layout.addWidget(self.title)
            layout.addWidget(self.artist)
            
            status_layout = QHBoxLayout()
            status_layout.setSpacing(6)
            status_layout.setContentsMargins(0, 0, 0, 0)
            status_layout.addStretch(1)
            status_layout.addWidget(self.status_dot)
            status_layout.addWidget(self.status_text)
            status_layout.addStretch(1)
            layout.addLayout(status_layout)
            
            layout.addStretch(1)
            
            controls_layout = QHBoxLayout()
            controls_layout.setSpacing(14)
            controls_layout.setContentsMargins(0, 0, 0, 0)
            controls_layout.addStretch(1)
            controls_layout.addWidget(self.prev_btn)
            controls_layout.addWidget(self.play_btn)
            controls_layout.addWidget(self.next_btn)
            controls_layout.addStretch(1)
            layout.addLayout(controls_layout)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        
        scale = self.current_scale_pct
        if scale == 50:
            self.min_btn.hide()
            return
            
        btn_w = 14 if scale == 75 else (18 if scale >= 125 else 16)
        btn_h = btn_w
        
        x_offset = btn_w + 4
        y_offset = 4
        
        self.min_btn.setGeometry(
            self.card.width() - x_offset,
            y_offset,
            btn_w,
            btn_h
        )

    def _build_tray(self):
        # self.tray = QSystemTrayIcon(icon_for_app(), self)
        # self.tray = QSystemTrayIcon(QIcon("PulseDock.ico"), self)
        # self.tray = QSystemTrayIcon(APP_ICON, self)
        self.tray = QSystemTrayIcon(QIcon(resource_path("PulseDock.ico")),self)
        self.tray.setToolTip(APP_NAME)

        menu = QMenu()

        # Always on Top toggle
        self.always_on_top_action = QAction("Always on Top", self, checkable=True)
        self.always_on_top_action.setChecked(self.always_on_top)
        self.always_on_top_action.triggered.connect(self.toggle_always_on_top)
        menu.addAction(self.always_on_top_action)

        menu.addSeparator()

        # Themes Submenu
        themes_menu = QMenu("Themes", self)
        self.themes_group = QActionGroup(self)
        
        themes = [
            ("Auto (Dynamic)", "auto"),
            ("Spotify Black", "spotify_black"),
            ("Spotify White", "spotify_white"),
            ("YouTube Music Black", "yt_black"),
            ("YouTube Music White", "yt_white"),
            ("Midnight Drive (Theme 1)", "theme_1"),
            ("Daylight (Theme 2)", "theme_2"),
            ("Coffee & Cigarettes (Theme 5)", "theme_5")
        ]
        
        self.theme_actions = {}
        for name, code in themes:
            action = QAction(name, self, checkable=True)
            action.setData(code)
            action.triggered.connect(self.change_theme_from_action)
            self.themes_group.addAction(action)
            themes_menu.addAction(action)
            self.theme_actions[code] = action

        # Check the active theme action
        active_theme = self.theme_actions.get(self.current_theme_code)
        if active_theme:
            active_theme.setChecked(True)
            
        menu.addMenu(themes_menu)

        # Transparency Submenu
        transparency_menu = QMenu("Transparency", self)
        self.trans_group = QActionGroup(self)
        
        trans_levels = [100, 90, 80, 70, 60, 50, 40, 30, 20]
        self.trans_actions = {}
        for pct in trans_levels:
            action = QAction(f"{pct}%", self, checkable=True)
            action.setData(pct)
            action.triggered.connect(self.change_transparency_from_action)
            self.trans_group.addAction(action)
            transparency_menu.addAction(action)
            self.trans_actions[pct] = action

        # Check the active transparency action
        active_trans = self.trans_actions.get(self.current_transparency_pct)
        if active_trans:
            active_trans.setChecked(True)

        menu.addMenu(transparency_menu)

        # Size Submenu
        size_menu = QMenu("Size", self)
        self.size_group = QActionGroup(self)

        size_levels = [
            ("Extra Small (XS)", 50),
            ("Small (S)", 75),
            ("Normal (N)", 100),
            ("Wide (W)", 125),
            ("Large (L)", 150),
        ]
        self.size_actions = {}
        for label, pct in size_levels:
            action = QAction(label, self, checkable=True)
            action.setData(pct)
            action.triggered.connect(self.change_scale_from_action)
            self.size_group.addAction(action)
            size_menu.addAction(action)
            self.size_actions[pct] = action

        # Check the active size action
        active_size = self.size_actions.get(self.current_scale_pct)
        if active_size:
            active_size.setChecked(True)

        menu.addMenu(size_menu)

        menu.addSeparator()

        # Show / Hide actions
        show_action = QAction("Show Widget", self)
        show_action.triggered.connect(self.show_from_tray)
        menu.addAction(show_action)

        hide_action = QAction("Hide Widget", self)
        hide_action.triggered.connect(self.hide_to_tray)
        menu.addAction(hide_action)

        menu.addSeparator()

        # Quit action
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        menu.addAction(quit_action)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._tray_activated)
        self.tray.show()

    def change_theme_from_action(self):
        action = self.sender()
        if action:
            self.current_theme_code = action.data()
            self._apply_theme_style()
            self.save_settings()

    def change_transparency_from_action(self):
        action = self.sender()
        if action:
            self.current_transparency_pct = action.data()
            self._apply_theme_style()
            self.save_settings()

    def change_scale_from_action(self):
        action = self.sender()
        if action:
            self.current_scale_pct = action.data()
            self._apply_scale()
            self._update_ui(self.snapshot)
            self.save_settings()

    def _apply_scale(self):
        scale = self.current_scale_pct
        if scale == 50:
            new_w, new_h = 140, 46
        elif scale == 75:
            new_w, new_h = 241, 51
        elif scale == 100:
            new_w, new_h = 330, 76
        elif scale == 125:
            new_w, new_h = 396, 86
        elif scale == 150:
            new_w, new_h = 216, 216
        else:
            new_w, new_h = 330, 76

        self.setMinimumSize(0, 0)
        self.setMaximumSize(16777215, 16777215)
        self.resize(new_w, new_h)
        self.setFixedSize(new_w, new_h)
        
        self._rebuild_card_layout(scale)

    def _apply_theme_style(self):
        # Resolve active theme settings config
        theme_code = self.current_theme_code
        if theme_code == "auto":
            # Autodetect from snapshot source app user model id
            aumid_lower = self.snapshot.aumid.lower()
            if "spotify" in aumid_lower:
                theme_code = "spotify_black"
            elif "youtube" in aumid_lower or "ytmusic" in aumid_lower:
                theme_code = "yt_black"
            else:
                # default fallback
                theme_code = "theme_1"

        status = (self.snapshot.status or "").lower()
        is_playing = "play" in status and "pause" not in status

        scale = self.current_scale_pct
        # Avoid redundant rendering and disc write operations
        if (theme_code == self.last_theme_code and 
            self.current_transparency_pct == self.last_transparency_pct and 
            is_playing == self.last_playing_status and
            getattr(self, "last_scale", None) == scale):
            return

        self.last_theme_code = theme_code
        self.last_transparency_pct = self.current_transparency_pct
        self.last_playing_status = is_playing
        self.last_scale = scale

        config = THEME_CONFIGS.get(theme_code, THEME_CONFIGS["theme_1"])
        
        # 1. Update source label and styling in QSS
        r, g, b = config["bg_color"]
        alpha = self.current_transparency_pct / 100.0
        bg_rgba = f"rgba({r}, {g}, {b}, {alpha})"
        
        is_light = config["light_theme"]
        border_color = "rgba(0, 0, 0, 0.06)" if is_light else "rgba(255, 255, 255, 0.08)"
        
        title_color = config["text_color"]
        artist_color = config["artist_color"]
        dot_color = config["dot_color"]
        icon_color = config["icon_color"]
        
        control_hover_bg = "rgba(0, 0, 0, 0.05)" if is_light else "rgba(255, 255, 255, 0.08)"
        control_pressed_bg = "rgba(0, 0, 0, 0.10)" if is_light else "rgba(255, 255, 255, 0.16)"
        
        # Get size configurations
        size_cfg = SIZE_CONFIGS.get(scale, SIZE_CONFIGS[100])
        
        play_radius = size_cfg["play_radius"]
        skip_radius = size_cfg["skip_radius"]
        title_font_size = size_cfg["title_size"]
        artist_font_size = size_cfg["artist_size"]
        status_font_size = size_cfg["status_size"]

        play_bg = config["play_bg"]
        play_fg = config["play_fg"]
        play_hover_bg = config["play_hover_bg"]
        
        # Build play button specific style sheet rules
        if play_bg is None:
            # Theme 1 outline circle
            play_style = f"""
                QToolButton#play_btn {{
                    background: transparent;
                    border: 1.5px solid {play_fg};
                    border-radius: {play_radius}px;
                }}
                QToolButton#play_btn:hover {{
                    background: rgba(255, 255, 255, 0.12);
                }}
                QToolButton#play_btn:pressed {{
                    background: rgba(255, 255, 255, 0.20);
                }}
            """
        else:
            # Solid color circle style
            play_style = f"""
                QToolButton#play_btn {{
                    background: {play_bg};
                    border: none;
                    border-radius: {play_radius}px;
                }}
                QToolButton#play_btn:hover {{
                    background: {play_hover_bg};
                }}
                QToolButton#play_btn:pressed {{
                    background: {play_fg};
                }}
            """

        self.setStyleSheet(f"""
            MusicWidget {{
                background: transparent;
                border: none;
            }}
            QLabel {{
                background: transparent;
                color: {title_color};
                font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            }}
            QFrame#card {{
                background: {bg_rgba};
                border: 1px solid transparent;
                border-radius: 1px;
            }}
            #title {{
                color: {title_color};
                font-size: {title_font_size}px;
                font-weight: 700;
            }}
            #artist {{
                color: {artist_color};
                font-size: {artist_font_size}px;
                font-weight: 500;
            }}
            #status_text {{
                color: {artist_color};
                font-size: {status_font_size}px;
                font-weight: 600;
            }}
            #status_dot {{
                background: {dot_color};
                border-radius: 4px;
            }}
            QToolButton#skip_btn {{
                background: transparent;
                border: none;
                border-radius: {skip_radius}px;
            }}
            QToolButton#skip_btn:hover {{
                background: {control_hover_bg};
            }}
            QToolButton#skip_btn:pressed {{
                background: {control_pressed_bg};
            }}
            QToolButton#min_btn {{
                background: transparent;
                border: none;
                border-radius: 4px;
            }}
            QToolButton#min_btn:hover {{
                background: {control_hover_bg};
            }}
            {play_style}
        """)

        # 2. Update icons dynamically colored based on theme
        self.prev_btn.setIcon(get_colored_icon("skip_previous", icon_color))
        self.next_btn.setIcon(get_colored_icon("skip_next", icon_color))
        self.min_btn.setIcon(get_colored_icon("down", icon_color))
        
        # Load play/pause button icon colored with play_fg (for solid circles) or icon_color
        p_color = play_fg if play_bg is not None else icon_color
        status = (self.snapshot.status or "").lower()
        if "play" in status and "pause" not in status:
            self.play_btn.setIcon(get_colored_icon("pause", p_color))
        else:
            self.play_btn.setIcon(get_colored_icon("play_arrow", p_color))

    def refresh_media(self):
        if hasattr(self, "worker"):
            self.worker.trigger_refresh()

    def _handle_snapshot(self, snap: Snapshot):
        if not isinstance(snap, Snapshot):
            return
        self.snapshot = snap
        self._update_ui(snap)

    def _update_ui(self, snap: Snapshot):
        self.title.setText(snap.title or "No music playing")
        self.artist.setText(snap.artist or "")
        
        # Format status text
        status_str = snap.status or "Stopped"
        if status_str == "Playing":
            status_str = "Playing"
        elif status_str == "Paused":
            status_str = "Paused"
            
        if self.current_scale_pct >= 125:
            source = get_friendly_source_name(snap.aumid, snap.artist)
            if source:
                status_str = f"{status_str} • {source}"
                
        self.status_text.setText(status_str)

        self.prev_btn.setEnabled(snap.can_prev)
        self.play_btn.setEnabled(snap.can_play or snap.can_pause)
        self.next_btn.setEnabled(snap.can_next)

        # Apply theme stylesheet (takes care of dynamic theme resolving and icon recoloring)
        self._apply_theme_style()

    def send_control(self, action: str):
        def run_control():
            import ctypes
            try:
                ctypes.windll.ole32.CoInitializeEx(None, 0)
            except Exception:
                pass
            try:
                ok = safe_run(send_control_async(action), False)
                if not ok:
                    QTimer.singleShot(0, lambda: self.tray.showMessage(
                        APP_NAME,
                        "Could not send media control to the current session.",
                        QSystemTrayIcon.MessageIcon.Warning,
                        1200,
                    ))
                else:
                    # Wake the worker immediately so UI reflects the new state
                    QTimer.singleShot(400, self.refresh_media)
            except Exception:
                pass
            finally:
                try:
                    ctypes.windll.ole32.CoUninitialize()
                except Exception:
                    pass
        threading.Thread(target=run_control, daemon=True).start()

    def toggle_always_on_top(self):
        self.always_on_top = not self.always_on_top
        self.always_on_top_action.setChecked(self.always_on_top)
        
        pos = self.pos()
        flags = self.windowFlags()
        if self.always_on_top:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        else:
            flags &= ~Qt.WindowType.WindowStaysOnTopHint

        self.setWindowFlags(flags)
        self.show()
        self.move(pos)
        self.save_settings()

    def _tray_activated(self, reason):
        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick,
        ):
            if self.isVisible():
                self.hide()
            else:
                self.show_from_tray()

    def hide_to_tray(self):
        self.hide()
        if self.tray.isVisible():
            self.tray.showMessage(
                APP_NAME,
                "Hidden to tray.",
                QSystemTrayIcon.MessageIcon.Information,
                800,
            )

    def show_from_tray(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def closeEvent(self, event):
        event.ignore()
        self.hide_to_tray()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()

    def _cleanup(self):
        self.save_settings()
        if hasattr(self, "worker"):
            self.worker.stop()
            # Wait up to 3 seconds; if still running, terminate forcibly so
            # the app always quits cleanly even if a WinRT call is stuck.
            if not self.worker.wait(3000):
                self.worker.terminate()
                self.worker.wait(1000)


def main():
    if sys.platform != "win32":
        print("This widget is for Windows.")
        return 1

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setQuitOnLastWindowClosed(False)
    # app.setWindowIcon(icon_for_app())
    # app.setWindowIcon(QIcon("PulseDock.ico"))
    APP_ICON = QIcon(resource_path("PulseDock.ico"))
    app.setWindowIcon(APP_ICON)

    if MediaManager is None:
        QMessageBox.critical(
            None,
            APP_NAME,
            "winsdk is not installed.\n\nInstall with:\n  pip install PyQt6 winsdk",
        )
        return 1

    widget = MusicWidget()
    widget.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
