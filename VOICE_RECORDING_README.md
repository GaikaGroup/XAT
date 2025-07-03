# Voice Recording Feature for HugDimonXat

This document provides instructions for setting up and using the voice recording feature in HugDimonXat.

## Overview

The voice recording feature allows users to send voice messages to the chatbot by clicking the microphone button. The voice message is transcribed using the transcription service and then processed by the main backend service.

## Requirements

- Python 3.7 or higher
- Virtual environment (venv or venv_new)
- Required Python packages (installed via dependencies.txt)
- Modern web browser with microphone access

## Setup Instructions

1. **Install Dependencies**

   ```bash
   # Create and activate a virtual environment (if not already done)
   python3 -m venv venv_new
   source venv_new/bin/activate

   # Install required packages
   pip install -r dependencies.txt
   ```

2. **Make Scripts Executable**

   ```bash
   chmod +x start_backend_service.sh
   chmod +x start_transcription_service.sh
   chmod +x start_all_services.sh
   ```

3. **Start Services**

   You can start both services with a single command:

   ```bash
   ./start_all_services.sh
   ```

   This will start both the backend service and the transcription service. On macOS, it will open separate terminal windows for each service.

   Alternatively, you can start each service individually:

   ```bash
   # Start the backend service
   ./start_backend_service.sh

   # Start the transcription service (in a separate terminal)
   ./start_transcription_service.sh
   ```

4. **Start the Frontend**

   ```bash
   cd frontend
   npm install  # Only needed the first time
   npm run dev
   ```

5. **Access the Application**

   Open your browser and navigate to:

   ```
   http://localhost:5173
   ```

## Using Voice Recording

1. Click the microphone button in the chat interface
2. Allow microphone access when prompted by your browser
3. Speak your message
4. Click the microphone button again to stop recording
5. The message will be automatically transcribed and sent to the chatbot

## Troubleshooting

### Connection Refused Errors

If you see "ERR_CONNECTION_REFUSED" errors in the browser console when trying to use voice recording:

1. Make sure the transcription service is running:
   ```bash
   ./start_transcription_service.sh
   ```

2. Check if the service is running on port 5050:
   ```bash
   lsof -i :5050
   ```

3. Check the transcription service logs:
   ```bash
   tail -f transcription.log  # If started with start_all_services.sh
   ```

### Port Conflicts on macOS

On macOS, port 5000 is used by AirPlay. The `start_backend_service.sh` script automatically uses port 5001 on macOS. If you're still having issues:

1. Disable AirPlay Receiver in System Preferences → General → AirDrop & Handoff
2. Or manually specify a different port:
   ```bash
   PORT=5002 ./start_backend_service.sh
   ```

### Microphone Access Issues

If the browser doesn't request microphone access or the recording doesn't work:

1. Check browser permissions (chrome://settings/content/microphone in Chrome)
2. Try using a different browser
3. Check the browser console for specific error messages

## Stopping the Services

To stop all services:

```bash
./stop_all_services.sh
```

Or manually stop them:

```bash
# Find the process IDs
ps aux | grep python

# Kill the processes
kill <backend_pid> <transcription_pid>
```

## Technical Details

The voice recording feature works as follows:

1. When the user clicks the microphone button, the browser requests microphone access
2. The MediaRecorder API is used to record audio
3. When recording stops, the audio is sent to the transcription service at http://localhost:5050/transcribe
4. The transcription service uses faster-whisper to transcribe the audio and detect the language
5. The transcribed text and detected language are sent to the main backend service
6. The backend processes the text and returns a response, which is displayed in the chat interface

The scripts ensure that both services are running correctly and handle common issues like port conflicts on macOS.

## Logs

If you started the services with `start_all_services.sh`, logs are available in:

- Backend service: `backend.log`
- Transcription service: `transcription.log`

You can view them with:

```bash
tail -f backend.log
tail -f transcription.log
```
