#!/bin/bash

#exit on any error
set -e

#define project name and virtual environment directory
# PROJECT_NAME="backend"
VENV_DIR="../venv"

# echo "Setting up the Django project '$PROJECT_NAME' in a virtual environment."

#create a virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv $VENV_DIR
else
    echo "Virtual environment already exists."
fi

#activate the virtual environment
source $VENV_DIR/bin/activate
echo "Virtual environment activated."


#we also have to check if its linux?
#https://pypi.org/project/mysqlclient/



#install MySQL client if necessary, gotta do this before installing pip requirement packages otherwise this will fail
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Installing MySQL client for macOS..."
    brew install mysql-client pkg-config
    export PKG_CONFIG_PATH="$(brew --prefix)/opt/mysql-client/lib/pkgconfig"
fi

#install required libraries
echo "Installing required libraries..."
pip install --upgrade pip
pip install -r ../requirements.txt


echo "Setup complete. Activate the virtual environment using 'source $VENV_DIR/bin/activate'."
