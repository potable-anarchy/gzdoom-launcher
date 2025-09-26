#!/usr/bin/env python3
"""
GZDoom Launcher Installer
Sets up the doom-launcher command for easy access
"""

import os
import sys
from pathlib import Path

def get_shell_config():
    """Detect shell and return config file path"""
    shell = os.environ.get('SHELL', '/bin/bash')
    home = Path.home()

    if 'zsh' in shell:
        return home / '.zshrc'
    elif 'bash' in shell:
        # Try .bash_profile first (macOS), then .bashrc (Linux)
        bash_profile = home / '.bash_profile'
        bashrc = home / '.bashrc'
        return bash_profile if bash_profile.exists() else bashrc
    elif 'fish' in shell:
        config_dir = home / '.config' / 'fish'
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / 'config.fish'
    else:
        return home / '.profile'

def create_alias(script_path, shell_config):
    """Add alias to shell configuration"""
    if shell_config.name == 'config.fish':
        # Fish shell syntax
        alias_line = f"alias doom-launcher='{script_path}'"
    else:
        # Bash/Zsh syntax
        alias_line = f'alias doom-launcher="{script_path}"'

    # Check if alias already exists
    if shell_config.exists():
        with open(shell_config, 'r') as f:
            content = f.read()
            if 'doom-launcher' in content:
                print(f"✓ Alias already exists in {shell_config}")
                return True

    # Add alias
    try:
        with open(shell_config, 'a') as f:
            f.write(f"\n# GZDoom Launcher\n{alias_line}\n")
        print(f"✓ Added alias to {shell_config}")
        return True
    except Exception as e:
        print(f"✗ Failed to add alias: {e}")
        return False

def main():
    print("🎮 GZDoom Launcher Installer")
    print("=" * 40)

    # Get script directory
    script_dir = Path(__file__).parent.absolute()
    launcher_script = script_dir / 'doom-launcher.py'

    if not launcher_script.exists():
        print("✗ doom-launcher.py not found in current directory")
        sys.exit(1)

    # Make launcher executable
    try:
        os.chmod(launcher_script, 0o755)
        print("✓ Made doom-launcher.py executable")
    except Exception as e:
        print(f"✗ Failed to make executable: {e}")

    # Detect shell and config file
    shell_config = get_shell_config()
    print(f"📁 Detected shell config: {shell_config}")

    # Create alias
    if create_alias(launcher_script, shell_config):
        print("\n🎉 Installation complete!")
        print("\nTo use the launcher:")
        print("1. Restart your terminal OR run:")
        print(f"   source {shell_config}")
        print("2. Run: doom-launcher")
        print("\nThe launcher will guide you through setup on first run.")
    else:
        print("\n❌ Installation failed")
        print("You can manually add this alias to your shell config:")
        print(f'alias doom-launcher="{launcher_script}"')

if __name__ == "__main__":
    main()