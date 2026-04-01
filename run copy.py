

import subprocess

subprocess.run([
    "watchmedo",
    "auto-restart",
    "--patterns=*.py",
    "--recursive",
    "--",
    "python",
    "main.py"
])