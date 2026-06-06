# PulseDock Widget 🎵

PulseDock Widget is a sleek, modern, and highly-customizable floating media controller for Windows 11. It integrates directly with the Windows Global System Media Transport Controls (SMTC) to display real-time playback info (title, artist, state) and control active media players like Spotify, YouTube Music, VLC, Edge, Chrome, and more.

Built with **PyQt6** and **Python Windows SDK (`winsdk`)**, it features a lightweight, frameless, and adaptive design that updates its theme based on the active media player.

---

## ✨ Features

- **Direct Windows SMTC Integration**: Reads media metadata (title, artist, player origin) and sends controls (Play/Pause, Next, Previous) asynchronously without blocking.
- **Dynamic Auto-Theme**: Automatically switches appearance matching the active source app (e.g., Spotify, YouTube Music) or lets you pick classic, dark, or warm custom themes manually.
- **Multi-Size Layouts**: Supports 5 scaling options ranging from Extra Small (XS) button-only mode to a Large (L) vertical card layout:
  - `50%` (Extra Small): 3-button compact controls.
  - `75%` (Small): Title/Artist display next to controls.
  - `100%` (Normal): Full layout with active playing status and metadata.
  - `125%` (Wide): Extended layouts showing the source name (e.g., *Playing • Spotify*).
  - `150%` (Large): Vertical square layout designed to look like a desktop gadget.
- **Marquee Text Scrolling**: Smooth scrolling effect for titles and artists that exceed the display boundaries.
- **Adaptive SVG Icon Colors**: Recolors all controls dynamically to match the active theme's accent colors.
- **Customizable Opacity**: Adjust transparency levels from 20% to 100% for a subtle desktop integration.
- **Settings Persistence**: Saves your layout position, window scaling, transparency, active theme preference, and "Always on Top" settings under `%LocalAppData%\PulseDock Widget\settings.json`.
- **System Tray Controls**: Run in the background, minimize to tray, toggle "Always on Top", switch styles, or hide/show the widget easily via the system tray context menu.

---

## 🎨 Theme Presets

PulseDock comes with several custom color schemes:
1. **Auto (Dynamic)**: Detects your active media player and applies matching brand styles.
2. **Spotify Black / Spotify White**: True dark and light themes with Spotify Green accents.
3. **YouTube Music Black / YouTube Music White**: Red accent styling optimized for YouTube Music.
4. **Midnight Drive (Theme 1)**: Deep dark blue background with emerald green accents.
5. **Daylight (Theme 2)**: Crisp light-grey interface with sky blue highlights.
6. **Coffee & Cigarettes (Theme 5)**: Warm vintage brown/coffee aesthetic.

---

## 🛠️ Prerequisites & Setup

PulseDock requires Windows 10 or Windows 11 because it utilizes the Windows Runtime (WinRT) APIs for media session tracking.

### Dependencies
Install the required dependencies via `pip`:

```bash
pip install PyQt6 winsdk
```

---

## 🚀 How to Run

Clone the repository and run the widget directly:

```bash
python pulse_dock_music_widget.py
```

### Dragging & Desktop Control
- **Move Widget**: Click and drag anywhere on the widget to reposition it on your desktop.
- **System Tray**: Right-click the PulseDock tray icon (usually in the bottom right corner of the taskbar) to open the configuration menu.
- **Minimize to Tray**: Click the small down arrow in the top right of the widget (visible at `75%` scale and above) to hide it. Left-click or right-click the system tray icon to bring it back.

---

## 📦 Building a Standalone Executable (`.exe`)

You can compile PulseDock into a standalone, windowed Windows executable using PyInstaller. A pre-configured `.spec` file is included in this repository.

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Build the app using the spec file:
   ```bash
   pyinstaller pulse_dock_music_widget.spec
   ```
3. Find your standalone executable in the `dist/` directory:
   - `dist/pulse_dock_music_widget.exe` (includes embedded icons and assets).

---

## 📂 File Structure

```plaintext
├── pulse_dock_music_widget.py      # Core widget application code
├── pulse_dock_music_widget.spec    # PyInstaller compilation instructions
├── PulseDock.ico                 # Main application & tray icon
├── icons/                        # Core SVG icons (dynamically colored at runtime)
│   ├── down.svg
│   ├── pause.svg
│   ├── play_arrow.svg
│   ├── refresh.svg
│   ├── skip_next.svg
│   └── skip_previous.svg
└── README.md                     # Documentation
```

---

## ⚙️ How it Works Under the Hood

1. **COM Multi-Threaded Apartment (MTA)**:
   The Windows SDK media APIs require COM to be initialized in a Multi-Threaded Apartment. PulseDock utilizes a specialized `QThread` (`SMTCWorker`) that triggers `CoInitializeEx` and periodically checks active sessions on a background task pool using asynchronous coroutines.
2. **Dynamic UI Re-Styling**:
   Whenever the track updates, the background worker sends a thread-safe Qt Signal to the main GUI thread. The widget updates text dimensions, evaluates the appropriate colors, compiles a custom Qt Style Sheet (QSS), reads SVG icon data, dynamically replaces color hex codes inside the SVG markup, and saves them to a local cache directory (`%LocalAppData%\PulseDock Widget\icon_cache`).
3. **Robust Cleanup**:
   If a WinRT query hangs during application shutdown, the cleanup cycle will attempt to shut down the background thread cleanly and force-terminates it after 3 seconds to guarantee that the application process never leaks or hangs in the Task Manager.

---

## 💡 Troubleshooting

- **"winsdk is not installed"**:
  Make sure you are on Windows and have run `pip install winsdk`. This widget does not support macOS or Linux because it depends on Windows media transport sessions.
- **No media controls appearing or showing "No music playing"**:
  Open your media player (e.g. Spotify, YouTube Music, Edge/Chrome tab playing audio) and start playback. The Windows OS requires at least one active media transport control session to register the widget.
- **Crash logs**:
  If a critical exception occurs, PulseDock creates a `crash_log.txt` in the root folder containing the stack trace to help debug the issue.
