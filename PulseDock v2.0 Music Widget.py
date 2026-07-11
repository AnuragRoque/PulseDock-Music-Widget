
from __future__ import annotations

import asyncio
import ctypes
import json
import os
import sys
import threading
import time
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Optional

from PyQt6.QtCore import (
    Qt,
    QTimer,
    QPoint,
    QRectF,
    QSize,
    QThread,
    pyqtSignal,
    QObject,
)
from PyQt6.QtGui import (
    QAction,
    QActionGroup,
    QIcon,
    QImage,
    QPainterPath,
    QPen,
    QPixmap,
    QPainter,
    QColor,
    QPolygon,
)
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

try:
    from winsdk.windows.storage.streams import (
        Buffer as WinBuffer,
        DataReader as WinDataReader,
        InputStreamOptions as WinInputStreamOptions,
    )
except Exception:
    WinBuffer = None
    WinDataReader = None
    WinInputStreamOptions = None


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
    artist: str = "Start YT Music / Spotify"
    status: str = "Stopped"
    can_play: bool = True
    can_pause: bool = True
    can_prev: bool = True
    can_next: bool = True
    aumid: str = ""
    thumb: bytes = b""
    pos_sec: float = -1.0   # current playback position; -1 = unknown
    dur_sec: float = -1.0   # track duration; -1 = unknown


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
        "card_radius": 12,
        "art_size": 38,
        "art_radius": 8,
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
        "card_radius": 14,
        "art_size": 35,
        "art_radius": 6,
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
        "card_radius": 16,
        "art_size": 52,
        "art_radius": 8,
        "vol_size": 16,
        "icon_vol": 11,
    },
    125: {  # Mini (M) - compact vertical card: art on top, text, controls
        "play_size": 32,
        "play_radius": 16,
        "skip_size": 26,
        "skip_radius": 13,
        "icon_play": 18,
        "icon_skip": 16,
        "title_size": 11,
        "artist_size": 9,
        "status_size": 8,
        "card_radius": 16,
        "art_size": 96,
        "art_radius": 10,
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
        "card_radius": 20,
        "art_size": 112,
        "art_radius": 12,
        "vol_size": 18,
        "icon_vol": 12,
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


_ICON_MEM_CACHE: dict = {}


def get_colored_icon(icon_name: str, color_hex: str) -> QIcon:
    # In-memory cache avoids rewriting the tinted SVG to disk on every call
    cache_key = (icon_name, color_hex)
    cached = _ICON_MEM_CACHE.get(cache_key)
    if cached is not None:
        return cached

    # svg_path = f"icons/{icon_name}.svg"
    svg_path = resource_path(f"icons/{icon_name}.svg")
    try:
        if not os.path.exists(svg_path):
            icon = QIcon()
            _ICON_MEM_CACHE[cache_key] = icon
            return icon
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
        icon = QIcon(temp_path)
    except Exception:
        icon = QIcon(svg_path)
    _ICON_MEM_CACHE[cache_key] = icon
    return icon


_VOLUME_ICON_CACHE: dict = {}


def make_volume_icon(state: str, color_hex: str) -> QIcon:
    """Speaker icon drawn in code ('high' | 'low' | 'off') — no SVG files needed."""
    cache_key = (state, color_hex)
    cached = _VOLUME_ICON_CACHE.get(cache_key)
    if cached is not None:
        return cached

    color = QColor(color_hex)
    icon = QIcon()
    for px in (16, 20, 24, 32, 48, 64):
        pm = QPixmap(px, px)
        pm.fill(Qt.GlobalColor.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        s = px / 64.0
        p.scale(s, s)

        # Speaker body (drawn on a 64x64 design grid)
        body = QPainterPath()
        body.moveTo(8, 24)
        body.lineTo(20, 24)
        body.lineTo(34, 10)
        body.lineTo(34, 54)
        body.lineTo(20, 40)
        body.lineTo(8, 40)
        body.closeSubpath()
        p.fillPath(body, color)

        pen = QPen(color, 5.5)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)

        if state == "off":
            # Small "x" next to the speaker
            p.drawLine(43, 25, 57, 39)
            p.drawLine(57, 25, 43, 39)
        else:
            p.drawArc(QRectF(31, 23, 18, 18), -50 * 16, 100 * 16)
            if state == "high":
                p.drawArc(QRectF(23, 15, 34, 34), -50 * 16, 100 * 16)
        p.end()
        icon.addPixmap(pm)

    _VOLUME_ICON_CACHE[cache_key] = icon
    return icon


def rounded_art_pixmap(data: bytes, width: int, height: int, radius: float, dpr: float = 1.0) -> QPixmap:
    """Decode album-art bytes into a rounded-corner pixmap of any aspect (HiDPI aware)."""
    src = QPixmap()
    if not data or not src.loadFromData(data):
        return QPixmap()

    w = max(1, int(round(width * dpr)))
    h = max(1, int(round(height * dpr)))
    scaled = src.scaled(
        w,
        h,
        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
        Qt.TransformationMode.SmoothTransformation,
    )
    # Center-crop to the target rect
    x = (scaled.width() - w) // 2
    y = (scaled.height() - h) // 2
    scaled = scaled.copy(x, y, w, h)

    out = QPixmap(w, h)
    out.fill(Qt.GlobalColor.transparent)
    p = QPainter(out)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    clip = QPainterPath()
    clip.addRoundedRect(QRectF(0, 0, w, h), radius * dpr, radius * dpr)
    p.setClipPath(clip)
    p.drawPixmap(0, 0, scaled)
    p.end()
    out.setDevicePixelRatio(dpr)
    return out


def make_art_placeholder(size: int, radius: float, theme_cfg: dict, dpr: float = 1.0) -> QPixmap:
    """Rounded placeholder tile with a music note, tinted for the active theme."""
    px = max(1, int(round(size * dpr)))
    pm = QPixmap(px, px)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    tile = QPainterPath()
    tile.addRoundedRect(QRectF(0, 0, px, px), radius * dpr, radius * dpr)
    bg = QColor(0, 0, 0, 24) if theme_cfg.get("light_theme") else QColor(255, 255, 255, 18)
    p.fillPath(tile, bg)

    note_color = QColor(theme_cfg.get("artist_color", "#888888"))
    note_color.setAlpha(160)

    # Double eighth-note (like a mini album icon) on a 64x64 design grid
    p.setClipPath(tile)
    scale = px / 64.0 * 0.6
    offset = px * 0.2
    p.translate(offset, offset)
    p.scale(scale, scale)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(note_color)
    p.drawRect(QRectF(20, 14, 28, 8))      # beam
    p.drawRect(QRectF(20, 14, 4.5, 30))    # left stem
    p.drawRect(QRectF(43.5, 14, 4.5, 34))  # right stem
    p.drawEllipse(QRectF(9, 38, 16, 11.5))     # left head
    p.drawEllipse(QRectF(32.5, 42, 16, 11.5))  # right head
    p.end()
    pm.setDevicePixelRatio(dpr)
    return pm


def art_accent_color(data: bytes) -> Optional[QColor]:
    """Pick a vibrant, representative color from album-art bytes.

    Downscales to 32x32, then votes across 12 hue buckets weighted by
    saturation and mid-range brightness so one colorful region wins over
    large dark/washed-out areas.
    """
    img = QImage.fromData(data)
    if img.isNull():
        return None
    img = img.scaled(
        32, 32,
        Qt.AspectRatioMode.IgnoreAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    ).convertToFormat(QImage.Format.Format_RGB32)

    buckets = [[0.0, 0.0, 0.0, 0.0] for _ in range(12)]  # weight, r, g, b
    total_r = total_g = total_b = 0
    for y in range(img.height()):
        for x in range(img.width()):
            c = img.pixelColor(x, y)
            total_r += c.red(); total_g += c.green(); total_b += c.blue()
            h, s, v = c.hueF(), c.saturationF(), c.valueF()
            if h < 0:  # achromatic
                continue
            w = s * (1.0 - abs(v - 0.6))
            if v < 0.15 or v > 0.97 or s < 0.20:
                w *= 0.05
            b = buckets[int(h * 12) % 12]
            b[0] += w
            b[1] += c.red() * w
            b[2] += c.green() * w
            b[3] += c.blue() * w

    best = max(buckets, key=lambda b: b[0])
    if best[0] > 1.0:
        return QColor(
            int(best[1] / best[0]),
            int(best[2] / best[0]),
            int(best[3] / best[0]),
        )
    # Mostly grayscale art: fall back to the average color
    n = img.width() * img.height()
    return QColor(total_r // n, total_g // n, total_b // n)


def blurred_bg_pixmap(data: bytes, width: int, height: int, radius: float,
                      opacity: float, dpr: float = 1.0) -> QPixmap:
    """Blurred + darkened album-art background for the card.

    The 'blur' is a cheap downscale-then-smooth-upscale, which needs no
    graphics scene and is plenty soft at card sizes.
    """
    src = QImage.fromData(data)
    if src.isNull():
        return QPixmap()

    w = max(1, int(round(width * dpr)))
    h = max(1, int(round(height * dpr)))

    tiny = src.scaled(12, 12, Qt.AspectRatioMode.IgnoreAspectRatio,
                      Qt.TransformationMode.SmoothTransformation)
    big = tiny.scaled(w, h, Qt.AspectRatioMode.IgnoreAspectRatio,
                      Qt.TransformationMode.SmoothTransformation)

    out = QPixmap(w, h)
    out.fill(Qt.GlobalColor.transparent)
    p = QPainter(out)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    clip = QPainterPath()
    clip.addRoundedRect(QRectF(0, 0, w, h), radius * dpr, radius * dpr)
    p.setClipPath(clip)
    p.setOpacity(max(0.0, min(1.0, opacity)))
    p.drawImage(0, 0, big)
    # Darken so light art stays readable behind white text
    p.fillRect(QRectF(0, 0, w, h), QColor(0, 0, 0, 140))
    p.end()
    out.setDevicePixelRatio(dpr)
    return out


def fmt_time(seconds: float) -> str:
    s = max(0, int(seconds))
    if s >= 3600:
        return f"{s // 3600}:{(s % 3600) // 60:02d}:{s % 60:02d}"
    return f"{s // 60}:{s % 60:02d}"


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


async def _read_thumbnail_async(props) -> bytes:
    """Read album-art bytes from the media properties thumbnail stream."""
    if WinBuffer is None or WinDataReader is None:
        return b""
    thumb_ref = getattr(props, "thumbnail", None)
    if thumb_ref is None:
        return b""
    stream = None
    try:
        stream = await thumb_ref.open_read_async()
        size = int(getattr(stream, "size", 0) or 0)
        cap = size if 0 < size <= 10_000_000 else 5_000_000
        buf = WinBuffer(cap)
        await stream.read_async(buf, cap, WinInputStreamOptions.READ_AHEAD)
        length = int(buf.length)
        if length <= 0:
            return b""
        try:
            # winsdk IBuffer implements the Python buffer protocol
            return bytes(memoryview(buf))
        except TypeError:
            # Older projections: DataReader with fill-array pattern
            reader = WinDataReader.from_buffer(buf)
            out = bytearray(length)
            reader.read_bytes(out)
            return bytes(out)
    except Exception:
        return b""
    finally:
        try:
            if stream is not None:
                stream.close()
        except Exception:
            pass


async def read_snapshot_async(thumb_cache: Optional[dict] = None) -> Snapshot:
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

        # Timeline (position / duration). Some apps update the timeline lazily
        # (Spotify only on seek/track change), so while playing we advance the
        # reported position by the time elapsed since its last_updated_time.
        pos_sec, dur_sec = -1.0, -1.0
        try:
            tl = session.get_timeline_properties()
            position = getattr(tl, "position", None)
            start = getattr(tl, "start_time", None)
            end = getattr(tl, "end_time", None)
            if position is not None and end is not None:
                start_s = start.total_seconds() if start is not None else 0.0
                dur_sec = end.total_seconds() - start_s
                pos_sec = position.total_seconds() - start_s
                is_playing = "play" in status.lower() and "pause" not in status.lower()
                last_updated = getattr(tl, "last_updated_time", None)
                if is_playing and last_updated is not None:
                    elapsed = (datetime.now(timezone.utc) - last_updated).total_seconds()
                    if 0 < elapsed < 24 * 3600:
                        pos_sec += elapsed
                if dur_sec > 0:
                    pos_sec = max(0.0, min(pos_sec, dur_sec))
                else:
                    pos_sec, dur_sec = -1.0, -1.0
        except Exception:
            pos_sec, dur_sec = -1.0, -1.0

        props = await session.try_get_media_properties_async()
        title = (getattr(props, "title", None) or "Unknown title").strip()
        artist = (getattr(props, "artist", None) or "Unknown artist").strip()
        aumid = getattr(session, "source_app_user_model_id", "")

        # Album art: only re-read the stream when the track changes (or while
        # art hasn't arrived yet) — not on every 1s poll.
        track_key = (title, artist, aumid)
        if (
            thumb_cache is not None
            and thumb_cache.get("key") == track_key
            and thumb_cache.get("data")
        ):
            thumb = thumb_cache["data"]
        else:
            thumb = await _read_thumbnail_async(props)
            if thumb_cache is not None:
                thumb_cache["key"] = track_key
                thumb_cache["data"] = thumb

        return Snapshot(
            title=title,
            artist=artist,
            status=status or "Unknown",
            can_play=bool(getattr(controls, "is_play_enabled", True)),
            can_pause=bool(getattr(controls, "is_pause_enabled", True)),
            can_prev=bool(getattr(controls, "is_previous_enabled", True)),
            can_next=bool(getattr(controls, "is_next_enabled", True)),
            aumid=aumid,
            thumb=thumb,
            pos_sec=pos_sec,
            dur_sec=dur_sec,
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


class _GUID(ctypes.Structure):
    _fields_ = [
        ("data1", ctypes.c_ulong),
        ("data2", ctypes.c_ushort),
        ("data3", ctypes.c_ushort),
        ("data4", ctypes.c_ubyte * 8),
    ]


def _guid(guid_str: str) -> _GUID:
    g = _GUID()
    ctypes.windll.ole32.CLSIDFromString(ctypes.c_wchar_p(guid_str), ctypes.byref(g))
    return g


def _com_call(ptr, vtbl_index: int, argtypes: tuple, *args):
    """Call a COM interface method by vtable index (raw ctypes, dependency-free)."""
    vtbl = ctypes.cast(ptr, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
    proto = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, *argtypes)
    return proto(vtbl[vtbl_index])(ptr, *args)


def _press_media_key(vk: int):
    """Fallback volume control: simulate the keyboard media keys."""
    try:
        ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
        ctypes.windll.user32.keybd_event(vk, 0, 2, 0)  # KEYEVENTF_KEYUP
    except Exception:
        pass


class SystemVolume:
    """Windows master volume + mute via Core Audio (IAudioEndpointVolume).

    Raw ctypes COM so no packages beyond PyQt6/winsdk are required.
    All calls must stay on one thread (used from the Qt GUI thread only).
    Vtable indices: 7 SetMasterVolumeLevelScalar, 9 GetMasterVolumeLevelScalar,
    14 SetMute, 15 GetMute.
    """

    _CLSID_ENUMERATOR = "{BCDE0395-E52F-467C-8E3D-C4579291692E}"  # MMDeviceEnumerator
    _IID_ENUMERATOR = "{A95664D2-9614-4F35-A746-DE8DB63617E6}"    # IMMDeviceEnumerator
    _IID_ENDPOINT_VOLUME = "{5CDF2C82-841E-4546-9722-0CF74078229A}"  # IAudioEndpointVolume

    def __init__(self):
        self._epv = None

    def _acquire(self) -> bool:
        if self._epv is not None:
            return True
        try:
            ole32 = ctypes.windll.ole32
            ole32.CoInitializeEx(None, 2)  # no-op if COM already initialized

            enum_ptr = ctypes.c_void_p()
            hr = ole32.CoCreateInstance(
                ctypes.byref(_guid(self._CLSID_ENUMERATOR)),
                None,
                23,  # CLSCTX_ALL
                ctypes.byref(_guid(self._IID_ENUMERATOR)),
                ctypes.byref(enum_ptr),
            )
            if hr != 0 or not enum_ptr.value:
                return False

            dev_ptr = ctypes.c_void_p()
            hr = _com_call(
                enum_ptr, 4,  # GetDefaultAudioEndpoint
                (ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_void_p)),
                0, 1, ctypes.byref(dev_ptr),  # eRender, eMultimedia
            )
            _com_call(enum_ptr, 2, ())  # Release enumerator
            if hr != 0 or not dev_ptr.value:
                return False

            epv_ptr = ctypes.c_void_p()
            iid = _guid(self._IID_ENDPOINT_VOLUME)
            hr = _com_call(
                dev_ptr, 3,  # IMMDevice::Activate
                (ctypes.POINTER(_GUID), ctypes.c_ulong, ctypes.c_void_p,
                 ctypes.POINTER(ctypes.c_void_p)),
                ctypes.byref(iid), 23, None, ctypes.byref(epv_ptr),
            )
            _com_call(dev_ptr, 2, ())  # Release device
            if hr != 0 or not epv_ptr.value:
                return False

            self._epv = epv_ptr
            return True
        except Exception:
            return False

    def _drop(self):
        """Release the interface so the next call re-binds (default device changed)."""
        if self._epv is not None:
            try:
                _com_call(self._epv, 2, ())
            except Exception:
                pass
            self._epv = None

    def get_volume(self) -> Optional[int]:
        for _ in range(2):
            if not self._acquire():
                return None
            val = ctypes.c_float()
            try:
                hr = _com_call(self._epv, 9, (ctypes.POINTER(ctypes.c_float),), ctypes.byref(val))
            except Exception:
                hr = -1
            if hr == 0:
                return int(round(val.value * 100))
            self._drop()
        return None

    def set_volume(self, pct: int) -> bool:
        level = max(0, min(100, int(pct))) / 100.0
        for _ in range(2):
            if not self._acquire():
                return False
            try:
                hr = _com_call(
                    self._epv, 7, (ctypes.c_float, ctypes.c_void_p),
                    ctypes.c_float(level), None,
                )
            except Exception:
                hr = -1
            if hr >= 0:
                return True
            self._drop()
        return False

    def get_mute(self) -> Optional[bool]:
        for _ in range(2):
            if not self._acquire():
                return None
            val = ctypes.c_int()
            try:
                hr = _com_call(self._epv, 15, (ctypes.POINTER(ctypes.c_int),), ctypes.byref(val))
            except Exception:
                hr = -1
            if hr == 0:
                return bool(val.value)
            self._drop()
        return None

    def set_mute(self, mute: bool) -> bool:
        for _ in range(2):
            if not self._acquire():
                return False
            try:
                hr = _com_call(
                    self._epv, 14, (ctypes.c_int, ctypes.c_void_p),
                    1 if mute else 0, None,
                )
            except Exception:
                hr = -1
            if hr >= 0:
                return True
            self._drop()
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
        self._marquee_enabled = True
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

    def set_marquee_enabled(self, enabled: bool):
        self._marquee_enabled = enabled
        if not enabled:
            self._timer.stop()
            self._delay_timer.stop()
            self._is_scrolling = False
            self._scroll_offset = 0.0
        self.update_geometry_and_scroll()
        self.update()

    def update_geometry_and_scroll(self):
        fm = self.fontMetrics()
        self._text_width = fm.horizontalAdvance(self.text())

        if self._marquee_enabled and self._text_width > self.width() and self.width() > 0:
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
            if self._text_width > self.width() > 0:
                # Not scrolling (marquee off or waiting): elide instead of clipping
                painter = QPainter(self)
                painter.setPen(self.palette().color(self.foregroundRole()))
                painter.setFont(self.font())
                fm = painter.fontMetrics()
                y = (self.height() - fm.height()) // 2 + fm.ascent()
                painter.drawText(0, y, fm.elidedText(self.text(), Qt.TextElideMode.ElideRight, self.width()))
                painter.end()
                return
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


class ProgressLine(QWidget):
    """Thin song-progress line painted along the card's bottom edge.

    Covers the whole card (mouse-transparent) and clips its painting to the
    card's rounded rect, so the line follows the corner curves and takes no
    layout space at all.
    """

    LINE_H = 3

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._fraction = 0.0
        self._radius = 14.0
        self._fill = QColor("#1DB954")
        self._track = QColor(255, 255, 255, 34)

    def set_style(self, fill: QColor, track: QColor, radius: float):
        self._fill = fill
        self._track = track
        self._radius = radius
        self.update()

    def set_fraction(self, fraction: float):
        fraction = max(0.0, min(1.0, fraction))
        if abs(fraction - self._fraction) < 0.001:
            return
        self._fraction = fraction
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        clip = QPainterPath()
        clip.addRoundedRect(QRectF(self.rect()), self._radius, self._radius)
        p.setClipPath(clip)
        y = self.height() - self.LINE_H
        p.fillRect(QRectF(0, y, self.width(), self.LINE_H), self._track)
        p.fillRect(QRectF(0, y, self.width() * self._fraction, self.LINE_H), self._fill)
        p.end()


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
        # Per-track album-art cache so the thumbnail stream is not re-read every poll
        self._thumb_cache: dict = {}

    def run(self):
        import ctypes
        try:
            ctypes.windll.ole32.CoInitializeEx(None, 0)
        except Exception:
            pass

        while self._running:
            try:
                snap = asyncio.run(read_snapshot_async(self._thumb_cache))
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
        self.art_bg_enabled = self.settings.get("art_bg", False)
        self.show_progress = self.settings.get("show_progress", True)
        self.marquee_enabled = self.settings.get("marquee", True)

        # System volume control + album art state
        self.sys_volume = SystemVolume()
        self._wheel_accum = 0
        self._vol_icon_key = None
        self._vol_flash_active = False
        self._current_icon_color = "#FFFFFF"
        self._last_thumb_data = None
        self._last_art_sig = None
        # XS mode: prev/next buttons only appear while hovering the card
        self._hovering = False
        # Art-derived dynamic theme + blurred-background caches
        self._auto_theme_cache: dict = {}
        self._last_bg_sig = None
        # Progress interpolation between 1s worker polls
        self._pos_base = -1.0
        self._pos_ts = time.monotonic()

        self._progress_timer = QTimer(self)
        self._progress_timer.timeout.connect(self._tick_progress)
        self._progress_timer.start(500)

        self._vol_flash_timer = QTimer(self)
        self._vol_flash_timer.setSingleShot(True)
        self._vol_flash_timer.timeout.connect(self._end_volume_flash)

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
            "art_bg": False,
            "show_progress": True,
            "marquee": True,
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
            "art_bg": self.art_bg_enabled,
            "show_progress": self.show_progress,
            "marquee": self.marquee_enabled,
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

        # Blurred album-art background (created first = bottom of z-order)
        self.bg_label = QLabel(self.card)
        self.bg_label.setObjectName("card_bg")
        self.bg_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.bg_label.hide()

        # Album art (shown in Normal / Wide / Large modes)
        self.art_label = QLabel(self.card)
        self.art_label.setObjectName("art")
        self.art_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Initialize labels as children of self.card
        self.title = MarqueeLabel("No music playing", self.card)
        self.title.setObjectName("title")
        self.title.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.artist = MarqueeLabel("Start YT Music / Spotify", self.card)
        self.artist.setObjectName("artist")
        self.artist.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.status_dot = QLabel(self.card)
        self.status_dot.setObjectName("status_dot")
        self.status_dot.setFixedSize(8, 8)

        self.status_text = QLabel("Stopped", self.card)
        self.status_text.setObjectName("status_text")

        # "1:23 / 3:45" — Large mode only
        self.time_label = QLabel("", self.card)
        self.time_label.setObjectName("time_text")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.hide()

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

        # Volume / mute button (click = mute toggle, wheel anywhere = volume)
        self.vol_btn = QToolButton(self.card)
        self.vol_btn.setObjectName("vol_btn")
        self.vol_btn.clicked.connect(self.toggle_mute)
        self.vol_btn.setToolTip("Click: mute / unmute • Scroll: volume")

        # Transient "Volume 45%" pill for XS/S modes (no status line there)
        self.vol_overlay = QLabel(self.card)
        self.vol_overlay.setObjectName("vol_overlay")
        self.vol_overlay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.vol_overlay.hide()

        # Subtle absolute-positioned minimize button in top-right of the card
        self.min_btn = QToolButton(self.card)
        self.min_btn.setObjectName("min_btn")
        self.min_btn.clicked.connect(self.hide_to_tray)

        # Song-progress line along the card's bottom edge (absolute overlay)
        self.progress_line = ProgressLine(self.card)
        self.progress_line.hide()

        self.title.set_marquee_enabled(self.marquee_enabled)
        self.artist.set_marquee_enabled(self.marquee_enabled)

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

        # Album art + volume button dimensions (Normal / Wide / Large only)
        art_size = size_cfg.get("art_size", 0)
        if art_size:
            self.art_label.setFixedSize(art_size, art_size)
        vol_size = size_cfg.get("vol_size", 0)
        if vol_size:
            self.vol_btn.setFixedSize(vol_size, vol_size)
            self.vol_btn.setIconSize(QSize(size_cfg["icon_vol"], size_cfg["icon_vol"]))
        
        # Configure minimize button
        if scale == 50:
            self.min_btn.hide()
        elif scale in (75, 125):
            self.min_btn.show()
            self.min_btn.setFixedSize(14, 14)
            self.min_btn.setIconSize(QSize(7, 7))
        elif scale == 100:
            self.min_btn.show()
            self.min_btn.setFixedSize(16, 16)
            self.min_btn.setIconSize(QSize(8, 8))
        else: # 150
            self.min_btn.show()
            self.min_btn.setFixedSize(18, 18)
            self.min_btn.setIconSize(QSize(9, 9))

        # Reset text alignments (Mini and Large center their text)
        if scale not in (125, 150):
            self.title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.artist.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.status_text.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        # 3. Create the appropriate layout based on size mode
        if scale == 50:  # Extra Small (XS) - art tile + title/artist; hover swaps to the 3 buttons
            self.status_dot.hide()
            self.status_text.hide()
            self.time_label.hide()
            self.vol_btn.hide()

            text_col = QVBoxLayout()
            text_col.setSpacing(0)
            text_col.setContentsMargins(0, 0, 0, 0)
            text_col.setAlignment(Qt.AlignmentFlag.AlignVCenter)
            text_col.addWidget(self.title)
            text_col.addWidget(self.artist)

            # The text column gets a huge stretch factor so the surrounding
            # stretch items take no space while it's visible; once hover hides
            # art + text, those stretches center the three buttons on the card.
            layout = QHBoxLayout(self.card)
            layout.setContentsMargins(4, 4, 10, 4)
            layout.setSpacing(8)
            layout.addWidget(self.art_label, 0)
            layout.addLayout(text_col, 100)
            layout.addStretch(1)
            layout.addWidget(self.prev_btn)
            layout.addWidget(self.play_btn)
            layout.addWidget(self.next_btn)
            layout.addStretch(1)

            self._set_xs_hover(self._hovering)

        elif scale == 75:  # Small (S) - Art tile + Title/Artist, media buttons centered
            self.title.show()
            self.artist.show()
            self.status_dot.hide()
            self.status_text.hide()
            self.time_label.hide()
            self.art_label.show()
            self.vol_btn.hide()

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
            layout.setSpacing(10)
            layout.addWidget(self.art_label, 0)
            layout.addLayout(left_layout, 1)
            layout.addLayout(right_layout, 0)
            
        elif scale == 100:  # Normal (N) - Art + full horizontal details
            self.title.show()
            self.artist.show()
            self.status_dot.show()
            self.status_text.show()
            self.time_label.hide()
            self.art_label.show()
            self.vol_btn.show()

            self.prev_btn.show()
            self.play_btn.show()
            self.next_btn.show()

            left_layout = QVBoxLayout()
            left_layout.setSpacing(2)
            left_layout.setContentsMargins(0, 0, 0, 0)
            left_layout.addWidget(self.title)
            left_layout.addWidget(self.artist)

            # Volume button lives at the end of the status line; the stretch
            # keeps it pinned so it doesn't shift while the text changes.
            status_layout = QHBoxLayout()
            status_layout.setSpacing(6)
            status_layout.setContentsMargins(0, 0, 0, 0)
            status_layout.addWidget(self.status_dot)
            status_layout.addWidget(self.status_text)
            status_layout.addStretch(1)
            status_layout.addWidget(self.vol_btn)
            left_layout.addLayout(status_layout)

            right_layout = QHBoxLayout()
            right_layout.setSpacing(6)
            right_layout.setContentsMargins(0, 0, 0, 0)
            right_layout.addWidget(self.prev_btn)
            right_layout.addWidget(self.play_btn)
            right_layout.addWidget(self.next_btn)

            layout = QHBoxLayout(self.card)
            # Left margin matches the vertical margins so the art tile sits flush
            layout.setContentsMargins(12, 12, 14, 12)
            layout.setSpacing(10)
            layout.addWidget(self.art_label, 0)
            layout.addLayout(left_layout, 1)
            layout.addLayout(right_layout, 0)

        elif scale == 125:  # Mini (M) - narrow vertical card: art, text, controls
            self.title.show()
            self.artist.show()
            self.status_dot.hide()
            self.status_text.hide()
            self.time_label.hide()
            self.art_label.show()
            self.vol_btn.hide()

            self.prev_btn.show()
            self.play_btn.show()
            self.next_btn.show()

            self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.artist.setAlignment(Qt.AlignmentFlag.AlignCenter)

            layout = QVBoxLayout(self.card)
            layout.setContentsMargins(8, 8, 8, 8)
            layout.setSpacing(0)

            art_row = QHBoxLayout()
            art_row.setSpacing(0)
            art_row.setContentsMargins(0, 0, 0, 0)
            art_row.addStretch(1)
            art_row.addWidget(self.art_label)
            art_row.addStretch(1)
            layout.addLayout(art_row)

            layout.addSpacing(4)
            layout.addWidget(self.title)
            layout.addWidget(self.artist)
            layout.addStretch(1)

            controls_layout = QHBoxLayout()
            controls_layout.setSpacing(10)
            controls_layout.setContentsMargins(0, 0, 0, 0)
            controls_layout.addStretch(1)
            controls_layout.addWidget(self.prev_btn)
            controls_layout.addWidget(self.play_btn)
            controls_layout.addWidget(self.next_btn)
            controls_layout.addStretch(1)
            layout.addLayout(controls_layout)

        elif scale == 150:  # Large (L) - Vertical card with big art on top
            self.title.show()
            self.artist.show()
            self.status_dot.show()
            self.status_text.show()
            self.art_label.show()
            self.vol_btn.show()

            self.prev_btn.show()
            self.play_btn.show()
            self.next_btn.show()

            # Center-align texts for Square mode
            self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.artist.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.status_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

            layout = QVBoxLayout(self.card)
            layout.setContentsMargins(16, 12, 16, 12)
            layout.setSpacing(4)

            art_row = QHBoxLayout()
            art_row.setSpacing(0)
            art_row.setContentsMargins(0, 0, 0, 0)
            art_row.addStretch(1)
            art_row.addWidget(self.art_label)
            art_row.addStretch(1)
            layout.addLayout(art_row)

            layout.addWidget(self.title)
            layout.addWidget(self.artist)

            # Volume button sits right after the playback status, centered group
            status_layout = QHBoxLayout()
            status_layout.setSpacing(6)
            status_layout.setContentsMargins(0, 0, 0, 0)
            status_layout.addStretch(1)
            status_layout.addWidget(self.status_dot)
            status_layout.addWidget(self.status_text)
            status_layout.addWidget(self.vol_btn)
            status_layout.addStretch(1)
            layout.addLayout(status_layout)

            layout.addStretch(1)

            # Elapsed / total time just above the controls
            layout.addWidget(self.time_label)

            # Symmetric triplet exactly like v1
            controls_layout = QHBoxLayout()
            controls_layout.setSpacing(14)
            controls_layout.setContentsMargins(0, 0, 0, 0)
            controls_layout.addStretch(1)
            controls_layout.addWidget(self.prev_btn)
            controls_layout.addWidget(self.play_btn)
            controls_layout.addWidget(self.next_btn)
            controls_layout.addStretch(1)
            layout.addLayout(controls_layout)

        # Keep the absolute overlays in the right stacking order after every
        # rebuild: blurred art background at the very bottom, progress on top.
        self.bg_label.lower()
        self.progress_line.raise_()
        self._tick_progress()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        
        # Absolute overlays track the card size (card fills the window)
        if hasattr(self, "progress_line"):
            self.progress_line.setGeometry(0, 0, self.width(), self.height())
        if hasattr(self, "bg_label"):
            # Inset 1px so the card's QSS border stays visible around the art
            self.bg_label.setGeometry(1, 1, self.width() - 2, self.height() - 2)

        scale = self.current_scale_pct
        if scale == 50:
            self.min_btn.hide()
            return

        btn_w = 14 if scale in (75, 125) else (18 if scale == 150 else 16)
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

        # Album art as blurred card background (also themes from the art)
        self.art_bg_action = QAction("Album Art Background", self, checkable=True)
        self.art_bg_action.setChecked(self.art_bg_enabled)
        self.art_bg_action.triggered.connect(self.toggle_art_bg)
        menu.addAction(self.art_bg_action)

        self.progress_action = QAction("Show Progress Bar", self, checkable=True)
        self.progress_action.setChecked(self.show_progress)
        self.progress_action.triggered.connect(self.toggle_progress)
        menu.addAction(self.progress_action)

        self.marquee_action = QAction("Scrolling Song Text", self, checkable=True)
        self.marquee_action.setChecked(self.marquee_enabled)
        self.marquee_action.triggered.connect(self.toggle_marquee)
        menu.addAction(self.marquee_action)

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
            ("Mini Card (M)", 125),
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

        # Same menu serves the tray icon and right-click on the widget itself
        self.context_menu = menu
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._tray_activated)
        self.tray.show()

    def contextMenuEvent(self, event):
        self.context_menu.exec(event.globalPos())

    def toggle_art_bg(self):
        self.art_bg_enabled = self.art_bg_action.isChecked()
        # Force a restyle: the art-derived theme depends on this flag
        self.last_theme_code = None
        self._last_art_sig = None
        self._apply_theme_style()
        self._update_card_bg()
        self.save_settings()

    def toggle_progress(self):
        self.show_progress = self.progress_action.isChecked()
        self._tick_progress()
        self.save_settings()

    def toggle_marquee(self):
        self.marquee_enabled = self.marquee_action.isChecked()
        self.title.set_marquee_enabled(self.marquee_enabled)
        self.artist.set_marquee_enabled(self.marquee_enabled)
        self.save_settings()

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
            new_w, new_h = 140, 178  # Mini: vertical card as narrow as XS
        elif scale == 150:
            new_w, new_h = 216, 292  # taller for big album art on top
        else:
            new_w, new_h = 330, 76

        self.setMinimumSize(0, 0)
        self.setMaximumSize(16777215, 16777215)
        self.resize(new_w, new_h)
        self.setFixedSize(new_w, new_h)
        
        self._rebuild_card_layout(scale)

    def _theme_from_art(self, thumb: bytes) -> Optional[tuple]:
        """Build (and cache) a dark theme config from the album art's colors."""
        key = hash(thumb)
        cached = self._auto_theme_cache.get(key)
        if cached is not None:
            return key, cached

        accent = art_accent_color(thumb)
        if accent is None:
            return None

        h, s, v = accent.hueF(), accent.saturationF(), accent.valueF()
        if h < 0:
            h, s = 0.0, 0.0
        chromatic = s > 0.08
        accent = QColor.fromHsvF(
            h,
            min(1.0, max(s, 0.45)) if chromatic else s,
            min(0.92, max(v, 0.55)),
        )
        hover = QColor.fromHsvF(h, accent.saturationF(), min(1.0, accent.valueF() + 0.08))
        bg = QColor.fromHsvF(h, s * 0.5 if chromatic else 0.0, 0.13)
        artist_col = QColor.fromHsvF(h, 0.12 if chromatic else 0.0, 0.78)
        luminance = 0.299 * accent.red() + 0.587 * accent.green() + 0.114 * accent.blue()

        config = {
            "name": "Auto (Album Art)",
            "bg_color": (bg.red(), bg.green(), bg.blue()),
            "text_color": "#FFFFFF",
            "artist_color": artist_col.name(),
            "dot_color": accent.name(),
            "icon_color": "#FFFFFF",
            "play_bg": accent.name(),
            "play_hover_bg": hover.name(),
            "play_fg": "#111111" if luminance > 160 else "#FFFFFF",
            "light_theme": False,
        }
        if len(self._auto_theme_cache) > 12:
            self._auto_theme_cache.clear()
        self._auto_theme_cache[key] = config
        return key, config

    def _apply_theme_style(self):
        # Resolve active theme settings config.
        # "Auto (Dynamic)" and the art-background toggle both derive the theme
        # from the current album art; without art, Auto falls back to a preset
        # matching the source app.
        theme_code = self.current_theme_code
        config = None
        if (theme_code == "auto" or self.art_bg_enabled) and self.snapshot.thumb:
            derived = self._theme_from_art(self.snapshot.thumb)
            if derived is not None:
                art_key, config = derived
                theme_code = f"art:{art_key}"
        if config is None and theme_code == "auto":
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

        if config is None:
            config = THEME_CONFIGS.get(theme_code, THEME_CONFIGS["theme_1"])
        self._active_theme_config = config
        
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
        vol_radius = size_cfg.get("vol_size", 24) // 2
        card_radius = size_cfg.get("card_radius", 14)
        overlay_bg = "rgba(255, 255, 255, 0.92)" if is_light else "rgba(25, 25, 25, 0.88)"

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
                border: 1px solid {border_color};
                border-radius: {card_radius}px;
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
            #time_text {{
                color: {artist_color};
                font-size: {status_font_size}px;
                font-weight: 500;
            }}
            #status_dot {{
                background: {dot_color};
                border-radius: 4px;
            }}
            QLabel#vol_overlay {{
                background: {overlay_bg};
                color: {title_color};
                border-radius: 10px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: 600;
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
            QToolButton#vol_btn {{
                background: transparent;
                border: none;
                border-radius: {vol_radius}px;
            }}
            QToolButton#vol_btn:hover {{
                background: {control_hover_bg};
            }}
            QToolButton#vol_btn:pressed {{
                background: {control_pressed_bg};
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

        # 3. Volume icon + album-art placeholder follow the theme colors
        self._current_icon_color = icon_color
        self._update_volume_icon(force=True)
        self._update_art()

        # 4. Progress line follows the theme accent
        fill = QColor(dot_color)
        track = QColor(0, 0, 0, 26) if is_light else QColor(255, 255, 255, 30)
        self.progress_line.set_style(fill, track, card_radius)

    def refresh_media(self):
        if hasattr(self, "worker"):
            self.worker.trigger_refresh()

    def _handle_snapshot(self, snap: Snapshot):
        if not isinstance(snap, Snapshot):
            return
        self.snapshot = snap
        # Re-anchor progress interpolation on every poll
        self._pos_base = snap.pos_sec
        self._pos_ts = time.monotonic()
        self._update_ui(snap)
        self._tick_progress()

    def _tick_progress(self):
        """Advance the progress line (and Large-mode times) between polls."""
        scale = self.current_scale_pct
        dur = self.snapshot.dur_sec
        show = (
            self.show_progress
            and scale != 50
            and dur is not None and dur > 0
            and self._pos_base >= 0
        )
        if not show:
            self.progress_line.hide()
            self.time_label.setText("")
            if scale == 150:
                self.time_label.hide()
            return

        status = (self.snapshot.status or "").lower()
        playing = "play" in status and "pause" not in status
        pos = self._pos_base + ((time.monotonic() - self._pos_ts) if playing else 0.0)
        pos = max(0.0, min(pos, dur))

        self.progress_line.setGeometry(0, 0, self.width(), self.height())
        self.progress_line.set_fraction(pos / dur)
        self.progress_line.show()
        if scale == 150:
            self.time_label.setText(f"{fmt_time(pos)} / {fmt_time(dur)}")
            self.time_label.show()

    def _update_card_bg(self):
        thumb = self.snapshot.thumb or b""
        if not (self.art_bg_enabled and thumb):
            if self._last_bg_sig is not None:
                self._last_bg_sig = None
                self.bg_label.clear()
            self.bg_label.hide()
            return
        w, h = self.width() - 2, self.height() - 2
        if w <= 0 or h <= 0:
            return
        size_cfg = SIZE_CONFIGS.get(self.current_scale_pct, SIZE_CONFIGS[100])
        radius = max(0.0, size_cfg.get("card_radius", 14) - 1)
        alpha = self.current_transparency_pct / 100.0
        sig = (w, h, radius, alpha, len(thumb), hash(thumb))
        if sig == self._last_bg_sig:
            self.bg_label.show()
            return
        pm = blurred_bg_pixmap(thumb, w, h, radius, alpha, self.devicePixelRatioF())
        if pm.isNull():
            self.bg_label.hide()
            return
        self.bg_label.setPixmap(pm)
        self.bg_label.setGeometry(1, 1, w, h)
        self.bg_label.show()
        self.bg_label.lower()
        self._last_bg_sig = sig

    def _update_ui(self, snap: Snapshot):
        self.title.setText(snap.title or "No music playing")
        self.artist.setText(snap.artist or "")
        
        # Format status text
        status_str = snap.status or "Stopped"
        if status_str == "Playing":
            status_str = "Playing"
        elif status_str == "Paused":
            status_str = "Paused"
            
        if self.current_scale_pct == 150:
            source = get_friendly_source_name(snap.aumid, snap.artist)
            if source:
                status_str = f"{status_str} • {source}"

        # Don't overwrite a transient "Volume 45%" flash
        if not self._vol_flash_active:
            self.status_text.setText(status_str)

        self.prev_btn.setEnabled(snap.can_prev)
        self.play_btn.setEnabled(snap.can_play or snap.can_pause)
        self.next_btn.setEnabled(snap.can_next)

        # Apply theme stylesheet (takes care of dynamic theme resolving and icon recoloring)
        self._apply_theme_style()

        # Album art + volume state follow every snapshot (both are cached internally)
        self._update_art()
        self._update_volume_icon()

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

    def enterEvent(self, event):
        super().enterEvent(event)
        self._hovering = True
        self._set_xs_hover(True)

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self._hovering = False
        self._set_xs_hover(False)

    def _set_xs_hover(self, hovering: bool):
        # XS only: art + title/artist at rest, the three buttons while hovering
        if self.current_scale_pct != 50:
            return
        # Rest state keeps extra right padding for the text; hovering equalizes
        # the margins and zeroes the text column's stretch (a nested layout
        # can't be hidden, so its stretch factor would otherwise keep eating
        # the free space) so the button triplet is perfectly centered.
        layout = self.card.layout()
        if layout is not None:
            layout.setContentsMargins(4, 4, 4 if hovering else 10, 4)
            layout.setStretch(1, 0 if hovering else 100)
        self.art_label.setVisible(not hovering)
        self.title.setVisible(not hovering)
        self.artist.setVisible(not hovering)
        self.prev_btn.setVisible(hovering)
        self.play_btn.setVisible(hovering)
        self.next_btn.setVisible(hovering)

    def wheelEvent(self, event):
        # Mouse wheel anywhere on the widget adjusts the system volume.
        delta = event.angleDelta().y() or event.angleDelta().x()
        if not delta:
            event.ignore()
            return
        # Accumulate so smooth-scrolling touchpads (small deltas) work too
        self._wheel_accum += delta
        steps = int(self._wheel_accum / 120)
        if steps:
            self._wheel_accum -= steps * 120
            self.adjust_volume(steps * 5)  # 5% per wheel notch
        event.accept()

    def adjust_volume(self, delta_pct: int):
        vol = self.sys_volume.get_volume()
        if vol is None:
            # COM unavailable — fall back to media volume keys (2% per press)
            vk = 0xAF if delta_pct > 0 else 0xAE  # VK_VOLUME_UP / VK_VOLUME_DOWN
            for _ in range(min(8, max(1, abs(delta_pct) // 2))):
                _press_media_key(vk)
            self._show_volume_feedback("Volume +" if delta_pct > 0 else "Volume −")
            return
        new_vol = max(0, min(100, vol + delta_pct))
        self.sys_volume.set_volume(new_vol)
        # Scrolling up while muted should be audible again
        if new_vol > 0 and delta_pct > 0 and self.sys_volume.get_mute():
            self.sys_volume.set_mute(False)
        self._update_volume_icon()
        self._show_volume_feedback(f"Volume {new_vol}%")

    def toggle_mute(self):
        muted = self.sys_volume.get_mute()
        if muted is None:
            _press_media_key(0xAD)  # VK_VOLUME_MUTE
            self._show_volume_feedback("Mute toggled")
            return
        self.sys_volume.set_mute(not muted)
        self._update_volume_icon()
        if not muted:
            self._show_volume_feedback("Muted")
        else:
            vol = self.sys_volume.get_volume()
            self._show_volume_feedback(
                f"Volume {vol}%" if vol is not None else "Unmuted"
            )

    def _show_volume_feedback(self, text: str):
        self._vol_flash_active = True
        if self.status_text.isVisibleTo(self.card):
            # Status line exists (Normal / Wide / Large): update the number
            # in place — one steady line, no popup re-drawing on every notch.
            self.status_text.setText(text)
        else:
            # XS / S have no status line: one small centered pill whose text
            # updates while scrolling.
            self.vol_overlay.setText(text)
            self.vol_overlay.adjustSize()
            self.vol_overlay.move(
                (self.card.width() - self.vol_overlay.width()) // 2,
                (self.card.height() - self.vol_overlay.height()) // 2,
            )
            self.vol_overlay.show()
            self.vol_overlay.raise_()
        self._vol_flash_timer.start(1200)

    def _end_volume_flash(self):
        self._vol_flash_active = False
        self.vol_overlay.hide()
        self._update_ui(self.snapshot)

    def _update_volume_icon(self, force: bool = False):
        # Only Normal and Large show the volume button (Mini has no room)
        if self.current_scale_pct not in (100, 150):
            return
        vol = self.sys_volume.get_volume()
        muted = self.sys_volume.get_mute()
        if muted or (vol is not None and vol <= 0):
            state = "off"
        elif vol is not None and vol < 50:
            state = "low"
        else:
            state = "high"
        key = (state, self._current_icon_color)
        if force or key != self._vol_icon_key:
            self._vol_icon_key = key
            self.vol_btn.setIcon(make_volume_icon(state, self._current_icon_color))
        if vol is None:
            tip = "Click: mute / unmute • Scroll: volume"
        else:
            tip = f"Volume {vol}%{' (muted)' if muted else ''} • Click: mute • Scroll: adjust"
        self.vol_btn.setToolTip(tip)

    def _update_art(self):
        scale = self.current_scale_pct
        size_cfg = SIZE_CONFIGS.get(scale, SIZE_CONFIGS[100])
        thumb = self.snapshot.thumb or b""
        dpr = self.devicePixelRatioF()

        # Blurred card background keeps its own signature cache
        self._update_card_bg()

        art_size = size_cfg.get("art_size", 0)
        if not art_size:
            return
        radius = size_cfg.get("art_radius", 8)
        theme_code = self.last_theme_code or "theme_1"
        sig = (art_size, radius, theme_code, len(thumb))
        if thumb == self._last_thumb_data and sig == self._last_art_sig:
            return
        pm = rounded_art_pixmap(thumb, art_size, art_size, radius, dpr) if thumb else QPixmap()
        if pm.isNull():
            theme_cfg = (
                getattr(self, "_active_theme_config", None)
                or THEME_CONFIGS.get(theme_code, THEME_CONFIGS["theme_1"])
            )
            pm = make_art_placeholder(art_size, radius, theme_cfg, dpr)
        self.art_label.setPixmap(pm)
        self._last_thumb_data = thumb
        self._last_art_sig = sig

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
