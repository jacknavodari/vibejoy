# VibeJoy Media Player

![VibeJoy Media Player](https://placehold.co/800x400/1e1e1e/4fc3f7?text=VibeJoy+Media+Player)

A modern, feature-rich media player with a sleek dark theme GUI built using Python and Tkinter.

## Features

- 🎵 **Modern Dark Theme Interface** - Sleek and visually appealing design
- 🎨 **Album Art Display** - Automatically shows album artwork from your music files
- 📝 **Track Information** - Displays title, artist, and other metadata
- ⏱️ **Progress Tracking** - Visual progress bar with time display
- 🔀 **Shuffle Mode** - Random playback of your music collection
- 🔁 **Repeat Mode** - Loop single tracks or entire playlists
- 📁 **Folder Import** - Easily add entire folders of music to your playlist
- 🔊 **Volume Control** - Adjustable volume slider
- 🎯 **Playlist Management** - Add or remove tracks from your playlist

## Screenshots

![Player Interface](https://placehold.co/600x400/2d2d2d/ffffff?text=Player+Interface)
*Main player interface with album art display and playlist*

## Installation

### For Users

1. Download the latest release from the [Releases](#) page
2. Run the `VibeJoy.exe` file in the main project directory
3. Enjoy your music!

### For Developers

#### Prerequisites

- Python 3.6 or higher
- pip (Python package installer)

#### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/vibejoy-media-player.git
   cd vibejoy-media-player
   ```

2. Install the required dependencies:
   ```bash
   pip install pygame Pillow mutagen
   ```

3. Run the application:
   ```bash
   python main.py
   ```

## Building from Source

To build a standalone executable for Windows:

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Build the executable:
   ```bash
   pyinstaller --noconfirm --onefile --windowed --name=VibeJoy --icon=NONE main.py
   ```

3. Find the executable in the project root folder

Alternatively, you can run the provided build script:
```bash
build_installer.bat
```

## Usage

1. Launch the application by double-clicking `VibeJoy.exe`
2. Click "Add Folder" to import your music collection
3. Select a track from the playlist to begin playback
4. Use the playback controls to play, pause, stop, skip, etc.
5. Adjust volume using the slider at the bottom
6. Enable shuffle or repeat modes using the respective buttons

### Controls

- ▶️ **Play** - Start playback of selected track
- ⏸️ **Pause** - Pause currently playing track
- ⏹️ **Stop** - Stop playback and clear selection
- ⏮️ **Previous** - Play previous track in playlist
- ⏭️ **Next** - Play next track in playlist
- 🔀 **Shuffle** - Toggle shuffle mode
- 🔁 **Repeat** - Toggle repeat mode

## Technical Details

### Libraries Used

- **Tkinter** - GUI framework
- **Pygame** - Audio playback
- **Pillow** - Image processing for album art
- **Mutagen** - Audio metadata handling
- **JSON** - Playlist persistence

### Supported Formats

- MP3
- WAV
- OGG

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by modern media player designs
- Thanks to the Python community for the excellent libraries
- Album art feature made possible by the Pillow and Mutagen libraries

## Support

If you encounter any issues or have feature requests, please [open an issue](#) on GitHub.

---

**Enjoy your music with VibeJoy!** 🎶