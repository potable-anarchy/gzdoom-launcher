#!/usr/bin/env python3
"""
GZDoom GUI Launcher
A native macOS interface for launching GZDoom with mod selection
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QPushButton, QLabel, QMessageBox, QInputDialog,
    QListWidgetItem, QSplitter, QGroupBox, QScrollArea, QFrame,
    QRadioButton, QCheckBox, QButtonGroup
)
from PySide6.QtGui import QFont, QIcon


class DoomLauncherGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.gzdoom_path = "/Applications/GZDoom.app/Contents/MacOS/gzdoom"
        self.base_dir = Path.home() / "Documents" / "GZDoom"
        self.iwad_dir = self.base_dir / "IWAD"
        self.mods_dir = self.base_dir / "Mods"
        self.presets_file = self.base_dir / "launcher_presets.json"
        self.iwads = []
        self.mods = []
        self.selected_iwad = None
        self.selected_mods = []
        self.presets = {}

        self.setWindowTitle("GZDoom Launcher")
        self.setMinimumSize(900, 600)

        self.load_presets()
        self.scan_files()
        self.init_ui()

    def scan_files(self):
        """Scan for IWAD files and mods"""
        self.iwads = []
        self.mods = []

        # Find IWAD files in ~/Documents/Doom/IWAD/
        if self.iwad_dir.exists():
            for ext in ["*.wad", "*.WAD"]:
                for file in self.iwad_dir.glob(ext):
                    self.iwads.append(file)

        # Find mod files in ~/Documents/Doom/Mods/
        if self.mods_dir.exists():
            for ext in ["*.pk3", "*.PK3", "*.wad", "*.WAD"]:
                for file in self.mods_dir.glob(ext):
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
            self.base_dir.mkdir(parents=True, exist_ok=True)
            with open(self.presets_file, 'w') as f:
                json.dump(self.presets, f, indent=2)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save presets: {e}")

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

    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # Title
        title = QLabel("GZDoom Launcher")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # Create splitter for preset/custom view
        splitter = QSplitter(Qt.Horizontal)

        # Left panel - Presets
        presets_widget = QWidget()
        presets_layout = QVBoxLayout(presets_widget)

        presets_label = QLabel("Presets")
        presets_label.setFont(QFont("", 16, QFont.Bold))
        presets_layout.addWidget(presets_label)

        self.presets_list = QListWidget()
        self.presets_list.itemDoubleClicked.connect(self.on_preset_selected)
        presets_layout.addWidget(self.presets_list)

        preset_buttons = QHBoxLayout()
        load_preset_btn = QPushButton("Load Preset")
        load_preset_btn.clicked.connect(self.on_preset_selected)
        delete_preset_btn = QPushButton("Delete Preset")
        delete_preset_btn.clicked.connect(self.delete_preset)
        preset_buttons.addWidget(load_preset_btn)
        preset_buttons.addWidget(delete_preset_btn)
        presets_layout.addLayout(preset_buttons)

        splitter.addWidget(presets_widget)

        # Right panel - Custom configuration
        custom_widget = QWidget()
        custom_layout = QVBoxLayout(custom_widget)

        custom_label = QLabel("Custom Configuration")
        custom_label.setFont(QFont("", 16, QFont.Bold))
        custom_layout.addWidget(custom_label)

        # IWAD selection with radio buttons
        iwad_group = QGroupBox("Select IWAD (Base Game)")
        iwad_layout = QVBoxLayout(iwad_group)
        self.iwad_button_group = QButtonGroup(self)
        self.iwad_scroll = QScrollArea()
        self.iwad_scroll.setWidgetResizable(True)
        iwad_scroll_widget = QWidget()
        self.iwad_scroll_layout = QVBoxLayout(iwad_scroll_widget)
        self.iwad_scroll_layout.addStretch()
        self.iwad_scroll.setWidget(iwad_scroll_widget)
        iwad_layout.addWidget(self.iwad_scroll)
        custom_layout.addWidget(iwad_group)

        # Mod selection with checkboxes
        mod_group = QGroupBox("Select Mods (Optional)")
        mod_layout = QVBoxLayout(mod_group)
        self.mod_scroll = QScrollArea()
        self.mod_scroll.setWidgetResizable(True)
        mod_scroll_widget = QWidget()
        self.mod_scroll_layout = QVBoxLayout(mod_scroll_widget)
        self.mod_scroll_layout.addStretch()
        self.mod_scroll.setWidget(mod_scroll_widget)
        mod_layout.addWidget(self.mod_scroll)
        custom_layout.addWidget(mod_group)

        splitter.addWidget(custom_widget)
        splitter.setSizes([400, 500])

        main_layout.addWidget(splitter)

        # Bottom buttons
        button_layout = QHBoxLayout()

        save_preset_btn = QPushButton("Save as Preset")
        save_preset_btn.clicked.connect(self.save_preset)
        button_layout.addWidget(save_preset_btn)

        button_layout.addStretch()

        setup_btn = QPushButton("Setup")
        setup_btn.clicked.connect(self.show_setup)
        button_layout.addWidget(setup_btn)

        launch_btn = QPushButton("Launch GZDoom")
        launch_btn.setMinimumHeight(40)
        launch_btn.clicked.connect(self.launch_game)
        launch_btn.setStyleSheet("QPushButton { font-size: 16px; font-weight: bold; }")
        button_layout.addWidget(launch_btn)

        main_layout.addLayout(button_layout)

        # Populate lists
        self.refresh_lists()

    def refresh_lists(self):
        """Refresh all list widgets"""
        # Presets
        self.presets_list.clear()
        for preset_name in self.presets.keys():
            self.presets_list.addItem(preset_name)

        # Clear existing IWAD radio buttons
        for button in self.iwad_button_group.buttons():
            self.iwad_button_group.removeButton(button)
            button.deleteLater()

        # Create IWAD radio buttons
        for i, iwad in enumerate(self.iwads):
            radio = QRadioButton(iwad.name)
            radio.toggled.connect(lambda checked, idx=i: self.on_iwad_selected(idx) if checked else None)
            self.iwad_scroll_layout.insertWidget(i, radio)
            self.iwad_button_group.addButton(radio, i)
            if self.selected_iwad == iwad:
                radio.setChecked(True)

        # Clear existing mod checkboxes
        for i in reversed(range(self.mod_scroll_layout.count())):
            widget = self.mod_scroll_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Create mod checkboxes
        self.mod_checkboxes = []
        for i, mod in enumerate(self.mods):
            checkbox = QCheckBox(mod.name)
            checkbox.stateChanged.connect(self.on_mods_selected)
            self.mod_scroll_layout.insertWidget(i, checkbox)
            self.mod_checkboxes.append(checkbox)
            if mod in self.selected_mods:
                checkbox.setChecked(True)

        self.mod_scroll_layout.addStretch()

        if not self.iwads:
            reply = QMessageBox.question(
                self,
                "No IWADs Found",
                f"No IWAD files found!\n\nPlace IWAD files in:\n{self.iwad_dir}\n\nOpen directory now?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                subprocess.Popen(["open", str(self.iwad_dir)])

    def on_preset_selected(self):
        """Handle preset selection"""
        current_item = self.presets_list.currentItem()
        if current_item:
            preset_name = current_item.text()
            if self.load_preset(preset_name):
                self.refresh_lists()
                QMessageBox.information(self, "Preset Loaded", f"Loaded preset: {preset_name}")

    def delete_preset(self):
        """Delete selected preset"""
        current_item = self.presets_list.currentItem()
        if current_item:
            preset_name = current_item.text()
            reply = QMessageBox.question(
                self,
                "Delete Preset",
                f"Are you sure you want to delete preset '{preset_name}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                del self.presets[preset_name]
                self.save_presets()
                self.refresh_lists()

    def on_iwad_selected(self, index):
        """Handle IWAD selection"""
        if 0 <= index < len(self.iwads):
            self.selected_iwad = self.iwads[index]

    def on_mods_selected(self):
        """Handle mod selection"""
        self.selected_mods = []
        for i, checkbox in enumerate(self.mod_checkboxes):
            if checkbox.isChecked() and i < len(self.mods):
                self.selected_mods.append(self.mods[i])

    def save_preset(self):
        """Save current configuration as a preset"""
        if not self.selected_iwad:
            QMessageBox.warning(self, "No IWAD Selected", "Please select an IWAD first.")
            return

        name, ok = QInputDialog.getText(self, "Save Preset", "Enter preset name:")
        if ok and name:
            self.save_current_as_preset(name)
            self.refresh_lists()
            QMessageBox.information(self, "Preset Saved", f"Preset '{name}' saved successfully!")

    def launch_game(self):
        """Launch GZDoom with selected configuration"""
        if not self.selected_iwad:
            QMessageBox.warning(self, "No IWAD Selected", "Please select an IWAD first.")
            return

        cmd = [self.gzdoom_path, "-iwad", str(self.selected_iwad)]

        if self.selected_mods:
            cmd.extend(["-file"] + [str(mod) for mod in self.selected_mods])

        try:
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            QMessageBox.information(self, "Launched", "GZDoom launched successfully!")
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to launch GZDoom:\n{e}")

    def show_setup(self):
        """Show setup dialog"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Setup & Configuration")
        msg.setText("GZDoom Launcher Setup")
        msg.setInformativeText(
            f"GZDoom path: {self.gzdoom_path}\n"
            f"IWAD directory: {self.iwad_dir}\n"
            f"Mods directory: {self.mods_dir}\n"
            f"IWAD files: {len(self.iwads)}\n"
            f"Mod files: {len(self.mods)}\n"
            f"Saved presets: {len(self.presets)}\n\n"
            f"Place IWAD files in: {self.iwad_dir}\n"
            f"Place mod files in: {self.mods_dir}"
        )

        rescan_btn = msg.addButton("Rescan Files", QMessageBox.ActionRole)
        create_dir_btn = msg.addButton("Create Directories", QMessageBox.ActionRole)
        msg.addButton(QMessageBox.Close)

        msg.exec()

        if msg.clickedButton() == rescan_btn:
            self.scan_files()
            self.refresh_lists()
            QMessageBox.information(self, "Rescan Complete", "Files rescanned successfully!")
        elif msg.clickedButton() == create_dir_btn:
            try:
                self.iwad_dir.mkdir(parents=True, exist_ok=True)
                self.mods_dir.mkdir(parents=True, exist_ok=True)
                QMessageBox.information(self, "Directories Created", f"Created:\n{self.iwad_dir}\n{self.mods_dir}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create directories: {e}")


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("GZDoom Launcher")

    window = DoomLauncherGUI()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
