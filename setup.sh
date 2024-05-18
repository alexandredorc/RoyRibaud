#!/bin/bash

# Step 1: Install Git
echo "Checking if Git is installed..."
if ! git --version 2>&1 >/dev/null; then
    echo "Git not found. Installing Git..."
    # Download the Git installer
    curl -Lo git-installer.exe https://github.com/git-for-windows/git/releases/latest/download/Git-2.39.1-64-bit.exe
    # Run the installer
    ./git-installer.exe /VERYSILENT /NORESTART
    echo "Git installed successfully."
else
    echo "Git is already installed."
fi

# Step 2: Clone the GitHub repository
REPO_URL="https://github.com/yourusername/yourrepository.git"
REPO_NAME=$(basename $REPO_URL .git)
cd $REPO_NAME

# Step 3: Install Python3
echo "Checking if Python3 is installed..."
if ! python3 --version 2>&1 >/dev/null; then
    echo "Python3 not found. Installing Python3..."
    # Download the Python installer
    curl -Lo python-installer.exe https://www.python.org/ftp/python/3.9.7/python-3.9.7-amd64.exe
    # Run the installer
    ./python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
    echo "Python3 installed successfully."
else
    echo "Python3 is already installed."
fi

# Step 4: Install dependencies
echo "Installing dependencies from requirements.txt..."
pip3 install -r requirements.txt

echo "Setup complete."
