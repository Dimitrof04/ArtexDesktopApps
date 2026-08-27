import os
import subprocess
import time
import re
from pathlib import Path

# Global Variabeis
USER_HOME = Path.home()
CONFIG_DIR = USER_HOME / ".config" / "ArtexDesktop"
LUA_CONFIG_PATH = CONFIG_DIR / "Files" / "hyprland.lua" # Altere para o caminho exato do seu sc
BASE_FILES_DIR = os.path.join(CONFIG_DIR, "basefiles")
GLOBAL_CONF_FILE = os.path.join(CONFIG_DIR, "ArtexConfig.conf")