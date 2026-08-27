#!/bin/bash

echo -e "${BLUE}=======================================${NC}"
echo -e "${BLUE}         Welcome to ArtexApps!         ${NC}"
echo -e "${BLUE}=======================================${NC}"

CreateBaseFolders(){
    mkdir ~/.local/share
    mkdir ~/.local/share/ArtexDesktopApps
    mkdir ~/.local/share/ArtexDesktopApps/Data
    mkdir ~/.config/ArtexDesktop
    mkdir ~/.config/ArtexDesktop/Files
}

cd ~/ArtexDesktopApps

CreateBaseFiles(){
    cp basefiles/artexconfig.py ~/.config/ArtexDesktop/artexconfig.py
}

echo -e "${green} Create Folders"
CreateBaseFolders
echo -e "${green} Create Files"
CreateBaseFiles

echo -e "${green} Install python dependecies"

cd ~

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install PyQt6

python3 ~/ArtexDesktopApps/ArtexAppsConnectConfig.py

deactivate

echo -e "${blue} Completed Install"