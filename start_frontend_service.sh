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

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
  echo "Node.js is not installed. Please install Node.js to run the frontend."
  exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
  echo "npm is not installed. Please install npm to run the frontend."
  exit 1
fi

# Navigate to the frontend directory
cd frontend

# Create or update .env file with the API URL from the root .env
echo "VITE_API_URL=${VITE_API_URL}" > .env

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
  echo "Installing frontend dependencies..."
  npm install
fi

# Start the frontend service
echo "Starting frontend service..."
npm run dev
