#!/bin/bash

# Exit on any error
set -e

# Define project name and virtual environment directory
PROJECT_NAME="backend"
VENV_DIR="venv"

echo "Setting up the Django project '$PROJECT_NAME' in a virtual environment."

# Step 1: Create a virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv $VENV_DIR
else
    echo "Virtual environment already exists."
fi

# Step 2: Activate the virtual environment
source $VENV_DIR/bin/activate
echo "Virtual environment activated."

# Step 3: Install required libraries
echo "Installing required libraries..."
pip install --upgrade pip
pip install django psycopg2-binary python-decouple

# Step 4: Create the Django project if it doesn't exist
if [ ! -d "$PROJECT_NAME" ]; then
    echo "Creating Django project '$PROJECT_NAME'..."
    django-admin startproject $PROJECT_NAME
else
    echo "Django project '$PROJECT_NAME' already exists."
fi

# Step 5: Create a requirements.txt file
echo "Generating requirements.txt..."
pip freeze > requirements.txt

# Step 6: Set up .env file
ENV_FILE=".env"

echo "Setup complete. Activate the virtual environment using 'source $VENV_DIR/bin/activate'."
