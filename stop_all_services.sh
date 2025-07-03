#!/bin/bash

# Script to stop all services started by start_all_services.sh

echo "Stopping all services..."

# Check if PID file exists
if [ -f service_pids.txt ]; then
  echo "Found service PIDs file, stopping services..."
  # Read PIDs from file and kill them
  while read pid; do
    if [ -n "$pid" ] && kill -0 $pid 2>/dev/null; then
      echo "Stopping process with PID: $pid"
      kill $pid
    else
      echo "Process with PID $pid is not running"
    fi
  done < service_pids.txt
  
  # Remove the PID file
  rm service_pids.txt
  echo "Removed service_pids.txt"
else
  echo "No service_pids.txt file found, attempting to find and stop services by name..."
  
  # Try to find and kill processes by their command patterns
  echo "Stopping backend service..."
  pkill -f "python backend/app/main.py" || echo "Backend service not found or already stopped"
  
  echo "Stopping transcription service..."
  pkill -f "python speech_service/transcribe_api.py" || echo "Transcription service not found or already stopped"
  
  echo "Stopping frontend service..."
  pkill -f "npm run dev" || echo "Frontend service not found or already stopped"
fi

echo "All services stopped."