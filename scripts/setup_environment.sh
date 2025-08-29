#!/bin/bash

set -e


VENV_DIR="venv"


if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv $VENV_DIR
else
    echo "Virtual environment already exists."
fi

source $VENV_DIR/bin/activate
echo "Virtual environment activated."



if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Installing MySQL client for macOS..."
    brew install mysql-client pkg-config
    export PKG_CONFIG_PATH="$(brew --prefix)/opt/mysql-client/lib/pkgconfig"
fi

echo "Installing required libraries..."
pip install --upgrade pip
pip install -r requirements.txt


echo "Setup complete. Activate the virtual environment using 'source $VENV_DIR/bin/activate'."
