import subprocess
import sys
from main import main
subprocess.run([
    "watchmedo",
    "auto-restart",
    "--patterns=*.py",
    "--ignore-patterns=*.json;__pycache__/*",
    "--recursive",
    "--",
    sys.executable,
    "main.py"
])
if __name__ == "__main__":
    main()