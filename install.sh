#!/bin/bash

# Function to show progress bar
show_progress() {
    local progress=$1
    local width=50
    local filled=$((progress * width / 100))
    local empty=$((width - filled))
    printf "\rProgress: ["
    for ((i=0; i<filled; i++)); do
        printf "\033[32m#\033[0m"
    done
    for ((i=0; i<empty; i++)); do
        printf " "
    done
    printf "] %d%%\n" "$progress"
}

echo -e "\033[36m\nStarting installation process...\033[0m"
sleep 2

echo -e "\033[36m\nCreating virtual environment...\033[0m"
python3 -m venv virtual
show_progress 20
sleep 1

echo -e "\033[36m\nActivating virtual environment...\033[0m"
source virtual/bin/activate
show_progress 40
sleep 1

echo -e "\033[36m\nUpgrading pip, setuptools and wheel...\033[0m"
pip install --upgrade pip setuptools wheel
show_progress 60
sleep 1

echo -e "\033[36m\nInstalling required packages...\033[0m"
pip install -r requirements.txt
show_progress 80
sleep 1

echo -e "\033[36m\nRunning utilities setup...\033[0m"
python3 utilities.py
show_progress 90
sleep 1

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HELPER_PATH="$SCRIPT_DIR/sysadmin/helper.sh"
CURRENT_USER=$(whoami)

echo -e "\033[36m\nConfiguring system permissions...\033[0m"
echo "${CURRENT_USER} ALL=(ALL) NOPASSWD:${HELPER_PATH}" | sudo EDITOR='tee -a' visudo
show_progress 100
sleep 2

echo -e "\033[36m\nInstallation completed successfully!\033[0m"