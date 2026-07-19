# PulseDock Widget 🎵

PulseDock is a sleek, frameless, always-on-top floating media controller for Windows 11. It hooks straight into the Windows Global System Media Transport Controls (SMTC) to show real-time playback info — title, artist, album art, progress — and control any active media player: Spotify, YouTube Music, VLC, Edge, Chrome, and more.

Built with **PyQt6** and the **Windows SDK (`winsdk`)**, it's lightweight, adaptive, and themes itself to whatever you're listening to.

<p align="center">
  <img src="sample%20images/v2/01_normal_auto.png" alt="PulseDock Widget — Normal mode with album art" width="520">
</p>

<p align="center">
  <img src="sample%20images/v2/island_expand.gif" alt="Dynamic Island — expands on track change, then collapses" width="620"><br>
  <sub>🏝️ <b>Dynamic Island mode</b> — the pill expands when the track changes, then melts back down.</sub>
</p>

---

## ✨ Features

- **Direct Windows SMTC Integration** — Reads media metadata (title, artist, source app) and sends Play/Pause/Next/Previous asynchronously, without ever blocking the UI.
- **🏝️ Dynamic Island (v2.0)** — iPhone-style island that docks to the top of your screen (or floats anywhere). Rests as a compact pill — or a bare circular album-art "Drop" — and smoothly expands to full controls on hover or track change, then auto-collapses.
- **Album Art Everywhere (v2.0)** — Cover art with rounded corners in every layout, fetched straight from the media session and cached per track. Optional **High-Res Album Art (Online)** lookup and an **Album Art Background** mode that blurs the cover into the card itself.
- **Live Progress Bar (v2.0)** — A slim accent-colored progress line tracks the song position along the bottom edge of the card.
- **Scrolling Song Text (v2.0)** — Long titles marquee smoothly instead of truncating.
- **Volume & Mute (v2.0)** — Scroll the mouse wheel anywhere on the widget to change system volume (5% per notch, touchpad friendly); click the speaker to mute/unmute. Implemented with raw Core Audio COM — zero extra dependencies.
- **Dynamic Auto-Theme** — Matches the active player's brand style (Spotify green, YouTube Music red, …) or derives an accent palette straight from the album art. Manual themes included.
- **7 Size Modes** — Drop (art only), Extra Small, Small, Normal, Mini Card, Large, plus the two Dynamic Island modes.
- **Desktop-Native Behavior** — Always on Top, Pin to Active Window, Auto-Hide on Fullscreen (games/videos/slides), Launch on Startup, adjustable transparency (20–100%).
- **Settings Persistence** — Position, size, theme, transparency and every toggle saved atomically under `%LocalAppData%\PulseDock Widget\settings.json`.
- **System Tray Control Center** — Everything is two clicks away from the tray icon.

---

## 📐 Size Modes

| Large (Mini-Player) | Mini Card | Normal |
|:---:|:---:|:---:|
| <img src="sample%20images/v2/02_large.png" width="230"> | <img src="sample%20images/v2/03_mini_card.png" width="240"> | <img src="sample%20images/v2/01_normal_auto.png" width="380"> |

| Small | Extra Small | Drop (Art Only) |
|:---:|:---:|:---:|
| <img src="sample%20images/v2/04_small.png" width="330"> | <img src="sample%20images/v2/05_xs.png" width="240"> | <img src="sample%20images/v2/06_drop.png" width="150"> |

**Large** is a full vertical mini-player: big cover, source app, elapsed/total time. **Drop** is a single floating circle of album art — the most minimal player you'll ever run.

---

## 🏝️ Dynamic Island

Two island modes, straight from the tray menu:

- **Dynamic Island (Top)** — docks to the top-center of your screen like a notch companion.
- **Dynamic Island (Floating)** — same behavior, parked wherever you drop it.

Pick the **idle size** (Drop / XS / Small) and the **expanded size** (Normal / Mini Card). The island expands on hover or when the song changes, shows full controls for a moment, and collapses back on its own.

<p align="center">
  <img src="sample%20images/v2/11_island_top.png" alt="Island idle pill docked at top of screen" width="400"><br>
  <sub>Idle pill docked at the top — title marquees while it rests.</sub>
</p>

---

## 🎨 Themes

**Auto (Dynamic)** detects the active player and matches its brand colors — or builds a palette from the album art itself. Prefer a fixed look? Pick one:

| Midnight Drive | Daylight |
|:---:|:---:|
| <img src="sample%20images/v2/07_theme_midnight.png" width="380"> | <img src="sample%20images/v2/08_theme_daylight.png" width="380"> |

| Coffee & Cigarettes | Spotify Black |
|:---:|:---:|
| <img src="sample%20images/v2/09_theme_coffee.png" width="380"> | <img src="sample%20images/v2/10_theme_spotify.png" width="380"> |

Also included: **Spotify White**, **YouTube Music Black**, **YouTube Music White**.

---

## ⚙️ Tray Control Center

Right-click the PulseDock tray icon for every setting — no config files to touch:

<p align="center">
  <img src="sample%20images/v2/12_tray_menu.png" alt="Tray menu: Always on Top, Pin to Active Window, Launch on Startup, Auto-Hide on Fullscreen, Album Art Background, High-Res Album Art, Show Progress Bar, Scrolling Song Text, Themes, Transparency, Size, Dynamic Island" width="340">
</p>

---

## 🛠️ Prerequisites & Setup

PulseDock requires Windows 10/11 (it uses WinRT media session APIs).

```bash
pip install PyQt6 winsdk
```

## 🚀 How to Run

```bash
python "PulseDock v2.0 Music Widget.py"
```

### Controls Cheat Sheet
- **Move** — click & drag anywhere on the widget.
- **Volume** — mouse wheel anywhere over the widget (scrolling up while muted auto-unmutes).
- **Mute** — click the speaker icon (Normal and larger modes). Unmuting restores your previous level.
- **Minimize to tray** — click the small chevron in the top-right corner; click the tray icon to bring it back.
- **Everything else** — right-click the tray icon.

---

## 📦 Building a Standalone Executable

A pre-configured PyInstaller `.spec` is included:

```bash
pip install pyinstaller
pyinstaller "PulseDock Widget.spec"
```

Your standalone build lands in `dist/PulseDock Widget.exe` with icons and assets embedded.

---

## 📂 File Structure

```plaintext
├── PulseDock v2.0 Music Widget.py   # Core widget application
├── PulseDock Widget.spec            # PyInstaller build recipe
├── PulseDock.ico                    # App & tray icon
├── icons/                           # SVG icons (recolored at runtime per theme)
├── sample images/                   # README media
└── README.md
```

---

## 🔩 How It Works Under the Hood

1. **COM Multi-Threaded Apartment** — WinRT media APIs need an MTA; a dedicated `QThread` (`SMTCWorker`) runs `CoInitializeEx` and polls active sessions with async coroutines, then hands snapshots to the GUI thread via Qt signals.
2. **Dynamic Restyling** — On every track change the widget recompiles its QSS, recolors the SVG icon set to the active theme (cached in `%LocalAppData%\PulseDock Widget\icon_cache`), and — in Auto mode — votes across hue buckets of the cover art to derive the accent color.
3. **Core Audio, no dependencies** — Volume/mute talk directly to `IAudioEndpointVolume` via raw COM vtables in ctypes.
4. **Robust Cleanup** — If a WinRT call hangs at shutdown, the worker is force-terminated after 3s so the process never lingers in Task Manager.

---

## 💡 Troubleshooting

- **"winsdk is not installed"** — `pip install winsdk` (Windows only; no macOS/Linux support).
- **"No music playing"** — Start playback in any SMTC-aware player (Spotify, YT Music, a browser tab). Windows needs at least one active media session.
- **Crash logs** — Critical errors write `crash_log.txt` under `%LocalAppData%\PulseDock Widget\` with the full stack trace.
