# PulseDock Widget 🎵

PulseDock Widget is a sleek, modern, and highly-customizable floating media controller for Windows 11. It integrates directly with the Windows Global System Media Transport Controls (SMTC) to display real-time playback info (title, artist, state) and control active media players like Spotify, YouTube Music, VLC, Edge, Chrome, and more.

Built with **PyQt6** and **Python Windows SDK (`winsdk`)**, it features a lightweight, frameless, and adaptive design that updates its theme based on the active media player.

<p align="center">
  <img src="sample%20images/2.png" alt="PulseDock Widget Theme Presets" width="650">
</p>

---

## ✨ Features

- **Direct Windows SMTC Integration**: Reads media metadata (title, artist, player origin) and sends controls (Play/Pause, Next, Previous) asynchronously without blocking.
- **Album Art (v2.0)**: Displays the current track's cover art with rounded corners in Normal, Wide, and Large modes — fetched straight from the media session and cached per track. Shows a themed music-note placeholder when no art is available.
- **Volume & Mute Control (v2.0)**: Scroll the mouse wheel anywhere on the widget to raise/lower the system master volume (5% per notch, touchpad friendly), and click the speaker button to mute/unmute. The speaker icon reflects the live state (off / low / high) and a tooltip + status flash shows the volume percentage. Implemented with raw Core Audio COM — no extra dependencies.
- **Dynamic Auto-Theme**: Automatically switches appearance matching the active source app (e.g., Spotify, YouTube Music) or lets you pick classic, dark, or warm custom themes manually.
- **Multi-Size Layouts**: Supports 5 preset sizes: Extra Small (XS) button-only mode, Small, Normal, Wide, and Large. Normal/Wide place the art beside the track info; Large shows a big cover on top, mini-player style.

- **Customizable Opacity**: Adjust transparency levels from 20% to 100% for a subtle desktop integration.
- **Settings Persistence**: Saves your layout position, window scaling, transparency, active theme preference, and "Always on Top" settings under `%LocalAppData%\PulseDock Widget\settings.json`.
- **System Tray Controls**: Run in the background, minimize to tray, toggle "Always on Top", switch styles, or hide/show the widget easily via the system tray context menu.
<p align="center">
  <b>Tray Icon Pin</b><br>
  <img src="sample%20images/5.png" alt="Tray bar" width="400">
</p>
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

## 📸 Screenshots

<p align="center">
  <b>Multi-Size Layouts (from 50% XS to 150% L) & Custom Styles</b><br>
  <img src="sample%20images/1.png" alt="Multi-Size Layouts" width="500">
</p>

<br>

<p align="center">
  <b>Seamless Desktop Integration</b><br>
  <img src="sample%20images/4.png" alt="Desktop Integration" width="500">
</p>

<br>

<p align="center">
  <b>Visual Studio Code Development Environment</b><br>
  <img src="sample%20images/3.png" alt="Development Environment" width="650">
</p>

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
- **Volume**: Scroll the mouse wheel anywhere over the widget to adjust the system volume (works in every size mode). Scrolling up while muted automatically unmutes.
- **Mute**: Click the speaker button (Normal, Wide, and Large modes) to toggle mute. Muting preserves your volume level; unmuting restores it.
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
