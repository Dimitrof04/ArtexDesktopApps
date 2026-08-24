class ThemeManager:
    """Gerenciador de temas para o ecossistema ArtexDesktop."""

    THEME_FILE = UserHome / ".config" / "theme_mode"
    SIGNAL_FILE = Path("/tmp/desktop_theme.signal")
    
    KITTY_CONF = UserHome / ".config" / "kitty" / "kitty.conf"
    FOOT_CONF = UserHome / ".config" / "foot" / "foot.ini"
    XFCE_CHANNEL = "xsettings"

    @classmethod
    def read_current_theme(cls) -> str:
        """Lê o tema atual do arquivo ~/.config/theme_mode."""
        if cls.THEME_FILE.exists():
            content = cls.THEME_FILE.read_text().strip().lower()
            if content in ["dark", "light"]:
                return content
        return "dark"

    @classmethod
    def _update_kitty(cls, is_dark: bool):
        if not cls.KITTY_CONF.exists():
            return
        theme_name = "Catppuccin-Mocha" if is_dark else "Catppuccin-Latte"
        subprocess.Popen(
            ["kitty", "@", "set-colors", "-a", f"~/.config/kitty/themes/{theme_name}.conf"],
            stderr=subprocess.DEVNULL
        )

    @classmethod
    def _update_foot(cls, is_dark: bool):
        if not cls.FOOT_CONF.exists():
            return
        theme_file = "dark-theme.ini" if is_dark else "light-theme.ini"
        foot_theme_link = UserHome / ".config" / "foot" / "current_theme.ini"
        target_theme = UserHome / ".config" / "foot" / theme_file

        if target_theme.exists():
            if foot_theme_link.is_symlink() or foot_theme_link.exists():
                foot_theme_link.unlink()
            foot_theme_link.symlink_to(target_theme)

    @classmethod
    def _update_thunar(cls, is_dark: bool):
        theme_name = "Adwaita-dark" if is_dark else "Adwaita"
        subprocess.Popen([
            "xfconf-query", "-c", cls.XFCE_CHANNEL,
            "-p", "/Net/ThemeName",
            "-s", theme_name
        ], stderr=subprocess.DEVNULL)

    @classmethod
    def apply_theme(cls, theme_mode: str):
        """Aplica o tema 'dark' ou 'light' no sistema todo."""
        mode = theme_mode.strip().lower()
        if mode not in ["dark", "light"]:
            mode = "dark"

        is_dark = (mode == "dark")

        # 1. Salva o estado simples
        cls.THEME_FILE.parent.mkdir(parents=True, exist_ok=True)
        cls.THEME_FILE.write_text(f"{mode}\n")

        # 2. GNOME / GTK / Cinnamon
        scheme = "prefer-dark" if is_dark else "prefer-light"
        gtk_theme = "Adwaita-dark" if is_dark else "Adwaita"
        
        subprocess.Popen(["gsettings", "set", "org.gnome.desktop.interface", "color-scheme", scheme], stderr=subprocess.DEVNULL)
        subprocess.Popen(["gsettings", "set", "org.gnome.desktop.interface", "gtk-theme", gtk_theme], stderr=subprocess.DEVNULL)

        # 3. Apps de terceiros e Terminais
        try:
            cls._update_kitty(is_dark)
            cls._update_foot(is_dark)
            cls._update_thunar(is_dark)
        except Exception as e:
            print(f"[ArtexDesktop] Erro ao aplicar subtemas: {e}")

        # 4. Notifica via arquivo de sinal
        cls.SIGNAL_FILE.write_text(str(time.time()))

    @classmethod
    def toggle(cls):
        """Alterna automaticamente entre dark e light."""
        current = cls.read_current_theme()
        new_theme = "light" if current == "dark" else "dark"
        cls.apply_theme(new_theme)

        # 1. Salva o estado simples
        cls.THEME_FILE.parent.mkdir(parents=True, exist_ok=True)
        cls.THEME_FILE.write_text(f"{mode}\n")

        # 2. GNOME / GTK / Cinnamon
        scheme = "prefer-dark" if is_dark else "prefer-light"
        gtk_theme = "Adwaita-dark" if is_dark else "Adwaita"
        
        subprocess.Popen(["gsettings", "set", "org.gnome.desktop.interface", "color-scheme", scheme], stderr=subprocess.DEVNULL)
        subprocess.Popen(["gsettings", "set", "org.gnome.desktop.interface", "gtk-theme", gtk_theme], stderr=subprocess.DEVNULL)

        # 3. Apps de terceiros e Terminais
        try:
            cls._update_kitty(is_dark)
            cls._update_foot(is_dark)
            cls._update_thunar(is_dark)
        except Exception as e:
            print(f"[ArtexDesktop] Erro ao aplicar subtemas: {e}")

        # 4. Notifica via arquivo de sinal
        cls.SIGNAL_FILE.write_text(str(time.time()))

    @classmethod
    def toggle(cls):
        """Alterna automaticamente entre dark e light."""
        current = cls.read_current_theme()
        new_theme = "light" if current == "dark" else "dark"
        cls.apply_theme(new_theme)

class Boot: #when the system starts, it will check if the theme is set and apply it
    def __init__(self):
        self.apply_theme_on_boot()

    def apply_theme_on_boot(self):
        """Aplica o tema salvo no boot do sistema."""
        current_theme = ThemeManager.read_current_theme()
        ThemeManager.apply_theme(current_theme)

    def RunCommand(self, command: list):
        # Run Command
        try:
            subprocess.run([command])
        except subprocess.CalledProcessError as e:
            print(f"[ArtexDesktop] Erro ao executar o comando: {e}")