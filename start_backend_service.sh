#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
  echo "Loading environment variables from .env file"
  # Use a more robust method to load environment variables
  while IFS='=' read -r key value || [ -n "$key" ]; do
    # Skip comments and empty lines
    [[ $key =~ ^[[:space:]]*# ]] && continue
    [[ -z "$key" ]] && continue

    # Extract the value without inline comments
    value=$(echo "$value" | sed 's/[[:space:]]*#.*$//')

    # Export the variable
    export "$key=$value"
  done < .env
fi

# Activate the virtual environment
if [ -d "venv_new" ]; then
  echo "Activating virtual environment: venv_new"
  source venv_new/bin/activate
elif [ -d "venv" ]; then
  echo "Activating virtual environment: venv"
  source venv/bin/activate
else
  echo "No virtual environment found. Using system Python."
fi

# Check if required packages are installed
pip show flask > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "Installing required packages..."
  pip install -r dependencies.txt
fi

# Start the backend service
echo "Starting backend service on port ${BACKEND_PORT}..."
PORT=${BACKEND_PORT} python backend/app/main.py
