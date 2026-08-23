import os
import json
import subprocess
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QLabel, QLineEdit, QScrollArea, QFrame, QGridLayout, QTabWidget
)
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon

JSON_PATH = Path.home() / ".local/share/ArtexDesktopApps/Data/StartMenu.json"

class DataManager:
    """Gerencia a persistência de dados, detecção de apps do sistema (incluindo Flatpaks) e instalador por distro."""

    @staticmethod
    def init_json():
        JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
        if not JSON_PATH.exists():
            with open(JSON_PATH, "w") as f:
                json.dump({"favorites": []}, f)

    @staticmethod
    def load_favorites():
        DataManager.init_json()
        try:
            with open(JSON_PATH, "r") as f:
                return json.load(f).get("favorites", [])
        except Exception:
            return []

    @staticmethod
    def save_favorites(favorites):
        with open(JSON_PATH, "w") as f:
            json.dump({"favorites": favorites}, f, indent=4)

    @staticmethod
    def load_system_apps():
        # Incluindo diretórios de atalhos Flatpak
        app_dirs = [
            Path("/usr/share/applications"),
            Path("/usr/local/share/applications"),
            Path.home() / ".local/share/applications",
            Path("/var/lib/snapd/desktop/applications"),
            Path.home() / ".nix-profile/share/applications",
            Path("/var/lib/flatpak/exports/share/applications"),
            Path.home() / ".local/share/flatpak/exports/share/applications"
        ]

        seen_names = set()
        apps = []
        
        for d in app_dirs:
            if not d.exists():
                continue
            for file in d.glob("*.desktop"):
                try:
                    name, exec_cmd, icon = None, None, None
                    with open(file, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            if line.startswith("Name=") and not name:
                                name = line.split("=", 1)[1].strip()
                            elif line.startswith("Exec=") and not exec_cmd:
                                exec_cmd = line.split("=", 1)[1].strip().split("%")[0].strip()
                            elif line.startswith("Icon=") and not icon:
                                icon = line.split("=", 1)[1].strip()

                    if name and exec_cmd and name not in seen_names:
                        seen_names.add(name)
                        apps.append({
                            "id": file.name,
                            "name": name,
                            "exec": exec_cmd,
                            "icon": icon or "application-x-executable"
                        })
                except Exception:
                    continue

        apps.sort(key=lambda x: x["name"].lower())
        return apps

    @staticmethod
    def detect_distro():
        """Detecta a base da distribuição Linux."""
        os_release = Path("/etc/os-release")
        if os_release.exists():
            content = os_release.read_text().lower()
            if "ubuntu" in content or "debian" in content or "mint" in content:
                return "debian"
            elif "arch" in content or "manjaro" in content:
                return "arch"
            elif "fedora" in content or "rhel" in content:
                return "fedora"
        return "unknown"

    @staticmethod
    def install_package(pkg_name):
        """Instala o pacote usando o gerenciador correspondente da distro."""
        distro = DataManager.detect_distro()
        cmd = ""
        
        if distro == "debian":
            cmd = f"sudo apt update && sudo apt install -y {pkg_name}"
        elif distro == "arch":
            cmd = f"sudo pacman -Sy --noconfirm {pkg_name}"
        elif distro == "fedora":
            cmd = f"sudo dnf install -y {pkg_name}"
        else:
            cmd = f"echo 'Distribuição não reconhecida para instalar {pkg_name}'"

        # Abre no terminal padrão do sistema para que o usuário possa digitar a senha do sudo
        terminal_cmd = f"x-terminal-emulator -e bash -c '{cmd}; read -p \"Pressione Enter para fechar...\"'"
        subprocess.Popen(terminal_cmd, shell=True)


class StyleManager:
    """Centraliza as folhas de estilo QSS."""

    @staticmethod
    def get_main_style():
        return """
            QWidget {
                background-color: #1e1e2e;
                color: #cdd6f4;
                font-family: 'Segoe UI', sans-serif;
            }
            QTabWidget::pane {
                border: 1px solid #313244;
                background-color: #1e1e2e;
            }
            QTabBar::tab {
                background-color: #181825;
                color: #cdd6f4;
                padding: 8px 16px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #313244;
                font-weight: bold;
            }
            QPushButton {
                background-color: #313244;
                border: 1px solid #45475a;
                border-radius: 6px;
                padding: 8px;
                color: #cdd6f4;
            }
            QPushButton:hover {
                background-color: #45475a;
            }
            QLineEdit {
                background-color: #181825;
                border: 1px solid #45475a;
                border-radius: 6px;
                padding: 8px;
                color: #cdd6f4;
            }
            QScrollArea {
                border: none;
            }
            QLabel {
                background-color: transparent;
            }
        """

    @staticmethod
    def get_card_style():
        return "QFrame { background-color: #2b2b3b; border-radius: 8px; border: 1px solid #313244; }"


class StartMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.favorites = DataManager.load_favorites()
        self.apps = DataManager.load_system_apps()
        
        self.init_ui()
        self.render_apps()

    def init_ui(self):
        self.setWindowTitle("Artex Start Menu")
        self.resize(900, 550)
        self.setStyleSheet(StyleManager.get_main_style())

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # PAINEL ESQUERDO: Ações do Sistema
        left_panel = QVBoxLayout()
        left_panel.setSpacing(8)

        btn_shutdown = QPushButton(" Desligar")
        btn_reboot = QPushButton(" Reiniciar")
        btn_suspend = QPushButton(" Suspender")
        btn_logout = QPushButton(" Sair")

        btn_shutdown.clicked.connect(lambda: self.sys_action("poweroff"))
        btn_reboot.clicked.connect(lambda: self.sys_action("reboot"))
        btn_suspend.clicked.connect(lambda: self.sys_action("systemctl suspend"))
        btn_logout.clicked.connect(lambda: self.sys_action("loginctl terminate-session self"))

        left_panel.addWidget(btn_shutdown)
        left_panel.addWidget(btn_reboot)
        left_panel.addWidget(btn_suspend)
        left_panel.addWidget(btn_logout)
        left_panel.addStretch()

        left_container = QWidget()
        left_container.setLayout(left_panel)
        left_container.setFixedWidth(140)

        # PAINEL CENTRO: Sistema de Abas (Apps e Central de Instalação)
        self.tabs = QTabWidget()
        
        # --- Aba 1: Aplicativos ---
        tab_apps = QWidget()
        tab_apps_layout = QVBoxLayout(tab_apps)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Buscar aplicativo...")
        self.search_bar.textChanged.connect(self.render_apps)
        tab_apps_layout.addWidget(self.search_bar)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        self.scroll_content = QWidget()
        self.grid_layout = QGridLayout(self.scroll_content)
        self.grid_layout.setSpacing(10)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.scroll_area.setWidget(self.scroll_content)
        tab_apps_layout.addWidget(self.scroll_area)

        # --- Aba 2: Instalador / Store ---
        tab_store = self.create_store_tab()

        self.tabs.addTab(tab_apps, "Aplicativos")
        self.tabs.addTab(tab_store, "Instalador / Pacotes")

        # Montagem
        main_layout.addWidget(left_container)
        main_layout.addWidget(self.tabs, stretch=1)

    def create_store_tab(self):
        """Cria a aba com botões de instalação adaptados para a distro detectada."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        distro = DataManager.detect_distro().upper()
        lbl_info = QLabel(f"<b>Base do Sistema Detectada:</b> {distro}")
        lbl_info.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(lbl_info)

        items_to_install = [
            ("Flatpak", "flatpak"),
            ("Wine", "wine"),
            ("Steam", "steam"),
            ("Lutris", "lutris"),
            ("VLC Player", "vlc"),
            ("GIMP", "gimp")
        ]

        grid = QGridLayout()
        grid.setSpacing(10)
        grid.setAlignment(Qt.AlignmentFlag.AlignTop)

        row, col = 0, 0
        for name, pkg in items_to_install:
            card = QFrame()
            card.setStyleSheet(StyleManager.get_card_style())
            card_layout = QHBoxLayout(card)

            lbl = QLabel(name)
            btn_install = QPushButton("Instalar")
            btn_install.clicked.connect(lambda _, p=pkg: DataManager.install_package(p))

            card_layout.addWidget(lbl)
            card_layout.addWidget(btn_install)

            grid.addWidget(card, row, col)
            col += 1
            if col >= 2:
                col = 0
                row += 1

        layout.addLayout(grid)
        layout.addStretch()
        return widget

    def sys_action(self, cmd):
        subprocess.Popen(cmd, shell=True)

    def toggle_favorite(self, app_id):
        if app_id in self.favorites:
            self.favorites.remove(app_id)
        else:
            self.favorites.append(app_id)
        DataManager.save_favorites(self.favorites)
        self.render_apps()

    def launch_app(self, exec_cmd):
        subprocess.Popen(exec_cmd, shell=True)
        self.close()

    def resizeEvent(self, event):
        """Calcula dinamicamente a quantidade de colunas quando a janela é redimensionada."""
        super().resizeEvent(event)
        self.render_apps()

    def render_apps(self):
        """Renderiza os apps fixando os Favoritos no topo e a lista Geral abaixo com layout dinâmico."""
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        search_query = self.search_bar.text().lower()
        
        # Correção 2: Adapta a quantidade de colunas baseando-se na largura do ScrollArea
        available_width = self.scroll_area.width()
        card_width = 180  # Largura estimada do card + spacing
        col_count = max(1, available_width // card_width)

        fav_apps = [a for a in self.apps if a["id"] in self.favorites]
        normal_apps = [a for a in self.apps if a["id"] not in self.favorites]

        if search_query:
            fav_apps = [a for a in fav_apps if search_query in a["name"].lower()]
            normal_apps = [a for a in normal_apps if search_query in a["name"].lower()]

        current_row = 0

        # Correção 1: Sessão Fixa de Favoritos no Topo
        if fav_apps:
            lbl_fav = QLabel("⭐ Favoritos")
            lbl_fav.setStyleSheet("font-weight: bold; font-size: 14px; margin: 5px 0px;")
            self.grid_layout.addWidget(lbl_fav, current_row, 0, 1, col_count)
            current_row += 1

            col = 0
            for app in fav_apps:
                card = self.create_app_card(app, is_fav=True)
                self.grid_layout.addWidget(card, current_row, col)
                col += 1
                if col >= col_count:
                    col = 0
                    current_row += 1
            if col != 0:
                current_row += 1

        # Sessão Fixa de Todos os Aplicativos Abaixo
        if normal_apps:
            lbl_all = QLabel("📱 Todos os Aplicativos")
            lbl_all.setStyleSheet("font-weight: bold; font-size: 14px; margin: 10px 0px 5px 0px;")
            self.grid_layout.addWidget(lbl_all, current_row, 0, 1, col_count)
            current_row += 1

            col = 0
            for app in normal_apps:
                card = self.create_app_card(app, is_fav=False)
                self.grid_layout.addWidget(card, current_row, col)
                col += 1
                if col >= col_count:
                    col = 0
                    current_row += 1

    def create_app_card(self, app, is_fav):
        """Cria o card de apresentação do app."""
        card = QFrame()
        card.setStyleSheet(StyleManager.get_card_style())
        card_layout = QVBoxLayout(card)

        btn_app = QPushButton(app["name"])
        btn_app.setIcon(QIcon.fromTheme(app["icon"]))
        btn_app.setIconSize(QSize(24, 24))
        btn_app.clicked.connect(lambda _, cmd=app["exec"]: self.launch_app(cmd))

        fav_star = "★" if is_fav else "☆"
        btn_fav = QPushButton(fav_star)
        btn_fav.setFixedWidth(30)
        btn_fav.clicked.connect(lambda _, aid=app["id"]: self.toggle_favorite(aid))

        top_row = QHBoxLayout()
        top_row.addWidget(btn_app, stretch=1)
        top_row.addWidget(btn_fav)

        card_layout.addLayout(top_row)
        return card
    
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = StartMenu()
    window.show()
    sys.exit(app.exec())

"""
source ~/.venv/bin/activate.fish || source ~/.venv/bin/activate
python3 ~/ArtexDesktopApps/ADA-StartMenu/Main.py
"""