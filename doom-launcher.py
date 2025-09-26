#!/usr/bin/env python3
"""
GZDoom TUI Launcher
A terminal-based interface for launching GZDoom with mod selection
"""

import curses
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

class DoomLauncher:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.gzdoom_path = "/Applications/GZDoom.app/Contents/MacOS/gzdoom"
        self.base_dir = Path.home() / "Documents" / "GZDoom"
        self.presets_file = self.base_dir / "launcher_presets.json"
        self.iwads = []
        self.mods = []
        self.selected_iwad = None
        self.selected_mods = []
        self.presets = {}

        # Setup colors
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)     # Header
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)   # Menu items
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)    # Selected/Active
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)      # Error
        curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLACK)     # Info
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLUE)     # Highlighted

    def scan_files(self):
        """Scan for IWAD files and mods"""
        if not self.base_dir.exists():
            return False

        # Find IWAD files (both .wad and .WAD)
        for ext in ["*.wad", "*.WAD"]:
            for file in self.base_dir.glob(ext):
                if file.name.upper() in ["DOOM.WAD", "DOOM1.WAD", "DOOM2.WAD", "PLUTONIA.WAD", "TNT.WAD", "HERETIC.WAD", "HEXEN.WAD", "STRIFE1.WAD"]:
                    self.iwads.append(file)

        # Find mod files (both .pk3/.PK3 and .wad/.WAD that aren't IWADs)
        for ext in ["*.pk3", "*.PK3", "*.wad", "*.WAD"]:
            for file in self.base_dir.glob(ext):
                if file not in self.iwads:
                    self.mods.append(file)

        return True

    def load_presets(self):
        """Load saved presets from JSON file"""
        try:
            if self.presets_file.exists():
                with open(self.presets_file, 'r') as f:
                    self.presets = json.load(f)
        except Exception:
            self.presets = {}

    def save_presets(self):
        """Save presets to JSON file"""
        try:
            with open(self.presets_file, 'w') as f:
                json.dump(self.presets, f, indent=2)
        except Exception:
            pass

    def save_current_as_preset(self, name):
        """Save current configuration as a preset"""
        if self.selected_iwad and name:
            self.presets[name] = {
                'iwad': self.selected_iwad.name,
                'mods': [mod.name for mod in self.selected_mods]
            }
            self.save_presets()

    def load_preset(self, name):
        """Load a preset configuration"""
        if name in self.presets:
            preset = self.presets[name]

            # Find the IWAD file
            for iwad in self.iwads:
                if iwad.name == preset['iwad']:
                    self.selected_iwad = iwad
                    break

            # Find the mod files
            self.selected_mods = []
            for mod_name in preset['mods']:
                for mod in self.mods:
                    if mod.name == mod_name:
                        self.selected_mods.append(mod)
                        break

            return True
        return False

    def draw_header(self, title):
        """Draw the header"""
        h, w = self.stdscr.getmaxyx()
        self.stdscr.clear()

        # Draw border
        header = f"┌{'─' * (w-2)}┐"
        self.stdscr.addstr(0, 0, header, curses.color_pair(1) | curses.A_BOLD)

        # Center title
        title_line = f"│{title.center(w-2)}│"
        self.stdscr.addstr(1, 0, title_line, curses.color_pair(1) | curses.A_BOLD)

        footer = f"└{'─' * (w-2)}┘"
        self.stdscr.addstr(2, 0, footer, curses.color_pair(1) | curses.A_BOLD)

    def draw_preset_details(self, current, preset_names, all_items):
        """Draw preset configuration details in right pane"""
        h, w = self.stdscr.getmaxyx()
        mid_x = w // 2

        # Draw vertical separator
        for y in range(3, h - 1):
            try:
                self.stdscr.addstr(y, mid_x, "│", curses.color_pair(1))
            except:
                pass

        # Right pane header
        right_start = mid_x + 2
        self.stdscr.addstr(3, right_start, "Configuration Preview", curses.color_pair(1) | curses.A_BOLD)

        if current < len(preset_names):
            # Show preset details
            preset_name = preset_names[current]
            preset = self.presets[preset_name]

            y = 5
            self.stdscr.addstr(y, right_start, f"Preset: {preset_name}", curses.color_pair(3) | curses.A_BOLD)
            y += 1
            self.stdscr.addstr(y, right_start, f"IWAD: {preset['iwad']}", curses.color_pair(5))
            y += 2

            if preset['mods']:
                self.stdscr.addstr(y, right_start, f"Mods ({len(preset['mods'])}):", curses.color_pair(5) | curses.A_BOLD)
                y += 1
                for i, mod in enumerate(preset['mods']):
                    if y >= h - 2:
                        self.stdscr.addstr(y, right_start, "...", curses.color_pair(2))
                        break
                    # Truncate long mod names
                    max_mod_width = w - right_start - 4
                    display_mod = mod if len(mod) <= max_mod_width else mod[:max_mod_width-3] + "..."
                    self.stdscr.addstr(y, right_start + 2, f"• {display_mod}", curses.color_pair(2))
                    y += 1
            else:
                self.stdscr.addstr(y, right_start, "No mods", curses.color_pair(2))
        elif current == len(preset_names):  # CUSTOM selected
            y = 5
            self.stdscr.addstr(y, right_start, "Custom Configuration", curses.color_pair(3) | curses.A_BOLD)
            y += 2
            self.stdscr.addstr(y, right_start, "Create a new configuration", curses.color_pair(2))
            y += 1
            self.stdscr.addstr(y, right_start, "by selecting IWAD and mods", curses.color_pair(2))
        elif current == len(preset_names) + 1:  # SETUP selected
            y = 5
            self.stdscr.addstr(y, right_start, "Setup & Configuration", curses.color_pair(5) | curses.A_BOLD)
            y += 2
            self.stdscr.addstr(y, right_start, "• Find and organize IWAD files", curses.color_pair(2))
            y += 1
            self.stdscr.addstr(y, right_start, "• Locate mod files", curses.color_pair(2))
            y += 1
            self.stdscr.addstr(y, right_start, "• Configure GZDoom path", curses.color_pair(2))
            y += 1
            self.stdscr.addstr(y, right_start, "• View current configuration", curses.color_pair(2))

    def select_preset(self):
        """Preset selection screen with two panes"""
        current = 0
        preset_names = list(self.presets.keys())
        all_items = preset_names + ["[CUSTOM]", "[SETUP]"]

        while True:
            h, w = self.stdscr.getmaxyx()
            mid_x = w // 2

            self.draw_header("Select Preset")

            start_y = 4
            left_width = mid_x - 4

            if not preset_names:
                self.stdscr.addstr(start_y, 2, "No presets saved yet.", curses.color_pair(2))
                self.stdscr.addstr(start_y + 1, 2, "Select CUSTOM to create your first preset.", curses.color_pair(2))
            else:
                self.stdscr.addstr(start_y, 2, "Use ↑↓ arrows, Enter to select", curses.color_pair(5))

            # Left pane - preset list
            for i, item in enumerate(all_items):
                y = start_y + 2 + i
                if y >= h - 2:
                    break

                prefix = "→ " if i == current else "  "

                if item == "[CUSTOM]":
                    attr = curses.color_pair(3) | curses.A_BOLD
                    if i == current:
                        attr |= curses.A_REVERSE

                    text = f"{prefix}🔧 Custom Configuration"
                    # Truncate if too long for left pane
                    if len(text) > left_width:
                        text = text[:left_width-3] + "..."
                    self.stdscr.addstr(y, 2, text, attr)
                elif item == "[SETUP]":
                    attr = curses.color_pair(5) | curses.A_BOLD
                    if i == current:
                        attr |= curses.A_REVERSE

                    text = f"{prefix}⚙️  Setup & Configuration"
                    # Truncate if too long for left pane
                    if len(text) > left_width:
                        text = text[:left_width-3] + "..."
                    self.stdscr.addstr(y, 2, text, attr)
                else:
                    attr = curses.color_pair(2)
                    if i == current:
                        attr |= curses.A_REVERSE

                    # Truncate preset name if too long for left pane
                    display_name = item if len(item) <= left_width - 6 else item[:left_width-9] + "..."
                    text = f"{prefix}{display_name}"
                    self.stdscr.addstr(y, 2, text, attr)

            # Right pane - configuration details
            self.draw_preset_details(current, preset_names, all_items)

            self.stdscr.refresh()

            key = self.stdscr.getch()

            if key == ord('q'):
                return False
            elif key == curses.KEY_UP:
                current = (current - 1) % len(all_items)
            elif key == curses.KEY_DOWN:
                current = (current + 1) % len(all_items)
            elif key == ord('\n') or key == curses.KEY_ENTER or key == 10:
                if current == len(preset_names):  # CUSTOM
                    return "custom"
                elif current == len(preset_names) + 1:  # SETUP
                    return "setup"
                else:
                    preset_name = preset_names[current]
                    if self.load_preset(preset_name):
                        return "preset"
            elif key >= ord('1') and key <= ord('9'):
                idx = key - ord('1')
                if idx < len(all_items):
                    current = idx

    def select_iwad(self):
        """IWAD selection with arrow keys"""
        if not self.iwads:
            self.stdscr.clear()
            self.draw_header("GZDoom Launcher")
            self.stdscr.addstr(4, 2, "No IWAD files found!", curses.color_pair(4) | curses.A_BOLD)
            self.stdscr.addstr(5, 2, f"Place DOOM.WAD, DOOM2.WAD, etc. in:", curses.color_pair(2))
            self.stdscr.addstr(6, 2, str(self.base_dir), curses.color_pair(2))
            self.stdscr.addstr(8, 2, "Press any key to exit...", curses.color_pair(2))
            self.stdscr.refresh()
            self.stdscr.getch()
            return False

        current = 0
        while True:
            self.draw_header("Select IWAD (Base Game)")

            start_y = 4
            self.stdscr.addstr(start_y, 2, "Use ↑↓ arrows to navigate, Enter to select, 'q' to quit", curses.color_pair(5))

            for i, iwad in enumerate(self.iwads):
                y = start_y + 2 + i
                prefix = "→ " if i == current else "  "
                marker = "✓ " if iwad == self.selected_iwad else "  "

                attr = curses.color_pair(6) | curses.A_BOLD if i == current else curses.color_pair(2)
                self.stdscr.addstr(y, 2, f"{prefix}{marker}{iwad.name}", attr)

            self.stdscr.refresh()

            key = self.stdscr.getch()

            if key == ord('q'):
                return False
            elif key == curses.KEY_UP:
                current = (current - 1) % len(self.iwads)
            elif key == curses.KEY_DOWN:
                current = (current + 1) % len(self.iwads)
            elif key == ord('\n') or key == curses.KEY_ENTER or key == 10:
                # Select this IWAD and immediately continue
                self.selected_iwad = self.iwads[current]
                return True
            elif key >= ord('1') and key <= ord('9'):
                idx = key - ord('1')
                if idx < len(self.iwads):
                    current = idx
                    self.selected_iwad = self.iwads[current]

    def select_mods(self):
        """Mod selection with arrow keys"""
        current = 0
        all_items = ["[LAUNCH]", "[SAVE PRESET]", "[BACK]"] + [mod.name for mod in self.mods]

        while True:
            self.draw_header("Select Mods (Optional)")

            start_y = 4
            self.stdscr.addstr(start_y, 2, f"IWAD: {self.selected_iwad.name}", curses.color_pair(5) | curses.A_BOLD)
            self.stdscr.addstr(start_y + 1, 2, "Use ↑↓ arrows, Space to toggle, Enter to select", curses.color_pair(5))

            for i, item in enumerate(all_items):
                y = start_y + 3 + i
                if y >= curses.LINES - 2:  # Don't draw past screen
                    break

                prefix = "→ " if i == current else "  "

                if item == "[LAUNCH]":
                    attr = curses.color_pair(3) | curses.A_BOLD
                    if i == current:
                        attr |= curses.A_REVERSE
                    self.stdscr.addstr(y, 2, f"{prefix}🚀 LAUNCH GZDOOM", attr)
                elif item == "[SAVE PRESET]":
                    attr = curses.color_pair(3) | curses.A_BOLD
                    if i == current:
                        attr |= curses.A_REVERSE
                    self.stdscr.addstr(y, 2, f"{prefix}💾 SAVE PRESET", attr)
                elif item == "[BACK]":
                    attr = curses.color_pair(2)
                    if i == current:
                        attr |= curses.A_REVERSE
                    self.stdscr.addstr(y, 2, f"{prefix}← Back to preset selection", attr)
                else:
                    # It's a mod
                    mod_idx = i - 3
                    mod = self.mods[mod_idx]
                    is_selected = mod in self.selected_mods
                    marker = "✓ " if is_selected else "  "

                    attr = curses.color_pair(3) if is_selected else curses.color_pair(2)
                    if i == current:
                        attr |= curses.A_REVERSE

                    self.stdscr.addstr(y, 2, f"{prefix}{marker}{item}", attr)

            # Show selected mods count
            if self.selected_mods:
                count_y = min(start_y + 3 + len(all_items) + 1, curses.LINES - 3)
                self.stdscr.addstr(count_y, 2, f"Selected: {len(self.selected_mods)} mod(s)",
                                 curses.color_pair(3) | curses.A_BOLD)

            self.stdscr.refresh()

            key = self.stdscr.getch()

            if key == ord('q'):
                return False
            elif key == curses.KEY_UP:
                current = (current - 1) % len(all_items)
            elif key == curses.KEY_DOWN:
                current = (current + 1) % len(all_items)
            elif key == ord('\n') or key == curses.KEY_ENTER or key == 10:
                if current == 0:  # LAUNCH
                    return "launch"
                elif current == 1:  # SAVE & LAUNCH
                    return "save_launch"
                elif current == 2:  # BACK
                    return None
                else:  # Toggle mod
                    mod_idx = current - 3
                    mod = self.mods[mod_idx]
                    if mod in self.selected_mods:
                        self.selected_mods.remove(mod)
                    else:
                        self.selected_mods.append(mod)
            elif key == ord(' ') and current >= 3:  # Space to toggle mod
                mod_idx = current - 3
                mod = self.mods[mod_idx]
                if mod in self.selected_mods:
                    self.selected_mods.remove(mod)
                else:
                    self.selected_mods.append(mod)
            elif key >= ord('1') and key <= ord('9'):
                idx = key - ord('1')
                if idx < len(all_items):
                    current = idx

    def launch_game(self):
        """Launch GZDoom with selected configuration"""
        cmd = [self.gzdoom_path, "-iwad", str(self.selected_iwad)]

        if self.selected_mods:
            cmd.extend(["-file"] + [str(mod) for mod in self.selected_mods])

        self.stdscr.clear()
        self.draw_header("Launching GZDoom")

        self.stdscr.addstr(4, 2, "Command:", curses.color_pair(5) | curses.A_BOLD)

        # Display command (truncate if too long)
        cmd_str = " ".join(cmd)
        max_width = curses.COLS - 4
        if len(cmd_str) > max_width:
            cmd_str = cmd_str[:max_width-3] + "..."
        self.stdscr.addstr(5, 2, cmd_str, curses.color_pair(2))

        self.stdscr.addstr(7, 2, "Launching...", curses.color_pair(3) | curses.A_BOLD)
        self.stdscr.refresh()

        try:
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.stdscr.addstr(8, 2, "GZDoom launched successfully!", curses.color_pair(3))
            self.stdscr.addstr(9, 2, "Exiting launcher...", curses.color_pair(2))
            self.stdscr.refresh()
            curses.napms(1000)  # Brief pause to show success message
            return True
        except Exception as e:
            self.stdscr.addstr(8, 2, f"Error: {str(e)}", curses.color_pair(4) | curses.A_BOLD)
            self.stdscr.addstr(10, 2, "Press any key to continue...", curses.color_pair(2))
            self.stdscr.refresh()
            self.stdscr.getch()
            return False

    def get_preset_name(self):
        """Get preset name from user"""
        self.stdscr.clear()
        self.draw_header("Save Preset")

        self.stdscr.addstr(4, 2, "Enter preset name:", curses.color_pair(5) | curses.A_BOLD)
        self.stdscr.addstr(5, 2, "Name: ", curses.color_pair(2))

        curses.curs_set(1)  # Show cursor
        curses.echo()  # Show typed characters

        self.stdscr.refresh()

        try:
            # Get input
            name = self.stdscr.getstr(5, 8, 30).decode('utf-8').strip()
        except:
            name = ""

        curses.noecho()  # Hide typed characters
        curses.curs_set(0)  # Hide cursor

        return name if name else None

    def setup_menu(self):
        """Setup and configuration menu"""
        current = 0
        setup_items = [
            "Scan for IWAD files",
            "Scan for mod files",
            "Configure GZDoom path",
            "View current configuration",
            "Create directories",
            "[BACK]"
        ]

        while True:
            self.draw_header("Setup & Configuration")

            start_y = 4
            self.stdscr.addstr(start_y, 2, "Use ↑↓ arrows to navigate, Enter to select", curses.color_pair(5))

            for i, item in enumerate(setup_items):
                y = start_y + 2 + i
                prefix = "→ " if i == current else "  "

                if item == "[BACK]":
                    attr = curses.color_pair(2)
                    if i == current:
                        attr |= curses.A_REVERSE
                    self.stdscr.addstr(y, 2, f"{prefix}← Back to presets", attr)
                else:
                    attr = curses.color_pair(3) if i == current else curses.color_pair(2)
                    if i == current:
                        attr |= curses.A_REVERSE
                    self.stdscr.addstr(y, 2, f"{prefix}{item}", attr)

            self.stdscr.refresh()

            key = self.stdscr.getch()

            if key == ord('q'):
                return False
            elif key == curses.KEY_UP:
                current = (current - 1) % len(setup_items)
            elif key == curses.KEY_DOWN:
                current = (current + 1) % len(setup_items)
            elif key == ord('\n') or key == curses.KEY_ENTER or key == 10:
                if current == len(setup_items) - 1:  # BACK
                    return True
                elif current == 0:  # Scan for IWAD files
                    self.scan_iwads()
                elif current == 1:  # Scan for mod files
                    self.scan_mods()
                elif current == 2:  # Configure GZDoom path
                    self.configure_gzdoom_path()
                elif current == 3:  # View current configuration
                    self.view_configuration()
                elif current == 4:  # Create directories
                    self.create_directories()

    def scan_iwads(self):
        """Scan for IWAD files on the system"""
        self.stdscr.clear()
        self.draw_header("Scanning for IWAD Files")

        self.stdscr.addstr(4, 2, "Searching for IWAD files...", curses.color_pair(5))
        self.stdscr.refresh()

        # Search common locations
        search_paths = [
            Path.home() / "Documents" / "GZDoom",
            Path.home() / "Games",
            Path("/Applications/GZDoom.app/Contents/MacOS"),
            Path("/usr/share/games/doom"),
            Path("/opt/games/doom")
        ]

        found_iwads = []
        for search_path in search_paths:
            if search_path.exists():
                for ext in ["*.wad", "*.WAD"]:
                    for file in search_path.glob(ext):
                        if file.name.upper() in ["DOOM.WAD", "DOOM1.WAD", "DOOM2.WAD", "PLUTONIA.WAD", "TNT.WAD", "HERETIC.WAD", "HEXEN.WAD", "STRIFE1.WAD"]:
                            found_iwads.append(file)

        self.stdscr.clear()
        self.draw_header("IWAD Scan Results")

        y = 4
        if found_iwads:
            self.stdscr.addstr(y, 2, f"Found {len(found_iwads)} IWAD file(s):", curses.color_pair(3) | curses.A_BOLD)
            y += 2
            for iwad in found_iwads:
                self.stdscr.addstr(y, 4, f"• {iwad.name} ({iwad.parent})", curses.color_pair(2))
                y += 1
            y += 1
            self.stdscr.addstr(y, 2, f"To use these files, copy them to:", curses.color_pair(5))
            y += 1
            self.stdscr.addstr(y, 4, str(self.base_dir), curses.color_pair(2))
        else:
            self.stdscr.addstr(y, 2, "No IWAD files found in common locations.", curses.color_pair(4))
            y += 2
            self.stdscr.addstr(y, 2, "You can manually place DOOM.WAD, DOOM2.WAD, etc. in:", curses.color_pair(2))
            y += 1
            self.stdscr.addstr(y, 4, str(self.base_dir), curses.color_pair(2))

        y += 2
        self.stdscr.addstr(y, 2, "Press any key to continue...", curses.color_pair(5))
        self.stdscr.refresh()
        self.stdscr.getch()

    def scan_mods(self):
        """Scan for mod files on the system"""
        self.stdscr.clear()
        self.draw_header("Scanning for Mod Files")

        self.stdscr.addstr(4, 2, "Searching for mod files...", curses.color_pair(5))
        self.stdscr.refresh()

        # Search Downloads and common locations
        search_paths = [
            Path.home() / "Downloads",
            Path.home() / "Documents" / "GZDoom",
            Path.home() / "Games",
        ]

        found_mods = []
        for search_path in search_paths:
            if search_path.exists():
                for ext in ["*.pk3", "*.PK3", "*.wad", "*.WAD"]:
                    for file in search_path.glob(ext):
                        # Exclude IWAD files
                        if file.name.upper() not in ["DOOM.WAD", "DOOM1.WAD", "DOOM2.WAD", "PLUTONIA.WAD", "TNT.WAD", "HERETIC.WAD", "HEXEN.WAD", "STRIFE1.WAD"]:
                            found_mods.append(file)

        self.stdscr.clear()
        self.draw_header("Mod Scan Results")

        y = 4
        if found_mods:
            self.stdscr.addstr(y, 2, f"Found {len(found_mods)} mod file(s):", curses.color_pair(3) | curses.A_BOLD)
            y += 2
            for i, mod in enumerate(found_mods[:10]):  # Show first 10
                self.stdscr.addstr(y, 4, f"• {mod.name} ({mod.parent})", curses.color_pair(2))
                y += 1
            if len(found_mods) > 10:
                self.stdscr.addstr(y, 4, f"... and {len(found_mods) - 10} more", curses.color_pair(2))
                y += 1
            y += 1
            self.stdscr.addstr(y, 2, f"To use these files, copy them to:", curses.color_pair(5))
            y += 1
            self.stdscr.addstr(y, 4, str(self.base_dir), curses.color_pair(2))
        else:
            self.stdscr.addstr(y, 2, "No mod files found in common locations.", curses.color_pair(4))
            y += 2
            self.stdscr.addstr(y, 2, "You can manually place .pk3 and .wad mod files in:", curses.color_pair(2))
            y += 1
            self.stdscr.addstr(y, 4, str(self.base_dir), curses.color_pair(2))

        y += 2
        self.stdscr.addstr(y, 2, "Press any key to continue...", curses.color_pair(5))
        self.stdscr.refresh()
        self.stdscr.getch()

    def configure_gzdoom_path(self):
        """Configure GZDoom executable path"""
        self.stdscr.clear()
        self.draw_header("Configure GZDoom Path")

        self.stdscr.addstr(4, 2, f"Current GZDoom path:", curses.color_pair(5) | curses.A_BOLD)
        self.stdscr.addstr(5, 2, self.gzdoom_path, curses.color_pair(2))

        # Check if current path exists
        if Path(self.gzdoom_path).exists():
            self.stdscr.addstr(7, 2, "✓ Path exists and is accessible", curses.color_pair(3))
        else:
            self.stdscr.addstr(7, 2, "✗ Path not found", curses.color_pair(4))

        self.stdscr.addstr(9, 2, "Common GZDoom locations:", curses.color_pair(5) | curses.A_BOLD)
        common_paths = [
            "/Applications/GZDoom.app/Contents/MacOS/gzdoom",
            "/usr/local/bin/gzdoom",
            "/opt/homebrew/bin/gzdoom",
            "gzdoom"
        ]

        y = 10
        for path in common_paths:
            status = "✓" if Path(path).exists() or path == "gzdoom" else "✗"
            color = curses.color_pair(3) if status == "✓" else curses.color_pair(4)
            self.stdscr.addstr(y, 4, f"{status} {path}", color)
            y += 1

        y += 1
        self.stdscr.addstr(y, 2, "To change the path, edit the 'gzdoom_path' variable", curses.color_pair(2))
        y += 1
        self.stdscr.addstr(y, 2, "in the doom-launcher.py file.", curses.color_pair(2))

        y += 2
        self.stdscr.addstr(y, 2, "Press any key to continue...", curses.color_pair(5))
        self.stdscr.refresh()
        self.stdscr.getch()

    def view_configuration(self):
        """View current launcher configuration"""
        self.stdscr.clear()
        self.draw_header("Current Configuration")

        y = 4
        self.stdscr.addstr(y, 2, "Launcher Configuration:", curses.color_pair(5) | curses.A_BOLD)
        y += 2

        # GZDoom path
        self.stdscr.addstr(y, 2, f"GZDoom path: {self.gzdoom_path}", curses.color_pair(2))
        y += 1

        # Base directory
        self.stdscr.addstr(y, 2, f"Files directory: {self.base_dir}", curses.color_pair(2))
        y += 1

        # Directory status
        dir_status = "✓ exists" if self.base_dir.exists() else "✗ missing"
        dir_color = curses.color_pair(3) if self.base_dir.exists() else curses.color_pair(4)
        self.stdscr.addstr(y, 2, f"Directory status: {dir_status}", dir_color)
        y += 2

        # File counts
        self.stdscr.addstr(y, 2, f"IWAD files: {len(self.iwads)}", curses.color_pair(2))
        y += 1
        self.stdscr.addstr(y, 2, f"Mod files: {len(self.mods)}", curses.color_pair(2))
        y += 1
        self.stdscr.addstr(y, 2, f"Saved presets: {len(self.presets)}", curses.color_pair(2))

        y += 2
        self.stdscr.addstr(y, 2, "Press any key to continue...", curses.color_pair(5))
        self.stdscr.refresh()
        self.stdscr.getch()

    def create_directories(self):
        """Create necessary directories"""
        self.stdscr.clear()
        self.draw_header("Create Directories")

        y = 4
        self.stdscr.addstr(y, 2, "Creating launcher directories...", curses.color_pair(5))
        y += 2

        try:
            self.base_dir.mkdir(parents=True, exist_ok=True)
            self.stdscr.addstr(y, 2, f"✓ Created: {self.base_dir}", curses.color_pair(3))
        except Exception as e:
            self.stdscr.addstr(y, 2, f"✗ Failed to create: {self.base_dir}", curses.color_pair(4))
            y += 1
            self.stdscr.addstr(y, 4, f"Error: {str(e)}", curses.color_pair(4))

        y += 2
        self.stdscr.addstr(y, 2, "Directories are ready for IWAD and mod files.", curses.color_pair(2))

        y += 2
        self.stdscr.addstr(y, 2, "Press any key to continue...", curses.color_pair(5))
        self.stdscr.refresh()
        self.stdscr.getch()

    def run(self):
        """Main application loop"""
        # Setup curses
        curses.curs_set(0)  # Hide cursor
        self.stdscr.keypad(True)  # Enable arrow keys

        if not self.scan_files():
            self.stdscr.addstr(0, 0, f"Error: GZDoom directory not found at {self.base_dir}")
            self.stdscr.refresh()
            self.stdscr.getch()
            return

        self.load_presets()

        while True:
            # Preset selection
            preset_result = self.select_preset()
            if preset_result is False:  # Quit
                break
            elif preset_result == "preset":  # Selected a preset, launch directly
                if self.launch_game():
                    break
            elif preset_result == "setup":  # Setup menu
                self.setup_menu()
                # Rescan files after setup
                self.scan_files()
                self.load_presets()
                continue
            elif preset_result == "custom":  # Custom configuration
                # IWAD selection
                if not self.select_iwad():
                    continue

                # Mod selection
                mod_result = self.select_mods()
                if mod_result is False:  # Quit
                    break
                elif mod_result is None:  # Go back to presets
                    continue
                elif mod_result == "launch":  # Launch without saving
                    if self.launch_game():
                        break
                elif mod_result == "save_launch":  # Save preset
                    preset_name = self.get_preset_name()
                    if preset_name:
                        self.save_current_as_preset(preset_name)
                        # Show success message briefly
                        self.stdscr.clear()
                        self.draw_header("Preset Saved")
                        self.stdscr.addstr(4, 2, f"Preset '{preset_name}' saved successfully!", curses.color_pair(3) | curses.A_BOLD)
                        self.stdscr.addstr(5, 2, "Returning to mod selection...", curses.color_pair(2))
                        self.stdscr.refresh()
                        curses.napms(1500)
                    # Continue in the loop to return to mod selection

def main(stdscr):
    launcher = DoomLauncher(stdscr)
    launcher.run()

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        print("Goodbye!")
    except Exception as e:
        print(f"Error: {e}")