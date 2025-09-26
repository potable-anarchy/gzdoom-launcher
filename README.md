# GZDoom Launcher

A terminal-based user interface for launching GZDoom with customizable mod configurations and preset management.

## Features

- **Preset Management**: Save and load your favorite IWAD + mod combinations
- **Interactive TUI**: Navigate with arrow keys and intuitive controls
- **Two-Pane Interface**: Live preview of preset configurations
- **Auto-Discovery**: Automatically finds IWAD and mod files
- **Fast Launch**: Quick access to saved configurations
- **Cross-Platform**: Works on macOS, Linux, and Windows

## Screenshots

```
┌─────────────────────────────────────────┐
│              Select Preset              │
└─────────────────────────────────────────┘

→ Doom Infinite + Voxel    │ Configuration Preview
  Brutal Doom              │
  Vanilla DOOM2            │ Preset: Doom Infinite + Voxel
  🔧 Custom Configuration  │ IWAD: DOOM2.WAD
                           │
                           │ Mods (2):
                           │   • DOOM_Infinite_098_PP2_H2.pk3
                           │   • VoxelDoom_v2.4.pk3
```

## Installation

### Prerequisites

- Python 3.6 or higher
- GZDoom installed
- DOOM IWAD files (DOOM.WAD, DOOM2.WAD, etc.)

### Quick Install

1. Clone the repository:
   ```bash
   git clone https://github.com/potable-anarchy/gzdoom-launcher.git
   cd gzdoom-launcher
   ```

2. Run the installer:
   ```bash
   ./install.py
   ```

3. Restart your terminal or run:
   ```bash
   source ~/.zshrc  # or ~/.bashrc
   ```

4. Launch the launcher:
   ```bash
   doom-launcher
   ```

### Shell Integration

Add an alias to your shell configuration:

**For zsh/bash:**
```bash
echo 'alias doom-launcher="~/gzdoom-launcher/doom-launcher.py"' >> ~/.zshrc
source ~/.zshrc
```

## Usage

### First Time Setup

1. Run `doom-launcher` to start
2. Select **[SETUP]** from the main menu to:
   - Scan for existing IWAD and mod files
   - Create necessary directories
   - Configure GZDoom path
   - View current configuration
3. Use the setup tools to locate and organize your files

### Navigation

- **↑↓ Arrow Keys**: Navigate menus
- **Enter**: Select option or toggle mod
- **Space**: Toggle mod selection (in mod screen)
- **Numbers (1-9)**: Quick select items
- **q**: Quit

### Workflow

1. **Select Preset**: Choose from saved configurations or select "Custom"
2. **Custom Configuration** (if selected):
   - Choose IWAD (base game)
   - Select mods to load
   - Save as preset or launch directly
3. **Launch**: Game starts automatically

### Preset Management

- **Save Preset**: Create reusable configurations
- **Live Preview**: See IWAD and mod list before launching
- **Quick Launch**: Select preset and launch immediately

## File Structure

```
~/Documents/GZDoom/
├── DOOM.WAD              # IWAD files
├── DOOM2.WAD
├── mod1.pk3              # Mod files
├── mod2.pk3
└── launcher_presets.json # Saved configurations
```

## Supported File Types

- **IWAD**: `.wad` files (DOOM, DOOM2, Heretic, Hexen, etc.)
- **Mods**: `.pk3` and `.wad` files

## Configuration

The launcher automatically detects:
- GZDoom installation at `/Applications/GZDoom.app/Contents/MacOS/gzdoom` (macOS)
- IWAD and mod files in `~/Documents/GZDoom/`

To use a different GZDoom path, edit the `gzdoom_path` variable in `doom-launcher.py`.

## Troubleshooting

### "No IWAD files found"
- Ensure IWAD files are in `~/Documents/GZDoom/`
- Check file permissions are readable

### "Command not found: gzdoom"
- Verify GZDoom installation path in the script
- Update `gzdoom_path` variable if needed

### "Permission denied"
- Make the script executable: `chmod +x doom-launcher.py`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Requirements

- Python 3.6+
- curses library (included with Python on Unix systems)
- GZDoom