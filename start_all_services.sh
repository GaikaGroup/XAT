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

# Make sure the individual scripts are executable
chmod +x start_backend_service.sh
chmod +x start_transcription_service.sh
chmod +x start_frontend_service.sh

# Function to check if a command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

echo "Starting HugDimonXat services..."

# Check if we're on macOS and have terminal or iTerm
if [[ "$OSTYPE" == "darwin"* ]]; then
  if command_exists osascript; then
    echo "Detected macOS, starting services in separate terminal windows..."

    # Start backend in a new Terminal window
    osascript -e 'tell application "Terminal" to do script "cd \"'$PWD'\" && ./start_backend_service.sh"'

    # Start transcription service in another Terminal window
    osascript -e 'tell application "Terminal" to do script "cd \"'$PWD'\" && ./start_transcription_service.sh"'

    # Start frontend service in another Terminal window
    osascript -e 'tell application "Terminal" to do script "cd \"'$PWD'\" && ./start_frontend_service.sh"'

    echo "All services started in separate terminal windows."
    exit 0
  fi
fi

# For Linux or if the above didn't work, start in background
echo "Starting services in the background..."

# Start backend service in the background
./start_backend_service.sh > backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend service started with PID: $BACKEND_PID"

# Start transcription service in the background
./start_transcription_service.sh > transcription.log 2>&1 &
TRANSCRIPTION_PID=$!
echo "Transcription service started with PID: $TRANSCRIPTION_PID"

# Start frontend service in the background
./start_frontend_service.sh > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend service started with PID: $FRONTEND_PID"

echo "All services started in the background."
echo "To view logs:"
echo "  Backend: tail -f backend.log"
echo "  Transcription: tail -f transcription.log"
echo "  Frontend: tail -f frontend.log"
echo ""
echo "To stop services:"
echo "  kill $BACKEND_PID $TRANSCRIPTION_PID $FRONTEND_PID"

# Save PIDs to a file for easy stopping later
echo "$BACKEND_PID $TRANSCRIPTION_PID $FRONTEND_PID" > service_pids.txt
echo "PIDs saved to service_pids.txt"

# Create a stop script
cat > stop_all_services.sh << EOF
#!/bin/bash
if [ -f service_pids.txt ]; then
  echo "Stopping services..."
  kill \$(cat service_pids.txt) 2>/dev/null
  rm service_pids.txt
  echo "Services stopped."
else
  echo "No service PIDs found. Services may not be running."
  # Try to find and kill the processes anyway
  pkill -f "python backend/app/main.py" 2>/dev/null
  pkill -f "python speech_service/transcribe_api.py" 2>/dev/null
  pkill -f "npm run dev" 2>/dev/null
  echo "Attempted to stop any running services."
fi
EOF

chmod +x stop_all_services.sh
echo "Created stop_all_services.sh to easily stop the services."
