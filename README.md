# PulseDock Widget 🎵

PulseDock is a sleek, frameless, always-on-top floating media controller for Windows 11. It hooks straight into the Windows Global System Media Transport Controls (SMTC) to show real-time playback info — title, artist, album art, progress — and control any active media player: Spotify, YouTube Music, VLC, Edge, Chrome, and more.

Built with **PyQt6** and the **Windows SDK (`winsdk`)**, it's lightweight, adaptive, and themes itself to whatever you're listening to.

<p align="center">
  <img src="sample%20images/v2/01_normal_auto.png" alt="PulseDock Widget — Normal mode with album art" width="520">
</p>

<p align="center">
  <img src="sample%20images/v2/showcase.gif" alt="PulseDock cycling through its themes and morphing through every size" width="400"><br>
  <sub>🎨 One widget, every mood — themes crossfade and the card morphs through all its sizes.</sub>
</p>

---

## ✨ Features

- **Direct Windows SMTC Integration** — Reads media metadata (title, artist, source app) and sends Play/Pause/Next/Previous asynchronously, without ever blocking the UI.
- **🏝️ Dynamic Island (v2.0)** — iPhone-style island that docks to the top of your screen (or floats anywhere). Rests as a compact pill — or a bare circular album-art "Drop" — and smoothly expands to full controls on hover or track change, then auto-collapses.
- **Album Art Everywhere (v2.0)** — Cover art with rounded corners in every layout, fetched straight from the media session and cached per track. Optional **High-Res Album Art (Online)** lookup and an **Album Art Background** mode that blurs the cover into the card itself.
- **Live Progress Bar (v2.0)** — A slim accent-colored progress line tracks the song position along the bottom edge of the card.
- **Scrolling Song Text (v2.0)** — Long titles marquee smoothly instead of truncating.
- **Volume & Mute (v2.0)** — Scroll the mouse wheel anywhere on the widget to change system volume (5% per notch, touchpad friendly); click the speaker to mute/unmute. Implemented with raw Core Audio COM — zero extra dependencies.
- **Dynamic Auto-Theme** — Matches the active player's brand style (Spotify green, YouTube Music red, …) or derives an accent palette straight from the album art. Manual themes included — plus a **Liquid Glass** material theme that frosts the whole card like real glass.
- **Size Modes for Every Corner** — Drop (art only), Extra Small, **XS (Round)**, Small, Normal, Mini Card, Large — plus the two Dynamic Island modes.
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

<details>
<summary>🟢 <b>XS (Round)</b> — a new pocket-size mode (click to expand)</summary>

<br>

A pure circle of album art, twice the size of Drop. It rests as a clean cover "coin" and, on hover, melts the artwork away to reveal Previous / Play / Next — a complete player in a footprint smaller than a coaster.

| At rest | On hover |
|:---:|:---:|
| <img src="sample%20images/v2/17_xs_round.png" width="200"> | <img src="sample%20images/v2/18_xs_round_hover.png" width="200"> |

</details>

---

## 🏝️ Dynamic Island

An iPhone-style island that rests as a compact pill and swells to full controls on hover — or automatically when the track changes — then melts back down on its own. Two modes, straight from the menu:

| Dynamic Island (Top) | Dynamic Island (Floating) |
|:---:|:---:|
| <img src="sample%20images/v2/19_island_top.gif" alt="Top island expanding on hover" width="360"> | <img src="sample%20images/v2/20_island_floating.gif" alt="Floating island expanding on hover" width="360"> |
| Docks to the top-center bezel like a notch companion — grows **downward**. | Parked wherever you drop it — grows **outward from its center**. |

Pick the **idle size** (Drop / XS Round / Extra Small / Small) and what it **expands to** (XS Round / Small / Normal / Mini Card / Large / Circle).

<details>
<summary>🔀 Mix your own idle → expand — a few favorites (click to expand)</summary>

<br>

| Drop → Circle | XS Round → Small | XS Round → Mini Card |
|:---:|:---:|:---:|
| <img src="sample%20images/v2/21_island_drop_circle.gif" alt="Drop punch-hole expanding to a round card" width="240"> | <img src="sample%20images/v2/22_island_xs_small.gif" alt="XS round coin expanding to a small pill" width="240"> | <img src="sample%20images/v2/23_island_xs_minicard.gif" alt="XS round coin expanding to a mini card" width="240"> |
| A punch-hole dot that blossoms into a full **round** player. | A cover coin that stretches into a slim horizontal bar. | A cover coin that unfolds into a vertical mini card. |

</details>

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

<details>
<summary>🧊 <b>Liquid Glass</b> — the newest material theme (click to expand)</summary>

<br>

**Liquid Glass** swaps the flat fill for a frosted-glass material: a curved highlight sweeps the top edge, light pools where it enters the corners, and the play button becomes a translucent glass disc. It layers *over* whatever is behind it — including the album-art background — so the cover glows softly through the frost.

| Liquid Glass | Liquid Glass + Album Art |
|:---:|:---:|
| <img src="sample%20images/v2/13_theme_liquidglass.png" width="380"> | <img src="sample%20images/v2/14_liquidglass_art.png" width="380"> |

</details>

<details>
<summary>🖼️ <b>Album Art Background</b> — blur the cover into the card (click to expand)</summary>

<br>

Flip on **Album Art Background** and the cover blurs edge-to-edge into the card itself, tinting the whole widget with the track's own colors. It rides along at every size:

| Mini Card | Small |
|:---:|:---:|
| <img src="sample%20images/v2/15_artbg_mini.png" width="220"> | <img src="sample%20images/v2/16_artbg_small.png" width="330"> |

</details>

---

## ⚙️ Control Center

Every setting lives in one menu — open it by **right-clicking the tray icon _or_ the widget itself**. Same menu, whichever is closer to your cursor; no config files to touch:

<p align="center">
  <img src="sample%20images/v2/12_tray_menu.png" alt="Menu: Always on Top, Pin to Active Window, Launch on Startup, Auto-Hide on Fullscreen, Album Art Background, High-Res Album Art, Show Progress Bar, Scrolling Song Text, Themes, Transparency, Size, Dynamic Island" width="340">
</p>

The top section is all one-tap toggles — **Always on Top**, **Pin to Active Window**, **Launch on Startup**, **Auto-Hide on Fullscreen**, **Album Art Background**, **High-Res Album Art (Online)**, **Show Progress Bar** and **Scrolling Song Text** — followed by the **Themes**, **Transparency**, **Size** and **Dynamic Island** submenus.

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
- **Everything else** — right-click the widget (or the tray icon) for the full menu: themes, sizes, toggles and more.

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
