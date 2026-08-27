import os

Home = os.path.expanduser("~/ArtexDesktopApps")

ConfigPath = os.path.expanduser("~/.config/ArtexDesktop/artex.py")

HEADER_COMMENT = (
    "# ArtexDesktop library for ArtexConfig | thanks for use :3\n\n"
)

def HaveConfigFile() -> bool:
    return os.path.exists(ConfigPath)

def ReadFileContent(file_path: str) -> str:
    """Lê e retorna o conteúdo do arquivo de texto."""
    if not os.path.exists(file_path):
        print(f"Aviso: O arquivo '{file_path}' não foi encontrado.")
        return ""
    
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def WriteOrUpdateBlock(app_identifier: str, block_content: str, path: str = ConfigPath):
    block_header = f"### {app_identifier}\n\n"
    block_footer = "\n#### ---\n"
    
    # Formata o novo bloco completo
    new_block_lines = [
        block_header,
        *[f"{line}\n" for line in block_content.strip().splitlines()],
        f"{block_footer}\n"
    ]

    # Se o arquivo não existir, cria do zero
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(HEADER_COMMENT)
            f.writelines(new_block_lines)
        print(f"Arquivo criado e bloco '{app_identifier}' adicionado com sucesso.")
        return

    # Lê o arquivo linha por linha
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    start_idx = -1
    end_idx = -1

    # Localiza a linha onde o bloco começa
    for i, line in enumerate(lines):
        if line.strip() == f"### {app_identifier}":
            start_idx = i
            break

    if start_idx != -1:
        # Localiza onde o bloco termina a partir do início dele
        for i in range(start_idx, len(lines)):
            if lines[i].strip() == "#### ---":
                end_idx = i
                break

        # Se encontrou o fim, substitui exatamente aquele trecho de linhas [start_idx : end_idx + 1]
        if end_idx != -1:
            # Se a linha seguinte ao fim for em branco, inclui ela na substituição para manter a formatação limpa
            if end_idx + 1 < len(lines) and lines[end_idx + 1] == "\n":
                end_idx += 1

            lines[start_idx : end_idx + 1] = new_block_lines
            print(f"Bloco '{app_identifier}' (linhas {start_idx + 1} a {end_idx + 1}) substituído com sucesso.")
        else:
            # Caso de segurança se o arquivo foi corrompido e faltou o '#### ---'
            lines[start_idx:] = new_block_lines
            print(f"Bloco '{app_identifier}' atualizado até o fim do arquivo.")
    else:
        # Se o bloco não existia no arquivo, apenas faz append no final
        lines.extend(new_block_lines)
        print(f"Novo bloco '{app_identifier}' anexado com sucesso.")

    # Sobreve o arquivo com as linhas modificadas
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(lines)

if __name__ == "__main__":
    # Caminhos para os seus arquivos
    ImportsPath = f"{Home}/basefiles/imports.py"
    MainPath = f"{Home}/basefiles/main.py"
    ArtexDesktopAppsPath = f"{Home}/basefiles/ArtexDesktopApps.py"
    Hyprland = f"{Home}/basefiles/Hyprland.py"

    # Lê o CONTEÚDO REAL de dentro de cada arquivo
    imports_content = ReadFileContent(ImportsPath)
    main_content = ReadFileContent(MainPath)
    artex_content = ReadFileContent(ArtexDesktopAppsPath)
    hyprland = ReadFileContent(Hyprland)

    if imports_content:
        WriteOrUpdateBlock("imports", imports_content, ConfigPath)
    if main_content:
        WriteOrUpdateBlock("main", main_content, ConfigPath)    
    if artex_content:
        WriteOrUpdateBlock("ArtexDesktopApps", artex_content, ConfigPath)
    if hyprland:
        WriteOrUpdateBlock("Hyprland", hyprland)