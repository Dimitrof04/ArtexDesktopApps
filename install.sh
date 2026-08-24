echo -e "${BLUE}=======================================${NC}"
echo -e "${BLUE}         Welcome to ArtexApps!         ${NC}"
echo -e "${BLUE}=======================================${NC}"

CreateBaseFolders(){
    mkdir ~/.config/ArtexDesktop
    mkdir ~/.local/temp
    mkdir ~/.local/share
    mkdir ~/.local/share/ArtexDesktopApps
    mkdir ~/.local/share/ArtexDesktopApps/Data
    mkdir ~/.config/ArtexDesktop
}

CreateBaseFiles(){
    cp basefiles/ArtexDesktopTheme ~/.config/ArtexDesktop
    cp basefiles/ArtexDesktopApps.conf ~/.config/ArtexDesktop
}

echo -e "${green} Create Folders"
CreateBaseFolders
echo -e "${green} Create Files"
CreateBaseFiles

echo -e "${green} Install python dependecies"

python3 -m venv .venv
source .venv/bin/activate || source .venv/bin/activate.fish 
pip install --upgrade pip
pip install PyQt6

python3 ~/ArtexDesktopApps/ArtexAppsConnectConfig.py

deactivate