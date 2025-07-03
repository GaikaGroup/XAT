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

# Check if faster-whisper is installed
pip show faster-whisper > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "Installing required packages..."
  pip install -r dependencies.txt
fi

# Create audio directory if it doesn't exist
mkdir -p ${AUDIO_DIR:-audio}
chmod 755 ${AUDIO_DIR:-audio}

# Start the transcription service
echo "Starting transcription service on port ${SPEECH_PORT}..."
PORT=${SPEECH_PORT} python speech_service/transcribe_api.py
