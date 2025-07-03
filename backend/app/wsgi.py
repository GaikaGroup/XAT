from main import app, initialize_app  # because main.py is in the same folder

try:
    initialize_app()
except Exception as e:
    import sys
    print(f"Failed to initialize app: {e}", file=sys.stderr)
    raise

application = app
