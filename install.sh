echo -e "${BLUE}=======================================${NC}"
echo -e "${BLUE}            Welcome to Apps!           ${NC}"
echo -e "${BLUE}=======================================${NC}"

CreateBaseFolders(){
    mkdir ~/.config/ArtexDesktop
    mkdir ~/.local/temp
    mkdir ~/.local/share
    mkdir ~/.local/share/ArtexDesktopApps
    mkdir ~/.local/share/ArtexDesktopApps/Data
}

CreateBaseFiles(){
    cp basefiles/ArtexDesktopTheme ~/.config/ArtexDesktop
    cp basefiles/ArtexDesktopApps.conf ~/.config/ArtexDesktop
}

CreateBaseFolders
CreateBaseFiles